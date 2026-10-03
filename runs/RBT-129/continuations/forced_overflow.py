"""RBT-129 continuations: a FORCED EPA horizon overflow, on the instrumented build, in forked pool workers at the launch
WORKERS value (the Stage-2 plan adversary's item 1, relayed by the coordinator).

    /opt/rbt129-venvs/instr/bin/python runs/RBT-129/continuations/forced_overflow.py OUT_DIR [WORKERS]

The overflowing case is upstream's own regression for google-deepmind/mujoco#3646 (fix PR #3650, head f394095,
``test/engine/engine_collision_gjk_test.cc``): a cylinder against a 24-vertex convex hull whose EPA builds a 25-edge
horizon, run through the exported ``mjc_ccd`` with the test's config (max_iterations 1000, tolerance 1e-6) and its
support function (a direct argmax over the hull's vertices, as the test does, so the vertices keep their precision
and order).  It runs here as the ecology's bouts run: in a ``ProcessPoolExecutor`` (fork) of WORKERS processes, under
``epa_ecology.install``'s environment (RBT_HZN_LOG, RBT_HZN_UNIT, RBT_HZN_ATTEMPT), each worker replaying the case once.

What it checks, and prints (exit 0 only if all hold):
  - each worker that ran the case (all of them if none died; when one faults, the pool stops the rest) wrote its
    overflow line to the run's log, through the library's own O_APPEND write(2), with nedges > 24,
    this unit, this attempt, the worker's pid and a sequence number;
  - the lines arrived whether the worker then survived or died (stock behaviour after an overflow is undefined: either
    may happen, and FC-2 reads nothing into which); a worker that died is reported, with the pool's error;
  - ``epa_ecology.attested`` holds for (unit, attempt).
Guard off: what the overflow does after its line is written is undefined behaviour, here as in stock.
"""
import ctypes
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "launch"))
import epa_ecology  # noqa: E402
import mjbuild  # noqa: E402

mjtNum = ctypes.c_double
MAXCONPAIR = 50

# upstream's regression vertices (#3650, engine_collision_gjk_test.cc), verbatim
VERTICES = [
    (0.0192857398300826, 0.08690053994462224, 0.12097419707315368),
    (0.012714724723694176, 0.024107157414530199, 0.19175211498414968),
    (-0.0011256275721678258, 0.098217887198645215, 0.13850444948548318),
    (-0.018752134007769285, 0.047234769396963083, 0.1497708359846753),
    (0.045668230880901071, 0.060743174775825061, 0.17724322946299911),
    (-0.00086191888731417671, 0.098276507198356525, 0.13782006713140202),
    (0.038437554497325582, 0.07683494222154949, 0.15185771069290385),
    (-0.0088588157672199568, 0.08461301881630276, 0.13811505252552111),
    (-0.00054317638614224083, 0.098314970106874205, 0.13822590811731195),
    (0.038457417351559331, 0.07679515503857251, 0.15098725571869054),
    (-0.0013506305534411022, 0.098148803924522465, 0.13815000872258845),
    (-0.00047056039174176584, 0.098286491262649725, 0.13814422415961058),
    (-0.00066630751685884358, 0.098348969270490888, 0.13816114891308104),
    (-0.0011288320212504074, 0.098294459575060361, 0.13817455344055946),
    (-0.00087141037297690412, 0.098358808413634147, 0.13819917239730145),
    (-0.0014824987123017736, 0.097991238759218058, 0.13819153473514659),
    (-0.00073208609848285713, 0.098357791135834483, 0.1381526121045154),
    (-0.00053817830752837283, 0.0983148928109219, 0.13817846021820618),
    (0.018721713877566347, 0.087706476588619658, 0.16802865839004705),
    (-0.00042597771932059714, 0.098264696441667201, 0.13817887563321885),
    (-0.0010028463054115953, 0.098337468281656709, 0.1381870276042424),
    (-0.00060152151108238718, 0.09833463399211427, 0.13816978639941105),
    (-0.00047671920143554231, 0.098289886990783434, 0.13818711084128338),
    (0.019777916535283324, 0.087124075758308689, 0.12160763180585665),
]
XML = """<mujoco><worldbody>
  <geom type="cylinder" size=".035 .1" pos="0 .1 .1"/>
  <geom type="ellipsoid" size=".03 .04 .05" pos=".011571280096913501 .056467589149244865 .1562792693240185"/>
</worldbody></mujoco>"""
MESH_TYPE = 7  # mjGEOM_MESH


# engine_collision_convex.h's struct _mjCCDObj, 3.14.0 (the union's three variants, laid out by ctypes)
class _Mesh(ctypes.Structure):
    _fields_ = [("nvert", ctypes.c_int), ("mesh_polynum", ctypes.c_int)] + [(n, ctypes.c_void_p) for n in (
        "vert", "mpolymapadr", "mpolymapnum", "polymap", "polyvertadr", "polyvertnum", "polyvert", "polynormal", "graph",
        "extrema")]


class _Hfield(ctypes.Structure):
    _fields_ = [("prism", mjtNum * 18), ("hfield_data", ctypes.c_void_p), ("hfield_nrow", ctypes.c_int),
                ("hfield_ncol", ctypes.c_int)]


class _Flex(ctypes.Structure):
    _fields_ = [(n, ctypes.c_void_p) for n in ("elem", "dim", "aabb", "elemadr", "elemdataadr", "vert_xpos", "vertadr",
                                               "xradius")]


class _Data(ctypes.Union):
    _fields_ = [("mesh", _Mesh), ("hfield", _Hfield), ("flex", _Flex)]


class CCDObj(ctypes.Structure):
    pass


SUPPORT = ctypes.CFUNCTYPE(None, ctypes.POINTER(mjtNum), ctypes.POINTER(CCDObj), ctypes.POINTER(mjtNum))
CCDObj._fields_ = [("geom", ctypes.c_int), ("geom_type", ctypes.c_int), ("size", mjtNum * 4), ("pos", mjtNum * 3),
                   ("mat", mjtNum * 9), ("vertindex", ctypes.c_int), ("meshindex", ctypes.c_int), ("flex", ctypes.c_int),
                   ("elem", ctypes.c_int), ("vert", ctypes.c_int), ("margin", mjtNum), ("rotate", mjtNum * 4),
                   ("data", _Data), ("center", ctypes.c_void_p), ("support", ctypes.c_void_p)]


class CCDConfig(ctypes.Structure):
    _fields_ = [("max_iterations", ctypes.c_int), ("tolerance", mjtNum), ("max_contacts", ctypes.c_int),
                ("dist_cutoff", mjtNum), ("buffer", ctypes.c_void_p), ("npolygonmax", ctypes.c_int),
                ("nmeshdegmax", ctypes.c_int)]


class Vertex(ctypes.Structure):
    _fields_ = [("vert", mjtNum * 3), ("vert1", mjtNum * 3), ("vert2", mjtNum * 3), ("index1", ctypes.c_int),
                ("index2", ctypes.c_int)]


class CCDStatus(ctypes.Structure):
    _fields_ = [("separated", ctypes.c_int), ("dist", mjtNum * MAXCONPAIR), ("x1", mjtNum * (3 * MAXCONPAIR)),
                ("x2", mjtNum * (3 * MAXCONPAIR)), ("nx", ctypes.c_int), ("max_iterations", ctypes.c_int),
                ("tolerance", mjtNum), ("max_contacts", ctypes.c_int), ("dist_cutoff", mjtNum),
                ("gjk_iterations", ctypes.c_int), ("epa_iterations", ctypes.c_int), ("epa_status", ctypes.c_int),
                ("simplex", Vertex * 4), ("nsimplex", ctypes.c_int)]


@SUPPORT
def _hull_support(res, obj, d):
    best = max(range(len(VERTICES)), key=lambda i: (sum(VERTICES[i][k] * d[k] for k in range(3)), -i))
    for k in range(3):
        res[k] = VERTICES[best][k]
    obj.contents.vertindex = best


def replay(_=None) -> dict:
    """Upstream's #3646 case, once, in this process: what mjc_ccd returned (if it returned)."""
    import mujoco

    lib = ctypes.CDLL(mjbuild.loaded_libs()[0])
    m = mujoco.MjModel.from_xml_string(XML)
    d = mujoco.MjData(m)
    mujoco.mj_kinematics(m, d)
    lib.mjc_initCCDObj.argtypes = [ctypes.POINTER(CCDObj), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, mjtNum]
    o1, o2 = CCDObj(), CCDObj()
    lib.mjc_initCCDObj(ctypes.byref(o1), m._address, d._address, 0, 0.0)
    lib.mjc_initCCDObj(ctypes.byref(o2), m._address, d._address, 1, 0.0)
    o2.geom_type = MESH_TYPE
    o2.support = ctypes.cast(_hull_support, ctypes.c_void_p).value
    lib.mjc_ccdSize.restype = ctypes.c_size_t
    buf = ctypes.create_string_buffer(lib.mjc_ccdSize(0, 0, 1000))
    cfg = CCDConfig(max_iterations=1000, tolerance=1e-6, max_contacts=1, dist_cutoff=0.0,
                    buffer=ctypes.cast(buf, ctypes.c_void_p))
    st = CCDStatus()
    lib.mjc_ccd.restype = mjtNum
    dist = lib.mjc_ccd(ctypes.byref(cfg), ctypes.byref(st), ctypes.byref(o1), ctypes.byref(o2))
    return {"pid": os.getpid(), "dist": dist, "epa_iterations": st.epa_iterations, "nx": st.nx}


def clean_case(_=None) -> dict:
    """An ordinary contact (a cylinder on a box floor: the convex collider and EPA run, no overflow), stepped 200 times."""
    import mujoco

    m = mujoco.MjModel.from_xml_string("""<mujoco><worldbody><geom type="box" size="1 1 .1" pos="0 0 -.1"/>
      <body pos="0 0 .09"><freejoint/><geom type="cylinder" size=".1 .1"/></body></worldbody></mujoco>""")
    d = mujoco.MjData(m)
    for _ in range(200):
        mujoco.mj_step(m, d)
    return {"pid": os.getpid()}


def child(out: str, workers: int, case: str) -> int:
    """One attempt, as the ecology runs one: ``epa_ecology.install``, then a fork pool of ``workers`` running the case.
    A broken pool exits 1, as the ecology does when a bout's worker dies."""
    ident = mjbuild.check_instrumented()
    epa_ecology.install(out, ident, ["forced_overflow", case, "--workers", str(workers), "--out", out])
    fn = replay if case == "overflow" else clean_case
    with ProcessPoolExecutor(workers) as pool:  # Linux default: fork, as the ecology's BoutRunner
        res = list(pool.map(fn, range(workers)))
    print(json.dumps(res))
    return 0


def attempt(out: str, workers: int, case: str) -> tuple:
    """Run one attempt in a child process and write its exit line as run-lane does (``epa_ecology.write_exit``)."""
    import subprocess

    r = subprocess.run([sys.executable, os.path.abspath(__file__), "--child", out, str(workers), case],
                       capture_output=True, text=True)
    return r.returncode, epa_ecology.write_exit(out, r.returncode)["exit"]


def main(argv) -> int:
    if argv and argv[0] == "--child":
        return child(argv[1], int(argv[2]), argv[3])
    out = argv[0]
    workers = int(argv[1]) if len(argv) > 1 else int(os.environ.get("WORKERS", "2"))
    ident = mjbuild.check_instrumented()
    os.makedirs(out, exist_ok=True)
    log = os.path.join(out, mjbuild.EPA_LOG)
    unit = epa_ecology.unit_id(out)
    print(f"build {ident['libmujoco_sha256'][:12]}… {ident['build_id']}; unit {unit}; workers {workers}")
    ok = True
    for case in ("overflow", "clean"):
        a = epa_ecology.attempts(log)
        code, ex = attempt(out, workers, case)
        recs = [r for r in epa_ecology._records(log)]
        starts = [r for r in recs if "start" in r and r.get("attempt") == a]
        over = [r for r in recs if r.get("event") == "overflow" and r.get("attempt") == a and r.get("unit") == unit]
        hists = [r for r in recs if "hist" in r and r.get("attempt") == a]
        broken = [r["pool_broken"] for r in recs if "pool_broken" in r and r["pool_broken"].get("attempt") == a]
        att = epa_ecology.attested(log, unit, a)
        print(f"attempt {a} ({case}): exit code {code}; exit line {json.dumps(ex)}; start lines {len(starts)}"
              f" (workers {starts[0].get('workers') if starts else None}); overflow lines {len(over)}; histogram lines"
              f" {len(hists)}; pool_broken {json.dumps(broken)}; attested {att}")
        for r in over:
            print("  overflow line: " + json.dumps({k: r[k] for k in ("unit", "attempt", "pid", "seq", "nedges", "cap",
                                                                        "epa_iteration", "nverts", "nfaces", "step")}))
        if case == "overflow":
            # a faulting worker breaks the pool, which stops its sibling, perhaps before that one ran the case: at
            # least one worker's line, each with nedges > 24 and both ids; a native exit; attested
            ok &= (len(starts) == 1 and len(over) >= 1 and all(r["nedges"] > mjbuild.CAP and r["seq"] >= 1 for r in over)
                   and code != 0 and ex["native"] and ex["attempt"] == a and att)
        else:
            # no overflow, a clean exit, and every worker's histogram line in the log (forked workers leave via
            # os._exit; the wrapper's finalizer flushes them)
            ok &= (len(starts) == 1 and not over and code == 0 and not ex["native"] and len(hists) >= workers
                   and not att)
    print(f"FORCED OVERFLOW {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
