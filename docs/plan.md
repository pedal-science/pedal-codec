# pedal-codec: plan

From requirements to tested boards. Each phase has a done-when; the owner reviews the result of
each phase before the next starts (a demo of what was built, as for the pedal's milestones).

## Next session starts with

1. **The audio board's schematic is drawn, and the owner has looked it over** (2026-11-15: "looks
   good to my untrained eye"):
   [`hardware/audio-board/audio-board.pdf`](../hardware/audio-board/audio-board.pdf), five pages,
   ERC clean. [box-board.md](box-board.md) says what is on it, what was decided while drawing it,
   and what is open. It is step 4 of the box's plan
   ([../../pedal.project/docs/box-design.md](../../pedal.project/docs/box-design.md)), for one
   board of the three.
2. **The bypass has two relays** (the owner, 2026-11-15), so the bypassed guitar never touches
   the buffer. One thing is still the owner's to decide: whether the mic input keeps its four
   63 V capacitors (box-board.md, "Decided while drawing").
3. **Next here:** the Pi board's schematic and the control board's, each a KiCad project of its
   own beside `hardware/audio-board/`. The Pi board's flat-cable socket has to carry the nets in
   box-design.md's "The link's pin order", and its parts for the RP2350 and MIDI are already
   chosen (box-board.md, last section).
4. **Before the audio board is laid out:** phase 4's checks, the first of which needs one
   NMJ6HCD2 in the owner's hand.

Last changed 2026-11-15: phases 3 to 9 rewritten for the audio board. They had described one
L-shaped board on a ribbon with every control on it, which the box's design replaced on
2026-11-14 with an audio board, a Pi board and a control board. Before that, 2026-11-14: phase 2's
schematic of the full-size HAT, seven sheets, reviewed and redrawn as circuits (`a67618f`), which
is still in `hardware/` and is where the audio board's parts and values come from. 2026-11-11:
phase 1 (the TAC5212 brought up from userspace over I2C, every part with its LCSC number and
stock, ngspice for each mode, the supply rejection and the phantom thump and faults).

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

## Phase 3: the audio board's schematic

- A KiCad 10 project in `hardware/audio-board/`, drawn through Konnect, with the phase 2 project
  left as it is: the link and the supplies, the codec, the two inputs, the two outputs with the
  bypass relays and EXT FS.
- Every carried-over part keeps its value, footprint, `LCSC` and `MPN`; the five connectors are
  the parts box-design.md chose.
- The flat cable's pin order decided and written into box-design.md, for the Pi board to match.
- ERC clean; the netlist read net by net against the intended circuit.
- **Done when** the owner has reviewed the schematic as a PDF.
- **Status (2026-11-15):** done, and seen by the owner, who asked for the second bypass relay the
  same day. `hardware/audio-board/audio-board.pdf` is the export; box-board.md is the record.

## Phase 4: checks before layout

Each of these can change the schematic or a footprint, so they come before any copper.

- **The first NMJ6HCD2, with a meter: is the chrome ferrule joined to the sleeve contact?** The
  drawing doesn't say. The guitar socket is meant to be the one bond between circuit ground and
  the case, and the same part is used for the output and EXT FS. If the ferrule is joined, all
  three bond; the answer goes into box-board.md, with what is done about it. While the part is
  out: which contact each of its six pins is, against KiCad's symbol.
- The footprints against their makers' drawings: both Neutrik sockets, and the flat-cable socket
  (the schematic names KiCad's AFA07-S16FCA-00; the part is the FCC). The flat-cable socket's
  current rating per contact, from the same sheet.
- A TAC5212 footprint from TI's land pattern, with the four corner pads KiCad's lacks.
- KiCad's "do not populate" attribute set on X1, C28 and R15.
- The owner's decision on the mic's capacitors, and the schematic changed if it changes.
- ngspice for what changed: the bypass relays' switching transient at the output socket, and the
  right channel into a mono plug. The bypass with the buffer unpowered is done
  ([`sim/box/`](../sim/box/README.md)), and is why there are two relays.
- The kicad-happy analysis and its ngspice run on the new project, every finding answered, as
  phase 2 did; the independent `kicad-design-review-agent` pass.
- **Done when** each has its answer in box-board.md and ERC is still clean.

## Phase 5: layout

- The outline, the sockets' positions and the height limits come from the case model in
  `../pedal.project/enclosure/src/box_layout.py`, not from here: about 60 × 104 mm, the three
  ¼″ sockets 18.7 mm apart on the rear edge, the mic socket on the right edge, about 9 mm above
  the board under the footswitch.
- **4 layers**: signal, unbroken ground, power, signal. The 1 MΩ node is a few millimetres from
  the guitar socket to the buffer, guarded. The bypass's trace from K2 at the guitar socket to K1
  at the output socket carries the same raw signal and gets the same care. The flat-cable socket, the codec's
  digital side and K1 are at the end away from the inputs; K2 has to be at the guitar socket.
- The EXT FS lines run along the board's edge, filtered where they enter.
- The flat cable's type and the Pi board's pin numbering are fixed here, with the Pi board's
  layout, and written into box-design.md.
- DRC against JLCPCB's 4-layer rules; the `emc` skill's check; a STEP export set into the case
  model to check every height and that the board tilts into the rear wall.
- **Done when** DRC is clean and the owner has reviewed the plots and the board in the case model.

## Phase 6: order

- The fab package (Konnect `manufacturing`, or the `bom` and `jlcpcb` skills): Gerbers, drill,
  BOM with LCSC numbers, placement file. Stock checked again on the day.
- JLCPCB, 4-layer, assembled. The four sockets are through-hole: assembled by JLCPCB if they
  will, by hand if not (about 25 joints a board).
- Ordered with the Pi board and the control board, so the three arrive together.
- **Done when** the owner has the quote and has placed the order. Agents never place it.

## Phase 7: bring-up

On the bench first, the audio board alone on a short flat cable, then in the box on vip.

- Power before the Pi: 5 V and 3.3 V on a bench supply through the flat-cable socket, the rails
  at their test points, nothing warm. With 3.3 V off and 5 V on, +5VA and +3V3A are off.
- The codec at 0x50, configured from userspace (design.md, "Linux", route 2); the overlay in
  `overlay/`; playback, capture, loopback. GPIO2 reading the guitar socket's plug contact.
- Both relays from the RELAY line; the bypass at rest, with no power and a loud guitar; EXT FS's
  two lines at the cable.
- In the box, on vip: the pedal's own changes land in `pedal.project` and `rtpi` (the codec, its
  overlay and clocking replace the WM8960's), in dependency order, as the pedal's working rules
  say. They are decided with the owner then, not before.
- **Done when** the pedal plays through the board in the box, bypass and both inputs working.

## Phase 8: measure in the box

Evidence into `bench-results/<date>-<what>/`.

- Noise floor and headroom at the guitar input and the mic input, with the screen lit, the Pi
  under load, and each control and MIDI in use: the box is the test, not the bench.
- The case's bond: hum with the guitar socket's alone, and, if the ferrules are joined, with all
  three.
- A mono plug in the output: the left channel unaffected.
- The bypass at power-up, reboot, standby and with no power, with a loud guitar.
- Pi-master against codec-master clocking, if X1 is fitted on one board.
- **Done when** each number is in `bench-results/` and set against phase 1's predictions.

## Phase 9: what next

What the box taught; whether the bigger case's board (two combo inputs, balanced outputs,
phantom) is still wanted, and if so it starts from the phase 2 schematic in `hardware/` and this
board's lessons.
