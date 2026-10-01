#!/usr/bin/env bash
# JOSE-091 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export KRATE=frank_jwt SURUM=3.1.4 OZELLIK='' VARSAYILAN=true
exec bash /b/cargo.sh
