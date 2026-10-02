# =====================================================================
#  PQ-OID4VC | Step 5A | small preprocessor for the ProVerif templates
# =====================================================================
#  Usage: awk -v DEFS="ROOT_PQ,CA_PQ" -f betik/pp.awk modeller/proverif/R1_chain.pvt > cikti.pv
#  Supported directives (at the start of a line): #ifdef NAME, #ifndef NAME, #else, #endif (may be nested).
#  A single flag name only; no Boolean expression. Directive lines are not written to the output.
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
END { if (depth != 0) { print "pp.awk: unclosed #ifdef" > "/dev/stderr"; exit 1 } }
