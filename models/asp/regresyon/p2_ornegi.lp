% Pilot P2 topolojisi, yeni çekirdeğin olgu biçiminde (otomatik: regresyon/p2_regresyon.py)
sure(uzun,157680000). sure(sonsuz,2000000000).
param_alan(pilot_faz,coexist). param_alan(pilot_faz,post).
artefakt(lotl). sinif(lotl,pilot). imzali(lotl). karar(lotl). kanal(lotl,aktarilan). pencere_sabit(lotl,sonsuz).
artefakt(tl_pid). sinif(tl_pid,pilot). imzali(tl_pid). karar(tl_pid). kanal(tl_pid,aktarilan). pencere_sabit(tl_pid,sonsuz).
artefakt(tl_wp). sinif(tl_wp,pilot). imzali(tl_wp). karar(tl_wp). kanal(tl_wp,aktarilan). pencere_sabit(tl_wp,sonsuz).
artefakt(tl_rp). sinif(tl_rp,pilot). imzali(tl_rp). karar(tl_rp). kanal(tl_rp,aktarilan). pencere_sabit(tl_rp,sonsuz).
artefakt(ca_iss). sinif(ca_iss,pilot). imzali(ca_iss). karar(ca_iss). kanal(ca_iss,aktarilan). pencere_sabit(ca_iss,sonsuz).
artefakt(iss_cert). sinif(iss_cert,pilot). imzali(iss_cert). karar(iss_cert). kanal(iss_cert,aktarilan). pencere_sabit(iss_cert,sonsuz).
artefakt(meta). sinif(meta,pilot). imzali(meta). karar(meta). kanal(meta,aktarilan). pencere_sabit(meta,sonsuz).
artefakt(cred). sinif(cred,pilot). imzali(cred). karar(cred). kanal(cred,aktarilan). pencere_sabit(cred,sonsuz).
artefakt(status). sinif(status,pilot). imzali(status). karar(status). kanal(status,aktarilan). pencere_sabit(status,sonsuz).
artefakt(wua). sinif(wua,pilot). imzali(wua). karar(wua). kanal(wua,aktarilan). pencere_sabit(wua,sonsuz).
artefakt(kb). sinif(kb,pilot). imzali(kb). karar(kb). kanal(kb,aktarilan). pencere_sabit(kb,sonsuz).
artefakt(rp_cert). sinif(rp_cert,pilot). imzali(rp_cert). karar(rp_cert). kanal(rp_cert,aktarilan). pencere_sabit(rp_cert,sonsuz).
artefakt(req). sinif(req,pilot). imzali(req). karar(req). kanal(req,aktarilan). pencere_sabit(req,sonsuz).
kenar(p0,tl_pid,lotl).
kenar(p1,tl_wp,lotl).
kenar(p2,tl_rp,lotl).
kenar(p3,ca_iss,tl_pid).
kenar(p4,iss_cert,ca_iss).
kenar(p5,cred,iss_cert).
kenar(p6,meta,iss_cert).
kenar(p7,status,iss_cert).
kenar(p8,wua,tl_wp).
kenar(p9,kb,cred).
kenar(p10,rp_cert,tl_rp).
kenar(p11,req,rp_cert).
tasiyabilir(tl_pid,cred,m_f).
tasiyabilir(tl_pid,meta,m_f).
tasiyabilir(tl_pid,status,m_f).
tasiyabilir(meta,cred,m_f).
tasiyabilir(meta,status,m_f).
tasiyabilir(ca_iss,cred,m_f).
tasiyabilir(tl_rp,req,m_f).
tasiyabilir(rp_cert,req,m_f).
tasiyabilir(tl_wp,wua,m_f).
sabit(lotl). sabit_kosullu(tl_pid,capa,sabit).
klasik_alt_zorla(cred,pilot_faz,coexist).
klasik_alt_zorla(meta,pilot_faz,coexist).
klasik_alt_zorla(status,pilot_faz,coexist).
klasik_alt_zorla(req,pilot_faz,coexist).
klasik_alt_zorla(wua,pilot_faz,coexist).
wscd_artefakt(kb).
hedef_artefakt(g1,cred). ana_hedef(g1).
hedef_artefakt(g2,kb). ana_hedef(g2).
hedef_artefakt(g3,status). ana_hedef(g3).
hedef_artefakt(g4,req). ana_hedef(g4).
hedef_artefakt(g2i,wua). ana_hedef(g2i).
