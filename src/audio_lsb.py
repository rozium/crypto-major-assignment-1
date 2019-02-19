#!/usr/bin/env python2
from audio_io import *

# return array of bits from a message
def bytes_to_bits(message_bytes):
  return list(map(int, ''.join([bin(i).lstrip('0b').rjust(8, '0') for i in message_bytes])))

def put_message(audio_bytes, message_bits, indexes):
  for i, b in zip(indexes, message_bits):
    audio_bytes[i] = (audio_bytes[i] & 254) | b
  return bytearray(audio_bytes)

def put_flag(audio_bytes, flag):
  message_bits = bytes_to_bits(flag)
  return put_message(audio_bytes, message_bits, range(0, 8))

def get_message(audio_bytes, indexes):
  message_bytes = [audio_bytes[i] & 1 for i in indexes]
  message_bytes = "".join(list(map(str, message_bytes)))
  message_bytes = bytes(int(message_bytes[i : i + 8], 2) for i in range(0, len(message_bytes), 8))
  return bytearray(message_bytes)

def get_flag(audio_bytes):
  return get_message(audio_bytes, range(0, 8))