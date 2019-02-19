#!/usr/bin/env python
import random

def caesar(char, key, opt):
    return chr(((ord(char) + opt * key) % 256))

def encrypt(string, key):
    result = []
    for i, ch in enumerate(string):
        k = ord(key[i % len(key)])
        result.append(caesar(ch, k, 1))
    return ''.join(result)

def decrypt(string, key):
    result = []
    for i, ch in enumerate(string):
        k = ord(key[i % len(key)])
        result.append(caesar(ch, k, -1))
    return ''.join(result)

# string = 'Siapakah namamu? Nama saya 123'
# key = 'ini kunci rahasiA'

# x = encrypt(string, key)
# print x
# print decrypt(x, key)