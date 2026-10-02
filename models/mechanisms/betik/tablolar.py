# -*- coding: utf-8 -*-
"""
PQ-OID4VC | Step 7 | result tables (sonuc/karsilastirma.csv -> sonuc/tablolar.md)
Cell format: observed verdict (V/F); "F≠V" (observed≠expected) if it differs from the expectation; a label if not closed.
The script only formats; verdict and expectation are read from karsilastirma.csv.
"""
import csv
import io
import os

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def oku():
    with io.open(os.path.join(KOK, 'sonuc', 'karsilastirma.csv'), encoding='utf-8', newline='') as f:
        return {(r['varyant'], r['lemma']): r for r in csv.DictReader(f)}


def hucre(d, v, l):
    r = d.get((v, l))
    if r is None:
        return '—'
    g, e = r['gozlenen'], r['beklenen']
    if r['uyum'] == 'evet':
        return g
    if r['uyum'] == 'HAYIR':
        return '**%s≠%s**' % (g, e)
    return r['uyum']


def tablo(basliklar, satirlar):
    out = ['| ' + ' | '.join(basliklar) + ' |', '|' + '---|' * len(basliklar)]
    out += ['| ' + ' | '.join(s) + ' |' for s in satirlar]
    return '\n'.join(out)


def main():
    d = oku()
    md = ['# Adım 7 sonuç tabloları (otomatik; `betik/tablolar.py`)', '',
          'Hücre: gözlenen hüküm. **X≠Y**: gözlenen X, çapa 8 beklentisi Y. Exists-trace lemmada V = iz var.', '']
    G5 = ['G5_untimed', 'G5_migrated', 'G5_timed', 'no_rollback', 'first_contact_downgrade']
    md += ['## 1. İstek yönü ve meta veri (G5 biçimleri)', '']
    rows = []
    for v, ad, g in [('MB0_taban', 'M-b0', 'G4_rp_authentication'), ('MA_taban', 'M-a', 'G4_rp_authentication'),
                     ('MB_taban', 'M-b / A.3.2.2', 'G4_rp_authentication'),
                     ('ME_signed_fresh', 'M-e (PQ imzalı, taze)', 'G1_claims_unforgeability'),
                     ('MEP_signed_fresh', 'M-e′ (PQ imzalı, taze)', 'G1_claims_unforgeability'),
                     ('MEP_tls_classical', 'M-e′ (imzasız, klasik TLS)', 'G1_claims_unforgeability'),
                     ('MD_reg_pq', 'M-d (PQ kayıt kanalı)', 'G1_claims_unforgeability')]:
        rows.append([ad, '`%s`' % v] + [hucre(d, v, l) for l in G5] + [hucre(d, v, g), hucre(d, v, 'M_downgrade_s1'),
                                                                     hucre(d, v, 'M_forgery_crqc')])
    md.append(tablo(['Mekanizma', 'Varyant', 'zamansız', 'göç', 'zamanlı', 'NR', 'FCD', 'G1/G4', 'M_downgrade_s1',
                     'M_forgery_crqc'], rows))
    md += ['', '## 2. M-f çekirdeği ve görev 3b (kapsam × saldırı)', '']
    P = ['G5_path_untimed', 'G5_path_migrated', 'G5_path_timed', 'no_rollback_path']
    rows = [['çekirdek (üç saldırı)', '`MF_cekirdek`'] + [hucre(d, 'MF_cekirdek', l) for l in G5[:4]] +
            [hucre(d, 'MF_cekirdek', 'G1_claims_unforgeability')] + [hucre(d, 'MF_cekirdek', l) for l in P] +
            [hucre(d, 'MF_cekirdek', 'M_weak_path_forgery')]]
    for kap, ka in [('yol', 'yol_sinifi'), ('anahtar', 'anahtar'), ('yaprak', 'yaprak_alg')]:
        for sal, sa in [('farkli_ad', 'farklı adlı CA'), ('ayni_ad', 'aynı adlı CA'), ('klasik_kok', 'klasik kök + PQ ara')]:
            v = 'MF_3b_%s_%s' % (kap, sal)
            rows.append(['%s × %s' % (ka, sa), '`%s`' % v] + [hucre(d, v, l) for l in G5[:4]] +
                        [hucre(d, v, 'G1_claims_unforgeability')] + [hucre(d, v, l) for l in P] +
                        [hucre(d, v, 'M_weak_path_forgery')])
    md.append(tablo(['Hücre', 'Varyant', 'G5 zamansız', 'göç', 'zamanlı', 'NR', 'G1', 'yol zamansız', 'yol göç',
                     'yol zamanlı', 'yol NR', 'M_weak_path_forgery'], rows))
    md += ['', '## 3. Taşıyıcı ikamesi (A3-7)', '']
    rows = []
    for v, ad in [('MF_cekirdek', 'TL/LoTE çekilen-güncel'), ('MF_tas_tl_onbellek', 'TL/LoTE önbellek'),
                  ('MF_tas_wrprc_faz0', 'WRPRC faz0'), ('MF_tas_wrprc_faz1', 'WRPRC faz1'),
                  ('MF_tas_federasyon_pq', 'OpenID Federation (PQ ara)'),
                  ('MF_tas_federasyon_klasik_ara', 'OpenID Federation (klasik ara)'),
                  ('MF_tas_federasyon_bayat', 'OpenID Federation (trust_chain/önbellek)'), ('MF_tas_crit_baslik', 'crit başlığı')]:
        rows.append([ad, '`%s`' % v] + [hucre(d, v, l) for l in G5] + [hucre(d, v, 'G1_claims_unforgeability')] +
                    [hucre(d, v, l) for l in P] + [hucre(d, v, 'M_downgrade_s1')])
    md.append(tablo(['Taşıyıcı', 'Varyant', 'zamansız', 'göç', 'zamanlı', 'NR', 'FCD', 'G1', 'yol zamansız', 'yol göç',
                     'yol zamanlı', 'yol NR', 'M_downgrade_s1'], rows))
    md += ['', '## 4. M-h (reddy, vicente) ve görev 3a', '']
    L = ['G1_learned', 'G1_learned_pq', 'G1_learned_pq_genuine', 'no_rollback_path']
    rows = []
    for v, ad in [('MH_reddy_klasik_zincir', 'reddy, klasik zincir (3a-i)'), ('MH_reddy_farkli_ad', 'reddy × farklı adlı CA'),
                  ('MH_reddy_ayni_ad', 'reddy × aynı adlı CA'), ('MH_reddy_klasik_kok', 'reddy × klasik kök'),
                  ('MH_reddy_adbag_farkli_ad', 'reddy + ad bağlama × farklı adlı CA'),
                  ('MH_vicente_klasik_zincir', 'vicente, klasik zincir (3a-i)'), ('MH_vicente_farkli_ad', 'vicente × farklı adlı CA'),
                  ('MH_vicente_ayni_ad', 'vicente × aynı adlı CA'), ('MH_vicente_klasik_kok', 'vicente × klasik kök')]:
        rows.append([ad, '`%s`' % v] + [hucre(d, v, l) for l in G5] + [hucre(d, v, l) for l in L] +
                    [hucre(d, v, 'M_downgrade_s1')])
    md.append(tablo(['Hücre', 'Varyant', 'zamansız', 'göç', 'zamanlı', 'NR', 'FCD', 'G1_learned', 'G1_learned_pq',
                     'G1_learned_pq_genuine', 'no_rollback_path', 'M_downgrade_s1'], rows))
    md += ['', '## 5. EK: M-g (sheffer) zincir politikası okumaları × 3b', '']
    rows = []
    for ok, oa in [('anahtar', 'anahtar PQ'), ('imza', 'imza PQ')]:
        for sal, sa in [('farkli_ad', 'farklı adlı CA'), ('ayni_ad', 'aynı adlı CA'), ('klasik_kok', 'klasik kök')]:
            v = 'EK_mg_%s_%s' % (ok, sal)
            rows.append(['%s × %s' % (oa, sa), '`%s`' % v] + [hucre(d, v, l) for l in G5] +
                        [hucre(d, v, l) for l in ['G1_learned', 'G1_learned_pq', 'no_rollback_path', 'M_cache_cleared']])
    md.append(tablo(['Hücre', 'Varyant', 'zamansız', 'göç', 'zamanlı', 'NR', 'FCD', 'G1_learned', 'G1_learned_pq',
                     'no_rollback_path', 'M_cache_cleared'], rows))
    md += ['', '## 6. EK: yola duyarlı çevrimdışı ek (2 × 2)', '']
    rows = []
    for v, mono, sun in [('EK_mf_r7_tanimlari', 'dar', 'anahtar'), ('EK_mf_monoton_genis', 'geniş', 'anahtar'),
                         ('EK_mf_sunset_beklenti', 'dar', 'beklenti'), ('EK_mf_yola_duyarli', 'geniş', 'beklenti')]:
        rows.append([mono, sun, '`%s`' % v] + [hucre(d, v, l) for l in G5[:4]] + [hucre(d, v, l) for l in P] +
                    [hucre(d, v, 'G1_claims_unforgeability')])
    md.append(tablo(['Tekdüzelik', 'Sunset', 'Varyant', 'zamansız', 'göç', 'zamanlı', 'NR', 'yol zamansız', 'yol göç',
                     'yol zamanlı', 'yol NR', 'G1'], rows))
    with io.open(os.path.join(KOK, 'sonuc', 'tablolar.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(md) + '\n')
    print('sonuc/tablolar.md yazıldı')


if __name__ == '__main__':
    main()
