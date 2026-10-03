// RBT-133 spike: rabbitstew's arena bout in C, so that it can run inside WebAssembly (and, for comparison, natively).
//
//   rbt_wasm compile  DIR OUT.mjb   compile DIR/model.xml with this build's MuJoCo and save it
//   rbt_wasm openloop DIR OUTDIR    load DIR/model.mjb (the reference platform's compiled model) and DIR/init_state.bin,
//                                   drive DIR/ctrl.bin open loop; write OUTDIR/states.bin (one state row per mj_step)
//   rbt_wasm bout     DIR OUTDIR    the closed loop: compile DIR/model.xml here, settle, then run the bout with the
//                                   brains and sensors of DIR/pack.txt; write OUTDIR/states.bin (settle steps first),
//                                   OUTDIR/ticks.bin (per tick: sensors, activations, ctrl) and OUTDIR/result.txt
//   rbt_wasm bench    DIR N         run the closed-loop bout N times and print seconds per bout and per mj_step
//
// A state row is time, qpos, qvel, act, qacc_warmstart as float64: the bytes spikes/wasm/locate/probe.py hashes.
//
// It mirrors rabbitstew/simulation.py (Simulation.settle with settle_until_rest off, Simulation.step, run_bout's
// distances and zero_sum_fitness) and rabbitstew/brain.py (RuntimeBrain.step, effector_output) for the arena's rich
// sensor set.  Sums run in a fixed left-to-right order; transcendental functions are this toolchain's libm (in WASM:
// Emscripten's musl, itself compiled to WASM, so the same instructions on every host).

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include <mujoco/mujoco.h>

#define MAXR 4

// from the RBT-129 patch (src/engine/engine_rbt_hzn.h): proves the patched engine is the one linked
const char* rbt_hzn_build_id(void);

typedef struct {
  int unit, kind, axis, body, geom, jid, ball;
  double span, freq, phase;
} Sensor;

typedef struct {
  int aid, nunits;
  int* units;
} Act;

typedef struct {
  int root_body, root_qpos_adr, is_static, opp_root_body;
  double spawn[2];
  int nbodies;
  int* bodies;
  int n;  // units
  double *bias, *W, *a, *x, *prev, *nw;
  int* func;
  int nsens;
  Sensor* sens;
  int nact;
  Act* acts;
  int exploded;
} Robot;

typedef struct {
  int substeps, settle_steps, ticks, nu, nrobots;
  double control_dt, explosion_speed, target[3];
  Robot r[MAXR];
} Pack;

static void die(const char* msg, const char* arg) {
  fprintf(stderr, "rbt_wasm: %s %s\n", msg, arg ? arg : "");
  exit(2);
}

static char* path(const char* dir, const char* f) {
  static char buf[4][1024];
  static int k;
  k = (k + 1) & 3;
  snprintf(buf[k], sizeof buf[k], "%s/%s", dir, f);
  return buf[k];
}

static void expect(FILE* f, const char* word) {
  char w[64];
  if (fscanf(f, "%63s", w) != 1 || strcmp(w, word)) die("pack.txt: expected", word);
}

static double rd(FILE* f) {
  char w[64];
  if (fscanf(f, "%63s", w) != 1) die("pack.txt: short read", NULL);
  return strtod(w, NULL);  // C99 hex floats round-trip exactly
}

static int ri_(FILE* f) {
  int v;
  if (fscanf(f, "%d", &v) != 1) die("pack.txt: expected an int", NULL);
  return v;
}

static void load_pack(const char* dir, Pack* p) {
  FILE* f = fopen(path(dir, "pack.txt"), "r");
  if (!f) die("cannot open", path(dir, "pack.txt"));
  expect(f, "substeps"); p->substeps = ri_(f);
  expect(f, "settle_steps"); p->settle_steps = ri_(f);
  expect(f, "ticks"); p->ticks = ri_(f);
  expect(f, "control_dt"); p->control_dt = rd(f);
  expect(f, "explosion_speed"); p->explosion_speed = rd(f);
  expect(f, "target"); for (int i = 0; i < 3; i++) p->target[i] = rd(f);
  expect(f, "nu"); p->nu = ri_(f);
  expect(f, "robots"); p->nrobots = ri_(f);
  if (p->nrobots > MAXR) die("too many robots", NULL);
  for (int k = 0; k < p->nrobots; k++) {
    Robot* R = &p->r[k];
    memset(R, 0, sizeof *R);
    expect(f, "robot"); ri_(f);
    expect(f, "root_body"); R->root_body = ri_(f);
    expect(f, "root_qpos_adr"); R->root_qpos_adr = ri_(f);
    expect(f, "static"); R->is_static = ri_(f);
    expect(f, "spawn"); R->spawn[0] = rd(f); R->spawn[1] = rd(f);
    expect(f, "opp_root_body"); R->opp_root_body = ri_(f);
    // bodies: the rest of the line
    expect(f, "bodies");
    R->bodies = malloc(sizeof(int) * 256);
    int c;
    while ((c = fgetc(f)) == ' ') {
      if (fscanf(f, "%d", &R->bodies[R->nbodies]) == 1) R->nbodies++;
    }
    expect(f, "units"); int n = R->n = ri_(f);
    R->bias = calloc(n ? n : 1, sizeof(double));
    R->W = calloc(n * n ? n * n : 1, sizeof(double));
    R->a = calloc(n ? n : 1, sizeof(double));
    R->x = calloc(n ? n : 1, sizeof(double));
    R->prev = calloc(n ? n : 1, sizeof(double));
    R->nw = calloc(n ? n : 1, sizeof(double));
    R->func = calloc(n ? n : 1, sizeof(int));
    expect(f, "bias"); for (int i = 0; i < n; i++) R->bias[i] = rd(f);
    expect(f, "W"); for (int i = 0; i < n * n; i++) R->W[i] = rd(f);
    expect(f, "func"); for (int i = 0; i < n; i++) R->func[i] = ri_(f);
    expect(f, "sensors"); R->nsens = ri_(f);
    R->sens = calloc(R->nsens ? R->nsens : 1, sizeof(Sensor));
    for (int i = 0; i < R->nsens; i++) {
      Sensor* s = &R->sens[i];
      expect(f, "s");
      s->unit = ri_(f); s->kind = ri_(f); s->axis = ri_(f); s->body = ri_(f); s->geom = ri_(f); s->jid = ri_(f);
      s->ball = ri_(f); s->span = rd(f); s->freq = rd(f); s->phase = rd(f);
    }
    expect(f, "actuators"); R->nact = ri_(f);
    R->acts = calloc(R->nact ? R->nact : 1, sizeof(Act));
    for (int i = 0; i < R->nact; i++) {
      expect(f, "a");
      R->acts[i].aid = ri_(f);
      R->acts[i].nunits = ri_(f);
      R->acts[i].units = calloc(R->acts[i].nunits ? R->acts[i].nunits : 1, sizeof(int));
      for (int j = 0; j < R->acts[i].nunits; j++) R->acts[i].units[j] = ri_(f);
    }
  }
  fclose(f);
}

// ---- state rows -------------------------------------------------------------------------------------------------
static FILE* g_states;
static uint64_t g_fnv = 1469598103934665603ULL;
static long g_steps;

static void put(const double* v, int n) {
  if (g_states) fwrite(v, sizeof(double), n, g_states);
  const unsigned char* b = (const unsigned char*)v;
  for (size_t i = 0; i < sizeof(double) * (size_t)n; i++) {
    g_fnv ^= b[i];
    g_fnv *= 1099511628211ULL;
  }
}

static void row(const mjModel* m, const mjData* d) {
  put(&d->time, 1);
  put(d->qpos, m->nq);
  put(d->qvel, m->nv);
  put(d->act, m->na);
  put(d->qacc_warmstart, m->nv);
}

static void step(const mjModel* m, mjData* d) {
  mj_step(m, d);
  g_steps++;
  row(m, d);
}

// ---- the simulation, after rabbitstew/simulation.py -------------------------------------------------------------
static double norm3(const double* v) { return sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]); }

static void settle(const mjModel* m, mjData* d, const Pack* p) {
  mju_zero(d->ctrl, m->nu);
  for (int i = 0; i < p->settle_steps; i++) step(m, d);
  mju_zero(d->qvel, m->nv);
  mju_zero(d->qacc, m->nv);
  if (m->na) mju_zero(d->act, m->na);
  for (int k = 0; k < p->nrobots; k++) {
    const Robot* R = &p->r[k];
    if (R->root_qpos_adr < 0) continue;
    mj_forward(m, d);
    const double* com = d->subtree_com + 3 * R->root_body;
    d->qpos[R->root_qpos_adr] += R->spawn[0] - com[0];
    d->qpos[R->root_qpos_adr + 1] += R->spawn[1] - com[1];
  }
  d->time = 0.0;
  mj_forward(m, d);
}

static int touching(const mjModel* m, const mjData* d, int body) {
  for (int i = 0; i < d->ncon; i++) {
    const mjContact* c = d->contact + i;
    if (m->geom_bodyid[c->geom[0]] == body || m->geom_bodyid[c->geom[1]] == body) return 1;
  }
  return 0;
}

static void sensors(const mjModel* m, mjData* d, const Pack* p, Robot* R, double t, double* out) {
  double v6[6];
  for (int k = 0; k < R->nsens; k++) {
    const Sensor* s = &R->sens[k];
    double val = 0.0;
    switch (s->kind) {
      case 0:  // contact
        val = touching(m, d, s->body) ? 1.0 : 0.0;
        break;
      case 1:  // oscillator: sin(2*pi*freq*t + phase), Python's left-to-right order
        val = sin(2.0 * M_PI * s->freq * t + s->phase);
        break;
      case 2: case 3: case 4: case 5: {  // target / opponent direction and distance
        const double* point;
        if (s->kind == 2 || s->kind == 4) {
          point = p->target;
        } else {
          if (R->opp_root_body < 0) break;
          point = d->xpos + 3 * R->opp_root_body;
        }
        const double* gx = d->geom_xpos + 3 * s->geom;
        double v[3] = {point[0] - gx[0], point[1] - gx[1], point[2] - gx[2]};
        if (s->kind >= 4) {
          double dist = sqrt(v[0] * v[0] + v[1] * v[1]);
          val = dist / (1.0 + dist);
          break;
        }
        double n = norm3(v);
        if (n < 1e-9) break;
        const double* R9 = d->geom_xmat + 9 * s->geom;  // local = R^T (v/n)
        double u[3] = {v[0] / n, v[1] / n, v[2] / n};
        val = R9[0 * 3 + s->axis] * u[0] + R9[1 * 3 + s->axis] * u[1] + R9[2 * 3 + s->axis] * u[2];
        break;
      }
      case 6:  // up: row 2 of geom_xmat
        val = d->geom_xmat[9 * s->geom + 6 + s->axis];
        break;
      case 7:  // velocity: local linear velocity of the geom, tanh
        mj_objectVelocity(m, d, mjOBJ_GEOM, s->geom, v6, 1);
        val = tanh(v6[3 + s->axis]);
        break;
      case 8:  // height
        val = tanh(d->geom_xpos[3 * s->geom + 2]);
        break;
      case 9: case 10: {  // joint angle / velocity
        if (s->jid < 0) break;
        if (s->ball) {
          if (s->kind == 9) {
            double w = fabs(d->qpos[m->jnt_qposadr[s->jid]]);
            w = w < 0.0 ? 0.0 : (w > 1.0 ? 1.0 : w);
            val = 2.0 * acos(w) / M_PI;
          } else {
            const double* qv = d->qvel + m->jnt_dofadr[s->jid];
            val = tanh(norm3(qv) / 5.0);
          }
        } else if (s->kind == 9) {
          double q = d->qpos[m->jnt_qposadr[s->jid]];
          if (s->span >= 0) {
            double r = q / s->span;
            val = r < -1.0 ? -1.0 : (r > 1.0 ? 1.0 : r);
          } else {
            val = sin(q);
          }
        } else {
          val = tanh(d->qvel[m->jnt_dofadr[s->jid]] / 5.0);
        }
        break;
      }
      default:
        die("unknown sensor kind", NULL);
    }
    out[k] = val;
  }
}

static double signd(double x) { return x > 0 ? 1.0 : (x < 0 ? -1.0 : x); }  // np.sign: 0 -> 0, nan -> nan

static void brain_step(Robot* R, const double* sv) {
  int n = R->n;
  if (!n) return;
  for (int i = 0; i < n; i++) {  // x = W a + b, each row summed left to right
    double acc = 0.0;
    const double* w = R->W + (size_t)i * n;
    for (int j = 0; j < n; j++) acc += w[j] * R->a[j];
    R->x[i] = acc + R->bias[i];
  }
  for (int i = 0; i < n; i++) {
    double xi = R->x[i], v = 0.0;
    switch (R->func[i]) {
      case -1: v = 0.0; break;  // a sensor: overwritten below
      case 0: v = tanh(xi); break;
      case 1: v = sin(xi); break;
      case 2: v = tanh(fabs(xi)); break;
      case 3: v = tanh(xi > 0.0 ? xi : 0.0); break;
      case 4: v = signd(xi); break;
      case 5: { v = 0.9 * R->a[i] + 0.2 * tanh(xi); v = v < -1.0 ? -1.0 : (v > 1.0 ? 1.0 : v); break; }
      case 6: v = tanh(xi - R->prev[i]); break;
      default: die("unknown transfer function", NULL);
    }
    R->nw[i] = v;
  }
  memcpy(R->prev, R->x, sizeof(double) * n);
  for (int k = 0; k < R->nsens; k++) R->nw[R->sens[k].unit] = sv[k];
  memcpy(R->a, R->nw, sizeof(double) * n);
}

static void check_explosions(const mjModel* m, const mjData* d, Pack* p) {
  for (int i = 0; i < m->nq; i++) if (!isfinite(d->qpos[i])) goto all;
  for (int i = 0; i < m->nv; i++) if (!isfinite(d->qvel[i])) goto all;
  for (int k = 0; k < p->nrobots; k++) {
    Robot* R = &p->r[k];
    if (R->exploded || R->is_static) continue;
    double mx = -1.0;
    for (int b = 0; b < R->nbodies; b++) {
      const double* c = d->cvel + 6 * R->bodies[b] + 3;
      double sp = norm3(c);
      if (sp > mx || isnan(sp)) mx = sp;
    }
    if (mx > p->explosion_speed) R->exploded = 1;
  }
  return;
all:
  for (int k = 0; k < p->nrobots; k++) p->r[k].exploded = 1;
}

static mjModel* compile_xml(const char* file) {
  char err[1000] = "";
  mjModel* m = mj_loadXML(file, NULL, err, sizeof err);
  if (!m) die("compile failed:", err);
  return m;
}

// returns the number of mj_steps taken; fills dist[] and fit[]
static long run_bout(const char* dir, Pack* p, FILE* ticks_out, double* dist, double* fit) {
  mjModel* m = compile_xml(path(dir, "model.xml"));
  mjData* d = mj_makeData(m);
  if (m->nu != p->nu) die("nu differs from pack.txt", NULL);
  for (int k = 0; k < p->nrobots; k++) {
    Robot* R = &p->r[k];
    R->exploded = 0;
    if (R->n) { memset(R->a, 0, sizeof(double) * R->n); memset(R->prev, 0, sizeof(double) * R->n); }
  }
  long s0 = g_steps;
  settle(m, d, p);
  double sv[1024];
  int tick = 0;
  double t = 0.0;
  for (int it = 0; it < p->ticks; it++) {
    for (int k = 0; k < p->nrobots; k++) {
      Robot* R = &p->r[k];
      if (R->exploded) continue;
      sensors(m, d, p, R, t, sv);
      brain_step(R, sv);
      if (ticks_out) { fwrite(sv, sizeof(double), R->nsens, ticks_out); }
      for (int a = 0; a < R->nact; a++) {
        const Act* A = &R->acts[a];
        double sum = 0.0;
        for (int j = 0; j < A->nunits; j++) sum += R->a[A->units[j]];
        d->ctrl[A->aid] = A->nunits ? (sum < -1.0 ? -1.0 : (sum > 1.0 ? 1.0 : sum)) : 0.0;
      }
    }
    if (ticks_out) {
      for (int k = 0; k < p->nrobots; k++) fwrite(p->r[k].a, sizeof(double), p->r[k].n, ticks_out);
      fwrite(d->ctrl, sizeof(double), m->nu, ticks_out);
    }
    for (int s = 0; s < p->substeps; s++) step(m, d);
    tick++;
    t = tick * p->control_dt;
    check_explosions(m, d, p);
  }
  int ex[MAXR];
  for (int k = 0; k < p->nrobots; k++) {
    const double* com = d->subtree_com + 3 * p->r[k].root_body;
    double dx = com[0] - p->target[0], dy = com[1] - p->target[1];
    dist[k] = sqrt(dx * dx + dy * dy);
    ex[k] = p->r[k].exploded;
  }
  // zero_sum_fitness, two robots
  if (ex[0] && ex[1]) { fit[0] = fit[1] = 0.5; }
  else if (ex[0]) { fit[0] = 0.0; fit[1] = 1.0; }
  else if (ex[1]) { fit[0] = 1.0; fit[1] = 0.0; }
  else {
    double total = dist[0] + dist[1];
    if (total < 1e-9) { fit[0] = fit[1] = 0.5; }
    else { fit[0] = dist[1] / total; fit[1] = dist[0] / total; }
  }
  mj_deleteData(d);
  mj_deleteModel(m);
  return g_steps - s0;
}

static double now(void) {
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return ts.tv_sec + 1e-9 * ts.tv_nsec;
}

static void load_bin(const char* file, double* out, size_t n) {
  FILE* f = fopen(file, "rb");
  if (!f) die("cannot open", file);
  if (fread(out, sizeof(double), n, f) != n) die("short read", file);
  fclose(f);
}

int main(int argc, char** argv) {
  if (argc < 3) die("usage: rbt_wasm compile|openloop|bout|bench DIR ...", NULL);
  const char* cmd = argv[1];
  const char* dir = argv[2];
  printf("rbt_wasm: MuJoCo %s, %s\n", mj_versionString(), rbt_hzn_build_id());
  if (!strcmp(cmd, "compile")) {
    if (argc < 4) die("usage: compile DIR OUT.mjb", NULL);
    mjModel* m = compile_xml(path(dir, "model.xml"));
    mj_saveModel(m, argv[3], NULL, 0);
    printf("compiled %s -> %s\n", path(dir, "model.xml"), argv[3]);
    return 0;
  }
  Pack p;
  load_pack(dir, &p);
  if (!strcmp(cmd, "openloop")) {
    if (argc < 4) die("usage: openloop DIR OUTDIR", NULL);
    mjModel* m = mj_loadModel(path(dir, "model.mjb"), NULL);
    if (!m) die("cannot load", path(dir, "model.mjb"));
    mjData* d = mj_makeData(m);
    size_t ns = 1 + m->nq + 2 * m->nv + m->na;
    double* st = malloc(sizeof(double) * ns);
    load_bin(path(dir, "init_state.bin"), st, ns);
    size_t o = 0;
    d->time = st[o++];
    memcpy(d->qpos, st + o, sizeof(double) * m->nq); o += m->nq;
    memcpy(d->qvel, st + o, sizeof(double) * m->nv); o += m->nv;
    memcpy(d->act, st + o, sizeof(double) * m->na); o += m->na;
    memcpy(d->qacc_warmstart, st + o, sizeof(double) * m->nv);
    mj_forward(m, d);
    double* ctrl = malloc(sizeof(double) * (size_t)p.ticks * m->nu);
    load_bin(path(dir, "ctrl.bin"), ctrl, (size_t)p.ticks * m->nu);
    g_states = fopen(path(argv[3], "states.bin"), "wb");
    if (!g_states) die("cannot write", path(argv[3], "states.bin"));
    for (int t = 0; t < p.ticks; t++) {
      memcpy(d->ctrl, ctrl + (size_t)t * m->nu, sizeof(double) * m->nu);
      for (int s = 0; s < p.substeps; s++) step(m, d);
    }
    fclose(g_states);
    printf("openloop: %ld steps, digest %016llx\n", g_steps, (unsigned long long)g_fnv);
    return 0;
  }
  if (!strcmp(cmd, "bout")) {
    if (argc < 4) die("usage: bout DIR OUTDIR", NULL);
    g_states = fopen(path(argv[3], "states.bin"), "wb");
    FILE* tk = fopen(path(argv[3], "ticks.bin"), "wb");
    if (!g_states || !tk) die("cannot write into", argv[3]);
    double dist[MAXR], fit[MAXR];
    long n = run_bout(dir, &p, tk, dist, fit);
    fclose(g_states);
    fclose(tk);
    FILE* r = fopen(path(argv[3], "result.txt"), "w");
    for (FILE* f = stdout; f; f = (f == stdout ? r : NULL)) {
      fprintf(f, "steps %ld digest %016llx\n", n, (unsigned long long)g_fnv);
      for (int k = 0; k < p.nrobots; k++) fprintf(f, "robot %d distance %a fitness %a (%.6f) exploded %d\n", k, dist[k], fit[k], fit[k], p.r[k].exploded);
    }
    fclose(r);
    return 0;
  }
  if (!strcmp(cmd, "bench")) {
    int reps = argc > 3 ? atoi(argv[3]) : 5;
    double dist[MAXR], fit[MAXR];
    run_bout(dir, &p, NULL, dist, fit);  // warm up
    double t0 = now();
    long steps = 0;
    for (int i = 0; i < reps; i++) steps += run_bout(dir, &p, NULL, dist, fit);
    double el = now() - t0;
    printf("bench: %d bouts, %ld mj_steps, %.4f s per bout, %.3f us per mj_step (incl. compile, sensors, brains)\n", reps, steps, el / reps, 1e6 * el / steps);
    return 0;
  }
  die("unknown command", cmd);
  return 2;
}
