import numpy as np
import ffmpeg, os, uuid, shutil, subprocess
from PIL import Image

class LSB:
  def __init__(self):
    self.cover_object = None
    self.cover_object_fps = 0
    self.cover_object_path = "../example/avi/drop.avi"
    self.stego_object_type = "video" # ["video", "audio"]
    self.stego_object = None
    self.stego_key = None
    self.stego_object_path = "../example/avi/output.avi"
    self.png_frame_path = "../tmp"
    self.message = None
    self.message_path = "../example/message/msg.txt"
    self.lsb_bit_size = 1 # [1, 2]

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
    # get string of bit from message file and save to self.message

    # open file
    with open(self.message_path, mode='rb') as file:
      file_content = file.read()

    # read as 8 bits per character
    result = ''
    for c in file_content:
      result += format(ord(c), '08b')
    
    # self.message contains bits (0 or 1) string of message
    self.message = result

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

  def put_message(self):
    # TODO: suffle mode & 2 bits LSB, save message length & format
    # put message to self.cover_object and save to self.stego_object
    self.stego_object = np.copy(self.cover_object)
    idx_msg = 0
    while idx_msg < len(self.message):
      for idx_img, image in enumerate(self.stego_object):
        for idx_row, row in enumerate(image):
          for idx_col, col in enumerate(row):
            for i in range(0, 3): #rgb channel
              if idx_msg < len(self.message):
                if self.message[idx_msg] == '1':
                  if self.stego_object[idx_img][idx_row][idx_col][i] % 2 == 0:
                    self.stego_object[idx_img][idx_row][idx_col][i] += 1
                else:
                  if self.stego_object[idx_img][idx_row][idx_col][i] % 2 == 1:
                    self.stego_object[idx_img][idx_row][idx_col][i] -= 1
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
    # TODO: suffle mode & 2 bits LSB, save message length & format
    # extract message form self.stego_object
    result = ''
    idx_msg = 0
    while idx_msg < len(self.message):
      for idx_img, image in enumerate(self.stego_object):
        for idx_row, row in enumerate(image):
          for idx_col, col in enumerate(row):
            for i in range(0, 3): #rgb channel
              if idx_msg < len(self.message):
                result += str(self.stego_object[idx_img][idx_row][idx_col][i] & 1)
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

    
