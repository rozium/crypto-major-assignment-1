#!/usr/bin/env python

# Audio Steganography

import wave
f = wave.open('./example/wav/1.wav', 'rb')
fb = bytearray(list(f.readframes(f.getnframes())))

# embed
s = 'secret message'
s = s + int((len(fb)-(len(s)*8*8))/8) * '#'
bs = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in s])))
for i, b in enumerate(bs):
  fb[i] = (fb[i] & 254) | b
fm = bytes(fb)

# extract
lsb = [fb[i] & 1 for i in range(len(fb))]
s = ''.join(chr(int(''.join(map(str,lsb[i:i+8])),2)) for i in range(0,len(lsb),8)).split('###')[0]
print s