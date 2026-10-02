# Import check. NO function is called.
import jose
from jose import jws, jwt
from jose.backends import ECKey, RSAKey
print("modul=jose (python-jose) yuklendi; surum=" + jose.__version__)
print("sembol jws.verify", callable(jws.verify), "; jwt.decode", callable(jwt.decode))
print("secilen arka uc: ECKey=" + ECKey.__module__ + " RSAKey=" + RSAKey.__module__)
