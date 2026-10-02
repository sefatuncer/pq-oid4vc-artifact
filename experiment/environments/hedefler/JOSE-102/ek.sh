# JOSE-102 additional record (information; static): build conditions of the jwt-kit ML-DSA source (#if / @available). NO signature verification.
grep -rn -E "^\s*#if|@available|canImport" /tmp/p/.build/checkouts/jwt-kit/Sources/JWTKit/MLDSA/ 2>/dev/null | head -20 | tee "$C/mldsa-kosullar.txt"
