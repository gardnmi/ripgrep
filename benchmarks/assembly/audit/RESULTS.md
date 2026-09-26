# Complete performance results

Elapsed time per invocation, including startup; lower is better.
Positive percentages are slowdowns. Intervals are paired bootstrap
95% intervals for elapsed-time change. They are per-case intervals,
not simultaneous confidence across the whole suite. All observations
remain in the linked JSON files. PASS permits the predeclared practical
margin; it does not mean exactly zero slowdown.

Session A: [session-a.json](session-a.json); seed 417225; 15 paired rounds; reverse order False. 57 PASS, 2 FAIL, 22 INCONCLUSIVE.

Session B: [session-b.json](session-b.json); seed 931607; 15 paired rounds; reverse order True. 53 PASS, 5 FAIL, 23 INCONCLUSIVE.

| Workload | A upstream ms | A candidate ms | A change %, 95% interval | A verdict | B upstream ms | B candidate ms | B change %, 95% interval | B verdict |
| --- | ---: | ---: | --- | --- | ---: | ---: | --- | --- |
| empty | 2.311 | 2.332 | +0.88 [+0.52, +1.49] | PASS | 2.335 | 2.359 | +1.03 [+0.05, +1.62] | PASS |
| tiny-hit | 2.326 | 2.342 | +0.66 [-0.02, +1.72] | PASS | 2.343 | 2.365 | +0.94 [+0.08, +1.53] | PASS |
| tiny-miss | 2.340 | 2.360 | +0.85 [+0.51, +2.26] | PASS | 2.342 | 2.353 | +0.50 [+0.03, +1.20] | PASS |
| tiny-class30 | 2.397 | 2.413 | +0.69 [+0.27, +1.57] | PASS | 2.403 | 2.430 | +1.09 [+0.14, +1.70] | PASS |
| small-literal | 2.312 | 2.325 | +0.54 [+0.32, +0.92] | PASS | 2.348 | 2.373 | +1.07 [+0.40, +1.67] | PASS |
| small-regex | 2.944 | 2.950 | +0.22 [-0.45, +1.46] | PASS | 3.014 | 3.005 | -0.30 [-0.86, +0.91] | PASS |
| literal-dense | 22.006 | 22.946 | +4.27 [+2.92, +4.96] | INCONCLUSIVE | 22.432 | 23.335 | +4.03 [+3.18, +5.99] | FAIL |
| literal-sparse-lines | 4.587 | 4.593 | +0.12 [-3.41, +1.94] | PASS | 4.929 | 5.012 | +1.68 [-0.77, +3.74] | INCONCLUSIVE |
| literal-absent | 4.185 | 4.224 | +0.94 [-0.35, +3.63] | INCONCLUSIVE | 4.443 | 4.498 | +1.25 [-1.33, +2.88] | PASS |
| literal-fixed | 11.655 | 11.904 | +2.14 [-0.32, +3.55] | INCONCLUSIVE | 12.202 | 12.458 | +2.10 [-0.77, +2.96] | PASS |
| literal-insensitive | 38.000 | 39.398 | +3.68 [+1.49, +4.25] | INCONCLUSIVE | 39.041 | 39.829 | +2.02 [+0.45, +3.01] | INCONCLUSIVE |
| literal-word | 36.138 | 37.293 | +3.19 [+2.00, +4.61] | INCONCLUSIVE | 36.842 | 38.075 | +3.35 [+1.50, +4.35] | INCONCLUSIVE |
| literal-count | 13.884 | 14.940 | +7.61 [+3.83, +11.00] | FAIL | 14.530 | 15.511 | +6.75 [+4.20, +8.00] | FAIL |
| literal-count-matches | 49.328 | 50.502 | +2.38 [+1.33, +3.22] | INCONCLUSIVE | 50.777 | 51.781 | +1.98 [+0.89, +3.65] | INCONCLUSIVE |
| literal-only-offset | 40.077 | 43.959 | +9.69 [+7.85, +10.84] | FAIL | 41.707 | 46.535 | +11.57 [+6.08, +13.25] | FAIL |
| literal-context | 4.630 | 4.634 | +0.09 [-1.58, +1.44] | PASS | 4.978 | 4.969 | -0.19 [-7.07, +5.01] | INCONCLUSIVE |
| literal-invert | 10.319 | 10.524 | +1.99 [+1.18, +2.41] | PASS | 11.011 | 10.926 | -0.77 [-4.36, +3.14] | INCONCLUSIVE |
| literal-limit | 2.383 | 2.408 | +1.04 [+0.15, +1.81] | PASS | 2.429 | 2.407 | -0.92 [-1.86, +2.89] | PASS |
| literal-quiet | 2.385 | 2.393 | +0.35 [-0.27, +1.19] | PASS | 2.360 | 2.375 | +0.66 [-1.16, +2.11] | PASS |
| literal-multi-pattern | 13.458 | 13.753 | +2.20 [+1.51, +3.17] | INCONCLUSIVE | 13.089 | 13.347 | +1.97 [+1.39, +3.24] | INCONCLUSIVE |
| regex-general | 18.598 | 19.166 | +3.05 [+2.23, +3.94] | INCONCLUSIVE | 18.226 | 18.595 | +2.02 [+1.59, +3.01] | INCONCLUSIVE |
| regex-captures | 68.652 | 70.268 | +2.35 [+1.08, +2.77] | PASS | 68.171 | 69.590 | +2.08 [+0.93, +3.07] | INCONCLUSIVE |
| regex-replace | 138.174 | 140.816 | +1.91 [+0.64, +3.23] | INCONCLUSIVE | 137.108 | 139.308 | +1.60 [-0.20, +3.16] | INCONCLUSIVE |
| regex-anchored | 26.520 | 27.234 | +2.69 [+1.40, +4.11] | INCONCLUSIVE | 25.609 | 27.014 | +5.49 [+3.06, +10.58] | FAIL |
| regex-zero-length | 14.585 | 15.036 | +3.09 [+2.44, +4.11] | INCONCLUSIVE | 14.324 | 14.955 | +4.41 [+1.84, +6.34] | INCONCLUSIVE |
| regex-word-class | 42.489 | 42.485 | -0.01 [-0.30, +0.33] | PASS | 41.895 | 41.877 | -0.04 [-0.21, +0.16] | PASS |
| regex-lazy-class | 13.021 | 9.477 | -27.22 [-28.26, -26.62] | PASS | 12.717 | 9.245 | -27.31 [-27.77, -26.60] | PASS |
| regex-whole-class | 14.623 | 14.654 | +0.22 [-0.25, +0.90] | PASS | 14.351 | 14.249 | -0.71 [-1.05, +0.10] | PASS |
| unicode-literal | 8.551 | 9.003 | +5.28 [+2.35, +7.92] | INCONCLUSIVE | 8.292 | 8.759 | +5.63 [+3.30, +8.16] | FAIL |
| unicode-fold | 15.066 | 15.138 | +0.48 [-0.50, +1.21] | PASS | 15.288 | 15.492 | +1.33 [-0.37, +2.19] | PASS |
| unicode-word | 12.766 | 13.164 | +3.12 [+1.84, +4.03] | INCONCLUSIVE | 12.587 | 13.035 | +3.55 [+0.20, +4.92] | INCONCLUSIVE |
| unicode-property | 11.451 | 11.819 | +3.21 [+1.93, +3.88] | INCONCLUSIVE | 11.583 | 11.998 | +3.58 [-1.56, +6.42] | INCONCLUSIVE |
| unicode-class-fallback | 9.342 | 9.614 | +2.90 [+1.94, +3.67] | INCONCLUSIVE | 9.448 | 9.561 | +1.19 [+0.11, +2.64] | PASS |
| crlf | 23.246 | 23.600 | +1.52 [+0.32, +3.35] | INCONCLUSIVE | 23.348 | 23.839 | +2.10 [-0.45, +11.29] | INCONCLUSIVE |
| multiline | 30.869 | 30.924 | +0.18 [-2.41, +1.96] | PASS | 31.560 | 31.969 | +1.29 [-0.11, +3.71] | INCONCLUSIVE |
| binary-default | 2.339 | 2.359 | +0.86 [+0.20, +1.34] | PASS | 2.420 | 2.452 | +1.32 [-0.82, +2.38] | PASS |
| binary-text | 9.808 | 10.204 | +4.04 [+2.13, +7.41] | INCONCLUSIVE | 10.432 | 10.732 | +2.87 [+0.48, +3.87] | INCONCLUSIVE |
| null-lines | 9.760 | 9.773 | +0.13 [-1.01, +0.66] | PASS | 10.470 | 10.414 | -0.54 [-3.06, +2.10] | PASS |
| long-line-literal | 3.755 | 3.821 | +1.76 [-0.52, +3.84] | INCONCLUSIVE | 4.344 | 4.300 | -1.03 [-3.01, +3.92] | INCONCLUSIVE |
| long-line-class | 3.367 | 3.408 | +1.23 [-2.69, +3.06] | INCONCLUSIVE | 3.860 | 3.755 | -2.73 [-14.09, +2.08] | PASS |
| subtitles-sherlock | 10.260 | 10.198 | -0.61 [-4.56, +5.74] | INCONCLUSIVE | 10.089 | 10.018 | -0.71 [-6.08, +4.26] | INCONCLUSIVE |
| subtitles-sherlock-lines | 12.942 | 12.964 | +0.17 [-5.51, +4.88] | INCONCLUSIVE | 11.698 | 11.592 | -0.91 [-1.84, +1.37] | PASS |
| subtitles-frequent | 62.069 | 63.232 | +1.88 [+0.95, +2.87] | PASS | 61.626 | 62.356 | +1.18 [+0.69, +1.79] | PASS |
| subtitles-alpha30 | 159.647 | 14.015 | -91.22 [-91.36, -91.14] | PASS | 160.468 | 13.354 | -91.68 [-91.74, -91.31] | PASS |
| subtitles-hex17 | 159.806 | 14.658 | -90.83 [-90.92, -90.71] | PASS | 161.198 | 15.345 | -90.48 [-90.99, -90.12] | PASS |
| subtitles-digits8 | 12.974 | 11.836 | -8.76 [-10.29, -7.84] | PASS | 14.435 | 12.846 | -11.01 [-12.98, -5.33] | INCONCLUSIVE |
| json | 2.374 | 2.381 | +0.26 [-0.53, +1.03] | PASS | 2.518 | 2.553 | +1.39 [-3.69, +6.70] | INCONCLUSIVE |
| color | 2.525 | 2.562 | +1.48 [+0.95, +1.94] | PASS | 2.669 | 2.679 | +0.36 [-0.77, +5.59] | INCONCLUSIVE |
| class-dense-1 | 21.301 | 21.424 | +0.58 [+0.24, +1.37] | PASS | 21.509 | 21.616 | +0.50 [-0.04, +1.18] | PASS |
| class-dense-2 | 21.518 | 7.418 | -65.53 [-66.06, -65.23] | PASS | 21.510 | 7.328 | -65.93 [-66.16, -65.73] | PASS |
| class-dense-3 | 21.806 | 7.385 | -66.13 [-66.55, -65.79] | PASS | 21.808 | 7.415 | -66.00 [-66.30, -65.45] | PASS |
| class-dense-7 | 32.242 | 6.468 | -79.94 [-80.39, -79.77] | PASS | 32.289 | 6.519 | -79.81 [-80.18, -79.43] | PASS |
| class-dense-8 | 32.644 | 6.749 | -79.33 [-79.81, -78.60] | PASS | 32.400 | 6.637 | -79.52 [-79.96, -79.27] | PASS |
| class-dense-15 | 33.352 | 6.725 | -79.84 [-80.28, -79.59] | PASS | 33.011 | 6.547 | -80.17 [-81.02, -80.00] | PASS |
| class-dense-16 | 33.049 | 6.581 | -80.09 [-80.22, -79.78] | PASS | 33.201 | 6.754 | -79.66 [-79.99, -79.44] | PASS |
| class-dense-30 | 34.567 | 6.674 | -80.69 [-80.91, -80.36] | PASS | 34.519 | 6.578 | -80.94 [-81.09, -80.37] | PASS |
| class-dense-64 | 37.964 | 7.050 | -81.43 [-81.59, -81.25] | PASS | 37.921 | 6.999 | -81.54 [-81.66, -81.33] | PASS |
| class-dense-65 | 38.032 | 6.373 | -83.24 [-83.54, -83.02] | PASS | 38.012 | 6.372 | -83.24 [-83.36, -82.98] | PASS |
| class-dense-129 | 42.389 | 5.202 | -87.73 [-88.31, -87.56] | PASS | 42.234 | 5.005 | -88.15 [-88.85, -87.89] | PASS |
| class-absent-1 | 42.454 | 42.381 | -0.17 [-0.55, +0.12] | PASS | 42.102 | 42.171 | +0.16 [-0.26, +0.54] | PASS |
| class-absent-2 | 42.467 | 5.252 | -87.63 [-88.34, -87.40] | PASS | 42.429 | 5.323 | -87.45 [-88.33, -87.20] | PASS |
| class-absent-8 | 42.308 | 5.436 | -87.15 [-87.33, -86.91] | PASS | 42.391 | 5.198 | -87.74 [-88.11, -86.62] | PASS |
| class-absent-16 | 42.586 | 5.679 | -86.67 [-87.12, -86.42] | PASS | 42.469 | 5.245 | -87.65 [-88.17, -87.27] | PASS |
| class-absent-30 | 42.240 | 5.298 | -87.46 [-87.88, -86.70] | PASS | 42.272 | 5.168 | -87.77 [-88.21, -87.49] | PASS |
| class-absent-65 | 42.327 | 4.634 | -89.05 [-89.28, -88.35] | PASS | 42.473 | 4.901 | -88.46 [-88.83, -87.98] | PASS |
| class-varied-2 | 29.242 | 25.299 | -13.48 [-14.34, -12.04] | PASS | 29.858 | 25.898 | -13.26 [-15.82, -12.00] | PASS |
| class-varied-8 | 31.066 | 24.667 | -20.60 [-21.99, -20.07] | PASS | 31.248 | 24.560 | -21.40 [-22.02, -20.66] | PASS |
| class-varied-16 | 34.185 | 23.547 | -31.12 [-31.44, -30.48] | PASS | 34.063 | 23.465 | -31.11 [-31.48, -30.33] | PASS |
| class-varied-30 | 37.129 | 20.849 | -43.85 [-44.31, -43.49] | PASS | 36.928 | 20.648 | -44.08 [-44.63, -43.39] | PASS |
| class-varied-65 | 44.229 | 14.803 | -66.53 [-66.73, -66.45] | PASS | 44.181 | 14.739 | -66.64 [-66.82, -66.41] | PASS |
| wide-ascii | 22.440 | 9.291 | -58.60 [-59.13, -58.28] | PASS | 22.788 | 9.270 | -59.32 [-59.82, -58.76] | PASS |
| optional-class | 23.326 | 23.748 | +1.81 [+1.14, +2.46] | PASS | 23.008 | 23.418 | +1.78 [+1.05, +2.34] | PASS |
| captured-class | 28.620 | 28.679 | +0.21 [-0.01, +0.42] | PASS | 28.708 | 28.817 | +0.38 [-0.00, +0.85] | PASS |
| tree-literal | 4.149 | 4.109 | -0.96 [-2.67, -0.11] | PASS | 4.214 | 4.191 | -0.54 [-1.55, +2.73] | PASS |
| tree-regex | 7.267 | 7.345 | +1.07 [-1.97, +3.10] | INCONCLUSIVE | 7.308 | 7.366 | +0.79 [-1.51, +1.98] | PASS |
| tree-files | 4.088 | 4.093 | +0.12 [-4.66, +1.44] | PASS | 4.086 | 4.108 | +0.54 [-2.56, +1.58] | PASS |
| tree-sorted | 3.774 | 3.833 | +1.55 [+0.33, +2.20] | PASS | 3.795 | 3.794 | -0.02 [-0.55, +0.69] | PASS |
| kernel-default | 116.512 | 116.072 | -0.38 [-1.01, +0.34] | PASS | 117.530 | 116.508 | -0.87 [-1.60, +0.17] | PASS |
| kernel-c | 86.825 | 87.296 | +0.54 [-0.89, +1.91] | PASS | 86.317 | 86.606 | +0.33 [-0.53, +3.15] | INCONCLUSIVE |
| cold-literal | 10.815 | 10.712 | -0.95 [-2.71, +0.93] | PASS | 10.595 | 10.576 | -0.18 [-0.98, +0.31] | PASS |
| cold-regex | 24.814 | 25.238 | +1.71 [+0.72, +2.91] | PASS | 24.590 | 25.180 | +2.40 [+1.20, +3.57] | INCONCLUSIVE |

## Measurement checks

Session A: 3,645 timed batches / 23,085 timed invocations. Warm-I/O cases: none. Unstable-control cases: none. Cgroup peak: 0.05 GiB.

```text
low 0
high 0
max 0
oom 0
oom_kill 0
oom_group_kill 0
sock_throttled 0
```

Session B: 3,645 timed batches / 22,815 timed invocations. Warm-I/O cases: ['subtitles-digits8']. Unstable-control cases: none. Cgroup peak: 0.06 GiB.

```text
low 0
high 0
max 0
oom 0
oom_kill 0
oom_group_kill 0
sock_throttled 0
```
