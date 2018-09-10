from threading import Thread
import numpy as np
import socket
import cv2
import struct

class Transmitter(Thread):
    def __init__(self,HOST = "", PORT = 0):
        """HOST: str PORT: int"""
        Thread.__init__(self)
        self.address = (HOST,PORT)
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.socket.bind(self.address)
            self.socket.listen(1)
            self.con,add = self.socket.accept()
            self.connected = True
        except Exception as e:
            print(e)
            self.connected = False

    def send_image(self, img):
        """Sends OpenCV image over web socket connection"""
        try:
            # compress image to .png format and convert it to string
            img_str = cv2.imencode('.png', img)[1].tostring()
            # length of image string
            length = len(img_str)
            # pack length of image string to 4 bytes long byte array
            len_str = struct.pack('!i', len(img_str))
            #print('len:', len(img_str))

            # first send length of image string 
            self.con.send(len_str)

            # then send image string
            self.con.send(img_str);

        except Exception as e:
            self.con.close()
            self.connected = False
            raise ConnectionAbortedError("Transmitter Error: " + str(e) + " Connection Aborted!!!")
    
    def send_data(self, data):
        """Sends data over web socket connection"""
        try: 
            packed_data = struct.pack('!f', data)
            self.con.send(packed_data);
        except Exception as e:
            self.con.close()
            self.connected = False
            raise ConnectionAbortedError("Transmitter Error: " + str(e) + " Connection Aborted!!!")
    
    def reconnect(self):
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.bind(self.address)
        self.socket.listen(1)
        self.con,add = self.socket.accept()
        self.connected = True


class Reciever(Thread):
    def __init__(self, HOST = "", PORT = 0):
        """HOST: str PORT: int"""
        Thread.__init__(self)
        self.address = (HOST,PORT)
        self.connected = False
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        if HOST != "" and PORT != 0:
            try:
                self.socket.connect(self.address)
                self.connected = True
            except Exception as e:
                print(e)
                self.connected = False

    def recv_image(self):
        """Recieves OpenCV image over web socket connection"""
        try:

            # empty byte array for recieving image
            img_str = b''

            # recieve length of image string
            data = self.socket.recv(4)

            # unpack bytes to integer
            size = struct.unpack('!i', data)[0]
            
            #print(size)

            while size > 0:

                if size >= 4096:
                    # recieve 4 KB of image
                    data = self.socket.recv(4096)
                else:
                    # recieve last part of image
                    data = self.socket.recv(size)

                if not data:
                    break

                size -= len(data)
                #concatenate recieved image packets
                img_str += data

            #convert string to numpy array
            nparr = np.fromstring(img_str, np.uint8)
            #convert array to image
            img_np = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            
            return img_np
        
        except Exception as e:
            print("Reciever Error:\n" +str(e))
            self.connected = False
            raise ConnectionAbortedError("Transmitter Error: " + str(e) + " Connection Aborted!!!")
    
    def recv_data(self):
        try:
            data = self.socket.recv(4)
            data = struct.unpack('!f', data)[0]
            return data
        except Exception as e:
            print("Reciever Error:\n" +str(e))
            self.connected = False
            raise ConnectionAbortedError("Transmitter Error: " + str(e) + " Connection Aborted!!!")
