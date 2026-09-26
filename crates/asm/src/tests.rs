use super::*;

#[cfg(all(target_arch = "x86_64", target_os = "linux"))]
#[test]
fn fused_matches_and_counts() {
    if !available() {
        return;
    }
    let mut seed = 971u64;
    for len in [2, 3, 15, 31, 63, 64] {
        let needle: Vec<_> = (0..len).map(|i| b'A' + (i % 26) as u8).collect();
        let finder = Literal::new(&needle).unwrap();
        for trial in 0..500 {
            let mut bytes: Vec<_> = (0..(256 + trial * 7))
                .map(|_| {
                    seed ^= seed << 13;
                    seed ^= seed >> 7;
                    seed ^= seed << 17;
                    if seed % 4 == 0 { b'\n' } else { seed as u8 }
                })
                .collect();
            if trial % 2 == 0 {
                let at = seed as usize % (bytes.len() - len + 1);
                bytes[at..at + len].copy_from_slice(&needle);
            }
            let at = memmem::find(&bytes, &needle);
            let count = bytes[..at.unwrap_or(bytes.len())]
                .iter()
                .filter(|&&b| b == b'\n')
                .count() as u64;
            assert_eq!(
                unsafe { finder.scan_counted(&bytes, b'\n') },
                (at, count)
            );
        }
        let finder = Literal::new(&vec![b'a'; len]).unwrap();
        let mut bytes =
            [vec![b'a'; len - 1], vec![b'\n']].concat().repeat(1000);
        bytes.extend(vec![b'a'; len]);
        let at = memmem::find(&bytes, &vec![b'a'; len]);
        assert_eq!(unsafe { finder.scan_counted(&bytes, b'\n') }, (at, 1000));
    }
}

#[test]
fn counts_match_for_all_bytes_alignments_and_tails() {
    if !available() {
        return;
    }
    let mut data = vec![0; 2048 + 64];
    for (i, b) in data.iter_mut().enumerate() {
        *b = ((i * 137 + i / 7) & 255) as u8;
    }
    for offset in 0..64 {
        for len in [
            0, 1, 31, 32, 63, 64, 65, 127, 128, 255, 256, 257, 511, 512, 1023,
            2048,
        ] {
            let hay = &data[offset..offset + len];
            for byte in 0..=255u8 {
                let want = hay.iter().filter(|&&b| b == byte).count();
                #[cfg(all(target_arch = "x86_64", target_os = "linux"))]
                assert_eq!(
                    unsafe {
                        rg_asm_count(hay.as_ptr(), hay.len(), byte.into())
                    },
                    want,
                    "offset={offset} len={len} byte={byte}"
                );
                if let Some(got) = count(hay, byte) {
                    assert_eq!(got, want);
                }
            }
        }
    }
}

#[test]
fn literals_match_scalar_across_boundaries() {
    if !available() {
        return;
    }
    let mut state = 0x1234_5678_9abc_def0u64;
    for trial in 0..12000 {
        let needle_len = 2 + trial % 63;
        let hay_len = trial % 1537;
        let mut hay = vec![0; hay_len];
        let mut needle = vec![0; needle_len];
        for b in hay.iter_mut().chain(needle.iter_mut()) {
            state ^= state << 13;
            state ^= state >> 7;
            state ^= state << 17;
            *b = if trial % 3 == 0 { state as u8 & 3 } else { state as u8 };
        }
        if hay_len >= needle_len && trial % 2 == 0 {
            let at = (state as usize) % (hay_len - needle_len + 1);
            hay[at..at + needle_len].copy_from_slice(&needle);
        }
        let searcher = Literal::new(&needle).unwrap();
        let want = hay.windows(needle_len).position(|s| s == needle);
        assert_eq!(searcher.find(&hay), want, "trial={trial}");
    }
}

#[test]
fn adversarial_verification_falls_back_without_skipping() {
    if !available() {
        return;
    }
    let needle = vec![b'a'; 64];
    let searcher = Literal::new(&needle).unwrap();
    let mut hay = [vec![b'a'; 63], vec![b'b']].concat().repeat(512);
    assert_eq!(searcher.find(&hay), None);
    let at = hay.len();
    hay.extend_from_slice(&needle);
    assert_eq!(searcher.find(&hay), Some(at));
}

#[cfg(all(target_arch = "x86_64", target_os = "linux"))]
#[test]
fn masked_tails_do_not_access_guard_pages() {
    if !available() {
        return;
    }
    unsafe {
        let page = libc::sysconf(libc::_SC_PAGESIZE) as usize;
        let base = libc::mmap(
            std::ptr::null_mut(),
            3 * page,
            libc::PROT_NONE,
            libc::MAP_PRIVATE | libc::MAP_ANONYMOUS,
            -1,
            0,
        );
        assert_ne!(base, libc::MAP_FAILED);
        let data = base.cast::<u8>().add(page);
        assert_eq!(
            libc::mprotect(
                data.cast(),
                page,
                libc::PROT_READ | libc::PROT_WRITE
            ),
            0
        );
        for len in 0..=512 {
            for at_end in [false, true] {
                let ptr = if at_end { data.add(page - len) } else { data };
                let hay = std::slice::from_raw_parts_mut(ptr, len);
                hay.fill(0);
                assert_eq!(rg_asm_count(ptr, len, 0), len);
                assert_eq!(rg_asm_count(ptr, len, 1), 0);
                for min in [1, 2, 30, 64, 65, 129] {
                    let run = ClassRun::new(vec![(0, 1)], min).unwrap();
                    assert_eq!(run.shortest(hay), (len >= min).then_some(min));
                }
                for nlen in [2, 3, 16, 63, 64] {
                    if len < nlen {
                        continue;
                    }
                    let positions = len - nlen + 1;
                    assert_eq!(rg_asm_pair(ptr, positions, 0, nlen - 1, 0), 0);
                    assert_eq!(
                        rg_asm_pair(ptr, positions, nlen - 1, 0, 0x0101),
                        usize::MAX
                    );
                    let needle = vec![1; nlen];
                    let scanner = Literal::new(&needle).unwrap();
                    assert_eq!(scanner.find(hay), None);
                    assert_eq!(
                        scanner.scan_counted(hay, 0),
                        (None, len as u64)
                    );
                    hay[len - nlen..].fill(1);
                    assert_eq!(scanner.find(hay), Some(len - nlen));
                    assert_eq!(
                        scanner.scan_counted(hay, 0),
                        (Some(len - nlen), (len - nlen) as u64)
                    );
                    hay.fill(0);
                }
            }
        }
        assert_eq!(libc::munmap(base, 3 * page), 0);
    }
}
