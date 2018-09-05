import socket
import cv2
import numpy as np
from communication import Reciever
from PIL import Image
from PIL import ImageTk
import tkinter as tk

# Creating reciever object for recieve image from TCP socket
reciever = Reciever("localhost",8000)

"""Set up GUI"""

# Set up main window
root = tk.Tk() 
# Set window title
root.wm_title("Ovality Detection") 

"""Graphics window"""

imgFrame = tk.Frame(root, width=800, height=600)
imgFrame.grid(row=0, column=0, padx=10, pady=2)

# Set up label which contains the recieved frame
imgLabel = tk.Label(imgFrame)
# Place Label on window
imgLabel.grid(row=0, column=0)


def display_frame():
    """function that recieves image from client and display it on GUI"""
    try:
        # Recieve image from client
        img = reciever.recv_image()
        # Convert image to displayable on GUI
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        # Assign image to label
        imgLabel.imgtk = imgtk
        imgLabel.configure(image=imgtk)
        imgLabel.after(10, display_frame) 
    except ConnectionAbortedError as e:
        print(e)

display_frame()
#Starts GUI
root.mainloop()  

cv2.waitKey(0)
cv2.destroyAllWindows()