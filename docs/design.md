# pedal-codec: design

Started 2026-11-11. This is the design as far as it has been reasoned, with every open question
marked **Open**. [plan.md](plan.md) is the order in which they are settled and the board is made.

## What was asked for (owner, 2026-11-11)

- A board like Raspberry Pi's [Codec Zero](https://www.raspberrypi.com/documentation/accessories/audio.html)
  in size (Pi Zero size, 65 × 30 mm); a full-size HAT (65 × 56.5 mm) is fine too.
- The codec is TI's [TAC5242](https://www.ti.com/product/TAC5242).
- **Two analogue inputs** on JST XH 2-pin connectors, each switchable between **Instrument** and
  **Line**, each with **optional +48 V**.
- **Two analogue outputs** on JST XH 2-pin connectors, line level.
- Power, digital audio and control through the Pi's header, GPIO pins included.
- Supporting parts as needed: an LDO for the supply, op-amps for the instrument inputs, a phantom
  supply, passives.

## Decided (owner, 2026-11-11)

1. **Each input is a combo jack whose two halves are wired separately**: the XLR to an XH 3-pin
   (ground, hot, cold), the ¼″ to an XH 4-pin (sleeve, tip, ring, insert switch). This replaces the
   single XH 3-pin per input decided earlier the same day. The outputs stay on XH 2-pin,
   unbalanced.
2. **Each input has three modes**, Instrument, Line and Mic, with Mic on its own preamp. **Which
   half of the jack holds a plug chooses the path**, ¼″ or XLR; one panel switch per input chooses
   Line against the other mode (Instrument on the ¼″, Mic on the XLR).
3. **v1 is a full-size HAT+** (65 × 56.5 mm).
4. **The op-amps run from the Pi's 5 V, filtered.** No boost for an analogue rail; the only boost
   on the board is the phantom supply's.
5. **The modes and phantom power are under the player's physical control**: panel switches, not
   the Pi. Phantom power has a switch and an LED per input, reaches only the XLR pins, and is never
   switched on automatically or by software. The Pi reads every switch and the plug detection, so
   software can show the state, but it can't change it.

Why not detect everything (asked 2026-11-11): the board can tell which half of the jack is in use,
TS from TRS, a passive pickup's few kΩ from a dynamic mic's 150–600 Ω, and, once phantom is on,
whether something draws current. It can't tell an active guitar from a line output (both look
like a coupling capacitor, but a wrong guess there only costs level), and it can't tell whether a
device will tolerate 48 V before applying it, which is the guess that does damage. So the plug
chooses the path, the player chooses the rest, and phantom is always a deliberate switch.

## What the TAC5242 changes

Read from the datasheet, [SLASF27A](https://www.ti.com/lit/gpn/TAC5242) (November 2024).

**It is pin-controlled, with no I2C or SPI.** Six mode pins (MD0–MD5) set everything, and they
must be stable before the audio clocks start. So there are no registers, no mixer, no analogue
gain and no digital volume: whatever level the codec sees is set by the circuit in front of it.

| Pin | Setting it carries (target mode) | Choice for v1 |
|---|---|---|
| MD0 (multi-level) | Target/controller, I2S/TDM/LJ: GND = target I2S; AVDD = controller I2S; 4.7 k or 22 k for TDM and LJ | GND (target I2S), with a solder-jumper option for controller I2S |
| MD2, MD1 | AVDD 3.3 V or 1.8 V, word length 24/32, linear-phase or low-latency filters | Solder jumpers; default 0,0 (3.3 V, 32-bit, linear phase), option 1,1 (low-latency) |
| MD3 | I2S target: ADC high-pass 1 Hz or 12 Hz, and input-capacitor quick charge. Controller: the reference clock input (CCLK) | Low (1 Hz); footprint for a local oscillator on it for controller mode |
| MD5, MD4 | Input and output configuration together | 0,0: differential input, AC-coupled; differential line output |

**Inputs and outputs are configured together.** MD5/MD4 = 0,0 gives the best figures (119 dB
dynamic range in, 120 dB out) and is differential at both ends; single-ended mode (1,0) costs
9–10 dB of dynamic range at both ends. So the codec runs differential, and the board converts:
single-ended or balanced sources to differential at the inputs, differential to single-ended at the
outputs.

**Fixed full scale and a low input impedance.** At AVDD = 3.3 V, full scale is **2 Vrms
differential (+8.2 dBu)** in and out. VREF is 2.75 V and needs AVDD ≥ 3 V. Each input pin is
**5 kΩ ±20%**, so every source must be buffered, and the AC-coupling capacitors are sized against
5 kΩ (10 µF gives 3.2 Hz).

**It needs no MCLK.** In target mode its PLL locks to BCLK and FSYNC alone (BCLK/FSYNC from 16 to
512; 64 × 48 kHz = 3.072 MHz, which the Pi's I2S produces). That is the difference from the WM8960
board in the pedal now, whose 24 MHz oscillator forces the codec to be clock master. Here either
side can be master: the Pi (simplest), or the codec, from a local low-jitter oscillator on MD3
(CCLK/256 = FSYNC, so 12.288 MHz for 48 kHz). The board offers both, so the two can be measured.

**Latency.** The filters' group delay, at 48 kHz:

| Filters | ADC | DAC | Round trip |
|---|---|---|---|
| Linear phase | 16.1 samples | 17.6 samples | ≈ 0.70 ms |
| Low latency | 6.5 samples | 6.6 samples | ≈ 0.27 ms |

For a guitar pedal the low-latency filters are the likely choice; v1 measures both.

**Other pins.** DREG (1.55 V internal regulator) and VREF each need their own capacitor (VREF ≥ 1 µF,
no load). MICBIAS gives 2.75 V at up to 5 mA, for electret capsules; it is not phantom power. GPO
is a latched interrupt for a clock error. Supplies may come up in either order, ramping slower than
0.1 V/µs, with ≥ 100 ms between power-down and power-up.

**A software-controlled twin.** The [TAC5212](https://www.ti.com/product/TAC5212) is pin-for-pin
compatible, controlled over I2C or SPI, with programmable channel gain, digital volume, a
programmable MICBIAS (to 3 V) and a TI Linux driver (TAC5X1X-LINUX-DRIVER). **Open:** whether to
lay the board out so either part fits, with the MD pins' straps and an I2C route as alternatives.
Phase 1 checks the TAC5212's pin functions before deciding.

**Availability.** LCSC lists the TAC5242IRGER as C47122155, about 2,900 in stock and $6–8 each
when searched on 2026-11-11, from cached pages: check again before phase 2 and before ordering. A
Zynthian forum thread from 2024 reported it hard to get.

## Size

Pi Zero size (65 × 30 mm, holes on 58 × 23 mm) is not realistic for the first board. Two phantom
feeds need four 63 V coupling capacitors and a high-voltage boost converter with its inductor; add
two mode relays, four buffers or differential drivers, two output stages and four XH connectors,
and that is more than the 30 mm strip beside the header holds on one side.

**v1 is a full-size HAT+ (65 × 56.5 mm, M2.5 holes on 58 × 49 mm)** (decided), with room for test
points and alternative footprints. A Zero-size board can follow once v1 has shown which options
are needed.

## Connectors

**Phantom power needs three wires.** P48 (IEC 61938) feeds +48 V through matched 6.81 kΩ resistors
to both signal conductors, hot and cold, and returns it on the screen, pin 1 of the XLR. So the
XLR half needs three pins of its own, and keeping the ¼″ half on separate pins is what keeps
+48 V off anything plugged into it.

| Connector | Part | Pins |
|---|---|---|
| IN 1 XLR, IN 2 XLR | JST XH 3-pin (B3B-XH-A) | 1 ground (XLR 1), 2 hot (XLR 2), 3 cold (XLR 3) |
| IN 1 ¼″, IN 2 ¼″ | JST XH 4-pin (B4B-XH-A) | 1 sleeve, 2 tip, 3 ring, 4 insert switch |
| OUT 1, OUT 2 | JST XH 2-pin (B2B-XH-A) | 1 ground, 2 signal |
| PANEL | One connector, part chosen in phase 2 (about 10 pins) | Ground, both inputs' Line switches, both phantom switches, both phantom LEDs |

**The combo jack** needs a switching contact on its ¼″ side, **isolated** from the tip. A contact
normalled to the tip would put the detection's pull-up on the 1 MΩ instrument node. Neutrik's NCJ6
family has switching versions; phase 1 picks the part and checks the contact. A combo jack takes
only one plug at a time, so the board never has to choose between two.

**v1 also carries the panel's switches on the board**: small slide switches wired in parallel with
the PANEL connector, so the board can be tested on the bench with nothing attached.

## Blocks

```
Pi header ─ 5 V ─┬─ load switch (EN from 3.3 V) ─ ferrite + LC ─ analogue 5 V ─ op-amps
                 │                                              └─ RC-filtered, buffered mid-rail (≈ 2.45 V)
                 ├─ relay coils (own filter branch)
                 ├─ filter ─ low-noise LDO (EN from 3.3 V) ─ 3.3 V AVDD ─ TAC5242
                 └─ boost, ≥ 60 V switch ─ filter ─ +48 V ─ per-input switch ─ 6.81 k ×2 ─ XLR only
          3.3 V ─ IOVDD, EEPROM, switch and detect logic
          I2S (GPIO 18–21) ─ BCLK, FSYNC, DIN, DOUT

¼″ tip ────── 1 MΩ ─ JFET buffer ─────────────┐ KA          ┐
XLR 2/3 ─ 47 µF ×2 ─ mic preamp, ≈ 20 dB ─────┘ (plug)  ─ L ├ KB (Line switch) ─ FDA ─ 10 µF ─ IN1P/M
¼″ tip/ring ─────────────────────────────────┐ KA          │
XLR 2/3 (after the 47 µF) ───────────────────┘ (plug) ─ Line ┘

OUT1P/M ─ differential-to-single-ended stage ─ mute ─ 10 µF ─ 100 Ω ─ XH out (100 k bleed)
```

### Input

Each input has two signal paths, one per half of the jack, and two choices:

| Plug in | Line switch | Mode | Path into the FDA |
|---|---|---|---|
| ¼″ | off | **Instrument** | Tip, 1 MΩ, JFET buffer |
| ¼″ | on | **Line** | Tip and ring, balanced or (TS lead, ring grounded) unbalanced |
| XLR (or nothing) | off | **Mic** | Phantom feed, 47 µF ×2, mic preamp |
| XLR | on | **Line** | Hot and cold after the 47 µF, e.g. a balanced line output or an active DI |

- **KA follows the plug.** The ¼″ insert switch drives it, through a transistor; the Pi reads the
  same signal. It selects both the low-level stage (the instrument buffer or the mic preamp) and
  the pair the Line path takes (¼″ tip and ring, or the XLR's hot and cold). Four poles: two DPDT
  relays driven together.
- **KB follows the Line switch.** It chooses between the low-level stage and the Line pair, into
  the FDA's input resistors. One DPDT relay.
- **No contact touches the 1 MΩ node.** The instrument buffer sits on the ¼″ tip permanently and
  KA switches its *output*, so the noise-sensitive node never runs through a relay or out to the
  panel. The panel switches carry DC only.
- **Relays or analogue switches** for KA's low-level half: those nodes are buffered and low
  impedance, so an analogue switch would do there; the Line pair is the raw source, which can
  swing beyond a 5 V switch's rails, so it stays on a relay. Phase 1 decides.
- **Defaults.** With no plug, or with the Pi in standby (3.3 V off, so the logic is low), the input
  is in Mic mode on the XLR with phantom off unless its switch is on.
- **Software control, as an option.** A solder jumper per input lets a GPIO drive KB instead of the
  Line switch, if rigs should ever choose Instrument or Line. Phantom has no such option.

The stages:

- **Instrument:** 1 MΩ to the mid-rail, a JFET-input rail-to-rail op-amp (the pedal's buffer uses
  the OPA2197, which runs from 4.5 V), then the fully differential amplifier (FDA) into the codec.
  On the 5 V rail the buffer swings about 4.8 Vpp (1.7 Vrms, +6.8 dBu), which is ample for passive
  pickups and the edge for the hottest active ones; the FDA's gain maps that onto the codec's
  2 Vrms full scale.
- **Line:** the selected pair into the FDA wired inverting, so the source sees its input
  resistors (≥ 10 kΩ per leg) and the op-amp's own inputs sit at the mid-rail whatever the
  source does. Gain about −6 dB, so +4 dBu nominal has 10 dB of headroom (clip about +14 dBu) on a
  5 V rail.
- **Mic:** a low-noise differential preamp (two op-amps as the first stage of an instrumentation
  amplifier, unity common-mode gain), biased at mid-rail after the phantom coupling capacitors,
  then the FDA. Input impedance about 2 kΩ, as microphones expect.
- **The FDA** is shared by all modes (OPA1637 is the candidate: 3–36 V supply, rail-to-rail
  output, made for driving audio ADCs), its output common mode set to the mid-rail, and AC-coupled
  into the codec (10 µF against 5 kΩ: 3.2 Hz).

**Why the mic gain can be fixed at about 20 dB.** The codec's own noise is about 2.2 µVrms
A-weighted (119 dB below 2 Vrms), which is −110.8 dBu. Referred to the mic input through 20 dB of
gain it is −130.8 dBu, about the thermal noise of the microphone's own 150 Ω (−131 dBu over 20 Hz–
20 kHz). More gain buys almost no noise and costs headroom. At 20 dB the input clips at −12 dBu,
which a typical condenser (10 mV/Pa) reaches at about 120 dB SPL. So the preamp has a fixed gain,
about 20 dB, chosen exactly in phase 1 by simulating the whole chain's noise, and the 5 V rail is
no limit for signals that small. A louder source goes in on the XLR with the Line switch on.

**The preamp's op-amps on 5 V.** The candidates need a low voltage noise (≤ 3 nV/√Hz, since the
source is 150 Ω), a supply down to 4.5 V and an input common-mode range that includes 2.45 V with
the signal around it: OPA1612 (1.1 nV/√Hz, but its inputs need 2 V from each rail, which leaves
±0.5 V on 5 V: enough at mic level, checked in phase 1), OPA1656 (2.9 nV/√Hz, rail-to-rail
output). Phase 1 picks by simulation and LCSC stock.

### Phantom power

- One boost converter from 5 V to about 52 V with a ≥ 60 V switch, post-filtered (LC, then a
  capacitance multiplier or a high-voltage LDO) to 48 V ± 4 V, switching far above audio. It runs
  only while either input's phantom switch is on.
- Per input: a high-side switch, a slow ramp to keep the switch-on thump small, 6.81 kΩ 0.1%
  matched pair, 47 µF 63 V coupling capacitors on hot and cold, and the usual protection against a
  shorted or hot-plugged XLR (series resistors and clamps to the rails), in front of both the Mic
  preamp and the XLR's Line path.
- **Only the panel turns it on.** The phantom switch's DC line, ANDed with the 3.3 V rail (so the
  Pi's standby turns it off), enables that input's high-side switch. No GPIO is in that path.
- **It only reaches the XLR pins.** The ¼″ contacts have no connection to the feed, so a guitar or
  an unbalanced device on the ¼″ can't receive it whatever the switches say. With a ¼″ plug in, the
  XLR contacts are empty, and 48 V on them harms nothing.
- **The LED shows the feed, not the switch:** it is lit from that input's switched 48 V, so it
  can't say phantom is off while it is on. The Pi reads the same feed through a divider.
- Budget: P48 allows up to 10 mA per microphone, so 2 × 48 V × 10 mA ≈ 1 W out, about 250 mA from
  the Pi's 5 V.

### Output

The codec's differential line out (2 Vrms full scale, ≥ 1.2 kΩ load) into a differential-to-
single-ended op-amp stage on the 5 V rail, a mute (default on, so nothing reaches the jack while
the Pi boots), then 10 µF, 100 Ω and a 100 kΩ bleed to the connector. On 5 V the stage swings about
1.7 Vrms, so full scale at the output is about +6 dBu (1.5–1.7 Vrms): a gain of 0.75–0.85 from the
codec's 2 Vrms, set in phase 1.

### Power

| Rail | Source | Feeds |
|---|---|---|
| 3.3 V AVDD | Pi 5 V → LC filter → low-noise LDO (TPS7A20 or LP5907 class) | Codec AVDD |
| 3.3 V IOVDD | Pi 3.3 V | Codec IOVDD, MD straps, EEPROM, the switches' and plug detection's pull-ups, relay drivers' logic |
| Analogue 5 V | Pi 5 V → load switch → ferrite and LC filter, optionally a capacitance multiplier (owner, 2026-11-11: no boost) | Buffers, preamps, FDAs, output stages |
| Relay coils | Pi 5 V, on their own filter branch | Six relays: KA (two) and KB per input |
| Mid-rail | The analogue 5 V halved, RC-filtered to well below 1 Hz and buffered | Bias for every stage |
| +48 V | Its own boost, above | Phantom only |

The Pi's 5 V moves with its load (4.75–5.1 V, with steps when the CPU or USB load changes), so the
mid-rail reference, not the rail, is what every stage's signal is measured against: its filter is
the one that matters, and phase 1 simulates the rail's ripple through to the codec. The relay
coils are kept off the analogue branch so their switching current doesn't step the audio rail.

**HAT+ standby:** the Pi can hold 5 V on with 3.3 V off. The analogue load switch, the AVDD LDO and
the phantom boost are all enabled from 3.3 V, and the switch and detection logic is pulled up to
3.3 V, so in that state every relay drops out, phantom goes off, and nothing back-powers the
codec's IOVDD, the EEPROM or the Pi's pins.

**Budget from the Pi's 5 V**, worst case: phantom ≈ 250 mA, six relay coils ≈ 180 mA (a
¼″ plug in both inputs with Line on), op-amps ≈ 50 mA, codec ≈ 30 mA: about 500 mA. Latching
relays would take the coils' share to nearly nothing, at the cost of a driver that remembers
state; phase 1 weighs it.

### Header use

| GPIO | Use |
|---|---|
| 0, 1 (ID_SD, ID_SC) | HAT+ ID EEPROM: CAT24C32, 3.9 kΩ pull-ups, WP to a test point with 1 kΩ to 3.3 V |
| 18 | BCLK (PCM_CLK) |
| 19 | FSYNC (PCM_FS) |
| 20 | Codec DOUT → Pi (PCM_DIN) |
| 21 | Pi → codec DIN (PCM_DOUT) |
| 5, 6 | In: input 1 and 2, a ¼″ plug present (the insert switch, which also drives KA) |
| 12, 13 | In: input 1 and 2, the Line switch (which also drives KB). A solder jumper turns each into an output that drives KB instead |
| 22, 23 | In: input 1 and 2, +48 V present on the feed (through a divider) |
| 24 | Output mute (pulled to muted) |
| 25 | Codec GPO (clock-error interrupt) |

Left free on purpose: GPIO 2/3 (I2C1, needed if the TAC5212 is fitted), 14/15 (the UART that
carries the pedal's Pico link) and 7–11 (SPI0).

### Software

The Pi needs a device-tree overlay: `simple-audio-card` with the Pi's I2S and a codec node with no
controls (the kernel's generic codecs fit; which one is chosen in phase 5). The EEPROM names the
overlay (`pedalscience-codec`, following the HAT+ spec's maker-board form). Its source lives in
`overlay/`. If the pedal adopts the board, rtpi builds it into the pedal's kernels, as it does
device-tree work now.

## What the board must prove

- The analogue front end: noise floor and headroom in each mode, measured as the pedal's
  [codec bring-up](https://github.com/pedal-science/pedal.project/blob/main/docs/codec-bringup-2c.md)
  measures the WM8960 now, with the same `scripts/codec-noise.py`.
- The phantom supply's ripple and noise at the input with phantom on and off.
- Round-trip latency with each filter set, and Pi-master against codec-master clocking.
- That nothing from the Pi's 5 V reaches the audio.

## Relation to the pedal

The pedal's constraints (`../pedal.project/AGENTS.md`) name the WM8960 and its clock-master
arrangement. This board doesn't touch them. Fitting it to the pedal would change several of them
(the codec, the clocking, the Core host's I2C ownership no longer being needed), so it's a decision
for the owner once v1 has been measured.
