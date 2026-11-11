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

**Linux.** TI publishes a driver for the family (TAC5X1X-LINUX-DRIVER). An upstream ASoC driver,
`tac5x1x`, has been posted to the kernel lists several times, most recently as a reworked series
in March 2026; whether it has been merged is checked in phase 5. Until it is, rtpi builds TI's
driver as a module for the pedal's kernels. This is the one risk the TAC5242 didn't have: it needed
no driver at all.

**Availability.** LCSC lists the TAC5212IRGER as C44853694; stock wasn't confirmed on 2026-11-11.
Check it in phase 1, and again before ordering.

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
                 ├─ filter ─ low-noise LDO (EN from 3.3 V) ─ 3.3 V AVDD ─ TAC5212
                 └─ boost, ≥ 60 V switch ─ filter ─ +48 V ─ per-input switch ─ 6.81 k ×2 ─ XLR only
          3.3 V ─ IOVDD, EEPROM, switch and detect logic
          I2S (GPIO 18–21) ─ BCLK, FSYNC, DIN, DOUT;  I2C1 (GPIO 2, 3) ─ SCL, SDA

¼″ tip ────── 1 MΩ ─ JFET buffer ─────────────┐ KA          ┐
XLR 2/3 ─ 47 µF ×2 ─ mic preamp, ≈ 20 dB ─────┘ (plug)  ─ L ├ KB (Line switch) ─ FDA ─ 10 µF ─ IN1P/M
¼″ tip/ring ─────────────────────────────────┐ KA          │
XLR 2/3 (after the 47 µF) ───────────────────┘ (plug) ─ Line ┘

OUT1P/M ─ mute ─┬─ differential-to-single-ended stage ─ 10 µF ─ 100 Ω ─ OUT 1, unbalanced
                └─ followers ×2 ─ phantom-proof coupling ─ OUT 1 BAL, balanced ("Output" below)
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

Each of the two logical outputs appears twice, at once: **unbalanced** on an XH 2-pin, for a ¼″ TS
jack, and **balanced** on an XH 3-pin, for a male XLR panel socket. That is two signals on four
connectors, not four outputs; the two forms of one output always carry the same audio.

```
OUT1P/M ─ 10 µF ×2 ─ mute (K_M) ─┬─ diff-to-SE stage ─ 10 µF ─ 100 Ω ─ OUT 1 (100 k bleed)
                                  │
                                  └─ pad (−20 dB, panel) ─ follower ×2 ─ 100 Ω ─ 47 µF 63 V ─ 10 Ω ─ OUT 1 BAL pin 2
                                                                         (P → hot, M → cold)   clamps ┘ (100 k bleed) pin 3
```

**The mute** comes first, so one element silences both forms: K_M, a DPDT relay per output, whose
de-energised state ties each leg to the mid-rail through 1 kΩ (the pedal's arrangement: a load, not
a short across the codec's output). GPIO 24 drives both outputs' relays, pulled to muted, so
nothing reaches either jack while the Pi boots, in standby or before the software unmutes. While
the system runs, the codec's own soft-ramped DAC mute and volume do the everyday muting; the relay
is for the times the codec isn't configured yet, or isn't powered.

**Unbalanced:** a differential-to-single-ended op-amp stage, then 10 µF, 100 Ω and a 100 kΩ bleed to
the connector. On 5 V the stage swings about 1.7 Vrms, so full scale at the output is about +6 dBu
(1.5–1.7 Vrms): a gain of 0.75–0.85 from the codec's 2 Vrms, set in phase 1.

**Balanced:** the pedal worked this out for its own XLR outputs on 2026-10-14, in
[balanced-outputs.md](https://github.com/pedal-science/pedal.project/blob/main/docs/balanced-outputs.md)
(step 2), with a simulation in
[schematic/balanced-output-sim.py](https://github.com/pedal-science/pedal.project/blob/main/schematic/balanced-output-sim.py).
This board takes that design, with two differences.

- **The codec already drives both legs.** The pedal's WM8960 has single-ended outputs, so its
  driver makes cold with an inverter. The TAC5212's output is differential: hot follows OUTxP and
  cold follows OUTxM, through two identical unity followers on the 5 V rail. Symmetric drive comes
  from the codec, and the two legs are the same circuit.
- **5 V, not 9 V.** Each follower swings about 1.7 Vrms, so the pair could give +12.8 dBu
  differentially; at unity gain, codec full scale is 2 Vrms between pins 2 and 3, **+8.2 dBu**,
  with the op-amps well inside their swing. More level (up to about +12 dBu) is a resistor's
  change, decided in phase 1.

From the pedal's design, unchanged:

- **Balance comes from matched legs**, not from symmetric signal: the same 100 Ω (1 %), the 47 µF
  capacitors paired to 5 %, the same op-amp (a dual per output, one half per leg), the same 10 Ω
  and bleed on each pin.
- **Phantom power is survived, not merely tolerated.** A stage box may put +48 V on pins 2 and 3.
  So: 47 µF 63 V bipolar coupling capacitors; 100 kΩ bleeds on the connector side; 10 Ω between
  each capacitor and its pin, which took the pedal's simulated clamp current on a shorted, charged
  pin from 69 A to 3.7 A; Schottky clamps from each driver-side node to the analogue 5 V and from
  ground. Here the clamps return into the 5 V rail and its filter, so phase 1 re-runs the
  simulation with this board's rail and its capacitance.
- **A −20 dB pad, on a panel switch per output** (decided), at the followers' input so the output impedances, and the balance,
  never change. It is for mic inputs on stage boxes, many of which run out of headroom near
  +8.2 dBu at minimum gain. The codec's DAC volume could lower the level in software instead, but
  both forms share one codec output, so it would lower the ¼″ output with it; a pad lowers only
  the XLR. At full scale the pad takes the XLR from +8.2 dBu to −11.8 dBu.
  - **The divider is always fitted** (as in the pedal: 9.1 kΩ over 1 kΩ per leg, 0.1 % so the two
    legs match), and the switch chooses which point feeds the followers: the full signal, or the
    divider's tap.
  - **The panel switch carries DC only**, like the board's other switches. It drives a dual SPDT
    analogue switch on the board, one pole per leg. That node sits at the mid-rail, inside the
    5 V rails, and feeds a follower's high input impedance, so the analogue switch's on-resistance
    adds no measurable distortion there. Phase 1 picks the part and checks it in simulation.
  - The Pi reads each pad switch, as it reads the others (GPIO 16 and 26), but can't set it.
  - The amount is one resistor, as in the pedal's design: 330 Ω in place of the 1 kΩ gives about
    −29 dB, nearer a real microphone's level.
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
| 3.3 V AVDD | Pi 5 V → LC filter → low-noise LDO (TPS7A20 or LP5907 class) | Codec AVDD |
| 3.3 V IOVDD | Pi 3.3 V | Codec IOVDD, MD straps, EEPROM, the switches' and plug detection's pull-ups, relay drivers' logic |
| Analogue 5 V | Pi 5 V → load switch → ferrite and LC filter, optionally a capacitance multiplier (owner, 2026-11-11: no boost) | Buffers, preamps, FDAs, output stages |
| Relay coils | Pi 5 V, on their own filter branch | Eight relays: KA (two) and KB per input, K_M per output |
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
at 0x50 with the TAC5x1x driver (see "Linux" above), which gives ALSA its controls. The EEPROM names
the overlay (`pedalscience-codec`, following the HAT+ spec's maker-board form). Its source lives in
`overlay/`. If the pedal adopts the board, rtpi builds it into the pedal's kernels, as it does
device-tree work now.

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
