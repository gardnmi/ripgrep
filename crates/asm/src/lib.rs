//! Opt-in x86-64 assembly experiments. Unsupported hosts use the caller's
//! original implementation. This crate is not intended for publication.

use memchr::{arch::all::packedpair::Pair, memmem};

#[derive(Clone, Copy)]
enum Mode {
    Disabled,
    Assembly,
    Rust,
}

fn mode() -> Mode {
    static MODE: std::sync::OnceLock<Mode> = std::sync::OnceLock::new();
    *MODE.get_or_init(|| match std::env::var("RG_ASM").as_deref() {
        Ok("0") => Mode::Disabled,
        // Benchmark control: identical integration with memchr kernels.
        Ok("rust") => Mode::Rust,
        _ if available() => Mode::Assembly,
        _ => Mode::Disabled,
    })
}

#[cfg(all(target_arch = "x86_64", target_os = "linux"))]
core::arch::global_asm!(include_str!("x86_64.s"), options(raw));

#[cfg(all(target_arch = "x86_64", target_os = "linux"))]
unsafe extern "C" {
    fn rg_asm_count(ptr: *const u8, len: usize, byte: u32) -> usize;
    fn rg_asm_pair(
        ptr: *const u8,
        positions: usize,
        offset1: usize,
        offset2: usize,
        bytes: u32,
    ) -> usize;
}

/// Whether the kernels' instructions and OS vector state are available.
#[inline]
pub fn available() -> bool {
    #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
    {
        std::is_x86_feature_detected!("avx512f")
            && std::is_x86_feature_detected!("avx512bw")
            && std::is_x86_feature_detected!("popcnt")
    }
    #[cfg(not(all(target_arch = "x86_64", target_os = "linux")))]
    {
        false
    }
}

/// Count a byte, or decline when the input is short or the CPU is unsupported.
#[inline]
pub fn count(bytes: &[u8], byte: u8) -> Option<usize> {
    if bytes.len() < 256 {
        return None;
    }
    match mode() {
        Mode::Disabled => return None,
        Mode::Rust => return Some(memchr::memchr_iter(byte, bytes).count()),
        Mode::Assembly => {}
    }
    #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
    // SAFETY: the feature check includes OS support. The kernel reads only
    // the supplied slice, including a masked load for its partial tail.
    unsafe {
        return Some(rg_asm_count(bytes.as_ptr(), bytes.len(), byte.into()));
    }
    #[cfg(not(all(target_arch = "x86_64", target_os = "linux")))]
    {
        let _ = byte;
        None
    }
}

/// Exact single-literal matching with an assembly candidate scan.
#[derive(Clone, Debug)]
pub struct Literal {
    needle: Box<[u8]>,
    fallback: memmem::Finder<'static>,
    #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
    offset1: usize,
    #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
    offset2: usize,
    #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
    bytes: u32,
    use_assembly: bool,
}

impl Literal {
    /// Build a scanner for a literal of 2 through 64 bytes.
    pub fn new(needle: &[u8]) -> Option<Literal> {
        let mode = mode();
        if matches!(mode, Mode::Disabled) || !(2..=64).contains(&needle.len())
        {
            return None;
        }
        // Use the same frequency heuristic as the existing memchr prefilter.
        let pair = Pair::new(needle)?;
        #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
        let (offset1, offset2) =
            (usize::from(pair.index1()), usize::from(pair.index2()));
        #[cfg(not(all(target_arch = "x86_64", target_os = "linux")))]
        let _ = pair;
        Some(Literal {
            needle: needle.into(),
            fallback: memmem::Finder::new(needle).into_owned(),
            #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
            offset1,
            #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
            offset2,
            #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
            bytes: u32::from(needle[offset1])
                | (u32::from(needle[offset2]) << 8),
            use_assembly: matches!(mode, Mode::Assembly),
        })
    }

    /// Length in bytes of the literal.
    pub fn needle_len(&self) -> usize {
        self.needle.len()
    }

    /// Find the first complete match, preserving byte offsets.
    #[inline]
    pub fn find(&self, haystack: &[u8]) -> Option<usize> {
        if haystack.len() < self.needle.len() {
            return None;
        }
        if haystack.len() <= 256 {
            return self.fallback.find(haystack);
        }
        // AVX2 memmem has lower overhead when a match is close. Let it
        // handle the prefix before entering the wide streaming loop. Keep
        // needle.len()-1 bytes of overlap so boundary matches cannot be lost.
        if let Some(at) = self.fallback.find(&haystack[..256]) {
            return Some(at);
        }
        let start = 257 - self.needle.len();
        self.find_large(&haystack[start..]).map(|at| start + at)
    }

    fn find_large(&self, haystack: &[u8]) -> Option<usize> {
        if !self.use_assembly {
            return self.fallback.find(haystack);
        }
        let positions = haystack.len() - self.needle.len() + 1;
        let mut start = 0;
        // Limit verification work on adversarial inputs; memmem supplies its
        // established fallback once this predicate stops being selective.
        for _ in 0..16 {
            if start >= positions {
                return None;
            }
            #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
            let candidate = unsafe {
                // SAFETY: construction checked CPU/OS support. Both offsets
                // are within the needle, so all candidate loads (including
                // the masked tail) lie within haystack.
                rg_asm_pair(
                    haystack.as_ptr().add(start),
                    positions - start,
                    self.offset1,
                    self.offset2,
                    self.bytes,
                )
            };
            #[cfg(not(all(target_arch = "x86_64", target_os = "linux")))]
            let candidate = usize::MAX;
            if candidate == usize::MAX {
                return None;
            }
            let at = start + candidate;
            if &haystack[at..at + self.needle.len()] == &*self.needle {
                return Some(at);
            }
            start = at + 1;
        }
        self.fallback.find(&haystack[start..]).map(|at| start + at)
    }
}

#[cfg(test)]
mod tests;
