# İçe aktarma kontrolü: modül yüklenir, API sembollerinin varlığı yazılır. Hiçbir işlev ÇAĞRILMAZ.
import jwt
print("modul=jwt (pyjwt) yuklendi; surum=" + jwt.__version__)
print("sembol decode", callable(getattr(jwt, "decode", None)))
print("sembol PyJWS.register_algorithm", hasattr(jwt.PyJWS, "register_algorithm"))
