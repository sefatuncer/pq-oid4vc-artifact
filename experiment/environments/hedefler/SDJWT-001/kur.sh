#!/usr/bin/env bash
# SDJWT-001 — Gradle modül meta verisiyle (kanonik koordinat). Maven sonucu: cikti-maven/. İmza doğrulama YOK.
export GAV=at.asitplus.wallet:vck:7.0.1 HEDEF_JAR=vck-jvm-7.0.1.jar
exec bash /b/gradle-lib.sh
