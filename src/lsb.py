import numpy as np
import ffmpeg, os, uuid, shutil, subprocess, random
from PIL import Image
from math import log

SEQUENTIAL = 0
SHUFFLE = 1

class LSB:
  def __init__(self):
    # cover object related
    self.cover_object = None
    self.cover_object_path = "../example/avi/drop.avi"
    # stego object related
    self.stego_object_type = "video" # ["video", "audio"]
    self.stego_object = None
    self.stego_key = None
    self.stego_object_path = "../example/avi/output.avi"
    self.png_frame_path = "../tmp"
    # message related
    self.message = ""
    self.additional_message = ""
    self.message_path = "../example/message/msg.txt"
    self.message_length = 0
    self.message_file_format = ""
    self.message_output_path = "../example/message/"
    self.message_output_filename = "output"
    # key related
    self.key = "KEY"
    self.stego_key = 0
    # stego info related
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

  def get_cover_object_capacity(self):
    # get payload size from self.cover_object in bit
    # lsb_bit_size * number of frame * height of frame * width of frame * 3 pixel channel (rgb)
    return self.lsb_bit_size * self.cover_object.shape[0] * self.cover_object.shape[1] * self.cover_object.shape[2] * self.cover_object.shape[3]

  def load_message(self):
    # (1) get stego info (frame, pixel, encrypt, LSB size)
    # stego mode info (4 bits) : [frame, pixel, encrypt, LSB size]
    # frame => 0 : sequential, 1 : shuffle
    # pixel => 0 : sequential, 1 : shuffle
    # encrypt => 0 : not encrypted, 1 : encrypted
    # LSB size => 0 : 1 bit, 1 : 2 bits
    # (2) get format (how many bytes needed to store + length of message in binary) and length of message (how many bytes needed to store + length of message in binary)
    # format : (1 + m) bytes, length of message : (1 + n) bytes
    # (3) get string of bit from message file content and save to self.message
    # (4) append (1) and (2) and save to self.additional_message
    # TODO: encrypt message

    # open file
    with open(self.message_path, mode='rb') as file:
      file_content = file.read()

    # encrypt message
    # if self.is_message_encrypted:
      # file_content = encrypt(file_content)

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
    
    # self.message contains bits (0 or 1) string of message content
    self.message = content

    # self.additional_message contains bits (0 or 1) string of stego info, format & message length representation
    self.additional_message = stego_info + format(format_file_bytes_needed, '08b') + format(message_len_bytes_needed, '08b') + format_file_as_bit + message_len_as_bit

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
    # index = 0 for LSB
    mask = 1 << index
    val &= ~mask
    if x:
      val |= mask
    return val 

  def __msg_operation_stego_object(self, mode, is_additional, message = '', used_pixel = []):
    # mode in ['insert', 'get']

    random.seed(self.stego_key)
    count_frames = len(self.stego_object)
    count_rows_per_frame = len(self.stego_object[0])
    count_cols_per_frame = len(self.stego_object[0][0])

    frame_idx_arr = np.arange(0, count_frames, 1)
    row_idx_arr = np.arange(0, count_rows_per_frame, 1)
    col_idx_arr = np.arange(0, count_cols_per_frame, 1)

    if not is_additional:
      if self.frame_store_mode == SHUFFLE:
        frame_idx_arr = np.asarray(random.sample(range(count_frames), count_frames))

      if self.pixel_store_mode == SHUFFLE:
        row_idx_arr = np.asarray(random.sample(range(count_rows_per_frame), count_rows_per_frame))
        col_idx_arr = np.asarray(random.sample(range(count_cols_per_frame), count_cols_per_frame))

    used_pixel_return = []
    message_result = ''
    idx_msg = 0
    if mode == "insert":
      message_length = len(message)
    else: # mode == "get"
      if is_additional:
        message_length = 20 # stego info (4 bits) + format_file_bytes_needed (8 bits) + message_len_bytes_needed (8 bits)
      else:
        message_length = self.message_length
    while idx_msg < message_length:
      for idx_frame in frame_idx_arr:
        for idx_row in row_idx_arr:
          for idx_col in col_idx_arr:
            for i in range(0, 3): #rgb channel
              if idx_msg < message_length and (idx_frame, idx_row, idx_col, i) not in used_pixel:
                if not is_additional and self.lsb_bit_size == 2 and (message_length - idx_msg >= 2):
                  # lsb 2 bits
                  if mode == "insert":
                    self.stego_object[idx_frame][idx_row][idx_col][i] = self.__set_bit(self.stego_object[idx_frame][idx_row][idx_col][i], 1, int(message[idx_msg]))
                  else: # mode == "get"
                    message_result += str((self.stego_object[idx_frame][idx_row][idx_col][i] >> 1) & 1)
                  # if is_additional:
                  #   used_pixel_return.append((idx_frame, idx_row, idx_col))
                  idx_msg += 1
                if mode == "insert":
                  self.stego_object[idx_frame][idx_row][idx_col][i] = self.__set_bit(self.stego_object[idx_frame][idx_row][idx_col][i], 0, int(message[idx_msg]))
                else: # mode == "get"
                  message_result += str(self.stego_object[idx_frame][idx_row][idx_col][i] & 1)
                  if is_additional and (idx_msg == 19):
                    # add message length with format_file_bytes_needed (in bit) + message_len_bytes_needed (in bit)
                    format_file_bytes_needed = int(message_result[4:-8], 2)
                    message_len_bytes_needed = int(message_result[-8:], 2)
                    message_length += format_file_bytes_needed*8 + message_len_bytes_needed*8
                if is_additional:
                  used_pixel_return.append((idx_frame, idx_row, idx_col, i))
                idx_msg += 1
              else:
                break
            if idx_msg >= message_length:
              break
          if idx_msg >= message_length:
            break
        if idx_msg >= message_length:
          break
    
    if mode == "insert":
      if is_additional:
        return used_pixel_return
    else: # mode == "get"
      if is_additional:
        return used_pixel_return, message_result
      else: # is_additional == False
        return message_result

  def put_message(self):
    # put message to self.cover_object and save to self.stego_object
    
    # initialize
    self.stego_object = np.copy(self.cover_object)

    # put additional_message first
    used_pixel = self.__msg_operation_stego_object("insert", True, self.additional_message)

    # checking message size and capacity
    capacity = self.get_cover_object_capacity()
    additional_message_size = len(self.additional_message) * self.lsb_bit_size

    print "[LOG]", "capacity:", capacity
    print "[LOG]", "cover object shape:", self.cover_object.shape
    print "[LOG]", "additional_message_size:", additional_message_size
    print "[LOG]", "message_size:", len(self.message)

    if capacity - additional_message_size >= len(self.message):
      # put message content
      self.__msg_operation_stego_object("insert", False, self.message, used_pixel)
      return True
    else:
      return False

  def __extract_additional_message(self):
    # extract additional message from stego object

    # init
    used_pixel, additional_message = self.__msg_operation_stego_object("get", True)
    stego_info = additional_message[:4]
    format_file_bytes_needed = int(additional_message[4:12], 2)
    message_len_bytes_needed = int(additional_message[12:20], 2)
    format_file_as_bit = additional_message[20:20+format_file_bytes_needed*8]
    message_len_as_bit = additional_message[-1*message_len_bytes_needed*8:]

    # stego info
    self.frame_store_mode = SHUFFLE if stego_info[0] == '1' else SEQUENTIAL
    self.pixel_store_mode = SHUFFLE if stego_info[1] == '1' else SEQUENTIAL
    self.is_message_encrypted = True if stego_info[2] == '1' else False
    self.lsb_bit_size = 2 if stego_info[3] == '1' else 1

    # message file format
    self.message_file_format = ""
    bytes_char = [format_file_as_bit[i:i+8] for i in range(0, len(format_file_as_bit), 8)]
    for byte in bytes_char:
      self.message_file_format += chr(int(byte, 2))

    # message content length
    self.message_length = int(message_len_as_bit, 2)*8
    
    return used_pixel

  def get_message(self):
    # TODO: decrypt message
    # extract message form self.stego_object and save as file

    # extract additional message first
    used_pixel = self.__extract_additional_message()
    # extract message content
    result_as_bits = self.__msg_operation_stego_object("get", False, used_pixel = used_pixel)
    # convert bits to chars
    result = ''
    bytes_char = [result_as_bits[i:i+8] for i in range(0, len(result_as_bits), 8)]
    for byte in bytes_char:
      result += chr(int(byte, 2))

    # decrypt message
    # if self.is_message_encrypted:
      # result = decrypt(result)

    # save as file
    filepath = self.message_output_path + self.message_output_filename + "." + self.message_file_format
    f = open(filepath, 'wb')
    f.write(result)
    f.close()

    
