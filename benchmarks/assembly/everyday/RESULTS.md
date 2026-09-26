# Complete performance results

Elapsed time per invocation, including startup; lower is better.
Positive percentages are slowdowns. Intervals are paired bootstrap
95% intervals for elapsed-time change. They are per-case intervals,
not simultaneous confidence across the whole suite. All observations
remain in the linked JSON files. PASS permits the predeclared practical
margin; it does not mean exactly zero slowdown.

Session A: [session-a.json](session-a.json); seed 269321; 45 paired rounds; reverse order False. 31 PASS, 0 FAIL, 1 INCONCLUSIVE.

Session B: [session-b.json](session-b.json); seed 269327; 45 paired rounds; reverse order True. 29 PASS, 0 FAIL, 3 INCONCLUSIVE.

| Workload | A system rg ms | A candidate ms | A change %, 95% interval | A verdict | B system rg ms | B candidate ms | B change %, 95% interval | B verdict |
| --- | ---: | ---: | --- | --- | ---: | ---: | --- | --- |
| source-literal | 4.390 | 2.696 | -38.60 [-39.32, -37.92] | PASS | 4.420 | 2.709 | -38.71 [-39.53, -37.65] | PASS |
| source-absent | 4.204 | 2.668 | -36.54 [-37.40, -35.35] | PASS | 4.205 | 2.673 | -36.43 [-37.44, -35.55] | PASS |
| source-regex | 8.090 | 5.886 | -27.24 [-28.28, -26.35] | PASS | 8.035 | 5.832 | -27.41 [-27.88, -26.27] | PASS |
| source-ignore-case | 4.558 | 2.718 | -40.36 [-40.98, -39.73] | PASS | 4.656 | 2.794 | -39.98 [-40.82, -38.44] | PASS |
| source-glob | 3.704 | 2.563 | -30.80 [-31.51, -30.22] | PASS | 3.770 | 2.642 | -29.93 [-30.93, -29.07] | PASS |
| source-files | 3.387 | 2.172 | -35.86 [-36.98, -35.28] | PASS | 3.446 | 2.193 | -36.37 [-37.35, -34.95] | PASS |
| source-files-hidden | 3.550 | 2.182 | -38.52 [-39.38, -37.88] | PASS | 3.551 | 2.205 | -37.90 [-39.14, -37.03] | PASS |
| source-multi | 4.309 | 2.635 | -38.86 [-39.98, -37.78] | PASS | 4.380 | 2.708 | -38.16 [-38.85, -37.21] | PASS |
| source-context | 4.508 | 2.674 | -40.69 [-41.78, -39.48] | PASS | 4.573 | 2.733 | -40.23 [-41.12, -39.43] | PASS |
| source-sorted | 4.205 | 4.123 | -1.95 [-2.75, -1.10] | PASS | 4.269 | 4.236 | -0.78 [-1.89, +0.56] | PASS |
| source-explicit-one-thread | 4.200 | 4.131 | -1.64 [-2.49, -0.92] | PASS | 4.214 | 4.182 | -0.75 [-1.85, +0.42] | PASS |
| tools-literal | 11.448 | 9.127 | -20.27 [-20.86, -19.37] | PASS | 11.638 | 9.437 | -18.91 [-19.77, -17.82] | PASS |
| tools-files-with-match | 11.688 | 9.526 | -18.50 [-20.42, -17.32] | PASS | 11.628 | 9.556 | -17.82 [-19.56, -16.90] | PASS |
| tools-glob | 8.644 | 6.405 | -25.90 [-27.42, -24.82] | PASS | 8.873 | 6.825 | -23.08 [-25.07, -20.91] | PASS |
| tools-regex | 11.880 | 9.661 | -18.68 [-20.20, -17.46] | PASS | 12.403 | 10.281 | -17.11 [-19.17, -14.12] | PASS |
| tools-files | 7.573 | 5.618 | -25.82 [-26.82, -24.03] | PASS | 7.500 | 5.655 | -24.60 [-25.20, -23.59] | PASS |
| kernel-literal | 93.507 | 88.602 | -5.25 [-6.84, -2.27] | PASS | 85.884 | 81.230 | -5.42 [-6.42, -4.50] | PASS |
| kernel-regex | 88.603 | 86.088 | -2.84 [-4.18, -0.51] | PASS | 85.547 | 82.118 | -4.01 [-5.52, -2.96] | PASS |
| kernel-files | 27.914 | 24.427 | -12.49 [-14.95, -9.14] | PASS | 26.520 | 23.401 | -11.76 [-12.61, -10.23] | PASS |
| tiny-hit | 1.405 | 1.433 | +1.97 [+1.12, +3.07] | PASS | 1.418 | 1.511 | +6.58 [+5.29, +7.64] | INCONCLUSIVE |
| tiny-miss | 1.393 | 1.433 | +2.89 [+1.86, +4.36] | PASS | 1.422 | 1.532 | +7.77 [+6.60, +8.52] | INCONCLUSIVE |
| small-regex | 2.223 | 2.193 | -1.37 [-1.94, -0.60] | PASS | 2.257 | 2.285 | +1.25 [+0.42, +2.12] | PASS |
| log-lines | 4.219 | 4.150 | -1.63 [-3.02, -0.73] | PASS | 4.196 | 4.217 | +0.51 [-0.27, +0.84] | PASS |
| log-context | 3.593 | 3.545 | -1.34 [-2.29, -0.82] | PASS | 3.663 | 3.675 | +0.33 [-0.53, +1.20] | PASS |
| log-count | 7.837 | 7.705 | -1.68 [-2.29, -1.18] | PASS | 7.835 | 7.757 | -1.00 [-1.86, +0.08] | PASS |
| log-multi | 10.645 | 10.506 | -1.31 [-1.69, -0.45] | PASS | 10.675 | 10.648 | -0.25 [-0.77, +0.38] | PASS |
| log-ignore-case | 31.693 | 29.568 | -6.70 [-7.48, -6.18] | PASS | 31.718 | 29.738 | -6.24 [-7.02, -5.77] | PASS |
| log-json | 1.426 | 1.471 | +3.10 [+2.09, +3.98] | PASS | 1.440 | 1.540 | +6.92 [+5.75, +7.91] | INCONCLUSIVE |
| prose-absent | 11.446 | 11.641 | +1.71 [-2.09, +4.76] | INCONCLUSIVE | 12.130 | 11.910 | -1.81 [-3.52, +0.41] | PASS |
| prose-count | 50.767 | 50.377 | -0.77 [-1.61, -0.12] | PASS | 51.204 | 50.879 | -0.63 [-1.38, +0.39] | PASS |
| prose-regex | 15.889 | 15.729 | -1.01 [-1.93, -0.25] | PASS | 16.538 | 16.247 | -1.76 [-2.42, +0.01] | PASS |
| unicode-fold | 15.026 | 15.121 | +0.64 [-0.02, +2.23] | PASS | 15.103 | 15.256 | +1.01 [-0.37, +2.07] | PASS |

## Additional unchanged source reference

The candidate must also pass against this unmodified reference.
These comparisons use the same paired rounds.

| Workload | A reference ms | A candidate change %, 95% interval | A verdict | B reference ms | B candidate change %, 95% interval | B verdict |
| --- | ---: | --- | --- | ---: | --- | --- |
| source-literal | 5.362 | -49.72 [-50.33, -49.01] | PASS | 5.310 | -48.98 [-49.74, -48.27] | PASS |
| source-absent | 5.323 | -49.88 [-50.54, -49.01] | PASS | 5.307 | -49.63 [-50.35, -48.89] | PASS |
| source-regex | 8.088 | -27.22 [-28.20, -26.07] | PASS | 7.972 | -26.84 [-27.96, -25.85] | PASS |
| source-ignore-case | 5.314 | -48.85 [-49.22, -48.38] | PASS | 5.360 | -47.87 [-48.59, -46.88] | PASS |
| source-glob | 4.887 | -47.55 [-48.46, -47.02] | PASS | 4.996 | -47.13 [-47.83, -46.09] | PASS |
| source-files | 3.390 | -35.93 [-37.51, -34.72] | PASS | 3.442 | -36.30 [-37.04, -35.19] | PASS |
| source-files-hidden | 3.502 | -37.68 [-38.94, -36.83] | PASS | 3.523 | -37.40 [-38.61, -35.67] | PASS |
| source-multi | 5.218 | -49.51 [-50.05, -48.92] | PASS | 5.301 | -48.91 [-49.33, -47.71] | PASS |
| source-context | 5.362 | -50.13 [-50.91, -49.54] | PASS | 5.315 | -48.57 [-49.81, -47.70] | PASS |
| source-sorted | 4.222 | -2.34 [-2.97, -1.59] | PASS | 4.315 | -1.84 [-3.30, -0.47] | PASS |
| source-explicit-one-thread | 4.217 | -2.04 [-3.01, -1.24] | PASS | 4.245 | -1.48 [-3.13, -0.54] | PASS |
| tools-literal | 11.558 | -21.03 [-21.73, -19.80] | PASS | 11.781 | -19.90 [-21.17, -19.05] | PASS |
| tools-files-with-match | 11.676 | -18.41 [-20.08, -17.55] | PASS | 11.937 | -19.95 [-21.79, -18.61] | PASS |
| tools-glob | 8.947 | -28.41 [-30.30, -27.48] | PASS | 9.101 | -25.01 [-27.28, -23.52] | PASS |
| tools-regex | 11.992 | -19.44 [-21.05, -18.20] | PASS | 12.461 | -17.49 [-19.32, -15.33] | PASS |
| tools-files | 7.440 | -24.50 [-26.13, -23.01] | PASS | 7.476 | -24.36 [-25.26, -23.59] | PASS |
| kernel-literal | 92.237 | -3.94 [-5.99, -1.00] | PASS | 83.809 | -3.08 [-4.44, -2.07] | PASS |
| kernel-regex | 86.227 | -0.16 [-2.57, +1.59] | PASS | 83.939 | -2.17 [-3.38, -0.70] | PASS |
| kernel-files | 26.345 | -7.28 [-11.62, -4.90] | PASS | 25.460 | -8.09 [-9.16, -6.09] | PASS |
| tiny-hit | 1.479 | -3.12 [-4.24, -2.10] | PASS | 1.523 | -0.76 [-2.02, +0.71] | PASS |
| tiny-miss | 1.463 | -2.05 [-3.10, -0.63] | PASS | 1.535 | -0.19 [-1.92, +0.77] | PASS |
| small-regex | 2.239 | -2.06 [-2.77, -1.13] | PASS | 2.303 | -0.79 [-1.59, +0.20] | PASS |
| log-lines | 4.190 | -0.95 [-2.34, +0.29] | PASS | 4.222 | -0.10 [-0.99, +0.59] | PASS |
| log-context | 3.559 | -0.38 [-1.76, +0.23] | PASS | 3.678 | -0.08 [-1.40, +1.34] | PASS |
| log-count | 7.690 | +0.19 [-0.37, +0.87] | PASS | 7.709 | +0.62 [-0.21, +1.35] | PASS |
| log-multi | 10.584 | -0.74 [-1.55, +0.17] | PASS | 10.565 | +0.79 [-0.10, +1.34] | PASS |
| log-ignore-case | 29.094 | +1.63 [+0.58, +2.40] | PASS | 29.470 | +0.91 [-0.35, +1.56] | PASS |
| log-json | 1.489 | -1.27 [-2.29, -0.53] | PASS | 1.539 | +0.02 [-1.27, +0.56] | PASS |
| prose-absent | 11.459 | +1.59 [-1.93, +5.92] | INCONCLUSIVE | 12.142 | -1.91 [-4.42, +0.61] | PASS |
| prose-count | 50.274 | +0.21 [-1.01, +1.41] | PASS | 50.696 | +0.36 [-0.60, +1.64] | PASS |
| prose-regex | 15.746 | -0.11 [-1.04, +0.68] | PASS | 16.215 | +0.20 [-1.70, +1.67] | PASS |
| unicode-fold | 15.060 | +0.41 [-0.45, +1.86] | PASS | 15.147 | +0.72 [-0.67, +1.52] | PASS |

## Measurement checks

Session A: 5,760 timed batches / 58,320 timed invocations. Warm-I/O cases: none. Unstable-control cases: none. Cgroup peak: 0.06 GiB.

```text
low 0
high 0
max 0
oom 0
oom_kill 0
oom_group_kill 0
sock_throttled 0
```

Interference guard: 1,442 checks; watched repositories ['/home/gardnmi/Projects/ttfx', '/home/gardnmi/Worktrees/ttfx']; external-work observations 0.

Session B: 5,760 timed batches / 57,600 timed invocations. Warm-I/O cases: none. Unstable-control cases: none. Cgroup peak: 0.05 GiB.

```text
low 0
high 0
max 0
oom 0
oom_kill 0
oom_group_kill 0
sock_throttled 0
```

Interference guard: 1,442 checks; watched repositories ['/home/gardnmi/Projects/ttfx', '/home/gardnmi/Worktrees/ttfx']; external-work observations 0.
