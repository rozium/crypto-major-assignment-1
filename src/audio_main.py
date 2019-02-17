#!/usr/bin/env python
import random

from audio_lsb import *

def create_seed(key):
    return sum([ord(i) for i in key])

def insert_message(audio_file, message_file, stego_file, encrypted=False, randomized=False, key=None):
    message_extension = str.encode(get_message_extension(message_file))
    message_bytes = read_message_bytes(message_file)
    message_bytes = message_bytes + terminal + message_extension + terminal

    if (len(message_bytes) + 1 < get_audio_capacity(audio_file)):
        audio_bytes = read_audio_bytes(audio_file)
        audio_params = get_audio_params(audio_file)

        flag = 0
        flag = flag | 1 if encrypted else flag
        flag = flag | 2 if randomized else flag

        audio_bytes = put_flag(audio_bytes, bytes([flag]))
        message_bits = bytes_to_bits(message_bytes)
        if randomized:
            random.seed(create_seed(key))
            indexes = random.sample(range(8, len(audio_bytes)), len(message_bits))
        else:
            indexes = range(8, 8 + len(message_bits))
        audio_bytes = put_message(audio_bytes, message_bits, indexes)
        write_audio_bytes(stego_file, audio_bytes, audio_params)
        return True
    else:
        return False

def extract_message(stego_file, message_file, key=None):
    audio_bytes = read_audio_bytes(stego_file)
    flag = get_flag(audio_bytes)

    if (flag[0] & 2) == 2: # randomized
        random.seed(create_seed(key))
        indexes = random.sample(range(8, len(audio_bytes)), len(audio_bytes) - 8)
    else: #sequential
        indexes = range(8, len(audio_bytes))
    message_bytes = get_message(audio_bytes, indexes)
    chunks = message_bytes.split(terminal)
    write_message_bytes(message_file + chunks[1].decode('utf-8'), chunks[0])

audio_file = '../input/audio/04stereo.wav'
message_file = '../input/message/ptx01.mp3'
stego_file = '../output/audio/stego04ran.wav'
ext_message_file = '../output/message/ext_ptx'
key = 'vinjerdim'

if insert_message(audio_file, message_file, stego_file, True, True, key):
    print('Success')
    extract_message(stego_file, ext_message_file, key)
#   stego_extract(stego_file, ext_message_file, None)
# else:
#   print('Message is to big')