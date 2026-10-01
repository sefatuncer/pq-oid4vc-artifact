# -*- coding: utf-8 -*-
"""PQ-OID4VC Adım 3 — ASP sürücüsünün ortak kısmı (clingo 5.8.2, konteyner pq-a02-solver:1.0).

Kullanım (konteynerde, /work = model/asp):
    from sorgular.ortak import *
    kumeler, sure = asgari_kumeler(parametreler(faz='f2'), ['g1'])

Terimler:
  - parametreler: kategorik p(Ad,Deger) ve sayısal p_sayi(Ad,Deger) olguları.
  - asgari küme: sorgulanan hedef(ler)i sağlayan (pq ∪ tasi) kümelerinin alt küme bakımından en küçükleri
    (clingo --heuristic=Domain --enum-mode=domRec; pilot P2 ile aynı yöntem).
  - sonlu k (Ö8): kırılma senaryoları = ilgili anahtarların min(k,n) elemanlı bütün altkümeleri
    (ihlal, kırılan anahtar kümesinde tekdüze arttığı için daha küçük altkümeler kapsanır).
"""
import itertools, json, os, time
import clingo

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLGU_DOSYALARI = ['olgular/artefaktlar.lp', 'olgular/kenarlar.lp', 'olgular/tasiyicilar.lp',
                  'olgular/pencereler.lp', 'olgular/hedefler.lp', 'olgular/parametreler.lp']
CEKIRDEK = ['cekirdek.lp']

SURE = {'uzun': 157680000, 'gun': 86400}
GUN, YIL = 86400, 31536000
TAU_NOMINAL = {'hizli': 600, 'orta': 259200, 'yavas': 2246400}
TAU_DUYARLILIK = {'hizli': [60, 600, 3600], 'orta': [86400, 259200, 604800, 864000],
                  'yavas': [1209600, 2246400, 5184000]}                      # §2C 2.3 (Ö8)
TAU_GENIS = [84, 600, 3600, 50400, 259200, 864000, 2246400, 4492800, 22809600, 86400000, 2100000000]
PENCERE_IZGARA = [3600, 86400, 604800, 2592000, 15552000, 31536000, 157680000]

# BİRİNCİL YAPILANDIRMA (ön kayıt §2C 2.3; D1′). Tabloda olmayan parametreler için temkinli/spesifikasyon
# varsayılanı (RAPOR §1.5'te gerekçesiyle).
VARSAYILAN = {
    'saldirgan': 's2', 'k_sinir': 'sinirsiz',
    'faz': 'f1', 'capa': 'taze', 'onbellek_ufku': 'kararli', 'webpki': 'cl', 'politika': 'p4',
    'durum_listesi': 'var',
    'ihracci_anahtari': 'uzun', 'durum_anahtari': 'uzun', 'cihaz_anahtari': 'kimlik_basi',
    'wia_anahtari': 'wia_basi', 'tek_kullanim': 'cuzdan',
    'kimlik_turu': 'pid', 'guven_deposu': 'birlesik', 'anahtar_cozumleme': 'x5c', 'lotl_indirme': 'ojeu_sabit',
    'durum_imzaci': 'ayni_ca', 'durum_baglama': 'siki', 'durum_kanali': 'cekilen',
    'istek_iletimi': 'dc_api', 'imzasiz_istek_kabul': 'var', 'imzasiz_meta_kabul': 'var',
    'tmd_isleme': 'yok',
    'iptal_denetimi': 'var', 'cihaz_bagi': 'var', 'rp_auth_fail_open': 'yok', 'wrprc_dogrulama': 'faz0',
    'ca_baglama': 'yok', 'ayni_ad_klasik_ca': 'yok', 'anahtar_yeniden_kullanim': 'yok', 'sdjwtvc_surum': 's13',
    'diger_ca': 'yok', 'diger_ca_rejimi': 'klasik_sabit', 'coklu_cerceve': 'yok', 'cerceve_baglama': 'yok',
    'f2_rejimi': 'klasik', 'wscd_pq': 'var',
    'mekanizma_kancalari': 'kapali', 'md_kanca': 'kapali', 'ma_kanca': 'kapali',
    'ilk_temas': 'qday_sonrasi', 'gun_batimi': 'guven_deposu',
}
SAYISAL_VARSAYILAN = {'tau': TAU_NOMINAL['hizli'], 'saat_payi': 300,
                      'kimlik_gecerlilik': 30 * GUN, 'durum_ttl': GUN, 'kbjwt_iat': 600,
                      'w_kok': 5 * YIL, 'w_ca': 5 * YIL, 'w_ihracci': YIL, 'w_rp': YIL, 'w_tls': YIL,
                      'w_wia': GUN, 'w_ka': YIL}

ANA_HEDEFLER = ['g1', 'g2', 'g3', 'g4']


def parametreler(**degisen):
    """Birincil yapılandırmanın (§2C 2.3) üzerine değişenleri yazar."""
    kat = dict(VARSAYILAN)
    say = dict(SAYISAL_VARSAYILAN)
    for k, v in degisen.items():
        if k in SAYISAL_VARSAYILAN:
            say[k] = int(v)
        elif k in kat:
            kat[k] = v
        else:
            raise KeyError('bilinmeyen parametre: %s' % k)
    return {'kat': kat, 'say': say}


def parametre_olgulari(prm):
    s = ''.join('p(%s,%s).' % (k, v) for k, v in sorted(prm['kat'].items()))
    s += ''.join('p_sayi(%s,%d).' % (k, v) for k, v in sorted(prm['say'].items()))
    return s


def _kontrol(dosyalar, ek, argumanlar):
    ctl = clingo.Control(argumanlar + ['--warn=none'])
    for f in dosyalar:
        ctl.load(os.path.join(KOK, f))
    ctl.add('base', [], ek)
    return ctl


# ---------------------------------------------------------------- ilgili anahtarlar (sonlu k)
ILGILI_PROGRAM = """
ilgili_hedef(G) :- sorgu_hedef(G), hedef_artefakt(G,_).
ilgili_hedef(G) :- sorgu_hedef(tum), ana_hedef(G).
ilgili_hedef(G) :- sorgu_hedef(g5), ana_hedef(G).
ilgili(A) :- ilgili_hedef(G), hedef_etkin(G,A).
ilgili(B) :- ilgili(A), kabul_alti(A,B).
ilgili(Av) :- ilgili(A), varyant(A,Av), mevcut(Av).
ilgili(C) :- ilgili(X), tasiyabilir_etkin(C,X,_).
ilgili(K) :- ilgili(A), tasima_etkin(A,T), tasima_anahtari(T,K).
ilgili(e_crl) :- p(gun_batimi,iptal), ilgili(a12_istek).
anahtar_ilgili(A) :- ilgili(A), imzali(A).
anahtar_ilgili(alt(A)) :- ilgili(A), imzali(A), klasik_alt(A).
anahtar_ilgili(alt(a12_istek)) :- ilgili(a12_istek), p(faz,f3), p(gun_batimi,iptal).
anahtar_ilgili(p3_kanal) :- p(politika,p3).
#show anahtar_ilgili/1.
"""


def ilgili_anahtarlar(prm, hedefler, dosyalar=None):
    ek = parametre_olgulari(prm) + ''.join('sorgu_hedef(%s).' % h for h in hedefler) + ILGILI_PROGRAM
    ctl = _kontrol((dosyalar or OLGU_DOSYALARI) + CEKIRDEK, ek, [])
    ctl.ground([('base', [])])
    anahtarlar = []
    with ctl.solve(yield_=True) as h:
        for m in h:
            anahtarlar = sorted(str(s.arguments[0]) for s in m.symbols(shown=True))
            break
    return anahtarlar


def senaryo_olgulari(prm, hedefler, dosyalar=None):
    """Sonlu k için senaryo(sN) ve kir_izin(sN,K) olguları; sinirsiz/s1 için boş."""
    ks = prm['kat']['k_sinir']
    if prm['kat']['saldirgan'] != 's2' or ks == 'sinirsiz':
        return '', None
    k = {'k1': 1, 'k3': 3}[ks]
    anah = ilgili_anahtarlar(prm, hedefler, dosyalar)
    boy = min(k, len(anah))
    parcalar = []
    for i, alt in enumerate(itertools.combinations(anah, boy)):
        parcalar.append('senaryo(s%d).' % i + ''.join('kir_izin(s%d,%s).' % (i, a) for a in alt))
    return ''.join(parcalar), {'n_anahtar': len(anah), 'n_senaryo': len(parcalar), 'anahtarlar': anah}


# ---------------------------------------------------------------- asgari kümeler
def asgari_kumeler(prm, hedefler, ek='', sinir=0, dosyalar=None):
    """Alt küme bakımından asgari (pq ∪ tasi) kümeleri. Dönüş: (kumeler, bilgi).
    dosyalar: olgu dosyaları (varsayılan: ekosistem; regresyon örnekleri kendi dosyalarını verir)."""
    sen, sbilgi = senaryo_olgulari(prm, hedefler, dosyalar)
    metin = parametre_olgulari(prm) + ''.join('sorgu_hedef(%s).' % h for h in hedefler) + sen + ek
    t0 = time.perf_counter()
    ctl = _kontrol((dosyalar or OLGU_DOSYALARI) + CEKIRDEK + ['secim.lp', 'sorgu.lp'], metin,
                   [str(sinir), '--heuristic=Domain', '--enum-mode=domRec'])
    ctl.ground([('base', [])])
    t1 = time.perf_counter()
    kumeler = []
    sonuc = ctl.solve(on_model=lambda m: kumeler.append(tuple(sorted(str(s) for s in m.symbols(shown=True)))))
    t2 = time.perf_counter()
    kumeler = sorted(set(kumeler))
    bilgi = {'ground_s': round(t1 - t0, 4), 'solve_s': round(t2 - t1, 4), 'sonuc': str(sonuc),
             'n': len(kumeler)}
    if sbilgi:
        bilgi.update({'n_anahtar': sbilgi['n_anahtar'], 'n_senaryo': sbilgi['n_senaryo']})
    return kumeler, bilgi


def pq_sayisi(kume):
    return sum(1 for a in kume if a.startswith('pq('))


# ---------------------------------------------------------------- değerlendirme kipi
DEGERLENDIR_GOSTER = """
#show ihlal/2. #show sahte/2. #show beklenir/2. #show parametre_hatasi/1.
"""


def degerlendir(prm, pq=(), tasi=(), hedefler=('g1', 'g2', 'g3', 'g4'), g5_kapsam=None, ek='', ozel_kirik=None,
                dosyalar=None):
    """Sabit bir (pq, tasi) ataması için bütün senaryolarda ihlal/sahte/beklenir kümelerini döndürür.
    pq: karar DÜĞÜMÜ adları (ekosistem: a01..a13, ecrl, ejvi, eas) ya da regresyon örneklerinde artefakt adları.
    ozel_kirik: verilirse tek senaryo 'r0' kurulur ve yalnız bu anahtarlar kırılabilir
    (anahtar adları: 'a07_kimlik', 'alt(a07_kimlik)', 'p3_kanal'); parametrelerde k_sinir sonlu olmalıdır."""
    if ozel_kirik is not None:
        assert prm['kat']['k_sinir'] != 'sinirsiz' and prm['kat']['saldirgan'] == 's2'
        sen = 'senaryo(r0).' + ''.join('kir_izin(r0,%s).' % k for k in sorted(ozel_kirik))
    else:
        sen, _ = senaryo_olgulari(prm, list(hedefler), dosyalar)
    metin = parametre_olgulari(prm) + sen + ek
    metin += ''.join('pqd(%s).' % a for a in pq) + ''.join('tasi(%s,%s).' % ct for ct in tasi)
    for g in (g5_kapsam if g5_kapsam is not None else hedefler):
        if g in ANA_HEDEFLER:
            metin += 'g5_degerlendir(%s).' % g
    metin += DEGERLENDIR_GOSTER
    ctl = _kontrol((dosyalar or OLGU_DOSYALARI) + CEKIRDEK, metin, [])
    ctl.ground([('base', [])])
    sonuc = {'ihlal': set(), 'sahte': set(), 'beklenir': set(), 'hata': set()}
    with ctl.solve(yield_=True) as h:
        n = 0
        for m in h:
            n += 1
            for s in m.symbols(shown=True):
                if s.name == 'ihlal':
                    sonuc['ihlal'].add((str(s.arguments[0]), str(s.arguments[1])))
                elif s.name == 'sahte':
                    sonuc['sahte'].add((str(s.arguments[0]), str(s.arguments[1])))
                elif s.name == 'beklenir':
                    sonuc['beklenir'].add((str(s.arguments[0]), str(s.arguments[1])))
                elif s.name == 'parametre_hatasi':
                    sonuc['hata'].add(str(s.arguments[0]))
        assert n == 1, 'değerlendirme kipinde tek cevap kümesi beklenir (bulunan: %d)' % n
    if sonuc['hata']:
        raise ValueError('parametre hatası: %s' % sonuc['hata'])
    return sonuc


def ihlal_eden_hedefler(sonuc):
    return sorted({g for (_, g) in sonuc['ihlal']})


def kaydet_json(yol, veri):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, 'w', encoding='utf-8') as f:
        json.dump(veri, f, ensure_ascii=False, indent=1, sort_keys=True)
