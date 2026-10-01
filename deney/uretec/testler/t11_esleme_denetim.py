#!/usr/bin/env python3
"""T11 — BATARYA-ESLEME.md <-> ON-KAYIT §6.5 / §4.20 / §2B m.6, m.8 / §2H bagimsiz satir satir denetimi.

Esleme ureticisinden (uretec/esleme.py) AYRI bir ayristirici ile: ÖK §6.5 satirlarinin (K1-K11, V+/V-) icerik ve
oracle karari alintilarinin birebir oldugu, her kol hucresinin dolu ya da gerekceli "—" oldugu, K8 uyarlamasinin D-S1
atifli oldugu, MR1-MR4 tanimlarinin birebir oldugu ve her vektor kimliginin manifestte bulundugu denetlenir.
v1.3 eslemesinde ek olarak: COSE tablosu (K1-K11, V+/V-, MR1-MR4; COSE hucrelerinde yalniz COSE vektorleri, kol
tutarliligi, K11/MR3 gerekceli "—"), K8/K9'un ÖK §2H m.9'a uyarlanmasi, L4c tablosu (ÖK §2B m.6 alintilari; goc etmis
ve eski ihracci vektorlerinin iss degerleri dosyalardan) ve §2H alintilari.
Kullanim: python t11_esleme_denetim.py <ON-KAYIT-TASLAK.md> <BATARYA-ESLEME.md> <MANIFEST.json (v1.2 ya da v1.3)>
"""
import base64
import json
import os
import re
import sys

ok_txt = open(sys.argv[1], encoding='utf-8').read()
es_txt = open(sys.argv[2], encoding='utf-8').read()
man_yol = sys.argv[3]
man = json.load(open(man_yol, encoding='utf-8'))
ids = {v['id'] for v in man['vektorler']}
byid = {v['id']: v for v in man['vektorler']}
V13 = man['surum'] == 'v1.3'
sonuc = []


def kontrol(ad, kosul, ayrinti=''):
    sonuc.append((bool(kosul), ad, ayrinti))


def satirlar(metin, onek=''):
    out = {}
    for line in metin.splitlines():
        m = re.match(r'^\| %s(K\d+|V\+|V−|MR\d) \| ' % re.escape(onek), line)
        if m:
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            out[m.group(1)] = cells[1:]
    return out


def kimlikler(hucre):
    return [v for v in re.findall(r'`([^`]+)`', hucre) if re.match(r'^[A-Z0-9]', v) and '_' in v]


# ÖK §6.5 satirlari (bagimsiz ayristirma)
s65 = ok_txt.split('### 6.5 ', 1)[1].split('### 6.6', 1)[0]
ok_rows = {}
for line in s65.splitlines():
    if line.startswith('| K') or line.startswith('| V+'):
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        ok_rows[cells[0]] = cells[1:]
kontrol('ÖK §6.5 satir sayisi (K1-K11 + V+/V-) = 12', len(ok_rows) == 12, sorted(ok_rows))

# JOSE tablosu: v1.3'te COSE bolumunden onceki kisim
jose_txt = es_txt.split('## 3. COSE', 1)[0] if V13 else es_txt
es_rows = satirlar(jose_txt)
beklenen = ['K%d' % i for i in range(1, 12)] + ['V+', 'V−', 'MR1', 'MR2', 'MR3', 'MR4']


def alinti_ve_hucreler(rows, etiket, izinli_kimlik=None):
    kontrol('%s: tum satirlar var (K1-K11, V+, V-, MR1-MR4)' % etiket, all(r in rows for r in beklenen),
            [r for r in beklenen if r not in rows])
    for k in ['K%d' % i for i in range(1, 12)]:
        icerik, karar = ok_rows[k]
        e = rows[k]
        kontrol('%s %s icerik alintisi birebir' % (etiket, k), e[0] == icerik, (e[0], icerik))
        kontrol('%s %s oracle karari alintisi birebir' % (etiket, k), e[1] == karar, (e[1], karar))
    v_icerik, v_karar = ok_rows['V+ / V−']
    for k, parca in (('V+', 'KABUL'), ('V−', 'RED')):
        e = rows[k]
        kontrol('%s %s icerik ÖK metnini iceriyor' % (etiket, k), e[0].startswith(v_icerik), (e[0], v_icerik))
        kontrol('%s %s karar: %s ve ÖK alintisi "%s"' % (etiket, k, parca, v_karar), e[1].startswith(parca) and v_karar in e[1],
                e[1])
    for r in beklenen:
        kolon = rows[r][-3:]
        for i, c in enumerate(kolon):
            dolu = ('birincil' in c) or ('↔' in c) or ('(-13 ↔ -19)' in c)
            gerekce = c.startswith('—') and (('uygulanamaz' in c) or ('kol-bağımsız' in c))
            kontrol('%s %s kol %d hucresi dolu ya da gerekceli' % (etiket, r, i + 1), dolu or gerekce, c[:90])
            for vid in kimlikler(c):
                kontrol('%s %s kimlik manifestte: %s' % (etiket, r, vid), vid in ids)
                if izinli_kimlik is not None and not c.startswith('—'):
                    kontrol('%s %s kol %d kimligi bu tabakaya ve kola ait: %s' % (etiket, r, i + 1, vid),
                            izinli_kimlik(vid, i), byid.get(vid, {}).get('kol'))


alinti_ve_hucreler(es_rows, 'JOSE' if V13 else 'Esleme')

# K8 uyarlamasi D-S1'e atifli
k8 = es_rows['K8']
if V13:
    for k in ('K8', 'K9'):
        c = es_rows[k]
        kontrol('JOSE %s kontrol ve composite hucreleri "—" kol-bağımsız + ÖK §2H m.9' % k,
                all(x.startswith('—') and 'kol-bağımsız' in x and '§2H m.9' in x for x in (c[-3], c[-1])), (c[-3][:80], c[-1][:80]))
    kontrol('JOSE K8 ML-DSA hucresi X5C04 birincil + UYARLANMIŞ + D-S1 + HAIP §6.1.1 sapmasi',
            '**birincil:** `X5C04_karisik_pq_yaprak_klasik_ara`' in k8[-2] and 'UYARLANMIŞ' in k8[-2] and 'D-S1' in k8[-2]
            and 'HAIP §6.1.1' in k8[-2])
    kontrol('JOSE K9 ML-DSA hucresi X5C07 birincil', '**birincil:** `X5C07_korumasiz_x5c`' in es_rows['K9'][-2])
else:
    kontrol('K8 composite hucresi UYARLANMIŞ + D-S1 + HAIP §6.1.1 sapmasi', 'UYARLANMIŞ' in k8[-1] and 'D-S1' in k8[-1] and
            'HAIP §6.1.1' in k8[-1], k8[-1])
    kontrol('K8 ML-DSA hucresi X5C04 birincil', '**birincil:** `X5C04_karisik_pq_yaprak_klasik_ara`' in k8[-2])
    kontrol('K8 kontrol hucresi gerekceli (D-S1)', k8[-3].startswith('—') and 'D-S1' in k8[-3])
kontrol('Durustluk notunda K8 uyarlamasi D-S1 atifli', '**K8 uyarlanmış (D-S1):**' in es_txt)
# K6/K7 yalniz composite
for k in ('K6', 'K7'):
    kontrol('%s kontrol ve ML-DSA hucreleri uygulanamaz (gerekceli)' % k,
            all(c.startswith('—') and 'uygulanamaz' in c for c in es_rows[k][-3:-1]))
    kontrol('%s composite hucresi dolu' % k, 'birincil' in es_rows[k][-1])
# MR tanimlari birebir
s420 = ok_txt.split('### 4.20 Oracle', 1)[1].split('### 4.21', 1)[0]
mr_ok = {k: re.search(r'^\s*- %s: (.*)$' % k, s420, re.M).group(1).strip() for k in ('MR1', 'MR2', 'MR3')}
mr_ok['MR4'] = re.search(r'\*\*Metamorfik ilişki MR4\*\* \([^)]*\): (.*)$', ok_txt, re.M).group(1).strip()
for k in ('MR1', 'MR2', 'MR3'):
    kontrol('%s tanimi ÖK §4.20 ile birebir' % k, es_rows[k][0] == mr_ok[k], (es_rows[k][0], mr_ok[k]))
kontrol('MR4 tanimi ÖK §2B m.8 ile birebir', es_rows['MR4'][0] == mr_ok['MR4'], (es_rows['MR4'][0], mr_ok['MR4']))
# MR cift beklentileri
kontrol('MR1: her kolda T1 <-> T3', all('`T1%s_both_valid` ↔ `T3_stripped_to_ES256`' % a in c
                                        for a, c in zip('KPC', es_rows['MR1'][-3:])))
kontrol('MR2: her kolda T1 <-> T7 (birincil) ve T1 <-> T4', all('`T1%s_both_valid` ↔ `T7%s_plus_kayitsiz`' % (a, a) in c and
                                                               '`T1%s_both_valid` ↔ `T4%s_plus_' % (a, a) in c
                                                               for a, c in zip('KPC', es_rows['MR2'][-3:])))
kontrol('MR3: -13/-19 ve VC11 her kolda', all('(-13 ↔ -19)' in c and '`VC11_typ_vc+sd-jwt`' in c for c in es_rows['MR3'][-3:]))
kontrol('MR4: her kolda en az bir -SIRA- cifti', all('-SIRA-' in c for c in es_rows['MR4'][-3:]))
kontrol('VP05 MR4 disi tanimlayici notu', 'MR4 dışı, tanımlayıcı' in es_txt and 'VP05_GJ_ES256_MLDSA65_kb-SIRA-ters' in es_txt)
# ÖK politika ve senaryo alintisi
pol = re.search(r'\*\*Politika:\*\* (.*)', s65).group(1).strip()
kontrol('Politika alintisi birebir', pol in es_txt, pol)
for sat in re.search(r'\*\*Senaryo etiketleri.*?\*\*\s*\n(.*?)\n\n', s65, re.S).group(1).strip().splitlines():
    kontrol('Senaryo satiri birebir: ' + sat[:40], sat in es_txt)

if V13:
    # ------------------------------------------------------------ COSE tablosu
    cose_txt = es_txt.split('## 3. COSE', 1)[1].split('## 4. L4c', 1)[0]
    c_rows = satirlar(cose_txt, 'COSE ')
    KOL_IZIN = [{'kontrol-EdDSA', 'kontrol-Ed25519', 'ortak'}, {'tedavi-ML-DSA-65', 'ortak'}, {'tedavi-composite', 'ortak'}]
    alinti_ve_hucreler(c_rows, 'COSE', lambda vid, i: vid.startswith('COSE-') and byid.get(vid, {}).get('artefakt') == 'cose'
                       and byid[vid]['kol'] in KOL_IZIN[i])
    for k in ('K6', 'K7'):
        kontrol('COSE %s yalniz composite (diger hucreler uygulanamaz)' % k,
                all(c.startswith('—') and 'uygulanamaz' in c for c in c_rows[k][-3:-1]) and 'birincil' in c_rows[k][-1])
    for k in ('K8', 'K9'):
        c = c_rows[k]
        kontrol('COSE %s yalniz ML-DSA-65 sutununda birincil; kontrol/composite "—" §2H m.9' % k,
                'birincil' in c[-2] and all(x.startswith('—') and '§2H m.9' in x for x in (c[-3], c[-1])))
    kontrol('COSE K8 karisik x5chain korumali; K9 korumasiz (manifest insa)',
            byid['COSE-K8_x5chain_karisik']['insa']['x5chain']['sinif'] == 'karisik' and
            byid['COSE-K8_x5chain_karisik']['insa']['x5chain']['korumali'] is True and
            byid['COSE-K9_x5chain_korumasiz']['insa']['x5chain']['korumali'] is False)
    kontrol('COSE K11 her kolda gerekceli "uygulanamaz"', all(c.startswith('—') and 'uygulanamaz' in c for c in c_rows['K11'][-3:]))
    kontrol('COSE MR3 her kolda gerekceli "uygulanamaz"', all(c.startswith('—') and 'uygulanamaz' in c for c in c_rows['MR3'][-3:]))
    for kod in ('MR1', 'MR2', 'MR4'):
        kontrol('COSE %s tanimi ÖK ile birebir' % kod, c_rows[kod][0] == mr_ok[kod], c_rows[kod][0][:80])
    kontrol('COSE MR1: her kolda K1 <-> K3', all('`COSE-K1%s_iki_gecerli` ↔ `COSE-K3_X_soyuldu`' % a in c
                                                 for a, c in zip('KPC', c_rows['MR1'][-3:])))
    kontrol('COSE MR2: her kolda K1 <-> K5', all('`COSE-K1%s_iki_gecerli` ↔ `COSE-K5%s_arti_kayitsiz`' % (a, a) in c
                                                 for a, c in zip('KPC', c_rows['MR2'][-3:])))
    kontrol('COSE MR4: her kolda K1 ve K2 -SIRA-ters ciftleri', all(
        '`COSE-K1%s_iki_gecerli` ↔ `COSE-K1%s_iki_gecerli-SIRA-ters`' % (a, a) in c and
        '`COSE-K2%s_X_bozuk` ↔ `COSE-K2%s_X_bozuk-SIRA-ters`' % (a, a) in c for a, c in zip('KPC', c_rows['MR4'][-3:])))
    kontrol('COSE MR4 kontrol yedekleri (-ED25519) var', '`COSE-K1K_iki_gecerli-SIRA-ters-ED25519`' in c_rows['MR4'][-3] and
            '`COSE-K2K_X_bozuk-SIRA-ters-ED25519`' in c_rows['MR4'][-3])
    for vid in [v for v in ids if v.startswith('COSE-') and v.endswith('-ED25519')]:
        kontrol('COSE Ed25519 esi eslemede yedek olarak geciyor: %s' % vid, ('[yedek: `%s`' % vid in cose_txt) or
                ('↔ `%s`]' % vid in cose_txt))
    # ------------------------------------------------------------ L4c
    l4_txt = es_txt.split('## 4. L4c', 1)[1].split('## 5.', 1)[0]
    l4_ok = re.search(r'^\s*- \*\*L4c \(yalnız kompakt serileştirme destekleyen hedefler\):\*\* (.*)$', ok_txt, re.M).group(1).strip()
    yi_ok = re.search(r'^\s*- \*\*Y_i\*\* = (.*)$', ok_txt, re.M).group(1).strip()
    kontrol('L4c tanimi ÖK §2B m.6 ile birebir', '**L4c (alıntı):** ' + l4_ok in l4_txt)
    kontrol('Y_i tanimi ÖK §2B m.6 ile birebir', '**Y_i (alıntı):** ' + yi_ok in l4_txt)
    l4_rows = {}
    for line in l4_txt.splitlines():
        m = re.match(r'^\| (L4c-\d) \| ', line)
        if m:
            l4_rows[m.group(1)] = [c.strip() for c in line.strip().strip('|').split('|')][1:]
    kontrol('L4c tablosu uc satir (L4c-1..3)', sorted(l4_rows) == ['L4c-1', 'L4c-2', 'L4c-3'], sorted(l4_rows))
    vdir = os.path.dirname(man_yol)

    def iss_of(vid):
        v = byid[vid]
        b = open(os.path.join(vdir, v['dosya']), 'rb').read()
        if v['dosya'].endswith('.jws'):
            p = b.decode('ascii').split('.')[1]
            return json.loads(base64.urlsafe_b64decode(p + '=' * (-len(p) % 4)))['iss']
        from uretec import cbor   # yalniz CBOR cozucu (esleme ureticisinden bagimsiz)
        return cbor.decode(cbor.decode(b).value[2])['iss']
    k4_ic, k4_kr = ok_rows['K4']
    goc_c, eski_c = [p.strip() for p in l4_ok.split('. ') if p.startswith('Göç etmiş')][0].split(', ')
    bek = {'L4c-1': ('https://issuer.example', '"%s" → "%s"' % (k4_ic, k4_kr)),
           'L4c-2': ('https://issuer.example', '"%s"' % goc_c),
           'L4c-3': ('https://legacy-issuer.example', '"%s"' % eski_c.rstrip('.'))}
    for kod, (iss, alinti) in bek.items():
        r = l4_rows.get(kod, ['', '', '', ''])
        kontrol('%s dayanak ÖK alintisi birebir: %s' % (kod, alinti[:60]), alinti in r[1], r[1][:120])
        for i, kol in enumerate(('ML-DSA-65', 'composite')):
            vs = kimlikler(r[2 + i])
            ok_ = len(vs) == 2 and all(v in ids for v in vs) and byid.get(vs[0], {}).get('serilestirme') == 'compact' and \
                byid.get(vs[1], {}).get('serilestirme') == 'COSE_Sign1'
            kontrol('%s %s: JOSE compact + COSE_Sign1 kimlikleri manifestte' % (kod, kol), ok_, vs)
            if ok_:
                kontrol('%s %s: vektor dosyalarinda iss = %s' % (kod, kol, iss), all(iss_of(v) == iss for v in vs),
                        [iss_of(v) for v in vs])
                if kod == 'L4c-3':
                    kontrol('%s %s: insa.ihracci ayri kimlik (iss/kid/turetme etiketi)' % (kod, kol), all(
                        byid[v]['insa']['ihracci']['iss'] == iss and byid[v]['insa']['ihracci']['turetme_etiketi'] ==
                        'v1.3/issuer-eski/ES256' for v in vs))
    kontrol('L4c vektorlerinde oracle karari yok (insa/aciklama "KABUL"/"RED" icermez)', all(
        not re.search(r'\b(KABUL|RED|accept|reject)\b', json.dumps(byid[v], ensure_ascii=False))
        for v in ('L4C-JOSE_eski_ES256', 'L4C-COSE_eski_ES256')))
    # ------------------------------------------------------------ §2H alintilari ve denetim satiri
    for ad, desen in (('§2H m.9', r'^\*\*9\. K8/K9\.\*\* (.*)$'), ('§2H m.10', r'^\*\*10\. V±\.\*\* (.*)$'),
                      ('§2H m.12', r'^\*\*12\. COSE ve L4c\.\*\*\s*\n- (.*)$')):
        a = re.search(desen, ok_txt, re.M).group(1).strip()
        kontrol('%s alintisi birebir' % ad, a in es_txt, a[:80])
    kontrol('Denetim: v1.3 yeni kimliklerinin hepsi eslemede', "v1.3'te yeni olup eşlemede geçmeyen kimlik: **yok**" in es_txt)
    kontrol('Birincil/ikincil ayrimi (ÖK §2G m.4) aciklamasi', 'Birincil / ikincil (ÖK §2G m.4)' in es_txt)

gecen = sum(1 for s in sonuc if s[0])
print('ESLEME DENETIMI: %d/%d gecti' % (gecen, len(sonuc)))
for s in sonuc:
    if not s[0]:
        print('  KALDI:', s[1], str(s[2])[:200])
