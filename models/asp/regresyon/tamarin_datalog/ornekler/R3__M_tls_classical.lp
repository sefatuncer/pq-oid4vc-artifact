% Tamarin R3 M_tls_classical bayraklar=VIA_TLS (otomatik üretildi: regresyon/tamarin_esdegerlik.py)
sure(uzun,157680000). sure(sonsuz,2000000000).
artefakt(cred). sinif(cred,ornek). imzali(cred). pencere_sabit(cred,sonsuz). kanal(cred,aktarilan). sabit(cred). karar(cred). 
hedef_artefakt(g1,cred). ana_hedef(g1).
artefakt(chan_key). sinif(chan_key,ornek). imzali(chan_key). pencere_sabit(chan_key,sonsuz). kanal(chan_key,aktarilan). sabit(chan_key). 
artefakt(resp). sinif(resp,ornek). imzasiz(resp). kanal(resp,yalniz_tasima). 
tasima(resp,t_chan). tasima_anahtari(t_chan,chan_key). tasiyabilir(resp,cred,m_f).
