# =====================================================================
#  PQ-OID4VC | Adım 5A | ProVerif şablonları için küçük önişlemci
# =====================================================================
#  Kullanım: awk -v DEFS="ROOT_PQ,CA_PQ" -f betik/pp.awk modeller/proverif/R1_chain.pvt > cikti.pv
#  Desteklenen yönergeler (satır başında): #ifdef AD, #ifndef AD, #else, #endif (iç içe olabilir).
#  Yalnız tek bayrak adı; Boole ifadesi yok. Yönerge satırları çıktıya yazılmaz.
BEGIN {
  n = split(DEFS, a, ",")
  for (i = 1; i <= n; i++) if (a[i] != "") def[a[i]] = 1
  depth = 0; active[0] = 1
}
/^#ifdef[ \t]/  { depth++; cond = ($2 in def);  active[depth] = active[depth-1] && cond;  taken[depth] = cond; next }
/^#ifndef[ \t]/ { depth++; cond = !($2 in def); active[depth] = active[depth-1] && cond;  taken[depth] = cond; next }
/^#else/        { active[depth] = active[depth-1] && !taken[depth]; next }
/^#endif/       { depth--; next }
{ if (active[depth]) print }
END { if (depth != 0) { print "pp.awk: kapanmamış #ifdef" > "/dev/stderr"; exit 1 } }
