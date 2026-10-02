"""Test helpers: check log and result files."""
import json
import os
import time


class Kayit:
    def __init__(self, ad):
        self.ad = ad
        self.kontroller = []
        self.t0 = time.time()

    def kontrol(self, grup, ad, kosul, ayrinti=None):
        self.kontroller.append({'grup': grup, 'ad': ad, 'gecti': bool(kosul), 'ayrinti': ayrinti})
        return bool(kosul)

    def bilgi(self, grup, ad, deger):
        self.kontroller.append({'grup': grup, 'ad': ad, 'gecti': None, 'ayrinti': deger})

    def ozet(self):
        k = [c for c in self.kontroller if c['gecti'] is not None]
        return {'toplam': len(k), 'gecen': sum(c['gecti'] for c in k),
                'kalan': [c['grup'] + '/' + c['ad'] for c in k if not c['gecti']]}

    def yaz(self, cikti_dizini, ek=None):
        os.makedirs(cikti_dizini, exist_ok=True)
        from pqjose import versions
        d = {'test': self.ad, 'sure_s': round(time.time() - self.t0, 2), 'surumler': versions(),
             'ozet': self.ozet(), 'kontroller': self.kontroller}
        if ek:
            d.update(ek)
        with open(os.path.join(cikti_dizini, self.ad + '.json'), 'w', encoding='utf-8') as f:
            json.dump(d, f, indent=1, ensure_ascii=False)
            f.write('\n')
        o = self.ozet()
        satirlar = ['%s: %d/%d gecti' % (self.ad, o['gecen'], o['toplam'])]
        for c in self.kontroller:
            durum = {True: 'GECTI', False: 'KALDI', None: 'BILGI'}[c['gecti']]
            a = c['ayrinti']
            if isinstance(a, (dict, list)):
                a = json.dumps(a, ensure_ascii=False)
            satirlar.append('  [%s] %s / %s%s' % (durum, c['grup'], c['ad'], (' — ' + str(a)[:300]) if a is not None else ''))
        with open(os.path.join(cikti_dizini, self.ad + '.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(satirlar) + '\n')
        print(satirlar[0])
        for c in self.kontroller:
            if c['gecti'] is False:
                print('  KALDI:', c['grup'], c['ad'], str(c['ayrinti'])[:300])
        return o
