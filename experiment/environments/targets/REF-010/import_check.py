# Import check: the plug-in packages and ACA-Py are loaded. NO function is called, no agent instance is started.
import importlib, importlib.metadata as md
for mod in ("acapy_agent", "oid4vc", "oid4vc.public_routes", "sd_jwt_vc", "jwt_vc_json"):
    importlib.import_module(mod)
    print("modul", mod, "yuklendi")
for d in ("acapy-agent", "aries-askar", "cryptography"):
    print("surum", d, md.version(d))
