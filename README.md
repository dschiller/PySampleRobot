# PySampleRobot
Automatically record external Gear like Sampler, Synth, Groovebox, Rompler etc. by sending MIDI Notes and threshold Input to limit Audiodata by just peaked Signals.

## Schema

![Schema](SchemaDiagram.png?raw=true "Schema")

## Example Excerpt of Sampling Clavia Nord Drum 3P Preset A1 / A2

### Practical Notes on Sampling the Nord Drum 3P

- Set the two Soundcard Inputs which are connected with the two Audio Outputs of the Nord Drum 3P to full left and full right
- Set the Nord Drum 3P Pads Threshold to 5 ( Otherwise it will play unwanted Notes if it is set to 4 or lower )
#### Zoom L-12
- Set the two Soundcard Inputs which are connected with the two Audio Outputs of the Nord Drum 3P to 0 dB on your Soundcard
- Set the Main Volume on the Nord Drum 3P to 50 % ( Poti shows to the top ) otherwise there will be Clipping in some Recordings
#### MOTU UltraLite MK3
- Set the two Soundcard Inputs which are connected with the two Audio Outputs of the Nord Drum 3P to +5 dB on your Soundcard
  ( If you have Issues with low Level on the MOTU make a Factory Reset )
    1. Push the Setup/PARAM knob until the LCD screen reads "UL Hybrid Setup".
    2. Turn the Setup/PARAM knob until the LCD reads "Factory Defaults Push [VALUE]". Push the Value knob.
    3. The LCD screen will read: "Are you sure? Push [VALUE]". Push the Value knob.
    4. The LCD screen will read: "Initializing", and the LCD screen will return to "METER 48".
- Set the Main Volume on the Nord Drum 3P to 100 % ( Poti fully rotated right )

### Structure of the Sampleprocess Output

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
  
  Unfortunately NI doesn't provide an API for Kontakt so I need to use pywinauto / pyautogui
  
  **Update**
  - This is now possible with NI's Creator Tools
