# pedal-codec: plan

From requirements to tested boards. Each phase has a done-when; the owner reviews the result of
each phase before the next starts (a demo of what was built, as for the pedal's milestones).

## Next session starts with

1. The owner reviews phase 2: the schematic as a PDF, [hardware/pedal-codec.pdf](../hardware/pedal-codec.pdf),
   with [schematic-review.md](schematic-review.md) and design.md's "Phase 2 schematic".
2. Then phase 3, the layout, starting with two things the schematic leaves to it: a TAC5212
   footprint with the RGE package's four corner pads, and KiCad's DNP attribute on the seven
   unfitted parts.

Last changed 2026-11-14: phase 2's schematic done and reviewed, waiting for the owner. Seven sheets
in KiCad 10, every symbol with `LCSC` and `MPN`, ERC clean, the netlist checked across sheets, and
the kicad-happy analysis and its ngspice run triaged with every finding answered. The review added
one capacitor (C94, on the load switch's output) and checked every custom symbol's pinout against
its maker's datasheet; the relays became Omron G6K-2F-Y, whose pinout is published. Before that,
2026-11-11: phase 1 done (the TAC5212 brought up from userspace over I2C, every part with its
LCSC number and stock, the phantom supply a TPS61170 with a voltage doubler, and ngspice for each
mode, the supply rejection and the phantom thump and faults).

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

## Phase 3: layout

- The HAT+ outline (65 × 56.5 mm, M2.5 holes on 58 × 49 mm), the 40-pin header, the input, output
  and panel connectors along the edges, clear of the Pi 5's camera, display and PCIe connectors,
  with 16 mm standoffs so the Active Cooler fits beneath it. Nine connectors now (four input,
  four output, the panel's) take about 110 mm of edge in XH's 2.5 mm pitch, against about 120 mm
  of edge the header leaves free: place them first, then everything else.
- **4 layers**: signal, unbroken ground, power, signal. The boost converters in the corner
  furthest from the inputs, their switching loops small, the 1 MΩ nodes short and guarded. One
  ground plane, not split; analogue and digital kept apart by placement.
- DRC against JLCPCB's 4-layer rules; the `emc` skill's check; a 3D export checked against a Pi 5
  model.
- **Done when** DRC is clean and the owner has reviewed the layout (plots and the 3D view).

## Phase 4: order v1

- The fab package (Konnect `manufacturing`, or the `bom` and `jlcpcb` skills): Gerbers, drill,
  BOM with LCSC numbers, placement file, checked against JLCPCB's assembly rules.
- JLCPCB, 4-layer, 5 boards, assembled on the top side (the codec's QFN needs a stencil and reflow
  anyway); the through-hole header and XH connectors either by JLCPCB or by hand. PCBWay is the
  fallback if a part is out of stock at LCSC.
- Optionally, in parallel: TI's TAC5212 evaluation module, to bring the codec and its driver up
  on a Pi before the boards arrive. With the driver the one new risk, this is worth more than it
  was for the TAC5242.
- **Done when** the owner has the quote and has placed the order. Agents never place it.

## Phase 5: bring-up

On piv, the bench device, not vip (vip's WM8960 stays wired as it is).

- Power before the Pi: the board on a bench supply, every rail measured, the phantom rail with
  phantom off and on, no part warm.
- EEPROM: written with Raspberry Pi's `eepmake` and `eepflash.sh` (WP held low at its test
  point), naming the overlay.
- The codec answering at 0x50 on I2C1, configured by a start-up tool that writes its registers
  over `/dev/i2c-1` (design.md, "Linux", route 2). The driver (route 1) follows if ALSA's mixer
  controls are wanted.
- The overlay in `overlay/`, then playback, capture, and an analogue loopback at 48 kHz.
- **Done when** audio passes from input to output through the Pi, and the board identifies
  itself through `/proc/device-tree/hat/`.

## Phase 6: measure

Evidence into `bench-results/<date>-<what>/`, as the pedal does.

- Plug detection and every switch, read by the Pi, in each combination; phantom present only on
  the XLR pins, and never with its switch off, including through the Pi's standby and reboot.
- Noise floor and headroom per input mode, phantom off and on, and the Mic path's equivalent input
  noise with 150 Ω on its input.
- THD+N and frequency response, in and out.
- The balanced outputs: the two legs' impedances matched, level at full scale with the pad in and
  out, and phantom power
  switched on, left on and hot-plugged (a phantom-powered input, such as the SSL 2+'s, as the
  pedal plans).
- Round-trip latency, linear-phase against low-latency filters, Pi-master against codec-master.
- Interference from the Pi: its 5 V ripple and its load steps, seen at the outputs.
- **Done when** each number is in `bench-results/` and set against the datasheet's.

## Phase 7: v2

What v1 taught, and the step down to Pi Zero size if the options can go. Whether the pedal takes
the board is decided here, with the owner, and then lands in `pedal.project`'s plan.
