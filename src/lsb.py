import numpy as np
import ffmpeg, os, uuid, shutil, subprocess, random
from PIL import Image
from math import log

SEQUENTIAL = 0
SHUFFLE = 1

class LSB:
  def __init__(self):
    self.cover_object = None
    # self.cover_object_fps = 0
    self.cover_object_path = "../example/avi/drop.avi"
    self.stego_object_type = "video" # ["video", "audio"]
    self.stego_object = None
    self.stego_key = None
    self.stego_object_path = "../example/avi/output.avi"
    self.png_frame_path = "../tmp"
    self.message = None
    self.message_path = "../example/message/msg.txt"
    self.key = "KEY"
    self.stego_key = 0
    # stego info
    self.lsb_bit_size = 1 # [1, 2]
    self.frame_store_mode = SEQUENTIAL
    self.pixel_store_mode = SEQUENTIAL
    self.is_message_encrypted = True

  def load_object(self, object_type):
    # load cover / stego object video and save to self.cover_object / self.stego_object as array of image (rgb)
    if object_type == 'cover':
      path = self.cover_object_path
    else:
      path = self.stego_object_path

    # get video size
    command = [ 'ffprobe',
      '-v', 'error',
      '-select_streams', 'v:0',
      '-show_entries', 'stream=width,height',
      '-of', 'csv=s=x:p=0',
      path]
    cmd_out, cmd_error = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()
    width, height = cmd_out.split("x")

    # extract frames
    out, _ = (
      ffmpeg
      .input(path)
      .output('pipe:', format='rawvideo', pix_fmt='rgb24')
      .run(capture_stdout=True)
    )
    frames = (
      np
      .frombuffer(out, np.uint8)
      .reshape([-1, int(height), int(width), 3])
    )

    if object_type == 'cover':
      self.cover_object = np.copy(frames)
    else:
      self.stego_object = np.copy(frames)

  def get_payload_size(self):
    # get payload size from self.cover_object in bit
    # lsb_bit_size * number of image * height of image * width of image * 3 pixels (rgb)
    return self.lsb_bit_size * len(self.cover_object) * self.cover_object[0].shape[0] * self.cover_object[0].shape[1] * self.cover_object[0].shape[2]

  def load_message(self):
    # (1) get stego info (frame, pixel, encrypt, LSB size)
    # stego mode info (4 bits) : [frame, pixel, encrypt, LSB size]
    # frame => 0 : sequential, 1 : shuffle
    # pixel => 0 : sequential, 1 : shuffle
    # encrypt => 0 : not encrypted, 1 : encrypted
    # LSB size => 0 : 1 bit, 1 : 2 bits
    # (2) get format (how many bytes needed to store + length of message in binary) and length of message (how many bytes needed to store + length of message in binary)
    # format : (1 + m) bytes, length of message : (1 + n) bytes
    # (3) get string of bit from message file content
    # (4) append all of (1), (2), (3) and save to self.message
    # TODO: encrypt message

    # open file
    with open(self.message_path, mode='rb') as file:
      file_content = file.read()

    # read as 8 bits per character
    content = ''
    for c in file_content:
      content += format(ord(c), '08b')

    # get length of message & byte size
    message_len = len(file_content)
    message_len_bytes_needed = int(log(message_len, 256)) + 1
    message_len_as_bit = ("{0:0" + str(message_len_bytes_needed*8) +"b}").format(message_len)

    # get format message file
    format_file = self.message_path.split('.')[-1]
    format_file_bytes_needed = len(format_file)
    format_file_as_bit = ''
    for c in format_file:
      format_file_as_bit += format(ord(c), '08b')

    # get stego info
    stego_info = ''
    if self.frame_store_mode == SHUFFLE:
      stego_info += '1'
    else:
      stego_info += '0'
    if self.pixel_store_mode == SHUFFLE:
      stego_info += '1'
    else:
      stego_info += '0'
    if self.is_message_encrypted:
      stego_info += '1'
    else:
      stego_info += '0'
    if self.lsb_bit_size == 2 :
      stego_info += '1'
    else:
      stego_info += '0'
    
    # self.message contains bits (0 or 1) string of message
    self.message = stego_info + format(format_file_bytes_needed, '08b') + format_file_as_bit + format(message_len_bytes_needed, '08b') + message_len_as_bit + content

  def __stego_frame_to_png(self):
    # save self.stego_object (contains message) as png files that will be converted to video
    unique_dirname = '../tmp/' + str(uuid.uuid4())
    os.makedirs(unique_dirname)
    self.png_frame_path = unique_dirname
    count = 0
    for frame in self.stego_object:
      image = Image.fromarray(frame)
      image.save(unique_dirname + "/frame%d.png" % count)
      count += 1

  def save_stego_object(self):
    # convert self.stego_object to png files (contains message) and convert to video

    # save frames as png files
    self.__stego_frame_to_png()

    # convert to video
    # height, width, layers = self.cover_object[0].shape
    command = [ 'ffmpeg',
        '-y',
        '-i', self.png_frame_path + "/frame%d.png",
        '-vcodec', 'png',
        self.stego_object_path ]
    retcode = subprocess.call(command)

    # delete unused dir / png files
    shutil.rmtree(self.png_frame_path)

  def generate_stego_key(self):
    count = 0
    self.stego_key = 0
    for k in self.key:
      if count % 2 == 1:
        self.stego_key += ord(k)
      count +=1

    self.stego_key = int(self.stego_key / len(self.key))

  def __set_bit(self, val, index, x):
    # helper function
    # Set the index:th bit of val to x and return the new value.
    mask = 1 << index
    val &= ~mask
    if x:
      val |= mask
    return val 

  def put_message(self):
    # TODO: 2 bits LSB, save message length & format
    # put message to self.cover_object and save to self.stego_object

    self.stego_object = np.copy(self.cover_object)
    random.seed(self.stego_key)
    count_frames = len(self.stego_object)
    count_rows_per_frame = len(self.stego_object[0])
    count_cols_per_frame = len(self.stego_object[0][0])
      
    if self.frame_store_mode == SHUFFLE:
      frame_idx_arr = np.asarray(random.sample(range(count_frames), count_frames))
    else:
      frame_idx_arr = np.arange(0, count_frames, 1)

    if self.pixel_store_mode == SHUFFLE:
      row_idx_arr = np.asarray(random.sample(range(count_rows_per_frame), count_rows_per_frame))
      col_idx_arr = np.asarray(random.sample(range(count_cols_per_frame), count_cols_per_frame))
    else:
      row_idx_arr = np.arange(0, count_rows_per_frame, 1)
      col_idx_arr = np.arange(0, count_cols_per_frame, 1)

    idx_msg = 0
    while idx_msg < len(self.message):
      for idx_frame in frame_idx_arr:
        for idx_row in row_idx_arr:
          for idx_col in col_idx_arr:
            for i in range(0, 3): #rgb channel
              if idx_msg < len(self.message):
                self.stego_object[idx_frame][idx_row][idx_col][i] = self.__set_bit(self.stego_object[idx_frame][idx_row][idx_col][i], 0, int(self.message[idx_msg]))
                idx_msg += 1
              else:
                break
            if idx_msg >= len(self.message):
              break
          if idx_msg >= len(self.message):
            break
        if idx_msg >= len(self.message):
          break

  def get_message(self):
    # TODO: extract & use stego info, format & message length
    # TODO: 2 bits LSB
    # extract message form self.stego_object
    result = ''

    random.seed(self.stego_key)
    count_frames = len(self.stego_object)
    count_rows_per_frame = len(self.stego_object[0])
    count_cols_per_frame = len(self.stego_object[0][0])
      
    if self.frame_store_mode == SHUFFLE:
      frame_idx_arr = np.asarray(random.sample(range(count_frames), count_frames))
    else:
      frame_idx_arr = np.arange(0, count_frames, 1)

    if self.pixel_store_mode == SHUFFLE:
      row_idx_arr = np.asarray(random.sample(range(count_rows_per_frame), count_rows_per_frame))
      col_idx_arr = np.asarray(random.sample(range(count_cols_per_frame), count_cols_per_frame))
    else:
      row_idx_arr = np.arange(0, count_rows_per_frame, 1)
      col_idx_arr = np.arange(0, count_cols_per_frame, 1)

    idx_msg = 0
    while idx_msg < len(self.message):
      for idx_frame in frame_idx_arr:
        for idx_row in row_idx_arr:
          for idx_col in col_idx_arr:
            for i in range(0, 3): #rgb channel
              if idx_msg < len(self.message):
                result += str(self.stego_object[idx_frame][idx_row][idx_col][i] & 1)
                idx_msg += 1
              else:
                break
            if idx_msg >= len(self.message):
              break
          if idx_msg >= len(self.message):
            break
        if idx_msg >= len(self.message):
          break

    return result

    
