// BİLGİ: jwt-kit 5.3.0'ın ML-DSA türleri @_spi(PostQuantum) arkasında; Linux'ta türe başvurarak bağlanır.
// Hiçbir anahtar üretilmez, imza doğrulanmaz.
@_spi(PostQuantum) import JWTKit
print("modul JWTKit (SPI PostQuantum) baglandi")
print("tip \(String(describing: MLDSA.self))")
