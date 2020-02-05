import queue, os, time, rtmidi, mido, librosa, keyboard
import sounddevice as sd
import soundfile as sf
import numpy as np


class Sampler:

    def __init__(self, midiDevice, audioDevice, sampleRate=44100, bitDepth=16, inputChannels=[1, 2]):
        inputChannels[0]-=1
        inputChannels[1]-=1
        if bitDepth==16:
            bitDepth='PCM_16'
        if bitDepth==24:
            bitDepth='PCM_24'
        if bitDepth==32:
            bitDepth='PCM_32'
        self.md = MIDI(midiDevice)
        self.ad = Audio(device=audioDevice, samplerate=sampleRate, channels=2, inputChannels=inputChannels, subtype=bitDepth, midi=self.md)

    def samplePreset(self, preset, presetname, note):
        self.md.setBank(preset[0])
        self.md.setProgram(preset[1])
        for velocity in range(1, 128):
            self.ad.sampleNote(channel=0, note=note, velocity=velocity, fileprefix=presetname, folder=presetname, subfolder='note_%s'%note)

class MIDI:

    def __init__(self, port):
        self.midiOut = rtmidi.MidiOut()
        availablePorts = self.midiOut.get_ports()

        if availablePorts:
            for midiPort in availablePorts:
                if port in midiPort:
                    usePort = midiPort[-1]
                    realPortName = midiPort
            self.midiOut.open_port(int(usePort))
            print('Using %s Port'%port)
        else:
            print('Port %s not found.'%port)
        self.midiOut.close_port()
        self.midiOut = mido.open_output(realPortName)

    def sendNote(self, channel, note, velocity):
        self.midiOut.send(mido.Message('note_on', note=note, velocity=velocity, channel=channel))

    def setBank(self, bank):
        self.midiOut.send(mido.Message('control_change', control=0, channel=0, time=0))
        self.midiOut.send(mido.Message('control_change', control=32, value=bank, channel=0, time=0))
        time.sleep(.5)

    def setProgram(self, program):
        self.midiOut.send(mido.Message('program_change', program=program, channel=0, time=0))
        time.sleep(.5)


class Audio:

    def __init__(self, device, samplerate, channels, inputChannels, subtype, midi):
        self.device = device
        self.samplerate = samplerate
        self.channels = channels
        self.inputChannels = inputChannels
        self.subtype = subtype
        self.md = midi
        
        sd.default.device = self.device
        sd.default.samplerate = self.samplerate
        sd.default.channels = self.channels
        sd.default.extra_settings = sd.AsioSettings(channel_selectors=inputChannels)

        self.channels_in = sd.default.channels[0]
        self.channels_out = sd.default.channels[1]

    def sampleNote(self, channel, note, velocity, fileprefix='', folder=None, subfolder=None):
        if not folder is None:
            if not os.path.exists(folder):
                os.mkdir(folder)
            if not os.path.exists('%s\\%s'%(folder, subfolder)):
                os.mkdir('%s\\%s'%(folder, subfolder))
            file = '%s\\%s\\%s_%s_%s_%s.wav'%(folder, subfolder, fileprefix, channel, note, velocity)
        else:
            file = '%s_%s_%s_%s.wav'%(fileprefix, channel, note, velocity)

        if os.path.exists(file):
            os.remove(file)

        self.q = queue.Queue()
        self.record = True
        self.slagTime = 35 * 3
        self.thresholdStart = False
        self.startRecord = False
        self.timeStart = time.time()

        def callback(indata, frames, timeCFFI, status):
                
            if keyboard.is_pressed('Esc'):
                print("\nYou pressed Esc, so exiting...")
                os._exit(1)

            peak=np.average(np.abs(indata))*32*64
            if self.thresholdStart:
                if peak>=.1:
                    self.startRecord=True
                if self.startRecord:
                    self.q.put(indata.copy())
            else:
                self.q.put(indata.copy())
            bars="#"*int(128*64*peak/2**16)
            timeDiff = round((time.time() - self.timeStart) * 1000)
            print('  Preset %s - Channel %s - Note %s - Velocity %s - Device %s - Input Channels %s - Sample Rate %s - Bit Depth %s - Sample Time %sms - Used Frames %04d - Peak %05d %s'%(fileprefix, channel+1, note, velocity, sd.default.device[0], self.inputChannels, self.samplerate, self.subtype, timeDiff, frames, peak, bars))
            if peak<.1:
                self.slagTime -= 1
                if self.slagTime == 0:
                    self.record = False

        with sf.SoundFile(file, mode='x', samplerate=sd.default.samplerate, channels=self.channels_in, subtype=self.subtype) as f:
            with sd.InputStream(callback=callback):
                self.md.sendNote(channel, note, velocity)
                while self.record:
                    f.write(self.q.get())
        
        # y, sr = librosa.load(file, mono=False, sr=None)
        # yt, index = librosa.effects.trim(y)
        # sf.write(file, yt.T, sd.default.samplerate, subtype=self.subtype)

sp = Sampler(midiDevice='USB Midi 4i4o', audioDevice='MOTU Audio ASIO', sampleRate=44100, bitDepth=24, inputChannels=[3, 4])

# ###########################################
# # Debugging
# ###########################################
# bank=0
# bankLetter='A'
# preset=1
# note=10
# sp.samplePreset(preset=[bank, preset], presetname='%s%s'%(bankLetter, preset), note=note)
# exit()

'''
EXAMPLE - Clavia Nord Drum 3P

Example for Sampling Presets 'A1' to 'D50' of Clavia Nord Drum 3P all 6 Pads
at 44.1 KHz, 24 Bit, Stereo with 127 Velocity Levels. Results in 762 Files
per Preset ( x 50 x 4 ), 50 to 500 MB per Preset ( x 50 x 4 ). Automatic Recording
Time 15 to 60 Minutes per Preset ( x 50 x 4 ).
'''

for bank in range(0, 4):
    if bank==0:
        bankLetter='A'
    if bank==1:
        bankLetter='B'
    if bank==2:
        bankLetter='C'
    if bank==3:
        bankLetter='D'
    for preset in range(0, 50):
        sp.samplePreset(preset=[bank, preset], presetname='%s%s'%(bankLetter, preset+1), note=0)
        sp.samplePreset(preset=[bank, preset], presetname='%s%s'%(bankLetter, preset+1), note=1)
        sp.samplePreset(preset=[bank, preset], presetname='%s%s'%(bankLetter, preset+1), note=2)
        sp.samplePreset(preset=[bank, preset], presetname='%s%s'%(bankLetter, preset+1), note=8)
        sp.samplePreset(preset=[bank, preset], presetname='%s%s'%(bankLetter, preset+1), note=7)
        sp.samplePreset(preset=[bank, preset], presetname='%s%s'%(bankLetter, preset+1), note=10)
