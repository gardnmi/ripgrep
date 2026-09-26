# Complete performance results

Elapsed time per invocation, including startup; lower is better.
Positive percentages are slowdowns. Intervals are paired bootstrap
95% intervals for elapsed-time change. They are per-case intervals,
not simultaneous confidence across the whole suite. All observations
remain in the linked JSON files. PASS permits the predeclared practical
margin; it does not mean exactly zero slowdown.

Session A: [final-session-a.json](final-session-a.json); seed 269361; 15 paired rounds; reverse order False. 97 PASS, 1 FAIL, 19 INCONCLUSIVE.

Session B: [final-session-b.json](final-session-b.json); seed 269367; 15 paired rounds; reverse order True. 97 PASS, 1 FAIL, 19 INCONCLUSIVE.

| Workload | A system rg ms | A candidate ms | A change %, 95% interval | A verdict | B system rg ms | B candidate ms | B change %, 95% interval | B verdict |
| --- | ---: | ---: | --- | --- | ---: | ---: | --- | --- |
| source-literal | 4.363 | 2.615 | -40.07 [-41.45, -38.88] | PASS | 4.602 | 2.697 | -41.39 [-42.89, -39.43] | PASS |
| source-absent | 4.160 | 2.580 | -37.98 [-39.27, -37.30] | PASS | 4.330 | 2.700 | -37.64 [-39.55, -36.36] | PASS |
| source-regex | 7.970 | 5.763 | -27.69 [-29.49, -26.46] | PASS | 8.269 | 5.985 | -27.62 [-28.40, -25.32] | PASS |
| source-ignore-case | 4.725 | 2.750 | -41.79 [-42.94, -39.86] | PASS | 4.816 | 2.854 | -40.73 [-42.31, -38.64] | PASS |
| source-glob | 3.722 | 2.534 | -31.91 [-33.42, -30.96] | PASS | 3.912 | 2.713 | -30.66 [-33.09, -28.90] | PASS |
| source-files | 3.413 | 2.149 | -37.03 [-38.42, -35.47] | PASS | 4.076 | 2.363 | -42.03 [-44.14, -40.70] | PASS |
| source-files-hidden | 3.529 | 2.161 | -38.76 [-39.73, -37.28] | PASS | 3.918 | 2.224 | -43.22 [-45.56, -36.88] | PASS |
| source-multi | 4.391 | 2.676 | -39.05 [-40.33, -36.83] | PASS | 4.415 | 2.660 | -39.75 [-41.20, -38.45] | PASS |
| source-context | 4.506 | 2.740 | -39.19 [-40.56, -38.12] | PASS | 4.625 | 2.742 | -40.71 [-42.09, -38.79] | PASS |
| source-sorted | 4.226 | 4.167 | -1.41 [-2.42, +0.75] | PASS | 4.250 | 4.207 | -1.00 [-3.00, +1.64] | PASS |
| source-explicit-one-thread | 4.221 | 4.155 | -1.55 [-3.47, -0.39] | PASS | 4.234 | 4.250 | +0.38 [-1.68, +2.14] | PASS |
| tools-literal | 11.594 | 9.329 | -19.53 [-20.76, -16.16] | PASS | 11.600 | 9.260 | -20.17 [-20.72, -17.41] | PASS |
| tools-files-with-match | 11.506 | 9.329 | -18.92 [-20.48, -17.53] | PASS | 11.585 | 9.221 | -20.41 [-21.25, -19.26] | PASS |
| tools-glob | 8.557 | 6.292 | -26.46 [-27.81, -24.67] | PASS | 8.583 | 6.222 | -27.51 [-28.84, -25.34] | PASS |
| tools-regex | 11.921 | 9.624 | -19.27 [-21.20, -14.95] | PASS | 11.802 | 9.559 | -19.01 [-20.26, -16.97] | PASS |
| tools-files | 7.427 | 5.448 | -26.64 [-28.19, -23.83] | PASS | 7.419 | 5.567 | -24.96 [-27.01, -22.87] | PASS |
| kernel-literal | 92.405 | 84.009 | -9.09 [-14.09, -0.91] | INCONCLUSIVE | 85.105 | 80.782 | -5.08 [-7.36, -3.83] | PASS |
| kernel-regex | 84.073 | 78.977 | -6.06 [-7.30, -4.72] | PASS | 84.861 | 81.504 | -3.96 [-6.85, -0.57] | PASS |
| kernel-files | 26.535 | 23.475 | -11.53 [-14.24, -7.18] | PASS | 26.199 | 23.021 | -12.13 [-14.42, -7.13] | PASS |
| tiny-hit | 1.395 | 1.419 | +1.75 [+0.63, +4.78] | PASS | 1.409 | 1.447 | +2.72 [+0.77, +4.66] | PASS |
| tiny-miss | 1.384 | 1.429 | +3.30 [+0.81, +4.27] | PASS | 1.387 | 1.427 | +2.84 [-0.92, +4.28] | PASS |
| small-regex | 2.229 | 2.180 | -2.19 [-2.83, +0.06] | PASS | 2.234 | 2.200 | -1.53 [-3.91, -0.35] | PASS |
| log-lines | 4.354 | 4.334 | -0.45 [-5.86, +2.13] | INCONCLUSIVE | 4.823 | 4.866 | +0.90 [-6.79, +3.14] | INCONCLUSIVE |
| log-context | 3.779 | 3.757 | -0.59 [-1.54, +1.13] | PASS | 4.919 | 4.846 | -1.48 [-5.65, +0.88] | PASS |
| log-count | 8.025 | 7.912 | -1.42 [-3.20, +0.21] | PASS | 8.813 | 8.450 | -4.11 [-5.15, -1.41] | PASS |
| log-multi | 10.782 | 10.782 | +0.00 [-2.17, +1.57] | PASS | 11.605 | 11.460 | -1.24 [-2.84, +0.20] | PASS |
| log-ignore-case | 31.967 | 29.513 | -7.67 [-8.48, -5.76] | PASS | 33.101 | 31.332 | -5.35 [-7.33, -3.99] | INCONCLUSIVE |
| log-json | 1.420 | 1.455 | +2.48 [+0.80, +3.25] | PASS | 1.464 | 1.493 | +1.98 [+0.39, +3.84] | PASS |
| prose-absent | 13.016 | 12.799 | -1.66 [-7.80, +3.01] | INCONCLUSIVE | 15.742 | 15.443 | -1.90 [-8.93, +5.56] | INCONCLUSIVE |
| prose-count | 52.056 | 52.218 | +0.31 [-2.73, +1.64] | PASS | 55.898 | 55.701 | -0.35 [-2.17, +1.64] | INCONCLUSIVE |
| prose-regex | 17.664 | 17.279 | -2.18 [-3.22, -0.65] | PASS | 20.436 | 20.516 | +0.40 [-5.09, +5.83] | INCONCLUSIVE |
| unicode-fold | 14.923 | 15.061 | +0.92 [-1.41, +2.08] | PASS | 15.393 | 15.392 | -0.00 [-3.12, +2.95] | PASS |
| broad-empty | 2.293 | 2.313 | +0.86 [+0.55, +1.19] | PASS | 2.324 | 2.332 | +0.35 [-0.38, +1.83] | PASS |
| broad-tiny-hit | 2.299 | 2.327 | +1.24 [+0.78, +1.67] | PASS | 2.305 | 2.357 | +2.24 [+0.78, +3.04] | PASS |
| broad-tiny-miss | 2.296 | 2.324 | +1.19 [+0.79, +1.89] | PASS | 2.326 | 2.345 | +0.81 [-0.64, +2.50] | PASS |
| broad-tiny-class30 | 2.356 | 2.379 | +0.97 [+0.67, +1.24] | PASS | 2.396 | 2.427 | +1.29 [+0.44, +2.10] | PASS |
| broad-small-literal | 2.296 | 2.330 | +1.50 [+0.97, +1.71] | PASS | 2.327 | 2.357 | +1.27 [+0.42, +2.20] | PASS |
| broad-small-regex | 3.006 | 2.979 | -0.90 [-2.03, +0.59] | PASS | 3.014 | 2.979 | -1.16 [-2.47, +1.16] | PASS |
| broad-literal-dense | 24.928 | 23.439 | -5.97 [-6.44, -5.52] | PASS | 25.621 | 24.193 | -5.57 [-7.41, -2.96] | PASS |
| broad-literal-sparse-lines | 4.989 | 4.950 | -0.78 [-2.49, -0.12] | PASS | 5.717 | 5.660 | -1.00 [-2.17, -0.40] | PASS |
| broad-literal-absent | 4.414 | 4.360 | -1.22 [-2.31, +2.58] | PASS | 4.983 | 4.913 | -1.41 [-2.22, -0.04] | PASS |
| broad-literal-fixed | 12.387 | 12.147 | -1.94 [-2.89, -0.97] | PASS | 12.941 | 12.762 | -1.39 [-2.16, -0.87] | PASS |
| broad-literal-insensitive | 40.672 | 41.465 | +1.95 [+1.05, +2.53] | INCONCLUSIVE | 41.244 | 42.116 | +2.11 [+1.42, +2.94] | INCONCLUSIVE |
| broad-literal-word | 41.718 | 37.901 | -9.15 [-9.57, -8.63] | PASS | 42.549 | 38.678 | -9.10 [-9.47, -8.05] | PASS |
| broad-literal-count | 15.310 | 14.953 | -2.33 [-3.08, -1.99] | PASS | 16.220 | 15.841 | -2.34 [-3.70, -1.52] | PASS |
| broad-literal-count-matches | 59.532 | 57.393 | -3.59 [-5.15, -3.10] | INCONCLUSIVE | 60.845 | 58.664 | -3.58 [-6.11, -2.04] | INCONCLUSIVE |
| broad-literal-only-offset | 43.545 | 43.044 | -1.15 [-1.90, +0.17] | INCONCLUSIVE | 44.622 | 44.215 | -0.91 [-1.77, +2.54] | INCONCLUSIVE |
| broad-literal-context | 4.494 | 4.478 | -0.36 [-0.80, +0.07] | PASS | 5.181 | 5.110 | -1.36 [-3.83, +1.20] | PASS |
| broad-literal-invert | 11.499 | 11.145 | -3.07 [-3.64, -2.58] | PASS | 12.143 | 11.886 | -2.12 [-4.58, -1.12] | PASS |
| broad-literal-limit | 2.309 | 2.338 | +1.25 [+0.59, +1.73] | PASS | 2.319 | 2.350 | +1.34 [+1.03, +2.04] | PASS |
| broad-literal-quiet | 2.296 | 2.321 | +1.09 [+0.67, +1.20] | PASS | 2.305 | 2.337 | +1.39 [+0.81, +2.14] | PASS |
| broad-literal-multi-pattern | 14.373 | 13.948 | -2.96 [-3.43, -2.27] | PASS | 14.850 | 14.339 | -3.44 [-4.50, -1.72] | PASS |
| broad-regex-general | 20.512 | 20.297 | -1.05 [-1.64, -0.17] | FAIL | 20.626 | 20.447 | -0.87 [-1.83, +1.46] | FAIL |
| broad-regex-captures | 75.489 | 74.657 | -1.10 [-2.88, -0.16] | PASS | 74.918 | 73.340 | -2.11 [-2.99, -1.32] | PASS |
| broad-regex-replace | 146.303 | 145.500 | -0.55 [-2.78, +0.89] | PASS | 145.951 | 144.161 | -1.23 [-2.02, -0.37] | PASS |
| broad-regex-anchored | 29.728 | 29.866 | +0.47 [-3.49, +3.20] | INCONCLUSIVE | 29.326 | 29.953 | +2.14 [+0.26, +3.14] | INCONCLUSIVE |
| broad-regex-zero-length | 19.108 | 18.015 | -5.72 [-7.77, -3.39] | PASS | 19.050 | 18.159 | -4.68 [-6.57, -3.65] | PASS |
| broad-regex-word-class | 42.308 | 42.647 | +0.80 [+0.39, +1.57] | PASS | 42.525 | 42.944 | +0.99 [-0.18, +2.19] | PASS |
| broad-regex-lazy-class | 16.348 | 16.482 | +0.82 [-0.17, +1.59] | INCONCLUSIVE | 16.944 | 17.342 | +2.35 [-1.05, +5.94] | INCONCLUSIVE |
| broad-regex-whole-class | 15.708 | 16.074 | +2.33 [+1.33, +3.31] | INCONCLUSIVE | 16.154 | 16.477 | +2.00 [-1.92, +2.81] | PASS |
| broad-unicode-literal | 9.964 | 9.749 | -2.16 [-8.00, +4.76] | INCONCLUSIVE | 10.141 | 9.745 | -3.91 [-5.93, -1.52] | PASS |
| broad-unicode-fold | 15.835 | 15.963 | +0.81 [+0.25, +2.83] | PASS | 16.572 | 16.630 | +0.35 [-1.08, +2.28] | PASS |
| broad-unicode-word | 13.952 | 13.453 | -3.57 [-5.14, -2.84] | PASS | 14.785 | 14.240 | -3.68 [-5.68, -3.06] | PASS |
| broad-unicode-property | 13.173 | 12.408 | -5.81 [-6.51, -5.19] | PASS | 13.867 | 13.084 | -5.65 [-6.46, -4.69] | INCONCLUSIVE |
| broad-unicode-class-fallback | 11.423 | 11.573 | +1.31 [+0.23, +3.56] | INCONCLUSIVE | 12.097 | 12.055 | -0.35 [-0.65, +0.87] | PASS |
| broad-crlf | 26.133 | 24.981 | -4.41 [-5.08, -3.64] | PASS | 27.132 | 25.820 | -4.83 [-5.70, -4.28] | PASS |
| broad-multiline | 34.249 | 33.953 | -0.87 [-1.80, -0.36] | PASS | 35.241 | 34.917 | -0.92 [-1.88, -0.45] | PASS |
| broad-binary-default | 2.295 | 2.323 | +1.22 [+0.81, +1.96] | PASS | 2.324 | 2.354 | +1.27 [+0.46, +2.28] | PASS |
| broad-binary-text | 10.596 | 10.593 | -0.03 [-1.29, +1.15] | PASS | 10.918 | 10.972 | +0.49 [-0.85, +1.68] | PASS |
| broad-null-lines | 10.943 | 10.513 | -3.93 [-4.79, -3.09] | PASS | 11.005 | 10.530 | -4.31 [-5.03, -3.35] | PASS |
| broad-long-line-literal | 4.011 | 3.998 | -0.32 [-3.50, +1.65] | PASS | 4.173 | 4.118 | -1.32 [-1.82, -0.22] | PASS |
| broad-long-line-class | 3.674 | 3.622 | -1.42 [-3.36, +2.74] | PASS | 3.754 | 3.748 | -0.14 [-0.97, +1.36] | PASS |
| broad-subtitles-sherlock | 15.907 | 15.864 | -0.27 [-2.46, +3.32] | INCONCLUSIVE | 15.578 | 15.847 | +1.72 [-1.69, +6.09] | INCONCLUSIVE |
| broad-subtitles-sherlock-lines | 19.362 | 19.294 | -0.35 [-4.07, +0.91] | PASS | 19.185 | 18.917 | -1.40 [-2.07, -0.92] | PASS |
| broad-subtitles-frequent | 75.870 | 73.302 | -3.38 [-5.18, -0.69] | PASS | 73.042 | 72.535 | -0.69 [-1.43, +0.22] | PASS |
| broad-subtitles-alpha30 | 165.757 | 166.979 | +0.74 [+0.50, +0.87] | PASS | 165.012 | 166.233 | +0.74 [+0.60, +0.85] | PASS |
| broad-subtitles-hex17 | 164.666 | 166.190 | +0.93 [+0.59, +1.19] | PASS | 165.327 | 166.708 | +0.84 [+0.64, +1.09] | PASS |
| broad-subtitles-digits8 | 18.276 | 19.328 | +5.76 [-3.44, +12.65] | INCONCLUSIVE | 18.463 | 18.267 | -1.07 [-2.18, +0.51] | PASS |
| broad-json | 2.361 | 2.369 | +0.34 [-0.66, +2.01] | PASS | 2.332 | 2.357 | +1.06 [+0.77, +1.79] | PASS |
| broad-color | 2.623 | 2.575 | -1.82 [-2.88, +2.88] | PASS | 2.517 | 2.544 | +1.06 [+0.52, +2.62] | PASS |
| broad-class-dense-1 | 22.357 | 22.649 | +1.31 [+0.21, +2.59] | PASS | 22.656 | 22.946 | +1.28 [+0.73, +1.67] | PASS |
| broad-class-dense-2 | 22.433 | 22.701 | +1.20 [+0.53, +1.66] | PASS | 22.854 | 23.144 | +1.27 [+0.35, +1.83] | PASS |
| broad-class-dense-3 | 23.259 | 23.602 | +1.48 [-1.32, +4.34] | INCONCLUSIVE | 23.391 | 23.464 | +0.31 [-0.35, +1.52] | PASS |
| broad-class-dense-7 | 32.631 | 32.758 | +0.39 [-0.48, +1.72] | PASS | 32.936 | 33.510 | +1.74 [+0.69, +2.81] | PASS |
| broad-class-dense-8 | 32.498 | 32.961 | +1.43 [+0.62, +1.84] | PASS | 33.155 | 33.383 | +0.69 [+0.29, +1.05] | PASS |
| broad-class-dense-15 | 33.617 | 33.929 | +0.93 [-0.24, +1.81] | PASS | 33.763 | 34.008 | +0.73 [-0.28, +1.44] | PASS |
| broad-class-dense-16 | 33.618 | 33.896 | +0.83 [-0.22, +1.67] | PASS | 34.018 | 34.339 | +0.94 [-0.06, +1.58] | PASS |
| broad-class-dense-30 | 35.353 | 35.716 | +1.03 [-0.31, +2.93] | PASS | 35.256 | 35.701 | +1.26 [+0.41, +1.49] | PASS |
| broad-class-dense-64 | 38.784 | 38.963 | +0.46 [-0.53, +2.22] | PASS | 38.772 | 38.923 | +0.39 [-0.35, +0.84] | PASS |
| broad-class-dense-65 | 38.429 | 38.536 | +0.28 [-0.23, +1.13] | PASS | 38.374 | 38.650 | +0.72 [-0.45, +1.87] | PASS |
| broad-class-dense-129 | 42.367 | 42.755 | +0.91 [+0.56, +1.18] | PASS | 42.515 | 42.848 | +0.78 [-0.23, +1.82] | PASS |
| broad-class-absent-1 | 44.053 | 44.204 | +0.34 [-0.22, +3.40] | INCONCLUSIVE | 42.871 | 43.267 | +0.92 [+0.35, +1.67] | PASS |
| broad-class-absent-2 | 43.524 | 44.432 | +2.08 [+0.84, +3.24] | INCONCLUSIVE | 43.084 | 43.450 | +0.85 [-0.27, +1.60] | PASS |
| broad-class-absent-8 | 42.818 | 43.249 | +1.00 [+0.31, +2.04] | PASS | 43.396 | 43.743 | +0.80 [+0.30, +1.23] | PASS |
| broad-class-absent-16 | 42.653 | 42.945 | +0.68 [+0.10, +1.50] | PASS | 43.370 | 43.683 | +0.72 [+0.11, +1.05] | PASS |
| broad-class-absent-30 | 42.718 | 43.245 | +1.23 [+0.54, +2.24] | PASS | 43.509 | 43.905 | +0.91 [+0.53, +1.27] | PASS |
| broad-class-absent-65 | 42.821 | 43.150 | +0.77 [+0.11, +1.37] | PASS | 43.593 | 43.821 | +0.52 [-1.31, +2.02] | PASS |
| broad-class-varied-2 | 35.314 | 34.941 | -1.06 [-2.14, +2.08] | INCONCLUSIVE | 35.888 | 35.276 | -1.71 [-3.55, -0.89] | PASS |
| broad-class-varied-8 | 35.238 | 34.006 | -3.50 [-4.08, -2.61] | PASS | 35.988 | 34.419 | -4.36 [-5.14, -3.24] | PASS |
| broad-class-varied-16 | 37.950 | 36.667 | -3.38 [-3.80, -2.41] | PASS | 38.255 | 37.108 | -3.00 [-3.57, -1.56] | PASS |
| broad-class-varied-30 | 40.532 | 39.805 | -1.80 [-2.80, -0.88] | PASS | 41.132 | 39.674 | -3.54 [-4.68, -1.42] | PASS |
| broad-class-varied-65 | 46.506 | 45.863 | -1.38 [-2.27, -0.74] | PASS | 46.973 | 46.286 | -1.46 [-2.53, -0.96] | PASS |
| broad-wide-ascii | 24.418 | 24.544 | +0.52 [-0.30, +1.25] | PASS | 24.799 | 24.966 | +0.67 [+0.04, +3.05] | INCONCLUSIVE |
| broad-optional-class | 26.456 | 25.909 | -2.07 [-3.06, -1.08] | PASS | 26.733 | 26.184 | -2.05 [-3.42, +0.01] | PASS |
| broad-captured-class | 30.137 | 30.499 | +1.20 [+0.83, +1.71] | PASS | 29.843 | 30.197 | +1.18 [-0.55, +3.91] | INCONCLUSIVE |
| broad-tree-literal | 3.849 | 2.212 | -42.53 [-43.35, -41.41] | PASS | 3.938 | 2.286 | -41.96 [-44.54, -39.50] | PASS |
| broad-tree-regex | 7.463 | 5.471 | -26.69 [-29.12, -25.90] | PASS | 7.303 | 5.291 | -27.55 [-28.07, -26.09] | PASS |
| broad-tree-files | 3.756 | 2.198 | -41.48 [-42.88, -40.29] | PASS | 3.752 | 2.194 | -41.53 [-42.67, -39.29] | PASS |
| broad-tree-sorted | 3.813 | 3.741 | -1.88 [-3.65, +0.14] | PASS | 3.831 | 3.885 | +1.43 [-2.98, +3.51] | INCONCLUSIVE |
| broad-kernel-default | 122.190 | 118.839 | -2.74 [-6.22, +1.61] | INCONCLUSIVE | 120.029 | 115.292 | -3.95 [-5.00, -2.23] | PASS |
| broad-kernel-c | 91.849 | 88.404 | -3.75 [-5.76, +2.50] | PASS | 91.388 | 91.091 | -0.32 [-4.84, +5.99] | INCONCLUSIVE |
| broad-cold-literal | 14.917 | 15.115 | +1.32 [-6.67, +2.67] | PASS | 22.773 | 22.366 | -1.79 [-5.66, +5.58] | INCONCLUSIVE |
| broad-cold-regex | 29.750 | 26.953 | -9.40 [-22.05, +0.09] | INCONCLUSIVE | 30.641 | 30.331 | -1.01 [-5.73, +6.89] | INCONCLUSIVE |
| type-selected | 4.204 | 2.828 | -32.73 [-33.83, -31.25] | PASS | 4.118 | 2.793 | -32.19 [-35.05, -30.09] | PASS |
| type-negated | 3.759 | 2.343 | -37.68 [-38.92, -35.45] | PASS | 3.652 | 2.326 | -36.30 [-39.20, -34.73] | INCONCLUSIVE |
| type-custom | 4.189 | 2.833 | -32.37 [-35.30, -29.13] | PASS | 4.256 | 2.809 | -33.99 [-35.41, -32.59] | PASS |
| type-list | 1.156 | 1.139 | -1.42 [-2.98, +0.90] | PASS | 1.155 | 1.162 | +0.62 [-2.51, +3.01] | PASS |

## Additional unchanged source reference

The candidate must also pass against this unmodified reference.
These comparisons use the same paired rounds.

| Workload | A reference ms | A candidate change %, 95% interval | A verdict | B reference ms | B candidate change %, 95% interval | B verdict |
| --- | ---: | --- | --- | ---: | --- | --- |
| source-literal | 5.290 | -50.56 [-51.49, -48.92] | PASS | 5.303 | -49.13 [-50.74, -47.79] | PASS |
| source-absent | 5.263 | -50.98 [-52.19, -50.10] | PASS | 5.319 | -49.23 [-50.25, -48.27] | PASS |
| source-regex | 7.973 | -27.72 [-29.10, -25.85] | PASS | 8.210 | -27.09 [-28.32, -24.66] | PASS |
| source-ignore-case | 5.358 | -48.67 [-50.10, -47.95] | PASS | 5.502 | -48.12 [-49.80, -46.89] | PASS |
| source-glob | 4.950 | -48.81 [-50.04, -47.86] | PASS | 5.230 | -48.13 [-49.47, -44.88] | PASS |
| source-files | 3.355 | -35.95 [-38.35, -32.08] | PASS | 4.008 | -41.05 [-43.90, -40.21] | PASS |
| source-files-hidden | 3.476 | -37.83 [-38.80, -36.44] | PASS | 3.814 | -41.68 [-45.76, -36.82] | PASS |
| source-multi | 5.218 | -48.71 [-50.62, -47.70] | PASS | 5.295 | -49.76 [-51.76, -48.59] | PASS |
| source-context | 5.225 | -47.56 [-48.78, -46.64] | PASS | 5.243 | -47.70 [-49.28, -46.10] | PASS |
| source-sorted | 4.292 | -2.92 [-4.25, -0.99] | PASS | 4.249 | -0.99 [-4.30, +0.84] | PASS |
| source-explicit-one-thread | 4.242 | -2.05 [-5.10, -0.74] | PASS | 4.274 | -0.56 [-2.74, +1.79] | PASS |
| tools-literal | 11.851 | -21.28 [-22.45, -17.24] | PASS | 11.712 | -20.94 [-21.65, -18.23] | PASS |
| tools-files-with-match | 11.865 | -21.37 [-23.38, -19.62] | PASS | 11.544 | -20.13 [-21.95, -18.83] | PASS |
| tools-glob | 8.770 | -28.25 [-30.95, -25.84] | PASS | 8.597 | -27.63 [-31.57, -26.07] | PASS |
| tools-regex | 11.875 | -18.96 [-20.63, -14.46] | PASS | 11.963 | -20.10 [-22.08, -18.27] | PASS |
| tools-files | 7.360 | -25.98 [-27.05, -22.15] | PASS | 7.420 | -24.97 [-27.85, -23.21] | PASS |
| kernel-literal | 86.289 | -2.64 [-5.35, +6.38] | INCONCLUSIVE | 83.388 | -3.13 [-5.89, -1.20] | PASS |
| kernel-regex | 81.925 | -3.60 [-5.44, -2.54] | PASS | 84.026 | -3.00 [-6.54, +0.73] | PASS |
| kernel-files | 25.594 | -8.28 [-11.95, -3.48] | PASS | 25.408 | -9.40 [-12.00, -3.38] | PASS |
| tiny-hit | 1.524 | -6.84 [-8.16, -3.32] | PASS | 1.516 | -4.53 [-6.14, -2.93] | PASS |
| tiny-miss | 1.499 | -4.63 [-7.07, -3.08] | PASS | 1.498 | -4.78 [-6.34, -3.14] | PASS |
| small-regex | 2.277 | -4.24 [-5.02, -2.63] | PASS | 2.274 | -3.26 [-4.54, -2.17] | PASS |
| log-lines | 4.385 | -1.15 [-4.52, +4.15] | INCONCLUSIVE | 4.986 | -2.40 [-5.94, +2.60] | PASS |
| log-context | 3.857 | -2.60 [-3.72, -0.53] | PASS | 4.982 | -2.72 [-6.85, +0.16] | PASS |
| log-count | 7.990 | -0.98 [-3.02, +0.70] | PASS | 8.650 | -2.31 [-3.85, +0.91] | PASS |
| log-multi | 10.663 | +1.11 [-1.68, +2.13] | PASS | 11.553 | -0.80 [-3.76, +1.44] | PASS |
| log-ignore-case | 29.589 | -0.26 [-2.33, +1.35] | PASS | 30.659 | +2.19 [-0.24, +3.78] | INCONCLUSIVE |
| log-json | 1.538 | -5.38 [-7.59, -3.85] | PASS | 1.567 | -4.74 [-8.23, -3.24] | PASS |
| prose-absent | 12.489 | +2.49 [-4.78, +6.49] | INCONCLUSIVE | 15.591 | -0.95 [-9.93, +6.96] | INCONCLUSIVE |
| prose-count | 51.799 | +0.81 [-1.83, +1.62] | PASS | 54.973 | +1.32 [-2.04, +3.80] | INCONCLUSIVE |
| prose-regex | 17.567 | -1.64 [-3.80, +0.04] | PASS | 20.509 | +0.04 [-1.80, +10.45] | INCONCLUSIVE |
| unicode-fold | 14.850 | +1.42 [-1.04, +2.62] | PASS | 15.498 | -0.68 [-3.53, +2.36] | PASS |
| broad-empty | 2.383 | -2.92 [-3.19, -2.56] | PASS | 2.402 | -2.91 [-3.98, -1.71] | PASS |
| broad-tiny-hit | 2.392 | -2.70 [-3.11, -2.35] | PASS | 2.417 | -2.47 [-3.71, -1.35] | PASS |
| broad-tiny-miss | 2.398 | -3.08 [-3.64, -2.21] | PASS | 2.428 | -3.45 [-4.48, -1.02] | PASS |
| broad-tiny-class30 | 2.448 | -2.83 [-3.06, -2.43] | PASS | 2.491 | -2.58 [-3.71, -1.54] | PASS |
| broad-small-literal | 2.393 | -2.62 [-3.19, -2.15] | PASS | 2.445 | -3.60 [-4.28, -2.49] | PASS |
| broad-small-regex | 3.029 | -1.68 [-2.97, -0.06] | PASS | 3.034 | -1.80 [-2.65, +0.75] | PASS |
| broad-literal-dense | 23.906 | -1.95 [-2.60, -1.20] | PASS | 24.782 | -2.38 [-4.29, +0.40] | PASS |
| broad-literal-sparse-lines | 5.036 | -1.71 [-2.31, -0.93] | PASS | 5.694 | -0.59 [-1.94, +0.18] | PASS |
| broad-literal-absent | 4.467 | -2.39 [-4.06, +0.92] | PASS | 4.993 | -1.60 [-2.15, -0.59] | PASS |
| broad-literal-fixed | 12.185 | -0.31 [-1.17, +0.44] | PASS | 12.817 | -0.43 [-1.02, +0.86] | PASS |
| broad-literal-insensitive | 39.752 | +4.31 [+1.41, +5.16] | INCONCLUSIVE | 40.530 | +3.91 [+2.32, +4.54] | INCONCLUSIVE |
| broad-literal-word | 37.682 | +0.58 [+0.05, +1.16] | PASS | 38.608 | +0.18 [-0.68, +1.24] | PASS |
| broad-literal-count | 14.840 | +0.76 [-0.01, +1.31] | PASS | 15.580 | +1.67 [+0.47, +2.38] | PASS |
| broad-literal-count-matches | 56.521 | +1.54 [-1.79, +3.20] | INCONCLUSIVE | 57.048 | +2.83 [-0.28, +4.10] | INCONCLUSIVE |
| broad-literal-only-offset | 42.165 | +2.08 [+0.90, +3.61] | INCONCLUSIVE | 43.080 | +2.63 [+1.64, +6.59] | INCONCLUSIVE |
| broad-literal-context | 4.513 | -0.78 [-1.25, -0.28] | PASS | 5.145 | -0.68 [-2.18, +2.56] | PASS |
| broad-literal-invert | 11.166 | -0.19 [-0.82, +0.20] | PASS | 11.805 | +0.69 [-5.78, +2.39] | PASS |
| broad-literal-limit | 2.396 | -2.42 [-3.01, -2.01] | PASS | 2.425 | -3.08 [-3.67, -1.92] | PASS |
| broad-literal-quiet | 2.385 | -2.67 [-3.16, -2.43] | PASS | 2.393 | -2.34 [-2.94, -1.93] | PASS |
| broad-literal-multi-pattern | 14.164 | -1.52 [-2.66, -0.70] | PASS | 14.609 | -1.85 [-3.48, +0.05] | PASS |
| broad-regex-general | 19.458 | +4.31 [+3.89, +5.03] | FAIL | 19.558 | +4.55 [+3.65, +6.39] | FAIL |
| broad-regex-captures | 75.268 | -0.81 [-2.04, +0.38] | PASS | 74.371 | -1.39 [-2.61, -0.26] | PASS |
| broad-regex-replace | 146.958 | -0.99 [-2.59, +1.73] | PASS | 142.848 | +0.92 [-0.06, +1.72] | PASS |
| broad-regex-anchored | 30.926 | -3.43 [-5.82, +0.68] | PASS | 30.381 | -1.41 [-2.67, -0.03] | PASS |
| broad-regex-zero-length | 18.594 | -3.11 [-4.72, -0.36] | PASS | 18.705 | -2.92 [-4.67, -0.97] | PASS |
| broad-regex-word-class | 42.514 | +0.31 [-0.56, +1.08] | PASS | 43.030 | -0.20 [-1.44, +0.99] | PASS |
| broad-regex-lazy-class | 16.120 | +2.24 [+1.10, +3.64] | INCONCLUSIVE | 16.484 | +5.20 [+1.59, +9.70] | INCONCLUSIVE |
| broad-regex-whole-class | 16.039 | +0.22 [-1.74, +1.84] | PASS | 16.410 | +0.41 [-1.44, +1.69] | PASS |
| broad-unicode-literal | 10.230 | -4.70 [-12.40, +3.17] | INCONCLUSIVE | 9.743 | +0.02 [-3.27, +1.81] | PASS |
| broad-unicode-fold | 15.834 | +0.82 [-0.06, +2.49] | PASS | 16.678 | -0.29 [-2.00, +1.42] | PASS |
| broad-unicode-word | 13.425 | +0.21 [-0.44, +0.88] | PASS | 14.141 | +0.70 [-1.62, +1.44] | PASS |
| broad-unicode-property | 12.190 | +1.78 [+0.64, +2.56] | PASS | 12.780 | +2.38 [+0.34, +3.06] | INCONCLUSIVE |
| broad-unicode-class-fallback | 11.405 | +1.47 [+0.27, +3.51] | INCONCLUSIVE | 12.000 | +0.45 [-0.15, +2.51] | PASS |
| broad-crlf | 24.652 | +1.33 [-0.29, +2.75] | PASS | 25.656 | +0.64 [-0.59, +1.46] | PASS |
| broad-multiline | 33.683 | +0.80 [-0.12, +1.37] | PASS | 34.854 | +0.18 [-1.20, +1.25] | PASS |
| broad-binary-default | 2.385 | -2.59 [-3.37, -2.13] | PASS | 2.414 | -2.50 [-4.05, -1.54] | PASS |
| broad-binary-text | 10.574 | +0.18 [-0.63, +1.29] | PASS | 10.913 | +0.54 [-1.06, +2.32] | PASS |
| broad-null-lines | 10.771 | -2.40 [-3.86, -1.56] | PASS | 10.900 | -3.39 [-3.82, -2.10] | PASS |
| broad-long-line-literal | 4.014 | -0.38 [-3.89, +0.78] | PASS | 4.198 | -1.92 [-2.91, -0.26] | PASS |
| broad-long-line-class | 3.780 | -4.18 [-6.41, -1.23] | PASS | 3.832 | -2.18 [-3.29, -0.72] | PASS |
| broad-subtitles-sherlock | 16.091 | -1.41 [-5.16, +5.00] | INCONCLUSIVE | 16.320 | -2.90 [-8.19, +1.94] | PASS |
| broad-subtitles-sherlock-lines | 19.394 | -0.52 [-2.58, +2.08] | PASS | 19.045 | -0.67 [-1.17, +0.18] | PASS |
| broad-subtitles-frequent | 74.111 | -1.09 [-2.33, +2.58] | PASS | 71.694 | +1.17 [+0.35, +2.41] | PASS |
| broad-subtitles-alpha30 | 167.219 | -0.14 [-0.43, +0.09] | PASS | 166.200 | +0.02 [-0.12, +0.13] | PASS |
| broad-subtitles-hex17 | 166.285 | -0.06 [-0.23, +0.30] | PASS | 166.516 | +0.12 [-0.11, +0.33] | PASS |
| broad-subtitles-digits8 | 18.075 | +6.94 [-2.30, +12.55] | INCONCLUSIVE | 18.456 | -1.03 [-2.30, +0.89] | PASS |
| broad-json | 2.448 | -3.25 [-4.21, -1.99] | PASS | 2.424 | -2.77 [-3.21, -2.06] | PASS |
| broad-color | 2.667 | -3.46 [-4.71, +1.69] | PASS | 2.605 | -2.37 [-2.76, -0.78] | PASS |
| broad-class-dense-1 | 22.395 | +1.13 [-0.31, +2.91] | PASS | 22.806 | +0.62 [+0.19, +1.08] | PASS |
| broad-class-dense-2 | 22.496 | +0.91 [+0.32, +1.36] | PASS | 23.006 | +0.60 [+0.06, +1.42] | PASS |
| broad-class-dense-3 | 23.555 | +0.20 [-1.98, +3.67] | INCONCLUSIVE | 23.561 | -0.42 [-1.19, +0.63] | PASS |
| broad-class-dense-7 | 32.904 | -0.45 [-2.66, +0.03] | PASS | 33.266 | +0.73 [+0.00, +1.98] | PASS |
| broad-class-dense-8 | 32.815 | +0.45 [-0.26, +1.11] | PASS | 33.547 | -0.49 [-1.01, -0.14] | PASS |
| broad-class-dense-15 | 34.266 | -0.98 [-1.80, +0.07] | PASS | 33.985 | +0.07 [-0.37, +0.76] | PASS |
| broad-class-dense-16 | 34.079 | -0.54 [-1.97, +0.35] | PASS | 34.337 | +0.01 [-0.62, +0.92] | PASS |
| broad-class-dense-30 | 35.820 | -0.29 [-2.82, +0.93] | PASS | 35.764 | -0.18 [-1.20, +0.42] | PASS |
| broad-class-dense-64 | 39.104 | -0.36 [-2.34, +2.23] | PASS | 39.075 | -0.39 [-1.07, +0.19] | PASS |
| broad-class-dense-65 | 38.824 | -0.74 [-1.90, -0.01] | PASS | 38.745 | -0.25 [-0.48, +1.00] | PASS |
| broad-class-dense-129 | 42.863 | -0.25 [-0.81, +0.07] | PASS | 42.927 | -0.19 [-0.67, +0.92] | PASS |
| broad-class-absent-1 | 44.430 | -0.51 [-1.34, +2.24] | PASS | 43.324 | -0.13 [-0.82, +0.60] | PASS |
| broad-class-absent-2 | 44.010 | +0.96 [-0.13, +2.85] | PASS | 43.626 | -0.40 [-1.25, +0.20] | PASS |
| broad-class-absent-8 | 43.227 | +0.05 [-0.72, +1.08] | PASS | 43.644 | +0.23 [-0.23, +0.66] | PASS |
| broad-class-absent-16 | 43.048 | -0.24 [-0.58, +0.37] | PASS | 43.746 | -0.14 [-0.93, +0.37] | PASS |
| broad-class-absent-30 | 43.112 | +0.31 [-0.24, +1.28] | PASS | 43.979 | -0.17 [-0.48, +0.27] | PASS |
| broad-class-absent-65 | 43.213 | -0.15 [-0.64, +0.49] | PASS | 43.797 | +0.05 [-1.60, +0.88] | PASS |
| broad-class-varied-2 | 35.200 | -0.74 [-2.04, +3.15] | INCONCLUSIVE | 35.594 | -0.89 [-1.88, -0.41] | PASS |
| broad-class-varied-8 | 34.283 | -0.81 [-1.21, +0.11] | PASS | 34.886 | -1.34 [-1.85, -0.08] | PASS |
| broad-class-varied-16 | 36.481 | +0.51 [-0.21, +1.44] | PASS | 37.059 | +0.13 [-1.07, +2.05] | PASS |
| broad-class-varied-30 | 39.393 | +1.05 [+0.19, +1.82] | PASS | 39.647 | +0.07 [-2.44, +1.58] | PASS |
| broad-class-varied-65 | 45.944 | -0.18 [-1.05, +0.28] | PASS | 46.509 | -0.48 [-2.28, +0.25] | PASS |
| broad-wide-ascii | 24.139 | +1.68 [+0.85, +2.47] | PASS | 24.933 | +0.13 [-2.16, +3.87] | INCONCLUSIVE |
| broad-optional-class | 26.550 | -2.41 [-3.29, -1.33] | PASS | 26.868 | -2.55 [-4.15, -0.13] | PASS |
| broad-captured-class | 30.353 | +0.48 [-2.67, +0.81] | PASS | 30.500 | -0.99 [-3.55, +1.45] | PASS |
| broad-tree-literal | 4.183 | -47.12 [-48.16, -45.72] | PASS | 4.154 | -44.98 [-47.36, -42.24] | PASS |
| broad-tree-regex | 7.248 | -24.52 [-26.87, -23.47] | PASS | 7.050 | -24.95 [-25.64, -23.64] | PASS |
| broad-tree-files | 4.099 | -46.37 [-48.16, -43.85] | PASS | 4.044 | -45.75 [-46.84, -42.94] | PASS |
| broad-tree-sorted | 3.828 | -2.27 [-8.82, -1.33] | PASS | 3.932 | -1.19 [-6.10, +2.07] | PASS |
| broad-kernel-default | 117.992 | +0.72 [-1.90, +3.87] | INCONCLUSIVE | 118.464 | -2.68 [-3.67, +0.08] | PASS |
| broad-kernel-c | 92.663 | -4.60 [-6.87, +1.71] | PASS | 93.588 | -2.67 [-6.13, +3.65] | INCONCLUSIVE |
| broad-cold-literal | 15.171 | -0.37 [-8.97, +2.01] | PASS | 23.593 | -5.20 [-8.97, +2.96] | PASS |
| broad-cold-regex | 27.570 | -2.24 [-22.40, +5.34] | INCONCLUSIVE | 28.923 | +4.87 [-0.40, +10.47] | INCONCLUSIVE |
| type-selected | 5.293 | -46.57 [-47.92, -45.17] | PASS | 5.249 | -46.80 [-47.93, -45.33] | PASS |
| type-negated | 3.697 | -36.63 [-38.49, -34.86] | PASS | 3.605 | -35.48 [-38.24, -32.90] | PASS |
| type-custom | 5.328 | -46.82 [-48.93, -45.63] | PASS | 5.467 | -48.61 [-49.93, -46.63] | PASS |
| type-list | 1.201 | -5.14 [-7.53, -2.48] | PASS | 1.232 | -5.62 [-8.78, -3.90] | PASS |

## Measurement checks

Session A: 7,020 timed batches / 53,100 timed invocations. Warm-I/O cases: ['broad-literal-insensitive']. Unstable-control cases: none. Cgroup peak: 0.09 GiB.

```text
low 0
high 0
max 0
oom 0
oom_kill 0
oom_group_kill 0
sock_throttled 0
```

Interference guard: 1,757 checks; watched repositories ['/home/gardnmi/Projects/ttfx', '/home/gardnmi/Worktrees/ttfx']; external-work observations 0.

Session B: 7,020 timed batches / 50,940 timed invocations. Warm-I/O cases: ['type-negated']. Unstable-control cases: none. Cgroup peak: 0.10 GiB.

```text
low 0
high 0
max 0
oom 0
oom_kill 0
oom_group_kill 0
sock_throttled 0
```

Interference guard: 1,757 checks; watched repositories ['/home/gardnmi/Projects/ttfx', '/home/gardnmi/Worktrees/ttfx']; external-work observations 0.
