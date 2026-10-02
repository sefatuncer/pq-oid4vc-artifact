# -*- coding: utf-8 -*-
"""
PQ-OID4VC | Last condition of the technical gate (PR §2F) | ASP instance -> Tamarin translation
=================================================================================

Input : model/sampling/secim/secim.json (the maintainers' selection; NOT CHANGED)
Output: ornekler/<satir_id>.spthy   one Tamarin theory per instance
        ceviri_plani.tsv            translation summary per instance (target lemma, artefacts, keys)

BLINDNESS RULE
-------------
The translation reads only the INPUTS of ASP:
  - assignment: alt_cizge[].pq (node decision), kume.tasiyicilar (selected expectation carriers);
  - what is derived from the model structure and parameters: tanitici (active edges), sabit, kanal,
    klasik_alternatif (phase), klasikse_pencerede_kirilir (τ and window), hucre.politika;
  - tamarin.lemma (name of the target lemma).
The OUTPUTS of ASP are not read and do not enter the translation: asp_tahmini, ihlal_edilen,
tanik_sahte_artefaktlar, alt_cizge[].sahte, alt_cizge[].beklenti_var, tamarin.bayraklar.BEKLENTI.
The comparison is made in a separate script (karsilastir.py), after the runs.

TRANSLATION RULES (compiled from the patterns of the R1–R7 templates)
------------------------------------------------------------
For every signed artefact A (except a00_ojeu and the a13_* transports):
  * Keys (R1/R5): main key ('main'); PQ if pq(A), otherwise classical.
    Classical alternative ('alt', R2 coexistence): if pq(A) and klasik_alternatif(A), there is additionally a classical
    key; the honest party signs with both keys (like R2 Issue_Migrated).
  * CRQC (R1 CRQC_Break_*): a classical key can be extracted from the observed public key after Q-day only if
    klasikse_pencerede_kirilir holds (R6: if the window is shorter than τ, there is no breaking rule).
  * Pinning (R5 Pin_TL_Out_Of_Band): if sabit(A), A's signer keys are trusted out of band at the verifier;
    there is no introducer path (cuts K2).
  * Introduction (R1 chain; R1 X_alt_ca "any valid path"): if A is not pinned, for EVERY B in tanitici(A):
    a message <'intro', B, A, pk, tür> signed with an accepted key of B makes pk accepted for A.
    An honest B introduces only the honest keys of A.
  * Expectation (R2 EXPECT_AUTH / R3 channel; policy p4): if (C, X) ∈ kume.tasiyicilar, using the classical
    alternative ('alt') key of X requires a message <'exp', C, X, 'none'> signed with an accepted key of C;
    an honest C publishes only 'pq_required'.
    C = a00_ojeu (unsigned, pinned channel) is authentic: using 'alt' for X is never possible.
    Under policies p0–p2 no expectation is used (ASP beklenti_politikasi); p3 has no carrier in these instances.
  * Transport (R3a): in all instances a13 is classical and breakable, i.e. a forged fetched artefact can be
    delivered. Tamarin's network attacker already delivers every message; no separate rule is needed.
    The assumption is checked: if a13 turns out PQ or unbreakable, the translation stops.
Goals (olgular/hedefler.lp):
  G1 -> a07_kimlik: <'cred', c>; lemma "Accept(c) ⇒ Issued(c) before" (R1/R5 G1).
  G2 -> a10_kbjwt : <'kb', n> for the verifier nonce; the device key is introduced with a07_kimlik
        (cnf); lemma "AcceptPres(n) ⇒ Presented(n) before" (R4 G2). SINGLE_USE does not change the result
        (R4/R6h5 H5 result) and is not modelled.
  G3 -> a08_durum : <'status', s>; lemma "AcceptStatus(s) ⇒ IssuedStatus(s) before".
Every theory additionally has the sanity lemma `executable` (honest acceptance is reachable).
"""
import io
import json
import os
import sys

KOK = os.path.dirname(os.path.abspath(__file__))
SECIM = os.path.join(KOK, 'secim.json')
HEDEF_ARTEFAKT = {'G1': 'a07_kimlik', 'G2': 'a10_kbjwt', 'G3': 'a08_durum'}
OKUNMAYAN = ('asp_tahmini', 'ihlal_edilen', 'tanik_sahte_artefaktlar')


class CeviriHatasi(Exception):
    pass


def imzali_mi(a):
    return a['artefakt'] != 'a00_ojeu' and not a['artefakt'].startswith('a13_')


def cevir(ornek, gorev):
    """ornek: a row of secim.json (ASP output fields removed beforehand). Return: (spthy, plan_row)."""
    sid = ornek['satir_id']
    hedef = ornek['hedef']
    if hedef not in HEDEF_ARTEFAKT:
        raise CeviriHatasi('%s: hedef %s desteklenmiyor' % (sid, hedef))
    lemma = ornek['tamarin']['lemma']
    politika = ornek['hucre']['politika']
    alt = {a['artefakt']: a for a in ornek['alt_cizge']}
    imzali = [a for a in ornek['alt_cizge'] if imzali_mi(a)]
    ad = {a['artefakt'] for a in imzali}
    hedef_a = HEDEF_ARTEFAKT[hedef]
    if hedef_a not in ad:
        raise CeviriHatasi('%s: hedef artefakt %s alt çizgede yok' % (sid, hedef_a))

    # --- assumption checks (properties outside the scope of the translation)
    for a in ornek['alt_cizge']:
        if a.get('varyant'):
            raise CeviriHatasi('%s: imzasız varyant (%s) desteklenmiyor' % (sid, a['artefakt']))
        if a['artefakt'].startswith('a13_') and (a['pq'] or not a['klasikse_pencerede_kirilir']):
            raise CeviriHatasi('%s: taşıma %s kırılamaz; R3a taşıma ikamesi gerekli' % (sid, a['artefakt']))
    for a in imzali:
        if not a['sabit'] and not a['tanitici']:
            raise CeviriHatasi('%s: %s ne sabit ne tanıtılmış' % (sid, a['artefakt']))
        for b in a['tanitici']:
            if b not in ad:
                raise CeviriHatasi('%s: %s tanıtıcısı %s imzalı artefakt değil' % (sid, a['artefakt'], b))

    # --- expectation carriers
    tasiyici = {}  # X -> [C]
    if politika in ('p3', 'p4'):
        for c, x in ornek['kume']['tasiyicilar']:
            if politika == 'p3':
                raise CeviriHatasi('%s: p3 taşıyıcısı (p3 kanalı) bu çeviride yok' % sid)
            if x not in ad:
                raise CeviriHatasi('%s: taşıyıcı hedefi %s imzalı artefakt değil' % (sid, x))
            if c != 'a00_ojeu' and c not in ad:
                raise CeviriHatasi('%s: taşıyıcı %s alt çizgede yok' % (sid, c))
            tasiyici.setdefault(x, []).append(c)
    elif ornek['kume']['tasiyicilar']:
        raise CeviriHatasi('%s: p0-p2 politikasında taşıyıcı var' % sid)

    def alt_var(x):
        return alt[x]['pq'] and alt[x]['klasik_alternatif']

    def kapili(x):
        return x in tasiyici

    def alt_kapali(x):
        return any(c == 'a00_ojeu' for c in tasiyici.get(x, []))

    L = []
    w = L.append
    w('theory Ornek_%s' % sid.replace('-', '_'))
    w('begin')
    w('')
    w('/*')
    w(' * PQ-OID4VC | teknik kapı (ÖK §2F) | %s örneği %s — cevir.py ile üretildi; elle değiştirme.' % (gorev, sid))
    w(' * hedef %s (%s), tür %s, hücre %s' % (hedef, hedef_a, ornek['tur'], ornek['hucre_id']))
    w(' * Çeviri kuralları: cevir.py başlığı. Girdi: atama (pq), kenarlar (tanitici), sabitleme,')
    w(' * faz (klasik alternatif), pencere (kırılabilirlik), taşıyıcılar, politika. ASP çıktıları okunmadı.')
    w(' */')
    w('')
    w('builtins: signing')
    w('')
    w('restriction Equality: "All x y #i. Eq(x, y) @ #i ==> x = y"')
    w('restriction Unique:   "All x #i #j. Unique(x) @ #i & Unique(x) @ #j ==> #i = #j"')
    w('')
    w("rule Qday:")
    w("    [ ] --[ Unique('qday'), QdayEv() ]-> [ !CRQC() ]")
    w('')

    # --- key setup and breaking rules
    w('/* ---------------- artefakt imzacı anahtarları (R1/R5; birlikte yaşamada ikinci klasik anahtar: R2) ---------------- */')
    plan_anahtar = []
    for a in imzali:
        x = a['artefakt']
        fr = ['Fr(~km)']
        sk = ["!Sk('%s', 'main', ~km)" % x]
        out = ['Out(pk(~km))']
        if alt_var(x):
            fr.append('Fr(~ka)')
            sk.append("!Sk('%s', 'alt', ~ka)" % x)
            out.append('Out(pk(~ka))')
        w('rule Setup_%s:' % x)
        w("    [ %s ] --[ Unique('setup_%s') ]-> [ %s ]" % (', '.join(fr), x, ', '.join(sk + out)))
        kir = a['klasikse_pencerede_kirilir']
        if not a['pq'] and kir:
            w('rule Break_%s_main:' % x)
            w("    [ !Sk('%s', 'main', k), !CRQC(), In(pk(k)) ] --[ Broken('%s_main') ]-> [ Out(k) ]" % (x, x))
        if alt_var(x) and kir:
            w('rule Break_%s_alt:' % x)
            w("    [ !Sk('%s', 'alt', k), !CRQC(), In(pk(k)) ] --[ Broken('%s_alt') ]-> [ Out(k) ]" % (x, x))
        plan_anahtar.append('%s:%s%s%s%s' % (x, 'pq' if a['pq'] else 'kl', '+alt' if alt_var(x) else '',
                                           '' if kir else '(kirilmaz)', '+sabit' if a['sabit'] else ''))
    w('')

    # --- pinning
    w('/* ---------------- sabitleme (R5): sabit artefaktın imzacı anahtarları bant dışı güvenilir ---------------- */')
    for a in imzali:
        if a['sabit']:
            x = a['artefakt']
            w('rule Pin_%s:' % x)
            w("    [ !Sk('%s', t, k) ] --> [ !Acc('%s', pk(k), t) ]" % (x, x))
    w('')

    # --- gate premises
    def kapi_oncul(x):
        return ["!ExpVal('%s', '%s', 'none')" % (c, x) for c in tasiyici.get(x, [])]

    def kabul_kurallari(ad_kok, x, govde_oncul, govde_eylem, govde_sonuc, pk_ad):
        """Verification of x with the accepted key pk_ad; if x is gated, 'alt' is separate and gated."""
        if not kapili(x):
            w('rule %s:' % ad_kok)
            w("    [ !Acc('%s', %s, t)%s ]" % (x, pk_ad, govde_oncul))
            w('  --[ %s ]->' % govde_eylem)
            w('    [ %s ]' % govde_sonuc)
            return
        w('rule %s_main:' % ad_kok)
        w("    [ !Acc('%s', %s, 'main')%s ]" % (x, pk_ad, govde_oncul))
        w('  --[ %s ]->' % govde_eylem)
        w('    [ %s ]' % govde_sonuc)
        if alt_kapali(x):
            w("/* %s'nin 'alt' kullanımı yok: taşıyıcısı a00_ojeu özgün (R2 EXPECT_AUTH) */" % x)
            return
        w('rule %s_alt:' % ad_kok)
        w("    [ !Acc('%s', %s, 'alt'), %s%s ]" % (x, pk_ad, ', '.join(kapi_oncul(x)), govde_oncul))
        w('  --[ %s ]->' % govde_eylem)
        w('    [ %s ]' % govde_sonuc)

    # --- introduction
    w('/* ---------------- tanıtma (R1 zinciri; her tanıtıcı bir OR-kenarıdır: R1 X_alt_ca) ---------------- */')
    kenarlar = []
    for a in imzali:
        x = a['artefakt']
        for b in a['tanitici']:
            kenarlar.append((b, x))
            w('rule Intro_%s__%s:' % (b, x))
            w("    let m = <'intro', '%s', '%s', pk(kA), tA> in" % (b, x))
            w("    [ !Sk('%s', tB, kB), !Sk('%s', tA, kA) ] --> [ Out(<m, sign(m, kB)>) ]" % (b, x))
            if a['sabit']:
                w('/* %s sabit: tanıtıcı yolu doğrulayıcıda kullanılmaz (R5) */' % x)
                continue
            govde_oncul = ", In(<<'intro', '%s', '%s', pkA, tA>, s>)" % (b, x)
            govde_eylem = "Eq(verify(s, <'intro', '%s', '%s', pkA, tA>, pkB), true)" % (b, x)
            govde_sonuc = "!Acc('%s', pkA, tA)" % x
            kabul_kurallari('AccIntro_%s__%s' % (b, x), b, govde_oncul, govde_eylem, govde_sonuc, 'pkB')
    w('')

    # --- expectation carriers
    w('/* ---------------- beklenti (R2 EXPECT_AUTH / R3 kanal; politika %s) ---------------- */' % politika)
    for x, cs in sorted(tasiyici.items()):
        for c in cs:
            if c == 'a00_ojeu':
                w("/* (%s, %s): OJEU özgün; 'none' beyanı üretilemez */" % (c, x))
                continue
            w('rule ExpPub_%s__%s:' % (c, x))
            w("    let m = <'exp', '%s', '%s', 'pq_required'> in" % (c, x))
            w("    [ !Sk('%s', t, k) ] --> [ Out(<m, sign(m, k)>) ]" % c)
            govde_oncul = ", In(<<'exp', '%s', '%s', e>, s>)" % (c, x)
            govde_eylem = "Eq(verify(s, <'exp', '%s', '%s', e>, pkC), true)" % (c, x)
            govde_sonuc = "!ExpVal('%s', '%s', e)" % (c, x)
            kabul_kurallari('ExpAcc_%s__%s' % (c, x), c, govde_oncul, govde_eylem, govde_sonuc, 'pkC')
    w('')

    # --- goal
    w('/* ---------------- hedef %s ---------------- */' % hedef)
    x = hedef_a
    if hedef == 'G1':
        sk = ["!Sk('%s', 'main', km)" % x] + (["!Sk('%s', 'alt', ka)" % x] if alt_var(x) else [])
        outs = ['Out(<crb, sign(crb, km)>)'] + (['Out(<crb, sign(crb, ka)>)'] if alt_var(x) else [])
        w('rule Issue_Credential:')
        w("    let crb = <'cred', ~c> in")
        w('    [ %s, Fr(~c) ] --[ Issued(~c) ]-> [ %s ]' % (', '.join(sk), ', '.join(outs)))
        kabul_kurallari('Accept_Credential', x, ", In(<<'cred', c>, s>)",
                        "Eq(verify(s, <'cred', c>, pkI), true), Accept(c)", '', 'pkI')
        lem = ['lemma executable:', '  exists-trace', '  "Ex c #i #j. Issued(c) @ #i & Accept(c) @ #j"', '',
               'lemma %s:' % lemma, '  "All c #j. Accept(c) @ #j ==> (Ex #i. Issued(c) @ #i & #i < #j)"']
    elif hedef == 'G3':
        sk = ["!Sk('%s', 'main', km)" % x] + (["!Sk('%s', 'alt', ka)" % x] if alt_var(x) else [])
        outs = ['Out(<stb, sign(stb, km)>)'] + (['Out(<stb, sign(stb, ka)>)'] if alt_var(x) else [])
        w('rule Issue_Status:')
        w("    let stb = <'status', ~st> in")
        w('    [ %s, Fr(~st) ] --[ IssuedStatus(~st) ]-> [ %s ]' % (', '.join(sk), ', '.join(outs)))
        kabul_kurallari('Accept_Status', x, ", In(<<'status', st>, s>)",
                        "Eq(verify(s, <'status', st>, pkS), true), AcceptStatus(st)", '', 'pkS')
        lem = ['lemma executable:', '  exists-trace', '  "Ex st #i #j. IssuedStatus(st) @ #i & AcceptStatus(st) @ #j"', '',
               'lemma %s:' % lemma,
               '  "All st #j. AcceptStatus(st) @ #j ==> (Ex #i. IssuedStatus(st) @ #i & #i < #j)"']
    else:  # G2
        w('rule Verifier_Challenge:')
        w('    [ Fr(~n) ] --> [ VChal(~n), Out(~n) ]')
        w('rule Holder_Present:')
        w("    [ !Sk('%s', t, k), In(n) ] --[ Presented(n) ]-> [ Out(<<'kb', n>, sign(<'kb', n>, k)>) ]" % x)
        kabul_kurallari('Accept_Presentation', x, ", VChal(n), In(<<'kb', n>, s>)",
                        "Eq(verify(s, <'kb', n>, pkD), true), AcceptPres(n)", '', 'pkD')
        lem = ['lemma executable:', '  exists-trace', '  "Ex n #p #j. Presented(n) @ #p & AcceptPres(n) @ #j"', '',
               'lemma %s:' % lemma,
               '  "All n #j. AcceptPres(n) @ #j ==> (Ex #p. Presented(n) @ #p & #p < #j)"']
    w('')
    w('/* ================= lemmalar ================= */')
    L.extend(lem)
    w('')
    w('end')
    spthy = '\n'.join(L) + '\n'
    # correction of an empty result bracket "[  ]"
    spthy = spthy.replace('    [  ]\n', '    [ ]\n')
    plan = [sid, gorev, hedef, ornek['tur'], ornek['hucre_id'], lemma, 'ornekler/%s.spthy' % sid,
            ' '.join(plan_anahtar),
            ' '.join('%s>%s' % e for e in kenarlar),
            ' '.join('%s>%s' % (c, xx) for xx, cs in sorted(tasiyici.items()) for c in cs) or '-']
    return spthy, plan


def main():
    s = json.load(io.open(SECIM, encoding='utf-8'))
    isler = [(o, 'kapi') for o in s['kapi_ornekleri']]
    os.makedirs(os.path.join(KOK, 'ornekler'), exist_ok=True)
    satirlar = ['\t'.join(['satir_id', 'gorev', 'hedef', 'tur', 'hucre_id', 'lemma', 'dosya',
                           'anahtarlar', 'kenarlar', 'tasiyicilar'])]
    disi = []
    for o, gorev in isler:
        kor = {k: v for k, v in o.items() if k not in OKUNMAYAN}
        kor['alt_cizge'] = [{k: v for k, v in a.items() if k not in ('sahte', 'beklenti_var')}
                            for a in o['alt_cizge']]
        try:
            spthy, plan = cevir(kor, gorev)
        except CeviriHatasi as e:   # 5B: instance outside the scope of the translator; recorded, not run
            disi.append((o['satir_id'], o['hucre_id'], o['tur'], str(e)))
            continue
        with io.open(os.path.join(KOK, 'ornekler', '%s.spthy' % o['satir_id']), 'w',
                     encoding='utf-8', newline='\n') as f:
            f.write(spthy)
        satirlar.append('\t'.join(plan))
    with io.open(os.path.join(KOK, 'ceviri_plani.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(satirlar) + '\n')
    with io.open(os.path.join(KOK, 'ceviri_disi.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('satir_id\thucre_id\ttur\tneden\n' + ''.join('\t'.join(x) + '\n' for x in disi))
    print('cevrilen ornek: %d; ceviri disi: %d' % (len(satirlar) - 1, len(disi)))


if __name__ == '__main__':
    main()
