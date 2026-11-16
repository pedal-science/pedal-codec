# pedal-codec: the Pi board (1590DD box)

Written 2026-11-16, when its schematic was drawn. The pedal's box is three boards, agreed by the
owner on 2026-11-14: [../../pedal.project/docs/box-design.md](../../pedal.project/docs/box-design.md).
This file is the Pi board's part of that design: what is on it, what was decided while drawing it,
and what is still open. The audio board is [box-board.md](box-board.md), the control board
[control-board.md](control-board.md); [plan.md](plan.md) is the route to boards in the box.

## What it is

| | |
|---|---|
| Where | Under the Pi, as a HAT: about 71 × 71 mm (x 12–83, y 2–73 in box-design.md's frame), with a cut-out under the Pi's processor for the heat block |
| Held by | The Pi's 40-pin header, in a 2 × 20 socket 8.5 mm high, and the Pi's four mounting holes |
| Carries | The USB-C power socket and the MIDI in socket, both on the rear wall; the HAT+ ID EEPROM; the RP2350 with its flash and crystal; the MIDI optocoupler; three plugs for the footswitches' leads; the two flat-cable sockets, to the audio board and the control board |
| Does not carry | Anything analogue. The codec and every audio stage are on the audio board |

## The schematic

[`hardware/pi-board/`](../hardware/pi-board/) is a KiCad 10 project of its own: `pi-board.kicad_sch`
and three sheets, with [`pi-board.pdf`](../hardware/pi-board/pi-board.pdf) beside it. Drawn through
Konnect, as the audio board was. Parts the phase 2 HAT already had (the 40-pin socket, the ID
EEPROM and its resistors, the 33 Ω, the 100 µF, the holes, the 2N7002, the 1N4148W) took their
fields from its netlist; the rest are the parts chosen on 2026-11-14 ([box-board.md](box-board.md),
"Parts chosen earlier for what is now the Pi board") and the passives Raspberry Pi's *Hardware
design with RP2350* names.

| Sheet | Holds |
|---|---|
| USB-C power and the Pi header | J1, the USB-C socket, with F1 (4 A), D1 (SMAJ5.0A), 100 µF and 10 µF, 5.1 kΩ on each CC and the shell's 1 MΩ ‖ 10 nF; J2, the Pi's 40-pin socket, with 33 Ω on the three I2S lines the Pi drives; U1, the ID EEPROM; four M2.5 holes |
| RP2350 | U4 (AP2112K-3.3), the RP2350's own 3.3 V (VDD); U2, the RP2350A, laid out as Raspberry Pi's minimal design: decoupling, VREG_AVDD's 33 Ω and 4.7 µF, L1 and the core supply's capacitors, U3 (W25Q32JV flash), Y1 (12 MHz, 15 pF, 1 kΩ); Q1, through which the Pi resets it; USB and BOOTSEL to test pads; the resistors to the Pi's UART and SWD; the Pi's 3.3 V sense |
| Links, footswitches and MIDI | J3, the audio link, in box-design.md's pin order; J4, the control link; J5–J7, the footswitches' plugs, with their pull-ups and filters; EXT FS's pull-ups; the buttons' lights' resistors; J8, MIDI in, with U5 (H11L1) |

Checked on 2026-11-16:

| Check | Result |
|---|---|
| KiCad ERC, every severity (`kicad-cli sch erc --severity-all`, and Konnect's `run_erc`) | 0 errors, 0 warnings |
| Sheet pins (Konnect's `validate_sheet_pins`) | 0 issues; the sheets join by global labels |
| Netlist (`kicad-cli sch export netlist`) | 113 nets, none with one pin. Every pin left open is a flagged no-connect: the USB-C's data and SBU pins, the Pi's unused GPIO, the RP2350's GPIO 17–29, U4's NC pin, U5's pin 3, the MIDI socket's sleeve and two break contacts, the control link's pin 14 |
| `LCSC`, `MPN` and a footprint on every symbol | 100 of 100 (the four holes and ten test points carry `none`, as in phase 2) |
| Every LCSC number against JLCPCB's parts list (Konnect's copy) | Each is the MPN and package the schematic says, and in stock |

## Decided while drawing

1. **Power: any USB-C supply gives 5 V, and nothing is negotiated.** 5.1 kΩ on each CC asks for 5 V;
   the source's own advertisement sets the current, 3 A from a 3 A supply. The Pi is fed through
   its header's 5 V pins, as a HAT+ power supply does (box-design.md, "Power", decided by the
   owner). F1, a 4 A fast fuse, and D1, a 5 V TVS, are at the socket. The shell goes to ground
   through 1 MΩ ‖ 10 nF, so a cable's shield is tied to ground at radio frequencies but never
   joins ground to the case at DC; the guitar socket stays the one bond.
2. **33 Ω on the I2S lines the Pi drives** (BCLK, FSYNC and I2S_FROM_PI), at the header, as
   box-design.md asks now that they cross a cable. I2S_TO_PI has its 33 Ω at the codec.
3. **The ID EEPROM is phase 2's**: a CAT24C32 on ID_SD and ID_SC with 3.9 kΩ pull-ups, its write
   protect pulled up through 1 kΩ and TP4 to ground it for writing, all on the Pi's 3.3 V.
4. **The RP2350 has its own 3.3 V from the 5 V** (VDD, AP2112K-3.3, about 70 mA at most). It is up
   before the Pi and stays up through the Pi's standby, so the controls and the bypass never
   depend on the Pi's 3.3 V. Everything it reads (footswitches, EXT FS, the control board, MIDI)
   is pulled up to VDD.
5. **The Pi resets and programs the RP2350.** GPIO 23 (header pin 16) drives Q1, which pulls RUN
   low while the Pi holds it high; 100 kΩ holds Q1 off, so a Pi that isn't driving it leaves the
   RP2350 running. GPIO 24 and 25 (pins 18 and 22) are its SWDIO and SWCLK, through 330 Ω: the Pi
   flashes it with OpenOCD's GPIO driver, and no debug probe is needed in the box. Its USB and
   BOOTSEL are on test pads, for recovery only.
6. **The UART to the Pi is ttyAMA0 on pins 8 and 10**, as the Pico's is today, through 1 kΩ each
   way, on the RP2350's GPIO 0 and 1, so the firmware's link keeps its pins. The RP2350's whole pin
   map is in box-design.md, "The RP2350's pins".
7. **No back-powering a Pi in standby** (HAT+): GPIO 14 reads the Pi's 3.3 V through 10 kΩ and
   100 kΩ, and the firmware keeps MCU_TX an input while it is low. The resistors on every line
   limit what reaches the Pi if the firmware gets it wrong.
8. **MIDI in is a 3.5 mm socket, Type A**: the ring is the current source (DIN 4) and the tip the
   sink (DIN 5). The ring feeds the H11L1's LED through 220 Ω, the tip takes it back, and a
   1N4148W across the LED stops a reversed lead. The sleeve is left open, as a MIDI input leaves
   the shield; it is the socket's threaded nose, nutted to the case. The H11L1 runs on VDD with a
   1 kΩ pull-up; its output is low while current flows, so the line idles high, as a UART wants.
   Its pad layout is Everlight's, read from Everlight's own datasheet: LCSC's datasheet link for
   this part is LiteOn's H11L1.
9. **The footswitches' plugs** are JST S2B-XH-A, side entry, for bought two-wire XH leads, each
   pulled up to VDD through 10 kΩ, with 1 kΩ and 100 nF at the RP2350. The switches are wired
   closed at rest (the firmware's `PRESS_OPENS`), so each draws 0.33 mA while it isn't pressed.
10. **EXT FS** is filtered on the audio board (1 kΩ, 100 nF, where it enters); its pull-ups
    (10 kΩ to VDD) and a 1 kΩ are here.
11. **The buttons' lights** are GPIO 15 and 16 through 330 Ω, to the control link's pins 12 and
    13, which the control board leaves open until the light is chosen (box-design.md, "Still to
    choose").
12. **L1's polarity.** The footprint's pad 1 is the inductor's dot (+), and pad 1 is at VREG_LX,
    so current enters at the dot. Raspberry Pi's guide asks for its own orientation exactly, so
    the layout checks it against the Pico 2's or the minimal design's files before it is placed.

## The owner's decisions that bind this board

From box-design.md, "Decided (owner, 2026-11-14)": power through the Pi board (3); the Pi 5 stays,
the Compute Module is for later (6); sockets soldered to the boards and nutted to the case (1).

## Open

1. **The 40-pin socket faces the Pi.** The Pi hangs component side down, so this board's top faces
   the Pi's top, and seen from above the socket's pins are the mirror of an ordinary HAT's. The
   footprint is placed so that pin 1 meets the Pi's pin 1, checked in the case model before the
   layout goes anywhere.
2. **Telling the Pi what this supply gives.** A Pi fed through its header can't negotiate with
   the supply, and its firmware then limits what its USB ports may draw. How a HAT+ that powers
   the Pi says how much it gives (an EEPROM setting, or the Pi's own configuration) is checked in
   Raspberry Pi's HAT+ specification before the EEPROM is written (phase 5).
3. **Which contact is tip and which is ring on the MIDI socket** was read from XKB's cut-away view:
   the spring on terminal 5 touches the plug 7 to 11 mm in, where a plug's tip is, and the one on
   terminal 2 at 3 to 5 mm, where its ring is. The drawing doesn't say it in words. A plug and a
   meter on the first part confirm it; if it is the other way round, the footprint's T and R pads
   swap.
4. **Slots drawn as round holes.** XKB draws the MIDI socket's terminals in slots (1.5 × 0.6 and
   1.5 × 0.8 mm). Konnect can't draw a slotted hole, so each is a round hole as long as the slot,
   1.5 mm, which the terminal fits. The owner may redraw them as slots in KiCad's footprint editor
   before ordering.
5. **The flat-cable sockets' current rating** is not on JUSHUO's drawing (box-board.md, Open 2).
   The audio link's 5 V is about 0.15 A on one conductor.
6. **The current into a Pi in standby** is measured at bring-up: the RP2350's SWD pins have pulls
   of their own, and a pull-up can push tens of microamps through 330 Ω into an unpowered Pi's
   GPIO.

## Footprints checked against the makers' drawings (2026-11-16)

| Part | Footprint in the schematic | Against | Result |
|---|---|---|---|
| USB-C, SHOU HAN TYPE-C 16PIN L8.35 | KiCad's `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` | SHOU HAN's drawing (on LCSC's C5379909 page) | Matches within 0.07 mm: twelve pads, the inner eight at 0.5 mm, the outer pairs 6.33 and 4.73 mm apart (6.4 and 4.8 in the footprint), the pad row 1.14 mm behind the pegs (1.075); the shell's four legs 8.64 mm across and 4.18 mm apart, in slots 1.7 and 1.4 mm long; the pegs 5.78 mm apart. The body is 8.35 mm long, about 1 mm longer at the mouth than the footprint's outline. HRO's footprint, drawn first, has 1.2 mm rear slots |
| MIDI in, XKB PJ-324M0 | `pedal-codec:Jack_3.5mm_XKB_PJ-324M0_Horizontal`, new | XKB drawing X-PJ-324M0 rev A1 | Made from its PCB layout: the five terminals where it puts them, round 1.5 mm holes for its slots (Open 4); pads named for the symbol, S, R, RN, T and TN |
| L1, Abracon AOTA-B201610S3R3-101-T | `pedal-codec:L_Abracon_AOTA-B201610`, new | Abracon's datasheet, rev A | Made from its land pattern: two 1.0 × 1.6 mm pads, 1.0 mm apart. Pad 1 is the dot |
| U5, Everlight H11L1S(TA) | KiCad's `SMDIP-6_W9.53mm` | Everlight's H11LX datasheet, "Recommended pad layout for surface mount leadform" | KiCad's pads (2.0 × 1.78 mm, rows 9.53 mm apart) cover Everlight's (1.83 × 1.71 mm, 9.24 mm) except 0.06 mm at the inner edge. Everlight calls its layout a reference |

The rest are standard packages in KiCad's own footprints: the RP2350A's QFN-60 with its 3.4 mm
pad, the SOIC-8s, SOT-23 and SOT-23-5, the 3225 crystal, SMA, a 1206 fuse, the 2 × 20 socket, and
the JST and JUSHUO sockets, whose footprints KiCad names for those parts. The JUSHUO one was
checked for the audio board (box-board.md).

## Power

All from the USB-C socket's 5 V. The Pi takes most of it; the audio board about 0.15 A over the
link; the RP2350 side, through U4, about 70 mA at most (the RP2350, the optocoupler, the pull-ups
and the lights), which U4 drops to 3.3 V with about 0.12 W.

| Rail | From | Feeds |
|---|---|---|
| +5V | USB-C, through F1 | The Pi (header pins 2 and 4), the audio board (link pin 16), U4 |
| VDD | +5V, U4 | The RP2350, its flash, the optocoupler, every pull-up, the control board (control link pin 16) |
| DVDD | The RP2350's own regulator, L1 | Its core |
| +3V3 | The Pi | The ID EEPROM, the audio board (link pin 14), the RP2350's sense of it |

## Parts

All from JLCPCB's parts list; checked there on 2026-11-16 (stock again before ordering).

| Qty | Value | MPN | LCSC | Where |
|---|---|---|---|---|
| 1 | USB-C socket, 16 contacts | TYPE-C 16PIN L8.35 | C5379909 | J1 |
| 1 | 2 × 20 socket, 8.5 mm | 2.54-2*20 | C2977589 | J2 |
| 2 | Flat-cable socket, 16-way 1.0 mm | AFA07-S16FCC-00 | C13744 | J3, J4 |
| 3 | JST XH, 2-way, side entry | S2B-XH-A(LF)(SN) | C157931 | J5–J7 |
| 1 | 3.5 mm stereo socket | PJ-324M0 | C2884986 | J8 |
| 1 | RP2350A | RP2350A | C42411118 | U2 |
| 1 | 32 Mbit flash | W25Q32JVSSIQ | C179173 | U3 |
| 1 | 3.3 V LDO, 600 mA | AP2112K-3.3TRG1 | C51118 | U4 |
| 1 | ID EEPROM | CAT24C32WI-GT3 | C81193 | U1 |
| 1 | Optocoupler, Schmitt output | H11L1S(TA) | C78589 | U5 |
| 1 | 12 MHz crystal | ABM8-272-T3 | C20625731 | Y1 |
| 1 | 3.3 µH, polarity marked | AOTA-B201610S3R3-101-T | C42411119 | L1 |
| 1 | Fuse, 4 A fast, 1206 | 0466004.NRHF | C187596 | F1 |
| 1 | TVS, 5 V | SMAJ5.0A/TR13 | C78401 | D1 |
| 1 | 1N4148W | 1N4148W | C81598 | D2 |
| 1 | 2N7002 | 2N7002 | C8545 | Q1 |
| 1 | 100 µF 16 V | RVT100UF16V67RV0016 | C2887276 | C1 |
| 3 | 10 µF 0805 | CL21A106KAYNNNE | C15850 | C2, C4, C25 |
| 2 | 1 µF | CL10A105KA8NNNC | C5673 | C6, C7 |
| 3 | 4.7 µF 0402 | CL05A475MP5NRNC | C23733 | C16–C18 |
| 5 | 100 nF 0603 | CC0603KRX7R9BB104 | C14663 | C5, C26–C29 |
| 12 | 100 nF 0402 | CL05B104KO5NNNC | C1525 | C8–C15, C19–C22 |
| 1 | 10 nF | 0603B103K500NT | C57112 | C3 |
| 2 | 15 pF C0G | 0402CG150J500NT | C1548 | C23, C24 |
| 2 | 27 Ω | 0402WGF270JTCE | C25100 | R14, R15 |
| 1 | 33 Ω 0402 | 0402WGF330JTCE | C25105 | R10 |
| 3 | 33 Ω 0603 | 0603WAF330JT5E | C23140 | R4–R6 |
| 1 | 220 Ω | 0603WAF2200T5E | C22962 | R37 |
| 4 | 330 Ω | 0603WAF3300T5E | C23138 | R21, R22, R35, R36 |
| 2 | 1 kΩ 0402 | 0402WGF1001TCE | C11702 | R17, R18 |
| 10 | 1 kΩ 0603 | 0603WAF1001T5E | C21190 | R9, R12, R19, R20, R25, R27, R29, R31, R33, R38 |
| 2 | 3.9 kΩ | 0603WAF3901T5E | C23018 | R7, R8 |
| 2 | 5.1 kΩ | 0402WGF5101TCE | C25905 | R1, R2 |
| 2 | 10 kΩ 0402 | 0402WGF1002TCE | C25744 | R11, R16 |
| 6 | 10 kΩ 0603 | 0603WAF1002T5E | C25804 | R23, R26, R28, R30, R32, R34 |
| 2 | 100 kΩ | 0603WAF1003T5E | C25803 | R13, R24 |
| 1 | 1 MΩ | 0603WAF1004T5E | C22935 | R3 |

86 parts, four holes (H1–H4) and ten test pads (TP1–TP10).
