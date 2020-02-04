# PySampleRobot
Automatically record external Gear like Sampler, Synth, Groovebox, Rompler etc. by sending MIDI Notes and threshold Input to limit Audiodata by just peaked Signals.

## Shema

![Schema](Diagram.png?raw=true "Schema")

## Example Excerpt of Sampling Clavia Nord Drum 3P Preset A1 / A2

``A1 10 120 0256 00001 ####``
1. Preset Name
2. MIDI Note ( In Case of Clavia Nord Drum 3P, Pad 6 )
3. Velocity
4. Used Frames
5. Peak
6. Peak Vizualisation with '#' Char

![Example Recording Excerpt](RecordingExcerpt.gif?raw=true "Example Recording Excerpt")

Todo:
- Add Scripts to create Native Instruments Kontakt Instruments with the recorded Samples

