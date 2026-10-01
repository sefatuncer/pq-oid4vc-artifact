// Shared runner for the C3 Rust adapters (contract: adaptor-sozlesme 1.0, call format: KOSUCU.md).
//
// Each target crate includes this file with
//     #[path = "../../common/adapter_common.rs"] mod common;
// and supplies one `Target` implementation. The runner reads the job list, resolves the
// verification key the same way as the Python and Go reference adapters (kid, then issuer
// role by alg), calls the target, and writes one JSON line per job.
//
// The adapter never sees the oracle. From the vector manifest nothing is read: keys come
// from /anahtarlar (public JWKS + role table), vectors from /v.
#![allow(dead_code)]

use std::collections::HashMap;
use std::fs;
use std::io::Write;
use std::sync::mpsc::{self, RecvTimeoutError};
use std::sync::{Arc, OnceLock};
use std::time::{Duration, Instant};

use base64::Engine as _;
use serde::Serialize;
use serde_json::Value;
use sha2::{Digest, Sha256};

pub const VECTOR_DIR: &str = "/v";
pub const KEY_DIR: &str = "/anahtarlar";
/// Classical algorithm of every arm (A).
pub const A: &str = "ES256";
/// Issuer identifier of the legacy (not migrated) issuer, as in the reference adapters.
pub const LEGACY_ISS: &str = "https://legacy-issuer.example";
/// Verification time of the battery (`dogrulama_girdileri.simdi`).
pub const SIMDI: i64 = 1_790_003_700;
/// Hard per-vector limit of the runner interface.
pub const VECTOR_TIMEOUT: Duration = Duration::from_secs(60);

/// X of each arm (KOSUCU.md section 1).
pub fn x_of(kol: &str) -> &'static str {
    match kol {
        "kontrol-EdDSA" => "EdDSA",
        "kontrol-Ed25519" => "Ed25519",
        "tedavi-ML-DSA-65" => "ML-DSA-65",
        "tedavi-composite" => "ML-DSA-65-ES256",
        _ => "EdDSA",
    }
}

pub fn b64d(s: &str) -> Result<Vec<u8>, String> {
    base64::engine::general_purpose::URL_SAFE_NO_PAD
        .decode(s.trim_end_matches('='))
        .map_err(|e| format!("base64url: {e}"))
}

/// Protected header of a compact JWS (first segment), decoded only to find the key.
pub fn jws_header(compact: &str) -> Result<Value, String> {
    let first = compact.split('.').next().unwrap_or("");
    let raw = b64d(first)?;
    serde_json::from_slice(&raw).map_err(|e| format!("invalid header JSON: {e}"))
}

/// `iss` of the JWS payload (second segment); None when absent or unreadable.
pub fn payload_iss(compact: &str) -> Option<String> {
    let second = compact.split('.').nth(1)?;
    let raw = b64d(second).ok()?;
    let v: Value = serde_json::from_slice(&raw).ok()?;
    v.get("iss")?.as_str().map(str::to_string)
}

// ---------------------------------------------------------------- keys

pub struct Keys {
    by_kid: HashMap<String, Value>,
    alg_to_kid: HashMap<String, String>,
}

impl Keys {
    fn load() -> Keys {
        let mut by_kid = HashMap::new();
        for f in ["v1/acik-jwks.json", "v1.3/acik-jwks.json"] {
            match read_json(&format!("{KEY_DIR}/{f}")) {
                Ok(v) => {
                    for k in v.get("keys").and_then(Value::as_array).cloned().unwrap_or_default() {
                        if let Some(kid) = k.get("kid").and_then(Value::as_str) {
                            by_kid.insert(kid.to_string(), k.clone());
                        }
                    }
                }
                Err(e) => eprintln!("warning: {e}"),
            }
        }
        // First issuer role per key type wins. Role tables are JSON objects; within the
        // `issuer/` prefix every key type occurs once, so the iteration order does not matter.
        let mut alg_to_kid = HashMap::new();
        for f in ["v1/roller.json", "v1.3/roller.json"] {
            match read_json(&format!("{KEY_DIR}/{f}")) {
                Ok(v) => {
                    if let Some(roles) = v.get("roller").and_then(Value::as_object) {
                        for (role, d) in roles {
                            if !role.starts_with("issuer/") {
                                continue;
                            }
                            if let (Some(t), Some(kid)) = (
                                d.get("tur").and_then(Value::as_str),
                                d.get("kid").and_then(Value::as_str),
                            ) {
                                alg_to_kid.entry(t.to_string()).or_insert_with(|| kid.to_string());
                            }
                        }
                    }
                }
                Err(e) => eprintln!("warning: {e}"),
            }
        }
        Keys { by_kid, alg_to_kid }
    }

    /// Public JWK for a protected header: by `kid`; otherwise the issuer key of the header
    /// `alg` (EdDSA falls back to an Ed25519 role). Same rule as `jwk_for` in the references.
    pub fn jwk_for(&self, header: &Value) -> Option<Value> {
        if let Some(kid) = header.get("kid").and_then(Value::as_str) {
            if let Some(j) = self.by_kid.get(kid) {
                return Some(j.clone());
            }
        }
        let alg = header.get("alg").and_then(Value::as_str).unwrap_or("");
        let a = if self.alg_to_kid.contains_key(alg) {
            alg
        } else if alg == "EdDSA" {
            "Ed25519"
        } else {
            alg
        };
        let kid = self.alg_to_kid.get(a).or_else(|| self.alg_to_kid.get(alg))?;
        self.by_kid.get(kid).cloned()
    }
}

pub fn keys() -> &'static Keys {
    static KEYS: OnceLock<Keys> = OnceLock::new();
    KEYS.get_or_init(Keys::load)
}

fn read_json(path: &str) -> Result<Value, String> {
    let s = fs::read_to_string(path).map_err(|e| format!("{path}: {e}"))?;
    serde_json::from_str(&s).map_err(|e| format!("{path}: {e}"))
}

// ---------------------------------------------------------------- policy

/// Configuration name of a policy: the `|sdjwtvc=...` and `@-19` suffixes only split the
/// expected result on the oracle side.
pub fn temel(pol: &str) -> &str {
    let p = pol.split('|').next().unwrap_or(pol);
    p.split('@').next().unwrap_or(p)
}

/// Permitted algorithm set W (YONTEM.md section 2). For a single-signature compact object
/// R = {X}: a migrated issuer may only use X, the legacy issuer may use A or X.
pub fn allowed(pol: &str, x: &str, iss: Option<&str>, supported: &[&str]) -> Vec<String> {
    let all = || supported.iter().map(|s| s.to_string()).collect::<Vec<_>>();
    match temel(pol) {
        "GEC" | "GEC@-19" | "P0" | "P1" => all(),
        "IZIN-A" => vec![A.to_string()],
        "IZIN-AX" => vec![A.to_string(), x.to_string()],
        "L4" | "L4-S" | "L4-Y" | "L4@-19" | "L4-YOL" => {
            if iss == Some(LEGACY_ISS) {
                vec![A.to_string(), x.to_string()]
            } else {
                vec![x.to_string()]
            }
        }
        _ => all(),
    }
}

/// Fallback classification of an error message (union of the reference adapters' patterns).
/// Targets map their own error types first and only use this for unmapped messages.
pub fn klass(msg: &str) -> &'static str {
    let m = msg.to_lowercase();
    const PATTERNS: &[(&str, &str)] = &[
        ("not allowed", "alg-izin-disi"),
        ("signing method", "alg-izin-disi"),
        ("not supported", "alg-desteklenmiyor"),
        ("unsupported", "alg-desteklenmiyor"),
        ("unknown algorithm", "alg-desteklenmiyor"),
        ("unknown variant", "alg-desteklenmiyor"),
        ("unable to find an algorithm", "alg-desteklenmiyor"),
        ("algorithm not", "alg-desteklenmiyor"),
        ("algorithm mismatch", "alg-anahtar-uyusmazligi"),
        ("asymmetric key", "alg-anahtar-uyusmazligi"),
        ("key is of invalid type", "alg-anahtar-uyusmazligi"),
        ("signature", "imza-gecersiz"),
        ("verification failed", "imza-gecersiz"),
        ("expired", "zaman"),
        ("decode", "ayristirma"),
        ("invalid header", "ayristirma"),
        ("malformed", "ayristirma"),
        ("no key", "anahtar-bulunamadi"),
        ("key", "anahtar-bulunamadi"),
    ];
    for (p, c) in PATTERNS {
        if m.contains(p) {
            return c;
        }
    }
    "istisna-diger"
}

// ---------------------------------------------------------------- target interface

#[derive(Debug, Clone, Default)]
pub struct Job {
    pub vektor_id: String,
    pub politika: String,
    pub kol: String,
    pub dosya: String,
    pub serilestirme: String,
    pub artefakt: String,
    pub algler: String,
}

impl Job {
    fn from_value(v: &Value) -> Job {
        let s = |k: &str| v.get(k).and_then(Value::as_str).unwrap_or("").to_string();
        Job {
            vektor_id: s("vektor_id"),
            politika: s("politika"),
            kol: s("kol"),
            dosya: s("dosya"),
            serilestirme: s("serilestirme"),
            artefakt: s("artefakt"),
            algler: s("algler"),
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct VerifiedAlg {
    pub sira: u32,
    pub alg: String,
    pub sonuc: &'static str,
}

impl VerifiedAlg {
    pub fn valid(alg: impl Into<String>) -> Vec<VerifiedAlg> {
        vec![VerifiedAlg { sira: 0, alg: alg.into(), sonuc: "gecerli" }]
    }
}

pub enum Outcome {
    /// The library accepted the object.
    Accept(Vec<VerifiedAlg>),
    /// The policy cannot be expressed with the library's documented API.
    NotExpressible,
    /// The library (or key conversion before the call) refused the object.
    Reject { class: &'static str, summary: String },
}

pub fn reject(class: &'static str, summary: impl Into<String>) -> Outcome {
    Outcome::Reject { class, summary: summary.into() }
}

pub trait Target: Send + Sync + 'static {
    /// Target identifier (first command-line argument).
    fn id(&self) -> &'static str;
    /// Documented API path, written to `api_yolu`.
    fn api(&self) -> &'static str;
    /// Serialisations decided by API inspection (B6). "compact-as-sdjwt" means a plain
    /// compact JWS is handed to an SD-JWT API with an empty disclosure list ("jws~").
    fn formats(&self) -> &'static [&'static str];
    /// `eff` is the effective serialisation (see `formats`).
    fn verify(&self, job: &Job, eff: &str, data: &str, x: &str) -> Outcome;
}

#[derive(Serialize)]
struct Record<'a> {
    hedef_id: &'a str,
    hedef_surum: &'a str,
    adaptor_sha256: &'a str,
    kosu: &'a str,
    vektor_id: &'a str,
    politika: &'a str,
    kol: &'a str,
    sonuc_ham: Option<&'static str>,
    hata_sinifi: Option<&'static str>,
    hata_ozeti: Option<String>,
    dogrulanan_algoritmalar: Vec<VerifiedAlg>,
    api_yolu: &'a str,
    sure_ms: Option<f64>,
}

fn truncate(s: &str, n: usize) -> String {
    s.chars().take(n).collect()
}

fn panic_text(p: Box<dyn std::any::Any + Send>) -> String {
    if let Some(s) = p.downcast_ref::<&str>() {
        s.to_string()
    } else if let Some(s) = p.downcast_ref::<String>() {
        s.clone()
    } else {
        "panic".to_string()
    }
}

/// SHA-256 over the adapter sources (target main.rs followed by this file).
pub fn sources_sha256(parts: &[&[u8]]) -> String {
    let mut h = Sha256::new();
    for p in parts {
        h.update(p);
    }
    h.finalize().iter().map(|b| format!("{b:02x}")).collect()
}

/// Entry point: `<hedef_id> <isler.jsonl> <cikti.jsonl> <kosu>`.
pub fn run(target: Arc<dyn Target>, version: &str, adapter_sha: &str) {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 5 {
        eprintln!("usage: {} <hedef_id> <isler.jsonl> <cikti.jsonl> <kosu>", args[0]);
        std::process::exit(2);
    }
    let (hid, jobs_path, out_path, kosu) = (&args[1], &args[2], &args[3], &args[4]);
    if hid != target.id() {
        eprintln!("this image serves {} only, got {hid}", target.id());
        std::process::exit(2);
    }
    let jobs_text = match fs::read_to_string(jobs_path) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("{jobs_path}: {e}");
            std::process::exit(2);
        }
    };
    let mut out = match fs::File::create(out_path) {
        Ok(f) => f,
        Err(e) => {
            eprintln!("{out_path}: {e}");
            std::process::exit(2);
        }
    };
    let _ = keys(); // load once before the first job
    let formats = target.formats();

    for line in jobs_text.lines() {
        // Job lists may come with CRLF line ends (and a byte-order mark on the first line).
        let line = line.trim_end_matches('\r').trim_start_matches('\u{feff}').trim();
        if line.is_empty() {
            continue;
        }
        let v: Value = match serde_json::from_str(line) {
            Ok(v) => v,
            Err(e) => {
                eprintln!("skipping unreadable job line: {e}");
                continue;
            }
        };
        let job = Job::from_value(&v);
        let x = x_of(&job.kol);
        let mut rec = Record {
            hedef_id: target.id(),
            hedef_surum: version,
            adaptor_sha256: adapter_sha,
            kosu,
            vektor_id: &job.vektor_id,
            politika: &job.politika,
            kol: &job.kol,
            sonuc_ham: None,
            hata_sinifi: None,
            hata_ozeti: None,
            dogrulanan_algoritmalar: Vec::new(),
            api_yolu: target.api(),
            sure_ms: None,
        };

        let ser = job.serilestirme.as_str();
        let eff = if ser == "compact" && formats.contains(&"compact-as-sdjwt") {
            "compact-as-sdjwt"
        } else {
            ser
        };
        if !formats.contains(&eff) {
            rec.sonuc_ham = Some("uygulanamaz");
            rec.hata_sinifi = Some("bicim-desteklenmiyor");
            write_line(&mut out, &rec);
            continue;
        }

        let data = match fs::read(format!("{VECTOR_DIR}/{}", job.dosya)) {
            Ok(b) => String::from_utf8_lossy(&b).into_owned(),
            Err(e) => {
                rec.sonuc_ham = Some("istisna");
                rec.hata_sinifi = Some("adaptor-hatasi");
                rec.hata_ozeti = Some(truncate(&format!("vector file: {e}"), 200));
                write_line(&mut out, &rec);
                continue;
            }
        };

        // Each vector runs on its own thread so that a panic becomes `cokme` and a hang
        // becomes `zaman-asimi` without stopping the remaining jobs.
        let (tx, rx) = mpsc::channel();
        let t = Arc::clone(&target);
        let (job2, eff2) = (job.clone(), eff.to_string());
        let t0 = Instant::now();
        let spawned = std::thread::Builder::new().stack_size(64 << 20).spawn(move || {
            let r = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                t.verify(&job2, &eff2, &data, x)
            }));
            let _ = tx.send(r.map_err(panic_text));
        });
        if let Err(e) = spawned {
            rec.sonuc_ham = Some("istisna");
            rec.hata_sinifi = Some("adaptor-hatasi");
            rec.hata_ozeti = Some(truncate(&format!("worker thread: {e}"), 200));
            write_line(&mut out, &rec);
            continue;
        }
        match rx.recv_timeout(VECTOR_TIMEOUT) {
            Ok(Ok(Outcome::Accept(algs))) => {
                rec.sonuc_ham = Some("kabul");
                rec.dogrulanan_algoritmalar = algs;
            }
            Ok(Ok(Outcome::NotExpressible)) => rec.sonuc_ham = Some("ifade-edilemedi"),
            Ok(Ok(Outcome::Reject { class, summary })) => {
                rec.sonuc_ham = Some("red");
                rec.hata_sinifi = Some(class);
                rec.hata_ozeti = Some(truncate(&summary, 200));
            }
            Ok(Err(p)) => {
                rec.sonuc_ham = Some("cokme");
                rec.hata_sinifi = Some("cokme");
                rec.hata_ozeti = Some(truncate(&p, 200));
            }
            Err(RecvTimeoutError::Timeout) => {
                rec.sonuc_ham = Some("zaman-asimi");
                rec.hata_sinifi = Some("zaman-asimi");
            }
            Err(RecvTimeoutError::Disconnected) => {
                rec.sonuc_ham = Some("cokme");
                rec.hata_sinifi = Some("cokme");
                rec.hata_ozeti = Some("worker ended without a result".to_string());
            }
        }
        rec.sure_ms = Some((t0.elapsed().as_secs_f64() * 1000.0 * 100.0).round() / 100.0);
        write_line(&mut out, &rec);
    }
    let _ = out.flush();
}

fn write_line(out: &mut fs::File, rec: &Record) {
    let mut s = serde_json::to_string(rec).expect("record serialises");
    s.push('\n');
    if let Err(e) = out.write_all(s.as_bytes()) {
        eprintln!("write failed: {e}");
        std::process::exit(3);
    }
}
