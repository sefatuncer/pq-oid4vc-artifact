#!/usr/bin/env bash
# JOSE-031 — guardian (RESERVE CANDIDATE; general reserve 5.3-4-ii in place of JOSE-104). Hex package. NO signature verification.
set -uo pipefail
source /b/common.sh
PAKET=guardian; SURUM=2.5.0
yaz ekosistem hex; yaz paket $PAKET; yaz istenen_surum $SURUM
yaz arac "$(elixir --version | tail -1); $(mix hex.info 2>/dev/null | head -1 | tr -s ' ')"
cd /tmp && mix new ortam_deneme >/dev/null && cd ortam_deneme
sed -i "s/# {:dep_from_hexpm, \"~> 0.3.0\"},/{:$PAKET, \"== $SURUM\"},/" mix.exs
grep -n "$PAKET" mix.exs
echo "== mix deps.get"
if ! mix deps.get; then yaz not "mix deps.get başarısız"; bitir basarisiz 10; fi
cp mix.exs mix.lock "$C/"
yaz kilit_dosyasi "mix.lock (Hex iç/dış sağlama toplamları)"; yaz kilit_sha256 "$(ozet mix.lock)"
yaz bagimlilik_sayisi "$(grep -c ':hex,' mix.lock)"
DIS=$(grep "\"$PAKET\": {:hex" mix.lock | grep -oE '"[0-9a-f]{64}"' | tail -1 | tr -d '"')
[ -n "$DIS" ] && yaz paket_ozeti "sha256:$DIS (mix.lock dış sağlama toplamı)"
yaz kurulan_surum "$(grep "\"$PAKET\": {:hex" mix.lock | grep -oE '"[0-9]+\.[0-9]+\.[0-9]+"' | head -1 | tr -d '"')"
yaz lisans_kayit MIT
echo "== mix compile"
if ! mix compile 2>&1; then yaz not "mix compile başarısız"; bitir basarisiz 12; fi
cat > /tmp/kontrol.exs <<'EXS'
# Link check: the modules are loaded (Code.ensure_loaded?); NO verification function is called.
for m <- [Guardian, Guardian.Token.Jwt, JOSE.JWS, JOSE.JWK] do
  IO.puts("modul #{inspect(m)} #{if Code.ensure_loaded?(m), do: "OK", else: "HATA"}")
end
IO.puts("ortam erlang-crypto #{inspect(:crypto.info_lib())}")
{:ok, v} = :application.get_key(:jose, :vsn); IO.puts("bagimlilik jose (erlang-jose) #{v}")
EXS
if mix run --no-start /tmp/kontrol.exs > "$C/import_check.txt" 2>&1 && ! grep -q "HATA" "$C/import_check.txt"; then cat "$C/import_check.txt"; bitir basarili 0
else cat "$C/import_check.txt"; bitir basarisiz 20; fi
