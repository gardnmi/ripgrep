# Complete performance results

Elapsed time per invocation, including startup; lower is better.
Positive percentages are slowdowns. Intervals are paired bootstrap
95% intervals for elapsed-time change. They are per-case intervals,
not simultaneous confidence across the whole suite. All observations
remain in the linked JSON files. PASS permits the predeclared practical
margin; it does not mean exactly zero slowdown.

Session A: [bundle-v2-session-a.json](bundle-v2-session-a.json); seed 929711; 45 paired rounds; reverse order False. 64 PASS, 1 FAIL, 16 INCONCLUSIVE.

Session B: [bundle-v2-session-b.json](bundle-v2-session-b.json); seed 929719; 45 paired rounds; reverse order True. 61 PASS, 0 FAIL, 20 INCONCLUSIVE.

| Workload | A upstream ms | A candidate ms | A change %, 95% interval | A verdict | B upstream ms | B candidate ms | B change %, 95% interval | B verdict |
| --- | ---: | ---: | --- | --- | ---: | ---: | --- | --- |
| empty | 2.347 | 2.289 | -2.47 [-2.68, -1.94] | PASS | 2.825 | 2.752 | -2.57 [-4.47, -0.09] | PASS |
| tiny-hit | 2.358 | 2.306 | -2.21 [-2.38, -1.66] | PASS | 2.768 | 2.754 | -0.53 [-2.69, +0.47] | INCONCLUSIVE |
| tiny-miss | 2.370 | 2.313 | -2.42 [-2.75, -2.08] | PASS | 2.773 | 2.678 | -3.44 [-4.30, -1.71] | PASS |
| tiny-class30 | 2.437 | 2.376 | -2.51 [-2.72, -2.11] | PASS | 2.944 | 2.856 | -2.97 [-3.66, -1.83] | INCONCLUSIVE |
| small-literal | 2.373 | 2.315 | -2.43 [-2.85, -2.08] | PASS | 2.852 | 2.738 | -3.98 [-5.50, -2.25] | PASS |
| small-regex | 2.990 | 2.931 | -1.97 [-2.31, -1.67] | PASS | 3.898 | 3.763 | -3.45 [-5.30, -2.77] | PASS |
| literal-dense | 22.749 | 22.552 | -0.87 [-1.23, -0.52] | PASS | 28.068 | 27.151 | -3.27 [-5.41, +1.38] | PASS |
| literal-sparse-lines | 5.299 | 5.213 | -1.61 [-1.88, -1.14] | PASS | 8.766 | 8.705 | -0.70 [-2.04, +0.79] | INCONCLUSIVE |
| literal-absent | 4.809 | 4.749 | -1.24 [-1.71, -0.89] | PASS | 8.100 | 7.832 | -3.31 [-5.53, -1.11] | PASS |
| literal-fixed | 12.264 | 12.102 | -1.32 [-1.45, -1.05] | PASS | 17.254 | 16.780 | -2.74 [-4.87, +2.68] | PASS |
| literal-insensitive | 39.772 | 39.407 | -0.92 [-1.34, -0.12] | PASS | 51.070 | 51.423 | +0.69 [-2.37, +3.83] | INCONCLUSIVE |
| literal-word | 37.705 | 37.700 | -0.01 [-0.58, +0.59] | PASS | 44.392 | 44.379 | -0.03 [-4.92, +3.79] | INCONCLUSIVE |
| literal-count | 14.604 | 14.572 | -0.22 [-1.91, +0.88] | PASS | 18.643 | 18.540 | -0.55 [-4.16, +3.28] | INCONCLUSIVE |
| literal-count-matches | 50.609 | 50.206 | -0.80 [-1.24, -0.10] | PASS | 64.848 | 64.844 | -0.01 [-4.42, +2.82] | PASS |
| literal-only-offset | 40.959 | 43.948 | +7.30 [+6.66, +7.93] | INCONCLUSIVE | 56.203 | 57.474 | +2.26 [-2.82, +6.45] | INCONCLUSIVE |
| literal-context | 5.481 | 5.379 | -1.85 [-3.75, +0.27] | PASS | 8.448 | 8.283 | -1.96 [-3.90, +0.44] | PASS |
| literal-invert | 11.248 | 11.098 | -1.33 [-2.61, -0.21] | INCONCLUSIVE | 14.346 | 13.904 | -3.08 [-7.08, +2.92] | INCONCLUSIVE |
| literal-limit | 2.448 | 2.385 | -2.58 [-2.92, -2.16] | PASS | 3.269 | 3.287 | +0.55 [-6.71, +2.85] | INCONCLUSIVE |
| literal-quiet | 2.441 | 2.381 | -2.45 [-2.92, -2.06] | PASS | 3.563 | 3.434 | -3.61 [-6.39, -0.98] | INCONCLUSIVE |
| literal-multi-pattern | 13.985 | 13.798 | -1.34 [-1.88, -0.41] | INCONCLUSIVE | 18.803 | 18.210 | -3.15 [-5.54, +0.13] | PASS |
| regex-general | 19.921 | 19.689 | -1.16 [-2.11, -0.15] | PASS | 21.325 | 21.237 | -0.41 [-1.99, +1.29] | PASS |
| regex-captures | 68.567 | 71.892 | +4.85 [+4.39, +5.27] | FAIL | 75.018 | 77.892 | +3.83 [+0.87, +6.29] | INCONCLUSIVE |
| regex-replace | 135.206 | 139.498 | +3.17 [+2.80, +3.75] | INCONCLUSIVE | 152.822 | 157.156 | +2.84 [-0.36, +5.16] | INCONCLUSIVE |
| regex-anchored | 26.434 | 26.270 | -0.62 [-1.64, -0.08] | PASS | 31.015 | 30.266 | -2.42 [-4.15, +0.08] | PASS |
| regex-zero-length | 15.143 | 14.996 | -0.97 [-2.41, -0.15] | PASS | 18.157 | 18.129 | -0.16 [-3.91, +4.38] | INCONCLUSIVE |
| regex-word-class | 44.247 | 44.254 | +0.02 [-0.31, +0.31] | PASS | 47.420 | 47.093 | -0.69 [-1.25, -0.41] | PASS |
| regex-lazy-class | 13.597 | 9.954 | -26.79 [-27.69, -26.41] | PASS | 15.750 | 11.884 | -24.55 [-25.72, -22.41] | PASS |
| regex-whole-class | 15.556 | 15.456 | -0.65 [-1.05, -0.24] | PASS | 17.230 | 17.076 | -0.90 [-1.59, -0.39] | PASS |
| unicode-literal | 10.290 | 10.041 | -2.41 [-3.46, -0.77] | INCONCLUSIVE | 10.327 | 10.137 | -1.85 [-2.47, -1.06] | PASS |
| unicode-fold | 16.754 | 16.648 | -0.63 [-1.46, +0.04] | INCONCLUSIVE | 16.983 | 16.855 | -0.75 [-1.53, +0.82] | PASS |
| unicode-word | 14.449 | 14.248 | -1.39 [-3.80, +0.02] | PASS | 15.078 | 14.778 | -1.99 [-3.27, -0.51] | PASS |
| unicode-property | 13.356 | 13.192 | -1.23 [-2.44, +0.41] | PASS | 14.145 | 13.752 | -2.78 [-4.44, -0.62] | PASS |
| unicode-class-fallback | 10.900 | 10.791 | -1.00 [-2.03, -0.38] | INCONCLUSIVE | 11.685 | 11.526 | -1.37 [-4.70, +1.07] | PASS |
| crlf | 24.132 | 24.055 | -0.32 [-2.95, +0.92] | PASS | 26.319 | 27.142 | +3.13 [-2.42, +8.41] | INCONCLUSIVE |
| multiline | 32.422 | 32.036 | -1.19 [-7.34, +0.39] | PASS | 34.017 | 34.376 | +1.05 [-6.31, +4.63] | INCONCLUSIVE |
| binary-default | 3.316 | 3.143 | -5.23 [-8.00, -2.30] | PASS | 3.225 | 3.052 | -5.38 [-10.46, -3.05] | PASS |
| binary-text | 11.649 | 11.213 | -3.74 [-6.81, +1.57] | PASS | 11.006 | 10.707 | -2.72 [-4.71, -1.84] | INCONCLUSIVE |
| null-lines | 11.452 | 11.355 | -0.85 [-5.87, +4.58] | INCONCLUSIVE | 11.147 | 10.981 | -1.49 [-2.41, -0.20] | PASS |
| long-line-literal | 12.329 | 11.719 | -4.95 [-11.13, +1.61] | PASS | 6.408 | 6.293 | -1.80 [-3.56, +0.67] | PASS |
| long-line-class | 7.039 | 6.828 | -3.00 [-27.83, +3.35] | INCONCLUSIVE | 5.718 | 5.524 | -3.38 [-4.83, -1.35] | PASS |
| subtitles-sherlock | 15.561 | 15.355 | -1.32 [-4.16, +1.33] | INCONCLUSIVE | 16.973 | 16.640 | -1.96 [-3.40, -1.01] | INCONCLUSIVE |
| subtitles-sherlock-lines | 19.158 | 18.695 | -2.42 [-4.88, +1.28] | PASS | 20.058 | 19.493 | -2.82 [-5.22, +0.36] | PASS |
| subtitles-frequent | 69.327 | 67.306 | -2.91 [-4.79, +0.20] | PASS | 69.007 | 68.483 | -0.76 [-2.38, +1.91] | PASS |
| subtitles-alpha30 | 173.026 | 16.180 | -90.65 [-90.86, -90.49] | PASS | 170.909 | 15.677 | -90.83 [-91.04, -90.44] | PASS |
| subtitles-hex17 | 173.109 | 16.680 | -90.36 [-90.52, -90.22] | PASS | 170.411 | 15.932 | -90.65 [-90.77, -90.52] | PASS |
| subtitles-digits8 | 17.390 | 15.765 | -9.34 [-10.57, -8.53] | PASS | 17.385 | 15.546 | -10.58 [-11.77, -9.34] | PASS |
| json | 2.863 | 2.748 | -4.03 [-6.31, -2.42] | PASS | 2.983 | 2.803 | -6.01 [-7.96, -2.81] | PASS |
| color | 3.086 | 3.078 | -0.26 [-3.32, +1.99] | INCONCLUSIVE | 3.053 | 2.985 | -2.22 [-4.80, -0.77] | PASS |
| class-dense-1 | 25.012 | 24.715 | -1.19 [-3.07, +0.54] | INCONCLUSIVE | 24.773 | 24.385 | -1.56 [-2.77, -0.05] | PASS |
| class-dense-2 | 24.610 | 9.791 | -60.22 [-60.63, -59.55] | PASS | 24.783 | 9.936 | -59.91 [-60.32, -59.60] | PASS |
| class-dense-3 | 24.980 | 9.918 | -60.30 [-60.89, -59.86] | PASS | 25.263 | 9.930 | -60.69 [-61.28, -60.10] | PASS |
| class-dense-7 | 36.812 | 9.018 | -75.50 [-75.94, -74.88] | PASS | 36.100 | 8.744 | -75.78 [-76.01, -75.56] | PASS |
| class-dense-8 | 36.388 | 8.845 | -75.69 [-76.12, -75.22] | PASS | 36.121 | 8.695 | -75.93 [-76.28, -75.70] | PASS |
| class-dense-15 | 37.219 | 8.660 | -76.73 [-76.92, -76.31] | PASS | 37.154 | 8.917 | -76.00 [-76.55, -75.49] | PASS |
| class-dense-16 | 37.350 | 9.039 | -75.80 [-76.12, -75.30] | PASS | 37.558 | 9.004 | -76.03 [-76.35, -75.42] | PASS |
| class-dense-30 | 38.814 | 8.872 | -77.14 [-77.35, -76.57] | PASS | 38.804 | 8.902 | -77.06 [-77.46, -76.79] | PASS |
| class-dense-64 | 42.453 | 8.927 | -78.97 [-79.33, -78.66] | PASS | 42.649 | 9.124 | -78.61 [-79.18, -78.24] | PASS |
| class-dense-65 | 42.280 | 8.832 | -79.11 [-79.52, -78.82] | PASS | 42.461 | 8.855 | -79.15 [-79.39, -78.92] | PASS |
| class-dense-129 | 46.683 | 7.649 | -83.61 [-83.95, -83.15] | PASS | 46.812 | 7.939 | -83.04 [-83.22, -82.88] | PASS |
| class-absent-1 | 46.238 | 46.034 | -0.44 [-0.74, -0.01] | INCONCLUSIVE | 46.248 | 45.949 | -0.65 [-1.01, +0.12] | PASS |
| class-absent-2 | 46.138 | 7.264 | -84.26 [-84.53, -84.12] | PASS | 45.839 | 7.114 | -84.48 [-84.75, -84.21] | INCONCLUSIVE |
| class-absent-8 | 46.043 | 7.284 | -84.18 [-84.32, -84.08] | PASS | 46.065 | 7.154 | -84.47 [-84.66, -84.34] | PASS |
| class-absent-16 | 46.049 | 7.386 | -83.96 [-84.30, -83.78] | PASS | 46.159 | 7.230 | -84.34 [-84.56, -84.20] | PASS |
| class-absent-30 | 46.154 | 7.428 | -83.91 [-84.11, -83.68] | PASS | 45.996 | 7.295 | -84.14 [-84.41, -83.82] | PASS |
| class-absent-65 | 46.062 | 7.213 | -84.34 [-84.58, -84.15] | PASS | 46.133 | 7.242 | -84.30 [-84.62, -84.16] | INCONCLUSIVE |
| class-varied-2 | 32.265 | 28.433 | -11.88 [-13.71, -11.01] | PASS | 33.353 | 28.399 | -14.85 [-17.75, -11.72] | PASS |
| class-varied-8 | 34.193 | 27.790 | -18.73 [-21.97, -17.00] | PASS | 34.172 | 28.269 | -17.28 [-18.71, -14.04] | PASS |
| class-varied-16 | 36.523 | 25.801 | -29.36 [-29.73, -28.94] | PASS | 37.240 | 26.171 | -29.72 [-31.66, -28.44] | PASS |
| class-varied-30 | 40.775 | 23.383 | -42.65 [-43.71, -40.26] | PASS | 41.423 | 23.778 | -42.60 [-44.59, -39.29] | PASS |
| class-varied-65 | 48.447 | 17.261 | -64.37 [-64.72, -64.05] | PASS | 49.361 | 17.339 | -64.87 [-65.22, -64.20] | PASS |
| wide-ascii | 25.421 | 25.119 | -1.19 [-4.77, +0.47] | PASS | 25.575 | 25.292 | -1.10 [-2.20, +0.19] | PASS |
| optional-class | 25.609 | 25.147 | -1.81 [-6.21, -0.65] | INCONCLUSIVE | 26.138 | 25.598 | -2.07 [-3.45, +0.18] | PASS |
| captured-class | 32.076 | 31.837 | -0.75 [-1.55, -0.28] | PASS | 32.575 | 31.940 | -1.95 [-2.66, -0.57] | PASS |
| tree-literal | 5.114 | 5.037 | -1.50 [-3.47, +0.91] | INCONCLUSIVE | 4.948 | 4.961 | +0.26 [-2.04, +1.70] | PASS |
| tree-regex | 9.021 | 8.945 | -0.85 [-3.05, +0.57] | PASS | 8.933 | 8.912 | -0.24 [-2.90, +1.54] | PASS |
| tree-files | 5.034 | 4.980 | -1.07 [-2.91, +0.44] | INCONCLUSIVE | 4.905 | 4.916 | +0.21 [-1.41, +1.74] | INCONCLUSIVE |
| tree-sorted | 5.113 | 4.998 | -2.25 [-3.45, -0.93] | PASS | 5.163 | 4.979 | -3.57 [-5.30, -1.63] | PASS |
| kernel-default | 148.386 | 149.295 | +0.61 [-0.56, +1.73] | PASS | 149.617 | 148.070 | -1.03 [-2.31, +0.63] | PASS |
| kernel-c | 109.361 | 108.440 | -0.84 [-2.11, +0.02] | PASS | 107.817 | 107.892 | +0.07 [-0.48, +0.89] | PASS |
| cold-literal | 16.277 | 16.075 | -1.24 [-1.81, -0.33] | PASS | 16.439 | 16.212 | -1.38 [-2.35, -0.19] | PASS |
| cold-regex | 28.273 | 27.806 | -1.65 [-3.23, +0.26] | PASS | 28.472 | 28.436 | -0.12 [-2.31, +2.42] | PASS |

## Measurement checks

Session A: 10,935 timed batches / 60,210 timed invocations. Warm-I/O cases: ['literal-only-offset', 'literal-invert', 'literal-multi-pattern', 'unicode-literal', 'unicode-fold', 'unicode-class-fallback', 'subtitles-sherlock', 'color', 'class-dense-1', 'class-absent-1', 'optional-class', 'tree-literal', 'tree-files']. Unstable-control cases: none. Cgroup peak: 0.38 GiB.

```text
low 0
high 0
max 0
oom 0
oom_kill 0
oom_group_kill 0
sock_throttled 0
```

Session B: 10,935 timed batches / 54,675 timed invocations. Warm-I/O cases: ['tree-files', 'class-absent-65', 'class-absent-2', 'subtitles-sherlock', 'binary-text', 'regex-zero-length', 'literal-quiet', 'literal-limit', 'literal-invert', 'literal-only-offset', 'literal-count', 'literal-sparse-lines', 'tiny-class30', 'tiny-hit']. Unstable-control cases: none. Cgroup peak: 0.06 GiB.

```text
low 0
high 0
max 0
oom 0
oom_kill 0
oom_group_kill 0
sock_throttled 0
```
