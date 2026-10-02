#!/usr/bin/env bash
# pq-a09-analiz — Adim 9 gorev 9: imaji kur, sentetik testleri iki kez (iki taze konteynerde) kos,
# ornek sentetik analizi iki kez kos, bit duzeyinde karsilastir, SHA256SUMS uret.
#
# Kullanim (depo kokunden ya da herhangi bir yerden):  bash experiment/statistics/tumunu_calistir.sh [--insa-yok]
# Git Bash (Windows) ve Linux'ta calisir. Konteynerler: pq-a09-analiz-*, hep --rm, --memory=4g, --network none.
# YASAK: docker image/system prune, toplu silme. Bu betik HICBIR imaji ya da konteyneri silmez.
set -euo pipefail

BURASI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAJ="pq-a09-analiz:1.0"
SONUC="$BURASI/sonuclar"
KAYIT="$BURASI/kayit"
mkdir -p "$SONUC" "$KAYIT"

# Windows Git Bash: docker -v icin Windows yolu; MSYS yol donusumunu kapat
yol() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else echo "$1"; fi; }
export MSYS_NO_PATHCONV=1
KOS=(docker run --rm --memory=4g --network none)

echo "== 0. Baslangic imaj listesi"
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | sort > "$KAYIT/docker_images_once.txt"

if [[ "${1:-}" != "--insa-yok" ]]; then
  echo "== 1. Insa: $IMAJ (taban ozetli; pip --require-hashes)"
  docker build -t "$IMAJ" "$(yol "$BURASI")" 2>&1 | tee "$KAYIT/insa.log" | tail -5
fi
docker image inspect "$IMAJ" --format '{{.Id}}' | tee "$KAYIT/imaj_kimligi.txt"
"${KOS[@]}" --name pq-a09-analiz-surum "$IMAJ" python -m c3istat surum > "$KAYIT/surum.json"

echo "== 2. Sentetik testler: iki taze konteyner"
for i in 1 2; do
  rm -rf "$SONUC/test$i"; mkdir -p "$SONUC/test$i"
  "${KOS[@]}" --name "pq-a09-analiz-test$i" -v "$(yol "$SONUC/test$i")":/cikti "$IMAJ" \
    python /opt/c3istat/sentetik-testler/calistir.py --cikti /cikti 2>&1 | tee "$SONUC/test$i/konsol.log" | tail -25
done
cmp "$SONUC/test1/test_ozeti.json" "$SONUC/test2/test_ozeti.json" && echo "test ozetleri bayt-ayni"

echo "== 3. Ornek sentetik girdi (belirlenimci uretec) ve analiz: iki taze konteyner"
rm -rf "$SONUC/ornek_girdi"; mkdir -p "$SONUC/ornek_girdi"
"${KOS[@]}" --name pq-a09-analiz-uret -v "$(yol "$SONUC/ornek_girdi")":/cikti "$IMAJ" \
  python /opt/c3istat/sentetik-testler/ornek_veri_uret.py /cikti
cmp "$SONUC/ornek_girdi/ornek_n31_sentetik.json" "$BURASI/sentetik-testler/data/ornek_n31_sentetik.json" \
  && echo "ornek girdi depodaki kopyayla bayt-ayni"
for i in 1 2; do
  rm -rf "$SONUC/ornek_analiz$i"; mkdir -p "$SONUC/ornek_analiz$i"
  "${KOS[@]}" --name "pq-a09-analiz-kosu$i" -v "$(yol "$SONUC/ornek_girdi")":/girdi:ro \
    -v "$(yol "$SONUC/ornek_analiz$i")":/cikti "$IMAJ" \
    python -m c3istat analiz --girdi /girdi/ornek_n31_sentetik.json --cikti /cikti
done
rm -rf "$SONUC/ornek_analiz_csv"; mkdir -p "$SONUC/ornek_analiz_csv"
"${KOS[@]}" --name pq-a09-analiz-kosucsv -v "$(yol "$SONUC/ornek_girdi")":/girdi:ro \
  -v "$(yol "$SONUC/ornek_analiz_csv")":/cikti "$IMAJ" \
  python -m c3istat analiz --girdi /girdi/ornek_n31_sentetik_hedefler.csv \
    --vakalar /girdi/ornek_n31_sentetik_vakalar.csv --cikti /cikti
for f in sonuc.json sonuc.md karsilastirma.json; do
  cmp "$SONUC/ornek_analiz1/$f" "$SONUC/ornek_analiz2/$f" && echo "$f: iki konteynerde bayt-ayni"
done
( cd "$SONUC" && sha256sum ornek_analiz1/sonuc.json ornek_analiz2/sonuc.json ) | tee "$SONUC/ornek_analiz_sha256.txt"

echo "== 4. SHA256SUMS (dondurulacak dosyalar)"
( cd "$BURASI" && sha256sum Dockerfile tumunu_calistir.sh SCHEMA.md .dockerignore betikler/requirements.txt \
    betikler/c3istat/*.py sentetik-testler/*.py sentetik-testler/data/*.json sentetik-testler/data/*.csv \
    kaynak/NEWCOMBE-SOURCE.md ) > "$BURASI/SHA256SUMS"
cat "$BURASI/SHA256SUMS"

echo "== 5. Bitis imaj listesi (bu betik hicbir imaji silmez)"
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | sort > "$KAYIT/docker_images_sonra.txt"
diff "$KAYIT/docker_images_once.txt" "$KAYIT/docker_images_sonra.txt" || true
