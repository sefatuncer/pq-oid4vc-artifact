#!/usr/bin/env bash
# _bilgi-JOSE-092-rust_crypto — installation/build pre-test (Step 9 task 4a). NO signature verification.
export KRATE=jsonwebtoken SURUM=11.1.0 OZELLIK=rust_crypto VARSAYILAN=true
exec bash /b/cargo.sh
