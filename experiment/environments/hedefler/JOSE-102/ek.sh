# JOSE-102 ek kayıt (bilgi; statik): jwt-kit ML-DSA kaynağının derleme koşulları (#if / @available). İmza doğrulama YOK.
grep -rn -E "^\s*#if|@available|canImport" /tmp/p/.build/checkouts/jwt-kit/Sources/JWTKit/MLDSA/ 2>/dev/null | head -20 | tee "$C/mldsa-kosullar.txt"
