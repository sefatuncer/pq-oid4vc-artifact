// C3 adapter, JOSE-091: frank_jwt 3.1.4.
// Usage (in the container): /a/adapter JOSE-091 <jobs-v1.3.jsonl> <cikti.jsonl> <kosu>
//
// frank_jwt has no algorithm allow-list and never reads the header `alg`:
// `decode(token, key, algorithm, options)` verifies under the one algorithm the caller
// passes (lib.rs L167-181, L333-375). The permitted set W is therefore expressed through
// that parameter. See MAPPING.md for the full policy table.
#[path = "../../common/adapter_common.rs"]
mod common;

use std::sync::Arc;

use common::*;
use frank_jwt::{Algorithm, ValidationOptions};
use openssl::bn::BigNum;
use openssl::ec::{EcGroup, EcKey};
use openssl::nid::Nid;
use openssl::pkey::{Id, PKey};
use openssl::rsa::Rsa;
use serde_json::Value;

/// Asymmetric members of `frank_jwt::Algorithm` (HS* left out, as in the reference adapters).
const SUPPORTED: &[&str] = &["ES256", "ES384", "ES512", "RS256", "RS384", "RS512"];

fn algorithm(name: &str) -> Option<Algorithm> {
    Some(match name {
        "ES256" => Algorithm::ES256,
        "ES384" => Algorithm::ES384,
        "ES512" => Algorithm::ES512,
        "RS256" => Algorithm::RS256,
        "RS384" => Algorithm::RS384,
        "RS512" => Algorithm::RS512,
        _ => return None,
    })
}

fn field(j: &Value, k: &str) -> Result<Vec<u8>, String> {
    b64d(j.get(k).and_then(Value::as_str).ok_or(format!("JWK member {k} missing"))?)
}

/// frank_jwt takes the public key as a PEM document (`ToKey`). The JWK is converted with
/// the same openssl crate frank_jwt links; no verification happens here.
fn jwk_to_pem(j: &Value) -> Result<Vec<u8>, String> {
    let kty = j.get("kty").and_then(Value::as_str).unwrap_or("");
    let crv = j.get("crv").and_then(Value::as_str).unwrap_or("");
    let e = |err: openssl::error::ErrorStack| format!("key conversion: {err}");
    let pkey = match (kty, crv) {
        ("EC", c) => {
            let nid = match c {
                "P-256" => Nid::X9_62_PRIME256V1,
                "P-384" => Nid::SECP384R1,
                "P-521" => Nid::SECP521R1,
                _ => return Err(format!("unsupported key type EC/{c}")),
            };
            let group = EcGroup::from_curve_name(nid).map_err(e)?;
            let x = BigNum::from_slice(&field(j, "x")?).map_err(e)?;
            let y = BigNum::from_slice(&field(j, "y")?).map_err(e)?;
            PKey::from_ec_key(EcKey::from_public_key_affine_coordinates(&group, &x, &y).map_err(e)?)
                .map_err(e)?
        }
        ("RSA", _) => {
            let n = BigNum::from_slice(&field(j, "n")?).map_err(e)?;
            let ex = BigNum::from_slice(&field(j, "e")?).map_err(e)?;
            PKey::from_rsa(Rsa::from_public_components(n, ex).map_err(e)?).map_err(e)?
        }
        ("OKP", "Ed25519") => PKey::public_key_from_raw_bytes(&field(j, "x")?, Id::ED25519).map_err(e)?,
        ("OKP", "Ed448") => PKey::public_key_from_raw_bytes(&field(j, "x")?, Id::ED448).map_err(e)?,
        (k, c) => return Err(format!("unsupported key type {k}/{c}")),
    };
    pkey.public_key_to_pem().map_err(e)
}

fn class_of(err: &frank_jwt::Error) -> &'static str {
    use frank_jwt::Error::*;
    match err {
        SignatureInvalid => "imza-gecersiz",
        SignatureExpired | ExpirationInvalid => "zaman",
        JWTInvalid | FormatInvalid(_) | ProtocolError(_) => "ayristirma",
        // Raised while loading the PEM key for the requested algorithm (wrong key type).
        OpenSslError(_) => "alg-anahtar-uyusmazligi",
        IssuerInvalid | AudienceInvalid | IoError(_) => "istisna-diger",
    }
}

struct FrankJwt;

impl Target for FrankJwt {
    fn id(&self) -> &'static str {
        "JOSE-091"
    }

    fn api(&self) -> &'static str {
        "frank_jwt::decode(token, &public_key_pem, Algorithm::<W or header alg>, &ValidationOptions::dangerous())"
    }

    fn formats(&self) -> &'static [&'static str] {
        &["compact"]
    }

    fn verify(&self, job: &Job, _eff: &str, data: &str, x: &str) -> Outcome {
        if temel(&job.politika) == "L4-YOL" {
            // No x5c path-class policy in the API.
            return Outcome::NotExpressible;
        }
        let tok = data.trim();
        let header = match jws_header(tok) {
            Ok(h) => h,
            Err(e) => return reject("ayristirma", e),
        };
        let header_alg = header.get("alg").and_then(Value::as_str).unwrap_or("").to_string();

        // W reduced to the algorithms frank_jwt can be told to use.
        let w = allowed(&job.politika, x, payload_iss(tok).as_deref(), SUPPORTED);
        let usable: Vec<&str> = w.iter().map(String::as_str).filter(|a| SUPPORTED.contains(a)).collect();
        let name = match usable.len() {
            0 => {
                return reject(
                    "alg-desteklenmiyor",
                    format!("no permitted algorithm {w:?} exists in frank_jwt::Algorithm"),
                )
            }
            // One permitted algorithm: the verifier is pinned to it; frank_jwt ignores the header.
            1 => usable[0].to_string(),
            // No restriction (GEC/P0/P1): the token's own alg selects the algorithm.
            _ if usable.contains(&header_alg.as_str()) => header_alg.clone(),
            _ => {
                return reject(
                    "alg-desteklenmiyor",
                    format!("header alg {header_alg} does not exist in frank_jwt::Algorithm"),
                )
            }
        };
        let alg = algorithm(&name).expect("name taken from SUPPORTED");

        let jwk = match keys().jwk_for(&header) {
            Some(j) => j,
            None => return reject("anahtar-bulunamadi", "no key for kid/alg"),
        };
        let pem = match jwk_to_pem(&jwk) {
            Ok(p) => p,
            Err(e) => return reject("alg-desteklenmiyor", e),
        };

        // ValidationOptions::dangerous() switches off the only claim check (exp against the
        // wall clock); the signature is always verified (lib.rs L174).
        match frank_jwt::decode(tok, &pem, alg, &ValidationOptions::dangerous()) {
            Ok(_) => Outcome::Accept(VerifiedAlg::valid(name)),
            Err(err) => reject(class_of(&err), format!("frank_jwt::Error: {err}")),
        }
    }
}

fn main() {
    let sha = sources_sha256(&[include_bytes!("main.rs"), include_bytes!("../../common/adapter_common.rs")]);
    run(Arc::new(FrankJwt), env!("TARGET_CRATE_VERSION"), &sha);
}
