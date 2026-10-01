// C3 adapter, SDJWT-025: spruceid ssi-sd-jwt 0.6.0 (ssi-jws 0.5.0 / ssi-jwk 0.4.0 with the
// `secp256r1` and `ed25519` features, ssi-jwt 0.6.0).
// Usage (in the container): /a/adapter SDJWT-025 <isler.jsonl> <cikti.jsonl> <kosu>
//
// Verification goes through `VerificationParameters` (key resolver + date-time). There is no
// algorithm allow-list anywhere in the verification path: the header `alg` selects the
// algorithm (ssi-jws verification.rs L107-121, lib.rs L673-690). Only GEC/P0/P1/P2 can be
// expressed, as for the SD-JWT target of the Python adapter. See MAPPING.md.
#[path = "../../common/adapter_common.rs"]
mod common;

use std::sync::Arc;

use common::*;
use futures::executor::block_on;
use ssi_claims_core::chrono::DateTime;
use ssi_claims_core::{Invalid, InvalidClaims, InvalidProof, ProofValidationError, VerificationParameters};
use ssi_jwk::JWK;
use ssi_jws::JwsStr;
use ssi_jwt::ToDecodedJwt;
use ssi_sd_jwt::SdJwt;

fn class_invalid(inv: &Invalid) -> &'static str {
    match inv {
        Invalid::Proof(InvalidProof::Signature) => "imza-gecersiz",
        Invalid::Proof(InvalidProof::AlgorithmMismatch) | Invalid::Proof(InvalidProof::KeyMismatch) => {
            "alg-anahtar-uyusmazligi"
        }
        Invalid::Proof(InvalidProof::Missing) => "istisna-diger",
        Invalid::Proof(InvalidProof::Other(m)) => klass(m),
        Invalid::Claims(InvalidClaims::Expired { .. })
        | Invalid::Claims(InvalidClaims::Premature { .. })
        | Invalid::Claims(InvalidClaims::MissingIssuanceDate) => "zaman",
        Invalid::Claims(InvalidClaims::Other(_)) => "istisna-diger",
    }
}

fn class_pve(err: &ProofValidationError) -> &'static str {
    match err {
        // ssi-jws turns every non-signature failure of verify_bytes (algorithm/key mismatch,
        // unsupported algorithm) into this variant (verification.rs L116-119).
        ProofValidationError::InvalidSignature => "imza-gecersiz",
        ProofValidationError::InvalidInputData(m) if m.contains("unknown variant") => "alg-desteklenmiyor",
        ProofValidationError::InvalidInputData(_) => "ayristirma",
        ProofValidationError::UnknownKey | ProofValidationError::MissingPublicKey => "anahtar-bulunamadi",
        ProofValidationError::InvalidKey | ProofValidationError::InvalidKeyUse => "alg-anahtar-uyusmazligi",
        ProofValidationError::MissingAlgorithm => "alg-desteklenmiyor",
        other => klass(&other.to_string()),
    }
}

struct SsiSdJwt;

impl Target for SsiSdJwt {
    fn id(&self) -> &'static str {
        "SDJWT-025"
    }

    fn api(&self) -> &'static str {
        "sd-jwt-compact: SdJwt::new(p).decode_reveal_verify_any(&VerificationParameters::from_resolver(jwk).with_date_time(simdi)); compact: JwsStr::new(t).to_decoded_jwt().verify(&same params)"
    }

    fn formats(&self) -> &'static [&'static str] {
        // A plain compact JWS is verified through ssi-jwt, the JWT layer ssi-sd-jwt delegates to.
        &["sd-jwt-compact", "compact"]
    }

    fn verify(&self, job: &Job, eff: &str, data: &str, _x: &str) -> Outcome {
        if !matches!(temel(&job.politika), "GEC" | "P0" | "P1" | "P2") {
            // No allow-list, required set or path policy in the API.
            return Outcome::NotExpressible;
        }
        if job.artefakt.starts_with("vp") {
            // No KB-JWT verification entry point (only payload types and SdHash::verify).
            return Outcome::NotExpressible;
        }
        let input = data.trim();
        let jwt = input.split('~').next().unwrap_or(input);
        let header = match jws_header(jwt) {
            Ok(h) => h,
            Err(e) => return reject("ayristirma", e),
        };
        let jwk_value = match keys().jwk_for(&header) {
            Some(j) => j,
            None => return reject("anahtar-bulunamadi", "no key for kid/alg"),
        };
        let jwk: JWK = match serde_json::from_value::<JWK>(jwk_value) {
            Ok(k) => k,
            Err(e) => {
                let m = format!("ssi_jwk::JWK: {e}");
                let class = if m.contains("unknown variant") { "alg-desteklenmiyor" } else { "ayristirma" };
                return reject(class, m);
            }
        };
        let now = DateTime::from_timestamp(SIMDI, 0).expect("valid timestamp");
        let params = VerificationParameters::from_resolver(jwk).with_date_time(now);

        let (alg, verification) = if eff == "sd-jwt-compact" {
            let sd_jwt = match SdJwt::new(input) {
                Ok(s) => s,
                Err(_) => return reject("ayristirma", "ssi_sd_jwt::InvalidSdJwt"),
            };
            match block_on(sd_jwt.decode_reveal_verify_any(&params)) {
                Ok((revealed, v)) => (revealed.jwt.signing_bytes.header.algorithm.to_string(), v),
                Err(e) => return reject(class_pve(&e), format!("ssi: {e}")),
            }
        } else {
            let jws = match JwsStr::new(input) {
                Ok(j) => j,
                Err(_) => return reject("ayristirma", "ssi_jws::InvalidJws"),
            };
            let decoded = match jws.to_decoded_jwt() {
                Ok(d) => d,
                Err(e) => {
                    let pve: ProofValidationError = e.into();
                    return reject(class_pve(&pve), format!("ssi: {pve}"));
                }
            };
            match block_on(decoded.verify(&params)) {
                Ok(v) => (decoded.signing_bytes.header.algorithm.to_string(), v),
                Err(e) => return reject(class_pve(&e), format!("ssi: {e}")),
            }
        };
        match verification {
            Ok(()) => Outcome::Accept(VerifiedAlg::valid(alg)),
            Err(inv) => reject(class_invalid(&inv), format!("ssi: {inv}")),
        }
    }
}

fn main() {
    let sha = sources_sha256(&[include_bytes!("main.rs"), include_bytes!("../../common/adapter_common.rs")]);
    run(Arc::new(SsiSdJwt), env!("TARGET_CRATE_VERSION"), &sha);
}
