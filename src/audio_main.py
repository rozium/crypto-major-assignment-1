#!/usr/bin/env python
import random
import struct
import array

from audio_lsb import *
from vigenere import encrypt, decrypt

def create_seed(key):
    return sum([ord(i) for i in key])

def decide_flag(encrypted, randomized):
    flag = 0
    flag = flag | 1 if encrypted else flag
    flag = flag | 2 if randomized else flag
    return flag

def insert_message(audio_file, message_file, stego_file, encrypted=False, randomized=False, key=None):
    message = read_message_bytes(message_file)
    extension = get_message_extension(message_file)

    if encrypted:
        message = bytearray(encrypt(str(message), key))

    # get extraction flag and length for extension and message
    flag = decide_flag(encrypted, randomized)
    extension_length = len(extension)
    message_length = len(message)
    
    # convert to array of bits
    flag_bits = int_to_bits(flag) # 8 bits
    extension_length_bits = int_to_bits(extension_length)  # 8 bits
    extension_bits = bytes_to_bits(extension)
    message_length_bits = int_to_bits(message_length)
    message_length_flag = int_to_bits(int(len(message_length_bits) / 8)) # 8 bits
    message_bits = bytes_to_bits(message)

    # assemble arrays of bits to payload
    header = flag_bits + extension_length_bits + \
        extension_bits + message_length_flag + message_length_bits
    payload = header + message_bits

    if (len(payload) < get_audio_capacity(audio_file)):
        audio_bytes = read_audio_bytes(audio_file)
        audio_params = get_audio_params(audio_file)
        
        if randomized:
            random.seed(create_seed(key))
            initial_index = len(header)
            indexes = range(0, len(header)) + random.sample(range(initial_index, len(audio_bytes)), len(message_bits))
        else:
            indexes = range(0, len(payload))
        audio_bytes = put_message(audio_bytes, payload, indexes)
        write_audio_bytes(stego_file, audio_bytes, audio_params)
        return audio_bytes
    else:
        print('Not enough capacity')
        return False

def extract_message(stego_file, message_file, key=None):
    audio_bytes = read_audio_bytes(stego_file)    
    current_index = 0
    
    flag = get_message(audio_bytes, range(current_index, current_index + 8))[0]
    current_index = current_index + 8

    extension_length = get_message(audio_bytes, range(current_index, current_index + 8))[0]
    current_index = current_index + 8

    extension = get_message(audio_bytes, range(current_index, current_index + 8 * extension_length))
    current_index = current_index + 8 * extension_length
    
    message_length_flag = get_message(audio_bytes, range(current_index, current_index + 8))[0]
    current_index = current_index + 8
    
    message_length = int(get_message_in_bits_string(audio_bytes, range(current_index, current_index + 8 * message_length_flag)), 2)
    current_index = current_index + 8 * message_length_flag

    if (flag & 2) == 2: # randomized
        random.seed(create_seed(key))
        indexes = random.sample(
            range(current_index, len(audio_bytes)), 8 * message_length)
    else: #sequential
        indexes = range(current_index, current_index + 8 * message_length)
    message = get_message(audio_bytes, indexes)
    
    if (flag & 1) == 1:
        message = bytearray(decrypt(str(message), key))
    
    write_message_bytes(str(message_file + extension), message)
    return extension

# audio_file = '../input/audio/01stereo.wav'
# message_file = '../input/message/ktp.jpg'
# stego_file = '../output/audio/stego01seq.wav'
# ext_message_file = '../output/message/ext_ktp'
# key = 'vinjerdim'

# insert_message(audio_file, message_file, stego_file, True, True, key)
# extract_message(stego_file, ext_message_file, key)
