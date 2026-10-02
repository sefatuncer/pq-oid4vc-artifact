#!/usr/bin/env bash
# _bilgi-JOSE-092-rust_crypto — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export KRATE=jsonwebtoken SURUM=11.1.0 OZELLIK=rust_crypto VARSAYILAN=true
exec bash /b/cargo.sh
