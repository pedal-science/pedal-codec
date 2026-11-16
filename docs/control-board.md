# pedal-codec: the control board (1590DD box)

Written 2026-11-16, when its schematic was drawn; the two lamps added the same day. The box's three boards are in
[../../pedal.project/docs/box-design.md](../../pedal.project/docs/box-design.md); the other two are
[box-board.md](box-board.md) (audio) and [pi-board.md](pi-board.md).

## What it is

| | |
|---|---|
| Where | Under the face, rear right, behind the rear sockets: 37 × 47 mm (x 115.5–152.5, y 21.5–68.5 in box-design.md's frame), 7 mm below the face |
| Held by | The encoder's nut |
| Carries | The encoder (Bourns PEC11R-4215F-S0024, with its push), the two buttons (Kinghelm KH-12X12X12H-TJ), a lamp in front of each button (Everlight 204-10SURD/S530-A3, 3 mm, red), the switches' pull-ups and filters, one 16-way flat-cable socket |
| Joined to the rest by | One 16-way 1.0 mm flat cable to the Pi board's RP2350, in the pin order box-design.md gives ("The control link's pin order") |

## The schematic

[`hardware/control-board/`](../hardware/control-board/) is a KiCad 10 project with one sheet,
[`control-board.pdf`](../hardware/control-board/control-board.pdf) beside it, drawn through Konnect.

Checked on 2026-11-16, and again with the lamps: KiCad's ERC at every severity (`kicad-cli` and
Konnect's `run_erc`), 0 errors and 0 warnings; 16 nets, none with one pin; `LCSC`, `MPN` and a
footprint on all 22 parts, and every LCSC number is the MPN it names, in stock.

## Decided while drawing

1. **The filters are at the switches**, so the lines are slow before they reach the cable. The
   encoder's A and B take Bourns' own filter: 10 kΩ up, 10 kΩ in series, 10 nF. The encoder's push
   and the buttons take 10 kΩ up, 1 kΩ and 100 nF, as the Pi board's footswitches do. Its common
   (C) and one side of each switch go to ground.
2. **Everything is pulled up to VDD**, the RP2350's 3.3 V from the Pi board (control link pin 16),
   with 100 nF at the socket. Named VDD here as on the Pi board, so it is never mistaken for the
   Pi's 3.3 V.
3. **The encoder's lugs are not connected.** They are joined to its bush, which is nutted to the
   case, and the guitar socket is the one bond between circuit ground and the case.
4. **The buttons are wired corner to corner.** A 12 mm switch's four pins are two pairs; only one
   pin of each opposite corner is wired (pads 1 and 2 of its footprint), which is across the
   contact whichever way the pins are paired inside. The other two are soldered and carry no net.
5. **A lamp in front of each button** (the owner, 2026-11-16), D1 and D2: Everlight's
   204-10SURD/S530-A3, a 3 mm red lamp with a frosted lens, 2.0 V at 20 mA. Each is fed from the
   control link (pin 12 for button 1's, pin 13 for button 2's) and returns to ground; its
   resistor, 330 Ω, is on the Pi board, so each takes about 4 mA from the RP2350's 3.3 V. Red
   because its 2.0 V leaves the resistor something to work with at 3.3 V, where a white or blue
   lamp's 3.0 V or more would not. Pin 14 is spare.
6. **How a lamp meets the face.** The board is about 7 mm below the face and the face is 2.5 mm
   thick. The lamp's lens is 3.0 mm across and its flange 4.0 mm, 1.0 mm thick, with 4.2 mm of
   lens above it (Everlight's drawing). The face has a ⌀3.3 mm hole for each. The lamp is put in
   the board loose, the board is fitted to the face by the encoder's nut, each lamp is pushed up
   until its flange rests under the face, and then it is soldered. It stands 1.7 mm proud, a
   little less than the buttons' 2.5 mm, and its height sets itself whatever the encoder's
   exact body height turns out to be. These are the board's only joints made in the case; they
   are the lamp's own leads going into the board, which box-design.md's first rule allows.

## Open

1. **How the buttons are lit: answered 2026-11-16** (Decided 5 and 6). Still to try with a
   sample in the test case: the lamp in a ⌀3.3 mm hole once the case is coated, and whether
   4 mA of red is the brightness wanted. The colour is any 3 mm lamp's to change; the brightness
   is the Pi board's 330 Ω and the firmware's.
2. **The encoder's lugs are drawn as round holes.** Bourns draws 2.6 × 1.8 mm slots; Konnect
   can't draw a slot, so each is a round 2.7 mm hole, which the lug fits. The owner may redraw
   them as slots in KiCad's footprint editor.
3. **The board's outline and heights** come from the case model when it is laid out: the encoder's
   body is about 7 mm behind the face and the buttons' stems stand 2.5 mm proud of it.

## Footprints checked against the makers' drawings (2026-11-16)

| Part | Footprint | Against | Result |
|---|---|---|---|
| SW1, Bourns PEC11R-4215F-S0024 | `pedal-codec:RotaryEncoder_Bourns_Vertical_PEC11R-4xxxF-Sxxxx`, new | Bourns' PEC11R datasheet, PCB layout for PEC11R-4xxxF-Sxxxx | Made from it: A, C, B at 2.5 mm, 7.5 mm from the shaft; the switch's pins 5.0 mm apart, 7.0 mm from the shaft on the other side; 1.0 +0.1/−0 mm holes; the lugs 13.2 mm apart on the shaft's line. KiCad's Alps EC11E footprints have the same pins but lugs 11.2 mm apart, which this part doesn't fit |
| SW2, SW3, Kinghelm KH-12X12X12H-TJ | `pedal-codec:SW_Kinghelm_KH-12X12X12H-TJ`, new | Kinghelm's drawing | Made from it: four 1.5 mm holes on 12.5 × 5.0 mm. KiCad's `SW_PUSH-12mm` has the same grid with 1.3 mm holes |
| J1, JUSHUO AFA07-S16FCC-00 | KiCad's `JUSHUO_AFA07-S16FCA-00_1x16-1MP_P1.0mm_Horizontal` | JUSHUO's drawing | As on the audio board (box-board.md) |
| D1, D2, Everlight 204-10SURD/S530-A3 | KiCad's `LED_THT:LED_D3.0mm` | Everlight's drawing for the 204-10 package (the 204-10SDRD's sheet, the same package) | Fits: leads 0.5 mm square, 2.54 mm apart; lens 3.0 mm, flange 4.0 mm. The longer lead is the anode, the footprint's pad 2 |

## kicad-happy's analysis (2026-11-16)

kicad-happy 2.3.1's `analyze_schematic.py` and its ngspice pass, run again with the lamps: 2
errors, 1 warning (no `datasheets/` directory, answered as for the audio board), 11 info findings;
the six filters simulated, all pass. The two errors are "LED D1 (and D2): no current-limiting
resistor found" (LR-001): each lamp's 330 Ω is on the Pi board, at the other end of the cable
(pi-board.md, Decided 11), which the analyzer can't see from this project. Not a fault.

## Parts

| Qty | Value | MPN | LCSC | Where |
|---|---|---|---|---|
| 1 | Flat-cable socket, 16-way 1.0 mm | AFA07-S16FCC-00 | C13744 | J1 |
| 1 | Encoder, 24 detents, push switch | PEC11R-4215F-S0024 | C143790 | SW1 |
| 2 | 12 × 12 mm button | KH-12X12X12H-TJ | C18186459 | SW2, SW3 |
| 2 | 3 mm red lamp | 204-10SURD/S530-A3 | C99772 | D1, D2 |
| 4 | 100 nF | CC0603KRX7R9BB104 | C14663 | C1, C4–C6 |
| 2 | 10 nF | 0603B103K500NT | C57112 | C2, C3 |
| 3 | 1 kΩ | 0603WAF1001T5E | C21190 | R6, R8, R10 |
| 7 | 10 kΩ | 0603WAF1002T5E | C25804 | R1–R5, R7, R9 |

22 parts.
