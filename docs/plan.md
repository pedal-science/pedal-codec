# pedal-codec: plan

From requirements to tested boards. Each phase has a done-when; the owner reviews the result of
each phase before the next starts (a demo of what was built, as for the pedal's milestones).

## Next session starts with

1. **All three of the box's schematics are drawn and the owner has looked over all three**
   (the audio board on 2026-11-15, the Pi board and the control board on 2026-11-16: "look fine
   to my untrained eye"). Phase 3 is done. Each is a KiCad project of its own, ERC clean, with
   its PDF beside it: [`audio-board.pdf`](../hardware/audio-board/audio-board.pdf)
   ([box-board.md](box-board.md)), [`pi-board.pdf`](../hardware/pi-board/pi-board.pdf)
   ([pi-board.md](pi-board.md)) and
   [`control-board.pdf`](../hardware/control-board/control-board.pdf)
   ([control-board.md](control-board.md)).
2. **The owner's decisions of 2026-11-16 are drawn**, after those PDFs were looked over, so the
   PDFs now show a little more than the owner saw:
   - a red lamp in front of each button, on the control board (control-board.md, Decided 5, 6);
   - the mic input has one 22 µF capacitor in each leg, not two 63 V parts back to back, because
     the pairs were only for phantom power (box-board.md, "Mic input");
   - the RP2350 reads the USB-C socket's CC lines, to warn of a supply under 3 A (pi-board.md,
     Decided 15);
   - a fan is assumed: a plug for it on the Pi board, switched by the Pi's GPIO 12 (pi-board.md,
     Decided 16); its place and the vents are in box-design.md, "Heat".
3. **Next here:** what is left of phase 4, which is two checks that need parts in the owner's
   hand: one NMJ6HCD2 (is its ferrule joined to its sleeve?) and one PJ-324M0 (which contact is
   tip, which ring?). Both parts are on the order list in
   [../../pedal.project/docs/box-order.md](../../pedal.project/docs/box-order.md). Then phase 5,
   layout, whose outlines come from the case model. The independent design review runs when the
   owner asks for it.

Last changed 2026-11-16: the Pi board's and the control board's schematics (phase 3), footprints
of our own in `hardware/pedal-codec.pretty/`, the control link and the RP2350's pins in
box-design.md; then phase 4's desk checks, which added the eFuse and the codec's footprint; then
the owner's decisions of that day (the lamps, the mic's capacitors, the supply sensing, the fan). 2026-11-15: phases 3 to 9 rewritten for the box's boards. They had
described one L-shaped board on a ribbon with every control on it, which the box's design
replaced on 2026-11-14 with an audio board, a Pi board and a control board. Before that, 2026-11-14: phase 2's
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

## Phase 3: the box's schematics

- A KiCad 10 project in `hardware/audio-board/`, drawn through Konnect, with the phase 2 project
  left as it is: the link and the supplies, the codec, the two inputs, the two outputs with the
  bypass relays and EXT FS.
- Every carried-over part keeps its value, footprint, `LCSC` and `MPN`; the five connectors are
  the parts box-design.md chose.
- The flat cable's pin order decided and written into box-design.md, for the Pi board to match.
- The Pi board (`hardware/pi-board/`) and the control board (`hardware/control-board/`), each its
  own project: the Pi board's parts as chosen on 2026-11-14, the RP2350 as Raspberry Pi's minimal
  design; the control link's pin order and the RP2350's pin map written into box-design.md.
- ERC clean; the netlist read net by net against the intended circuit.
- **Done when** the owner has reviewed the schematics as PDFs.
- **Status (2026-11-16):** the audio board done, and seen by the owner, who asked for the second
  bypass relay (2026-11-15); `hardware/audio-board/audio-board.pdf` is the export, box-board.md
  the record. The Pi board and the control board drawn on 2026-11-16, ERC clean, and looked over
  by the owner the same day: `pi-board.pdf` and `control-board.pdf`, with pi-board.md and
  control-board.md. **Done.**

## Phase 4: checks before layout

Each of these can change the schematic or a footprint, so they come before any copper.

- **The first NMJ6HCD2, with a meter: is the chrome ferrule joined to the sleeve contact?** The
  drawing doesn't say. The guitar socket is meant to be the one bond between circuit ground and
  the case, and the same part is used for the output and EXT FS. If the ferrule is joined, all
  three bond; the answer goes into box-board.md, with what is done about it. While the part is
  out: which contact each of its six pins is, against KiCad's symbol.
- **The first PJ-324M0, with a plug and a meter: which terminal is the tip and which the ring?**
  Read from XKB's cut-away view, not stated on its drawing (pi-board.md, Open 3). MIDI's LED
  current only flows one way, so if it is the other way round the footprint's T and R pads swap.
- The footprints against their makers' drawings: both Neutrik sockets and the flat-cable socket.
  **Done 2026-11-15**, all three match (box-board.md, "Footprints checked"). The Pi board's and
  the control board's: **done 2026-11-16**. KiCad's GCT USB4105 footprint fits the USB-C socket;
  the MIDI socket, L1, the encoder and the buttons have footprints of our own in
  `hardware/pedal-codec.pretty/`, made through Konnect from the makers' drawings, with round holes
  where the makers draw slots, since Konnect can't draw a slot (pi-board.md, control-board.md).
  The flat-cable socket's current rating: 0.5 A a contact, from LCSC's listing for the series
  (**answered 2026-11-16**; JUSHUO's drawing gives none).
- A TAC5212 footprint from TI's land pattern, with the four corner pads KiCad's lacks. **Done
  2026-11-16** (box-board.md, Open 3); KiCad's had the wrong thermal pad as well.
- KiCad's "do not populate" attribute set on X1, C28 and R15.
- The owner's decision on the mic's capacitors, and the schematic changed if it changes. **Done
  2026-11-16:** kept only if needed, and they were not, so one 22 µF 16 V in each leg
  (box-board.md, "Mic input"; `sim/box/mic-coupling.cir`).
- The owner's other decisions of 2026-11-16, drawn the same day: the lamps (control-board.md),
  the supply sensing and the fan's plug (pi-board.md, Decided 15 and 16). ERC clean on all three,
  and the kicad-happy analysis run again.
- ngspice for what changed ([`sim/box/`](../sim/box/README.md)). **Done 2026-11-15:** the bypass
  with the buffer unpowered, which is why there are two relays; and what is left on an output's
  capacitor when the relays close, which is why its bleed is 10 kΩ and the firmware waits 10 s.
  The right channel into a mono plug is 15 mA rms into its own 100 Ω, reasoned, not simulated.
- The kicad-happy analysis and its ngspice run on the three projects, every finding answered, as
  phase 2 did. **Done 2026-11-16**, and again after the owner's decisions were drawn: three errors
  and nine warnings across the three, each answered in its board's page, none a fault; every
  simulated subcircuit passes. Still to run: the
  independent `kicad-design-review-agent` pass, when the owner asks for it.
- How a HAT+ that powers the Pi tells it so, from Raspberry Pi's HAT+ specification. **Answered
  2026-11-16** (pi-board.md, Decided 1 and 13): the EEPROM stays at 0x50, the Standard class, and
  the overlay says `hat_current_supply = <3000>`. The specification also requires a Power HAT+
  to pass current one way only and to survive the Pi's own supply being plugged in, which the
  first draft didn't: the Pi board gained U6, an eFuse (TPS259470A), in place of its fuse.
- **Done when** each has its answer in box-board.md, pi-board.md or control-board.md, and ERC is
  still clean.

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
- The Pi board and the control board take their outlines from the same model. The Pi board faces
  the Pi, so its 40-pin socket is the mirror of an ordinary HAT's (pi-board.md, Open 1); its
  RP2350 regulator, L1 the right way round, is laid out as the Pico 2's.
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
- Both relays from the RELAY line, held off for 10 s after the Pi's 3.3 V rises; the thump at
  release measured; the bypass at rest, with no power and a loud guitar; EXT FS's two lines at
  the cable.
- The Pi board: USB-C power with no Pi on it (5 V and VDD at their test points, the RP2350
  running), then on the Pi: the ID EEPROM, the RP2350 flashed from the Pi over SWD and reset by
  it, the UART to the Pi, MIDI in, the footswitches, EXT FS and the control board; the current
  into the Pi's 3.3 V in standby; the two CC readings with a 3 A supply, a 1.5 A one and a plain
  USB port, and the warning each should raise; the fan from GPIO 12 (`gpio-fan`); both lamps.
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
- The mic input's rejection of hum at 50 and 100 Hz, which depends on how well its two
  capacitors match (`sim/box/mic-coupling.cir`).
- The noise floor with the fan running and stopped.
- **Done when** each number is in `bench-results/` and set against phase 1's predictions.

## Phase 9: what next

What the box taught; whether the bigger case's board (two combo inputs, balanced outputs,
phantom) is still wanted, and if so it starts from the phase 2 schematic in `hardware/` and this
board's lessons.
