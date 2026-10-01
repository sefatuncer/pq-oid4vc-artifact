// Build script shared by the four adapter crates.
//
// Reads `[package.metadata.adapter] target_crate` from Cargo.toml and looks the crate up in
// Cargo.lock, so that the version written to every output line (`hedef_surum`) comes from
// the lock file that was actually built, not from a hand-written constant.
use std::env;
use std::fs;
use std::path::Path;

fn quoted_value(line: &str) -> Option<String> {
    let start = line.find('"')? + 1;
    let end = line[start..].find('"')? + start;
    Some(line[start..end].to_string())
}

fn main() {
    let dir = env::var("CARGO_MANIFEST_DIR").expect("CARGO_MANIFEST_DIR");
    let manifest = fs::read_to_string(Path::new(&dir).join("Cargo.toml")).expect("Cargo.toml");
    let lock = fs::read_to_string(Path::new(&dir).join("Cargo.lock")).expect("Cargo.lock");

    let target = manifest
        .lines()
        .find(|l| l.trim_start().starts_with("target_crate"))
        .and_then(quoted_value)
        .expect("package.metadata.adapter.target_crate");

    let mut version = String::from("?");
    let lines: Vec<&str> = lock.lines().collect();
    for (i, l) in lines.iter().enumerate() {
        if l.trim() == format!("name = \"{}\"", target) {
            if let Some(v) = lines.get(i + 1).and_then(|n| quoted_value(n)) {
                version = v;
            }
            break;
        }
    }

    println!("cargo:rustc-env=TARGET_CRATE_VERSION={}", version);
    println!("cargo:rerun-if-changed=Cargo.lock");
    println!("cargo:rerun-if-changed=Cargo.toml");
}
