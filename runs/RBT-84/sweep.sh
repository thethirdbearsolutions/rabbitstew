#!/bin/bash
# RBT-84: the four autopsies at 64 draws (not 12 -- RBT-28's adversary showed 12 cannot test a 25%
# effect). Run in parallel across the box's four cores.
R=runs/RBT-84/forage-807
for g in 590 500 300 100; do
  ( echo "##### holistic g$g #####"; python3 scripts/forage_lab.py "$R" holistic "$g" 64 120 2>&1 | grep -v WARNING ) \
    > "runs/RBT-84/lab_g${g}.txt" &
done
wait
cat runs/RBT-84/lab_g590.txt runs/RBT-84/lab_g500.txt runs/RBT-84/lab_g300.txt runs/RBT-84/lab_g100.txt > runs/RBT-84/lab.txt
echo "##### SWEEP COMPLETE #####" >> runs/RBT-84/lab.txt
