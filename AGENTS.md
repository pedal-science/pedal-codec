# pedal-codec

A Raspberry Pi audio board, in the spirit of Raspberry Pi's Codec Zero, built around Texas
Instruments' **TAC5242**: two inputs switchable between Instrument, Line and Mic, each with
optional +48 V phantom power, and two line outputs, all on JST XH connectors (3-pin inputs, 2-pin
outputs), on a full-size HAT+. Power, audio and control come
through the Pi's 40-pin header. Started 2026-11-11 as an aside from the pedal; it may later replace
the pedal's SparkFun WM8960 board, which is a separate decision.

This file is canonical for every agent; `CLAUDE.md` only imports it. The pedal as a system is
`../pedal.project/AGENTS.md`, and `../pedal.project/docs/working-across-repos.md` says which
repository owns what.

## What is here

| Path | What it is |
|---|---|
| `docs/design.md` | The requirements, what the TAC5242 datasheet changes about them, the board's blocks, and the open questions |
| `docs/plan.md` | The phases from requirements to tested boards, each with its done-when, and the tools each uses. Start at "Next session starts with" |
| `sim/` | The ngspice decks for the analogue stages and their results, once written (phase 1) |
| `hardware/` | The KiCad 10 project, once started (phase 2) |
| `overlay/` | The device-tree overlay the HAT+ EEPROM names, once written (phase 5) |
| `bench-results/` | Measurements of built boards, with their dates. Never `/tmp` |

## Rules

- **KiCad files change only through the Konnect MCP tools** (the `konnect` skill), or by the owner
  in KiCad. Never edit `.kicad_sch` or `.kicad_pcb` text by hand: Konnect keeps the files
  consistent and KiCad's IPC session in step.
- **Every part carries an `LCSC` field and an `MPN` field** from the start, so the BOM for JLCPCB
  assembly is a by-product, not a phase. Check stock when a part is chosen and again before
  ordering.
- **Nothing is ordered without the owner's say-so.** Agents prepare the fab package and the quote;
  the owner places the order and pays.
- **Datasheets are linked, not committed.** They are their makers' work. Keep local copies outside
  the repository or in the git-ignored `datasheets/` directory.
- **Phantom power is a safety feature, not a convenience.** +48 V must never reach the
  instrument path: the interlock is in hardware (`docs/design.md`, "Phantom power"), not only in
  software.
- **The HAT+ rules apply** (Raspberry Pi's HAT+ specification): an ID EEPROM on ID_SD/ID_SC with
  3.9 kΩ pull-ups, and nothing powered from 5 V may back-power the 3.3 V side while the Pi is in
  standby (5 V on, 3.3 V off).
- Every repository here is public: `../pedal.project/scripts/public-check` runs on push.
- Commit to `main`; pushes wait for the owner's say-so.

## Licensing

The board (schematic, layout, fab outputs, hardware docs) is CERN-OHL-P-2.0; scripts and the
overlay are MIT. [LICENSING.md](LICENSING.md) has the split.
