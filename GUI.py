import cv2
import numpy as np 
import math
import glob

from Matcher import Matcher
# from analyzer import analyzer

class Circle(object):
    def __init__(self, radius, x, y, folder, color):
        self.r = radius
        self.x = x
        self.y = y
        self.folder = folder
        self.color = color
        self.panoWindow = self.folder + " panorama"
        self.pano = cv2.imread(self.folder + "_panorama.jpg")

    def draw(self, image):
        cv2.circle(image, (self.x, self.y), self.r, self.color, -1)

    def setColor(self, co):
        self.color = co

    def showPanorama(self):
        cv2.imshow(self.panoWindow, self.pano)
        cv2.waitKey(0)
        cv2.destroyWindow(self.panoWindow)

    def inCircle(self, point):
        if (point[0]-self.x)**2 + (point[1]-self.y)**2 < self.r**2:
            return True
        return False

class Arrow(object):
    def __init__(self, Circle, length, angle, size, color):
        self.size = size
        self.color = color
        self.circle = Circle
        self.angle = angle
        self.length = length
        self.x = int(Circle.x + length*math.cos(angle + 3*math.pi/2))
        self.y = int(Circle.y + length*math.sin(angle + 3*math.pi/2))


    def setSize(self, s):
        self.size = s

    def setLength(self, l):
        mult_constant = self.length * l
        self.x = int(self.circle.x + mult_constant*math.cos(self.angle + 3*math.pi/2))
        self.y = int(self.circle.y + mult_constant*math.sin(self.angle + 3*math.pi/2))

    def setColor(self, co):
        self.color = co

    def draw(self, image):
        # print (self.color)
        cv2.arrowedLine(image, (self.circle.x, self.circle.y), (self.x, self.y), self.color, self.size)
        # cv2.arrowedLine(image, (self.circle.x,self.circle.y), (100,100), (50, 50, 50), 10)



def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        for circle in circles:
            if circle.inCircle((x,y)):
                circle.showPanorama()

def getArrows(Cir, intervals):
    '''return a list of arrows pointing in all direction
    intervals defined how many arrows there are in a full circle'''
    angInterval = 2*math.pi/intervals
    center_x = Cir.x
    center_y = Cir.y
    arrowList = []
    for i in range(intervals):
        arrow = Arrow(Cir, 60, angInterval * i, 1, (200,200,200))
        arrowList.append(arrow)   
    return arrowList

def drawArrows(arrowL):
    ''' this function initialize all the arrows. All grey with length 1'''
    # arrowL = getArrow(Circle, interval)
    for arrow in arrowL:
        arrow.draw(img)

def setArrow(arrowL, index, thickness, color, length):
    ''' this function access an individual arrow and modify its 
    size, color, and magnitude'''
    arrowL[index].setSize(thickness)
    arrowL[index].setColor(color)
    arrowL[index].setLength(length)

def resetArrow(arrowL):
    for arrows in arrowL:
        for ind_arrow in arrows:
            ind_arrow.setColor((200,200,200))
            ind_arrow.setLength(60)

def drawCircle(circleL):
    for circle in circleL:
        circle.draw(img) 

# def normalize(prob):
#     return [float(i)/sum(prob) for i in prob]

def illustrateProb(circle, arrowsL, probsL):
    '''circleL is the list of circles in one region, and arrowsL are the 
    corresponding circles'''
    
    # Let the color range goes from 50 to 255. The higher it is the more
    # likely the robot is there
    minColor = 0
    maxColor = 255
    diff = maxColor - minColor
    totalMatches = sum(list(map(lambda x: x[0],probsL)))
    # Resetting the arrows
    # resetArrow(arrowsL)

    for circle_ind in range(len(probsL)):
        num_matches, list_of_probs = probsL[circle_ind]
        diffProb = max(list_of_probs) - min(list_of_probs)
        num_probs = len(list_of_probs)
        this_circles_arrows = arrowsL[circle_ind]
        circle[circle_ind].setColor(((num_matches/ totalMatches)*255, (num_matches/ totalMatches)*255,
                                    (num_matches/ totalMatches)*255))
        for j in range(num_probs ):
            this_prob = list_of_probs[j]
            color = (this_prob/diffProb * 255, 50, 50)
            mult = (num_matches/ totalMatches) * this_prob * 20
            setArrow(this_circles_arrows, j, 1, color, mult)

def readProb(filename):
    '''this funciton reads the content of a txt file, turn the data into  dictionaries of 
    circles'''
    file = open(filename, 'r') 
    content = file.read().split('\n')[:-1]
    probDict = {}
    counter = 0
    for i in range(len(content))[::6]:
        name = str(counter).zfill(4)
        L1 = list(map(float, content[i+1].replace('[','').replace(']','').split(',')))
        L2 = list(map(float, content[i+3].replace('[','').replace(']','').split(',')))
        L3 = list(map(float, content[i+5].replace('[','').replace(']','').split(',')))
        probDict[name] = [[float(content[i]), L1], [float(content[i+2]), L2], [float(content[i+4]), L3]]
        counter += 1
    return probDict

def readCommand(filename):
    '''this function reads the command list from the robot'''
    file = open(filename, 'r')
    content = file.read().split('\n')[:-1]
    commandDict = {}
    for data in content:
        commandDict[data[:4]] = str(data[-1])
    return commandDict

def Laplacian(imagePath):
    ''' this function calcualte the blurriness factor'''
    img = cv2.imread(imagePath, 0)
    var = cv2.Laplacian(img, cv2.CV_64F).var()
    return var


# Initiate Screen
img = np.zeros((540, 960, 3), np.uint8)
cv2.namedWindow('GUI')

res1 = 320
res2 = 240

# Initiating Circles and Matches
circle1 = Circle(50, 200, 200, 'spot_one', [150, 150, 150])
circle2 = Circle(50, 400, 200, 'spot_two', [150, 150, 150])
circle3 = Circle(50, 600, 200, 'spot_three', [150, 150, 150])
circles = [circle1, circle2, circle3]

# Initiating Arrows
arrows1 = getArrows(circle1, 25)
arrows2 = getArrows(circle2, 25)
arrows3 = getArrows(circle3, 25)

Arrows = [arrows1, arrows2, arrows3]

method = 'SURF'
previousProbs = [[0, [0] * 25 ], [0,[0] * 25 ] , [0,[0] * 25]]
commandList = readCommand('commands.txt')
probDict = readProb('out.txt')


# Outputting the Probability


for imagePath in glob.glob('cam1_img' + '/*.jpg'):
        # Initiating views
        img = np.zeros((540,960,3), np.uint8)
        novelView = cv2.imread(imagePath)
        groundTruth = cv2.imread(imagePath.replace('cam1_img', 'cam2_img'))


        # Read matching data
        p = probDict[imagePath.replace('cam1_img/', '').replace('.jpg', '')]
        
        # Accounting for Blur factor 
        blurFactor = Laplacian(imagePath)
        illustrateProb(circles, Arrows, p)

        # Drawing Circles
        drawCircle(circles)
        drawArrows(arrows1)
        drawArrows(arrows2)
        drawArrows(arrows3)
        cv2.putText(img, imagePath, (500,400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255),2)
        cv2.putText(img, commandList[imagePath.replace('.jpg', '').replace('cam1_img/', '')], (500, 500), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255), 2)
        cv2.putText(img, str(blurFactor), (500, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
        cv2.imwrite('visual/' + imagePath.replace('cam1_img/', ''), img)
        cv2.imshow('Visualization', img)
        cv2.imshow('Ground Truth', groundTruth)
        cv2.imshow('Novel', novelView)

cv2.destroyAllWindows()