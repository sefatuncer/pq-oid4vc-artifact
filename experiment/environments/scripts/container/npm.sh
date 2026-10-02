#!/usr/bin/env bash
# npm target: install (version pinned), record the lock file and the integrity digest, import check.
# Input (inside install.sh): PAKET, SURUM, [IGNORE_SCRIPTS=true], /w/import_check.mjs
set -uo pipefail
source /b/common.sh
: "${PAKET:?}"; : "${SURUM:?}"
yaz ekosistem npm; yaz paket "$PAKET"; yaz istenen_surum "$SURUM"
yaz arac "node $(node --version); npm $(npm --version); node-openssl $(node -p process.versions.openssl)"
P=/tmp/proje; rm -rf $P; mkdir -p $P; cd $P
cp /w/import_check.mjs $P/
printf '{"name":"pq-a09-ortam","private":true,"version":"0.0.0","dependencies":{"%s":"%s"}}\n' "$PAKET" "$SURUM" > package.json
echo "== npm install $PAKET@$SURUM (ignore-scripts=${IGNORE_SCRIPTS:-true})"
if ! npm install --save-exact --ignore-scripts="${IGNORE_SCRIPTS:-true}"; then yaz not "npm install başarısız"; bitir basarisiz 10; fi
cp package.json package-lock.json "$C/"
yaz kilit_dosyasi package-lock.json; yaz kilit_sha256 "$(ozet package-lock.json)"
npm ls --all --json > "$C/npm-ls.json" 2>/dev/null || true
yaz bagimlilik_sayisi "$(node -e "const l=require('./package-lock.json');console.log(Object.keys(l.packages).filter(k=>k).length)")"
yaz kurulan_surum "$(node -p "require('./node_modules/$PAKET/package.json').version")"
yaz paket_ozeti "$(node -p "require('./package-lock.json').packages['node_modules/$PAKET'].integrity")"
npm view "$PAKET@$SURUM" gitHead dist.integrity dist.tarball repository.url license --json > "$C/npm-view.json" 2>/dev/null || true
GH=$(node -e "try{const v=require('$C/npm-view.json');console.log(v.gitHead||'')}catch(e){console.log('')}")
[ -n "$GH" ] && { yaz commit "$GH"; yaz commit_kaynagi "npm gitHead"; }
yaz lisans_kayit "$(node -p "require('./node_modules/$PAKET/package.json').license||''")"
echo "== içe aktarma kontrolü (imza doğrulama YOK)"
if node import_check.mjs > "$C/import_check.txt" 2>&1; then cat "$C/import_check.txt"; bitir basarili 0
else cat "$C/import_check.txt"; yaz not "içe aktarma hatası"; bitir basarisiz 20; fi
