import queue
import sounddevice as sd
import soundfile as sf
import numpy as np
import os
import time
import rtmidi
import mido
import librosa


class Sampler:

    def __init__(self):
        self.md = MIDI('USB Midi 4i4o')
        self.ad = Audio(device=16, samplerate=44100, channels=2, inputChannels=[3, 4], subtype='PCM_16', midi=self.md)

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
        self.slagTime = 35 * 1
        self.startRecord = False

        def callback(indata, frames, timeCFFI, status):
            peak=np.average(np.abs(indata))*32*64
            if peak>=.5:
                self.startRecord=True
            if self.startRecord:
                self.q.put(indata.copy())
            bars="#"*int(128*64*peak/2**16)
            print('%s %s %s %04d %05d %s'%(fileprefix, note, velocity, frames, peak, bars))
            if peak<.5:
                self.slagTime -= 1
                if self.slagTime == 0:
                    self.record = False

        with sf.SoundFile(file, mode='x', samplerate=sd.default.samplerate, channels=self.channels_in, subtype=self.subtype) as f:
            with sd.InputStream(callback=callback):
                self.md.sendNote(channel, note, velocity)
                while self.record:
                    f.write(self.q.get())


sp = Sampler()

# Example for Sampling Preset 'A1' of Clavia Nord Drum 3P all 6 Pads at 44.1 KHz with 127 Velocity Levels
sp.samplePreset(preset=[0, 0], presetname='A1', note=0)
sp.samplePreset(preset=[0, 0], presetname='A1', note=1)
sp.samplePreset(preset=[0, 0], presetname='A1', note=2)
sp.samplePreset(preset=[0, 0], presetname='A1', note=8)
sp.samplePreset(preset=[0, 0], presetname='A1', note=7)
sp.samplePreset(preset=[0, 0], presetname='A1', note=10)
