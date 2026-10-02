#!/usr/bin/env bash
# COSE-001 — Gradle modül meta verisiyle (kanonik koordinat). Maven sonucu: cikti-maven/. İmza doğrulama YOK.
export GAV=at.asitplus.signum:indispensable-cosef:3.26.0 HEDEF_JAR=indispensable-cosef-jvm-3.26.0.jar
exec bash /b/gradle-lib.sh
