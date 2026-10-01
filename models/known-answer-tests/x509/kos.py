# -*- coding: utf-8 -*-
"""Adım 6 | KAT-2 X.509 hibrit — ASP koşucusu. TEK ÇEKİRDEK: yalnız /asp/cekirdek.lp + bu klasörün örnek dosyaları.

Yüklenen dosyalar (başka hiçbiri yok): /asp/cekirdek.lp, kat2_x509.lp, ornekler/<kosu>.lp.
OKUMA KURALLARI (ESLEME.md §3.4; koşumdan ÖNCE sabitlendi):
  saldiri kipi (K2b): SALDIRI <=> ihlal(tum,g1).
  karar kipi (K2a/K2c/K2d): G5 := ihlal(bos,g5) (çekirdek: klasik kanıt, kimliği doğrulanmış PQ beklentisi
    olmadan kabul ediliyor). Etiket (karar_oku):
      G5                                           -> accept_classical
      değilse, Related:  bağlı PQ sertifikası geçerli -> accept_hybrid; 'unknown' -> indeterminate; diğer -> reject
      değilse, diğer:    PQ kanıtı (doğrulayıcının gördüğü) geçerli ve algoritma tanınıyor -> accept_hybrid; diğer -> reject
    'Doğrulayıcının gördüğü geçerlilik': kat_pqev = valid; §6 mutasyonu comp_pq_denetimi_yok'ta composite'in PQ
    bileşeni denetlenmediği için geçerli görülür. 'Tanınıyor': kat_vb != legacy_oid (Kim Tablo IV loud-fail).
Beklenen değerler: /nsurum/kat_nsurum.tsv 'ilk_ajan' (tek kaynak); mutasyonlarda mutasyonlar.tsv 'beklenen'
('accept' = herhangi bir accept_* etiketi; KAT-SPEC §6 "K2a-16 -> accept").
Kullanım: ./calistir.sh kos.py  ->  sonuc/asp.csv, sonuc/asp_mutasyon.csv, sonuc/asp_ozet.json
"""
import csv, hashlib, json, os, re, sys, time
import clingo

KOK = os.path.dirname(os.path.abspath(__file__))
CEKIRDEK = os.environ.get('KAT_CEKIRDEK', '/asp/cekirdek.lp')
NSURUM = os.environ.get('KAT_NSURUM', '/nsurum/kat_nsurum.tsv')
TABAN = ['kat2_x509.lp']
CEKIRDEK_BEKLENEN = 'a32372a7c646274ce672c9586e25b34f75f4febb2f966596cc97e7afb89e0b38'  # commit 45cbd0f


def sha(yol):
    return hashlib.sha256(open(yol, 'rb').read()).hexdigest()


def tablo(ad):
    yol = os.path.join(KOK, ad)
    if not os.path.exists(yol):
        return []
    with open(yol, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def nsurum():
    with open(NSURUM, encoding='utf-8', newline='') as f:
        return {(r['hucre'], r['sutun']): r['ilk_ajan'] for r in csv.DictReader(f, delimiter='\t')}


def coz(ornek):
    ctl = clingo.Control(['--warn=none', '0'])
    for d in [CEKIRDEK] + [os.path.join(KOK, t) for t in TABAN] + [os.path.join(KOK, 'ornekler', ornek)]:
        ctl.load(d)
    t0 = time.time()
    ctl.ground([('base', [])])
    modeller = []
    ctl.solve(on_model=lambda m: modeller.append({str(s) for s in m.symbols(atoms=True)}))
    sure = time.time() - t0
    if len(modeller) != 1:
        raise RuntimeError('%s: %d cevap kümesi (1 bekleniyordu)' % (ornek, len(modeller)))
    A = modeller[0]
    hata = sorted(a for a in A if a.startswith('parametre_hatasi('))
    if hata:
        raise RuntimeError('%s: parametre hatası %s' % (ornek, hata))
    return A, sure


def sabitler(asp_sabitler):
    """'kat_x(y). kat_z(w).' -> {'kat_x': 'y', ...} (yalnız okuma kuralının girdileri için)."""
    return {m.group(1): m.group(2) for m in re.finditer(r'(kat_\w+)\(([^)]*)\)', asp_sabitler)}


def karar_oku(A, s):
    g5 = 'ihlal(bos,g5)' in A
    if g5:
        return 'accept_classical', 'G5'
    if s['kat_sema'] == 'related':
        lb = s['kat_leafb']
        return ('accept_hybrid' if lb == 'valid' else 'indeterminate' if lb == 'unknown' else 'reject'), 'G5 yok'
    gorulen = s['kat_pqev'] == 'valid' or (s['kat_sema'] == 'composite' and s.get('kat_mutasyon') == 'comp_pq_denetimi_yok')
    taniniyor = s['kat_vb'] != 'legacy_oid'
    return ('accept_hybrid' if (gorulen and taniniyor) else 'reject'), 'G5 yok'


def oku(A, s):
    if s['kat_mod'] == 'saldiri':
        return ('SALDIRI' if 'ihlal(tum,g1)' in A else 'YOK'), 'g1'
    return karar_oku(A, s)


def eslesir(gozlenen, beklenen):
    return gozlenen == beklenen or (beklenen == 'accept' and gozlenen.startswith('accept'))


def tanik(A):
    sec = lambda on: sorted(a for a in A if a.startswith(on))
    return ' '.join(sec('ihlal(') + sec('sahte(') + sec('kirilir(') + sec('kirilir_alt(') + sec('beklenir(') +
                    sec('klasik_alt(') + sec('pq(') + sec('tasi('))


def main():
    s_once = sha(CEKIRDEK)
    NS = nsurum()
    os.makedirs(os.path.join(KOK, 'sonuc'), exist_ok=True)
    hucre, mut = [], []
    for r in tablo('hucreler.tsv'):
        if r['motor'] != 'asp':
            continue
        A, t = coz(r['kosu'][:-4] + '.lp')
        g, dayanak = oku(A, sabitler(r['asp_sabitler']))
        b = NS.get((r['nsurum_hucre'], r['nsurum_sutun']), 'YOK_ANAHTAR')
        hucre.append({'kosu': r['kosu'], 'hucre': r['nsurum_hucre'], 'sutun': r['nsurum_sutun'], 'beklenen': b,
                      'gozlenen': g, 'uyum': 'EVET' if g == b else 'HAYIR', 'cekirdek_dayanagi': dayanak,
                      'sure_s': round(t, 4), 'tanik': tanik(A)})
    for r in tablo('mutasyonlar.tsv'):
        if r['motor'] != 'asp':
            continue
        A, t = coz(r['kosu'][:-4] + '.lp')
        g, dayanak = oku(A, sabitler(r['asp_sabitler']))
        mut.append({'kosu': r['kosu'], 'mutasyon': r['mutasyon'], 'temel': r['temel'], 'beklenen': r['beklenen'],
                    'gozlenen': g, 'dondu': 'EVET' if eslesir(g, r['beklenen']) else 'HAYIR',
                    'cekirdek_dayanagi': dayanak, 'sure_s': round(t, 4), 'tanik': tanik(A)})
    s_sonra = sha(CEKIRDEK)
    for ad, satir in (('asp.csv', hucre), ('asp_mutasyon.csv', mut)):
        with open(os.path.join(KOK, 'sonuc', ad), 'w', encoding='utf-8', newline='') as f:
            if satir:
                w = csv.DictWriter(f, fieldnames=list(satir[0].keys()))
                w.writeheader()
                w.writerows(satir)
    ozet = {'kat': 'KAT-2', 'clingo': clingo.__version__, 'cekirdek_sha256_once': s_once,
            'cekirdek_sha256_sonra': s_sonra, 'cekirdek_commit_45cbd0f_ile_ayni': s_once == s_sonra == CEKIRDEK_BEKLENEN,
            'taban_sha256': {t: sha(os.path.join(KOK, t)) for t in TABAN},
            'hucre': len(hucre), 'hucre_uyum': sum(r['uyum'] == 'EVET' for r in hucre),
            'mutasyon_kosusu': len(mut), 'mutasyon_dondu': sum(r['dondu'] == 'EVET' for r in mut),
            'en_uzun_s': max([r['sure_s'] for r in hucre + mut] or [0])}
    json.dump(ozet, open(os.path.join(KOK, 'sonuc', 'asp_ozet.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(ozet, ensure_ascii=False, indent=1))
    for r in hucre:
        if r['uyum'] != 'EVET':
            print('UYUMSUZ', r)
    return 0 if s_once == s_sonra else 3


if __name__ == '__main__':
    sys.exit(main())
