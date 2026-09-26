//! Opt-in, bounded single-file parallel experiment for this machine.
//! Unsupported command shapes use the ordinary ripgrep implementation.
use crate::{flags::HiArgs, search::PatternMatcher};
use grep::searcher::{Searcher, SearcherBuilder, Sink, SinkMatch};
use std::{
    fs::File,
    io::{self, IsTerminal, Write},
    path::PathBuf,
    sync::mpsc,
    thread,
};

#[derive(Default)]
struct Matches(Vec<(usize, usize, u64)>);

impl Sink for Matches {
    type Error = io::Error;
    fn matched(
        &mut self,
        _: &Searcher,
        mat: &SinkMatch<'_>,
    ) -> io::Result<bool> {
        self.0.push((
            mat.absolute_byte_offset() as usize,
            mat.bytes().len(),
            mat.line_number().unwrap_or(0),
        ));
        Ok(true)
    }
}

/// Conservatively recognize a small CLI subset. Requiring --no-config prevents
/// configuration files from silently adding options this prototype bypasses.
fn options() -> Option<(PathBuf, bool)> {
    let mut positional = Vec::new();
    let mut numbers = false;
    let mut no_config = false;
    let mut flags = true;
    for arg in std::env::args_os().skip(1) {
        if flags && arg == "--" {
            flags = false;
            continue;
        }
        if flags && arg.as_encoded_bytes().starts_with(b"-") {
            match arg.to_str()? {
                "--no-config" => no_config = true,
                "-n" | "--line-number" => numbers = true,
                "-N" | "--no-line-number" => numbers = false,
                "-w" | "--word-regexp" | "-F" | "--fixed-strings" | "-i"
                | "--ignore-case" | "-s" | "--case-sensitive" | "-S"
                | "--smart-case" | "--color=never" | "--no-heading"
                | "--no-filename" => {}
                _ => return None,
            }
        } else {
            positional.push(arg);
        }
    }
    if !no_config || positional.len() != 2 || positional[1] == "-" {
        return None;
    }
    Some((PathBuf::from(&positional[1]), numbers))
}

pub(crate) fn try_parallel(args: &HiArgs) -> anyhow::Result<Option<bool>> {
    let workers = std::env::var("RG_PARALLEL")
        .ok()
        .and_then(|v| v.parse::<usize>().ok())
        .unwrap_or(0);
    if !(2..=6).contains(&workers) || io::stdout().is_terminal() {
        return Ok(None);
    }
    let Some((path, numbers)) = options() else {
        return Ok(None);
    };
    let matcher = match args.matcher()? {
        PatternMatcher::RustRegex(m) if m.parallel_safe() => m,
        _ => return Ok(None),
    };
    // Let upstream handle path errors, devices, small inputs and diagnostics.
    let Ok(file) = File::open(&path) else {
        return Ok(None);
    };
    let meta = file.metadata()?;
    if !meta.is_file() || meta.len() < 8 * 1024 * 1024 {
        return Ok(None);
    }
    // SAFETY: same file-mapping assumption as ripgrep's existing mmap path:
    // the caller must not concurrently truncate/mutate the mapped file.
    let map = unsafe { memmap2::Mmap::map(&file)? };
    if map.starts_with(b"\xff\xfe")
        || map.starts_with(b"\xfe\xff")
        || memchr::memchr(0, &map).is_some()
    {
        return Ok(None);
    }
    let bytes =
        if map.starts_with(b"\xef\xbb\xbf") { &map[3..] } else { &map[..] };
    let mut chunks = Vec::new();
    let mut start = 0;
    while start < bytes.len() {
        let target = (start + 1024 * 1024).min(bytes.len());
        let end = if target == bytes.len() {
            target
        } else {
            // Bound the largest chunk, including an unusually long line.
            let limit = (target + 16 * 1024 * 1024).min(bytes.len());
            let Some(n) = memchr::memchr(b'\n', &bytes[target..limit]) else {
                return Ok(None);
            };
            target + n + 1
        };
        chunks.push((start, end));
        start = end;
    }
    log::debug!(
        "machine parallel: {workers} workers, {} chunks",
        chunks.len()
    );
    let found = thread::scope(|scope| -> io::Result<bool> {
        let mut receivers = Vec::new();
        for worker in 0..workers {
            let (tx, rx) = mpsc::sync_channel(1);
            receivers.push(rx);
            let matcher = matcher.clone();
            let chunks = &chunks;
            scope.spawn(move || {
                let mut searcher = SearcherBuilder::new()
                    .line_number(numbers)
                    .bom_sniffing(false)
                    .build();
                for index in (worker..chunks.len()).step_by(workers) {
                    let (start, end) = chunks[index];
                    let chunk = &bytes[start..end];
                    let mut matches = Matches::default();
                    let result = searcher
                        .search_slice(&matcher, chunk, &mut matches)
                        .map(|()| {
                            let lines = if numbers {
                                memchr::memchr_iter(b'\n', chunk).count()
                                    as u64
                            } else {
                                0
                            };
                            (matches, lines)
                        });
                    let failed = result.is_err();
                    if tx.send(result).is_err() || failed {
                        break;
                    }
                }
            });
        }
        // Always drop receivers before scoped threads are joined, including
        // broken pipes and other output errors, so blocked producers can exit.
        let result = (|| {
            let stdout = io::stdout();
            let mut out =
                io::BufWriter::with_capacity(64 * 1024, stdout.lock());
            let mut line_base = 0;
            let mut found = false;
            for (index, &(start, _)) in chunks.iter().enumerate() {
                let (matches, lines) =
                    receivers[index % workers].recv().map_err(|_| {
                        io::Error::other("parallel worker stopped")
                    })??;
                found |= !matches.0.is_empty();
                for (offset, len, line) in matches.0 {
                    if numbers {
                        write!(out, "{}:", line_base + line)?;
                    }
                    let text = &bytes[start + offset..start + offset + len];
                    out.write_all(text)?;
                    if !text.ends_with(b"\n") {
                        out.write_all(b"\n")?;
                    }
                }
                line_base += lines;
            }
            out.flush()?;
            Ok(found)
        })();
        drop(receivers);
        result
    })?;
    Ok(Some(found))
}
