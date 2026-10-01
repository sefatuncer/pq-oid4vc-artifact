#!/usr/bin/env bash
# PyPI hedefi: sanal ortama sabit sürümle kur, pip --report'tan hash'li kilit üret, içe aktarma kontrolü.
# Girdi (kur.sh): PAKET, SURUM, [EKSTRA], /w/ice_aktar.py. İmza doğrulama YOK.
set -uo pipefail
source /b/ortak.sh
: "${PAKET:?}"; : "${SURUM:?}"
SPEC="${PAKET}${EKSTRA:+[$EKSTRA]}==${SURUM}"
yaz ekosistem pypi; yaz paket "$PAKET"; yaz istenen_surum "$SURUM"; [ -n "${EKSTRA:-}" ] && yaz not "ekstra [$EKSTRA]"
python -m venv /tmp/v && . /tmp/v/bin/activate
yaz arac "python $(python --version 2>&1 | cut -d' ' -f2); pip $(pip --version | cut -d' ' -f2)"
echo "== pip install $SPEC"
if ! pip install --no-cache-dir --report "$C/pip-report.json" "$SPEC"; then yaz not "pip install başarısız"; bitir basarisiz 10; fi
python - "$PAKET" <<'PY'
import json, sys, re
r = json.load(open("/w/cikti/pip-report.json"))
norm = lambda s: re.sub(r"[-_.]+", "-", s).lower()
hedef = norm(sys.argv[1]); satirlar = []; kendi = ""
for it in r["install"]:
    md = it["metadata"]; h = it.get("download_info", {}).get("archive_info", {}).get("hashes", {})
    sha = h.get("sha256", "")
    satirlar.append(f'{md["name"]}=={md["version"]} --hash=sha256:{sha}')
    if norm(md["name"]) == hedef:
        kendi = f'sha256:{sha} ({it["download_info"]["url"].rsplit("/",1)[-1]})'
open("/w/cikti/requirements.lock", "w").write("\n".join(sorted(satirlar, key=str.lower)) + "\n")
with open("/w/cikti/sonuc.tsv", "a") as f:
    f.write(f"paket_ozeti\t{kendi}\nbagimlilik_sayisi\t{len(satirlar)}\n")
PY
yaz kilit_dosyasi "requirements.lock (pip --report'tan, --hash'li)"; yaz kilit_sha256 "$(ozet $C/requirements.lock)"
yaz kurulan_surum "$(python -c "import importlib.metadata as m; print(m.version('$PAKET'))")"
yaz lisans_kayit "$(python -c "import importlib.metadata as m; d=m.metadata('$PAKET'); print(d.get('License-Expression') or d.get('License') or '')" | head -1 | cut -c1-60)"
# Ortam olgusu (imza doğrulama değil): cryptography sürümü, gömülü OpenSSL, ML-DSA modülünün varlığı
python - <<'PY' | tee -a /w/cikti/ortam.txt
import importlib.util
try:
    import cryptography
    from cryptography.hazmat.backends.openssl.backend import backend
    ml = importlib.util.find_spec("cryptography.hazmat.primitives.asymmetric.mldsa") is not None
    print(f"ORTAM cryptography {cryptography.__version__}; gömülü {backend.openssl_version_text()}; mldsa_modulu={'var' if ml else 'yok'}")
except ImportError:
    print("ORTAM cryptography kurulu değil")
PY
grep '^ORTAM' $C/ortam.txt | sed 's/^ORTAM /ortam\t/' >> $C/sonuc.tsv
echo "== içe aktarma kontrolü (imza doğrulama YOK)"
if python /w/ice_aktar.py > "$C/ice_aktar.txt" 2>&1; then cat "$C/ice_aktar.txt"; bitir basarili 0
else cat "$C/ice_aktar.txt"; yaz not "içe aktarma hatası"; bitir basarisiz 20; fi
