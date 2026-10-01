// Bağlama kontrolü: modül içe aktarılır, tür adlarına başvurulur; hiçbir doğrulama işlevi ÇAĞRILMAZ.
import JWTKit
print("modul JWTKit baglandi")
print("tip \(String(describing: JWTKeyCollection.self))")
print("tip \(String(describing: JWTAlgorithm.self))")
