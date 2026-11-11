# pedal-codec

A stereo audio board for the Raspberry Pi, built around Texas Instruments' TAC5242 codec (119 dB
ADC, 120 dB DAC):

- two inputs, each switchable between **Instrument** (1 MΩ), **Line** and **Mic**, each with
  optional **+48 V phantom power** (never in Instrument mode: a relay contact enforces it)
- two **line outputs**
- JST XH connectors for all four (3-pin balanced inputs, 2-pin outputs), so the board can sit
  inside a case with the jacks on the panel
- a full-size HAT+, powered from the Pi's 5 V
- power, I2S audio and control through the Pi's 40-pin header, with a HAT+ ID EEPROM

It is at the design stage: [docs/design.md](docs/design.md) is the design so far and its open
questions, and [docs/plan.md](docs/plan.md) is the route to boards made and tested.

Part of [pedal.science](https://pedal.science). The hardware is CERN-OHL-P-2.0 and the software
MIT; see [LICENSING.md](LICENSING.md).
