// RBT-133 adversary: drive the harness's own sensors() and brain_step() (harness/rbt_wasm.c, included verbatim) on
// inputs chosen to reach the branches the two packed bouts never take, so that semcheck.py can compare them with
// rabbitstew's Python on the same inputs.
//
//   semcheck sensors MODEL.mjb SPEC.txt STATES.bin OUT.bin
//       SPEC.txt: "target x y z", "opp R", "n K", then K lines "kind axis body geom jid ball span freq phase";
//                 then "cases C" and C lines "pre post t" (row indices into STATES.bin and the clock).
//       For each case: load row `pre`, mj_forward, then overwrite qpos/qvel/act with row `post` (what mj_step leaves),
//       and write the K sensor values.
//   semcheck brain SPEC.txt OUT.bin
//       SPEC.txt: "n N", "W ..." (N*N), "bias ...", "func ...", "nsens K", "units ...", "steps T", then T*K sensor values.
//       Writes the activation vector after each step.
#define main harness_main
#include "../harness/rbt_wasm.c"
#undef main

static double rdd(FILE* f) { return rd(f); }

int main(int argc, char** argv) {
  if (argc < 2) return 2;
  if (!strcmp(argv[1], "sensors")) {
    mjModel* m = mj_loadModel(argv[2], NULL);
    mjData* d = mj_makeData(m);
    FILE* f = fopen(argv[3], "r");
    Pack p;
    memset(&p, 0, sizeof p);
    Robot* R = &p.r[0];
    expect(f, "target"); for (int i = 0; i < 3; i++) p.target[i] = rdd(f);
    expect(f, "opp"); R->opp_root_body = ri_(f);
    expect(f, "n"); R->nsens = ri_(f);
    R->sens = calloc(R->nsens, sizeof(Sensor));
    for (int k = 0; k < R->nsens; k++) {
      Sensor* s = &R->sens[k];
      s->kind = ri_(f); s->axis = ri_(f); s->body = ri_(f); s->geom = ri_(f); s->jid = ri_(f); s->ball = ri_(f);
      s->span = rdd(f); s->freq = rdd(f); s->phase = rdd(f);
    }
    expect(f, "cases"); int nc = ri_(f);
    size_t w = 1 + m->nq + 2 * m->nv + m->na;
    FILE* sf = fopen(argv[4], "rb");
    fseek(sf, 0, SEEK_END);
    long nrows = ftell(sf) / (long)(sizeof(double) * w);
    double* rows = malloc(sizeof(double) * w * nrows);
    fseek(sf, 0, SEEK_SET);
    if (fread(rows, sizeof(double) * w, nrows, sf) != (size_t)nrows) return 3;
    FILE* out = fopen(argv[5], "wb");
    double* sv = malloc(sizeof(double) * R->nsens);
    for (int c = 0; c < nc; c++) {
      int pre = ri_(f), post = ri_(f);
      double t = rdd(f);
      const double* a = rows + (size_t)pre * w;
      size_t o = 0;
      d->time = a[o++];
      memcpy(d->qpos, a + o, sizeof(double) * m->nq); o += m->nq;
      memcpy(d->qvel, a + o, sizeof(double) * m->nv); o += m->nv;
      memcpy(d->act, a + o, sizeof(double) * m->na); o += m->na;
      memcpy(d->qacc_warmstart, a + o, sizeof(double) * m->nv);
      mj_forward(m, d);
      const double* b = rows + (size_t)post * w;
      o = 1;
      memcpy(d->qpos, b + o, sizeof(double) * m->nq); o += m->nq;
      memcpy(d->qvel, b + o, sizeof(double) * m->nv); o += m->nv;
      memcpy(d->act, b + o, sizeof(double) * m->na);
      sensors(m, d, &p, R, t, sv);
      fwrite(sv, sizeof(double), R->nsens, out);
    }
    fclose(out);
    return 0;
  }
  if (!strcmp(argv[1], "brain")) {
    FILE* f = fopen(argv[2], "r");
    Robot R;
    memset(&R, 0, sizeof R);
    expect(f, "n"); int n = R.n = ri_(f);
    R.W = calloc(n * n, sizeof(double)); R.bias = calloc(n, sizeof(double)); R.a = calloc(n, sizeof(double));
    R.x = calloc(n, sizeof(double)); R.prev = calloc(n, sizeof(double)); R.nw = calloc(n, sizeof(double));
    R.func = calloc(n, sizeof(int));
    expect(f, "W"); for (int i = 0; i < n * n; i++) R.W[i] = rdd(f);
    expect(f, "bias"); for (int i = 0; i < n; i++) R.bias[i] = rdd(f);
    expect(f, "func"); for (int i = 0; i < n; i++) R.func[i] = ri_(f);
    expect(f, "nsens"); R.nsens = ri_(f);
    R.sens = calloc(R.nsens ? R.nsens : 1, sizeof(Sensor));
    expect(f, "units"); for (int k = 0; k < R.nsens; k++) R.sens[k].unit = ri_(f);
    expect(f, "steps"); int T = ri_(f);
    double* sv = malloc(sizeof(double) * (R.nsens ? R.nsens : 1));
    FILE* out = fopen(argv[3], "wb");
    for (int t = 0; t < T; t++) {
      for (int k = 0; k < R.nsens; k++) sv[k] = rdd(f);
      brain_step(&R, sv);
      fwrite(R.a, sizeof(double), n, out);
    }
    fclose(out);
    return 0;
  }
  return 2;
}
