import socket
import cv2
import numpy as np
from communication import Reciever
import tkinter as tk
from PIL import Image
from PIL import ImageTk



class GUI():
    """description of class"""

    def __init__(self, master):

        self.connected = False

        
        self.master = master
        self.hostvar = tk.StringVar(self.master, value = "localhost")
        self.portvar = tk.IntVar(self.master, value = "8000")
        self.reciever = Reciever()
        # Set window title
        self.master.wm_title("Ovality Detection")

        self.imgFrame = tk.Frame(self.master, width=800, height=600)
        self.inputFrame = tk.Frame(self.master, width=200, height=600)
        self.connectButton = tk.Button(self.inputFrame, text = "Connect", command = self.connect_click)
        self.HOSTLabel = tk.Label(self.inputFrame,text = "Host: ")
        self.PORTLabel = tk.Label(self.inputFrame,text = "Port: ")
        self.HOST = tk.Entry(self.inputFrame, textvariable = self.hostvar)
        self.PORT = tk.Entry(self.inputFrame, textvariable = self.portvar)

        # Layout
        self.imgFrame.grid(row=0, column=0, padx=2, pady=2)
        self.inputFrame.grid(row=0, column=1, padx=2, pady=2)
        self.connectButton.grid(row = 2, column = 0, padx = 2, pady = 2)
        self.HOSTLabel.grid(row = 0, column = 0, padx = 2, pady = 2)
        self.PORTLabel.grid(row = 1, column = 0, padx = 2, pady = 2)
        self.HOST.grid(row = 0, column = 1, padx = 2, pady = 2)
        self.PORT.grid(row = 1, column = 1, padx = 2, pady = 2)

        # Set up label which contains the recieved frame
        self.imgLabel = tk.Label(self.imgFrame)
        # Place Label on window
        self.imgLabel.grid(row=0, column=0)

        

    def display_frame(self):
        if self.connected:
            img = self.reciever.recv_image()
        else:
            img = np.zeros((600, 800, 1),np.uint8)
            img = cv2.flip(img,1)
        # Convert image to displayable on GUI
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        # Assign image to label
        self.imgLabel.imgtk = imgtk
        self.imgLabel.configure(image=imgtk)
        self.imgLabel.after(10, self.display_frame) 

    def connect_click(self):
        try:
            self.reciever = Reciever(self.hostvar.get(), self.portvar.get())
            self.connected = True
        except Exception as e:
            print(e)
            self.connected = False



# Creating reciever object for recieve image from TCP socket


"""Set up GUI"""

# Set up main window
root = tk.Tk() 


mygui = GUI(root)

mygui.display_frame()

"""Graphics window"""


#Starts GUI
root.mainloop()  

cv2.waitKey(1)
cv2.destroyAllWindows()