# Complete performance results

Elapsed time per invocation, including startup; lower is better.
Positive percentages are slowdowns. Intervals are paired bootstrap
95% intervals for elapsed-time change. They are per-case intervals,
not simultaneous confidence across the whole suite. All observations
remain in the linked JSON files. PASS permits the predeclared practical
margin; it does not mean exactly zero slowdown.

Session A: [entry-quiet-session-a.json](entry-quiet-session-a.json); seed 942111; 15 paired rounds; reverse order False. 80 PASS, 0 FAIL, 1 INCONCLUSIVE.

Session B: [entry-quiet-session-b.json](entry-quiet-session-b.json); seed 942119; 15 paired rounds; reverse order True. 81 PASS, 0 FAIL, 0 INCONCLUSIVE.

| Workload | A upstream ms | A candidate ms | A change %, 95% interval | A verdict | B upstream ms | B candidate ms | B change %, 95% interval | B verdict |
| --- | ---: | ---: | --- | --- | ---: | ---: | --- | --- |
| empty | 2.334 | 2.225 | -4.66 [-5.03, -4.43] | PASS | 2.338 | 2.224 | -4.90 [-5.29, -4.24] | PASS |
| tiny-hit | 2.338 | 2.230 | -4.65 [-5.02, -4.21] | PASS | 2.347 | 2.232 | -4.92 [-5.23, -4.46] | PASS |
| tiny-miss | 2.333 | 2.226 | -4.59 [-4.93, -4.22] | PASS | 2.334 | 2.227 | -4.60 [-5.28, -4.29] | PASS |
| tiny-class30 | 2.404 | 2.301 | -4.29 [-4.69, -3.97] | PASS | 2.400 | 2.289 | -4.64 [-5.13, -4.33] | PASS |
| small-literal | 2.343 | 2.230 | -4.80 [-5.02, -4.46] | PASS | 2.347 | 2.234 | -4.84 [-5.12, -4.50] | PASS |
| small-regex | 2.973 | 2.869 | -3.48 [-3.94, -3.27] | PASS | 2.978 | 2.862 | -3.89 [-4.36, -3.45] | PASS |
| literal-dense | 22.774 | 22.431 | -1.51 [-1.97, -1.11] | PASS | 22.584 | 22.361 | -0.99 [-1.29, -0.44] | PASS |
| literal-sparse-lines | 5.341 | 5.216 | -2.35 [-3.24, -0.92] | PASS | 5.326 | 5.159 | -3.13 [-3.77, -2.23] | PASS |
| literal-absent | 4.799 | 4.692 | -2.22 [-3.36, -1.07] | PASS | 4.815 | 4.691 | -2.59 [-4.17, -1.33] | PASS |
| literal-fixed | 12.217 | 12.023 | -1.59 [-2.12, -1.24] | PASS | 12.190 | 12.055 | -1.11 [-1.78, -0.55] | PASS |
| literal-insensitive | 39.032 | 38.742 | -0.74 [-1.35, +0.75] | PASS | 38.798 | 38.516 | -0.73 [-1.18, -0.09] | PASS |
| literal-word | 36.540 | 36.366 | -0.48 [-1.23, +0.13] | PASS | 36.344 | 36.386 | +0.12 [-1.28, +1.03] | PASS |
| literal-count | 14.169 | 13.932 | -1.67 [-5.41, -1.15] | PASS | 14.053 | 13.886 | -1.18 [-1.94, -0.69] | PASS |
| literal-count-matches | 49.314 | 48.791 | -1.06 [-1.28, -0.48] | PASS | 48.893 | 48.727 | -0.34 [-0.82, -0.01] | PASS |
| literal-only-offset | 40.029 | 40.309 | +0.70 [+0.18, +1.60] | PASS | 39.913 | 39.975 | +0.16 [-0.72, +1.18] | PASS |
| literal-context | 5.043 | 4.942 | -2.01 [-3.73, -1.00] | PASS | 5.098 | 4.883 | -4.23 [-4.98, -3.00] | PASS |
| literal-invert | 10.649 | 10.430 | -2.06 [-2.42, +0.54] | PASS | 10.580 | 10.483 | -0.92 [-2.53, -0.03] | PASS |
| literal-limit | 2.362 | 2.251 | -4.70 [-5.36, -4.22] | PASS | 2.358 | 2.255 | -4.39 [-5.17, -3.93] | PASS |
| literal-quiet | 2.364 | 2.259 | -4.46 [-5.32, -4.00] | PASS | 2.358 | 2.243 | -4.89 [-5.27, -4.27] | PASS |
| literal-multi-pattern | 13.647 | 13.512 | -0.99 [-1.65, -0.28] | PASS | 13.569 | 13.438 | -0.97 [-1.50, -0.32] | PASS |
| regex-general | 18.795 | 18.656 | -0.74 [-1.43, -0.02] | PASS | 18.758 | 18.570 | -1.00 [-1.40, -0.35] | PASS |
| regex-captures | 68.317 | 68.089 | -0.33 [-0.77, +0.14] | PASS | 68.554 | 68.008 | -0.80 [-1.70, -0.08] | PASS |
| regex-replace | 133.554 | 134.353 | +0.60 [+0.22, +1.11] | PASS | 133.403 | 134.012 | +0.46 [+0.02, +0.85] | PASS |
| regex-anchored | 26.361 | 26.186 | -0.66 [-1.30, +0.21] | PASS | 26.228 | 26.094 | -0.51 [-1.19, -0.19] | PASS |
| regex-zero-length | 14.858 | 14.667 | -1.28 [-2.00, -0.93] | PASS | 14.841 | 14.609 | -1.56 [-2.03, -0.38] | PASS |
| regex-word-class | 42.574 | 42.358 | -0.51 [-0.87, +0.01] | PASS | 42.519 | 42.385 | -0.32 [-0.60, -0.19] | PASS |
| regex-lazy-class | 13.598 | 9.970 | -26.68 [-26.97, -26.28] | PASS | 13.565 | 9.925 | -26.84 [-27.32, -26.41] | PASS |
| regex-whole-class | 15.188 | 15.050 | -0.90 [-1.54, -0.63] | PASS | 15.193 | 14.968 | -1.48 [-1.78, -0.99] | PASS |
| unicode-literal | 8.629 | 8.541 | -1.02 [-1.45, -0.30] | PASS | 8.619 | 8.456 | -1.89 [-2.59, -0.64] | PASS |
| unicode-fold | 15.018 | 14.782 | -1.57 [-2.12, -1.01] | PASS | 14.895 | 14.768 | -0.85 [-1.92, -0.34] | PASS |
| unicode-word | 12.690 | 12.530 | -1.25 [-1.65, -0.45] | PASS | 12.750 | 12.572 | -1.40 [-1.80, -0.68] | PASS |
| unicode-property | 11.442 | 11.277 | -1.44 [-2.36, -0.98] | PASS | 11.427 | 11.229 | -1.73 [-2.15, -0.86] | PASS |
| unicode-class-fallback | 9.420 | 9.293 | -1.35 [-2.01, +0.34] | PASS | 9.453 | 9.252 | -2.12 [-2.84, -1.24] | PASS |
| crlf | 22.499 | 22.256 | -1.08 [-1.62, -0.68] | PASS | 22.503 | 22.356 | -0.65 [-1.44, -0.05] | PASS |
| multiline | 30.380 | 30.115 | -0.87 [-2.67, -0.16] | PASS | 30.281 | 30.113 | -0.55 [-1.03, -0.09] | PASS |
| binary-default | 2.358 | 2.245 | -4.81 [-5.13, -4.56] | PASS | 2.346 | 2.245 | -4.30 [-4.75, -3.93] | PASS |
| binary-text | 9.661 | 9.537 | -1.28 [-1.75, -1.00] | PASS | 9.689 | 9.570 | -1.22 [-1.68, -0.52] | PASS |
| null-lines | 9.842 | 9.779 | -0.64 [-1.80, -0.01] | PASS | 9.845 | 9.729 | -1.18 [-1.64, -0.83] | PASS |
| long-line-literal | 4.041 | 3.881 | -3.96 [-5.23, -2.79] | INCONCLUSIVE | 4.031 | 3.990 | -1.03 [-2.91, +0.27] | PASS |
| long-line-class | 3.669 | 3.547 | -3.32 [-4.59, -2.04] | PASS | 3.636 | 3.563 | -2.01 [-4.23, -0.89] | PASS |
| subtitles-sherlock | 12.900 | 12.814 | -0.66 [-3.67, +1.19] | PASS | 13.105 | 12.743 | -2.76 [-4.00, -0.59] | PASS |
| subtitles-sherlock-lines | 15.884 | 15.751 | -0.83 [-1.89, -0.08] | PASS | 15.941 | 15.504 | -2.75 [-3.82, -0.36] | PASS |
| subtitles-frequent | 63.705 | 63.803 | +0.15 [-0.36, +0.46] | PASS | 64.098 | 63.810 | -0.45 [-1.05, -0.12] | PASS |
| subtitles-alpha30 | 162.030 | 13.794 | -91.49 [-91.75, -91.25] | PASS | 162.029 | 14.100 | -91.30 [-91.74, -90.91] | PASS |
| subtitles-hex17 | 162.177 | 13.887 | -91.44 [-92.08, -91.23] | PASS | 161.910 | 13.954 | -91.38 [-91.71, -91.28] | PASS |
| subtitles-digits8 | 15.022 | 12.507 | -16.74 [-17.70, -15.85] | PASS | 15.174 | 12.435 | -18.05 [-18.83, -16.74] | PASS |
| json | 2.370 | 2.257 | -4.78 [-5.18, -4.14] | PASS | 2.352 | 2.235 | -4.96 [-5.41, -4.62] | PASS |
| color | 2.526 | 2.420 | -4.17 [-4.66, -3.88] | PASS | 2.523 | 2.408 | -4.55 [-4.83, -4.15] | PASS |
| class-dense-1 | 21.642 | 21.452 | -0.88 [-1.33, -0.53] | PASS | 21.632 | 21.448 | -0.85 [-1.11, -0.64] | PASS |
| class-dense-2 | 21.742 | 7.916 | -63.59 [-64.13, -63.33] | PASS | 21.795 | 7.861 | -63.93 [-64.39, -63.72] | PASS |
| class-dense-3 | 21.939 | 7.914 | -63.93 [-64.20, -63.82] | PASS | 21.973 | 7.872 | -64.17 [-64.33, -63.87] | PASS |
| class-dense-7 | 32.565 | 6.795 | -79.13 [-79.37, -78.68] | PASS | 32.470 | 6.741 | -79.24 [-79.47, -78.83] | PASS |
| class-dense-8 | 32.664 | 6.880 | -78.94 [-79.16, -78.60] | PASS | 32.604 | 6.911 | -78.80 [-78.87, -78.68] | PASS |
| class-dense-15 | 33.433 | 6.964 | -79.17 [-79.36, -79.01] | PASS | 33.276 | 6.884 | -79.31 [-79.45, -79.20] | PASS |
| class-dense-16 | 33.442 | 6.944 | -79.24 [-79.40, -78.90] | PASS | 33.347 | 6.904 | -79.30 [-79.44, -79.09] | PASS |
| class-dense-30 | 34.843 | 7.020 | -79.85 [-80.14, -79.46] | PASS | 34.833 | 6.913 | -80.15 [-80.25, -80.02] | PASS |
| class-dense-64 | 38.276 | 6.954 | -81.83 [-82.31, -81.64] | PASS | 38.088 | 6.968 | -81.71 [-81.92, -81.58] | PASS |
| class-dense-65 | 38.292 | 6.994 | -81.74 [-81.94, -81.43] | PASS | 38.197 | 6.950 | -81.81 [-81.98, -81.58] | PASS |
| class-dense-129 | 42.664 | 5.778 | -86.46 [-86.71, -86.14] | PASS | 42.602 | 5.855 | -86.26 [-86.72, -86.10] | PASS |
| class-absent-1 | 42.429 | 42.245 | -0.43 [-0.67, -0.13] | PASS | 42.338 | 42.171 | -0.39 [-0.58, -0.20] | PASS |
| class-absent-2 | 42.426 | 5.553 | -86.91 [-87.30, -86.68] | PASS | 42.340 | 5.432 | -87.17 [-87.43, -87.06] | PASS |
| class-absent-8 | 42.472 | 5.650 | -86.70 [-87.24, -86.53] | PASS | 42.369 | 5.584 | -86.82 [-87.12, -86.67] | PASS |
| class-absent-16 | 43.410 | 6.240 | -85.63 [-86.68, -84.99] | PASS | 42.308 | 5.549 | -86.88 [-87.27, -86.58] | PASS |
| class-absent-30 | 43.499 | 5.808 | -86.65 [-86.87, -85.54] | PASS | 42.350 | 5.574 | -86.84 [-86.94, -86.78] | PASS |
| class-absent-65 | 42.644 | 5.531 | -87.03 [-87.35, -86.79] | PASS | 42.437 | 5.458 | -87.14 [-87.37, -86.80] | PASS |
| class-varied-2 | 29.966 | 26.124 | -12.82 [-13.15, -12.37] | PASS | 29.991 | 26.139 | -12.84 [-13.23, -12.50] | PASS |
| class-varied-8 | 31.340 | 25.008 | -20.20 [-20.44, -19.59] | PASS | 31.339 | 25.033 | -20.12 [-20.39, -19.75] | PASS |
| class-varied-16 | 34.335 | 24.016 | -30.06 [-30.32, -29.71] | PASS | 34.204 | 23.915 | -30.08 [-30.77, -29.84] | PASS |
| class-varied-30 | 37.439 | 21.365 | -42.93 [-43.07, -42.66] | PASS | 37.368 | 21.301 | -43.00 [-43.10, -42.76] | PASS |
| class-varied-65 | 44.553 | 15.445 | -65.33 [-65.62, -65.22] | PASS | 44.620 | 15.484 | -65.30 [-65.43, -65.09] | PASS |
| wide-ascii | 22.939 | 22.697 | -1.06 [-1.32, -0.39] | PASS | 23.009 | 22.753 | -1.11 [-1.24, -0.64] | PASS |
| optional-class | 23.508 | 23.333 | -0.74 [-1.18, -0.41] | PASS | 23.512 | 23.312 | -0.85 [-1.08, -0.54] | PASS |
| captured-class | 29.280 | 29.134 | -0.50 [-1.11, -0.15] | PASS | 29.296 | 29.078 | -0.74 [-1.19, +0.24] | PASS |
| tree-literal | 3.973 | 3.962 | -0.29 [-2.46, +0.43] | PASS | 3.984 | 3.950 | -0.85 [-1.66, +0.18] | PASS |
| tree-regex | 7.039 | 7.080 | +0.58 [-1.61, +2.07] | PASS | 7.030 | 6.987 | -0.61 [-1.46, +0.66] | PASS |
| tree-files | 3.966 | 3.944 | -0.54 [-1.25, +2.21] | PASS | 3.942 | 3.868 | -1.87 [-3.41, -0.37] | PASS |
| tree-sorted | 3.748 | 3.630 | -3.15 [-3.44, -2.27] | PASS | 3.755 | 3.623 | -3.52 [-3.97, -3.09] | PASS |
| kernel-default | 116.370 | 116.372 | +0.00 [-0.97, +0.79] | PASS | 117.709 | 115.788 | -1.63 [-3.54, -0.86] | PASS |
| kernel-c | 87.231 | 85.936 | -1.48 [-2.99, -0.65] | PASS | 86.948 | 85.510 | -1.65 [-2.32, +0.35] | PASS |
| cold-literal | 15.894 | 15.762 | -0.83 [-2.26, +0.29] | PASS | 15.926 | 15.819 | -0.68 [-2.64, -0.02] | PASS |
| cold-regex | 25.112 | 24.554 | -2.22 [-5.18, +1.27] | PASS | 24.844 | 24.914 | +0.28 [-2.98, +2.94] | PASS |

## Measurement checks

Session A: 3,645 timed batches / 22,545 timed invocations. Warm-I/O cases: ['long-line-literal']. Unstable-control cases: none. Cgroup peak: 0.05 GiB.

```text
low 0
high 0
max 0
oom 0
oom_kill 0
oom_group_kill 0
sock_throttled 0
```

Interference guard: 1,217 checks; watched repositories ['/home/gardnmi/Projects/ttfx', '/home/gardnmi/Worktrees/ttfx']; external-work observations 0.

Session B: 3,645 timed batches / 22,635 timed invocations. Warm-I/O cases: none. Unstable-control cases: none. Cgroup peak: 0.06 GiB.

```text
low 0
high 0
max 0
oom 0
oom_kill 0
oom_group_kill 0
sock_throttled 0
```

Interference guard: 1,217 checks; watched repositories ['/home/gardnmi/Projects/ttfx', '/home/gardnmi/Worktrees/ttfx']; external-work observations 0.
