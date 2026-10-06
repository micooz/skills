#!/usr/bin/env python3
"""Create a video-only MIDI with small gaps between back-to-back notes.

Transcriptions often end each note exactly where the next note on the same
channel starts, so consecutive notes look fused in NoteFall's waterfall.
This shortens every note tail by --gap seconds (never below --min-length)
while keeping onsets and total duration unchanged. The canonical .mid for
score/marketplace delivery is left untouched; only the video MIDI changes.

Run it in place (omit DST) right after the Songscription MIDI download so the
track directory keeps a single gap-processed `.mid` for NoteFall and any
fallback conversion.

Usage:
    uv run --no-project --with mido python midi_note_gap.py IN.mid [OUT.mid]
"""
import argparse
from bisect import bisect_right

import mido


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src")
    ap.add_argument("dst", nargs="?", default=None,
                    help="output path; defaults to in-place (same as src)")
    ap.add_argument("--gap", type=float, default=0.05,
                    help="seconds removed from each note tail (default 0.05)")
    ap.add_argument("--min-length", type=float, default=0.08,
                    help="shortest allowed note length in seconds (default 0.08)")
    args = ap.parse_args()
    dst = args.dst or args.src

    mid = mido.MidiFile(args.src)
    tpb = mid.ticks_per_beat

    # global tempo map (tick -> tempo) across all tracks
    tc = [(0, 500000)]
    for tr in mid.tracks:
        t = 0
        for m in tr:
            t += m.time
            if m.type == "set_tempo":
                tc.append((t, m.tempo))
    tc.sort(key=lambda x: x[0])
    ticks = [a for a, _ in tc]
    tempos = [b for _, b in tc]

    def sec_at(tick):
        i = bisect_right(ticks, tick) - 1
        s = 0.0
        cur = ticks[0]
        tempo = tempos[0]
        for j in range(1, len(ticks)):
            if ticks[j] >= tick:
                break
            s += (ticks[j] - cur) * (tempo / 1e6) / tpb
            cur = ticks[j]
            tempo = tempos[j]
        s += (tick - cur) * (tempo / 1e6) / tpb
        return s

    def sec_per_tick(tick):
        i = bisect_right(ticks, tick) - 1
        return (tempos[i] / 1e6) / tpb

    shortened = total = 0
    for tr in mid.tracks:
        evs = []  # [tick, original order, msg]
        t = 0
        for i, m in enumerate(tr):
            t += m.time
            evs.append([t, i, m])
        open_notes = {}
        for ev in evs:
            tick, _, m = ev
            key = (getattr(m, "channel", 0), getattr(m, "note", None))
            if m.type == "note_on" and m.velocity > 0:
                open_notes[key] = (tick, sec_at(tick))
            elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
                st = open_notes.pop(key, None)
                if st:
                    start_tick, start_sec = st
                    dur = sec_at(tick) - start_sec
                    new_dur = max(args.min_length, dur - args.gap)
                    if new_dur < dur - 1e-6:
                        d_tick = int(round((dur - new_dur) / sec_per_tick(tick)))
                        ev[0] = max(start_tick + 1, tick - d_tick)
                        shortened += 1
                    total += 1
        # stable reorder: keep original order for events sharing a tick
        evs.sort(key=lambda e: (e[0], e[1]))
        prev = 0
        out = []
        for tick, _, m in evs:
            m2 = m.copy()
            m2.time = tick - prev
            prev = tick
            out.append(m2)
        tr[:] = out

    mid.save(dst)
    print(f"shortened {shortened} of {total} notes; saved {dst}")


if __name__ == "__main__":
    main()
