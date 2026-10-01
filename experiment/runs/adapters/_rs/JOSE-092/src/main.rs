// C3 adapter, JOSE-092: jsonwebtoken 11.1.0 (crypto backend: aws_lc_rs).
// Usage (in the container): /a/adapter JOSE-092 <jobs-v1.3.jsonl> <cikti.jsonl> <kosu>
//
// The permitted set W goes into `Validation::algorithms` (per-call allow-list). The library
// requires every entry to belong to the family of the verifying algorithm and rejects a
// mixed-family list outright (decoding.rs L346-358), so W is passed restricted to the family
// of the resolved key, which is what `Validation::new_for_family` does. See MAPPING.md.
#[path = "../../common/adapter_common.rs"]
mod common;

use std::sync::Arc;

use common::*;
use jsonwebtoken::errors::ErrorKind;
use jsonwebtoken::jwk::Jwk;
use jsonwebtoken::{decode, Algorithm, DecodingKey, Validation};
use serde_json::Value;

/// Asymmetric members of `jsonwebtoken::Algorithm` (HS* left out, as in the reference adapters).
const SUPPORTED: &[&str] = &["ES256", "ES384", "RS256", "RS384", "RS512", "PS256", "PS384", "PS512", "EdDSA"];

fn class_of(kind: &ErrorKind) -> &'static str {
    match kind {
        ErrorKind::InvalidSignature => "imza-gecersiz",
        ErrorKind::InvalidAlgorithm | ErrorKind::MissingAlgorithm => "alg-izin-disi",
        ErrorKind::InvalidAlgorithmName | ErrorKind::UnsupportedAlgorithm => "alg-desteklenmiyor",
        ErrorKind::InvalidEcdsaKey
        | ErrorKind::InvalidEddsaKey
        | ErrorKind::InvalidRsaKey(_)
        | ErrorKind::InvalidKeyFormat => "alg-anahtar-uyusmazligi",
        ErrorKind::InvalidToken | ErrorKind::Base64(_) | ErrorKind::Utf8(_) => "ayristirma",
        // An unknown `alg` value fails while the header is deserialised into `Algorithm`.
        ErrorKind::Json(e) if e.to_string().contains("unknown variant") => "alg-desteklenmiyor",
        ErrorKind::Json(_) => "ayristirma",
        ErrorKind::ExpiredSignature | ErrorKind::ImmatureSignature => "zaman",
        _ => "istisna-diger",
    }
}

struct JsonWebToken;

impl Target for JsonWebToken {
    fn id(&self) -> &'static str {
        "JOSE-092"
    }

    fn api(&self) -> &'static str {
        "jsonwebtoken::decode(token, &DecodingKey::from_jwk(&jwk), &Validation{algorithms: W within key family, claim checks off})"
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
        let jwk_value = match keys().jwk_for(&header) {
            Some(j) => j,
            None => return reject("anahtar-bulunamadi", "no key for kid/alg"),
        };
        let jwk: Jwk = match serde_json::from_value(jwk_value) {
            Ok(j) => j,
            Err(e) => return reject("ayristirma", format!("jsonwebtoken::jwk::Jwk: {e}")),
        };
        let key = match DecodingKey::from_jwk(&jwk) {
            Ok(k) => k,
            Err(e) => return reject(class_of(e.kind()), format!("DecodingKey::from_jwk: {e}")),
        };

        let w = allowed(&job.politika, x, payload_iss(tok).as_deref(), SUPPORTED);
        let family = key.family();
        let mut validation = Validation::new_for_family(family);
        validation.algorithms = w
            .iter()
            .filter_map(|a| a.parse::<Algorithm>().ok())
            .filter(|a| a.family() == family)
            .collect();
        // Claim checks off (no clock can be injected; signature policy is what is measured).
        validation.validate_exp = false;
        validation.validate_nbf = false;
        validation.validate_aud = false;
        validation.required_spec_claims.clear();

        match decode::<Value>(tok, &key, &validation) {
            Ok(td) => {
                let alg = serde_json::to_value(td.header.alg)
                    .ok()
                    .and_then(|v| v.as_str().map(str::to_string))
                    .unwrap_or_default();
                Outcome::Accept(VerifiedAlg::valid(alg))
            }
            Err(e) => reject(class_of(e.kind()), format!("jsonwebtoken::errors::Error: {e}")),
        }
    }
}

fn main() {
    let sha = sources_sha256(&[include_bytes!("main.rs"), include_bytes!("../../common/adapter_common.rs")]);
    run(Arc::new(JsonWebToken), env!("TARGET_CRATE_VERSION"), &sha);
}
