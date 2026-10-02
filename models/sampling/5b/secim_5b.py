# -*- coding: utf-8 -*-
"""
PQ-OID4VC | Step 5B | selection for the abstraction sampling (PR §4.18)
- Frame: models/asp/sampling/cerceve.jsonl (2442 rows, 189 cells; SHA-256 in the summary file).
- Rule: frame > 200 -> sample stratified by cell; at least 1 from every cell, 200 in total, seed 20260926.
- Deterministic selection (the same method as the technical gate): key = sha256("20260926|<context>|<row_id>").
  In every cell the row with the smallest key (context "5B-hucre:<hucre_id>"); the remaining quota is filled with the rows
  with the smallest key sha256("20260926|5B-tamamlama|<kimlik>").
- Written by the maintainers only. The ASP output fields stay in the row; cevir.py does NOT READ them (blindness rule).
Usage: python models/sampling/5b/secim_5b.py
"""
import hashlib, io, json, os
KOK = os.path.dirname(os.path.abspath(__file__))
CERCEVE = os.path.join(KOK, '..', '..', 'asp', 'sampling', 'cerceve.jsonl')
TOHUM, N = "20260926", 200
anahtar = lambda b, k: hashlib.sha256(f"{TOHUM}|{b}|{k}".encode("utf-8")).hexdigest()
def main():
    raw = io.open(CERCEVE, 'rb').read()
    rows = [json.loads(l) for l in raw.decode('utf-8').splitlines() if l.strip()]
    hucre = {}
    for r in rows: hucre.setdefault(r['hucre_id'], []).append(r)
    secilen = [min(v, key=lambda r: anahtar(f"5B-hucre:{h}", r['satir_id'])) for h, v in sorted(hucre.items())]
    ids = {r['satir_id'] for r in secilen}
    kalan = sorted((r for r in rows if r['satir_id'] not in ids), key=lambda r: anahtar("5B-tamamlama", r['satir_id']))
    secilen += kalan[: max(0, N - len(secilen))]
    out = {"kural": "ÖK §4.18 (Adım 5B; hücre katmanlı, her hücreden ≥1, toplam 200, tohum 20260926)",
           "tohum": TOHUM, "cerceve": {"sha256": hashlib.sha256(raw).hexdigest(), "satir": len(rows), "hucre": len(hucre)},
           "ornek_sayisi": len(secilen),
           "tur_dagilimi": {t: sum(1 for r in secilen if r['tur'] == t) for t in sorted({r['tur'] for r in secilen})},
           "kapi_ornekleri": secilen, "kesif_ornegi (kapı sayımına girmez)": None}
    with io.open(os.path.join(KOK, 'secim.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=False)
    print(json.dumps({k: out[k] for k in ("cerceve", "ornek_sayisi", "tur_dagilimi")}, ensure_ascii=False))
if __name__ == '__main__': main()
