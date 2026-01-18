import sounddevice as sd
import soundfile as sf

AUDIO_PATH = "/home/antisocialartificers/Downloads/converted_sng.wav"
data, fs = sf.read(AUDIO_PATH, dtype="float32")
sd.play(data, fs)
sd.wait()
