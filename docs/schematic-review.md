# pedal-codec: schematic review (phase 2, 2026-11-14)

The review of the v1 schematic in [`hardware/`](../hardware/), before layout. Every finding has an
answer; the one change it made is in the schematic (C94).

**Verdict: ready for the owner's review and then for layout**, with two items carried into phase 3:
the DNP attribute, and the review steps that need a board.

## What was run

| Check | Result |
|---|---|
| KiCad ERC (`kicad-cli sch erc --severity-all`) | 0 violations, 0 warnings |
| Sheet pins against hierarchical labels (Konnect `validate_sheet_pins`) | 0 issues |
| Netlist (`kicad-cli sch export netlist`), every net | 238 nets; the only one-pin nets are the 15 flagged no-connects (J1's unused GPIO, the mute relays' NO contacts, U3's NC pin) |
| Cross-sheet nets | ADC1/2 ± join U6 and each input's OPA1637; DAC1/2 ± join U6 and each output; I2S, I2C, CODEC_IRQ, PLUG, LINE, PH_SW, PHP, PH_LED, PAD and UNMUTE join the header, the panel and the channel sheets; +48V reaches both inputs' phantom switches; VM reaches all seven loads |
| kicad-happy `analyze_schematic.py` | 173 findings: 0 errors, 10 warnings, 163 info; triaged below |
| kicad-happy `spice` (ngspice) on the subcircuits it detects | 84 subcircuits: 81 pass, 1 warning, 2 skipped; triaged below |
| Pinouts against the makers' datasheets | TAC5212, OPA1637, TPS22917, TPS61170, TS5A23157, G6K-2F, HSO321S: below |
| Decoupling | Each op-amp and the analogue switch has its own 100 nF on +5VA (13 of 13); the codec has 10 µF + 100 nF on IOVDD and 10 µF + 2.2 µF + 100 nF on AVDD |

The analogue stages' gains, noise, headroom, supply rejection, the phantom thump and faults were
settled by simulation in phase 1 ([sim/results/README.md](../sim/results/README.md)); this review
checks that the schematic carries those values, not the analysis again.

**The sheets were then redrawn for reading** (same day): every sheet now draws its circuit with
wires in signal order, where the first version placed parts on a grid joined only by net labels.
The redraw changed no connection. Its netlist matches the reviewed one net for net (238 nets, 352
parts, every part's value, footprint, LCSC and MPN), checked part by part rather than by
designator, and ERC is still clean. Only a few designators on the channel sheets moved: each
input's three op-amps (now OPA2197, OPA1612, OPA1637 in that order: U7–U9 and U10–U12), and the
second output's 22 µF (C85) and shield parts (C92, R163). The findings below were made on the
reviewed netlist and stand.

## The change it made

**C94, 10 µF on the load switch's output (+5V_SW).** U2 (TPS22917) feeds L1, the analogue 5 V
filter's 10 µH. When the Pi's 3.3 V drops with 5 V still up (shutdown, standby), U2 turns off with
the analogue rail's current still flowing in L1, and with nothing on VOUT but QOD that current
pulls VOUT below ground. The datasheet's absolute minimum for VOUT is −0.3 V, and TI characterises
the part with a 1 µF load. With 10 µF there, about 70 mA in 10 µH swings VOUT by about 70 mV,
I·√(L/C). Same part as C13 (C15850). ERC is still clean with it.

## Findings and answers

| Finding (analyzer rule) | Answer |
|---|---|
| Single-pin nets SDA, SCL, CODEC_IRQ, I2S_* (NT-001) | Analyzer artefact: it doesn't count J1's pins (the 40-pin header symbol). KiCad's own netlist has J1 on each: SDA = J1.3 + U6.8, CODEC_IRQ = J1.22 + U6.11, I2S_BCLK = J1.12 + R19, and so on |
| No pull-ups on SDA/SCL (PU-001) | By design: the Pi has 1.8 kΩ pull-ups to 3.3 V on GPIO 2 and 3. ID_SD/ID_SC carry the HAT+ 3.9 kΩ (R1, R2) |
| QOD "pull-up" R164 is 0 Ω (PU-001) | By design: QOD tied to VOUT is TI's quickest discharge; the 0 Ω exists only so ERC accepts the tie, and it can be fitted as a resistor to slow the discharge |
| +48V, V27, V54, +5V_RLY have no declared source (RS-001) | The boost and doubler diodes, the capacitance multiplier's emitter and the relays' ferrite (FB1) are their sources; no regulator pin to point at. Not an issue |
| U5 output estimated at 24.1 V (DO-DET) | Analyzer guess (an assumed 0.6 V reference, and the wrong rail). The TPS61170's reference is 1.229 V, so R9 392 kΩ over R10 10 kΩ holds the doubled rail at 49.4 V, and the capacitance multiplier's emitter, +48V, sits about 0.7 V below: 48.7 V, inside 48 ± 4 V |
| LC filter L2/C17 at 50 kHz, Q 116 (SPICE warning) | Not a filter: L2 is the boost inductor and C17 the doubler's flying capacitor |
| OPA1637 stages U9, U12 skipped by SPICE | Fully differential amplifiers, which the detector can't model; phase 1 simulated them (−3 dB at 137–139 kHz in every mode) |
| No ESD protection on J2–J10 (EP-AUD) | The inputs have series resistors and Schottky clamps (SS14) to the analogue 5 V and from ground behind the phantom capacitors; the outputs have 100 Ω and 10 Ω series resistors and, on the balanced side, the same clamps. TVS diodes on every audio line would add capacitance and leakage at the 1 MΩ node; not added for v1. Revisit if bring-up shows the panel wiring needs it |
| J2 has eight signals to one ground (CG-AUD) | The panel's lines are DC logic and two LED feeds through 22 kΩ; one ground is enough |
| Two "headphone jacks" J4, J6 (AH-001) | The ¼″ halves of the combo jacks, named by footprint. Not an issue |
| Lifecycle audit skipped (LC-007) | Every part's LCSC stock was checked when it was chosen (phase 1 and this phase); `bom`/`lcsc` repeat it before the order (phase 4) |
| Seven unfitted parts are marked DNP only in their Value text: the oscillator option (X1, its decoupling C37, its link R22) and each balanced output's SHIELD-to-ground footprints (C82 and R130, C92 and R163) | Carried to phase 3: KiCad's "do not populate" attribute must be set on them before the BOM and placement files are made, or JLCPCB would fit them. Konnect has no tool for the attribute, so the owner or KiCad sets it |

## Pinouts checked against the datasheets

Checked from each maker's PDF (kept outside the repository), not from the symbols:

- **TAC5212 (U6)**, TI SLASF23A, Table 5-1: pins 1–24, the four corner VSS pins A1–A4 and the
  thermal pad all match.
- **OPA1637 (U9, U12)**: IN− 1, VOCM 2, VS+ 3, OUT+ 4, OUT− 5, VS− 6, PD 7, IN+ 8. PD is tied
  high, which is normal operation.
- **TPS22917 (U2)**: VIN 1, GND 2, ON 3, CT 4, QOD 5, VOUT 6.
- **TPS61170 (U5)**: FB 1, COMP 2, GND 3, SW 4, CTRL 5, VIN 6, the pad to ground; the boost diode,
  doubler diodes and capacitors face the right way.
- **TS5A23157 (U15, U18)**: IN1 1, NO1 2, GND 3, NO2 4, IN2 5, COM2 6, NC2 7, V+ 8, NC1 9, COM1 10.
  PADN low selects NC, the padded path.
- **G6K-2F (K1–K8)**, Omron's terminal drawing (top view): coil + 1 and − 8, COM 3 and 6, NC 2
  and 7, NO 4 and 5. So each mute relay (K7, K8) ties its output to the mid-rail at rest and opens
  when energised, and each input's selector (K1, K4) takes the XLR at rest and the ¼″ when
  energised. Coil polarity matches the drivers.
- **HSO321S (X1)**: OE 1 (tied high), GND 2, OUT 3, VDD 4.
- **MMBT5551, MMBT5401, 2N7002**: SOT-23 pin 1 base/gate, 2 emitter/source, 3 collector/drain, the
  makers' usual order, as the symbols assume.
- **CAT24C32 (U1)**: the standard SOIC-8 I2C EEPROM order. WP is pulled up through R3 (1 kΩ), with
  TP1 to ground it for writing, as the HAT+ guide does.

## Not done here, and why

| Step | Why |
|---|---|
| PCB analysis, cross-analysis, EMC, thermal | No layout yet: phase 3 runs them, with DRC |
| Gerber analysis | No fab outputs yet: phase 4 |
| `kicad-design-review-agent` | The independent review the plan names; it runs on request, and best on the finished layout (phase 3) |
| Manufacturer op-amp models in the SPICE decks | Phase 1's behavioural models stand; the makers' models are a phase 3 refinement if a result is marginal |
