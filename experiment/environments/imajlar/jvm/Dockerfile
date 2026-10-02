# pq-a09-env-jvm:1.0 — JVM environment (JDK 25 + Maven 3.9.16 + Gradle 9.6.1), Step 9 task 4a
# Bases: official Docker Hub images, pinned by digest. apt/apk are NOT used.
# Gradle 9.6.1 = the wrapper version of the EUDI verifier (REF-003); the distribution is copied from the official gradle image
# (the wrapper does not need to download from services.gradle.org). JDK 25 = required by jvmToolchain(25) of REF-003.
FROM gradle:9.6.1-jdk25-noble@sha256:b94f2560a917545c815a1dedbb0d0cfc9f31083c777dd2cb72235fbcd5cbe8e3 AS gradle
FROM maven:3.9.16-eclipse-temurin-25-noble@sha256:dd8e01b3be719853578c07b57ff8d9bbbbfe746f802226f05b19689420815221
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-jvm:1.0"
COPY --from=gradle /opt/gradle /opt/gradle
ENV GRADLE_HOME=/opt/gradle GRADLE_OPTS="-Dorg.gradle.welcome=never"
# Automatic toolchain download OFF (no foojay → JDK download); daemon off.
RUN set -eux; ln -s /opt/gradle/bin/gradle /usr/local/bin/gradle; mkdir -p /root/.gradle; \
    printf 'org.gradle.daemon=false\norg.gradle.java.installations.auto-download=false\norg.gradle.java.installations.auto-detect=true\n' > /root/.gradle/gradle.properties
COPY Yetenek.java /opt/pq/Yetenek.java
RUN set -eux; echo "SURUM $(java -version 2>&1 | head -2 | tr '\n' ' ')"; echo "SURUM $(mvn -v 2>&1 | head -1)"; \
    echo "SURUM $(gradle --version 2>/dev/null | grep -E '^Gradle')"; echo "SURUM $(git --version)"; echo "SURUM sistem $(openssl version)"; \
    java /opt/pq/Yetenek.java
