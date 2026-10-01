# C3 adaptörü (JVM/Kotlin). Önce: sh derle.sh <t>. Sonra: docker build --build-arg T=<t> -t a10-kt-<t>:1 .
# T=cose → COSE-001 (Signum indispensable-cosef 3.26.0 + supreme 0.16.0); T=sdjwt → SDJWT-001 (vck 7.0.1).
# Sürümler build.gradle.kts'de sabit; çözülen ağaç /a/dep-tree.txt.
FROM pq-a09-env-jvm:1.0
ARG T
COPY build-${T}/kt-adaptor /a/app
COPY build-${T}/dep-tree.txt /a/
COPY src/common /a/src/common
COPY src/${T} /a/src/${T}
ENTRYPOINT ["/a/app/bin/kt-adaptor"]
