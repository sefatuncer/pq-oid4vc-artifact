#!/usr/bin/env bash
# JOSE-092 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export KRATE=jsonwebtoken SURUM=11.1.0 OZELLIK=aws_lc_rs VARSAYILAN=true
exec bash /b/cargo.sh
