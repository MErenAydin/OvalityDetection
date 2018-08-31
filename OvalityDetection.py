import cv2
import numpy as np
from videoCapture import VideoCapture
from communication import Transmitter
import time
#import sys
#import socket
#from communication import Reciever
#from communication import Transmitter
#import math
#import socket
#from PIL import Image

transmitter = Transmitter("localhost", 8000)

cap = cv2.VideoCapture("videoplayback_2.avi")


def create_mask(img,thickness):
    """function for creating mask to delete unused areas at frame"""
    mask = img.copy()
    

    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

    ret, mask = cv2.threshold(mask,255,0,cv2.THRESH_BINARY)
    x = len(mask)
    y = len(mask[0])
    cv2.circle(mask, (y//2, x//2), (x//2) - thickness // 2 , (255,255,255), thickness = thickness)
    return mask


def define_circle(p1, p2, p3):
    """
    Returns the center and radius of the circle passing the given 3 points.
    In case the 3 points form a line, returns (None, infinity).
    """
    temp = p2[0] * p2[0] + p2[1] * p2[1]
    bc = (p1[0] * p1[0] + p1[1] * p1[1] - temp) / 2
    cd = (temp - p3[0] * p3[0] - p3[1] * p3[1]) / 2
    det = (p1[0] - p2[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p2[1])

    if abs(det) < 1.0e-6:
        return (None, np.inf)

    # Center of circle
    cx = (bc*(p2[1] - p3[1]) - cd*(p1[1] - p2[1])) / det
    cy = ((p1[0] - p2[0]) * cd - (p2[0] - p3[0]) * bc) / det

    radius = np.sqrt((cx - p1[0])**2 + (cy - p1[1])**2)
    return ((cx, cy), radius)


def distance(a, b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]- b[1])**2)



q = 0
centers = []

while(cap.isOpened()):

    ret, frame = cap.read()
    
    if frame is not None:

        mask = create_mask(frame,len(frame[0])//4)

        
        img = frame.copy()
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        #img = cv2.bilateralFilter(img, 11,15,15)


        #cv2.imshow('unprocessed',img)

        #kernel = np.ones((3,3),np.uint8)
        #img = cv2.GaussianBlur(img,(3,3),0)
        #img = cv2.dilate(img, kernel,iterations = 1)
        #İmg = cv2.erode(img, kernel,iterations = 1)
        

        #img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,3,2)

        
        
        img = cv2.bitwise_and(img,mask)

        img = cv2.Canny(img,60,60)

        kernel = np.ones((5,5),np.uint8)
        img = cv2.dilate(img, kernel,iterations = 1)

        kernel = np.ones((6,6),np.uint8)
        img = cv2.erode(img, kernel,iterations = 1)
        #kernel = np.ones((3,3),np.uint8)
        #img = cv2.erode(img, kernel,iterations = 1)
        #img = cv2.Canny(img,60,60)


        
        points = np.nonzero(img)
        distances = []
        arctans = []
        if q == 5:
            q = 0
            centers = []
        for i in range(len(points[0])):
            arctans.append(np.floor(np.rad2deg(np.arctan2([points[0][i] - len(img)//2] , [points[1][i] -len(img[0])//2]))))
        
        a = img.copy()

        
        for i,j,k in zip(range(-150,181,10),range(-120,181,10),range(-90,181,10)):
            try:
                x = [points[0][arctans.index(i)],points[1][arctans.index(i)]]
                y = [points[0][arctans.index(j)],points[1][arctans.index(j)]]
                z = [points[0][arctans.index(k)],points[1][arctans.index(k)]]
                center,radius = define_circle((x),(y),(z))
                if center is not None and radius < len(img[0]) // 2\
                        and center[1] < len(img[0]) // 2 + 100 and center[1] > len(img[0]) // 2 - 100 \
                        and center[0] < len(img) // 2 +100 and center[0] > len(img) //2 -100:
                    cv2.circle(a,(x[1],x[0]),1,(255,255,255),3)
                    cv2.circle(a,(y[1],y[0]),1,(255,255,255),3)
                    cv2.circle(a,(z[1],z[0]),1,(255,255,255),3)
                    cv2.circle(a,(int(center[1]),int(center[0])),int(radius),(100,0,0))
                    centers.append(center)
            except Exception as e:
                pass
        if centers is not None:
            try:
                c1,c2 = int(np.mean(centers,axis = 0)[1]), int(np.mean(centers,axis = 0)[0])
                cv2.circle(a,(c1,c2),1,(255,0,0),3)
                for i in range(len(points[0])):
                    dist = distance((c1,c2), (points[1][i],points[0][i]))
                    distances.append(dist)
                print(np.std(distances))
            except:
                pass
        
        cv2.imshow("a",a)
        
        """
        for i,j,k in zip(range(20,181,60),range(40,181,60),range(60,181,60)):
            
            try:
                
                center,radius = define_circle((points[0][arctans.index(i)],points[1][arctans.index(i)]),
                                          (points[0][arctans.index(j)],points[1][arctans.index(j)]),
                                          (points[0][arctans.index(k)],points[1][arctans.index(k)]))
                if center is not None:
                    cv2.circle(a,(points[1][arctans.index(i)],points[0][arctans.index(i)]),1,(255,255,255),3)
                    cv2.circle(a,(points[1][arctans.index(j)],points[0][arctans.index(j)]),1,(255,255,255),3)
                    cv2.circle(a,(points[1][arctans.index(k)],points[0][arctans.index(k)]),1,(255,255,255),3)
                    cv2.circle(a,(int(center[1]),int(center[0])),int(radius),(100,0,0))
            
            except Exception as e:
                print(e)
            cv2.imshow("a",a)
        """
        #center, radius = define_circle((points[0][100],points[1][100]), (points[0][len(points[0])-100],points[1][len(points[1])-100]), (points[0][len(points[0])//2], points[1][len(points[1])//2]))
        #if center is not None:
        #    pass
            #cv2.circle(img,(points[1][100],points[0][100]),2,(255,255,255),10)
            #print(np.arctan([points[1][100] - 640 /points[0][100] - 480 ]))
            #cv2.circle(img,(points[1][len(points[1])-100],points[0][len(points[0])-100]),2,(100,100,100),2)
            #cv2.circle(img,( points[1][len(points[1])//2],points[0][len(points[0])//2]),2,(100,100,100),2)
            #cv2.circle(img,(int(center[1]),int(center[0])),int(radius),(100,100,100),3)
        q += 1
        try:
            transmitter.send_image(img)
        except ConnectionAbortedError as e:
            print(e)
            break
        

        #m_p= np.mean(points, axis = 1)
        
        #cv2.circle(img,(int(m_p[1]), int(m_p[0])),2,(255,255,255),3)
        



        """
        circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,0.1,2000,param1=50,param2=30,minRadius=0)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                cv2.circle(img,(i[0],i[1]),i[2],(100,10,0),2)
                cv2.circle(img,(i[0],i[1]),2,(255,0,10),3)
        """

        #cv2.imshow('processed',img)
        
    else:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()






"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
        h, s, v = cv2.split(hsv)
        h.fill(255)
        s.fill(255)
        hsv = cv2.merge([h, s, v])
        out = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        kernel = np.ones((5,5),np.uint8)
        out = cv2.erode(out, kernel,iterations = 1)
        out = cv2.cvtColor(hsv, cv2.COLOR_BGR2GRAY)
        out = cv2.adaptiveThreshold(out, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
        
        cv2.imshow("red",out)
"""


"""
        r = frame.copy()
        # set blue and green channels to 0
        r[:, :, 0] = 0
        r[:, :, 1] = 0

        cv2.imshow("r",r)
"""


"""
        im2, contours, hierarchy = cv2.findContours(img.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours,key = len)[len(contours)-15:]
        
        for c in contours:
            if cv2.contourArea(c) > 1000 and cv2.contourArea(c) < 2000:
                img = cv2.drawContours(img, contours, -1, (0,255,0), 3)
"""

"""
        img = cv2.GaussianBlur(img,(5,5),1)

        circles = cv2.HoughCircles(cimg,cv2.HOUGH_GRADIENT,.1,1000,param1=100,param2=50,minRadius=30)
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            cv2.circle(cimg,(i[0],i[1]),i[2],(255,255,0),2)
            cv2.circle(cimg,(i[0],i[1]),2,(255,0,255),3)
"""