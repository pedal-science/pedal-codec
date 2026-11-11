# pedal-codec

A stereo audio board for the Raspberry Pi, built around Texas Instruments' TAC5242 codec (119 dB
ADC, 120 dB DAC):

- two inputs for combo XLR/¼″ jacks: **Instrument** (1 MΩ) or **Line** on the ¼″, **Mic** or
  **Line** on the XLR. The plug chooses the half; a panel switch chooses Line
- optional **+48 V phantom power** per input, from a panel switch with an LED, wired only to the
  XLR pins so it can never reach a ¼″ plug
- two **line outputs**, each both unbalanced (for a ¼″ jack) and balanced (for a male XLR), live
  at once, the balanced form protected against phantom power
- JST XH connectors for everything (XLR and ¼″ halves separately, outputs, the panel's switches),
  so the board can sit inside a case with the jacks on the panel
- a full-size HAT+, powered from the Pi's 5 V
- power, I2S audio and control through the Pi's 40-pin header, with a HAT+ ID EEPROM

It is at the design stage: [docs/design.md](docs/design.md) is the design so far and its open
questions, and [docs/plan.md](docs/plan.md) is the route to boards made and tested.

Part of [pedal.science](https://pedal.science). The hardware is CERN-OHL-P-2.0 and the software
MIT; see [LICENSING.md](LICENSING.md).
