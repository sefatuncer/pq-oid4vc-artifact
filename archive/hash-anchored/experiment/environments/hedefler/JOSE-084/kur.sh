#!/usr/bin/env bash
# JOSE-084 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export PAKET=python-jose SURUM=3.5.0 EKSTRA=cryptography
exec bash /b/pip.sh
