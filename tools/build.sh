#!/bin/sh
# Step 2 — builds the tool images and prints their versions. From Git Bash: sh tools/build.sh
set -e
cd "$(dirname "$0")"
docker build -q -t pq-a02-tamarin:1.12.0 tamarin
docker build -q -t pq-a02-solver:1.0 solver
docker run --rm pq-a02-tamarin:1.12.0 sh -c 'tamarin-prover --version 2>&1 | head -2; maude --version 2>&1 | head -1'
docker run --rm pq-a02-solver:1.0 python -c "import clingo, z3; print('clingo', clingo.__version__, '| z3', z3.get_version_string())"
