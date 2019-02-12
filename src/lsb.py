import cv2

class LSB:

  def __init__(self):
    self.cover_object = None
    self.stego_object_type = "video" # ["video", "audio"]
    self.message = None
    self.stego_object = None
    self.stego_key = None
    self.stego_object_path = "../example/avi/drop.avi"

  def video_to_images(self):
    vidcap = cv2.VideoCapture(self.stego_object_path)
    success,image = vidcap.read()
    count = 0
    self.stego_object = []
    while success:
      self.stego_object.append(image)
      success,image = vidcap.read()
      count += 1
    # self.stego_object contains array of image (rgb)
