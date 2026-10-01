#!/usr/bin/env bash
# REF-010 — ACA-Py oid4vc eklentisi: kaynaktan (commit sabit), depodaki poetry.lock ile kurulum.
# Adım 9 görev 4a. İmza doğrulama YOK; çalışma/doğrulayıcı başlatılmaz.
set -uo pipefail
source /b/ortak.sh
DEPO=https://github.com/openwallet-foundation/acapy-plugins
SHA=18c7d1f3c8497e0bc35797d26f3417ce96afeee9
POETRY_SURUM=2.3.2   # kilit dosyasını üreten sürüm (poetry.lock başlığı)
yaz ekosistem "kaynak (git) + poetry.lock"; yaz paket "acapy-plugins/oid4vc"; yaz istenen_surum "git:$SHA"
mkdir -p /tmp/src && cd /tmp/src
if ! { git_anonim init -q . && git_anonim remote add origin "$DEPO.git" && git_anonim fetch -q --depth 1 origin "$SHA" && git_anonim checkout -q FETCH_HEAD; }; then
  yaz sonuc erisilemedi; yaz not "anonim git fetch başarısız"; bitir basarisiz 30; fi
HEAD=$(git rev-parse HEAD); echo "HEAD=$HEAD"
yaz commit "$HEAD"; yaz commit_kaynagi "git checkout (CERCEVE son_commit_sha)"
yaz paket_ozeti "git-tree:$(git rev-parse HEAD:oid4vc) (oid4vc/ alt ağacı)"
cd oid4vc
cp poetry.lock pyproject.toml "$C/"
yaz kilit_dosyasi "oid4vc/poetry.lock (depodaki; Poetry 2.3.2 üretimi)"; yaz kilit_sha256 "$(ozet poetry.lock)"
python -m venv /tmp/pv && /tmp/pv/bin/pip install --no-cache-dir -q --report "$C/poetry-report.json" "poetry==$POETRY_SURUM" || { yaz not "poetry kurulamadı"; bitir basarisiz 11; }
P=/tmp/pv/bin/poetry
yaz arac "python $(python --version 2>&1 | cut -d' ' -f2); $($P --version | tr -d '()')"
$P config virtualenvs.in-project true
echo "== poetry check --lock"; $P check --lock 2>&1 | tee "$C/poetry-check.txt"
echo "== poetry install (extras: aca-py sd_jwt_vc; dev/integration grupları hariç)"
if ! $P install --no-interaction --extras "aca-py sd_jwt_vc" --without dev,integration; then
  yaz not "poetry install başarısız"; bitir basarisiz 10; fi
$P run pip freeze > "$C/pip-freeze.txt"
yaz bagimlilik_sayisi "$(grep -c . "$C/pip-freeze.txt")"
yaz kurulan_surum "git:${HEAD:0:12}"
$P run python - <<'PY' | tee -a "$C/ortam.txt"
import importlib.util, importlib.metadata as md
import cryptography
from cryptography.hazmat.backends.openssl.backend import backend
ml = importlib.util.find_spec("cryptography.hazmat.primitives.asymmetric.mldsa") is not None
print(f"ORTAM acapy-agent {md.version('acapy-agent')}; cryptography {cryptography.__version__}; gömülü {backend.openssl_version_text()}; mldsa_modulu={'var' if ml else 'yok'}")
PY
grep '^ORTAM' "$C/ortam.txt" | sed 's/^ORTAM /environments\t/' >> "$C/sonuc.tsv"
echo "== içe aktarma kontrolü (imza doğrulama YOK)"
if $P run python /w/ice_aktar.py > "$C/ice_aktar.txt" 2>&1; then cat "$C/ice_aktar.txt"; bitir basarili 0
else cat "$C/ice_aktar.txt"; yaz not "içe aktarma hatası"; bitir basarisiz 20; fi
