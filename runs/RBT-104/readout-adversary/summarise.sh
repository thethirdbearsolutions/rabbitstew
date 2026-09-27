#!/bin/bash
# RBT-104 readout adversary: one line per probe (POST HOC), from probes/*.txt, with the install and the host.
cd "$(dirname "$0")/probes"
for f in *.txt; do [ "$f" = SUMMARY.txt ] && continue
  inst=$(grep -o 'output w = [0-9.]*, input +-[0-9.]* (linear a = [0-9.]*)' "$f")
  base=$(awk '/^g[0-9]/{s+=$4;n++} END{printf "%.2f", s/n}' "$f")
  echo "${f%.txt} | $inst | mean lesioned base $base | $(grep -h '^LINE' "$f" | sed 's/^LINE [^:]*: //')"
done
