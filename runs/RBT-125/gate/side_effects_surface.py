"""RBT-125 §C, re-run of the surface rows on the fixed code (the coordinator's re-ruling of 03:10: the eating rule is
`--eat-from root --eat-rule surface`; the §C readout adversary #445 found the "+5.31" surface sweeper was mostly a
clearance leak, fixed in #446 (the minimal guard): under eat_rule = surface with
clear_from = root, no item is placed within eat_radius of an eating surface).  side_effects.py's instruments, unchanged, on the surface conditions only, plus root + surface:

  founders   RBT-113 seed-1 generation 0, 40 + 40, 8 draws (126000..): U-G0, U-G0/surface, U-G0/root, U-G0/root+surface,
             PW-G2.5, PW-G2.5/surface, PW-G2.5/root+surface
  corpus     RBT-90 seed 801's living at season 600, 60 + 60, 4 draws (127000..): U-G0, U-G0/surface, U-G0/root+surface,
             PW-G2.5/root+surface
  tumbler    the full-throttle rod at 0.45 and 6.46 m, 20 draws: U-G0, U-G0/surface, U-G0/root+surface, PW-G0/surface,
             PW-G0/root+surface

The U-G0, U-G0/root and PW-G2.5 rows repeat side_effects.txt's conditions on the fixed code: they do not use
eat_rule = surface, so they must reproduce those rows to the digit (a parity check of the fix).

    PYTHONPATH=<fixed tree> side_effects_surface.py BODIES_ROOT [--procs 2]
"""
import sys
import side_effects as se

se.FLAG.update({"root+surface": {"eat_from": "root", "eat_rule": "surface"}})
se.CONDS_FOUNDERS = ["U-G0", "U-G0/surface", "U-G0/root", "U-G0/root+surface", "PW-G2.5", "PW-G2.5/surface", "PW-G2.5/root+surface"]
se.CONDS_CORPUS = ["U-G0", "U-G0/surface", "U-G0/root+surface", "PW-G2.5/root+surface"]
se.CONDS_TUMBLER = ["U-G0", "U-G0/surface", "U-G0/root+surface", "PW-G0/surface", "PW-G0/root+surface"]

if __name__ == "__main__":
    import rabbitstew
    print(f"# fixed code: {rabbitstew.__file__}")
    se.main()
