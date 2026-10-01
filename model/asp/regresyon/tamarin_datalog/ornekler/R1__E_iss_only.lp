% Tamarin R1 E_iss_only bayraklar=ISS_PQ (otomatik üretildi: regresyon/tamarin_esdegerlik.py)
sure(uzun,157680000). sure(sonsuz,2000000000).
artefakt(ca_cert). sinif(ca_cert,ornek). imzali(ca_cert). pencere_sabit(ca_cert,sonsuz). kanal(ca_cert,aktarilan). sabit(ca_cert). 
artefakt(iss_cert). sinif(iss_cert,ornek). imzali(iss_cert). pencere_sabit(iss_cert,sonsuz). kanal(iss_cert,aktarilan). 
artefakt(cred). sinif(cred,ornek). imzali(cred). pencere_sabit(cred,sonsuz). kanal(cred,aktarilan). 
kenar(e1,iss_cert,ca_cert). kenar(e2,cred,iss_cert).
hedef_artefakt(g1,cred). ana_hedef(g1).
