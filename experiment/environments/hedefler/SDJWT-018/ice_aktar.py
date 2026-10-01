# İçe aktarma kontrolü. Hiçbir işlev ÇAĞRILMAZ.
import importlib.metadata as md
import sd_jwt
from sd_jwt.verifier import SDJWTVerifier
print("modul=sd_jwt yuklendi; dagitim surumu=" + md.version("sd-jwt"))
print("sembol SDJWTVerifier", SDJWTVerifier.__name__)
print("bagimlilik jwcrypto " + md.version("jwcrypto"))
