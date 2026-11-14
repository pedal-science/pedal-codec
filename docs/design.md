# pedal-codec: design

Started 2026-11-11. This is the design as far as it has been reasoned, with every open question
marked **Open**. [plan.md](plan.md) is the order in which they are settled and the board is made.

## What was asked for (owner, 2026-11-11)

- A board like Raspberry Pi's [Codec Zero](https://www.raspberrypi.com/documentation/accessories/audio.html)
  in size (Pi Zero size, 65 × 30 mm); a full-size HAT (65 × 56.5 mm) is fine too.
- The codec is TI's [TAC5242](https://www.ti.com/product/TAC5242). (Changed to the TAC5212 the
  same day; see "Decided".)
- **Two analogue inputs** on JST XH 2-pin connectors, each switchable between **Instrument** and
  **Line**, each with **optional +48 V**.
- **Two analogue outputs** on JST XH 2-pin connectors, line level.
- Power, digital audio and control through the Pi's header, GPIO pins included.
- Supporting parts as needed: an LDO for the supply, op-amps for the instrument inputs, a phantom
  supply, passives.
- Later the same day, since the board is full-size: **two more output connectors, balanced**, for
  the same two outputs, wired to XLR sockets on the panel.

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
6. **Each output is also balanced**, on its own XH 3-pin for a male XLR panel socket, carrying the
   same audio as its unbalanced XH 2-pin. Both forms are live at once.
7. **The codec is the TAC5212**, the TAC5242's I2C-controlled twin, so the Pi configures it in
   software. The question of laying out for either part is closed.
8. **Each balanced output has a −20 dB pad on a panel switch**, so its XLR can feed a stage box's
   mic input at about DI-box level without turning the ¼″ output down.

Why not detect everything (asked 2026-11-11): the board can tell which half of the jack is in use,
TS from TRS, a passive pickup's few kΩ from a dynamic mic's 150–600 Ω, and, once phantom is on,
whether something draws current. It can't tell an active guitar from a line output (both look
like a coupling capacitor, but a wrong guess there only costs level), and it can't tell whether a
device will tolerate 48 V before applying it, which is the guess that does damage. So the plug
chooses the path, the player chooses the rest, and phantom is always a deliberate switch.

## The codec: TAC5212

The board was specified with the TAC5242 and changed to its software-controlled twin, the
[TAC5212](https://www.ti.com/product/TAC5212), on 2026-11-11 (owner). Both are the same converters
in the same 4 × 4 mm VQFN-24: 119 dB ADC and 120 dB DAC dynamic range, 2 Vrms differential full
scale in and out. The TAC5242 is set by six strap pins and nothing else; the TAC5212 has registers,
reached over I2C, so the Pi sets it up. Read from the TAC5212's datasheet,
[SLASF23A](https://www.ti.com/lit/gpn/TAC5212) (January 2025).

**What I2C control gives this board:**

- **Every setting changes in software**, not by moving a strap: the filters, the clocking,
  differential or single-ended per channel, the input impedance, the high-pass filter, and the
  DAC's level. The ALSA mixer can expose them, and the pedal's rule that the Core host owns the
  codec's configuration holds as it does for the WM8960.
- **Digital volume** on every channel: ADC −80 to +47 dB and DAC −100 to +27 dB, both in 0.5 dB
  steps, with soft ramping and mute. The DAC also has a coarse output level, −12 to +12 dB in 6 dB
  steps.
- **Ultra-low-latency filters**, which the TAC5242 lacks. Group delay at 48 kHz:

  | Filters | ADC | DAC | Round trip | Passband |
  |---|---|---|---|---|
  | Linear phase | about 16 samples | 17.6 samples | ≈ 0.70 ms | 0.455 × fS |
  | Low latency | 6.5 samples | 7.2 samples | ≈ 0.29 ms | 0.376 × fS |
  | Ultra-low latency | about 3–4 samples | 3.2 samples | ≈ 0.14 ms | 0.325 × fS |

  The ultra-low filters' passband ends at 0.325 × fS: 15.6 kHz at 48 kHz, 31 kHz at 96 kHz. For a
  guitar at 48 kHz that is no loss; for full-range sources, run at 96 kHz. v1 measures all three.
- **Selectable input impedance**, 5, 10 or 40 kΩ per pin (SNR 119, 115 and 105 dB). The FDA drives
  it, so 5 kΩ, the quietest, stays the choice.
- **A high-swing mode**, 4 Vrms differential (+14.2 dBu), DC-coupled with external bias. On the
  5 V rail the FDA can't swing that far (about 3.4 Vrms differential), so this board doesn't use
  it; it would matter only if a higher analogue rail ever appears.
- **Four GPIO-type pins** (GPIO1, GPIO2, GPO1, GPI1): an interrupt to the Pi, and GPI1 as the PLL's
  reference clock for codec-master operation.
- Programmable MICBIAS (to 3 V). Unused here, since the mic path has its own preamp and phantom
  supply; it goes to a test point.

**What it does not give:** an analogue preamp. Its "channel gain" lowers the full scale and the SNR
together (119 dB at 0 dB, 107 dB at 12 dB), so the noise referred to the input doesn't improve: it
is gain in the digital domain. The mic preamp stays on the board.

**I2C:** SCL and SDA go to the Pi's I2C1 (GPIO 2 and 3, which already carry pull-ups on the Pi).
The ADDR pin sets the address with a resistor: to ground 0x50 (the default here), 4.7 kΩ to ground
0x51, 22 kΩ to AVDD 0x52, 4.7 kΩ to AVDD 0x53, and tied to AVDD it selects SPI instead. The HAT+ ID
EEPROM is on the separate ID bus (GPIO 0 and 1), so 0x50 doesn't collide with it.

**Configuration:** the codec runs differential at both ends, which gives the 119/120 dB, and the
board converts: single-ended or balanced sources to differential at the inputs, differential to
single-ended at the unbalanced outputs. At the default VREF (2.75 V, which needs AVDD ≥ 3 V) full
scale is **2 Vrms differential (+8.2 dBu)** in and out, and each input pin is 5 kΩ at the default
impedance setting, so every source is buffered and the coupling capacitors are sized against it
(10 µF gives 3.2 Hz).

**Clocking: no MCLK.** In target mode the PLL locks to BCLK and FSYNC alone (64 × 48 kHz =
3.072 MHz from the Pi's I2S). That is the difference from the WM8960 board in the pedal now, whose
24 MHz oscillator forces the codec to be clock master. Here either side can be master: the Pi
(simplest), or the codec, from a local low-jitter oscillator on GPI1 (up to 36.864 MHz). The board
carries the oscillator's footprint, so the two can be measured.

**Other pins.** DREG (1.55 V internal regulator) and VREF each need their own capacitor (VREF
≥ 1 µF, no load). Supplies may come up in either order, ramping slower than 0.1 V/µs.

**Linux** (checked 2026-11-11, phase 1). There is no TAC5212 driver in mainline (7.4-rc2) or in
Raspberry Pi's kernel trees (`rpi-7.3.y`, `rpi-7.4.y`). Mainline's `pcm6240` driver covers its
ADC-only and DAC-only siblings (TAA5212, TAD5212) but not the codec. TI posted `tac5x1x` as a
v1 series of eight patches on 2026-03-12: an MFD core, a pinctrl driver for the four GPIO pins and
the ASoC codec driver, covering the TAC5212 among eleven parts. Mark Brown asked for changes to the
codec driver (analogue input routing from the device tree rather than mixer controls, a duplicate
control registration, an empty resume function), Krzysztof Kozlowski said the bindings repeat
problems raised before, and no later revision or "applied" notice was found. TI also publishes
TAC5X1X-LINUX-DRIVER outside the kernel. vip runs Ubuntu's 7.0 raspi-realtime kernel, rebuilt by
rtpi. Three routes, in order:

1. **TI's series as an out-of-tree module** built by rtpi for its kernel: the codec, the MFD core
   and pinctrl, from the posted patches or TI's package. Most functionality, most work.
2. **Configure the codec from userspace.** The codec is only registers: a small tool writes them
   over `/dev/i2c-1` at start-up, as pedald already configures the pedal, and the device tree
   describes the codec to ALSA as one with no controls, as the TAC5242 plan would have. No kernel
   work at all; ALSA has no mixer controls, so the pedal's software owns volume and the filters.
3. Upstream, if a later revision is merged and reaches the kernels the pedal uses.

Route 2 removes the driver risk outright, so v1 is brought up that way (phase 5) and route 1 follows
if the mixer controls are wanted. The evaluation module (phase 4) lets both be tried before the
boards arrive.

**Availability.** LCSC C44853694: 774 in stock at $7.46 each on 2026-11-11. Check again before
ordering.

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
| OUT 1, OUT 2 | JST XH 2-pin (B2B-XH-A) | 1 ground, 2 signal: unbalanced, for a ¼″ TS jack |
| OUT 1 BAL, OUT 2 BAL | JST XH 3-pin (B3B-XH-A) | 1 SHIELD (XLR pin 1), 2 hot, 3 cold: balanced, for a male XLR panel socket (the pedal's choice is the Neutrik NC3MD-LX) |
| PANEL | One connector, part chosen in phase 2 (about 12 pins) | Ground, both inputs' Line switches, both phantom switches, both phantom LEDs, both balanced outputs' pad switches |

**The combo jack** needs a switching contact that changes when a ¼″ plug goes in. The candidate is
Neutrik's NCJ9FI-S (XLR and a switching stereo jack, three switching contacts). Neutrik's page
doesn't say whether they are isolated or normalled to the tip and ring; its circuit drawing settles
it in phase 2. Either way works: an isolated contact is the detection; if they are normals,
detection uses the **ring's** normal, not the tip's. The ring isn't on the 1 MΩ node (Instrument
uses the tip alone), any plug lifts the ring contact off its normal, a TS plug included, and with no
plug the ¼″ half isn't in the signal path, so the pull-up's DC on the ring goes nowhere. A combo jack takes
only one plug at a time, so the board never has to choose between two.

**v1 also carries the panel's switches on the board**: small slide switches wired in parallel with
the PANEL connector, so the board can be tested on the bench with nothing attached.

## Blocks

```
Pi header ─ 5 V ─┬─ load switch (EN from 3.3 V) ─ ferrite + LC ─ analogue 5 V ─ op-amps
                 │                                              └─ RC-filtered, buffered mid-rail (≈ 2.45 V)
                 ├─ relay coils (own filter branch)
                 ├─ filter ─ low-noise LDO (EN from 3.3 V) ─ 3.3 V AVDD ─ TAC5212
                 └─ boost, ≥ 60 V switch ─ filter ─ +48 V ─ per-input switch ─ 6.81 k ×2 ─ XLR only
          3.3 V ─ IOVDD, EEPROM, switch and detect logic
          I2S (GPIO 18–21) ─ BCLK, FSYNC, DIN, DOUT;  I2C1 (GPIO 2, 3) ─ SCL, SDA

¼″ tip ────── 1 MΩ ─ JFET buffer ─────────────┐ KA          ┐
XLR 2/3 ─ 23.5 µF ×2 ─ mic preamp, ≈ 20 dB ───┘ (plug)  ─ L ├ KB (Line switch) ─ FDA ─ 10 µF ─ IN1P/M
¼″ tip/ring ─────────────────────────────────┐ KA          │
XLR 2/3 (after the 23.5 µF) ─────────────────┘ (plug) ─ Line ┘

OUT1P/M ─ mute ─┬─ differential-to-single-ended stage ─ 10 µF ─ 100 Ω ─ OUT 1, unbalanced
                └─ followers ×2 ─ phantom-proof coupling ─ OUT 1 BAL, balanced ("Output" below)
```

### Input

Each input has two signal paths, one per half of the jack, and two choices:

| Plug in | Line switch | Mode | Path into the FDA |
|---|---|---|---|
| ¼″ | off | **Instrument** | Tip, 1 MΩ, JFET buffer |
| ¼″ | on | **Line** | Tip and ring, balanced or (TS lead, ring grounded) unbalanced |
| XLR (or nothing) | off | **Mic** | Phantom feed, 23.5 µF ×2, mic preamp |
| XLR | on | **Line** | Hot and cold after the 23.5 µF, e.g. a balanced line output or an active DI |

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

- **The supply** (phase 1): a TPS61170 boost (1.2 MHz, 38 V switch) to about 27 V, with a
  diode-capacitor doubler on its switch node to about 54 V, regulated from the doubled output. A
  single boost stage can't step 5 V to 52 V (a 90 % duty cycle), and the boosts with a 60 V switch
  are scarce at LCSC (the LT8362 had 33). Then an LC filter and a capacitance multiplier (an
  MMBT5551 with an RC-filtered base) to 48 V ± 4 V. It runs only while either input's phantom
  switch is on.
- **Per input:** a PNP high-side switch (MMBT5401, 150 V) driven by a 2N7002, with an RC on its base
  that ramps the feed over about 1.5 s; the 6.81 kΩ feed as two 3.4 kΩ 0.1 % 1206 resistors in
  series per leg, since a shorted pin puts 0.34 W in each leg, more than one 1206 takes; and 2 × 47 µF
  63 V electrolytics back to back per leg (23.5 µF, bipolar), since JLCPCB's library has no bipolar
  63 V part. Then 10 Ω, Schottky clamps (SS14) to the analogue 5 V and from ground, 22 Ω into the
  preamp, and 1.2 kΩ to the mid-rail. That protection sits in front of both the Mic preamp and
  the XLR's Line path.
- **The thump.** With every part matched, switching phantom on is silent. With cold's capacitors
  20 % larger and its feed resistor 0.1 % higher, a 300 ms ramp thumps at −6 dBFS and a 1.5 s ramp
  at −20 dBFS (`sim/results/README.md`). So the ramp is 1.5 s, and the Pi, which reads each input's
  phantom feed (GPIO 22, 23), mutes that channel in the codec for 3 s whenever it changes.
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

Each of the two logical outputs appears twice, at once: **unbalanced** on an XH 2-pin, for a ¼″ TS
jack, and **balanced** on an XH 3-pin, for a male XLR panel socket. That is two signals on four
connectors, not four outputs; the two forms of one output always carry the same audio.

```
OUT1P/M ─ 10 µF ×2 ─ mute (K_M) ─┬─ diff-to-SE stage ─ 10 µF ─ 100 Ω ─ OUT 1 (100 k bleed)
                                  │
                                  └─ pad (−20 dB, panel) ─ ×1.13 ×2 ─ 100 Ω ─ 23.5 µF 63 V ─ 10 Ω ─ OUT 1 BAL pin 2
                                                                         (P → hot, M → cold)   clamps ┘ (100 k bleed) pin 3
```

**The mute** comes first, so one element silences both forms: K_M, a DPDT relay per output, whose
de-energised state ties each leg to the mid-rail through 1 kΩ (the pedal's arrangement: a load, not
a short across the codec's output). GPIO 24 drives both outputs' relays, pulled to muted, so
nothing reaches either jack while the Pi boots, in standby or before the software unmutes. While
the system runs, the codec's own soft-ramped DAC mute and volume do the everyday muting; the relay
is for the times the codec isn't configured yet, or isn't powered.

**Unbalanced:** a differential-to-single-ended op-amp stage, then 10 µF, 100 Ω and a 100 kΩ bleed to
the connector. Its gain is 7.5 kΩ over 9.09 kΩ plus the mute's 1 kΩ, 0.743, so codec full scale
gives **1.45 Vrms (+5.4 dBu)** at the ¼″ output, with the op-amp swinging 0.42–4.56 V on the 5 V
rail.

**Balanced:** the pedal worked this out for its own XLR outputs on 2026-10-14, in
[balanced-outputs.md](https://github.com/pedal-science/pedal.project/blob/main/docs/balanced-outputs.md)
(step 2), with a simulation in
[schematic/balanced-output-sim.py](https://github.com/pedal-science/pedal.project/blob/main/schematic/balanced-output-sim.py).
This board takes that design, with two differences.

- **The codec already drives both legs.** The pedal's WM8960 has single-ended outputs, so its
  driver makes cold with an inverter. The TAC5212's output is differential: hot follows OUTxP and
  cold follows OUTxM, through two identical non-inverting stages on the 5 V rail. Symmetric drive
  comes from the codec, and the two legs are the same circuit.
- **5 V, not 9 V.** Each stage has a gain of 1.13 (1.3 kΩ over 10 kΩ), which makes up what the
  mute's 1 kΩ loses against the loads on the codec's output, so codec full scale gives **1.98 Vrms
  (+8.1 dBu)** between pins 2 and 3, each op-amp swinging 1.01–3.97 V. More level (up to about
  +12 dBu) is a resistor's change.

From the pedal's design, unchanged:

- **Balance comes from matched legs**, not from symmetric signal: the same 100 Ω (1 %), the same
  capacitors, the same op-amp (a dual per output, one half per leg), the same 10 Ω and bleed on
  each pin. The capacitors are 2 × 47 µF 63 V back to back per leg, as on the inputs; electrolytics
  are ±20 %, which unbalances the legs at 50 Hz, so v1 measures the balance and, if it needs it,
  the pairs are matched by hand.
- **Phantom power is survived, not merely tolerated.** A stage box may put +48 V on pins 2 and 3.
  So: 63 V capacitors; 100 kΩ bleeds on the connector side; 10 Ω between each capacitor and its
  pin, which took the pedal's simulated clamp current on a shorted, charged pin from 69 A to
  3.7 A; Schottky clamps (SS14) from each driver-side node to the analogue 5 V and from ground. With
  this board's rail (phase 1): phantom on puts 44.9 V on the pin, the driver side of the capacitor
  stays between −0.63 and 1.62 V, the op-amp carries at most 13.4 mA, and the short puts 4.25 A
  through the 10 Ω for a moment, inside the SS14's 25 A surge rating.
- **A −20 dB pad, on a panel switch per output** (decided), at the followers' input so the output impedances, and the balance,
  never change. It is for mic inputs on stage boxes, many of which run out of headroom near
  +8.2 dBu at minimum gain. The codec's DAC volume could lower the level in software instead, but
  both forms share one codec output, so it would lower the ¼″ output with it; a pad lowers only
  the XLR. At full scale the pad takes the XLR from +8.2 dBu to −11.8 dBu.
  - **The divider is always fitted**: 91 kΩ over 10 kΩ per leg, 0.1 % so the two legs match, ten
    times the pedal's values so it loads the codec's output less (−20.2 dB simulated), and the switch chooses which point feeds the followers: the full signal, or the
    divider's tap.
  - **The panel switch carries DC only**, like the board's other switches. It drives a dual SPDT
    analogue switch on the board, one pole per leg. That node sits at the mid-rail, inside the
    5 V rails, and feeds a follower's high input impedance, so the analogue switch's on-resistance
    adds no measurable distortion there. Phase 1 picks the part and checks it in simulation.
  - The Pi reads each pad switch, as it reads the others (GPIO 16 and 26), but can't set it.
  - The amount is one resistor, as in the pedal's design: 3.3 kΩ in place of the 10 kΩ gives about
    −29 dB, nearer a real microphone's level.
  - The analogue switch is a TS5A23157 (dual SPDT, 10 Ω, 5 V).
- **Pin 1 belongs to the chassis at the socket**, not to the board's ground: AES48, and the
  pedal's "pin 1 problem". The XH 3-pin carries pin 1 as its own net, SHIELD, which reaches the
  board's ground only through an unfitted footprint (0 Ω or 10 nF) for builds with no metal case.
  The **ground lift** is a panel part: a toggle per XLR between pin 1 and a lug on the case, with
  10 nF across it, wired at the socket.
- **RF:** matched small capacitors from each pin to SHIELD at the connector, sized in phase 1
  (matched, or they unbalance the legs).

**The codec's load.** Both forms hang on the same output, after the mute: the unbalanced stage's
input resistors and the followers' 100 kΩ bias resistors, together far above the codec's 1.2 kΩ
minimum.

### Power

| Rail | Source | Feeds |
|---|---|---|
| 3.3 V AVDD | Pi 5 V → LC filter → TPS7A2033 (10 µVrms) | Codec AVDD |
| 3.3 V IOVDD | Pi 3.3 V | Codec IOVDD, EEPROM, the switches' and plug detection's pull-ups, relay drivers' logic |
| Analogue 5 V | Pi 5 V → load switch (TPS22917) → 10 µH and 110 µF (owner, 2026-11-11: no boost) | Buffers, preamps, FDAs, output stages |
| Relay coils | Pi 5 V, on their own filter branch | Eight relays: KA (two) and KB per input, K_M per output |
| Mid-rail | The analogue 5 V halved (10 kΩ, 10 kΩ), then two RC stages (100 µF; 10 kΩ and 100 µF: 0.32 Hz and 0.16 Hz), buffered by an OPA1656 | Bias for every stage |
| +48 V | Its own boost, above | Phantom only |

The Pi's 5 V moves with its load (4.75–5.1 V, with steps when the CPU or USB load changes), so the
mid-rail reference, not the rail, is what every stage's signal is measured against: its filter is
the one that matters, and phase 1 simulates the rail's ripple through to the codec. The relay
coils are kept off the analogue branch so their switching current doesn't step the audio rail.

**HAT+ standby:** the Pi can hold 5 V on with 3.3 V off. The analogue load switch, the AVDD LDO and
the phantom boost are all enabled from 3.3 V, and the switch and detection logic is pulled up to
3.3 V, so in that state every relay drops out, phantom goes off, and nothing back-powers the
codec's IOVDD, the EEPROM or the Pi's pins.

**Budget from the Pi's 5 V**, worst case: phantom ≈ 250 mA, eight relay coils ≈ 240 mA (a
¼″ plug in both inputs with Line on, and both outputs unmuted), op-amps ≈ 60 mA, codec ≈ 30 mA:
about 580 mA. Latching
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
| 24 | Out: mute, both outputs in both forms (pulled to muted) |
| 2, 3 | I2C1: the codec's SCL and SDA (address 0x50) |
| 25 | In: the codec's interrupt (GPO1, or GPIO1 by register) |
| 16, 26 | In: output 1 and 2, the balanced pad switch (which also drives the pad's analogue switch) |

Left free on purpose: 14/15 (the UART that carries the pedal's Pico link) and 7–11 (SPI0).

### Software

The Pi needs a device-tree overlay: `simple-audio-card` with the Pi's I2S, and the codec on I2C1
at 0x50. With route 2 (see "Linux" above), a start-up tool configures the codec's registers and
ALSA sees a codec with no controls; with route 1, the TAC5x1x driver gives ALSA its controls. The EEPROM names
the overlay (`pedalscience-codec`, following the HAT+ spec's maker-board form). Its source lives in
`overlay/`. If the pedal adopts the board, rtpi builds it into the pedal's kernels, as it does
device-tree work now.

## Phase 1 values (2026-11-11)

Settled in phase 1 ([plan.md](plan.md)): every part with its LCSC number and stock that day, the
values the stages use, and what the simulation shows. The decks and their full results are in
[`sim/`](../sim/): `python3 sim/sim.py` reruns them and rewrites
[`sim/results/README.md`](../sim/results/README.md). The op-amps there are behavioural (each
part's gain-bandwidth, voltage noise and output swing); the makers' models replace them when the
schematic is reviewed.

### Parts

| Part | Use | LCSC | Stock | Each |
|---|---|---|---|---|
| TAC5212IRGER | Codec | C44853694 | 774 | $7.46 |
| OPA2197IDR | Instrument buffers (one dual, both inputs) | C139363 | 5,174 | $0.83 |
| OPA1612AIDR | Mic preamps (a dual per input) | C94590 | 21,246 | $1.35 |
| OPA1637DGKR | The FDA (one per input) | C2860968 | 9,229 | $2.55 |
| OPA1656IDR | Unbalanced outputs (one dual), balanced stages (a dual per output), mid-rail buffer | C1849431 | 3,803 | $1.51 |
| TPS7A2033PDBVR | AVDD, 3.3 V, 10 µVrms | C2862740 | 114,268 | $0.21 |
| TPS22917DBVR | Analogue 5 V load switch, enabled from 3.3 V | C2681320 | 2,017 | $0.45 |
| FNR4030S100MT | 10 µH: the analogue 5 V filter, and the boost | C167879 | 128,247 | $0.05 |
| TPS61170DRVR | Phantom boost | C15163 | 46,950 | $0.79 |
| SS210 | Boost and doubler diodes (100 V) | C14996 (basic) | 1,021,840 | $0.03 |
| SS14 | Clamps, inputs and balanced outputs | C2480 (basic) | 1,521,813 | $0.02 |
| MMBT5551 | Capacitance multiplier | C2145 (basic) | 1,410,804 | $0.02 |
| MMBT5401 | Phantom high-side switch, per input | C8326 (basic) | 715,341 | $0.02 |
| 2N7002 | Relay and phantom drivers | C8545 (basic) | 6,118,004 | $0.02 |
| RT1206BRD073K4L | Phantom feed, 3.4 kΩ 0.1 %, two in series per leg | C870711 | 1,252 | $0.05 |
| RV63V47M6X8 | 47 µF 63 V, two back to back per leg (inputs and balanced outputs: 16) | C48971005 | 363,499 | $0.06 |
| G6K-2F-Y DC5 | DPDT signal relay, 5 V, gold-clad contacts (eight); replaced the HFD4/5-SR in phase 2 | C231389 | 4,579 | $1.48 |
| TS5A23157DGSR | Balanced pad's analogue switch (one per output) | C11133 | 6,924 | $0.48 |
| CAT24C32WI-GT3 | HAT+ ID EEPROM | C81193 | 7,757 | $0.39 |
| HSO321S 12.288 MHz | Oscillator for codec-master, footprint only on v1 | C160458 | 1,372 | $0.75 |
| B2B-XH-A / B3B-XH-A / B4B-XH-A | Outputs / XLR and balanced outputs / ¼″ | C158012 / C144394 / C144395 | 577,754 / 130,009 / 537,163 | $0.03–0.05 |
| 2.54-2*20 | 40-pin header socket | C2977589 | 37,783 | $0.32 |

None of the op-amps is a JLCPCB "basic" part, so each adds an assembly feeder fee; the passives
are chosen from the basic library in phase 2. Panel parts (combo jacks, XLR sockets, switches,
LEDs) are bought separately and wired to the board's connectors.

### Values

| Stage | Values | Gives |
|---|---|---|
| FDA | 4.99 kΩ feedback with 220 pF each side; OPA1637, output common mode at the mid-rail | −3 dB at 137–139 kHz in every mode |
| Instrument | 100 nF film into 1 MΩ to the mid-rail, 1 kΩ, OPA2197 follower; FDA input 3.83 kΩ | Gain +2.1 dB, full scale at +6.1 dBu (4.4 Vpp), −3 dB at 3.8 Hz |
| Line | 10 µF and 10 kΩ per leg into the FDA | Gain −6.2 dB, full scale at +14.5 dBu, 10 kΩ per leg |
| Mic | 23.5 µF, 10 Ω, clamps, 22 Ω, 1.2 kΩ bias per leg; OPA1612 pair with 249 Ω feedback and 49.9 Ω gain resistor (×10.98); FDA input 4.99 kΩ | Gain +19.9 dB, full scale at −11.7 dBu, about 2 kΩ input, −3 dB at 6.6 Hz |
| Codec input | 47 Ω per leg, 2.2 nF across, 10 µF per leg | |
| Unbalanced output | 1 kΩ mute resistor, 9.09 kΩ and 7.5 kΩ around an OPA1656, 10 µF, 100 Ω, 100 kΩ bleed | 0.743, full scale +5.4 dBu |
| Balanced output | 1 kΩ mute resistor, pad 91 kΩ / 10 kΩ, OPA1656 ×1.13 (1.3 kΩ / 10 kΩ) per leg, 100 Ω, 2 × 47 µF, 10 Ω, 100 kΩ bleed | Full scale +8.1 dBu, −11.9 dBu padded |

### What the simulation shows

Noise is over 20 Hz–20 kHz, unweighted, referred to the source (a 10 kΩ pickup for Instrument,
100 Ω per leg for Line, a 150 Ω microphone for Mic), with the codec's own floor added.

| Mode | Full scale | Noise | Dynamic range |
|---|---|---|---|
| Instrument | +6.1 dBu | −106.6 dBu | 112.7 dB |
| Line | +14.5 dBu | −101.3 dBu | 115.8 dB |
| Mic | −11.7 dBu | −123.1 dBu | 111.5 dB |

- **Mic noise.** −123.1 dBu, against −130.9 dBu for the 150 Ω source alone over the same band.
  What the board adds is the series protection resistors, the OPA1612s, the 49.9 Ω gain resistor
  and the FDA, in about equal shares; A-weighting would take 2–3 dB off. Halving the preamp's
  resistances and the series resistor gained 0.8 dB, so what is left is the price of protecting the
  input against phantom power.
- **Swing.** At codec full scale every op-amp has at least 0.17 V before its rail; the instrument
  buffer is the closest, so in Instrument mode the codec clips first, as intended. The OPA1612's
  inputs stay inside the 2.0–2.95 V its common-mode range allows on 5 V.
- **The Pi's 5 V.** Ripple reaches the codec at −110 dB or less at 100 Hz in Instrument mode, and
  far below that in Line and Mic, which are differential; −112 dB at the unbalanced outputs. That
  is the two-stage mid-rail filter's work: with one stage, Instrument and the unbalanced output
  were at −54 dB and −56 dB.
- **Mute:** −79 dB at both forms of each output.
- **Phantom on an input**, and **on a balanced output**: in "Phantom power" and "Output" above.

## Phase 2 schematic (2026-11-14)

The KiCad 10 project in [`hardware/`](../hardware/): a root sheet and seven sheets (header and
EEPROM, power, phantom supply, codec, panel, and the input and output channels, each used twice).
ERC is clean, every symbol carries `LCSC` and `MPN`, and [schematic-review.md](schematic-review.md)
is the review with every finding answered. What the schematic settled or changed from phase 1:

- **The relays are Omron G6K-2F-Y** (C231389), not the HFD4/5-SR: the HFD4/5's pin assignment
  isn't published anywhere it could be checked, and the G6K's is, on Omron's sheet and in KiCad's
  own symbol and footprint. Same 5 V coil class and DPDT form; 4,579 in stock on 2026-11-11, which
  covers eight per board many times over.
- **The pad switch has a level shifter.** The TS5A23157 runs from the analogue 5 V, where its logic
  high is 0.7 × V+, 3.5 V, more than a 3.3 V GPIO gives. A 2N7002 per output inverts the Pi's PAD
  line into PADN, pulled up to 5 V: PAD high pads the output. In standby the analogue 5 V is off, so
  nothing reaches the Pi's 3.3 V side.
- **Plug detection uses the combo jack's sleeve normal.** The NCJ9FI-S's normals are closed with no
  ¼″ plug and open with one. The sleeve normal (the XH 4-pin's pin 4) is pulled up to 3.3 V on the
  board and drives both the GPIO (PLUG1, PLUG2) and the KA relays' driver directly, so the jack's
  routing follows the plug without software.
- **QOD has a 0 Ω (R164) to VOUT**, which is TI's quickest discharge; fitted as a resistor it slows
  the discharge. **C94, 10 µF, on the load switch's output** came from the review: it keeps VOUT
  above −0.3 V when the switch turns off with current in L1.
- **The TAC5212's footprint needs its corner pins.** The RGE package has four corner VSS pads (A1–A4)
  besides the thermal pad; the symbol carries them, and KiCad's `Texas_RGE0024H` footprint the
  schematic names does not. Phase 3 makes a footprint from TI's land pattern with the corner pads,
  or the board update will leave A1–A4 unplaced.
- **The phantom feed resistors run warm in a sustained short.** A pin shorted to ground puts about
  0.17 W in each 3.4 kΩ 1206 (two in series per leg), 67 % of its 0.25 W rating, against the usual
  60 % derating. Acceptable for a fault that the player sees and removes; 1210 parts would bring it
  to 34 % if v2 wants the margin.
- **The XLR's Line mode loads its source with about 2 kΩ**, because the line path sits behind the
  same phantom protection as the mic (1.2 kΩ bias per leg to the mid-rail). Balanced line sources
  drive that easily; a weak consumer source would lose a little level. Measured in phase 6.
- **10 µF X7R capacitors sit in the signal path** (the Line inputs' coupling, the codec's inputs).
  Class 2 dielectrics distort when the voltage across them swings; here the DC across them is
  small and the signal across them smaller, so the distortion should be under the codec's.
  Measured in phase 6, with film or electrolytic parts as the fallback.
- **The unbalanced outputs' 22 µF 16 V electrolytic coupling capacitors (C81, C85; C22387968) had
  about 7,000 in stock** on the day: enough, but checked again before ordering.
- **The bench DIP switch (SW1, SMXS-06K-TP, C5439765)** uses KiCad's generic 6-way slide footprint;
  phase 3 checks it against the maker's drawing before placement.
- **Seven parts are unfitted options**, marked DNP: the 12.288 MHz oscillator with its decoupling and
  link (X1, C37, R22), and each balanced output's SHIELD-to-ground 0 Ω and 10 nF (R130, C82; R163,
  C92). Phase 3 sets KiCad's DNP attribute on them before any BOM is made.
- **Input 2's parts have the lower designators** (J3, J4, R36–R70, U7–U9, K1–K3; Input 1 is J5, J6,
  R71–R105, U10–U12, K4–K6), because KiCad annotated the second sheet instance first.
  In each, the OPA2197 is the lowest U, then the OPA1612, then the OPA1637 (U7–U9, U10–U12). Cosmetic;
  the silkscreen and the BOM say which channel a part belongs to by its sheet.

## What the board must prove

- The analogue front end: noise floor and headroom in each mode, measured as the pedal's
  [codec bring-up](https://github.com/pedal-science/pedal.project/blob/main/docs/codec-bringup-2c.md)
  measures the WM8960 now, with the same `scripts/codec-noise.py`.
- The phantom supply's ripple and noise at the input with phantom on and off.
- The balanced outputs' balance (output impedance matching, as IEC 60268-3 tests a receiver) and
  their survival of phantom power switched on, left on and hot-plugged.
- Round-trip latency with each filter set (linear, low, ultra-low), and Pi-master against codec-master clocking.
- That nothing from the Pi's 5 V reaches the audio.

## Relation to the pedal

The pedal's constraints (`../pedal.project/AGENTS.md`) name the WM8960 and its clock-master
arrangement. This board doesn't touch them. Fitting it to the pedal would change several of them
(the codec, its driver, the clocking: the Pi as master instead of the codec), so it's a decision
for the owner once v1 has been measured. The Core host still owns the codec's I2C bus, as it does
now.
