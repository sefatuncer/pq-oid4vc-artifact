# -*- coding: utf-8 -*-
"""Adım 6 | KAT-1 DÜZELTME SONRASI Tamarin koşumu (v2; yürütücü kararı 26.09.2026, "sonuç görüldükten sonra düzeltme").

Dondurulmuş tamarin_kos.py'yi DEĞİŞTİRMEDEN içe aktarır ve yalnız iki şeyi değiştirir:
  (i)  model: KAT1_DNSSEC_v2.spthy (düzeltilmiş kapı modeli; KAT1_DNSSEC.spthy dokunulmadan kalır);
  (ii) bütün çıktılar sonuc_v2/ altına: sonuc_v2/tamarin_ham/*, sonuc_v2/iyi_bicim/*, sonuc_v2/tamarin.csv,
       sonuc_v2/tamarin_mutasyon.csv. İlk koşumun sonuc/ ve iyi_bicim/ dosyalarına dokunulmaz.
Hücreler, bayraklar, lemmalar, merdiven, zaman/bellek sınırları, bekleme kuralı ve beklenen değerlerin kaynağı
(nsurum/kat_nsurum.tsv 'ilk_ajan'; mutasyonlarda mutasyonlar.tsv) ilk koşumla AYNIDIR (tk.kanitla, tk.tablo).
Kipler: python tamarin_kos_v2.py iyi_bicim | kos
"""
import csv, os, re, subprocess, sys

KOK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KOK)
import tamarin_kos as tk  # noqa: E402  (dondurulmuş koşucu; değiştirilmedi)

tk.MODEL = 'KAT1_DNSSEC_v2.spthy'
CIKTI = 'sonuc_v2'
_asil_cagir = tk.cagir


def cagir_v2(ad, model, bayraklar, argumanlar, cikti_dizin, bellek='12g'):
    """tk.cagir ile aynı; yalnız çıktı dizini sonuc_v2/ altına yönlendirilir."""
    d = cikti_dizin.replace('\\', '/')
    d = CIKTI + '/' + (d[len('sonuc/'):] if d.startswith('sonuc/') else d)
    return _asil_cagir(ad, model, bayraklar, argumanlar, d, bellek)


tk.cagir = cagir_v2          # tk.kanitla modül genelindeki 'cagir' adını çağrı anında çözer
TABLOLAR = [('hucreler.tsv', 'tamarin.csv'), ('mutasyonlar.tsv', 'tamarin_mutasyon.csv')]


def iyi_bicim():
    """tk.iyi_bicim ile aynı mantık; özet sonuc_v2/iyi_bicim/ozet.tsv'ye yazılır."""
    satirlar = sum((tk.tablo(t) for t, _ in TABLOLAR), [])
    goruldu, cikti = {}, []
    for r in satirlar:
        bay = [b for b in r['tamarin_bayraklari'].split(',') if b and b != '-']
        model = r.get('model') or tk.MODEL
        k = tk.anahtar(bay, model)
        if k in goruldu:
            continue
        ad = 'wf%02d' % (len(goruldu) + 1)
        goruldu[k] = ad
        txt, meta = tk.cagir(ad, model, bay, [], 'iyi_bicim', bellek='4g')
        uyari = len(re.findall(r'WARNING', txt))
        cikti.append({'ad': ad, 'model': model, 'bayraklar': ','.join(bay), 'iyi_bicim': 'EVET' if tk.wf_tamam(txt) else 'HAYIR',
                      'uyari_sayisi': uyari, 'meta': meta, 'ilk_kosu': r['kosu']})
        print(cikti[-1], flush=True)
    with open(os.path.join(KOK, CIKTI, 'iyi_bicim', 'ozet.tsv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(cikti[0].keys()), delimiter='\t')
        w.writeheader()
        w.writerows(cikti)
    return 0 if all(c['iyi_bicim'] == 'EVET' and c['uyari_sayisi'] == 0 for c in cikti) else 2


def kos():
    """tk.kos ile aynı mantık ve sütunlar; çıktılar sonuc_v2/ altına."""
    NS = {}
    with open(tk.NSURUM, encoding='utf-8', newline='') as f:
        for x in csv.DictReader(f, delimiter='\t'):
            NS[(x['hucre'], x['sutun'])] = x['ilk_ajan']
    surum = subprocess.run(['docker', 'image', 'inspect', '--format', '{{.Id}}', tk.IMG], capture_output=True, text=True).stdout.strip()
    os.makedirs(os.path.join(KOK, CIKTI), exist_ok=True)
    for tablo_adi, cikti_adi in TABLOLAR:
        cikti = []
        for r in tk.tablo(tablo_adi):
            ex = tk.kanitla(r, 'executable')
            ln = tk.kanitla(r, r['tamarin_lemma'])
            if r.get('nsurum_hucre') and r.get('nsurum_sutun'):
                bek = NS.get((r['nsurum_hucre'], r['nsurum_sutun']), 'YOK_ANAHTAR')   # tek kaynak
            else:
                bek = r['beklenen']
            gozlenen = ln[0] if ln[4] == 'EVET' else 'gecersiz_wf'
            satir = {'kosu': r['kosu'], 'model': r.get('model') or tk.MODEL, 'bayraklar': r['tamarin_bayraklari'],
                     'lemma': r['tamarin_lemma'], 'beklenen': bek, 'gozlenen': gozlenen,
                     'uyum': 'EVET' if gozlenen == bek else 'HAYIR', 'lemma_ham_sonucu': ln[0],
                     'adim': ln[1], 'merdiven': ln[2], 'meta': ln[3], 'iyi_bicim': ln[4],
                     'executable': ex[0], 'imaj': surum}
            if tablo_adi == 'hucreler.tsv':
                satir.update({'hucre': r['nsurum_hucre'], 'sutun': r['nsurum_sutun']})
            else:
                satir.update({'mutasyon': r['mutasyon'], 'temel': r['temel']})
            cikti.append(satir)
            print(satir, flush=True)
        with open(os.path.join(KOK, CIKTI, cikti_adi), 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(cikti[0].keys()))
            w.writeheader()
            w.writerows(cikti)
    return 0


if __name__ == '__main__':
    kip = sys.argv[1] if len(sys.argv) > 1 else ''
    sys.exit(iyi_bicim() if kip == 'iyi_bicim' else kos() if kip == 'kos' else 1)
