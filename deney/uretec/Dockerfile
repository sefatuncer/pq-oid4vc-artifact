# pq-a09-credgen — PQ-OID4VC Adim 9b: SD-JWT VC / KB-JWT / TSL / OID4VP istek / DPoP ve test vektoru ureteci
#
# Taban: yerel pq-a09-signer:1.0 (deney/imzalayici; python:3.11-slim@sha256:9534e5a8...; OpenSSL 3.5.7;
#        cryptography 50.0.1). Yerel imaj oldugu icin ozetle degil etiketle cagrilir; kullanilan imaj
#        kimligi README'de kayitlidir. Ek paket YOK.
# Surumler: 1.0 = v1'i ureten insa; 1.1 = + uretec/v11.py (v1.1) ve boyut_dpop.py;
#           1.2 = + uretec/v12.py (v1.2) ve esleme.py (BATARYA-ESLEME.md).
#           1.3 = + uretec/cbor.py, cose.py (COSE_Sign/COSE_Sign1), v13.py (v1.3: COSE + L4c eski ihracci),
#                 esleme.py v1.3 bolumleri, testler t10_cose.py ve t12_cose.py. v1, v1.1, v1.2 uretim kodu degismedi.
# Insa:   docker build -t pq-a09-credgen:1.3 deney/uretec
# Uretim (v1.3; donmus v1, v1.1, v1.2 ve anahtarlar/v1 salt-okunur baglanir):
#   docker run --rm --name pq-a09-credgen -v <kok>:/work -v <kok>/vektorler/v1:/work/vektorler/v1:ro
#     -v <kok>/vektorler/v1.1:/work/vektorler/v1.1:ro -v <kok>/vektorler/v1.2:/work/vektorler/v1.2:ro
#     -v <kok>/anahtarlar/v1:/work/anahtarlar/v1:ro pq-a09-credgen:1.3
# Esleme:  ... -v <proje>/00-on-kayit:/onkayit:ro pq-a09-credgen:1.3 python -m uretec.esleme /work /onkayit/ON-KAYIT-TASLAK.md
# Onceki setler: python -m uretec.uret /work (v1), python -m uretec.v11 /work (v1.1), python -m uretec.v12 /work (v1.2)
FROM pq-a09-signer:1.0

LABEL org.opencontainers.image.title="pq-a09-credgen" \
      org.opencontainers.image.version="1.3" \
      org.opencontainers.image.description="PQ-OID4VC 9b: kimlik bilgisi ve test vektoru ureteci (v1, v1.1, v1.2, v1.3)"

COPY uretec /opt/uretec/uretec
COPY testler /opt/uretec/testler
ENV PYTHONPATH=/opt/pq:/opt/uretec

RUN python -c "import uretec, uretec.vektorler, uretec.uret, uretec.v11, uretec.boyut_dpop, uretec.v12, uretec.esleme, uretec.cbor, uretec.cose, uretec.v13; print('uretec', uretec.__version__)"

WORKDIR /work
CMD ["python", "-m", "uretec.v13", "/work"]
