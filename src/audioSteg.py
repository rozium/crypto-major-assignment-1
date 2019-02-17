#!/usr/bin/env python
import numpy as np
import scipy as sp
import scipy.io.wavfile
import wave

terminal = b'marvin'

# return bytes of an audio file
def read_audio_bytes(filename):
  audio_file = wave.open(filename, 'rb')
  audio_bytes = bytearray(audio_file.readframes(audio_file.getnframes()))
  audio_file.close()
  return audio_bytes

# return message size supported by an audio file
def get_audio_capacity(filename):
  audio_bytes = read_audio_bytes(filename)
  return int(len(audio_bytes) / 8) - len(terminal)

def get_audio_params(filename):
  audio_file = wave.open(filename, 'rb')
  return audio_file.getparams()

def read_message_bytes(filename):
  message_file = open(filename, 'rb')
  message_bytes = message_file.read()
  message_file.close()
  return message_bytes

def get_message_size(filename):
  return len(read_message_bytes(filename))

def write_audio_bytes(filename, audio_bytes, audio_params):
  with wave.open(filename, 'wb') as output_file:
    output_file.setparams(audio_params)
    output_file.writeframes(audio_bytes)

def write_message_bytes(filename, message_bytes):
  with open(filename, 'wb') as output_file:
    output_file.write(message_bytes)

# return array of bits from a message
def message_to_bits(message_bytes):
  return list(map(int, ''.join([bin(i).lstrip('0b').rjust(8, '0') for i in message_bytes])))

# return audio bytes embedded with message bits
def embed_message(message_bits, audio_bytes):
  for i, b in enumerate(message_bits):
    audio_bytes[i] = (audio_bytes[i] & 254) | b
  return bytearray(audio_bytes)

def extract_message(audio_bytes):
  extracted_bytes = [audio_bytes[i] & 1 for i in range(len(audio_bytes))]
  extracted_message = "".join(list(map(str, extracted_bytes)))
  message_bytes = bytes(int(extracted_message[i : i + 8], 2) for i in range(0, len(extracted_message), 8))
  return message_bytes.split(terminal)[0]

def stego_embed(audio_file, message_file, stego_file):
  print(len(read_audio_bytes(audio_file)))
  print(get_message_size(message_file))
  print(get_audio_capacity(audio_file))
  if (get_message_size(message_file) < get_audio_capacity(audio_file)):
    audio_bytes = read_audio_bytes(audio_file)
    audio_params = get_audio_params(audio_file)

    message_bytes = read_message_bytes(message_file)
    message_bytes = message_bytes + terminal
    message_bits = message_to_bits(message_bytes)

    stego_audio_bytes = embed_message(message_bits, audio_bytes)
    write_audio_bytes(stego_file, stego_audio_bytes, audio_params)
    return True
  else:
    return False

def stego_extract(stego_file, message_file):
  audio_bytes = read_audio_bytes(stego_file)
  message = extract_message(audio_bytes)
  write_message_bytes(message_file, message)

audio_file = '../input/audio/03mono.wav'
message_file = '../input/message/index.php'
stego_file = '../output/audio/stego03timber.wav'
ext_message_file = '../output/message/ext_index.dat'

# if stego_embed(audio_file, message_file, stego_file):
#   print('Success')
#   stego_extract(stego_file, ext_message_file)
# else:
#   print('Message is to big')

# f = wave.open(audio_file, 'rb')
audio_bytes = read_audio_bytes(audio_file)
print(len(audio_bytes))
rate, channels = sp.io.wavfile.read(audio_file)
print(rate)
print(len(channels.shape))
