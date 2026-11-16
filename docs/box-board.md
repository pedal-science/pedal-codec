# pedal-codec: the audio board (1590DD box)

Rewritten 2026-11-15 for the audio board. The pedal's box is three boards now, agreed by the owner
on 2026-11-14: [../../pedal.project/docs/box-design.md](../../pedal.project/docs/box-design.md).
This file is the audio board's part of that design: what is on it, how its schematic was made
from the phase 2 sheets, what was decided while drawing it, and what is still open.
[plan.md](plan.md) is the route from here to a board in the box.

Until 2026-11-14 this file described one L-shaped board on a ribbon, with the RP2350 and every
control on it. That version is in git (`8b55ef9`). Its circuits and the owner's answers carry over
and are below; its form, its XH leads, its ribbon and its measurements of the prototype do not.

## What it is

| | |
|---|---|
| Where | Rear right of the case and the right end of the front strip: about 60 × 104 mm, near the base plate |
| Held by | The three ¼″ sockets' nuts on the rear wall and the mic socket's two screws on the right wall |
| Carries | Guitar in, EXT FS and stereo out (three Neutrik NMJ6HCD2); the mic input (a Neutrik NCJ6FA-H); the guitar buffer; the mic preamp; the TAC5212 with its filters and decoupling; one output stage per channel; the two bypass relays; the analogue supplies; one 16-way flat-cable socket |
| Does not carry | Anything digital but the codec's own lines. The RP2350, MIDI, the footswitches, the encoder, the buttons, the ID EEPROM and the USB-C socket are on the Pi board and the control board |
| Joined to the rest by | One 16-way 1.0 mm flat cable to the Pi board, which is the only place the two boards' grounds meet |

## The schematic

[`hardware/audio-board/`](../hardware/audio-board/) is a KiCad 10 project of its own:
`audio-board.kicad_sch` and four sheets. [`audio-board.pdf`](../hardware/audio-board/audio-board.pdf),
beside it, is the export. **The phase 2 project in `hardware/` is untouched**, so the full-size
HAT's approved schematic is still there and still opens.

The sheets were drawn new, through Konnect, rather than cut out of copies of the phase 2 files:
most of each phase 2 sheet goes, and what is left reads better drawn in signal order than with
gaps. Every carried-over part took its value, footprint, `LCSC` and `MPN` from the phase 2 part it
replaces, read from that schematic's netlist, not retyped. Designators are numbered afresh, sheet
by sheet.

| Sheet | Holds |
|---|---|
| Link and power | J1, the flat-cable socket; U1, the analogue 5 V's load switch, and L1; U2, the AVDD regulator; the mid-rail and its buffer, U3; FB1 and the relay coil's rail; test points on +5VA, +3V3A, VM and ground |
| Codec | U4, the TAC5212, with its supplies' decoupling, the two input filters, the I2S series resistors, the address strap, and the unfitted oscillator option (X1) |
| Inputs | J2, guitar in, with K2 (the bypass relay at the input), U5 (the buffer) and U6 (its differential driver); J3, mic in, with U7 (the preamp) and U8 (its driver) |
| Outputs, bypass and EXT FS | U9, both output stages; K1, the bypass relay at the output, with Q1, which drives both coils; J4, stereo out; J5, EXT FS, with its two filters |

Checked on 2026-11-15:

| Check | Result |
|---|---|
| KiCad ERC, every severity (`kicad-cli sch erc --severity-all`, and Konnect's `run_erc`) | 0 errors, 0 warnings |
| Netlist (`kicad-cli sch export netlist`), every net read against the intended circuit | 108 nets. The only one-pin nets are the nine flagged no-connects: the unused switch contacts of J2, J4 and J5, K2's spare contact, and U2's NC pin |
| `LCSC`, `MPN` and a footprint on every symbol | 144 of 144 (the eight test points carry `none` and "PCB test pad", as in phase 2) |
| Polarised parts and diodes, read from the netlist | Each electrolytic's positive pin is on its higher-voltage side; the clamps and the coil's diode face the right way |

## What carried over, and from where

| On the audio board | From phase 2 | Changed? |
|---|---|---|
| U1 TPS22917, L1, the 110 µF, U2 TPS7A2033, the mid-rail (R2–R5, C10–C12) and U3 OPA1656, FB1 and the coil rail | Power sheet: U2, L1, U3, U4, FB1 | No |
| U4 TAC5212, its decoupling, DREG and VREF capacitors, input filters (47 Ω, 2.2 nF, 10 µF), I2S 33 Ω, address 0 Ω, X1 and its two parts (unfitted) | Codec sheet: U6, X1 | The interrupt (GPO1) goes to a test point, not the Pi. GPIO2 reads the guitar socket |
| U5 OPA2197 and the instrument path: 100 nF film, 1 MΩ to VM, 1 kΩ, follower, 3.83 kΩ | Input sheet: U10 | No relays after it: it goes straight to its driver |
| U6 and U8 OPA1637, each with 4.99 kΩ and 220 pF feedback | Input sheet: U12 (and U9) | No |
| U7 OPA1612 and the mic path: 2 × 47 µF 63 V back to back, 10 Ω, SS14 clamps, 22 Ω, 1.2 kΩ to VM, 249 Ω and 49.9 Ω, 4.99 kΩ | Input sheet: U11 | The phantom feed is gone; a 100 kΩ bleed per leg is added (below) |
| U9 OPA1656, both halves: 10 µF, the differential-to-single-ended stage, 22 µF, 100 Ω, a bleed | Output sheet: U14, one per output | One dual for both channels; 10 kΩ in place of 1 kΩ + 9.09 kΩ; the bleed is 10 kΩ, not 100 kΩ (below) |
| K1 and K2 G6K-2F-Y, Q1 2N7002, D5 and D6 1N4148W | Output sheet: K7, Q10, D24 | Two relays on one driver, at the sockets, as a bypass, not two as mutes |

Gone: the 40-pin header, the ID EEPROM and the mounting holes (the Pi board's now); the phantom
supply and both feeds; the mode relays KA and KB and the Line path; the balanced followers, their
protection, the pad and its analogue switch; the panel connector and bench switches; both mute
relays; every XH connector.

## Decided while drawing

These are choices the schematic needed that no document had made. Each is one part or one wire to
change.

**Guitar input (J2).**
- The sleeve goes straight to ground. It is the one bond between circuit ground and the case.
- **The tip's switch contact goes to ground**, so with no plug in, the input is shorted and
  silent, and so is the bypassed output. Phase 2's four-wire lead did not bring that contact
  to the board.
- The 2.2 MΩ to ground is on the buffer's side of K2, so the buffer's input capacitor is settled
  before the relay ever joins it to the guitar. The tip itself always has a path to ground: the
  guitar, or with no plug the contact above.
- The ring goes to ground: a guitar lead's plug shorts it there anyway.
- **Plug detection** is the sleeve's switch contact, as phase 2: closed to the sleeve with no
  plug, open with one, pulled up to 3.3 V through 10 kΩ. It goes through 1 kΩ to the codec's
  GPIO2, so it costs no conductor in the cable. The Pi reads it over I2C: GPIO2 set as an input
  (`GPIO2_CFG` = 1, page 0 register 0x0B), then bit 2 of `GPO_GPI_VAL` (page 0 register 0x0E,
  1 = plug in). GPIO2 is disabled at reset, so it drives nothing before it is configured
  (SLASF23A, tables 8-12 and 8-15).

**Mic input (J3).**
- Both halves in parallel, as R8 decided: XLR 2 and the tip are hot, XLR 3 and the ring cold,
  XLR 1, the sleeve and the socket's ground contact are ground.
- **The coupling and protection stay as phase 2 drew them**, two 47 µF 63 V back to back per leg
  with the 10 Ω, the clamps and the 22 Ω, though the board supplies no phantom power. Then the
  input survives 48 V arriving from outside (a splitter, a wrong cable), and phase 1's noise and
  gain figures hold unchanged. One 22 µF 16 V part per leg would save four cans and give up
  both; it is the owner's to choose.
- A 100 kΩ bleed from each leg to ground, at the socket. In phase 2 the phantom feed's resistors
  gave the capacitors' socket side its path to ground; without them it would float.

**Output stages (U9).**
- One OPA1656 serves both channels. Phase 2 used one per output with half of each parked.
- Each input leg is one 10 kΩ. Phase 2 had 1 kΩ, for the mute relay to work against, and 9.09 kΩ.
  The gain goes from 0.743 to 0.750, 0.08 dB, and full scale from 1.45 to **1.50 Vrms (+5.7 dBu)**.
- The 100 kΩ bias resistors to VM are gone: with no relay there, the stage itself holds the
  capacitors' DC.
- **The bleed after each 22 µF is 10 kΩ, not phase 2's 100 kΩ**, and **the relays must not be
  energised until 10 s after the Pi's 3.3 V comes up**. At power-on each stage rises to the
  mid-rail and its capacitor charges through the bleed; whatever is still on it when K1 closes
  steps onto the output. With 100 kΩ that is 0.6 V at 5 s and 0.1 V at 10 s; with 10 kΩ it is
  24 mV at 5 s, 4 mV at 8 s and 1.3 mV at 10 s, and the rest is the mid-rail's own filter
  settling ([`sim/box/`](../sim/box/README.md)). The cost is 0.09 dB of level. The pedal's boot
  is being brought toward 5 s, so the wait is the firmware's to keep, not the boot's.

**Bypass relays (K1 and K2).** Two, on one line and one driver (the owner, 2026-11-15; R10 had
one). Both are drawn at rest.
- **K2, at the guitar socket.** At rest the tip goes to the bypass trace and is off the buffer.
  Energised, the tip goes to the buffer, and K2's other pole grounds the bypass trace, so the
  trace can't carry the output back to the input while the effect is on.
- **K1, at the output socket.** At rest the output's tip takes the bypass trace and its ring
  rests on 100 Ω to ground. Energised, the poles take the left and right stages. The bleeds
  are on the stages' side of the contacts, so each coupling capacitor settles while the pedal is
  still bypassed ("Output stages" above says how long that takes).
- **Why two.** With one, the tip stayed on the buffer's input while bypassed, and with the
  analogue 5 V off (the pedal unpowered, or the Pi in standby) that input's protection diodes
  clipped a loud guitar: 35 % distortion at 1 V peak, simulated with a generic diode
  ([`sim/box/`](../sim/box/README.md)). Now the bypass is a wire from socket to socket, whatever
  the supplies are doing.
- RELAY comes from the RP2350 through 1 kΩ to Q1's gate, with 100 kΩ to ground: no cable, or an
  RP2350 that isn't driving the line, is bypass. Each coil has its own diode.
- A mono plug in the output shorts the ring to the sleeve. Bypassed, that shorts the rest
  resistor. In effect it loads the right stage with its own 100 Ω through 22 µF: 15 mA rms at
  full scale, which the OPA1656 drives all day.

**EXT FS (J5).** Tip is switch A, ring is switch B, sleeve is ground. Each line has 1 kΩ at the
socket and 100 nF to ground on the cable's side of it. The pull-ups belong to the RP2350's supply,
so they are on the Pi board; with 10 kΩ there, a closed switch reads a tenth of the supply.

**Codec (U4).** As phase 2. The oscillator option for codec-master clocking stays as three
unfitted parts (X1, C28, R15), so the comparison phase 2 planned can still be made on this board.

**The link (J1).** Its pin order is in box-design.md, "The link's pin order". 10 µF on each of
+5 V and +3.3 V where they arrive.

## The owner's decisions that bind this board

From 2026-11-14, unchanged:

1. The mic socket is a combo XLR/¼″.
2. No phantom power in the box.
3. A bypass at rest, released by the RP2350 once the Pi's audio runs. Two relays on one line since
   2026-11-15, so the bypassed guitar never touches the buffer.
4. The guitar socket is a switching one, and the board reads its plug contact.
5. One bond between circuit ground and the case, at the guitar socket.
6. EXT FS is a ¼″ socket, between out and in.

## Open

1. **Is the NMJ6HCD2's chrome ferrule joined to its sleeve contact?** Neutrik's drawing doesn't
   say. One part serves all three places, so if it is, the output's and EXT FS's sleeves bond to
   the case too, 19 and 37 mm from the guitar socket's. Checked with a meter on the first part
   (plan.md, phase 4). If they are joined and the measurement in the box minds, the fix is an
   insulating washer set on two of the three, or a different part there.
2. **The flat-cable socket's current rating: answered 2026-11-16.** 0.5 A a contact, from
   LCSC's listing for the AFA07 series (JUSHUO's drawing gives none). The cable carries about
   0.15 A, on pin 16.
3. **The TAC5212's four corner pads: done 2026-11-16.** U4 now has
   `pedal-codec:Texas_RGE0024R_VQFN-24-1EP_4x4mm_P0.5mm_EP2.1x2.1mm`, made through Konnect from
   TI's RGE0024R land pattern. KiCad's `Texas_RGE0024H` had no corner pads and the wrong thermal
   pad too: 2.7 mm, where the TAC5212's is 2.1 mm.
4. **The three unfitted parts are marked DNP only in their value text**, as in phase 2. KiCad's
   "do not populate" attribute is set on X1, C28 and R15 before any BOM is made.
5. **Q1's gate gets 3.3 V.** The 2N7002's on-resistance is specified at 4.5 V and above. The two
   coils need 40 to 60 mA, and phase 2's relays were drawn the same way; checked at bring-up.
6. **The supply rejection, gain and noise simulations were not rerun.** Phase 1's decks cover
   the stages that are unchanged. What changed is small (0.08 dB at the outputs; the mic's bleeds,
   100 kΩ against a 2.4 kΩ input; the bypass, now a wire) and is reasoned here, not simulated.
7. **The mic input's four 63 V capacitors** stay unless the owner prefers one 22 µF per leg
   ("Decided while drawing").

## Footprints checked against the makers' drawings (2026-11-15)

| Part | Footprint in the schematic | Against | Result |
|---|---|---|---|
| NMJ6HCD2 | KiCad's `Jack_6.35mm_Neutrik_NMJ6HCD2_Horizontal` | Neutrik ST-NMJ6HCD2 | Matches: T, R and S in a row 6.35 mm apart, S nearest the panel; the three switch contacts 16.23 mm across; ⌀1.4 holes |
| NCJ6FA-H | KiCad's `Jack_XLR-6.35mm_Neutrik_NCJ6FA-H_Horizontal` | Neutrik drawing 20004521 | Matches to 0.07 mm: five ⌀1.2 holes (1, 2, 3, S, R), ⌀1.6 for both T pins and G, three ⌀1.6 unplated peg holes; the same hand as the drawing |
| TAC5212 (U4) | `pedal-codec:Texas_RGE0024R_VQFN-24-1EP_4x4mm_P0.5mm_EP2.1x2.1mm`, new (2026-11-16) | TI's RGE0024R example board layout and stencil (4225246/A), in the TAC5212 datasheet | Made from them: 24 pads 0.24 × 0.6 mm at 0.5 mm, rows 3.8 mm apart; the four corner VSS pads A1–A4, 0.25 mm square, 3.45 mm apart; the 2.1 mm thermal pad with its paste as four 0.94 mm squares. TI's optional vias in the pad are left to the layout |
| AFA07-S16FCC-00 | KiCad's `JUSHUO_AFA07-S16FCA-00_1x16-1MP_P1.0mm_Horizontal` | JUSHUO's AFA07 drawing | The same part in other packing. In JUSHUO's numbering F is lower contact, the first C is matt tin, and the last letter is the packing: A is tape and reel, C is tube. Pads 0.6 × 1.8 mm at 1.0 mm, fitting pads 2.6 × 3.0 mm, as drawn. The cable is 0.3 mm thick |

So the flat-cable socket is a lower-contact part, as box-design.md has it, and it comes in tubes.

## kicad-happy's analysis (2026-11-16)

kicad-happy 2.3.1's `analyze_schematic.py` and its ngspice pass (`simulate_subcircuits.py`), run as
phase 2's were: 0 errors, 4 warnings, 63 info findings; 34 subcircuits simulated, all pass. Every
warning, and the info findings that look like faults, answered:

| Finding (rule) | Answer |
|---|---|
| No `datasheets/` directory beside the project (DS-002) | The pinouts were read from the makers' PDFs, kept outside the repository as the rules ask (schematic-review.md lists phase 2's); the new footprints name the drawings they came from |
| No pull-ups on SDA and SCL (PU-001) | By design: the Pi's own 1.8 kΩ pull-ups on GPIO 2 and 3, across the cable |
| +5V_RLY has no declared source (RS-001) | FB1, the ferrite from +5V, is its source; the analyzer doesn't count a ferrite as one |
| U1's QOD "pull-up" is 0 Ω (PU-001, info) | By design, as in phase 2: QOD tied to VOUT is the quickest discharge |
| Four op-amp stages of "unknown" configuration (OA-DET, info) | The followers, the mid-rail buffer and the differential stages, which the detector doesn't classify; phase 1's decks simulate them |

## Power

From the cable's +5 V, about 0.15 A by the earlier budget's figures (design.md, "Power"): the
two relay coils up to 60 mA, the codec about 30 mA, and the op-amps the rest, which are fewer than
the 60 mA estimate counted. One conductor carries it; the socket's rating per contact is read
from its sheet before layout.

| Rail | From | Feeds |
|---|---|---|
| +5VA | +5 V, U1 (on with the Pi's 3.3 V), L1 and 110 µF | Every op-amp, the mid-rail, U2 |
| +3V3A | +5VA, U2 (on with the Pi's 3.3 V) | The codec's AVDD |
| +3V3 | The Pi's 3.3 V, over the cable | The codec's IOVDD, the plug contact's pull-up, the two enables |
| VM | +5VA halved, two RC stages, U3 | The bias of every stage |
| +5V_RLY | +5 V through FB1, 110 µF | The two relays' coils |

With the Pi in standby (5 V on, 3.3 V off) both enables are low, so +5VA and +3V3A are off and
nothing back-powers the codec's IOVDD or the Pi's pins. The relay rail stays up, so the RP2350
could still hold the relays; it lets go when the Pi's reports stop.

## Parts

All from JLCPCB's parts list. The five connectors are new to this board (chosen in box-design.md,
"Parts chosen so far"); everything else kept its phase 2 part (design.md, "Parts"). Stock is
checked again before ordering.

| Qty | Value | MPN | LCSC | Where |
|---|---|---|---|---|
| 1 | Flat-cable socket, 16-way 1.0 mm | AFA07-S16FCC-00 | C13744 | J1 |
| 3 | ¼″ socket | NMJ6HCD2 | C368502 | J2, J4, J5 |
| 1 | Combo XLR and ¼″ socket | NCJ6FA-H | C368458 | J3 |
| 1 | TAC5212IRGER | TAC5212IRGER | C44853694 | U4 |
| 1 | OPA2197IDR | OPA2197IDR | C139363 | U5 |
| 1 | OPA1612AIDR | OPA1612AIDR | C94590 | U7 |
| 2 | OPA1637DGKR | OPA1637DGKR | C2860968 | U6, U8 |
| 2 | OPA1656IDR | OPA1656IDR | C1849431 | U3, U9 |
| 1 | TPS22917DBVR | TPS22917DBVR | C2681320 | U1 |
| 1 | TPS7A2033PDBVR | TPS7A2033PDBVR | C2862740 | U2 |
| 2 | G6K-2F-Y DC5 | G6K-2F-Y DC5 | C231389 | K1, K2 |
| 1 | 2N7002 | 2N7002 | C8545 | Q1 |
| 4 | SS14 | SS14 | C2480 | D1–D4 |
| 2 | 1N4148W | 1N4148W | C81598 | D5, D6 |
| 1 | 10 µH | FNR4030S100MT | C167879 | L1 |
| 1 | Ferrite | BLM18PG221SN1D | C80165 | FB1 |
| 1 | 12.288 MHz oscillator, unfitted | HSO321S | C160458 | X1 |
| 4 | 47 µF 63 V | RV63V47M6X8 | C48971005 | C35–C38 |
| 4 | 100 µF 16 V | RVT100UF16V67RV0016 | C2887276 | C6, C10, C11, C14 |
| 2 | 22 µF 16 V | EFVH016ADA220M0554 | C22387968 | C46, C49 |
| 4 | 10 µF X7R 1206 | CL31B106KAHNNNE | C14860 | C44, C45, C47, C48 |
| 15 | 10 µF 0805 | CL21A106KAYNNNE | C15850 | C1–C3, C5, C7, C12, C15, C16, C18, C22, C23, C25, C26, C34, C43 |
| 1 | 2.2 µF | CL10A225KO8NNNC | C23630 | C9 |
| 3 | 1 µF | CL10A105KA8NNNC | C5673 | C8, C20, C21 |
| 11 | 100 nF | CC0603KRX7R9BB104 | C14663 | C13, C17, C19, C32, C33, C41, C42, C50–C52; C28 unfitted |
| 1 | 100 nF C0G 1206 | GRM31C5C1H104JA01L | C97946 | C29 |
| 2 | 2.2 nF C0G | 0603CG222J500NT | C2991172 | C24, C27 |
| 1 | 1 nF | CL10B102KB8NNNC | C1588 | C4 |
| 4 | 220 pF C0G | GCM1885C2A221JA16D | C388907 | C30, C31, C39, C40 |
| 3 | 0 Ω | 0603WAF0000T5E | C21189 | R1, R14; R15 unfitted |
| 2 | 10 Ω | 0603WAF100JT5E | C22859 | R27, R32 |
| 2 | 22 Ω | 0603WAF220JT5E | C23345 | R28, R33 |
| 4 | 33 Ω | 0603WAF330JT5E | C23140 | R10–R13 |
| 5 | 47 Ω | 0603WAF470JT5E | C23182 | R5–R9 |
| 1 | 49.9 Ω | 0603WAF499JT5E | C23185 | R37 |
| 3 | 100 Ω | 0603WAF1000T5E | C22775 | R46, R52, R56 |
| 2 | 249 Ω | FRC0603F2490TS | C2933176 | R35, R38 |
| 5 | 1 kΩ | 0603WAF1001T5E | C21190 | R17, R20, R54, R57, R58 |
| 2 | 1.2 kΩ | 0603WAF1201T5E | C22765 | R29, R34 |
| 2 | 3.83 kΩ | FRC0603F3831TS | C2933213 | R21, R22 |
| 6 | 4.99 kΩ | 0603WAF4991T5E | C23046 | R23, R24, R36, R39–R41 |
| 4 | 7.5 kΩ | 0603WAF7501T5E | C23234 | R43, R45, R49, R51 |
| 10 | 10 kΩ | 0603WAF1002T5E | C25804 | R2–R4, R16, R42, R44, R47, R48, R50, R53 |
| 3 | 100 kΩ | 0603WAF1003T5E | C25803 | R25, R30, R55 |
| 3 | 1 MΩ | 0603WAF1004T5E | C22935 | R19, R26, R31 |
| 1 | 2.2 MΩ | 0603WAF2204T5E | C22938 | R18 |

136 parts and eight test pads.

## Parts chosen earlier for what is now the Pi board

The earlier version of this file chose the RP2350's parts and the MIDI optocoupler, on
2026-11-14. They are not on the audio board; the Pi board, drawn on 2026-11-16, uses them
([pi-board.md](pi-board.md)), with the SOIC-8 flash. Stock and prices were Konnect's copy of the
JLCPCB list that day.

| Part | Use | LCSC | Stock | Price |
|---|---|---|---|---|
| RP2350A (QFN-60, 7 × 7 mm) | The controls' microcontroller | C42411118 | 6,146 | $1.29 |
| Abracon AOTA-B201610S3R3-101-T (3.3 µH, polarity marked) | The RP2350's core regulator inductor | C42411119 | 672 | $0.34 |
| Abracon ABM8-272-T3 (12 MHz, 10 pF, 3225) | The RP2350's crystal, with 1 kΩ in series and its load capacitors | C20625731 | 442 | $0.40 |
| Winbond W25Q16JVUXIQ (16 Mbit, USON-8) | The RP2350's flash. With more stock: W25Q32JVSSIQ, SOIC-8, C179173 | C2843335 | 900 | $1.57 |
| Diodes AP2112K-3.3TRG1 (600 mA LDO, SOT-23-5) | The RP2350's 3.3 V from 5 V | C51118 | 9,742 | $0.17 |
| Everlight H11L1S(TA) (Schmitt-output optocoupler, SOP-6) | MIDI in, with 220 Ω, a 1N4148W across its LED and a pull-up to 3.3 V | C78589 | 20,375 | $0.33 |

Why these, briefly: the core regulator and the crystal follow Raspberry Pi's *Hardware design
with RP2350* exactly, because that document says other choices are at the designer's risk; the
H11L1 runs from 3.3 V where the 6N138 needs 4.5 V. The full reasoning is in `8b55ef9`.
