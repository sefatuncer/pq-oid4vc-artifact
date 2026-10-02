#!/bin/sh
# Step 2 acceptance test: reproduces the design-stage pilots P1 (Tamarin) and P2 (ASP + z3) of set B with the new images.
# Expected (raw outputs of B): V1,V2,V3,V6 falsified; V4,V5 verified; L2 verified; L1 timeout; P2 z3–clingo 48/48.
set -e
cd "$(dirname "$0")"
P1=$(cygpath -m "$PWD/p1"); P2=$(cygpath -m "$PWD/p2")
export MSYS_NO_PATHCONV=1
T="docker run --rm --memory=12g --memory-swap=12g -v $P1:/work pq-a02-tamarin:1.12.0 sh /work/run_p1.sh"
{
$T V1_base 300 weakest_link.spthy
$T V2_expectTL 300 weakest_link.spthy -D=EXPECT_IN_TL
$T V3_tlPQ 300 weakest_link.spthy -D=TL_PQ
$T V4_tlPQ_expectTL 300 weakest_link.spthy -D=TL_PQ -D=EXPECT_IN_TL
$T V5_tlPQ_nocoexist 300 weakest_link.spthy -D=TL_PQ -D=NO_COEXIST
$T V6_tlClassical_nocoexist 300 weakest_link.spthy -D=NO_COEXIST
$T L2_induction 300 delegation_loop.spthy -D=INDUCTION
$T L1_noinduction 60 delegation_loop.spthy
} 2>&1 | tee results/p1_summary.txt
docker run --rm -v $P2:/work -w /work pq-a02-solver:1.0 python run_p2.py > results/p2_stdout.txt 2>&1
