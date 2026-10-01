"""sonuc.json'dan insan okunur Markdown tablo (belirlenimci; tarih/saat içermez)."""
from __future__ import annotations

import math


def _s(x, basamak: int = 4) -> str:
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "evet" if x else "hayır"
    if isinstance(x, int):
        return str(x)
    if isinstance(x, float):
        if math.isnan(x):
            return "tanımsız"
        if math.isinf(x):
            return "∞" if x > 0 else "−∞"
        return f"{x:.{basamak}f}".replace(".", ",").replace("-", "−")
    return str(x)


def _ga(g) -> str:
    if not g:
        return "—"
    return f"[{_s(g[0])}; {_s(g[1])}]"


def _p(p: dict) -> str:
    return f"{_s(p['deger'], 6)} (kesin {p['kesin'] if len(p['kesin']) <= 40 else p['kesin'][:37] + '…'})"


HUKUM = {"destek": "DESTEK", "kirilgan_destek": "KIRILGAN DESTEK", "yanlislama": "YANLIŞLAMA", "kirilgan_yanlislama": "KIRILGAN YANLIŞLAMA",
         "belirsiz": "BELİRSİZ", "tanimlayici": "YALNIZ TANIMLAYICI (n_eff < 20)"}


def markdown(s: dict) -> str:
    L = []
    a = L.append
    g = s["girdi"]
    a("# C3 (H6) istatistik çıktısı")
    a("")
    a(f"- Araç: c3istat {s['arac']['surumler']['c3istat']} · Python {s['arac']['surumler']['python']} · "
      f"numpy {s['arac']['surumler']['numpy']} · scipy {s['arac']['surumler']['scipy']} · "
      f"statsmodels {s['arac']['surumler']['statsmodels']}")
    a(f"- Girdi: `{g['kaynak'].get('dosya', '(sözlük)')}` · SHA-256 `{g['kaynak'].get('sha256', '—')}` · "
      f"veri türü **{g['veri_turu']}** · şema {g['sema_surumu']}")
    iu = s["iki_uygulama"]
    a(f"- İki uygulama (kesin ↔ kütüphane): {iu['uyumlu']} uyumlu + {iu['sinirda']} sınırda / {iu['karsilastirma']}; "
      f"hata {iu['hata']} → **{'GEÇERLİ' if iu['gecerli'] else 'GEÇERSİZ'}**")
    for u in s["orneklem"]["uyarilar"]:
        a(f"- UYARI: {u}")
    a("")
    h = s["H6_hukmu"]
    a(f"## H6 hükmü: **{HUKUM[h['hukum']]}**")
    a("")
    a(f"{h['gerekce']}. Birincil: {h['birincil']}; duyarlılık (i): {h['duyarlilik_i']}.")
    a("")
    a("## T1 (birincil, Holm dışı) ve duyarlılıklar")
    a("")
    a("| Analiz | n_eff | X | c | u | P(X′ ≤ X) | P(X′ ≥ X) | Oran | Wilson %95 GA | Karar |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    satirlar = [("Birincil", s["T1"])] + [
        (ad, s["T1_duyarlilik"][k]) for ad, k in (("(i) belirsiz = 1", "i_belirsiz_1"), ("(ii) belirsiz = 0", "ii_belirsiz_0"),
                                                  ("Pilot hariç", "pilot_haric"), ("Devralan hariç", "devralan_haric"),
                                                  ("Adaptör geçersiz = 0", "gecersiz_y0"))]
    for ad, t in satirlar:
        a(f"| {ad} | {t['n_eff']} | {t['X']} | {_s(t['c'])} | {_s(t['u'])} | {_s(t['p_alt']['deger'], 6)} | "
          f"{_s(t['p_ust']['deger'], 6)} | {_s(t['oran'])} | {_ga(t['wilson'])} | {t['karar']} |")
    a("")
    a("## T2–T5 ve Holm (aile T2–T5, m = 4, α = 0,05)")
    a("")
    a("| Test | Veri | p (ham) | p (Holm) | Holm reddi | Etki büyüklüğü |")
    a("|---|---|---|---|---|---|")
    ho = s["holm"]["sonuclar"]
    t2 = s["T2"]
    e2 = t2["etki"]
    a(f"| T2 McNemar (TK1+TK2) | n_çift = {t2['n_cift']}; b = {t2['b']}, c = {t2['c']} | {_p(t2['p'])} | "
      f"{_s(ho['T2']['p_duzeltilmis']['deger'], 6)} | {_s(ho['T2']['red'])} | "
      f"{'fark ' + _s(e2['fark']) + ' ' + _ga([e2['alt'], e2['ust']]) + ' (Newcombe 10, eşl.)' if e2 else '—'} |")
    for t in ("T3", "T4"):
        b = s[t]
        o = b["or"]
        f = b["fark"]
        a(f"| {t} Fisher | {b['satirlar'][0]} {b['tablo'][0]} / {b['satirlar'][1]} {b['tablo'][1]} | {_p(b['p'])} | "
          f"{_s(ho[t]['p_duzeltilmis']['deger'], 6)} | {_s(ho[t]['red'])} | OR {_s(o['mle'])} "
          f"[{_s(o['alt'])}; {_s(o['ust'])}] (koşullu kesin); "
          f"{'fark ' + _s(f['fark']) + ' ' + _ga([f['alt'], f['ust']]) + ' (Newcombe 10)' if f else 'fark —'} |")
    t5 = s["T5"]
    a(f"| T5 binom (üst) | {t5['X']}/{t5['n']} | {_p(t5['p'])} | {_s(ho['T5']['p_duzeltilmis']['deger'], 6)} | "
      f"{_s(ho['T5']['red'])} | oran {_s(t5['oran'])} {_ga(t5['wilson'])} |")
    a("")
    d2 = s["T2_devralan_haric"]
    a(f"Devralan hariç T2 (tanımlayıcı, Holm dışı): n_çift = {d2['n_cift']}, b = {d2['b']}, c = {d2['c']}, "
      f"p = {_s(d2['p']['deger'], 6)}. TK3 (tanımlayıcı): {s['TK3_tanimlayici']['tablo']}.")
    a("")
    a("## Wilson %95 GA (ÖK §6.8)")
    a("")
    a("| Değişken | Kategori | x/n | Oran | GA |")
    a("|---|---|---|---|---|")
    w = s["wilson"]
    for d in range(6):
        v = w["L_duzeyi"][f"L{d}"]
        a(f"| L düzeyi | L{d} | {v['x']}/{v['n']} | {_s(v['oran'])} | {_ga(v['ga'])} |")
    for d in range(1, 6):
        v = w["L_en_az"][f"L{d}"]
        a(f"| L ≥ k (ek) | L≥{d} | {v['x']}/{v['n']} | {_s(v['oran'])} | {_ga(v['ga'])} |")
    for alan, blok in w["bayraklar"].items():
        for kat, v in blok.items():
            if kat == "n":
                continue
            a(f"| {alan} | {kat} | {v['x']}/{v['n']} | {_s(v['oran'])} | {_ga(v['ga'])} |")
    for bicim in ("L4m", "L4c"):
        v = w["Y_L4_l4_bicimine_gore"][bicim]
        a(f"| Y_L4 | {bicim} | {v['x']}/{v['n']} | {_s(v['oran'])} | {_ga(v['ga'])} |")
    a("")
    a("## Küme bootstrap (ÖK §6.9; B = 10.000; tohum 20260927; yüzdelik tip 7)")
    a("")
    a("| Kapsam | k | Vaka | Oracle'a uymayan oran | %95 GA | Durum |")
    a("|---|---|---|---|---|---|")
    for kapsam, b in s["bootstrap"].items():
        a(f"| {kapsam} | {b['k']} | {b['toplam_vaka']} | {_s(b['tahmin'])} | {_ga([b['alt'], b['ust']]) if b['alt'] is not None else '—'} | {b['durum']} |")
    a("")
    t = s["tanimlayici"]
    a("## Tanımlayıcılar")
    a("")
    a(f"- n = {s['orneklem']['n']}; n_eff (T1) = {s['orneklem']['n_eff']}; adaptör geçersiz: "
      f"{', '.join(x['hedef_id'] for x in s['orneklem']['adaptor_gecersiz']) or 'yok'}; "
      f"Y_L4 belirsiz: {', '.join(s['orneklem']['Y_L4_belirsiz']) or 'yok'}")
    a(f"- Tabaka: {t['tabaka']}; TK: {t['tk_sinifi']}; L4 biçimi: {t['l4_bicimi']}; kontrol etiketi: {t['kontrol_etiketi']}")
    a(f"- Belirsiz nedenleri: {t['belirsiz_nedenleri'] or 'yok'}; kararsız hücre (vaka): {t['kararsiz_hucre_sayisi']}")
    a(f"- B4 satır: {t['B4_satir']}; devralanlar: {t['devralanlar'] or 'yok'}; pilotlar: {t['pilotlar'] or 'yok'}")
    a(f"- REF (n dışı): {[r['hedef_id'] for r in t['REF']] or 'yok'}")
    a("")
    return "\n".join(L) + "\n"
