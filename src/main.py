import lsb, random
import numpy as np

lsb_stego = lsb.LSB()

# config stego info
lsb_stego.frame_store_mode = lsb.SHUFFLE
lsb_stego.pixel_store_mode = lsb.SHUFFLE
lsb_stego.lsb_bit_size = 2
lsb_stego.is_message_encrypted = True

############### INSERT MESSAGE ###############
# input key
lsb_stego.key = "jangan dikasih tau"
lsb_stego.generate_stego_key()

# load cover object
lsb_stego.cover_object_path = "static/example/avi/drop.avi"
lsb_stego.load_object("cover")

# load message
lsb_stego.message_path = "static/example/message/msg.png"
lsb_stego.load_message()

# put message to cover object
success = lsb_stego.put_message()
if success:
  print "[STATUS] message size OK"
  # save cover object to video
  lsb_stego.stego_object_path = "static/example/avi/output.avi"
  lsb_stego.save_stego_object()
  # display psnr
  print "[LOG] psnr :", lsb_stego.calculate_psnr(), "dB"
else:
  print "[ERROR] message size > capacity"

if success:
  ############### EXTRACT MESSAGE ###############
  # load stego object
  lsb_stego.load_object("stego")

  # get hidden message and save it
  lsb_stego.message_output_path = "static/example/message/"
  lsb_stego.message_output_filename = "output"
  lsb_stego.get_message()
