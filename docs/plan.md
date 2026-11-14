# pedal-codec: plan

From requirements to tested boards. Each phase has a done-when; the owner reviews the result of
each phase before the next starts (a demo of what was built, as for the pedal's milestones).

## Next session starts with

1. **The owner takes the measurements** [box-board.md](box-board.md) lists, in the case, with
   the new footswitches fitted. The questions are all answered (box-board.md, "Decided").
2. Then phase 3: the fit, drawn in `pedal.project`'s case layout.
3. Meanwhile, nothing waiting on the case: the parts phase 4 adds (the RP2350, its flash, crystal
   and regulator, the optocoupler, the box header, the combo socket's footprint, the 3.5 mm and
   ¼″ TRS sockets for the case), chosen with LCSC stock.

Last changed 2026-11-14: **the target changed to a board for the 1590DD box** (the owner, after
running the pedal in that case the same day), specified in [box-board.md](box-board.md), and
its eight questions answered by the owner the same day: a combo mic socket, no phantom, bypass
at rest, a switching guitar jack, the RP2350 as a chip, one case bond, MIDI on 3.5 mm TRS, and
the encoder (KY-040) and button chosen. Phases 3
onward are rewritten for it. The full-size HAT's phase 2 schematic, reviewed and redrawn as a
circuit (`a67618f`, pushed), is the source its sheets are cut from. Before that, 2026-11-14:
phase 2's schematic, seven sheets in KiCad 10, every symbol with `LCSC` and `MPN`, ERC clean, the
kicad-happy analysis and its ngspice run triaged. 2026-11-11: phase 1 (the TAC5212 brought up from
userspace over I2C, every part with its LCSC number and stock, ngspice for each mode, the supply
rejection and the phantom thump and faults).

## Tools

Everything runs from a session opened on the workspace, `~/code.local/pedal/`.

| Tool | What it does here |
|---|---|
| KiCad 10 (`/Applications/KiCad`, `kicad-cli`) | The design files. The owner can open them at any point |
| Konnect MCP (`mcp__konnect__*`, the `konnect` skill) | Every change to the schematic and PCB, through KiCad's IPC: symbols, wiring, hierarchy, ERC, placement, routing, DRC, exports. Its `integration` toolset searches the JLCPCB parts database; `manufacturing` builds and checks the fab package and estimates cost |
| `kicad-schematic-build-agent` | Builds a block (an LDO, the boost, an input channel) from a reference circuit, with the values from phase 1 |
| `kicad-design-review-agent`, `kicad-review` skill | A full review before each fab order |
| kicad-happy skills | `kicad` (analysis, DFM against JLCPCB's rules), `spice` (ngspice, installed), `emc` (pre-compliance), `lcsc`, `digikey`, `mouser` (parts, stock, datasheets), `bom`, `jlcpcb` and `pcbway` (fab rules, ordering) |
| `../pedal.project/scripts/codec-noise.py` | The noise-floor analysis already used for the WM8960, for phase 6 |

## Phase 1: decisions and numbers

- Find the state of the `tac5x1x` driver upstream (merged, and in which kernel) and whether TI's
  out-of-tree driver builds against rtpi's kernel, so phase 5 isn't the first time anyone tries.
- Choose each active part with an LCSC number and stock (the `lcsc` skill, Konnect's JLCPCB search):
  AVDD LDO, the analogue rail's load switch and filter, the phantom boost and its post-regulator,
  the JFET op-amp, the mic preamp's op-amp, the FDA, the output op-amps (the unbalanced stage, and
  the balanced followers: a dual per output), the relays (latching or not) and their drivers, the
  pad's analogue switch, the EEPROM, the oscillator, and the combo jack: one whose ¼″ switching
  contact is isolated from the tip, and the panel's switches and LEDs. Prefer JLCPCB "basic" parts
  for passives.
- Simulate in ngspice (the `spice` skill), with models from the makers where they exist:
  - each input mode (Instrument, Line, Mic): gain, headroom against the 5 V rail and the codec's
    +8.2 dBu, noise referred to the input, frequency response with the 5 kΩ input and the coupling
    capacitors;
  - the Mic path's total noise against the codec's floor, to fix its gain (about 20 dB) and choose
    the preamp's op-amp;
  - the Pi's 5 V ripple and load steps through the filter and the mid-rail reference to the codec;
  - the phantom network: the 48 V ramp, the thump at the connector, the protection with a shorted
    XLR;
  - the output stages: level, the mute's click, stability into a cable's capacitance;
  - the balanced outputs' phantom survival, starting from the pedal's
    `../pedal.project/schematic/balanced-output-sim.py` with this board's 5 V rail and its
    capacitance under the clamps: phantom switched on, a charged pin shorted, a hot plug.
- **Done (2026-11-11), waiting for the owner's review.** The driver: none anywhere yet, so v1
  configures the codec from userspace (design.md, "Linux"). The parts, values and results:
  design.md, "Phase 1 values"; the decks: `sim/`.
- **Done when** `docs/design.md` has every value with its reason, no "Open" left that blocks the
  schematic, and the SPICE decks and their results are committed under `sim/`.

## Phase 2: schematic

- A KiCad 10 project in `hardware/`, hierarchical: header and EEPROM, power, phantom supply, codec
  and its I2C address and clock options, input channel (one sheet used twice: both halves of the jack, KA and KB, the panel
  logic), output channel (one sheet used twice: the mute, the unbalanced stage, the balanced
  followers and their protection), the panel connector and v1's on-board switches.
- `LCSC` and `MPN` fields on every symbol from the start; footprints chosen for JLCPCB assembly
  (0402 or 0603 passives, the codec's VQFN-24 with its thermal pad).
- Test points on every rail, BCLK, FSYNC, both data lines, MD0–MD5, the phantom rail and each
  stage's output.
- ERC clean; a design review (`kicad-design-review-agent`) and the kicad-happy analysis (power
  tree, regulators, decoupling) with every finding answered.
- **Done when** the owner has reviewed the schematic as a PDF export.
- **Status (2026-11-14):** done but for the owner's review. `hardware/pedal-codec.pdf` is the export,
  [schematic-review.md](schematic-review.md) the review. The independent `kicad-design-review-agent`
  pass moves to phase 3, where it can see the layout too.

## Phase 3: the fit

The box board's outline, found in the case before anything is drawn in KiCad.

- The owner's measurements (box-board.md, "Measurements needed").
- `../pedal.project/enclosure/src/medium_layout.py` gains the rotary controller, the button, the
  new footswitches' depth, the USB-C, the board's outline with its pillar notches and any cut-outs,
  the ribbon's path from the Pi's header, the standoffs, and, if they fit, the mic, MIDI and
  EXT FS sockets. Its section view gains the heights: the floor, standoffs, board, the tallest
  parts, the footswitches. That is a `pedal.project` change, committed there.
- An area budget: the blocks the board keeps (box-board.md, "What is reused"), each with a
  footprint estimate from the phase 2 parts, against the outline. If it doesn't fit, the order of
  retreat is: the right-hand extension (R3), parts on both sides, then the controls off the board.
- A 1:1 print of the outline, cut from card and tried in the case by the owner with the Pi,
  screen, footswitches, encoder and button fitted.
- **Done when** the owner has tried the card in the case and the outline, the connector
  positions and the height limits are written into box-board.md.

## Phase 4: schematic for the box

- In `hardware/`, through Konnect: the phase 2 project cut down to the box board, sheet by sheet
  as box-board.md's table says. One input sheet for the guitar path and one for the mic path,
  one output sheet for both channels with the one relay, a controls sheet (the
  RP2350 with its flash, crystal and supply; FS1–FS3, EXT FS, MIDI, encoder, button, the Pi's
  reset and SWD lines), the box header for the ribbon, and no phantom. Drawn as
  circuits from the start, as the redraw left them.
- Every new part with `LCSC` and `MPN` and stock checked (the optocoupler, the box header, the
  RP2350 and its parts, the extra XH sizes).
- ngspice for what changed: the right channel into a short (R9), the bypass relay's switching
  transient (the bypass), and the MIDI input's opto at 31 250 baud.
- The header's pin map rewritten (design.md, "Header use"), with the UART, SWD and reset lines
  added; and the RP2350's pin map, which `../pedal.project/firmware/` will follow.
- ERC clean, netlist reviewed, the kicad-happy analysis triaged, as in phase 2.
- **Done when** the owner has reviewed the schematic as a PDF.

## Phase 5: layout

- The outline from phase 3; standoff holes for the base plate; the box header at the end nearest
  the Pi; the XH connectors on the board's edges, each placed for its wire's shortest clean run
  (R18–R20); the height limit as a keep-out under the footswitches.
- **4 layers**: signal, unbroken ground, power, signal. The 1 MΩ node short and guarded; the
  analogue end free of digital traces on every layer; the RP2350 and its crystal at the
  far end from the inputs.
- DRC against JLCPCB's 4-layer rules; the `emc` skill's check; the independent
  `kicad-design-review-agent` pass, now that it can see the layout; a STEP export set into the
  case model to check heights and the ribbon's path.
- **Done when** DRC is clean and the owner has reviewed the plots and the 3D view in the case.

## Phase 6: order

- The fab package (Konnect `manufacturing`, or the `bom` and `jlcpcb` skills): Gerbers, drill,
  BOM with LCSC numbers, placement file, KiCad's DNP attribute set on every unfitted part.
- JLCPCB, 4-layer, 5 boards, assembled on the top side; the box header and XH connectors by
  JLCPCB or by hand. Also the ribbon (40-way,
  2.54 mm, the length phase 3 measured) and the standoffs.
- **Done when** the owner has the quote and has placed the order. Agents never place it.

## Phase 7: bring-up

On piv, the bench device, first, then in the box on vip.

- Power before the Pi: rails on a bench supply, nothing warm; the Pi's standby (5 V on, 3.3 V
  off) back-powers nothing, the RP2350 included.
- EEPROM written (`eepmake`, `eepflash.sh`); the codec at 0x50, configured from userspace
  (design.md, "Linux", route 2); the overlay in `overlay/`; playback, capture, loopback.
- The RP2350 programmed from the Pi over SWD; the Pico firmware ported to the board's pin map in
  `../pedal.project/firmware/`; the footswitches, EXT FS, encoder, button and MIDI each producing
  their UART messages.
- In the box, on vip: the pedal's own changes land in `pedal.project` and `rtpi` (the codec, its
  overlay and clocking replace the WM8960's), in dependency order, as the pedal's working rules
  say. They are decided with the owner then, not before.
- **Done when** the pedal plays through the board in the box, with every control working.

## Phase 8: measure in the box

Evidence into `bench-results/<date>-<what>/`.

- Noise floor and headroom at the guitar input and the mic input, with the screen lit, the fans
  running, the Pi under load, and each control and MIDI in use: the box is the test, not the
  bench.
- The case's ground bond: hum with it, without it, and in another place.
- The right channel shorted by a mono plug: the left channel unaffected.
- The bypass or mute at power-up, reboot, standby and power loss.
- **Done when** each number is in `bench-results/` and set against phase 1's predictions.

## Phase 9: what next

What the box taught; whether the bigger case's board (two combo inputs, balanced outputs,
phantom) is still wanted, and if so it starts from the phase 2 schematic and this board's lessons.
