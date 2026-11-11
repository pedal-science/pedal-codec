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

**v1 is a full-size HAT+ (65 × 56.5 mm, M2.5 holes on 58 × 49 mm)**, with room for test points and
alternative footprints. A Zero-size board can follow once v1 has shown which options are needed.
**Open:** confirm.

## Connectors

**Phantom power needs three wires.** P48 (IEC 61938) feeds +48 V through matched 6.81 kΩ resistors
to both signal conductors, hot and cold, and returns it on the screen, pin 1 of the XLR. A 2-pin
connector carries signal and ground only, so a balanced microphone can't be wired to it and phantom
power can't be fed through it to the standard.

**Recommended:** the inputs on **JST XH 3-pin** (ground, hot, cold). A combo XLR/¼″ jack on the
panel then wires straight to it: XLR pins 1, 2, 3, and the ¼″ tip and ring to hot and cold. A TS
instrument lead grounds cold through its sleeve, and the board treats that as unbalanced. The
outputs can stay on XH 2-pin (unbalanced line), or go to 3-pin as well, which would let a later
board drive them balanced. **Open:** the owner's choice.

## Blocks

```
Pi header ─ 5 V ─┬─ filter ─ low-noise LDO ─ 3.3 V AVDD ─ TAC5242
                 ├─ boost ─ post-regulator ─ analogue rail (op-amps)
                 └─ boost ≥ 60 V switch ─ filter ─ +48 V ─ per-channel switch ─ 6.81 k ×2
          3.3 V ─ IOVDD, EEPROM, logic
          I2S (GPIO 18–21) ─ BCLK, FSYNC, DIN, DOUT

XH in ─ protection ─ mode relay ─┬─ Instrument: 1 MΩ ─ JFET buffer ─┐
                                 └─ Line: balanced receiver ────────┴─ differential driver ─ 10 µF ─ IN1P/M

OUT1P/M ─ differential-to-single-ended stage ─ mute ─ 10 µF ─ 100 Ω ─ XH out (100 k bleed)
```

### Input

- **Instrument:** 1 MΩ to bias, a JFET-input op-amp (the pedal's buffer used the OPA2197;
  OPA1642 and OPA1656 are candidates), then a fully differential amplifier (FDA; OPA1637 is
  designed for driving audio ADCs) into the codec's differential input. Gain chosen in phase 1 so
  a hot passive pickup reaches about −6 dBFS.
- **Line:** a balanced input through the same FDA, wired inverting so the source sees its input
  resistors (≥ 10 kΩ per leg) and the op-amp sees an attenuated signal. Unbalanced sources work with
  cold grounded. Gain set so +4 dBu nominal leaves ≥ 10 dB of headroom (clip about +14 dBu), which
  means attenuation into the codec's +8.2 dBu full scale.
- **The mode switch is a relay** per channel (a small DPDT signal relay), not an analogue switch:
  the 1 MΩ node is the noise-sensitive one, and a relay keeps a semiconductor's leakage and
  capacitance off it. A relay's de-energised state is the default, so it is the mode with no
  phantom power.
- **Mic gain. Open.** Phantom power implies condenser microphones or active DI boxes. A condenser
  mic gives roughly −50 to −30 dBu, and with no gain in the codec it would sit 40–55 dB below full
  scale. The codec's floor (about 2.2 µVrms A-weighted against 2 Vrms) leaves only about 65 dB of
  signal-to-noise for such a mic. Three answers: (a) phantom is for active DIs and line-level
  devices only, with no mic gain; (b) a third mode, **Mic**, with a dedicated preamp (THAT1512 or
  INA163-class, about 40 dB); (c) the FDA's gain switched. (b) is the right one if microphones
  matter.

### Phantom power

- One boost converter from 5 V to about 52 V with a ≥ 60 V switch, post-filtered (LC, then a
  capacitance multiplier or a high-voltage LDO) to 48 V ± 4 V, switching far above audio and
  enabled only while some channel has phantom on.
- Per channel: a high-side switch, a slow ramp to keep the switch-on thump small, 6.81 kΩ 0.1%
  matched pair, 47 µF 63 V coupling capacitors on hot and cold, and the usual protection against a
  shorted or hot-plugged XLR (series resistors and clamps to the rails).
- **Interlock:** the phantom feed runs through a contact of the mode relay, so +48 V can reach the
  connector only with the relay in its Line position. A software fault can't put it on an
  instrument.
- Budget: P48 allows up to 10 mA per microphone, so 2 × 48 V × 10 mA ≈ 1 W out, about 250 mA from
  the Pi's 5 V.

### Output

The codec's differential line out (2 Vrms full scale, ≥ 1.2 kΩ load) into a differential-to-
single-ended op-amp stage, a mute (default on, so nothing reaches the jack while the Pi boots),
then 10 µF, 100 Ω and a 100 kΩ bleed to the connector. The level at full scale (+2 to +8 dBu) is
chosen in phase 1.

### Power

| Rail | Source | Feeds |
|---|---|---|
| 3.3 V AVDD | Pi 5 V → LC filter → low-noise LDO (TPS7A20 or LP5907 class) | Codec AVDD |
| 3.3 V IOVDD | Pi 3.3 V | Codec IOVDD, MD straps, EEPROM, logic |
| Analogue | **Open.** Pi 5 V filtered (simplest, ~±2 V of swing) or a boost to ~12 V with a low-noise LDO (headroom for active pickups and +14 dBu line) | Buffers, FDAs, output stages |
| +48 V | Its own boost, above | Phantom only |

**HAT+ standby:** the Pi can hold 5 V on with 3.3 V off. Every converter fed from 5 V is enabled
from 3.3 V, so nothing back-powers the codec's IOVDD, the EEPROM or the Pi's pins in that state.

### Header use

| GPIO | Use |
|---|---|
| 0, 1 (ID_SD, ID_SC) | HAT+ ID EEPROM: CAT24C32, 3.9 kΩ pull-ups, WP to a test point with 1 kΩ to 3.3 V |
| 18 | BCLK (PCM_CLK) |
| 19 | FSYNC (PCM_FS) |
| 20 | Codec DOUT → Pi (PCM_DIN) |
| 21 | Pi → codec DIN (PCM_DOUT) |
| 5, 6 | Input 1 and 2 mode (relay drivers; low = Line, the de-energised state; to be confirmed) |
| 22, 23 | Input 1 and 2 phantom enable (pulled down: off by default) |
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
