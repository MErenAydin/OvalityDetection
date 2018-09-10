import cv2
import numpy as np
from videoCapture import VideoCapture
from communication import Transmitter
from datetime import datetime


HOST = "localhost"
PORT = 8000

# Creating transmitter object for transmit image from TCP socket
transmitter = Transmitter(HOST, PORT)

# Uncomment for starting video capturing
#cap = cv2.VideoCapture("videoplayback_2.avi")

# starting camera capturing
cap = cv2.VideoCapture(0)

def create_mask(img,thickness):
    """Function for creating mask to delete unused areas at frame"""

    mask = img.copy()
    # Take x and y resolution of frame
    x = len(mask)
    y = len(mask[0])
    # Create black image same size with camera frame
    mask = np.zeros((x, y, 1),np.uint8)
    # Create circle for mask using area
    cv2.circle(mask, (y//2, x//2), (x//2) - thickness // 2 , (255,255,255), thickness = thickness)
    return mask


def define_circle(p1, p2, p3):
    """
    Returns the center and radius of the circle passing the given 3 points.
    In case the 3 points form a line, returns (None, infinity).
    """

    temp = p2[0] * p2[0] + p2[1] * p2[1]
    # Calculate midpoint of two points
    bc = (p1[0] * p1[0] + p1[1] * p1[1] - temp) / 2
    # Calculate midpoint of other two points
    cd = (temp - p3[0] * p3[0] - p3[1] * p3[1]) / 2
    # Calculate determinant
    det = (p1[0] - p2[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p2[1])


    # If points are nearly form a line return None and infinity
    if abs(det) < 1.0e-6:
        return (None, np.inf)

    # Calculate coordinates of center of circle 
    cx = (bc*(p2[1] - p3[1]) - cd*(p1[1] - p2[1])) / det
    cy = ((p1[0] - p2[0]) * cd - (p2[0] - p3[0]) * bc) / det

    # Calculate radius of circle
    radius = np.sqrt((cx - p1[0])**2 + (cy - p1[1])**2)

    return ((cx, cy), radius)


def distance(a, b):
    """Returns distance between two given points"""
    return np.sqrt((a[0]-b[0])**2 + (a[1]- b[1])**2)

def skeletonize(img):
    """Returns a skeletonized version of OpenCV image"""

    img = img.copy()
    skel = img.copy()

    skel[:,:] = 0
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))

    while True:
        eroded = cv2.morphologyEx(img, cv2.MORPH_ERODE, kernel)
        temp = cv2.morphologyEx(eroded, cv2.MORPH_DILATE, kernel)
        temp  = cv2.subtract(img, temp)
        skel = cv2.bitwise_or(skel, temp)
        img[:,:] = eroded[:,:]
        if cv2.countNonZero(img) == 0:
            break

    return skel

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


# Counter for calculating mean of centers
fps = 0
q = 0
percentage = 0
centers = []
now = datetime.now()


while(cap.isOpened()):

    if not transmitter.connected:
        transmitter.reconnect()

    # Capture the frame
    ret, frame = cap.read()
    
    if frame is not None:
        if (datetime.now() - now).seconds >= 1:
            print(fps)
            fps = 0
            now = datetime.now()

        mask = create_mask(frame,len(frame[0])//4)

        
        img = frame.copy()
        # Flip image vertically
        img = cv2.flip(img, 1)
        # Convert image's color space to grayscale
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        
        # Apply mask to image
        img = cv2.bitwise_and(img,mask)

        # Apply Canny Edge Detection to image  
        img = cv2.Canny(img,60,60)

        # Morphological operations
        kernel = np.ones((5,5),np.uint8)
        img = cv2.dilate(img, kernel,iterations = 1)

        kernel = np.ones((6,6),np.uint8)
        img = cv2.erode(img, kernel,iterations = 1)

        img = skeletonize(img)

        # Find coordinates of white pixels
        points = np.nonzero(img)
        distances = []
        arctans = []
        
        # Take mean of 5 center 
        if q == 5:
            q = 0
            centers = []

        # Calculate every pixel's arctan to center of image.
        for i in range(len(points[0])):
            arctans.append(np.floor(np.rad2deg(np.arctan2([points[0][i] - len(img)//2] , [points[1][i] -len(img[0])//2])))[0])
        
        a = img.copy()
        
        # Scan the perimeter of the pipe in 30 by 30 degrees 
        for i,j,k in zip(range(-150,181,10),range(-120,181,10),range(-90,181,10)):
            try:# Get initial 3 points
                index_i = arctans.index(i)
                index_j = arctans.index(j)
                index_k = arctans.index(k)
                x = [points[0][index_i],points[1][index_i]]
                y = [points[0][index_j],points[1][index_j]]
                z = [points[0][index_k],points[1][index_k]]
                # Define the circle pass through from these three points
                center,radius = define_circle((x),(y),(z))

                if center is not None and radius < len(img[0]) // 2\
                        and center[1] < len(img[0]) // 2 + 100 and center[1] > len(img[0]) // 2 - 100 \
                        and center[0] < len(img) // 2 +100 and center[0] > len(img) //2 -100:
                    # Draw points and the circle
                    cv2.circle(a,(x[1],x[0]),1,(255,255,255),3)
                    cv2.circle(a,(y[1],y[0]),1,(255,255,255),3)
                    cv2.circle(a,(z[1],z[0]),1,(255,255,255),3)
                    cv2.circle(a,(int(center[1]),int(center[0])),int(radius),(100,0,0))
                    centers.append(center)
            except Exception as e:
                pass
        if centers is not None:
            
            # Calculate standard deviation of all points's distances from center
            try:
                c1,c2 = int(np.mean(centers,axis = 0)[1]), int(np.mean(centers,axis = 0)[0])
                cv2.circle(a,(c1,c2),1,(255,0,0),3)
                for i in range(len(points[0])):
                    dist = distance((c1,c2), (points[1][i],points[0][i]))
                    distances.append(dist)
                percentage = map(np.std(distances),1,48,0,100)
                print("% {0:0.2f}".format(percentage))
                
            except:
                pass
        
        #cv2.imshow("a",a)

        # Increase counters
        q += 1
        fps += 1
        # Send the image to Server
        try:
            transmitter.send_image(img)
            transmitter.send_data(percentage)
        except ConnectionAbortedError as e:
            print(e)

        
    else:
        break
    # wait 'q' key to break (NECESSARRY) 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
