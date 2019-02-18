import lsb, random
import numpy as np

lsb_stego = lsb.LSB()

# default lsb config
# lsb bit = 1
# frame mode = sequence
# pixel mode = sequence
# encryption = True
lsb_stego.frame_store_mode = lsb.SHUFFLE
lsb_stego.pixel_store_mode = lsb.SHUFFLE
lsb_stego.lsb_bit_size = 2
lsb_stego.key = "jangan dikasih tau"
lsb_stego.generate_stego_key()

# load cover object
lsb_stego.cover_object_path = "static/example/avi/drop.avi"
lsb_stego.load_object("cover")

# load message
lsb_stego.message_path = "static/example/message/msg.txt"
lsb_stego.load_message()

# put message to cover object
lsb_stego.put_message()

# save cover object to video
lsb_stego.stego_object_path = "static/example/avi/output.avi"
lsb_stego.save_stego_object()

# load stego object
lsb_stego.load_object("stego")

# get hidden message
print lsb_stego.get_message()
print "format:", lsb_stego.message_file_format
