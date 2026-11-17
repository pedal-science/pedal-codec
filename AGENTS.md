# pedal-codec

A Raspberry Pi audio board, in the spirit of Raspberry Pi's Codec Zero, built around Texas
Instruments' **TAC5212** (I2C-controlled): two inputs for combo XLR/¼″ jacks (Instrument or Line on
the ¼″, Mic or Line on the XLR, chosen by the plug and a panel switch), each with optional +48 V
phantom power from a panel switch, and two line outputs, each both unbalanced and balanced (for
XLR), all on JST XH connectors, on a full-size HAT+. Power, audio and control come through the Pi's
40-pin header. Started 2026-11-11 as an aside from the pedal; it may later replace the pedal's
SparkFun WM8960 board, which is a separate decision.

This file is canonical for every agent; `CLAUDE.md` only imports it. The pedal as a system is
`../pedal.project/AGENTS.md`, and `../pedal.project/docs/working-across-repos.md` says which
repository owns what.

## What is here

| Path | What it is |
|---|---|
| `../pedal.project/docs/box-design.md` | **The current target**, agreed 2026-11-14: the 1590DD pedal designed to be made again, as an audio board, a Pi board and a control board |
| `docs/box-board.md` | The audio board's part of that design: what is on it, how its schematic came from the phase 2 sheets, what was decided while drawing it, what is open |
| `docs/pi-board.md`, `docs/control-board.md` | The same for the Pi board (USB-C power, the ID EEPROM, the RP2350, MIDI, the footswitches' plugs, the fan's plug) and the control board (the encoder, the two buttons and their lamps) |
| `docs/design.md` | The requirements, the codec (TAC5212) and what its datasheet means for the board, the board's blocks, and the open questions |
| `docs/plan.md` | The phases from requirements to tested boards, each with its done-when, and the tools each uses. Start at "Next session starts with" |
| `sim/` | The ngspice decks for the analogue stages and their results (phase 1); `sim/box/` holds the ones written for the audio board |
| `hardware/` | The phase 2 KiCad 10 project: the full-size HAT's approved schematic, kept as the source of every shared circuit |
| `hardware/audio-board/` | The box's audio board: its own KiCad 10 project and the PDF of its schematic |
| `hardware/pi-board/`, `hardware/control-board/` | The box's Pi board and control board, the same way |
| `hardware/pedal-codec.kicad_sym`, `hardware/pedal-codec.pretty/` | The symbols and footprints of our own, which every project here uses; each footprint's description names the maker's drawing it came from |
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
- **Phantom power is under the player's hand only.** It is wired to the XLR pins and nothing else,
  it is switched on by a panel switch and nothing else, and no GPIO, script or default may enable
  it (`docs/design.md`, "Phantom power"). Software may read it, never set it.
- **The HAT+ rules apply** (Raspberry Pi's HAT+ specification): an ID EEPROM on ID_SD/ID_SC with
  3.9 kΩ pull-ups, and nothing powered from 5 V may back-power the 3.3 V side while the Pi is in
  standby (5 V on, 3.3 V off).
- Every repository here is public: `../pedal.project/scripts/public-check` runs on push.
- Commit to `main`; pushes wait for the owner's say-so.

## Licensing

The board (schematic, layout, fab outputs, hardware docs) is CERN-OHL-P-2.0; scripts and the
overlay are MIT. [LICENSING.md](LICENSING.md) has the split.
