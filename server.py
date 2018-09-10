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

        
        self.master = master
        self.hostvar = tk.StringVar(self.master, value = "localhost")
        self.portvar = tk.IntVar(self.master, value = "8000")
        self.distvar = tk.StringVar(self.master, value = "0")
        self.reciever = Reciever()
        # Set window title
        self.master.wm_title("Ovality Detection")

        self.imgFrame = tk.Frame(self.master, width=800, height=600)
        self.inputFrame = tk.Frame(self.master, width=200, height=600)
        self.statuFrame = tk.Frame(self.master, height=10)
        self.connectButton = tk.Button(self.inputFrame, text = "Connect", command = self.connect_click)
        self.disconnectButton = tk.Button(self.inputFrame, text = "Disconnect", command = self.disconnect_click)
        self.HOSTLabel = tk.Label(self.inputFrame,text = "Host: ")
        self.PORTLabel = tk.Label(self.inputFrame,text = "Port: ")
        self.distortionLabel = tk.Label(self.inputFrame, text = "Distortion:" )
        self.distValLabel = tk.Label(self.inputFrame, textvariable = self.distvar)
        self.HOST = tk.Entry(self.inputFrame, textvariable = self.hostvar)
        self.PORT = tk.Entry(self.inputFrame, textvariable = self.portvar)
        self.statubar = tk.Listbox(self.statuFrame, height = 3)

        # Layout
        self.imgFrame.grid(row=0, column=0, padx=2, pady=2)
        self.inputFrame.grid(row=0, column=1, padx=2, pady=2, sticky = tk.N)
        self.statuFrame.grid(row=1, column=0, columnspan = 2, padx=2, pady=2, sticky = tk.E + tk.W + tk.S)

        self.statubar.pack(fill = tk.BOTH)
        self.connectButton.grid(row = 2, column = 0, padx = 2, pady = 2)
        self.disconnectButton.grid(row = 2, column = 1, padx = 2, pady = 2)
        self.HOSTLabel.grid(row = 0, column = 0, padx = 2, pady = 2)
        self.PORTLabel.grid(row = 1, column = 0, padx = 2, pady = 2)
        self.HOST.grid(row = 0, column = 1, padx = 2, pady = 2)
        self.PORT.grid(row = 1, column = 1, padx = 2, pady = 2)
        self.distortionLabel.grid(row = 3, column = 0, padx = 2, pady = 2)
        self.distValLabel.grid(row = 3, column = 1, padx = 2, pady = 2)

        # Set up label which contains the recieved frame
        self.imgLabel = tk.Label(self.imgFrame)
        # Place Label on window
        self.imgLabel.grid(row=0, column=0)

        

    def display_frame(self):
        try:
            if self.reciever.connected:
                img = self.reciever.recv_image()
                data = self.reciever.recv_data()
                data = "% {0:0.2f}".format(float(data))
                self.distvar.set(data)
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
        except Exception as e:
            self.update_statu(e)
            self.reciever.connected = False

    def connect_click(self):
        if self.reciever.connected is False:
            try:
                self.reciever = Reciever(self.hostvar.get(), self.portvar.get())
                self.reciever.connected = True
                
            except Exception as e:
                self.update_statu(e)
                self.reciever.connected = False
                return
            else:
                self.update_statu("Connected.")
        else:
            self.update_statu("Already Connected!!!")

        

    def update_statu(self,msg):
        self.statubar.insert(tk.END, msg)
        self.statubar.see(tk.END)

    def disconnect_click(self):
        if self.reciever.connected is True:
            self.reciever = Reciever()
            self.reciever.connected = False
            self.update_statu("Disconnected.")
        else:
            self.update_statu("Already Disconnected!!!")

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