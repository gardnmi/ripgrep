# CPU time per invocation

Sum of child user and system CPU time, divided by batch repetitions.
Baseline controls are averaged within each paired round before taking the median.
CPU time can exceed wall time when multiple workers run simultaneously.
Positive changes mean more CPU use; a wall-time speedup is not an energy claim.

| Workload | A system CPU ms | A candidate CPU ms | A change | B system CPU ms | B candidate CPU ms | B change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| source-literal | 5.136 | 6.345 | +23.54% | 5.061 | 6.382 | +26.10% |
| source-absent | 4.757 | 5.923 | +24.51% | 4.654 | 5.965 | +28.17% |
| source-regex | 10.558 | 11.305 | +7.08% | 10.422 | 11.343 | +8.84% |
| source-ignore-case | 5.498 | 6.848 | +24.54% | 5.674 | 6.985 | +23.12% |
| source-glob | 3.866 | 5.053 | +30.72% | 3.981 | 5.151 | +29.41% |
| source-files | 3.231 | 4.166 | +28.94% | 3.269 | 4.192 | +28.25% |
| source-files-hidden | 3.264 | 4.265 | +30.66% | 3.288 | 4.283 | +30.26% |
| source-multi | 4.896 | 6.277 | +28.21% | 5.028 | 6.362 | +26.53% |
| source-context | 5.197 | 6.499 | +25.05% | 5.372 | 6.621 | +23.26% |
| source-sorted | 4.014 | 3.941 | -1.83% | 4.067 | 4.037 | -0.74% |
| source-explicit-one-thread | 4.006 | 3.928 | -1.94% | 4.020 | 3.987 | -0.82% |
| tools-literal | 75.727 | 73.641 | -2.76% | 76.411 | 74.463 | -2.55% |
| tools-files-with-match | 76.117 | 74.433 | -2.21% | 76.016 | 74.259 | -2.31% |
| tools-glob | 40.839 | 40.296 | -1.33% | 41.523 | 41.139 | -0.92% |
| tools-regex | 78.052 | 76.281 | -2.27% | 78.917 | 76.702 | -2.81% |
| tools-files | 33.815 | 32.862 | -2.82% | 33.816 | 32.785 | -3.05% |
| kernel-literal | 918.006 | 897.212 | -2.27% | 909.530 | 883.290 | -2.89% |
| kernel-regex | 920.340 | 892.816 | -2.99% | 910.367 | 885.936 | -2.68% |
| kernel-files | 232.770 | 216.183 | -7.13% | 232.224 | 214.897 | -7.46% |
| tiny-hit | 1.227 | 1.261 | +2.78% | 1.248 | 1.339 | +7.35% |
| tiny-miss | 1.226 | 1.264 | +3.05% | 1.251 | 1.350 | +7.90% |
| small-regex | 2.041 | 2.010 | -1.54% | 2.070 | 2.096 | +1.26% |
| log-lines | 3.972 | 3.904 | -1.71% | 3.963 | 3.983 | +0.52% |
| log-context | 3.375 | 3.319 | -1.65% | 3.425 | 3.430 | +0.15% |
| log-count | 7.594 | 7.444 | -1.97% | 7.575 | 7.502 | -0.97% |
| log-multi | 10.368 | 10.242 | -1.22% | 10.395 | 10.363 | -0.30% |
| log-ignore-case | 31.317 | 29.199 | -6.76% | 31.362 | 29.381 | -6.32% |
| log-json | 1.254 | 1.294 | +3.22% | 1.264 | 1.364 | +7.91% |
| prose-absent | 11.140 | 11.287 | +1.32% | 11.770 | 11.564 | -1.75% |
| prose-count | 50.208 | 49.860 | -0.69% | 50.738 | 50.346 | -0.77% |
| prose-regex | 15.494 | 15.340 | -0.99% | 16.124 | 15.862 | -1.62% |
| unicode-fold | 14.730 | 14.837 | +0.72% | 14.798 | 14.928 | +0.88% |
