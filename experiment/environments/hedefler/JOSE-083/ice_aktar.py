# Import check: the module is loaded and the presence of the API symbols is written. NO function is called.
import jwt
print("modul=jwt (pyjwt) yuklendi; surum=" + jwt.__version__)
print("sembol decode", callable(getattr(jwt, "decode", None)))
print("sembol PyJWS.register_algorithm", hasattr(jwt.PyJWS, "register_algorithm"))
