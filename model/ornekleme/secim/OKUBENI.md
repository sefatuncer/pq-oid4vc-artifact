# Teknik kapının örneklem seçimi (yürütücüye ait)

- Kural: ÖK §2F madde 2 (Değişiklik 6, çapa 6 = `998276a`).
- Betik: `teknik_kapi_secim.py`. ASP çerçevesi (`model/asp/ornekleme/cerceve.jsonl`) ve keşif ızgarası (`kesif_2x2.jsonl`) gelmeden ÖNCE yazıldı ve commit edildi.
- Seçim, `sha256("20260926|<bağlam>|<kimlik>")` sıralamasıyla belirlenimci yapılır. Python sürümünden bağımsızdır ve elle denetlenebilir.
- Çıktı: `secim.json` (çerçeve ve keşif dosyalarının SHA-256'sı, katman sayımları, 10 kapı örneği ve kapı dışı 1 keşif örneği).
- Bu klasöre yalnız yürütücü yazar. Adım 5B'nin örneklem üreteci `model/ornekleme/uretec/` (Tamarin çalışması) ayrıdır.
