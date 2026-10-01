# -*- coding: utf-8 -*-
"""Adım 6 | Tamarin koşucusu (host'ta çalışır; her Tamarin çağrısı ayrı konteynerde).

Kipler:
  python tamarin_kos.py iyi_bicim   -> yalnız iyi biçimlilik (--prove YOK): benzersiz her bayrak kümesi
                                       iyi_bicim/<ad>.{txt,meta}, iyi_bicim/ozet.tsv
  python tamarin_kos.py kos         -> hücreler + mutasyonlar: 'executable' + hedef lemma (merdivenle)
                                       sonuc/tamarin_ham/*, sonuc/tamarin.csv, sonuc/tamarin_mutasyon.csv
Kurallar (Adım 6 görevi; Tamarin çalışmasının calistir.sh'siyle aynı): imaj pq-a02-tamarin:1.12.0;
--memory=12g --memory-swap=12g (iyi biçimlilikte 4g); zaman aşımı 600 s; ad öneki pq-a06-;
aynı anda tek ağır Tamarin işi: başka bir pq-a02-tamarin konteyneri çalışıyorsa beklenir.
Merdiven (sentez §7.9): 1 --prove=<lemma>; 3 + --auto-sources; 5 + --bound=40; 6 'belirsiz'.
İyi biçimlilik her çağrıda denetlenir ("wellformedness check failed" => 'gecersiz_wf'). Türetme denetimi
kapatılmaz; zaman aşımı --derivcheck-timeout=60 (ÖK §2H.2).
Beklenen değerler: hücrelerde nsurum/kat_nsurum.tsv 'ilk_ajan' (tek kaynak), mutasyonlarda mutasyonlar.tsv.
"""
import csv, json, os, re, subprocess, sys, time

KOK = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.abspath(os.path.join(KOK, '..', '..', '..'))
NSURUM = os.path.join(PROJE, 'model', 'bilinen-cevap', 'nsurum', 'kat_nsurum.tsv')
IMG = 'pq-a02-tamarin:1.12.0'
MODEL = 'KAT2_X509.spthy'            # klasöre özgü varsayılan (satırda 'model' sütunu varsa o kullanılır)
EK_BAGLAR = []                         # klasöre özgü salt okunur bağlar: [(host_yolu, konteyner_yolu)]
TO = 600
ORTAK = ['--derivcheck-timeout=60']
MERDIVEN = [(1, []), (3, ['--auto-sources']), (5, ['--bound=40'])]
SONUC_RE = re.compile(r'^\s*(\S+) \((all-traces|exists-trace)\): (verified|falsified|analysis incomplete)(.*)$')


def dyol(p):
    return p.replace('\\', '/')


def tablo(ad):
    yol = os.path.join(KOK, ad)
    if not os.path.exists(yol):
        return []
    with open(yol, encoding='utf-8', newline='') as f:
        return [r for r in csv.DictReader(f, delimiter='\t') if r['motor'] == 'tamarin']


AGIR_MIB = 2048   # bu bellek düzeyinin üstündeki Tamarin konteyneri "ağır iş" sayılır


def mib(deger):
    """docker stats bellek dizesinin ilk kısmı ('1.2GiB') -> MiB."""
    m = re.match(r'\s*([\d.]+)\s*([KMG]i?B)', deger)
    if not m:
        return 0.0
    return float(m.group(1)) * {'KiB': 1 / 1024, 'kB': 1 / 1024, 'KB': 1 / 1024, 'MiB': 1, 'MB': 1,
                                'GiB': 1024, 'GB': 1024}.get(m.group(2), 0)


def bekle():
    """Aynı anda tek AĞIR Tamarin işi: başka bir pq-a02-tamarin konteyneri AGIR_MIB ve üstü bellek kullanıyorsa
    bitmesini bekle. Daha hafif işlerle (ör. Tamarin çalışmasının kısa koşuları) küçük KAT işi aynı anda koşabilir."""
    while True:
        adlar = subprocess.run(['docker', 'ps', '--filter', 'ancestor=' + IMG, '--format', '{{.Names}}'],
                               capture_output=True, text=True).stdout.split()
        adlar = [a for a in adlar if not a.startswith('pq-a06-')]
        if not adlar:
            return
        st = subprocess.run(['docker', 'stats', '--no-stream', '--format', '{{.Name}}\t{{.MemUsage}}'] + adlar,
                            capture_output=True, text=True).stdout
        agir = [s.split('\t')[0] for s in st.splitlines() if '\t' in s and mib(s.split('\t')[1]) >= AGIR_MIB]
        if not agir:
            return
        print('  bekleniyor (ağır iş): %s' % ', '.join(agir), flush=True)
        time.sleep(3)


def cagir(ad, model, bayraklar, argumanlar, cikti_dizin, bellek='12g'):
    bekle()
    os.makedirs(os.path.join(KOK, cikti_dizin), exist_ok=True)
    konteyner_model = model if model.startswith('/') else '/kat/' + model
    komut = ['docker', 'run', '--rm', '--name', 'pq-a06-' + re.sub(r'[^A-Za-z0-9_.-]', '_', ad)[:60],
             '--memory=' + bellek, '--memory-swap=' + bellek, '-v', dyol(KOK) + ':/kat']
    for h, k in EK_BAGLAR:
        komut += ['-v', dyol(h) + ':' + k + ':ro']
    komut += [IMG, 'sh', '/kat/tamarin_ic.sh', '/kat/%s/%s' % (cikti_dizin.replace('\\', '/'), ad), str(TO), konteyner_model]
    komut += ['-D=' + b for b in bayraklar] + ORTAK + argumanlar
    env = dict(os.environ, MSYS_NO_PATHCONV='1')
    subprocess.run(komut, env=env, capture_output=True, text=True)
    txt = open(os.path.join(KOK, cikti_dizin, ad + '.txt'), encoding='utf-8', errors='replace').read()
    meta = open(os.path.join(KOK, cikti_dizin, ad + '.meta'), encoding='utf-8').read().strip()
    return txt, meta


def wf_tamam(txt):
    return 'wellformedness check failed' not in txt


def lemma_sonucu(txt, lemma):
    for satir in txt.splitlines():
        m = SONUC_RE.match(satir)
        if m and m.group(1) == lemma:
            adim = re.search(r'\((\d+) steps\)', m.group(4))
            return m.group(3), (adim.group(1) if adim else '')
    return 'yok', ''


def anahtar(bayraklar, model):
    return '%s|%s' % (model, ','.join(sorted(bayraklar)))


TABLOLAR = [('hucreler.tsv', 'tamarin.csv'), ('mutasyonlar.tsv', 'tamarin_mutasyon.csv'), ('ek_tamarin.tsv', 'tamarin_ek.csv')]


def iyi_bicim():
    satirlar = sum((tablo(t) for t, _ in TABLOLAR), [])
    goruldu, cikti = {}, []
    for r in satirlar:
        bay = [b for b in r['tamarin_bayraklari'].split(',') if b and b != '-']
        model = r.get('model') or MODEL
        k = anahtar(bay, model)
        if k in goruldu:
            continue
        ad = 'wf%02d' % (len(goruldu) + 1)
        goruldu[k] = ad
        txt, meta = cagir(ad, model, bay, [], 'iyi_bicim', bellek='4g')
        uyari = len(re.findall(r'WARNING', txt))
        cikti.append({'ad': ad, 'model': model, 'bayraklar': ','.join(bay), 'iyi_bicim': 'EVET' if wf_tamam(txt) else 'HAYIR',
                      'uyari_sayisi': uyari, 'meta': meta, 'ilk_kosu': r['kosu']})
        print(cikti[-1], flush=True)
    with open(os.path.join(KOK, 'iyi_bicim', 'ozet.tsv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(cikti[0].keys()), delimiter='\t')
        w.writeheader()
        w.writerows(cikti)
    return 0 if all(c['iyi_bicim'] == 'EVET' and c['uyari_sayisi'] == 0 for c in cikti) else 2


def kanitla(r, lemma):
    """Merdivenle tek lemma; (sonuc, adim, basamak, meta, wf). Lemma sonucu iyi biçimlilikten bağımsız ayrıştırılır;
    uyarılı koşunun kapı hücresinde geçersiz sayılması kos() içinde yapılır."""
    bay = [b for b in r['tamarin_bayraklari'].split(',') if b and b != '-']
    model = r.get('model') or MODEL
    wf = 'EVET'
    for basamak, ek in MERDIVEN:
        ad = '%s__%s__b%d' % (r['kosu'], lemma, basamak)
        txt, meta = cagir(ad, model, bay, ['--prove=' + lemma] + ek, os.path.join('sonuc', 'tamarin_ham'))
        if not wf_tamam(txt):
            wf = 'HAYIR'
        sonuc, adim = lemma_sonucu(txt, lemma)
        if sonuc in ('verified', 'falsified'):
            if basamak == 5 and sonuc == 'verified':
                continue                     # sınırlı arama 'verified' kanıt değildir
            return sonuc, adim, basamak, meta, wf
    return 'belirsiz', '', 6, meta, wf


def kos():
    NS = {}
    with open(NSURUM, encoding='utf-8', newline='') as f:
        for x in csv.DictReader(f, delimiter='\t'):
            NS[(x['hucre'], x['sutun'])] = x['ilk_ajan']
    surum = subprocess.run(['docker', 'image', 'inspect', '--format', '{{.Id}}', IMG], capture_output=True, text=True).stdout.strip()
    for tablo_adi, cikti_adi in TABLOLAR:
        cikti = []
        for r in tablo(tablo_adi):
            ex = kanitla(r, 'executable')
            ln = kanitla(r, r['tamarin_lemma'])
            if r.get('nsurum_hucre') and r.get('nsurum_sutun'):
                bek = NS.get((r['nsurum_hucre'], r['nsurum_sutun']), 'YOK_ANAHTAR')   # tek kaynak
            else:
                bek = r['beklenen']
            # kapı tablolarında iyi biçimlilik uyarılı koşu geçersizdir; ek tabloda ham sonuç kaydedilir
            gozlenen = ln[0] if (ln[4] == 'EVET' or tablo_adi == 'ek_tamarin.tsv') else 'gecersiz_wf'
            satir = {'kosu': r['kosu'], 'model': r.get('model') or MODEL, 'bayraklar': r['tamarin_bayraklari'],
                     'lemma': r['tamarin_lemma'], 'beklenen': bek, 'gozlenen': gozlenen,
                     'uyum': 'EVET' if gozlenen == bek else 'HAYIR', 'lemma_ham_sonucu': ln[0],
                     'adim': ln[1], 'merdiven': ln[2], 'meta': ln[3], 'iyi_bicim': ln[4],
                     'executable': ex[0], 'imaj': surum}
            if tablo_adi == 'hucreler.tsv':
                satir.update({'hucre': r['nsurum_hucre'], 'sutun': r['nsurum_sutun']})
            elif tablo_adi == 'mutasyonlar.tsv':
                satir.update({'mutasyon': r['mutasyon'], 'temel': r['temel']})
            else:
                satir.update({'ek': r['ek'], 'hucre': r.get('nsurum_hucre', ''), 'sutun': r.get('nsurum_sutun', '')})
            cikti.append(satir)
            print(satir, flush=True)
        if cikti:
            with open(os.path.join(KOK, 'sonuc', cikti_adi), 'w', encoding='utf-8', newline='') as f:
                w = csv.DictWriter(f, fieldnames=list(cikti[0].keys()))
                w.writeheader()
                w.writerows(cikti)
    return 0


if __name__ == '__main__':
    kip = sys.argv[1] if len(sys.argv) > 1 else ''
    sys.exit(iyi_bicim() if kip == 'iyi_bicim' else kos() if kip == 'kos' else 1)
