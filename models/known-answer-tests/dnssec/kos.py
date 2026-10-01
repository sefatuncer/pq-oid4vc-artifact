# -*- coding: utf-8 -*-
"""Adım 6 | KAT-1 DNSSEC — ASP koşucusu. TEK ÇEKİRDEK: yalnız /asp/cekirdek.lp + bu klasörün örnek dosyaları.

Yüklenen dosyalar (başka hiçbiri yok): /asp/cekirdek.lp, kat1_dnssec.lp, ornekler/<kosu>.lp.
Okuma kuralı (ESLEME.md §2.5; KAT-SPEC §0 "saldırı var" sorusu): SALDIRI <=> ihlal(tum,g1) tek cevap
kümesinde; aksi YOK. Program tabakalıdır: tam olarak bir cevap kümesi beklenir (denetlenir).
Beklenen değerler: hücrelerde /nsurum/kat_nsurum.tsv 'ilk_ajan' (tek kaynak; ÖK §2H.1), mutasyonlarda
mutasyonlar.tsv 'beklenen' (KAT-SPEC §6). Çekirdeğin SHA-256'sı koşudan önce ve sonra kaydedilir.
Kullanım: ./calistir.sh kos.py   ->  sonuc/asp.csv, sonuc/asp_mutasyon.csv, sonuc/asp_ozet.json
"""
import csv, hashlib, json, os, sys, time
import clingo

KOK = os.path.dirname(os.path.abspath(__file__))
CEKIRDEK = os.environ.get('KAT_CEKIRDEK', '/asp/cekirdek.lp')
NSURUM = os.environ.get('KAT_NSURUM', '/nsurum/kat_nsurum.tsv')
TABAN = ['kat1_dnssec.lp']
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
    """cekirdek + taban + örnek; tek cevap kümesinin atomları."""
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


def oku(A):
    return 'SALDIRI' if 'ihlal(tum,g1)' in A else 'YOK'


def tanik(A):
    """İz/tanık: senaryo 'tum'da sahte artefaktlar, kırılan anahtarlar, etkin beklentiler, M-f geri alma."""
    sec = lambda on: sorted(a for a in A if a.startswith(on))
    return ' '.join(sec('sahte(tum,') + sec('kirilir(tum,') + sec('kirilir_alt(tum,') +
                    sec('beklenir(tum,') + sec('geri_alinir(') + sec('klasik_alt(') + sec('pq('))


def main():
    s_once = sha(CEKIRDEK)
    NS = nsurum()
    os.makedirs(os.path.join(KOK, 'sonuc'), exist_ok=True)
    hucre, mut = [], []
    for r in tablo('hucreler.tsv'):
        if r['motor'] != 'asp':
            continue
        A, t = coz(r['kosu'][:-4] + '.lp')
        g = oku(A)
        b = NS.get((r['nsurum_hucre'], r['nsurum_sutun']), 'YOK_ANAHTAR')
        hucre.append({'kosu': r['kosu'], 'hucre': r['nsurum_hucre'], 'sutun': r['nsurum_sutun'], 'beklenen': b,
                      'gozlenen': g, 'uyum': 'EVET' if g == b else 'HAYIR', 'sure_s': round(t, 4), 'tanik': tanik(A)})
    for r in tablo('mutasyonlar.tsv'):
        if r['motor'] != 'asp':
            continue
        A, t = coz(r['kosu'][:-4] + '.lp')
        g = oku(A)
        mut.append({'kosu': r['kosu'], 'mutasyon': r['mutasyon'], 'temel': r['temel'], 'beklenen': r['beklenen'],
                    'gozlenen': g, 'dondu': 'EVET' if g == r['beklenen'] else 'HAYIR', 'sure_s': round(t, 4),
                    'tanik': tanik(A)})
    s_sonra = sha(CEKIRDEK)
    for ad, satir in (('asp.csv', hucre), ('asp_mutasyon.csv', mut)):
        with open(os.path.join(KOK, 'sonuc', ad), 'w', encoding='utf-8', newline='') as f:
            if satir:
                w = csv.DictWriter(f, fieldnames=list(satir[0].keys()))
                w.writeheader()
                w.writerows(satir)
    ozet = {'kat': 'KAT-1', 'clingo': clingo.__version__, 'cekirdek_sha256_once': s_once,
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
