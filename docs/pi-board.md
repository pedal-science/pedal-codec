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
| USB-C power and the Pi header | J1, the USB-C socket, with D1 (SMAJ5.0A), 10 µF, 5.1 kΩ on each CC, each CC's tap to the RP2350 (10 kΩ, 100 nF), and the shell's 1 MΩ ‖ 10 nF; U6, the eFuse (TPS259470A) that feeds the Pi's 5 V, with its divider, current-limit resistor and slew capacitor, and 100 µF after it; J2, the Pi's 40-pin socket, with 33 Ω on the three I2S lines the Pi drives; U1, the ID EEPROM; J9, the fan's plug, with Q2, which the Pi switches it by; four M2.5 holes |
| RP2350 | U4 (AP2112K-3.3), the RP2350's own 3.3 V (VDD); U2, the RP2350A, laid out as Raspberry Pi's minimal design: decoupling, VREG_AVDD's 33 Ω and 4.7 µF, L1 and the core supply's capacitors, U3 (W25Q32JV flash), Y1 (12 MHz, 15 pF, 1 kΩ); Q1, through which the Pi resets it; USB and BOOTSEL to test pads; the resistors to the Pi's UART and SWD; the Pi's 3.3 V sense; the two CC taps on ADC0 and ADC1 |
| Links, footswitches and MIDI | J3, the audio link, in box-design.md's pin order; J4, the control link; J5–J7, the footswitches' plugs, with their pull-ups and filters; EXT FS's pull-ups; the two lamps' resistors; J8, MIDI in, with U5 (H11L1) |

Checked on 2026-11-16, again after the eFuse went in, and again after the supply sensing and the fan went in the same day:

| Check | Result |
|---|---|
| KiCad ERC, every severity (`kicad-cli sch erc --severity-all`, and Konnect's `run_erc`) | 0 errors, 0 warnings |
| Sheet pins (Konnect's `validate_sheet_pins`) | 0 issues; the sheets join by global labels |
| Netlist (`kicad-cli sch export netlist`) | 122 nets, none with one pin. Every pin left open is a flagged no-connect: the USB-C's data and SBU pins, U6's FLT, AUXOFF and ITIMER, the Pi's unused GPIO, the RP2350's GPIO 17–25, 28 and 29, U4's NC pin, U5's pin 3, the MIDI socket's sleeve and two break contacts, the control link's pin 14 |
| `LCSC`, `MPN` and a footprint on every symbol | 115 of 115 (the four holes and ten test points carry `none`, as in phase 2) |
| Every LCSC number against JLCPCB's parts list (Konnect's copy) | Each is the MPN and package the schematic says, and in stock |

## Decided while drawing

1. **Power: any USB-C supply gives 5 V, and nothing is negotiated.** 5.1 kΩ on each CC asks for 5 V;
   the source's own advertisement sets the current, 3 A from a 3 A supply. The Pi is fed through
   its header's 5 V pins (box-design.md, "Power", decided by the owner), which makes this a
   **Power HAT+** in Raspberry Pi's HAT+ specification (chapters 4 and 6). That asks for two
   things the first draft lacked, and USB-C asks a third, so U6 went in on 2026-11-16, in place of
   a 4 A fuse:
   - *It must only source current, and survive the Pi's own USB-C supply being plugged in too.*
     U6, TI's TPS259470A eFuse, has back-to-back FETs: current flows from the USB-C socket to the
     Pi and never back, so a supply on the Pi's own socket can't drive this one's.
   - *At least 3 A at 5.1 V.* U6's 28 mΩ costs about 0.09 V at 3 A, where a Schottky diode would
     cost 0.4 V; the supply's own voltage is the rest. A Raspberry Pi 27 W
     supply gives 5.1 V; an ordinary 5 V one leaves the Pi about 4.9 V at full load.
   - *USB-C's limit of 10 µF across a power sink's VBUS*, which the Pi and the audio board's
     hundreds of µF would break: U6 starts slowly (2.2 nF on DVDT, about 5 ms to 5 V), so only
     C1's 10 µF is on the socket at plug-in; the 100 µF is after U6.

   U6's settings, from TI's equations: on above 4.36 V and off above 6.13 V (100 kΩ, 11 kΩ,
   27 kΩ from VBUS on EN/UVLO and OVLO); current limit about 4 A (820 Ω on ILM, 3334 / R);
   ITIMER open, so it limits at once; FLT and AUXOFF unused. D1, a 5 V TVS, stays at the socket.
   The shell goes to ground through 1 MΩ ‖ 10 nF, so a cable's shield is tied to ground at radio
   frequencies but never joins ground to the case at DC; the guitar socket stays the one bond.
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
11. **The buttons' lamps** are GPIO 15 and 16 through 330 Ω, to the control link's pins 12 and
    13. The lamps are on the control board (control-board.md, Decided 5): red, 2.0 V, so each
    takes about 4 mA.
12. **L1's polarity.** The footprint's pad 1 is the inductor's dot (+), and pad 1 is at VREG_LX,
    so current enters at the dot. Raspberry Pi's guide asks for its own orientation exactly, so
    the layout checks it against the Pico 2's or the minimal design's files before it is placed.
13. **The ID EEPROM's address, and what the overlay tells the Pi.** The board uses GPIO 2–27, so its
    EEPROM is the HAT+ Standard class at 0x50 (A0–A2 to ground, as drawn); the Power HAT+
    addresses, 0x52 and 0x53, are only for boards that use none of those GPIO. The overlay, written
    in phase 5, tells the Pi what the supply gives, as the specification's section 4.2 shows:
    `hat_current_supply = <3000>` (mA) in a `/chosen/power` node.
14. **The flat-cable sockets** carry 0.5 A a contact (LCSC's listing for the AFA07 series; JUSHUO's
    drawing gives no rating). The audio link's 5 V is about 0.15 A, on pin 16 alone.

15. **The board reads what the supply offers** (the owner, 2026-11-16: "warn when the supply is
    poor"). A USB-C source says how much current it gives by the voltage it puts across the
    sink's 5.1 kΩ, on whichever CC line the cable connects: 0.25 to 0.61 V for the USB default
    (0.5 or 0.9 A), 0.70 to 1.16 V for 1.5 A, 1.31 to 2.04 V for 3 A (USB Type-C specification,
    the sink's vRd thresholds). Each CC line goes through 10 kΩ, with 100 nF to ground, to an ADC
    pin of the RP2350: CC1 to GPIO 26, CC2 to GPIO 27. The 10 kΩ draws nothing at DC, so the
    5.1 kΩ stays what the source sees; the capacitor smooths the chatter of a supply that speaks
    Power Delivery, which this board doesn't answer. The firmware reads the higher of the two
    and tells the Pi, which warns on the screen when it is under 3 A; the message is the
    firmware's and the pedal service's work, at bring-up. What the supply does under load is a
    separate reading the Pi already has: its own measure of its 5 V (`vcgencmd pmic_read_adc`)
    and its under-voltage flag.
16. **A fan, switched by the Pi** (the owner, 2026-11-16: assume one is needed). J9 is a two-way
    JST XH plug for a two-wire 5 V fan, pin 1 at +5 V; Q2 (AO3400A) switches its other wire to
    ground, with a 1N4148W across the fan and 10 µF beside it. The Pi's GPIO 12 (header pin 32)
    drives Q2's gate through 1 kΩ, with 100 kΩ to ground, so the fan is off whenever the Pi
    isn't driving it. GPIO 12 because it is one of the Pi's hardware PWM pins: the kernel's
    `gpio-fan` overlay turns the fan on above a temperature, and `pwm-fan` could vary it later
    with no change here. The Pi's own fan header wants a four-wire fan with its small plug, and the ones
    found for it are 30 mm and four-wire. Since 2026-11-17 the fan is one 30 mm two-wire fan lying
    on the base plate just in front of this board, between footswitches 1 and 2, drawing air in
    (box-design.md, "Heat"), so J9 at the board's front edge is beside it. Nothing goes from the
    5 V to the Pi's pins through this: the gate is the only thing GPIO 12 touches.

## The owner's decisions that bind this board

From box-design.md, "Decided (owner, 2026-11-14)": power through the Pi board (3); the Pi 5 stays,
the Compute Module is for later (6); sockets soldered to the boards and nutted to the case (1).

## Open

1. **The 40-pin socket faces the Pi.** The Pi hangs component side down, so this board's top faces
   the Pi's top, and seen from above the socket's pins are the mirror of an ordinary HAT's. The
   footprint is placed so that pin 1 meets the Pi's pin 1, checked in the case model before the
   layout goes anywhere.
2. **A supply that gives less than 3 A: answered 2026-11-16.** The owner asked for the warning,
   so the RP2350 reads both CC lines (Decided 15). The Pi is still told 3 A (Decided 13); the
   warning is how a smaller supply shows.
3. **Which contact is tip and which is ring on the MIDI socket** was read from XKB's cut-away view:
   the spring on terminal 5 touches the plug 7 to 11 mm in, where a plug's tip is, and the one on
   terminal 2 at 3 to 5 mm, where its ring is. The drawing doesn't say it in words. A plug and a
   meter on the first part confirm it; if it is the other way round, the footprint's T and R pads
   swap.
4. **Slots drawn as round holes.** XKB draws the MIDI socket's terminals in slots (1.5 × 0.6 and
   1.5 × 0.8 mm). Konnect can't draw a slotted hole, so each is a round hole as long as the slot,
   1.5 mm, which the terminal fits. The owner may redraw them as slots in KiCad's footprint editor
   before ordering.
5. **The current into a Pi in standby** is measured at bring-up: the RP2350's SWD pins have pulls
   of their own, and a pull-up can push tens of microamps through 330 Ω into an unpowered Pi's
   GPIO.

## Footprints checked against the makers' drawings (2026-11-16)

| Part | Footprint in the schematic | Against | Result |
|---|---|---|---|
| USB-C, SHOU HAN TYPE-C 16PIN L8.35 | KiCad's `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` | SHOU HAN's drawing (on LCSC's C5379909 page) | Matches within 0.07 mm: twelve pads, the inner eight at 0.5 mm, the outer pairs 6.33 and 4.73 mm apart (6.4 and 4.8 in the footprint), the pad row 1.14 mm behind the pegs (1.075); the shell's four legs 8.64 mm across and 4.18 mm apart, in slots 1.7 and 1.4 mm long; the pegs 5.78 mm apart. The body is 8.35 mm long, about 1 mm longer at the mouth than the footprint's outline. HRO's footprint, drawn first, has 1.2 mm rear slots |
| MIDI in, XKB PJ-324M0 | `pedal-codec:Jack_3.5mm_XKB_PJ-324M0_Horizontal`, new | XKB drawing X-PJ-324M0 rev A1 | Made from its PCB layout: the five terminals where it puts them, round 1.5 mm holes for its slots (Open 4); pads named for the symbol, S, R, RN, T and TN |
| L1, Abracon AOTA-B201610S3R3-101-T | `pedal-codec:L_Abracon_AOTA-B201610`, new | Abracon's datasheet, rev A | Made from its land pattern: two 1.0 × 1.6 mm pads, 1.0 mm apart. Pad 1 is the dot |
| U6, TI TPS259470ARPWR | `pedal-codec:Texas_RPW0010A_VQFN-HR-10_2x2mm_P0.45mm`, new | TI's RPW0010A example board layout and stencil (4225183/A) in the TPS25947 datasheet | Made from them: the L-shaped corner pads as two rectangles each, the IN and OUT bars 0.3 × 2.4 mm, paste as TI's stencil. KiCad has neither this footprint nor the symbol, which is in `pedal-codec.kicad_sym` |
| U5, Everlight H11L1S(TA) | KiCad's `SMDIP-6_W9.53mm` | Everlight's H11LX datasheet, "Recommended pad layout for surface mount leadform" | KiCad's pads (2.0 × 1.78 mm, rows 9.53 mm apart) cover Everlight's (1.83 × 1.71 mm, 9.24 mm) except 0.06 mm at the inner edge. Everlight calls its layout a reference |

The rest are standard packages in KiCad's own footprints: the RP2350A's QFN-60 with its 3.4 mm
pad, the SOIC-8s, SOT-23 (Q1, and Q2, whose gate, source and drain are pins 1, 2 and 3 as KiCad's
AO3400A symbol has them) and SOT-23-5, the 3225 crystal, SMA, the 2 × 20 socket, and
the JST (J5–J7 and the fan's J9) and JUSHUO sockets, whose footprints KiCad names for those parts. The JUSHUO one was
checked for the audio board (box-board.md).

## kicad-happy's analysis (2026-11-16)

kicad-happy 2.3.1's `analyze_schematic.py` and its ngspice pass, on the board as it is now (with
U6, the CC taps and the fan): 1 error, 4 warnings, 51 info findings; 22 subcircuits simulated
(the dividers, filters, the crystal's load), all pass. Answered:

| Finding (rule) | Answer |
|---|---|
| U2's VREG_AVDD has no DC path to a power rail (PP-001, error) | It is fed from VDD through R18, 33 Ω, with C21, 4.7 µF: the RC filter Raspberry Pi's guide asks for. VREG_AVDD draws about 200 µA, so R18 drops about 7 mV. The analyzer accepts only 0 Ω, inductors and ferrites as a supply path. Not an issue |
| CC1 and CC2 "missing 5.1 kΩ pull-down" (UC-003, two warnings, new with the CC taps) | Each has it: R5 and R7, 5.1 kΩ from the CC line to ground, read from KiCad's netlist. The analyzer stops seeing them as pull-downs now that each line also has a 10 kΩ tap, and reads the pair as a divider |
| J8, the MIDI socket, has no ground pin (CG-AUD) | By design: a MIDI input leaves the shield open, and the current loop goes through the optocoupler's LED, with nothing referred to this board's ground |
| No `datasheets/` directory (DS-002) | As for the audio board (box-board.md) |
| Twelve nets "with one pin": SDA, SCL, I2S_TO_PI, the fan's line and the Pi's UART, SWD and RUN lines (NT-001, info) | The analyzer doesn't count the 40-pin socket's pins (J2), as in phase 2's review. KiCad's own netlist has J2 on each of them and no net with one pin |
| U6 taken for an LDO (PR-DET, info) | It is the eFuse; nothing to answer |

## Power

All from the USB-C socket's 5 V, through U6. The Pi takes most of it; the audio board about 0.15 A over the
link; the fan about 70 mA while it runs; the RP2350 side, through U4, about 70 mA at most (the
RP2350, the optocoupler, the pull-ups and the lamps), which U4 drops to 3.3 V with about 0.12 W.

| Rail | From | Feeds |
|---|---|---|
| VBUS | The USB-C socket | U6, D1 and C1 (10 µF) only |
| +5V | VBUS, through U6 | The Pi (header pins 2 and 4), the audio board (link pin 16), U4, the fan (J9); C3 (100 µF) |
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
| 4 | JST XH, 2-way, side entry | S2B-XH-A(LF)(SN) | C157931 | J5–J7, J9 |
| 1 | 3.5 mm stereo socket | PJ-324M0 | C2884986 | J8 |
| 1 | eFuse, 5.5 A, reverse blocking | TPS259470ARPWR | C3662799 | U6 |
| 1 | RP2350A | RP2350A | C42411118 | U2 |
| 1 | 32 Mbit flash | W25Q32JVSSIQ | C179173 | U3 |
| 1 | 3.3 V LDO, 600 mA | AP2112K-3.3TRG1 | C51118 | U4 |
| 1 | ID EEPROM | CAT24C32WI-GT3 | C81193 | U1 |
| 1 | Optocoupler, Schmitt output | H11L1S(TA) | C78589 | U5 |
| 1 | 12 MHz crystal | ABM8-272-T3 | C20625731 | Y1 |
| 1 | 3.3 µH, polarity marked | AOTA-B201610S3R3-101-T | C42411119 | L1 |
| 1 | TVS, 5 V | SMAJ5.0A/TR13 | C78401 | D1 |
| 2 | 1N4148W | 1N4148W | C81598 | D2, D3 |
| 1 | 2N7002 | 2N7002 | C8545 | Q1 |
| 1 | AO3400A (N-channel, on at 2.5 V) | AO3400A | C20917 | Q2 |
| 1 | 100 µF 16 V | RVT100UF16V67RV0016 | C2887276 | C3 |
| 4 | 10 µF 0805 | CL21A106KAYNNNE | C15850 | C1, C6, C8, C29 |
| 2 | 1 µF | CL10A105KA8NNNC | C5673 | C10, C11 |
| 3 | 4.7 µF 0402 | CL05A475MP5NRNC | C23733 | C20–C22 |
| 7 | 100 nF 0603 | CC0603KRX7R9BB104 | C14663 | C4, C5, C9, C30–C33 |
| 12 | 100 nF 0402 | CL05B104KO5NNNC | C1525 | C12–C19, C23–C26 |
| 1 | 10 nF | 0603B103K500NT | C57112 | C7 |
| 1 | 2.2 nF | 0603B222K500NT | C1604 | C2 |
| 2 | 15 pF C0G | 0402CG150J500NT | C1548 | C27, C28 |
| 2 | 27 Ω | 0402WGF270JTCE | C25100 | R22, R23 |
| 1 | 33 Ω 0402 | 0402WGF330JTCE | C25105 | R18 |
| 3 | 33 Ω 0603 | 0603WAF330JT5E | C23140 | R12–R14 |
| 1 | 220 Ω | 0603WAF2200T5E | C22962 | R45 |
| 4 | 330 Ω | 0603WAF3300T5E | C23138 | R29, R30, R43, R44 |
| 1 | 820 Ω | 0603WAF8200T5E | C23253 | R4 |
| 2 | 1 kΩ 0402 | 0402WGF1001TCE | C11702 | R25, R26 |
| 11 | 1 kΩ 0603 | 0603WAF1001T5E | C21190 | R9, R17, R20, R27, R28, R33, R35, R37, R39, R41, R46 |
| 2 | 3.9 kΩ | 0603WAF3901T5E | C23018 | R15, R16 |
| 2 | 5.1 kΩ | 0402WGF5101TCE | C25905 | R5, R7 |
| 2 | 10 kΩ 0402 | 0402WGF1002TCE | C25744 | R19, R24 |
| 8 | 10 kΩ 0603 | 0603WAF1002T5E | C25804 | R6, R8, R31, R34, R36, R38, R40, R42 |
| 1 | 11 kΩ | 0603WAF1102T5E | C25950 | R2 |
| 1 | 27 kΩ | 0603WAF2702T5E | C22967 | R3 |
| 4 | 100 kΩ | 0603WAF1003T5E | C25803 | R1, R10, R21, R32 |
| 1 | 1 MΩ | 0603WAF1004T5E | C22935 | R11 |

101 parts, four holes (H1–H4) and ten test pads (TP1–TP10).
