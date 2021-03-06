from threading import Thread
import cv2

class VideoCapture():
    """Video capturing with opencv and threads"""
    def __init__(self, src=0, name="WebcamVideoStream", resolution = (800,600)):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        self.stream.set(3,resolution[0])
        self.stream.set(4,resolution[1])
        (self.grabbed, self.frame) = self.stream.read()
        # initialize the thread name
        self.name = name

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return (1, self.frame)

    def release(self):
        # indicate that the thread should be stopped
        self.stopped = True

    def isOpened(self):
        return not self.stopped
