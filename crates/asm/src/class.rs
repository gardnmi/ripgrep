//! SIMD recognition of a minimum-length run from an ASCII byte class.

#[derive(Clone, Debug)]
pub struct ClassRun {
    ranges: Vec<(u8, u8)>,
    min: usize,
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
        Some(Self { ranges, min })
    }

    /// End offset of the earliest minimum-length match.
    pub fn shortest(&self, bytes: &[u8]) -> Option<usize> {
        #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
        // SAFETY: construction requires the same AVX-512 checks as the kernels.
        unsafe {
            self.scan(bytes)
        }
        #[cfg(not(all(target_arch = "x86_64", target_os = "linux")))]
        {
            let _ = bytes;
            None
        }
    }

    #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
    #[target_feature(enable = "avx512f,avx512bw")]
    unsafe fn scan(&self, bytes: &[u8]) -> Option<usize> {
        use std::arch::x86_64::*;
        let mut offset = 0;
        let mut carry = 0;
        while offset + 64 <= bytes.len() {
            // SAFETY: the loop condition guarantees a complete readable vector.
            let chars = unsafe {
                _mm512_loadu_si512(bytes.as_ptr().add(offset).cast())
            };
            let mut mask = 0u64;
            for &(lo, hi) in &self.ranges {
                let adjusted =
                    _mm512_sub_epi8(chars, _mm512_set1_epi8(lo as i8));
                mask |= _mm512_cmple_epu8_mask(
                    adjusted,
                    _mm512_set1_epi8((hi - lo) as i8),
                );
            }
            let prefix = mask.trailing_ones() as usize;
            if carry + prefix >= self.min {
                return Some(offset + self.min - carry);
            }
            if self.min <= 64 {
                // Bit i survives precisely when min consecutive bits starting
                // at i are set. Doubling avoids a per-character state machine.
                let mut runs = mask;
                let mut width = 1;
                while width * 2 <= self.min {
                    runs &= runs >> width;
                    width *= 2;
                }
                if width < self.min {
                    runs &= runs >> (self.min - width);
                }
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
            if self.ranges.iter().any(|&(lo, hi)| lo <= byte && byte <= hi) {
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
        ] {
            for min in [1, 2, 3, 15, 30, 31, 32, 33, 63, 64, 65, 127, 128, 129]
            {
                let run = ClassRun { ranges: ranges.clone(), min };
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
