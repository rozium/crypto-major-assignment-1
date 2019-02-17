#!/usr/bin/env python
import os.path
import wave

terminal = b'1HrmaL8c'

# return bytes of an audio file
def read_audio_bytes(filename):
  audio_file = wave.open(filename, 'rb')
  audio_bytes = bytearray(audio_file.readframes(audio_file.getnframes()))
  audio_file.close()
  return audio_bytes

# return message size supported by an audio file
def get_audio_capacity(filename):
  audio_bytes = read_audio_bytes(filename)
  return int(len(audio_bytes) / 8)

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

def get_message_extension(filename):
  return os.path.splitext(filename)[1]

def write_audio_bytes(filename, audio_bytes, audio_params):
  with wave.open(filename, 'wb') as output_file:
    output_file.setparams(audio_params)
    output_file.writeframes(audio_bytes)

def write_message_bytes(filename, message_bytes):
  with open(filename, 'wb') as output_file:
    output_file.write(message_bytes)
