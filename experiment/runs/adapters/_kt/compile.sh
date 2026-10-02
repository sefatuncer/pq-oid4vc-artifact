#!/bin/sh
# Builds the Kotlin adapter in a container (Gradle cache in the named volume pq-a10-kt-gradle; deleted by name when the work is done).
# Usage: sh compile.sh cose|sdjwt   → build-<t>/kt-adaptor (installDist) + build-<t>/dep-tree.txt
set -e
T=$1
MSYS_NO_PATHCONV=1 docker run --rm -e GRADLE_USER_HOME=/gh -v pq-a10-kt-gradle:/gh -v "$(cygpath -m "$(pwd)" 2>/dev/null || pwd):/src" pq-a09-env-jvm:1.0 sh -c "
  set -e; rm -rf /tmp/w; mkdir /tmp/w; cp -r /src/build.gradle.kts /src/settings.gradle.kts /src/src /tmp/w/; cd /tmp/w
  gradle -q --no-daemon -Pt=$T installDist
  gradle -q --no-daemon -Pt=$T dependencies --configuration runtimeClasspath > dep-tree.txt
  rm -rf /src/build-$T; mkdir -p /src/build-$T; cp -r build/install/kt-adaptor /src/build-$T/; cp dep-tree.txt /src/build-$T/"
