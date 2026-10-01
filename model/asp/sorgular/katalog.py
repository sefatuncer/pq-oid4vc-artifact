# -*- coding: utf-8 -*-
"""Sorgu kataloğu (ön kayıt §2C D1′ ile düzenlendi): her sorgu = {id, grup, hedefler, degisen, etiket}.

BİRİNCİL ve ÖNCEDEN BELİRLENMİŞ TASARIMLAR (§2C 2.2, 2.4; (2a)/(2b) yalnız bunlarda sayılır):
  birincil : Q = hedef{g1,g2,g3,g4,tum} × Φ{f1,f2,f3} × τ{10 dk, 3 g, 26 g} × çıpa{taze,sabit,onbellek}
             × politika{p0..p4}; birincil yapılandırma (WebPKI klasik, k sınırsız, ...)          = 675
  h1       : H1 tasarımı — WebPKI{cl,pq} × kanal etiketi varyantı (8) × Q; (cl, birincil) = birincil grup
  h2       : H2′ tasarımı — anahtar kipi {V2,V3} × {durum, ihraççı} × Q  (V1 = birincil)
  h5       : H5 tasarımı — cnf penceresi 1 gün × Q (30 gün = birincil)
  h4       : H4 adlandırılmış hücreleri (Ö3) ve sadakat hücresi (alternatif CA; koordinatör 24.09)
  cab      : §2D m.11 KEŞİFSEL 2×2 ızgara {ca_baglama: ad, anahtar} × {ayni_ad_klasik_ca: yok, var} × Q
             (diger_ca = var, klasik_sabit) + sağlık: ca_baglama = yok × bayrak {yok, var} (diger_ca var/yok)
DUYARLILIK / KEŞİFSEL (kapıyı geçirmez; §2C 2.5):
  oat      : birincilden tek parametre sapması × Q
  tau      : τ duyarlılık ızgarası (Ö8) × Q boyutları (τ hariç)
  a5       : anahtar penceresi × belirteç ömrü × τ geniş ızgarası (Ö1 kanıt ızgarası; ek)
  h        : H0, H3-ön, H5 tek kullanım, mekanizma kancaları (M-g/M-h), politika parametreleri
"""
import itertools
from sorgular.ortak import TAU_NOMINAL, TAU_GENIS, TAU_DUYARLILIK, PENCERE_IZGARA, GUN, YIL

HEDEF5 = ['g1', 'g2', 'g3', 'g4', 'tum']
FAZ = ['f1', 'f2', 'f3']
TAU3 = ['hizli', 'orta', 'yavas']
CAPA = ['taze', 'sabit', 'onbellek']
POL = ['p0', 'p1', 'p2', 'p3', 'p4']


def _Q(grup, onek, ek, etiket_ek, hedefler=HEDEF5, taus=None):
    """Q boyutlarını (hedef × Φ × τ × çıpa × politika) verilen sapmalarla gezer."""
    taus = taus or [(t, TAU_NOMINAL[t]) for t in TAU3]
    for h, f, (tad, tval), c, p in itertools.product(hedefler, FAZ, taus, CAPA, POL):
        d = dict(ek, faz=f, tau=tval, capa=c, politika=p)
        et = dict(etiket_ek, hedef=h, faz=f, tau=tad, capa=c, politika=p)
        yield {'id': '%s|%s|%s|%s|%s|%s' % (onek, h, f, tad, c, p), 'grup': grup, 'hedefler': [h],
               'degisen': d, 'etiket': et}


def birincil():
    yield from _Q('birincil', 'birincil', {}, {'tasarim': 'birincil'})


# H1: kanal etiketi varyantları (§2C 2.4: WebPKI {klasik, PQ} × kanal etiketleri)
H1_KANAL = {
    'birincil': {},
    'durum_aktarilan': {'durum_kanali': 'aktarilan'},          # A08 çevrimdışı aktarım (T166)
    'istek_request_uri': {'istek_iletimi': 'request_uri'},     # A12 sunan-ucundan-çekilen (T284)
    'imzasiz_istek_yok': {'imzasiz_istek_kabul': 'yok'},       # yalnız-taşıma istek varyantı kapalı
    'lotl_webpki': {'lotl_indirme': 'webpki'},                 # LOTL indirme kanalı WebPKI (T002 yerine)
    'tmd_isleniyor': {'tmd_isleme': 'var'},                    # A06 yalnız-taşıma (özet A06 kararıdır)
    'jvi': {'anahtar_cozumleme': 'x5c_jvi'},                   # E_JVI yalnız-taşıma anahtar yolu (T309)
    'imzasiz_meta_yok': {'imzasiz_meta_kabul': 'yok'},         # A05 imzasız biçim kapalı
}


def h1():
    for w in ['cl', 'pq']:
        for kad, kd in H1_KANAL.items():
            if w == 'cl' and kad == 'birincil':
                continue                      # = birincil grup
            yield from _Q('h1', 'h1|%s|%s' % (w, kad), dict(kd, webpki=w), {'tasarim': 'h1', 'webpki': w, 'kanal': kad})


def h2():
    for anahtar in ['durum_anahtari', 'ihracci_anahtari']:
        for kip in ['gunluk', 'gecici']:
            yield from _Q('h2', 'h2|%s|%s' % (anahtar, kip), {anahtar: kip},
                          {'tasarim': 'h2', 'anahtar': anahtar, 'kip': kip})


def h5():
    yield from _Q('h5', 'h5|cnf1g', {'kimlik_gecerlilik': GUN}, {'tasarim': 'h5', 'cnf': '1g'})


def _h(grup, ad, hedefler, **d):
    return {'id': '%s|%s' % (grup, ad), 'grup': grup, 'hedefler': hedefler, 'degisen': d, 'etiket': {'ad': ad}}


def h4():
    """Ö3 adlandırılmış hücreleri: kısa pencereli anahtarlar, G4 ve WebPKI; + sadakat hücresi."""
    Q = []
    for w in ['cl', 'pq']:
        for wr in ['faz0', 'faz1']:
            for f in FAZ:
                for p in ['p0', 'p4']:
                    Q.append(_h('h4', 'G4_imzasiz_istek_%s_%s_%s_%s' % (w, wr, f, p), ['g4'], webpki=w,
                                wrprc_dogrulama=wr, faz=f, politika=p))
    for cb in ['var', 'yok']:
        for f2 in ['klasik', 'pq']:
            for p in ['p0', 'p4']:
                # WRPRC faz1: imzasız-istek yolu (M-b0) RP başına beklentiyle kapatılabilsin ki A.3.2.2 ayrışsın
                Q.append(_h('h4', 'G4_A322_cerceve_bag_%s_f2_%s_%s' % (cb, f2, p), ['g4'], coklu_cerceve='var',
                            cerceve_baglama=cb, f2_rejimi=f2, faz='f3', politika=p, wrprc_dogrulama='faz1'))
    for di in ['ayni_ca', 'farkli_capa']:
        for db in ['siki', 'gevsek']:
            for gd in ['birlesik', 'liste_bagli']:
                Q.append(_h('h4', 'G3_delegasyon_%s_%s_%s' % (di, db, gd), ['g3'], durum_imzaci=di, durum_baglama=db,
                            guven_deposu=gd, faz='f3', politika='p0'))
    for gd in ['birlesik', 'liste_bagli']:
        for tur in ['pid', 'qeaa']:
            for f in FAZ:
                Q.append(_h('h4', 'G1_deposu_%s_%s_%s' % (gd, tur, f), ['g1'], guven_deposu=gd, kimlik_turu=tur,
                            faz=f, politika='p4'))
    for t in TAU3:
        for kg, kad in [(GUN, '1g'), (30 * GUN, '30g')]:
            Q.append(_h('h4', 'G2_cnf%s_%s' % (kad, t), ['g2'], kimlik_gecerlilik=kg, tau=TAU_NOMINAL[t], faz='f3',
                        politika='p0'))
            Q.append(_h('h4', 'tum_cnf%s_%s_f3p4' % (kad, t), ['tum'], kimlik_gecerlilik=kg, tau=TAU_NOMINAL[t],
                        faz='f3', politika='p4'))
        for kip in ['uzun', 'gunluk', 'gecici']:
            Q.append(_h('h4', 'G3_durum_%s_%s' % (kip, t), ['g3'], durum_anahtari=kip, tau=TAU_NOMINAL[t], faz='f3',
                        politika='p0'))
    # Sadakat (model sadakati / bilinen olgu; Ö3; RFC 6840 §6.2, Kim M2): ihraççı zinciri PQ, listede başka
    # (farklı adlı) klasik CA; ca_baglama yok -> G1 çiğnenir, ad -> korunur (Tamarin R1 X_alt_ca[_namebind])
    for cb in ['yok', 'ad']:
        for rej in ['klasik_sabit', 'karar']:
            for f in FAZ:
                Q.append(_h('h4', 'SADAKAT_altCA_G1_cab_%s_%s_%s' % (cb, rej, f), ['g1'], diger_ca='var',
                            ca_baglama=cb, diger_ca_rejimi=rej, faz=f, politika='p4'))
            Q.append(_h('h4', 'SADAKAT_altCA_G4_cab_%s_%s' % (cb, rej), ['g4'], diger_ca='var', ca_baglama=cb,
                        diger_ca_rejimi=rej, faz='f3', politika='p4', wrprc_dogrulama='faz1'))
    return Q


# OAT duyarlılık sapmaları (§2C 2.3 'Duyarlılık' sütunu + modele özgü parametreler)
OAT = {
    'k1': {'k_sinir': 'k1'}, 'k3': {'k_sinir': 'k3'},
    'iptal_denetimi_yok': {'iptal_denetimi': 'yok'}, 'cihaz_bagi_yok': {'cihaz_bagi': 'yok'},
    'rp_auth_fail_open_var': {'rp_auth_fail_open': 'var'}, 'wrprc_faz1': {'wrprc_dogrulama': 'faz1'},
    'ca_baglama_ad': {'ca_baglama': 'ad'}, 'ca_baglama_anahtar': {'ca_baglama': 'anahtar'},
    'ayni_ad_klasik_ca_var': {'ayni_ad_klasik_ca': 'var'}, 'sdjwtvc_s19': {'sdjwtvc_surum': 's19'},
    'w_kok_1y': {'w_kok': YIL}, 'w_ca_1y': {'w_ca': YIL},
    'w_ihracci_30g': {'w_ihracci': 30 * GUN}, 'w_ihracci_180g': {'w_ihracci': 180 * GUN},
    'w_rp_180g': {'w_rp': 180 * GUN}, 'w_tls_47g': {'w_tls': 47 * GUN}, 'w_ka_180g': {'w_ka': 180 * GUN},
    'cnf_180g': {'kimlik_gecerlilik': 180 * GUN}, 'cnf_1y': {'kimlik_gecerlilik': YIL},
    'durum_ttl_1sa': {'durum_ttl': 3600}, 'durum_ttl_7g': {'durum_ttl': 7 * GUN},
    'kbjwt_iat_1dk': {'kbjwt_iat': 60}, 'kbjwt_iat_60dk': {'kbjwt_iat': 3600},
    # modele özgü (§2C tablosunda yok; birincil değer RAPOR §1.5'te gerekçeli)
    'webpki_pq_birlikte': {'webpki': 'pq_birlikte'},
    'guven_deposu_liste_bagli': {'guven_deposu': 'liste_bagli'}, 'kimlik_turu_qeaa': {'kimlik_turu': 'qeaa'},
    'durum_imzaci_farkli_capa': {'durum_imzaci': 'farkli_capa'}, 'durum_baglama_gevsek': {'durum_baglama': 'gevsek'},
    'onbellek_ufku_ilk_pencere': {'onbellek_ufku': 'ilk_pencere'}, 'durum_listesi_yok': {'durum_listesi': 'yok'},
    'cihaz_anahtari_kalici': {'cihaz_anahtari': 'kalici'}, 'wia_anahtari_kalici': {'wia_anahtari': 'kalici'},
    'tek_kullanim_yok': {'tek_kullanim': 'yok'}, 'tek_kullanim_dogrulayici': {'tek_kullanim': 'dogrulayici'},
    'tek_kullanim_kuresel_pasif': {'tek_kullanim': 'kuresel_pasif'}, 'wscd_pq_yok': {'wscd_pq': 'yok'},
    'anahtar_yeniden_kullanim_var': {'anahtar_yeniden_kullanim': 'var'},
    'diger_ca_var': {'diger_ca': 'var'}, 'coklu_cerceve_var': {'coklu_cerceve': 'var'},
    'saat_payi_0': {'saat_payi': 0}, 'saat_payi_60': {'saat_payi': 60}, 'saat_payi_600': {'saat_payi': 600},
    'mekanizma_kancalari_acik': {'mekanizma_kancalari': 'acik'}, 'md_kanca_acik': {'md_kanca': 'acik'},
    'ma_kanca_acik': {'ma_kanca': 'acik'}, 'gun_batimi_iptal': {'gun_batimi': 'iptal'},
}


def oat():
    for ad, d in OAT.items():
        yield from _Q('oat', 'oat|' + ad, d, {'tasarim': 'oat', 'sapma': ad})


def tau_duyarlilik():
    alt = [(('%s_%d' % (r, v)), v) for r, vs in TAU_DUYARLILIK.items() for v in vs if v != TAU_NOMINAL[r]]
    yield from _Q('tau', 'tau', {}, {'tasarim': 'tau'}, taus=alt)


def a5():
    """Ö1 kanıt ızgarası (ek): anahtar penceresi (kip) × belirteç ömrü × τ geniş. Φ3, P0, taze, cl."""
    taban = {'faz': 'f3', 'politika': 'p0', 'capa': 'taze', 'webpki': 'cl'}
    taus = sorted(set(TAU_GENIS) | {v for vs in TAU_DUYARLILIK.values() for v in vs})
    for rej, ttl, tau in itertools.product(['uzun', 'gunluk', 'gecici'], PENCERE_IZGARA, taus):
        d = dict(taban, durum_anahtari=rej, durum_ttl=ttl, tau=tau)
        yield {'id': 'a5|g3|%s|%d|%d' % (rej, ttl, tau), 'grup': 'a5', 'hedefler': ['g3'], 'degisen': d,
               'etiket': {'hedef': 'g3', 'rejim': rej, 'omur': ttl, 'tau': tau}}
    for rej, kg, tau in itertools.product(['uzun', 'gunluk', 'gecici'], PENCERE_IZGARA, taus):
        d = dict(taban, ihracci_anahtari=rej, kimlik_gecerlilik=kg, tau=tau)
        yield {'id': 'a5|g1|%s|%d|%d' % (rej, kg, tau), 'grup': 'a5', 'hedefler': ['g1'], 'degisen': d,
               'etiket': {'hedef': 'g1', 'rejim': rej, 'omur': kg, 'tau': tau}}
    for rej, kg, tau in itertools.product(['kalici', 'kimlik_basi'], PENCERE_IZGARA, taus):
        d = dict(taban, cihaz_anahtari=rej, kimlik_gecerlilik=kg, tau=tau)
        yield {'id': 'a5|g2|%s|%d|%d' % (rej, kg, tau), 'grup': 'a5', 'hedefler': ['g2'], 'degisen': d,
               'etiket': {'hedef': 'g2', 'rejim': rej, 'omur': kg, 'tau': tau}}
    for rej, tau in itertools.product(['wia_basi', 'kalici'], taus):
        d = dict(taban, wia_anahtari=rej, tau=tau)
        yield {'id': 'a5|g2i|%s|%d' % (rej, tau), 'grup': 'a5', 'hedefler': ['g2i'], 'degisen': d,
               'etiket': {'hedef': 'g2i', 'rejim': rej, 'omur': GUN, 'tau': tau}}
    # τ_hızlı ≈ saat payı sınırı (Ö8): küresel tek kullanım + pasif toplayıcı => pencere = KB-JWT iat penceresi
    for pay, tau, iat in itertools.product([0, 60, 300, 600], [60, 84, 600], [60, 300, 600]):
        d = dict(taban, tek_kullanim='kuresel_pasif', saat_payi=pay, tau=tau, kbjwt_iat=iat, durum_listesi='yok')
        yield {'id': 'a5|g2pay|%d|%d|%d' % (pay, tau, iat), 'grup': 'a5', 'hedefler': ['g2'], 'degisen': d,
               'etiket': {'hedef': 'g2', 'rejim': 'kuresel_pasif', 'omur': iat, 'tau': tau, 'saat_payi': pay}}


def adlandirilmis():
    Q = []
    # ---------------- H0 sağlık
    Q.append(_h('h', 'H0_tau_sonsuz_tum_f1_p0', ['tum'], faz='f1', politika='p0', tau=2100000000))
    for f in FAZ:
        Q.append(_h('h', 'H0_S1_%s_p0_tum' % f, ['tum'], faz=f, politika='p0', saldirgan='s1'))
    # ---------------- H3 ön sinyal: G1+G5 politikaya göre (S2 k sınırsız / k1 / S1)
    for pol in POL:
        for f in FAZ:
            Q.append(_h('h', 'H3_g1g5_%s_%s_S2' % (f, pol), ['g1', 'g5'], faz=f, politika=pol))
            Q.append(_h('h', 'H3_g1g5_%s_%s_k1' % (f, pol), ['g1', 'g5'], faz=f, politika=pol, k_sinir='k1'))
            Q.append(_h('h', 'H3_g1g5_%s_%s_S1' % (f, pol), ['g1', 'g5'], faz=f, politika=pol, saldirgan='s1'))
    for f in FAZ:
        for wr in ['faz0', 'faz1']:
            Q.append(_h('h', 'H3_g4_Mb0_%s_%s_p4' % (wr, f), ['g4'], faz=f, politika='p4', wrprc_dogrulama=wr))
    # ---------------- H5 tek kullanım × τ × cnf
    for tk in ['yok', 'cuzdan', 'dogrulayici', 'kuresel_pasif']:
        for kg in [GUN, 30 * GUN]:
            for t in TAU3:
                Q.append(_h('h', 'H5_%s_%d_%s' % (tk, kg, t), ['g2'], tek_kullanim=tk, kimlik_gecerlilik=kg,
                            tau=TAU_NOMINAL[t], faz='f3', politika='p0'))
    # ---------------- R6 KEY_REUSE ve ID_PQ karşılıkları (Tamarin M_rot_reuse, M_rot_id, M_tok_id)
    for kip in ['gunluk', 'gecici']:
        for t in TAU3:
            Q.append(_h('h', 'R6_reuse_%s_%s' % (kip, t), ['g3'], durum_anahtari=kip, anahtar_yeniden_kullanim='var',
                        tau=TAU_NOMINAL[t], faz='f3', politika='p0'))
            Q.append(_h('h', 'R6_ihracci_reuse_%s_%s' % (kip, t), ['g1'], ihracci_anahtari=kip,
                        anahtar_yeniden_kullanim='var', kimlik_gecerlilik=GUN, tau=TAU_NOMINAL[t], faz='f3', politika='p0'))
        # ---------------- Mekanizma kancaları (Adım 7 önizlemesi; Ö2 (i), §2C 3)
    for cb in ['yok', 'ad', 'anahtar']:
        for aa in ['yok', 'var']:
            for f in ['f1', 'f2']:
                Q.append(_h('h', 'MH_altCA_cab_%s_aa_%s_%s' % (cb, aa, f), ['g1'], mekanizma_kancalari='acik',
                            diger_ca='var', ca_baglama=cb, ayni_ad_klasik_ca=aa, faz=f, politika='p4'))
    for f in ['f1', 'f2']:
        Q.append(_h('h', 'MH_jvi_webpkipq_%s' % f, ['g1'], mekanizma_kancalari='acik',
                    anahtar_cozumleme='x5c_jvi', webpki='pq', faz=f, politika='p4'))
    for it in ['qday_oncesi', 'qday_sonrasi']:
        Q.append(_h('h', 'MG_ilk_temas_%s_f2_g1' % it, ['g1'], mekanizma_kancalari='acik', ilk_temas=it, faz='f2',
                    politika='p4'))
        Q.append(_h('h', 'MG_ilk_temas_%s_f2_g4' % it, ['g4'], mekanizma_kancalari='acik', ilk_temas=it, faz='f2',
                    politika='p4'))
    for f in FAZ:
        Q.append(_h('h', 'MD_g1_%s_p4' % f, ['g1'], md_kanca='acik', faz=f, politika='p4'))
        Q.append(_h('h', 'MA_g1_%s_p4' % f, ['g1'], ma_kanca='acik', faz=f, politika='p4'))
    return Q


def cab():
    """§2D m.11: keşifsel 2×2 ızgara + ca_baglama = yok sağlık denetimi (beklentiler: beklenti_2x2.json)."""
    for cb, aa in [('ad', 'yok'), ('ad', 'var'), ('anahtar', 'yok'), ('anahtar', 'var')]:
        yield from _Q('cab', 'cab|%s|%s' % (cb, aa),
                      {'diger_ca': 'var', 'diger_ca_rejimi': 'klasik_sabit', 'ca_baglama': cb, 'ayni_ad_klasik_ca': aa},
                      {'tasarim': 'cab_2x2', 'ca_baglama': cb, 'ayni_ad_klasik_ca': aa})
    for aa in ['yok', 'var']:
        yield from _Q('cab', 'cab|saglik_diger|%s' % aa,
                      {'diger_ca': 'var', 'diger_ca_rejimi': 'klasik_sabit', 'ca_baglama': 'yok', 'ayni_ad_klasik_ca': aa},
                      {'tasarim': 'cab_saglik_diger', 'ca_baglama': 'yok', 'ayni_ad_klasik_ca': aa})
    yield from _Q('cab', 'cab|saglik_birincil|var', {'ca_baglama': 'yok', 'ayni_ad_klasik_ca': 'var'},
                  {'tasarim': 'cab_saglik_birincil', 'ca_baglama': 'yok', 'ayni_ad_klasik_ca': 'var'})


GRUPLAR = {'birincil': birincil, 'h1': h1, 'h2': h2, 'h5': h5, 'h4': h4, 'cab': cab, 'oat': oat,
           'tau': tau_duyarlilik, 'a5': a5, 'h': adlandirilmis}


def hepsi(gruplar=None):
    for g in (gruplar or GRUPLAR):
        yield from GRUPLAR[g]()
