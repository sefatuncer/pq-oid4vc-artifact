"""c3istat — PQ-OID4VC C3 (H6) önceden kayıtlı istatistik betikleri (Adım 9, görev 9).

Modüller:
- yapilandirma : ÖK'ye dayanan sabitler (α, tohum, B, aileler, toleranslar)
- kesin        : A uygulaması — yalnız standart kütüphane (fractions, math.comb, decimal)
- referans     : B uygulaması — scipy / statsmodels / numpy
- karsilastir  : iki uygulamanın karşılaştırılması (toleranslar)
- sema         : girdi şeması (SEMA.md) yükleme ve doğrulama
- bootstrap    : küme bootstrap (saf Python ve numpy)
- analiz       : T1–T5, Holm, etki büyüklükleri, Wilson, bootstrap, duyarlılıklar, H6 hükmü
- rapor        : insan okunur Markdown tablo
"""
__version__ = "1.0.0"
