// Evidence-rule second attempt, SDJWT-025 (spruceid ssi, ssi-sd-jwt 0.6.0).
// Own keys and objects only. A = ES256, X = EdDSA (Ed25519).
use std::{borrow::Cow, cell::Cell, collections::HashMap};

use ssi_claims_core::{
    chrono::{DateTime, Utc},
    DateTimeProvider, ProofValidationError, ResolverProvider,
};
use ssi_jwk::{Algorithm, JWKResolver, JWK};
use ssi_jws::{encode_sign_custom_header, Header};
use ssi_sd_jwt::SdJwt;

const MIG: &str = "https://issuer.example";
const LEG: &str = "https://legacy-issuer.example";

/// Documented hook: a JWK resolver. The library passes only the key id.
struct KidResolver {
    keys: HashMap<String, JWK>,
    log: bool,
}
impl JWKResolver for KidResolver {
    async fn fetch_public_jwk(&self, key_id: Option<&str>) -> Result<Cow<'_, JWK>, ProofValidationError> {
        if self.log {
            println!("      resolver called with key_id = {:?} (this is the only input)", key_id);
        }
        key_id
            .and_then(|k| self.keys.get(k))
            .map(Cow::Borrowed)
            .ok_or(ProofValidationError::UnknownKey)
    }
}
struct Params(KidResolver);
impl ResolverProvider for Params {
    type Resolver = KidResolver;
    fn resolver(&self) -> &KidResolver {
        &self.0
    }
}
impl DateTimeProvider for Params {
    fn date_time(&self) -> DateTime<Utc> {
        Utc::now()
    }
}

fn sd_jwt(key: &JWK, alg: Algorithm, kid: &str, iss: &str) -> String {
    let header = Header { algorithm: alg, key_id: Some(kid.to_string()), ..Default::default() };
    let payload = format!(r#"{{"iss":"{iss}","sub":"user-1","_sd_alg":"sha-256"}}"#);
    encode_sign_custom_header(&payload, key, &header).unwrap() + "~"
}
fn corrupt(s: &str) -> String {
    let i = s.rfind('.').unwrap() + 5;
    let c = if &s[i..i + 1] == "A" { "B" } else { "A" };
    format!("{}{}{}", &s[..i], c, &s[i + 1..])
}
fn with_alg(k: &JWK, alg: Option<Algorithm>) -> JWK {
    let mut p = k.to_public();
    p.algorithm = alg;
    p
}

thread_local!(static OK: Cell<u32> = Cell::new(0); static N: Cell<u32> = Cell::new(0));

fn verify(sd: &str, params: &Params) -> (bool, String) {
    let sd = SdJwt::new(sd).unwrap();
    match futures::executor::block_on(sd.decode_reveal_verify_any(params)) {
        Ok((_, Ok(()))) => (true, String::new()),
        Ok((_, Err(invalid))) => (false, format!("invalid: {invalid}")),
        Err(e) => (false, format!("error: {e}")),
    }
}
fn report(label: &str, r: (bool, String), expect: Option<&str>) {
    let res = if r.0 { "accept" } else { "reject" };
    let mut mark = "-";
    if let Some(e) = expect {
        N.with(|n| n.set(n.get() + 1));
        if res == e {
            OK.with(|o| o.set(o.get() + 1));
            mark = "OK";
        } else {
            mark = "MISMATCH";
        }
    }
    let d: String = r.1.chars().take(70).collect();
    println!("{:<54} {:<7} expect={:<7} {:<9} {}", label, res, expect.unwrap_or("-"), mark, d);
}

fn main() {
    println!("== ssi-sd-jwt 0.6.0 / ssi-jws 0.5.0 / ssi-jwk 0.4.0 (features secp256r1, ed25519)");
    let mut mig_es = JWK::generate_p256();
    mig_es.key_id = Some("mig-es256".into());
    let mut mig_x = JWK::generate_ed25519().unwrap();
    mig_x.key_id = Some("mig-eddsa".into());
    let mut leg_es = JWK::generate_p256();
    leg_es.key_id = Some("leg-es256".into());

    let t_mig_es = sd_jwt(&mig_es, Algorithm::ES256, "mig-es256", MIG);
    let t_mig_x = sd_jwt(&mig_x, Algorithm::EdDSA, "mig-eddsa", MIG);
    let t_leg_es = sd_jwt(&leg_es, Algorithm::ES256, "leg-es256", LEG);

    let all = |a_es: Option<Algorithm>, a_x: Option<Algorithm>, a_leg: Option<Algorithm>, log: bool| {
        Params(KidResolver {
            keys: HashMap::from([
                ("mig-es256".to_string(), with_alg(&mig_es, a_es)),
                ("mig-eddsa".to_string(), with_alg(&mig_x, a_x)),
                ("leg-es256".to_string(), with_alg(&leg_es, a_leg)),
            ]),
            log,
        })
    };

    println!("\n== 1. Validity check (one resolver holding the keys of both issuers)");
    let p = all(None, None, None, true);
    report("V+ migrated ES256", verify(&t_mig_es, &p), Some("accept"));
    report("V+ migrated EdDSA", verify(&t_mig_x, &p), Some("accept"));
    report("V+ legacy ES256", verify(&t_leg_es, &p), Some("accept"));
    report("V- migrated EdDSA corrupted", verify(&corrupt(&t_mig_x), &p), Some("reject"));

    println!("\n== 2. Per-key algorithm binding (JWK alg member = the key's own algorithm)");
    let p = all(Some(Algorithm::ES256), Some(Algorithm::EdDSA), Some(Algorithm::ES256), false);
    report("  migrated ES256 (L4c wants reject)", verify(&t_mig_es, &p), Some("reject"));
    report("  migrated EdDSA (L4c wants accept)", verify(&t_mig_x, &p), Some("accept"));
    report("  legacy ES256 (L4c wants accept)", verify(&t_leg_es, &p), Some("accept"));
    // binding works as L3: a key labelled ES256 refuses an object whose header says EdDSA
    let mut relabel = mig_x.clone();
    relabel.key_id = Some("mig-es256".into());
    let t_mismatch = sd_jwt(&relabel, Algorithm::EdDSA, "mig-es256", MIG);
    report("  EdDSA object naming the ES256-bound kid (L3 check)", verify(&t_mismatch, &p), None);

    println!("\n== 3. Paths that reach the L4c decisions only by changing the migrated issuer's key material");
    println!("  (a) resolver withholds the migrated ES256 key");
    let p = Params(KidResolver {
        keys: HashMap::from([
            ("mig-eddsa".to_string(), mig_x.to_public()),
            ("leg-es256".to_string(), leg_es.to_public()),
        ]),
        log: false,
    });
    report("    migrated ES256", verify(&t_mig_es, &p), None);
    report("    migrated EdDSA", verify(&t_mig_x, &p), None);
    report("    legacy ES256", verify(&t_leg_es, &p), None);
    println!("  (b) migrated P-256 key labelled alg=EdDSA (an inconsistent JWK)");
    let p = all(Some(Algorithm::EdDSA), Some(Algorithm::EdDSA), Some(Algorithm::ES256), false);
    report("    migrated ES256", verify(&t_mig_es, &p), None);
    report("    migrated EdDSA", verify(&t_mig_x, &p), None);
    report("    legacy ES256", verify(&t_leg_es, &p), None);
    println!("  -> both remove the migrated ES256 key from use; the record no longer holds it (contract 5.3).");

    println!("\n== 4. Own code after verification (B4 record only): per-issuer check of header alg and iss");
    let p = all(None, None, None, false);
    // BEGIN custom
    let required: HashMap<&str, Vec<Algorithm>> = HashMap::from([(MIG, vec![Algorithm::EdDSA]), (LEG, vec![])]);
    let l4c = |t: &str| -> (bool, String) {
        let (ok, d) = verify(t, &p);
        if !ok {
            return (false, d);
        }
        let jwt = t.split('~').next().unwrap();
        let (header, payload) = ssi_jws::decode_unverified(jwt).unwrap();
        let claims: serde_json::Value = serde_json::from_slice(&payload).unwrap();
        let iss = claims["iss"].as_str().unwrap_or("");
        match required.get(iss) {
            Some(r) if r.is_empty() || r.contains(&header.algorithm) => (true, String::new()),
            _ => (false, format!("alg {} not acceptable for {iss}", header.algorithm)),
        }
    };
    // END custom
    report("  migrated ES256", l4c(&t_mig_es), None);
    report("  migrated EdDSA", l4c(&t_mig_x), None);
    report("  legacy ES256", l4c(&t_leg_es), None);
    println!("  (these decisions come from the own code above, not from a library mechanism)");

    println!("\n== SUMMARY: checked rows OK = {} of {}", OK.with(|o| o.get()), N.with(|n| n.get()));
}
