//! SIMD recognition of a minimum-length run from an ASCII byte class.

#[derive(Clone, Debug)]
pub struct ClassRun {
    ranges: [(u8, u8); 4],
    min: usize,
    #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
    scan: unsafe fn(&ClassRun, &[u8]) -> Option<usize>,
}

impl ClassRun {
    pub fn new(ranges: Vec<(u8, u8)>, min: usize) -> Option<Self> {
        if !matches!(super::mode(), super::Mode::Assembly)
            || std::env::var_os("RG_CLASS").is_some_and(|v| v == "0")
            || min == 0
            || ranges.is_empty()
            || ranges.len() > 4
            || ranges.iter().any(|&(lo, hi)| lo > hi || hi >= 128)
        {
            return None;
        }
        Some(Self::from_ranges(&ranges, min))
    }

    fn from_ranges(original: &[(u8, u8)], min: usize) -> Self {
        // Paired intervals in adjacent 32-byte ASCII blocks can share one
        // comparison after OR-ing bit 0x20. Unpaired intervals (notably digits)
        // must still inspect the original bytes: folding digits alone would
        // incorrectly admit control characters 0x10..0x19.
        let mut used = [false; 4];
        let mut folded = [(0, 0); 2];
        let mut folded_count = 0;
        for (i, &(lo, hi)) in original.iter().enumerate() {
            if used[i] || lo & 0x20 != 0 || lo >> 5 != hi >> 5 {
                continue;
            }
            let pair = (lo | 0x20, hi | 0x20);
            if let Some(j) = original.iter().enumerate().find_map(|(j, r)| {
                (i != j && !used[j] && *r == pair).then_some(j)
            }) {
                used[i] = true;
                used[j] = true;
                folded[folded_count] = pair;
                folded_count += 1;
            }
        }
        let mut ranges = [(0, 0); 4];
        let mut plain_count = 0;
        for (i, &range) in original.iter().enumerate() {
            if !used[i] {
                ranges[plain_count] = range;
                plain_count += 1;
            }
        }
        ranges[plain_count..plain_count + folded_count]
            .copy_from_slice(&folded[..folded_count]);
        #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
        let scan = {
            // Fix the range count, folding and intersection depth once per
            // pattern instead of recomputing them for each 64-byte block.
            macro_rules! row {
                ($n:literal, $fold:literal) => {
                    [
                        Self::scan::<$n, $fold, 0>,
                        Self::scan::<$n, $fold, 1>,
                        Self::scan::<$n, $fold, 2>,
                        Self::scan::<$n, $fold, 3>,
                        Self::scan::<$n, $fold, 4>,
                        Self::scan::<$n, $fold, 5>,
                        Self::scan::<$n, $fold, 6>,
                    ]
                };
            }
            type Scan = unsafe fn(&ClassRun, &[u8]) -> Option<usize>;
            let table: [[Scan; 7]; 8] = [
                row!(1, 0),
                row!(2, 0),
                row!(3, 0),
                row!(4, 0),
                row!(1, 1),
                row!(2, 2),
                row!(3, 4),
                row!(2, 3),
            ];
            let group = match (plain_count, folded_count) {
                (n, 0) => n - 1,
                (0, 1) => 4,
                (1, 1) => 5,
                (2, 1) => 6,
                (0, 2) => 7,
                _ => unreachable!("at most four original ranges"),
            };
            table[group][min.ilog2().min(6) as usize]
        };
        Self {
            ranges,
            min,
            #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
            scan,
        }
    }

    /// End offset of the earliest minimum-length match.
    pub fn shortest(&self, bytes: &[u8]) -> Option<usize> {
        if bytes.len() < self.min {
            return None;
        }
        #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
        // SAFETY: construction requires the same AVX-512 checks as the kernels.
        unsafe {
            (self.scan)(self, bytes)
        }
        #[cfg(not(all(target_arch = "x86_64", target_os = "linux")))]
        {
            let _ = bytes;
            None
        }
    }

    #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
    #[target_feature(enable = "avx512f,avx512bw")]
    unsafe fn scan<const N: usize, const FOLD: usize, const STEPS: usize>(
        &self,
        bytes: &[u8],
    ) -> Option<usize> {
        use std::arch::x86_64::*;
        let lows: [__m512i; N] =
            std::array::from_fn(|i| _mm512_set1_epi8(self.ranges[i].0 as i8));
        let spans: [__m512i; N] = std::array::from_fn(|i| {
            _mm512_set1_epi8((self.ranges[i].1 - self.ranges[i].0) as i8)
        });
        let mut offset = 0;
        let mut carry = 0;
        while offset + 64 <= bytes.len() {
            // SAFETY: the loop condition guarantees a complete readable vector.
            let chars = unsafe {
                _mm512_loadu_si512(bytes.as_ptr().add(offset).cast())
            };
            let folded = if FOLD == 0 {
                chars
            } else {
                _mm512_or_si512(chars, _mm512_set1_epi8(0x20))
            };
            let mut mask = 0u64;
            for i in 0..N {
                let input = if FOLD & (1 << i) == 0 { chars } else { folded };
                let adjusted = _mm512_sub_epi8(input, lows[i]);
                mask |= _mm512_cmple_epu8_mask(adjusted, spans[i]);
            }
            let prefix = mask.trailing_ones() as usize;
            if carry + prefix >= self.min {
                return Some(offset + self.min - carry);
            }
            // Runs of at least 64 bytes are caught by the prefix/carry check.
            if STEPS < 6 {
                // Bit i survives precisely when min consecutive bits starting
                // at i are set. Doubling avoids a per-character state machine.
                let mut runs = mask;
                for step in 0..STEPS {
                    runs &= runs >> (1 << step);
                }
                runs &= runs >> (self.min - (1 << STEPS));
                if runs != 0 {
                    return Some(
                        offset + runs.trailing_zeros() as usize + self.min,
                    );
                }
            }
            carry = if mask == u64::MAX {
                carry + 64
            } else {
                mask.leading_ones() as usize
            };
            offset += 64;
        }
        for (i, &byte) in bytes[offset..].iter().enumerate() {
            if (0..N).any(|r| {
                let b = if FOLD & (1 << r) == 0 { byte } else { byte | 0x20 };
                let (lo, hi) = self.ranges[r];
                lo <= b && b <= hi
            }) {
                carry += 1;
                if carry >= self.min {
                    return Some(offset + i + 1);
                }
            } else {
                carry = 0;
            }
        }
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn runs_against_scalar() {
        if !super::super::available() {
            return;
        }
        let mut state = 6193u64;
        for ranges in [
            vec![(b'A', b'Z'), (b'a', b'z')],
            vec![(b'0', b'9')],
            vec![(0, 127)],
            vec![(b'0', b'9'), (b'A', b'F'), (b'a', b'f')],
            vec![(b'A', b'Z'), (b'_', b'_'), (b'a', b'z')],
            vec![(b'a', b'f'), (b'A', b'F'), (b'0', b'9'), (b'_', b'_')],
            vec![(b'A', b'F'), (b'P', b'Z'), (b'a', b'f'), (b'p', b'z')],
            vec![(1, 2), (8, 9), (65, 67), (100, 106)],
            vec![(0, 80), (32, 112)],
        ] {
            for min in [1, 2, 3, 15, 30, 31, 32, 33, 63, 64, 65, 127, 128, 129]
            {
                let run = ClassRun::from_ranges(&ranges, min);
                for len in [0, 1, 63, 64, 65, 127, 128, 129, 511, 1024] {
                    for trial in 0..20 {
                        let bytes: Vec<_> = (0..len)
                            .map(|i| {
                                state ^= state << 13;
                                state ^= state >> 7;
                                state ^= state << 17;
                                if trial < 10 && i % (min + 7) < min + trial {
                                    ranges[0].0
                                } else {
                                    state as u8
                                }
                            })
                            .collect();
                        let expected = bytes
                            .windows(min)
                            .position(|w| {
                                w.iter().all(|b| {
                                    ranges
                                        .iter()
                                        .any(|(lo, hi)| lo <= b && b <= hi)
                                })
                            })
                            .map(|i| i + min);
                        assert_eq!(
                            run.shortest(&bytes),
                            expected,
                            "min={min} len={len} trial={trial}"
                        );
                    }
                }
            }
        }
    }
}
