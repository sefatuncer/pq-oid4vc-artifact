// C3 adapter, SDJWT-010: sd-jwt-payload 0.5.1 with josekit 0.8.7 as JOSE layer.
// Usage (in the container): /a/adapter SDJWT-010 <jobs-v1.3.jsonl> <cikti.jsonl> <kosu>
//
// sd-jwt-payload parses SD-JWTs and resolves disclosures but verifies no signature. The
// crate's own example and its test `sd_jwt_is_verifiable` verify the issuer-signed JWT with
// josekit: `josekit::jwt::decode_with_verifier(jwt, &verifier)` where the verifier is built
// for one algorithm. That pattern is reproduced here; see MAPPING.md and NOTES.md.
#[path = "../../common/adapter_common.rs"]
mod common;

use std::sync::Arc;

use common::*;
use josekit::jwk::Jwk;
use josekit::jws::{JwsVerifier, EdDSA, ES256, ES256K, ES384, ES512, PS256, PS384, PS512, RS256, RS384, RS512};
use josekit::JoseError;
use sd_jwt_payload::{SdJwt, Sha256Hasher};
use serde_json::Value;

/// Asymmetric JWS algorithms of josekit (HS* left out, as in the reference adapters).
const SUPPORTED: &[&str] = &[
    "ES256", "ES384", "ES512", "ES256K", "RS256", "RS384", "RS512", "PS256", "PS384", "PS512", "EdDSA",
];

fn verifier_for(name: &str, jwk: &Jwk) -> Result<Box<dyn JwsVerifier>, JoseError> {
    Ok(match name {
        "ES256" => Box::new(ES256.verifier_from_jwk(jwk)?),
        "ES384" => Box::new(ES384.verifier_from_jwk(jwk)?),
        "ES512" => Box::new(ES512.verifier_from_jwk(jwk)?),
        "ES256K" => Box::new(ES256K.verifier_from_jwk(jwk)?),
        "RS256" => Box::new(RS256.verifier_from_jwk(jwk)?),
        "RS384" => Box::new(RS384.verifier_from_jwk(jwk)?),
        "RS512" => Box::new(RS512.verifier_from_jwk(jwk)?),
        "PS256" => Box::new(PS256.verifier_from_jwk(jwk)?),
        "PS384" => Box::new(PS384.verifier_from_jwk(jwk)?),
        "PS512" => Box::new(PS512.verifier_from_jwk(jwk)?),
        "EdDSA" => Box::new(EdDSA.verifier_from_jwk(jwk)?),
        other => unreachable!("{other} is not in SUPPORTED"),
    })
}

fn class_jose(err: &JoseError) -> &'static str {
    let msg = err.to_string();
    match err {
        JoseError::InvalidSignature(_) => "imza-gecersiz",
        JoseError::UnsupportedSignatureAlgorithm(_) => "alg-desteklenmiyor",
        JoseError::InvalidJwkFormat(_) | JoseError::InvalidKeyFormat(_) => "alg-anahtar-uyusmazligi",
        JoseError::InvalidJwsFormat(_) | JoseError::InvalidJwtFormat(_) => {
            if msg.contains("alg header claim is not") {
                "alg-izin-disi"
            } else if msg.contains("kid header claim") {
                "anahtar-bulunamadi"
            } else if msg.contains("critical name") {
                "crit"
            } else {
                "ayristirma"
            }
        }
        JoseError::InvalidJson(_) => "ayristirma",
        _ => klass(&msg),
    }
}

fn class_sd(err: &sd_jwt_payload::Error) -> &'static str {
    match err {
        sd_jwt_payload::Error::DeserializationError(_) => "ayristirma",
        _ => "istisna-diger",
    }
}

struct SdJwtPayloadTarget;

impl Target for SdJwtPayloadTarget {
    fn id(&self) -> &'static str {
        "SDJWT-010"
    }

    fn api(&self) -> &'static str {
        "SdJwt::parse(p) + josekit::jwt::decode_with_verifier(jwt, &<ALG>.verifier_from_jwk(&jwk)) + SdJwt::into_disclosed_object(&Sha256Hasher::new())"
    }

    fn formats(&self) -> &'static [&'static str] {
        &["sd-jwt-compact", "compact-as-sdjwt"]
    }

    fn verify(&self, job: &Job, eff: &str, data: &str, x: &str) -> Outcome {
        if temel(&job.politika) == "L4-YOL" {
            // No x5c path-class policy in the API.
            return Outcome::NotExpressible;
        }
        if job.artefakt.starts_with("vp") {
            // KB-JWT is parsed but never verified by the library (no API); a presentation
            // policy with required key binding cannot be expressed.
            return Outcome::NotExpressible;
        }
        let mut presentation = data.trim().to_string();
        if eff == "compact-as-sdjwt" {
            presentation.push('~'); // SD-JWT without disclosures; signature and payload unchanged
        }

        let sd_jwt = match SdJwt::parse(&presentation) {
            Ok(s) => s,
            Err(e) => return reject(class_sd(&e), format!("SdJwt::parse: {e}")),
        };
        // Issuer-signed JWT, extracted as in tests/api_test.rs `sd_jwt_is_verifiable`.
        let full = sd_jwt.presentation();
        let jwt = full.split_once('~').map(|(j, _)| j).unwrap_or(full.as_str()).to_string();

        let header = match jws_header(&jwt) {
            Ok(h) => h,
            Err(e) => return reject("ayristirma", e),
        };
        let header_alg = header.get("alg").and_then(Value::as_str).unwrap_or("").to_string();
        let w = allowed(&job.politika, x, payload_iss(&jwt).as_deref(), SUPPORTED);
        let usable: Vec<&str> = w.iter().map(String::as_str).filter(|a| SUPPORTED.contains(a)).collect();
        let name = match usable.len() {
            0 => {
                return reject(
                    "alg-desteklenmiyor",
                    format!("no permitted algorithm {w:?} has a josekit verifier"),
                )
            }
            // One permitted algorithm: the verifier is built for it; josekit then requires
            // the header alg to match (jws_context.rs L428-437).
            1 => usable[0].to_string(),
            // No restriction (GEC/P0/P1): the verifier follows the token's own alg.
            _ if usable.contains(&header_alg.as_str()) => header_alg.clone(),
            _ => {
                return reject(
                    "alg-desteklenmiyor",
                    format!("header alg {header_alg} has no josekit verifier"),
                )
            }
        };

        let jwk_value = match keys().jwk_for(&header) {
            Some(j) => j,
            None => return reject("anahtar-bulunamadi", "no key for kid/alg"),
        };
        let jwk = match jwk_value.as_object().cloned().map(Jwk::from_map) {
            Some(Ok(j)) => j,
            Some(Err(e)) => return reject(class_jose(&e), format!("Jwk::from_map: {e}")),
            None => return reject("ayristirma", "JWK is not an object"),
        };
        let verifier = match verifier_for(&name, &jwk) {
            Ok(v) => v,
            Err(e) => return reject(class_jose(&e), format!("{name}.verifier_from_jwk: {e}")),
        };
        if let Err(e) = josekit::jwt::decode_with_verifier(&jwt, &*verifier) {
            return reject(class_jose(&e), format!("josekit: {e}"));
        }
        // Disclosure processing as documented in the README ("Verifying").
        if let Err(e) = sd_jwt.into_disclosed_object(&Sha256Hasher::new()) {
            return reject(class_sd(&e), format!("SdJwt::into_disclosed_object: {e}"));
        }
        Outcome::Accept(VerifiedAlg::valid(verifier.algorithm().name()))
    }
}

fn main() {
    let sha = sources_sha256(&[include_bytes!("main.rs"), include_bytes!("../../common/adapter_common.rs")]);
    run(Arc::new(SdJwtPayloadTarget), env!("TARGET_CRATE_VERSION"), &sha);
}
