# -*- coding: utf-8 -*-
"""Tamarin R1–R5 datalog eşdeğerliği (44 güvenlik hükmü) — sistem modelinin çekirdeğiyle.

Girdi (salt okunur): ../tamarin/sonuc/datalog_uyum.csv (Tamarin hükümleri), ../tamarin/betik/varyantlar.tsv.
Her (kural, varyant, bayraklar) için Tamarin modelinin yapısı, SİSTEM çekirdeğinin olgu biçimine çevrilir
(regresyon/tamarin_datalog/ornekler/*.lp) ve cekirdek.lp ile (ASP), z3 kodlamasıyla ve Jacobi
değerlendiricisiyle değerlendirilir. Zaman: Tamarin'de τ=0 ve pencere sınırsız (R6 kapsam dışı) =>
her örnek artefaktın penceresi 'sonsuz', τ = 600 s. Kanal: Dolev–Yao her iletiyi taşır => 'aktarilan'.
Ek: 'naif' okuma (yalnız gerçek ebeveyn; alternatif CA kenarı yok) aynı çekirdekle koşulur.
Çıktı: regresyon/sonuc/tamarin_esdegerlik.csv ve .json
"""
import csv, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'z3'))
from sorgular.ortak import parametreler, degerlendir, KOK
from yapi import olgulari_oku
from z3_kodlama import degerlendir_z3
from py_degerlendirici import degerlendir_py

TAMARIN = os.environ.get('TAMARIN_DIZIN', '/tamarin')   # salt okunur bağ (calistir.sh)
ORNEK_DIZIN = os.path.join(KOK, 'regresyon', 'tamarin_datalog', 'ornekler')
BAS = 'sure(uzun,157680000). sure(sonsuz,2000000000).\n'


def art(a, imzali=True, sabit=False, kanal='aktarilan', karar=False):
    s = 'artefakt(%s). sinif(%s,ornek). ' % (a, a)
    s += ('imzali(%s). pencere_sabit(%s,sonsuz). ' % (a, a)) if imzali else 'imzasiz(%s). ' % a
    s += 'kanal(%s,%s). ' % (a, kanal)
    if sabit:
        s += 'sabit(%s). ' % a
    if karar:
        s += 'karar(%s). ' % a
    return s + '\n'


def R1(b, naif=False):
    """kök (sabit) -> ca_cert -> iss_cert -> cred; ALT_CA: aynı kök altında klasik ikinci CA."""
    s = BAS + art('ca_cert', sabit=True) + art('iss_cert') + art('cred')
    s += 'kenar(e1,iss_cert,ca_cert). kenar(e2,cred,iss_cert).\n'
    pq = [x for x, f in [('ca_cert', 'ROOT_PQ'), ('iss_cert', 'CA_PQ'), ('cred', 'ISS_PQ')] if f in b]
    if 'ALT_CA' in b:
        s += art('alt_ca_cert', sabit=True) + art('alt_iss')
        s += 'kenar(e3,alt_iss,alt_ca_cert).\n'
        if 'ROOT_PQ' in b:
            pq.append('alt_ca_cert')
        if 'NAME_BIND' not in b and not naif:
            s += 'kenar(e4,cred,alt_iss).   % ad bağlama yok: doğrulayıcı kökün onayladığı HER CA\'nın sertifikasını kabul eder\n'
    s += 'hedef_artefakt(g1,cred). ana_hedef(g1).\n'
    return s, pq, [], 'f3', {'g1'}


def R2(b):
    """göç etmiş ihraççı (klasik + PQ, birlikte yaşama); beklenti: kimliği doğrulanmış yapılandırma | kimliksiz alan | yok."""
    s = BAS + art('cred', sabit=True, karar=True) + 'hedef_artefakt(g1,cred). ana_hedef(g1).\n'
    tasi = []
    if 'EXPECT_AUTH' in b:
        s += art('cfg', imzali=False, kanal='sabitlenmis') + 'tasiyabilir(cfg,cred,m_d).\n'
        tasi.append(('cfg', 'cred'))
    elif 'EXPECT_UNAUTH' in b:
        s += art('net', imzali=False, kanal='kimliksiz') + 'tasiyabilir(net,cred,m_a).\n'
        tasi.append(('net', 'cred'))
    faz = 'f3' if 'NO_COEXIST' in b else 'f1'
    return s, ['cred'], tasi, faz, {'g1', 'g5'}


def R3(b):
    """beklenti kanalı: nesne imzası (chan) ya da taşıma (VIA_TLS: yalnız-taşıma yanıt + kanal anahtarı)."""
    s = BAS + art('cred', sabit=True, karar=True) + 'hedef_artefakt(g1,cred). ana_hedef(g1).\n'
    pq = ['cred']
    if 'VIA_TLS' in b:
        s += art('chan_key', sabit=True) + art('resp', imzali=False, kanal='yalniz_tasima')
        s += 'tasima(resp,t_chan). tasima_anahtari(t_chan,chan_key). tasiyabilir(resp,cred,m_f).\n'
        tasi = [('resp', 'cred')]
        if 'CHAN_PQ' in b:
            pq.append('chan_key')
    else:
        s += art('chan', sabit=True) + 'tasiyabilir(chan,cred,m_f).\n'
        tasi = [('chan', 'cred')]
        if 'CHAN_PQ' in b:
            pq.append('chan')
    return s, pq, tasi, 'f1', {'g1', 'g5'}


def R4(b):
    """cred (ihraççı anahtarı sabit) -> kb (cnf); SINGLE_USE'un karşılığı tek_kullanim (pencereyi değiştirmez: H5)."""
    s = BAS + art('cred', sabit=True) + art('kb') + 'kenar(e1,kb,cred). hedef_artefakt(g2,kb). ana_hedef(g2).\n'
    pq = [x for x, f in [('cred', 'ISS_PQ'), ('kb', 'DEV_PQ')] if f in b]
    return s, pq, [], 'f3', {'g2'}


def R5(b):
    """LOTL (sabit) -> tl -> cred (PQ); PIN_TL: TL anahtarı bant dışı sabit."""
    s = BAS + art('lotl', sabit=True) + art('tl', sabit=('PIN_TL' in b)) + art('cred')
    s += 'kenar(e1,tl,lotl). kenar(e2,cred,tl). hedef_artefakt(g1,cred). ana_hedef(g1).\n'
    pq = ['cred'] + [x for x, f in [('lotl', 'LOTL_PQ'), ('tl', 'TL_PQ')] if f in b]
    return s, pq, [], 'f3', {'g1'}


KURAL = {'R1': R1, 'R2': R2, 'R3': R3, 'R4': R4, 'R5': R5}


def degerlendir3(dosya, pq, tasi, faz, tek_kullanim):
    prm = parametreler(faz=faz, politika='p4', tau=600, tek_kullanim=tek_kullanim)
    goreli = os.path.relpath(dosya, KOK).replace('\\', '/')
    dosyalar = [goreli, 'olgular/parametreler.lp', 'olgular/pencereler.lp']
    hed = ['g1', 'g2']
    a = degerlendir(prm, pq, tasi, hedefler=hed, dosyalar=dosyalar)
    O = olgulari_oku([goreli, 'olgular/parametreler.lp'])
    z = degerlendir_z3(prm, pq, tasi, hedefler=hed, O=O)
    p = degerlendir_py(prm, pq, tasi, hedefler=hed, O=O)
    return {g for (_, g) in a['ihlal']}, z['ihlal'], p['ihlal']


def main():
    os.makedirs(ORNEK_DIZIN, exist_ok=True)
    satirlar = list(csv.DictReader(open(os.path.join(TAMARIN, 'sonuc', 'datalog_uyum.csv'), encoding='utf-8')))
    cikti, uyum, uyum3, naif_fark = [], 0, 0, []
    for r in satirlar:
        bay = set() if r['bayraklar'] == '-' else set(r['bayraklar'].split('+'))
        s, pq, tasi, faz, hedefler = KURAL[r['kural']](bay)
        dosya = os.path.join(ORNEK_DIZIN, '%s__%s.lp' % (r['kural'], r['varyant']))
        with open(dosya, 'w', encoding='utf-8') as f:
            f.write('%% Tamarin %s %s bayraklar=%s (otomatik üretildi: regresyon/tamarin_esdegerlik.py)\n'
                    % (r['kural'], r['varyant'], r['bayraklar']) + s)
        tk = 'dogrulayici' if 'SINGLE_USE' in bay else 'cuzdan'
        a, z, p = degerlendir3(dosya, pq, tasi, faz, tk)
        g = r['hedef']
        tahmin = 'falsified' if g in a else 'verified'
        esit3 = (g in a) == (g in z) == (g in p)
        ok = tahmin == r['tamarin']
        uyum += ok
        uyum3 += esit3
        naif = ''
        if r['kural'] == 'R1':
            s2, pq2, _, _, _ = R1(bay, naif=True)
            dn = os.path.join(ORNEK_DIZIN, 'R1__%s__NAIF.lp' % r['varyant'])
            with open(dn, 'w', encoding='utf-8') as f:
                f.write('% naif okuma: yalnız gerçek ebeveyn (alternatif CA kenarı yok)\n' + s2)
            an, _, _ = degerlendir3(dn, pq2, [], 'f3', 'cuzdan')
            naif = 'falsified' if g in an else 'verified'
            if naif != r['tamarin']:
                naif_fark.append('%s %s' % (r['kural'], r['varyant']))
        cikti.append({'kural': r['kural'], 'varyant': r['varyant'], 'rol': r['rol'], 'bayraklar': r['bayraklar'],
                      'hedef': g, 'tamarin': r['tamarin'], 'sistem_asp': tahmin,
                      'z3': 'falsified' if g in z else 'verified', 'py': 'falsified' if g in p else 'verified',
                      'uyum': 'EVET' if ok else 'HAYIR', 'uclu_esit': 'EVET' if esit3 else 'HAYIR',
                      'naif_sistem': naif, 'eski_datalog_class': r['datalog_tahmini']})
    yol = os.path.join(KOK, 'regresyon', 'sonuc', 'tamarin_esdegerlik.csv')
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(cikti[0].keys()))
        w.writeheader()
        w.writerows(cikti)
    ozet = {'hukum': len(cikti), 'tamarin_ile_uyum': uyum, 'asp_z3_py_esit': uyum3,
            'naif_okuma_uyumsuz': naif_fark, 'varyant': len({(c['kural'], c['varyant']) for c in cikti})}
    json.dump({'ozet': ozet, 'satirlar': cikti}, open(yol.replace('.csv', '.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(json.dumps(ozet, ensure_ascii=False))
    for c in cikti:
        if c['uyum'] != 'EVET' or c['uclu_esit'] != 'EVET':
            print('UYUMSUZ', c)


if __name__ == '__main__':
    main()
