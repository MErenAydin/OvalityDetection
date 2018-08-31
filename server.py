import socket
import cv2
import numpy as np
from communication import Reciever

reciever = Reciever("localhost",8000)


while True:
    try:
        img = reciever.recv_image()
    except ConnectionAbortedError as e:
        print(e)
        break
    cv2.imshow("FINAL",img)
    if cv2.waitKey(1) & 0XFF == ord('q'):
        break


cv2.waitKey(0)
cv2.destroyAllWindows()
