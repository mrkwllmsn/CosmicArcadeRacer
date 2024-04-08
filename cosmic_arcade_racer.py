import gc
from cosmic import CosmicUnicorn, Channel
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN, PEN_P8
import random
import time
import math 
import machine
machine.freq(200000000) # The best clocks are over clocks. 
print("Cosmic Outrun v4 ")

#Raindrop
class Rn:
    x = 0
    y = 0
    v = 1
    tv = 5 #targetVelocity
    wind = 0

    def __init__(self, x=0, h=32):
        self.x = x
        self.h = h
        self.y = -int(random.random() * h*10) 

    def update(self):
        #If you're wondering, this is preloading the vars and functions, which speeds up micropython lookups a lot
        #local variables are good, classes and function names and global variables are slow and eat memory

        x = self.x
        y = self.y
        v = self.v
        h = self.h
        tv = self.tv #Target velocity
        wind = self.wind
        rd = random.random

        if(v < tv):
           v += 0.2 
        if(v > tv):
           v -= 0.2 

        y += int(v + wind*0.8)
        x += int(wind*0.3)
        if(y > h):
            y = -int(rd() * h*10)
            v = 1
        if(y < -4):
            y = -int(rd() * h*10)
            v = 1
        if(x > h):
            x = -int(rd() * h*10) 
            y = int(rd() * h) 
            v = 1
        if(x < -4):
            x = int(rd() * h*10) 
            y = int(rd() * h) 
            v = 1

        #set them back at the end 
        self.tv = tv
        self.x = x
        self.y = y
        self.v = v

    def draw(self, gfx, pen, wind=0):
        self.wind = wind
        gfx.set_pen(pen)
        gfx.pixel(int(self.x),int(self.y))
        self.update()
        return gfx
#Raining
class Rng:
    raindrops = []
    wind = 0
    framecount =0
    def __init__(self, gfx, pen, w=32):
        self.y = -int(random.random() * 100)
        self.gfx = gfx
        self.w = w
        self.pen = pen
        self.generateRainDrops()

    def generateRainDrops(self):
        self.raindrops = []
        w = self.w
        for x in range(w):
          self.raindrops.append(Rn(x))

    def draw(self):
        gfx = self.gfx
        p = self.pen
        wd = self.wind
        for drop in self.raindrops: 
            gfx = drop.draw(gfx, p, wd)
        return gfx




# Used to make the mountains on the horizon out of 3 sine waves
class Mountain:
  pointCloud = []
  lastPoint = (0,16)
  pCurve = -1 
  waveMod = -1
  gfx = None
  w = 32
  h = 32
  yoffset = 12
  xoffset = 0
  base = -100
  peak = 100
  currentHillHeight = 0
  def __init__(self,gfx, waveMod=4, hm=12, w=32,h=32):
      self.w = w
      self.h = h
      self.hm = hm
      self.gfx = gfx
      self.createPalette()
      self.generatePointCloud()
      self.waveMod = waveMod

  @micropython.native  
  def generatePointCloud(self, pCurve=0, waveMod=4, yoffset=12): 
      self.base = -1000
      self.peak = 1000

      if pCurve == self.pCurve and self.waveMod == waveMod:
        return
      self.waveMod = waveMod

      if(waveMod > self.currentHillHeight):
        self.currentHillHeight += 0.01
      if(waveMod < self.currentHillHeight):
        self.currentHillHeight -= 0.01

      self.yoffset = yoffset
      pointCloud = [(-1,yoffset)] # Start at the zeroeth pizel 
      self.pCurve = pCurve
      
      for j in range(0,self.w*2):
        j2,s2 = self.lastPoint
        s = int(math.cos(  self.pCurve*0.001 + j* 0.1)*self.currentHillHeight)
        if(int(s) <= 0):
          self.lastPoint = (j,s+self.yoffset)
          pointCloud.append(self.lastPoint)
        else:
          self.lastPoint = (j,int(-s*0.8)+self.yoffset)
          pointCloud.append(self.lastPoint)
      pointCloud.append((self.w,yoffset)) # Finish on the last pixel
      self.pointCloud = pointCloud 

  def updatePalette(self, colours):
      for (idx,p) in enumerate(self.greens):
        try:
          self.gfx.update_pen(p, *colours[idx])
        except IndexError:
          idc = True
          del idc

  @micropython.native  
  def createPalette(self):
     self.black = self.gfx.create_pen(0,0,0)
     self.white = self.gfx.create_pen(255,255,255)
     greens = [ (42, 170, 138), (26, 187, 43), (50, 205, 50), (1, 50, 32), (150, 255, 150), (71, 135, 120), ]
     self.greens = []
     for p in greens:
        r,g,b = p
        self.greens.append(self.gfx.create_pen(r,g,b))
        del r,g,b
     self.mountain = self.greens


  @micropython.native  
  def drawMountains(self, pen=None, outline=None, shade=None):
     if(pen == None):
        pen = self.white
    
     if(shade == None):
        shade = self.white

     gm = -14
     heightMod = int(self.w/2)
     lastPoint = (0,16)
    

     self.gfx.set_pen(pen)
     self.gfx.polygon(self.pointCloud)


     # draw a happy mountain 
     minY = 100
     maxY = -100
     for x,y in self.pointCloud:
        #self.gfx.set_pen(self.white)
        lx,ly = self.lastPoint

        if outline is not None and outline is not False:  
          self.gfx.set_pen(outline)
          self.gfx.pixel(x,y )
        #else: #looks like a mega plumber planet or whatever it's called
          #self.gfx.set_pen(self.black)
          #self.gfx.pixel(x,y )

        self.gfx.set_pen(self.mountain[0])
        if y < minY:
           minY = y
           if(minY < self.peak):
              self.peak = minY
        if y > maxY:
           maxY = y
           if(maxY > self.base):
              self.base = maxY

     #Using the highest and lowest points we now have, 
     #find the highest, and do some shading lines , 
     #the pointCloud is twice screen size so we see both 
     #waves when getting highest point in the pointCloud 

     for x,y in self.pointCloud:
        if(y > self.peak+1):
           self.gfx.set_pen(self.mountain[3])
           self.gfx.pixel(x,y) # shade edges 

        if(y ==  self.peak and y < 12):
           self.gfx.set_pen(self.mountain[1])
           self.gfx.pixel(x,y+1) # shade just under the peak 


     return self.gfx

# The player is called Car... deal with it. Short var names are best var names
class Car:
  red = None
  blue = None
  x=0
  y=0
  pCurvature = 0
  tCurvature = 0
  speed = 80
  gfx = None

  @micropython.native  
  def draw(self, gfx):
    gc.collect() #this makes a pretty big difference to mem usage and i can't really tell if its slower but take it out if you want
    gp = gfx.create_pen
    if self.red is None:
      self.red = gp(255,0,0)
      self.blue = gp(11,82,62)
      self.grey = gp(50,50,80)
      self.yellow = gp(255,255,0)
      self.red1 = gp(205,23,0)
      self.red2 = gp(105,0,0)
      self.white = gp(255,255,255)
      self.yellow = gp(255,255,0)
      self.brown = gp(160,82,45)
    self.h = 32
    self.w = 32
    self.gfx = gfx

    #car


    self.curveDiff =  int((self.pCurvature - self.tCurvature) * self.speed * 0.001)
    if(abs(self.curveDiff) > self.w*0.8):
        #self.speed *= 0.5
        #print("NEWSPEED:", self.speed)
        if self.speed < 1:
            self.speed = 0
       
    if self.speed < 10:
            self.speed = 0

    carpos = int(self.w/2)+4 + self.curveDiff  
    t = self.tCurvature
    p = self.pCurvature
    if(carpos < -4):
        carpos = -4
    if(carpos > 31):
        carpos = 31
    if(carpos < -4):
        carpos = -4 
        p = t  + self.w
        self.curveDiff =  int((p - t) * self.speed * 0.001)
    if(carpos > self.w-1):
        carpos = self.w-1 
        p = t + carpos
        p = t 
        self.curveDiff =  int((p - t) * self.speed * 0.001)
   
    gp = gfx.set_pen
    grect = gfx.rectangle 

    #print("curveDiff:", self.curveDiff, "carpos:", carpos)
    cary = int(self.h)-3
    gp(self.red1)
    grect(int(carpos), cary, 8, 1)
    gp(self.red2)
    grect(int(carpos), cary+1, 8, 1)
    grect(int(carpos), cary+2, 8, 1)
    gp(self.white)
    grect(int(carpos)+3, cary+1, 2, 1)

    #screen
    gp(self.blue)
    grect(int(carpos)+1, cary-1, 6, 1)

    #hair
    gp(self.yellow)
    grect(int(carpos)+1, cary-1, 2, 2)
    gp(self.brown)
    grect(int(carpos)+5, cary-1, 2, 2)

    #tyres

    gp(self.grey)
    grect(int(carpos), cary+2, 2, 1)
    grect(int(carpos)+6, cary+2, 2, 1)

    #lights
    
    gp(self.red)
    grect(int(carpos), cary, 2, 1)
    grect(int(carpos)+6, cary, 2, 1)
    self.gfx = gfx
    return gfx

# All the scenery is in road. Deal with that too
class Road:
  distance = 1
  theme = 'day'
  sceneChangeCount = 0 
  sceneChangeLast = 0 
  bHills = True 
  raintimer = 1
  fcurvature = 0 

  def __init__(self, graphics, w=32, h=32 ):
    self.themes = ['day', 'night', 'starrynight', 'vice', 'desert', 'daytoo', 'snow', 'f32', 'red'] 
    self.w = w
    self.fcurvature = 0.0
    self.sunSizeMod = 0
    self.mountains = True
    self.bSigns = False
    self.h = h
    self.bBoards = False
    self.bMoon = False
    self.bStars = False
    self.bSkyline = True
    self.gfx = graphics
    self.initPallette() 
    self.startTime = time.time()
    self.elapsedTime = 0
    self.setupColours()
    self.speed =  80
    self.roadcurve = 0
    self.curve = 0
    self.randomCurve = True
    self.sectionDistance = 0
    self.sectionLength = 4000
    self.tCurvature = 0
    self.pCurvature = 0
    self.mountain = Mountain(self.gfx,self.pCurvature,w,h)
    self.rain = None
    self.lastJ = -3
    self.skyline = True
    self.bank = 0
    self.bankTarget = 3

  def initStars(self):
      self.greyscale = [ (255,255,255), (100,100,100), (205,205,205),  (100, 80, 80) ] 
      self.starColours = []
      self.stars = []
      for i,c in enumerate(self.greyscale):
          r,g,b = c
          self.starColours.append(self.gfx.create_pen(r,g,b))

      w = self.w
      h = int(self.h/3)
      for x in range(-20, w+20):
          p = random.choice(self.starColours)
          y = int(random.random()*h)
          if(random.random() > 0.5):
            self.stars.append((x,y,p))


  def initPallette(self):
    gp = self.gfx.create_pen

    gc.collect()
    self.white = gp(255,255,255)
    self.black = gp(0,0,0)
    self.red = gp(255,0,0)
    self.blue = gp(0,0,255)
    self.mountains = False
    self.bSun = True
    self.skylineModifier = 1.2
    self.streetlamp = gp(255,155,0)
    self.banner =gp(107,1,125) 
    self.banner2 =gp(255,205,0) 
    self.bClouds = False
    self.skyColour = gp(22,26,164)
    self.bTrees = False
    self.bSigns = False
    self.bBoards = False
    self.bBushes = True
    self.shwStrLgts = False
    self.tree2 = gp(245,25,250)
    self.tree1 = gp(255,155,100)
    self.cactusColour = gp(0,105,30)
    self.horizon = gp(0,0,0)
    self.skylineColour =gp(10,10,17)
    self.cloudColour = gp(153,153,153)
    self.horizon = gp(51,51,51)
    self.grassColour1 = gp(0,255,0)
    self.grassColour2 =gp(106,1,125) 
    self.whitelines1 =gp(0,0,0) 
    self.whitelines2 =gp(100,100,100) 
    self.edgeCol = gp(255,0,0)
    self.edgeCol2 = gp(0,0,0)
    self.grassColour1 = gp(106,1,125)
    self.red = gp(206,0,0)
    self.grassColour2 = gp(93,177,220)
    self.skyColour = gp(255,51,51)
    self.newSCL = [ (238, 175, 97),
        (251, 144, 98),
        (238, 93, 108),
        (206, 73, 147),
        (106, 13, 131),
        (58, 13, 51),
        (68, 68, 68),
        (51, 51, 51),
        (17, 17, 17),
        (0, 0, 0)
    ]
    self.hillColours = [
       (42, 170, 138),
       (26, 187, 43),
       (50, 205, 50),
	     (1, 50, 32),
       (150, 255, 150),
       (71, 135, 120),
       ] # Green hill palette

    SCL = []
    for i,c in enumerate(self.newSCL):
        r,g,b = c
        SCL.append( self.updatePen(i, r,g,b))
        del r,g,b

    self.SCL = SCL
    self.moonColour = self.gfx.create_pen(255,255,255)
    self.initStars()
    
  def hex2rgb(self, h):
    h = h.replace('#', '')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

  def setupColoursF32(self):
    up = self.updatePen
    self.bSkyline = False
    self.bBoards = True
    self.hillColours =  [ (50,50,55), (60,60,105) , (100,100,120),(115,115,145) ,(115,120,155)] #Greys 
    self.hillHeight = 4

    self.skylineModifier = 2
    self.banner =up(self.banner ,200,0,0) 
    self.banner2 =up(self.banner2 ,255,255,255) 
    self.mountains = True
    self.bClouds = True
    self.bTrees = False
    self.bBushes = True
    self.shwStrLgts = False
    self.bSigns = False
    self.bMoon = False
    self.bStars = False
    self.lamppost = up(self.lamppost, 165,161,221) # brown lamp posts

    self.horizon = up(self.horizon ,255, 255, 255)
    self.bSun = True
    self.sunSizeMod = 6
    self.skyColour = up(self.skyColour ,10, 40, 255)
    self.skylineColour = up(self.skylineColour ,73, 73, 73)
    SCL = [
        (38, 75, 197), #sun1
        (12, 70, 197),#sun2
        (12, 70, 197),
        (98, 93, 229),
        (32, 67, 219),
        (28, 80, 197),
        (28, 100, 197),
        (28, 50, 197),
        (85, 85, 85),
    ]

    for i,c in enumerate(self.newSCL):
        r,g,b = c
        SCL[i] = up(i, r,g,b)
    self.SCL = SCL 
    # [(25, 69, 105), (95, 132, 162), (145, 174, 196), (183, 208, 225), (202, 222, 237), (219, 236, 244)]  #Winter blues
 
    self.grassColour1 = up(self.grassColour1 ,0, 132, 0)
    self.grassColour2 = up(self.grassColour2,  0,222, 0)

    #self.bushCol =up(self.bushCol , 219, 236, 244)
    self.bushCol =up(self.bushCol , 30, 30, 30)

    self.cloudColour = up(self.cloudColour ,255, 255, 255)
    self.moonColour = up(self.moonColour ,255, 255, 255)
    self.edgeCol = up(self.edgeCol ,255, 0, 0)
    self.edgeCol2 = up(self.edgeCol2 ,255, 255, 255)
    self.tree1 = up(self.tree1,130,82,45)
    self.tree2 = up(self.tree2, 0,200,40)



  def setupColoursRed(self):
    up = self.updatePen

    self.bSkyline = True
    self.bBoards = False
    self.hillColours= [ (156, 0, 1), (126, 24, 7), (94, 18, 3), (74, 15, 0), (55, 0, 0) ] #Darker red
    #self.hillColours = [ ( 150,47,33), ( 210,71,52), (255,116,0), (255,77,0), (255,0,0), ] #Fire RED palette  

    self.hillHeight = 2  #Big red mountains? 
    self.edgeCol = up(self.edgeCol , 155, 51, 0)
    self.edgeCol2 = up(self.edgeCol2 , 255, 255, 0)
    self.skylineModifier = 2
    self.banner =up(self.banner ,100,0,0) 
    self.banner2 =up(self.banner2 ,0,0,0) 
    self.mountains = True
    self.bClouds = False
    self.bTrees = False
    self.bBushes = False
    self.shwStrLgts = False
    self.bSigns = False
    self.bMoon = False
    self.bStars = False
    self.lamppost = up(self.lamppost, 0,0,0) # brown lamp posts
    self.horizon = up(self.horizon ,0, 0, 0)
    self.bSun = True
    self.sunSizeMod = 0
    self.skyColour = up(self.skyColour ,255, 0, 0)
    self.skylineColour = up(self.skylineColour ,73, 73, 0)
    #Sky colours
    self.newSCL = [
        (0, 0, 0), #sun1
        (212, 107, 7),#sun2
        (167, 0, 0),
        (219, 20, 0),
        (236, 83, 0),
        (242, 112, 6),
        (255, 141, 0),
        (0, 0, 0),
    ]

    for i,c in enumerate(self.newSCL):
        r,g,b = c
        self.SCL[i] = up(i, r,g,b)
    self.grassColour1 = up(self.grassColour1, 255,13,0)
    self.grassColour2 = up(self.grassColour2, 80,0,0)
    self.bushCol =up(self.bushCol , 255, 255, 0)
    self.cloudColour = up(self.cloudColour ,255, 255, 255)
    self.moonColour = up(self.moonColour ,255, 255, 255)
    self.tree1 = up(self.tree1,40,0,0) #trunk
    self.tree2 = up(self.tree2, 255,155,0) # leaves
    self.raintimer = time.time()
    self.rain = Rng(self.gfx,self.edgeCol2,self.w)


  def setupColoursSnow(self):
    up = self.updatePen
    self.raintimer = time.time()
    self.rain = Rng(self.gfx,self.white,self.w)

    self.bSkyline = True
    self.bBoards = False
    #self.hillColours = [(212, 224, 229), (184, 207, 213), (92, 140, 156), (92, 148, 164), (167, 164, 164)] #Snow palette  too light
    self.hillColours = [(106, 112, 114), (92, 103, 106), (46, 70, 78), (46, 74, 82), (255, 255, 255)] #Snow palette  @50% with 5 being snow tipped peaks 
    self.hillHeight = 8  #Big snowy mountains? 
    self.edgeCol = up(self.edgeCol , 51, 51, 68)
    self.edgeCol2 = up(self.edgeCol2 , 255, 255, 0)
    self.skylineModifier = 2
    self.banner =up(self.banner ,200,0,0) 
    self.banner2 =up(self.banner2 ,255,255,255) 
    self.mountains = True
    self.bClouds = True
    self.bTrees = False
    self.bBushes = False
    self.shwStrLgts = False
    self.bSigns = False
    self.bMoon = False
    self.bStars = False
    self.lamppost = up(self.lamppost, 165,161,221) # brown lamp posts
    self.horizon = up(self.horizon ,255, 255, 255)
    self.bSun = True
    self.sunSizeMod = 6
    self.skyColour = up(self.skyColour ,183, 208, 225)
    self.skylineColour = up(self.skylineColour ,73, 73, 73)
    self.newSCL = [
        (238, 175, 97), #sun1
        (12, 70, 197),#sun2
        (12, 70, 197),
        (198, 193, 229),
        (132, 167, 219),
        (128, 150, 197),
        (128, 150, 197),
        (128, 150, 197),
        (185, 85, 85),
    ]

    for i,c in enumerate(self.newSCL):
        r,g,b = c
        self.SCL[i] = up(i, r,g,b)

    self.grassColour1 = up(self.grassColour1 ,95, 132, 162)
    self.grassColour2 = up(self.grassColour2 ,202,222, 237)
    self.bushCol =up(self.bushCol , 219, 236, 244)
    self.cloudColour = up(self.cloudColour ,255, 255, 255)
    self.moonColour = up(self.moonColour ,255, 255, 255)
    self.edgeCol = up(self.edgeCol ,0, 0, 0)
    self.edgeCol2 = up(self.edgeCol2 ,255, 255, 255)
    self.tree1 = up(self.tree1,160,82,45)
    self.tree2 = up(self.tree2, 200,200,240)



  def setupColoursDayToo(self):
    up = self.updatePen

    self.bSkyline = True
    self.bBoards = False
    self.hillColours = [ 
      (66, 139, 16),
      (102, 177, 11),
      (139, 203, 35),
      (183, 233, 66),
    ]

    self.hillHeight = 8

    self.skylineModifier = 2
    self.banner =up(self.banner ,200,200,200) 
    self.banner2 =up(self.banner2 ,0,0,0) 
    self.mountains = True
    self.bClouds = True
    self.bTrees = False
    self.bBushes = True
    self.shwStrLgts = False
    self.bSigns = False
    self.bMoon = False
    self.bStars = False
    self.lamppost = up(self.lamppost, *(86,61,45)) # brown lamp posts
    self.horizon = up(self.horizon ,51, 51, 51)
    self.bSun = True
    self.skyColour = up(self.skyColour ,22, 26, 164)
    self.skylineColour = up(self.skylineColour ,73, 73, 73)
    self.newSCL = [
        (238, 175, 97), #sun1
        (12, 70, 197),#sun2
        (12, 70, 197),
        (98, 193, 229),
        (32, 167, 219),
        (28, 150, 197),
        (28, 150, 197),
        (28, 150, 197),
        (85, 85, 85),
    ]

    for i,c in enumerate(self.newSCL):
        r,g,b = c
        self.SCL[i] = up(i, r,g,b)
    self.grassColour1 = up(self.grassColour1 ,255, 213, 0)
    self.grassColour2 = up(self.grassColour2 ,145, 149, 54)
    self.bushCol =up(self.bushCol ,192,182,42) 
    self.cloudColour = up(self.cloudColour ,255, 255, 255)
    self.moonColour = up(self.moonColour ,255, 255, 255)
    self.edgeCol = up(self.edgeCol ,0, 0, 0)
    self.edgeCol2 = up(self.edgeCol2 ,255, 255, 255)
    self.tree1 = up(self.tree1,160,82,45)
    self.tree2 = up(self.tree2, 0,220,10)



  def setupColoursDay(self):
    up = self.updatePen
    self.bSkyline = True
    self.bBoards = False
    self.hillColours = [
         (42, 170, 138),
         (26, 187, 43),
         (50, 205, 50),
         (1, 50, 32),
         (150, 255, 150),
         (71, 135, 120),
         ] # Green pop hill palette


    self.hillHeight = 8

    self.skylineModifier = 2
    self.bushCol =up(self.bushCol ,0,255,100) 
    self.banner =up(self.banner ,200,200,200) 
    self.banner2 =up(self.banner2 ,0,0,0) 
    self.mountains = True
    self.bClouds = True
    self.bTrees = False
    self.bBushes = True
    self.shwStrLgts = False
    self.bSigns = False
    self.bMoon = False
    self.bStars = False
    self.lamppost = up(self.lamppost, 45,45,150)

    self.horizon = up(self.horizon ,51, 51, 51)
    self.bSun = True
    self.skyColour = up(self.skyColour ,22, 26, 164)
    self.skylineColour = up(self.skylineColour ,73, 73, 73)
    self.newSCL = [
        (238, 175, 97), #sun1
        (12, 70, 197),#sun2
        (12, 70, 197),
        (98, 193, 229),
        (32, 167, 219),
        (28, 150, 197),
        (28, 150, 197),
        (28, 150, 197),
        (85, 85, 85),
    ]

    for i,c in enumerate(self.newSCL):
        r,g,b = c
        self.SCL[i] = up(i, r,g,b)

    self.grassColour1 = up(self.grassColour1 ,0, 255, 17)
    self.grassColour2 = up(self.grassColour2 ,0, 68, 0)
    self.cloudColour = up(self.cloudColour ,255, 255, 255)
    self.moonColour = up(self.moonColour ,255, 255, 255)
    self.edgeCol = up(self.edgeCol ,0, 0, 0)
    self.edgeCol2 = up(self.edgeCol2 ,255, 255, 255)
    self.tree1 = up(self.tree1,160,82,45)
    self.tree2 = up(self.tree2, 0,220,10)


  def updatePen(self,colourIdx, r,g,b):
    if(colourIdx is None):
      idx = self.gfx.create_pen(r,g,b)
    elif(colourIdx > -1):
      self.gfx.update_pen(colourIdx,r,g,b)
      idx = colourIdx
    return idx


  def setupColoursStarryNight(self):
      up = self.updatePen
      self.bSkyline = True
      self.tree1 = up(self.tree1, 55,55,100)
      self.tree2 = up(self.tree2, 45,55,250)
      self.skylineColour = up(self.skylineColour , 10, 10, 50)
      self.bClouds = False
      self.bMoon = True
      self.bStars = True
      self.bSun = False
      self.bClouds = False
      self.bushCol =up(self.bushCol ,0,255,100) 
      self.edgeCol = up(self.edgeCol , 51, 51, 68)
      self.edgeCol2 = up(self.edgeCol2 , 255, 255, 0)
      self.grassColour1 = up(self.grassColour1 , 12, 20, 69)
      self.grassColour2 = up(self.grassColour2 , 51, 34, 77)
      self.lamppost = up(self.lamppost, 45,45,150)
      self.skyColourList = []
      self.horizon = up(self.horizon, 0,0,0)
      self.skyColourList = [ (0, 0, 0), (17, 17, 17), (34, 34, 34), (51, 51, 51), (68, 68, 68), (40,40,50), (30,30,40), (20,20,40)]
      self.hillHeight = 7
      self.hillColours = [ (42, 170, 138), (26, 187, 43), (50, 205, 50), (1, 50, 32), (150, 255, 150), (71, 135, 120), ] # starrynight hill palette


      for i,c in enumerate(self.skyColourList):
          self.SCL[i] = up(i, *c)

  def setupColoursDesert(self):
      up = self.updatePen
      self.bStars = False
      self.bSun = True
      self.rain = None
      self.bMoon = False
      self.bStars = False
      self.bClouds = False
      self.bSkyline = False
      self.sunSizeMod = 4
      self.bHills = True
      self.bTrees = False
      self.shwStrLgts = True #FIXME move all this into a theme config soon, it's beyond a joke now 

      self.hillHeight = 0
      self.hillColours = [ (243, 112, 49) , (247, 167, 65) , (239, 222, 99) , (197, 153, 96) , (145, 44, 12)  , ]
      self.cactusColour = up(self.cactusColour, 0,105,30)
      self.tree1 = up(self.tree1, 84,60,44)
      self.tree2 = up(self.tree2, 165,135,122)
      self.bushCol = up(self.bushCol, 84,70,54)
      self.skylineColour = up(self.skylineColour , 120, 10, 120)
      self.edgeCol = up(self.edgeCol , 255, 255, 255)
      self.edgeCol2 = up(self.edgeCol2 , 0, 0, 0)
      self.grassColour1 = up(self.grassColour1,223, 145, 94)
      self.grassColour2 = up(self.grassColour2,243, 180, 139)
      #First 2 in SCL are the sun colours the rest are the sky bands
      self.SCL = []
      self.skyColourList = [
        (255,255,0), 
        (230, 230, 0),
        (105,189,210), 
        (55, 158, 183),
        (66, 172, 198),
        (85, 180, 204),
        (105, 189, 210),
        (125, 198, 216),
        (144, 206, 222),
        (164, 215, 228),
      ]
      for i,c in enumerate(self.skyColourList):
          self.SCL.append(up(i, *c))


  def setupColoursNight(self):
      up = self.updatePen
      self.bStars = False
      self.bSun = False
      self.bMoon = True
      self.bStars = True
      self.bClouds = False
      self.bSkyline = True
      self.lamppost = up(self.lamppost, 45,45,150)
      self.tree1 = up(self.tree1, 55,55,100)
      self.tree2 = up(self.tree2, 45,55,250)
      self.bushCol = up(self.bushCol, 45,55,150)
      self.skylineColour = up(self.skylineColour , 120, 10, 120)
      self.edgeCol = up(self.edgeCol , 51, 51, 68)
      self.edgeCol2 = up(self.edgeCol2 , 255, 255, 0)
      self.grassColour1 = up(self.grassColour1,0, 0, 128)
      self.grassColour2 = up(self.grassColour2,128, 0, 128)
      self.skyColourList = [(12, 20, 69), (76, 64, 142), (92, 84, 164), (56, 40, 92), (51, 34, 77), (40,25,60), (30,15,40)]
      self.hillColours = [(132, 77, 163), (102, 59, 148), (67, 28, 118), (34, 28, 105), (8, 9, 66)] #purple hill palette
      self.hillHeight = 8
      for i,c in enumerate(self.skyColourList):
          self.SCL[i] = up(i, *c)

  def setupColoursVice(self):
    up = self.updatePen
 
    self.hillHeight = 3
    self.bSkyline = True
    self.bushCol =up(self.bushCol,240,0,240) 
    self.mountains = False
    self.bSun = True
    self.shwStrLgts = False
    self.bMoon = False
    self.bStars = False
    self.bTrees = False
    self.bSigns = False
    self.bBoards = False
    self.bBushes = True
    self.bClouds = False
    self.skylineModifier = 1.2
    self.streetlamp = up(self.streetlamp,255,155,0)
    self.lamppost = up(self.lamppost, 45,45,150)

    self.grassColour1 = up(self.grassColour1,106,1,105)
    self.grassColour2 = up(self.grassColour2,	42, 143, 194)

    self.banner =up(self.banner, 107,1,125) 
    self.banner2 =up(self.banner2, 189,140,195) 
    self.skyColour = up(self.skyColour, 22,26,164)
    self.tree2 = up(self.tree2, 128, 0, 128)
    self.tree1 = up(self.tree1, 255,155,100)
    self.horizon = up(self.horizon, 0,0,0)
    self.skylineColour =up(self.skylineColour, 10,10,17)
    self.cloudColour = up(self.cloudColour, 153,153,153)
    self.horizon = up(self.horizon, 0,0,0)
    self.moonColour = up(self.moonColour ,255, 255, 255)
    self.whitelines1 =up(self.whitelines1, 0,0,0) 
    self.whitelines2 =up(self.whitelines2, 100,100,100) 
    self.edgeCol = up(self.edgeCol, 235,123,120)
    self.edgeCol2 = up(self.edgeCol2,237, 191, 118)
    self.hillColours = [ (42, 170, 138), (26, 187, 43), (50, 205, 50), (1, 50, 32), (150, 255, 150), (71, 135, 120), ] # Vice hill palette
    self.skyColour = up(self.skyColour, 255, 51, 51)
    self.newSCL = [(238, 175, 97), (251, 144, 98), (238, 93, 108), (206, 73, 147), (106, 13, 51), (58, 13, 51), (58, 13, 41)] #Vice purple sky

    for i,c in enumerate(self.newSCL):
        r,g,b = c
        self.SCL[i] = up(i, r,g,b)

  def setupColours(self):
    self.sceneChangeLast = time.time()
    print("THEME IS", self.theme)
    self.hillHeight = 8
    self.hillColours = [ (42, 170, 138), (26, 187, 43), (50, 205, 50), (1, 50, 32), (150, 255, 150), (71, 135, 120), ] # Default Green hill palette
    self.sunSizeMod = 0
    #FIXME #TODO add a config class with a handler for each of these
    theme = self.theme
    try:
      if(self.bushCol is not None and self.bushCol > 0):
        if(theme == 'day'):
          self.setupColoursDay()
        elif(theme == 'snow'):
          self.setupColoursSnow()
        elif(theme == 'red'):
          self.setupColoursRed()
        elif(theme == 'f32'):
          self.setupColoursF32()
        elif(theme == 'daytoo'):
          self.setupColoursDayToo()
        elif(theme == 'night'):
          self.setupColoursNight()
        elif(theme == 'starrynight'):
          self.setupColoursStarryNight()
        elif(theme == 'vice'):
          self.setupColoursVice()
        elif(theme == 'desert'):
          self.setupColoursDesert()
        else:
          print("Unknown Theme", theme)
          self.setupColoursDay()
        return
    except AttributeError: 
          idc = True
          del idc

    gp = self.gfx.create_pen
    self.tree1 = gp(45,45,150)
    self.tree2 = gp(0,155,100)
    self.lamppost = gp(45,45,150)
    self.streetlamp = gp(255,205,0)
    self.black = gp(0,0,0)
    self.whitelines1 =gp(0,0,0) 
    self.whitelines2 =gp(100,100,100) 
    self.bushCol =gp(240,0,240) 
    self.SCL = [
       gp(238, 175, 97),
       gp(251, 144, 98),
       gp(238, 93, 108),
       gp(206, 73, 147),
       gp(106, 13, 131),
       gp(58, 13, 51),
       gp(0, 0, 0),
       gp(0, 0, 0),
       gp(0, 0, 0),
    ]
    self.setupColours() #call yourself now we have some defaults...no danger

  def banksAndCurves(self):
    if(self.roadcurve < self.curve):
          self.roadcurve += 0.01 * self.speed/2
    if(self.roadcurve > self.curve):
          self.roadcurve -= 0.01 * self.speed/2

    if(self.bank < self.bankTarget):
          self.bank +=  0.05
    if(self.bank > self.bankTarget):
          self.bank -= 0.05

    if(abs(self.curve) < 3): 
      self.curve = 0
    

  def update(self):
    currentTime = time.time();
    self.elapsedTime = currentTime - self.startTime; 
    self.distance += 1*self.speed 
    if(currentTime - self.raintimer > 60): #Can't rain all the time
        self.rain = None

    self.banksAndCurves()

    if(self.sectionDistance > self.sectionLength): 
        if(self.sectionDistance > 0):
          self.curve = int(random.random()*16) -8
          self.sectionDistance = 0
          self.sectionLength = int(1000+random.random()*4000) 
          print((gc.mem_free()/1024))

          j = self.lastJ      
          if(self.lastJ < 0):
              self.lastJ += 1
              self.hillHeight += 0.05
          else:
            j = int(random.random()*10)
            self.lastJ = j
 
          if(j == 0 and self.theme != 'desert' and self.theme != 'day'): #No signs in the desert #FIXME sort this config out it's crazy now
            self.lastJ = 0
            self.shwStrLgts = False
            self.bTrees = False
            self.bBoards = False
            self.bSigns = True
            self.bBushes = False
 
          if(j  > 10): #It wont be 
            #self.lastJ = -3
            self.shwStrLgts = True
            self.bTrees = False
            self.bBoards = False
            self.bSigns = False
            self.bBushes = False

          if(j == 1):
            if self.theme != 'desert': # no rain in the desert either 
              self.raintimer = time.time()
              self.rain = Rng(self.gfx,self.white,self.w) #This is the pink rain bug but I like it so it stays, Red theme has yellow rain 

          if(j == 2):
            self.lastJ = -3
            self.bTrees = True
            self.bBoards = False
            self.bSigns = False
            self.bBushes = False
          if(j ==  3):
            self.lastJ = -3
            self.bTrees = True
            self.bBushes = True
          if(j ==  4):
            self.lastJ = -4
            self.bankTarget = int(random.random()*5)
            if self.theme == 'desert':
              self.bankTarget = 0

          if(j == 5 ): 
            self.sceneChangeLast = time.time()
            newtheme = random.choice(self.themes)
            while self.theme == newtheme:
                newtheme = random.choice(self.themes)
            self.theme = newtheme
            self.setupColours()
            self.lastJ = -6
            self.bTransition = True


          if(int(j) == 6):
            self.lastJ = -3
            self.bBushes = not self.bBushes
            self.bBoards = not self.bBushes
            self.bSigns = False
          if(int(j) ==  7):
            self.lastJ = -3
            self.bBoards = True
            self.bBushes = False
            self.bSigns = False
            self.bTrees = False
            self.bBoards = False
          if(j >  8):
            self.lastJ = -3
            self.shwStrLgts = not self.shwStrLgts
            self.bTrees = not self.shwStrLgts
            self.bBoards = False
            self.bSigns = False

             

          if( self.bTrees or self.shwStrLgts or self.bBoards):
              self.bSigns = False
          if( self.bTrees ):
              self.shwStrLgts = False

    self.sectionDistance += 1*self.speed 


  tunnelCounter = 0
  def drawTunnel():
      print("tunnel?")
  

  def draw(self, gfx, car):
    self.update()
    self.car = car
    gp = gfx.set_pen
    gr = gfx.rectangle
    w = self.w
    gp(self.SCL[6])
    gr(0,0,int(w),int(w/2))
    gp(self.SCL[5])
    gr(0,0,int(w),int(w/3))
    gp(self.SCL[4])
    gr(0,0,int(w),int(w/4))
    gp(self.SCL[3])
    gr(0,0,int(w),int(w/6))
    gp(self.SCL[2])
    gr(0,0,int(w),1)
    gp(self.SCL[0])

    sunpos = abs(int(self.w/3) - int((round(-self.tCurvature*0.01)  )+self.w))
    sunpos = (sunpos % 48) -8
    if(self.bSun):
      suny = int(self.h/3)
      suny2 = int(self.h/2)

      sunyMod = 6
      if(self.theme == 'desert'):
        #higher sun 
        suny -= sunyMod 
        suny2 -= sunyMod
      # the sun itself
      gp(self.SCL[0]) #sun colour is first entries in SCL list
      gfx.circle(sunpos,int(suny),8 - int(self.sunSizeMod)) 
      gp(self.SCL[1])
      if self.theme != 'desert':
        gfx.circle(sunpos,int(suny2),6 - int(self.sunSizeMod))

      # lines over the sun
      gp(self.SCL[5])
      for p in range(int(self.h/4- int(sunyMod/2)),int(self.w/2)):
            if(p % 2 != 0):
              gfx.line(0,p, self.w,p) 

    if(self.bStars):
      for sx,sy,sp in self.stars:
        gp(sp)
        gfx.pixel(sunpos + sx,sy)



    if(self.bMoon):
      gp(self.moonColour)
      gfx.circle(sunpos,5,4) 
      gp(self.SCL[5])
      gfx.circle(sunpos+2,5,3) 


    cloudPoints = [(1,3), (9,0), (18,4), (36,1), (22,2), (32,3), (55,-1), \
                    (-1,3), (-9,0), (-18,4), (-36,1), (-22,2), (-32,3), (-55,-1) ] 
    gfx.set_pen(self.cloudColour)  
    if (self.bClouds): 
      for c,h in cloudPoints: 
          sm = sunpos + c
          #Draw clouds 
          for x in range(6,3):
            gfx.pixel( x+sm,0+h)
          for x in range(8,2):
            gfx.pixel(x+sm,1+h)
          for x in range(14,16):
            gfx.pixel( x+sm,2+h)
          for x in range(12,18):
            gfx.pixel( x+sm, 3+h)
        
    waveMod = self.hillHeight
    yoffset = 15

    if(self.bHills):

      self.mountain.generatePointCloud(-self.tCurvature, waveMod, yoffset)
      self.mountain.updatePalette(self.hillColours)
      gfx = self.mountain.drawMountains(self.mountain.mountain[2]) 

      self.mountain.generatePointCloud(self.tCurvature*0.5, waveMod*1.1, yoffset)
      gfx = self.mountain.drawMountains(self.mountain.mountain[0]) 

      self.mountain.generatePointCloud(self.tCurvature*2, int(waveMod*0.5), yoffset)
      gfx = self.mountain.drawMountains(self.mountain.mountain[3]) 


    rc = self.roadcurve

    ftrackcurvediff = (self.roadcurve - self.fcurvature) * self.elapsedTime
    self.fcurvature += ftrackcurvediff

    self.tCurvature += round(((self.roadcurve) * self.sectionDistance)*0.001) * (self.speed*0.01)
    #print("TCURVE",self.tCurvature)
    bBush = False

    #preload these methods to save some memory
    gline = gfx.line
    gpixel = gfx.pixel
    gcirc = gfx.circle
    gpen = gp
    del gp
 
    for y in range(int(self.h/2)):

        perspective = y / (self.w / 2)
        middlepoint = 0.5  + (self.roadcurve/10) * pow(1- perspective, 3)
        roadwidth = 0.1 + perspective*0.80 # 95% of perspective + minimum 10% 
        clipwidth = roadwidth * 0.2
        roadwidth *= 0.6 

        leftgrass = (middlepoint - roadwidth - clipwidth) * self.w
        leftclip = (middlepoint - roadwidth  ) * self.w
        rightclip = (middlepoint + roadwidth  ) * self.w
        rightgrass = (middlepoint + roadwidth + clipwidth) * self.w

        clipMod = self.w/8
        if self.speed < 20:
            clipMod = self.w/16
        clipMod = self.w

        bBush = False
        grassCol = self.grassColour2
        if math.sin(20 * pow(1.0 - perspective,3) + self.distance * 0.01) > 0:
             grassCol = self.grassColour1
             bBush = True

        edgeCol = self.edgeCol2

        if math.sin(clipMod * pow(1.0 - perspective,3) + self.distance * 0.1) > 0:
             edgeCol = self.edgeCol

        #Definitely room for optimisation round here  
        roadmarker = self.whitelines1
        if math.sin(20 * pow(1.0 - perspective,3) + self.distance * 0.01) > 0:
               roadmarker = self.whitelines2
        if(self.speed < 20):
          if math.sin(40 * pow(1.0 - perspective,2) + self.distance * 0.01) > 0:
               roadmarker = self.whitelines2


        nrow = int(self.w/2+y)

        if bBush and self.bBushes: 
          # (\@/)
          bushPos = int(leftgrass-4)  
          bushPos2 = int((rightgrass+4))  
          if(nrow < 26):
            gpen(self.black)
            gcirc(bushPos,nrow,  int(y/2)+1)
            gcirc(bushPos2,nrow,  int(y/2)+1)
            gpen(self.bushCol)
            gcirc(bushPos,nrow,  int(y/2))
            gcirc(bushPos2,nrow,  int(y/2))


        # Draw the road and the grass  
        bank = int(self.bank)
        roadHeightMod = 0 #TODO
        #rhcurve = max(0, int(math.floor(math.sin(y*0.206)*y)*0.5)) #height #TODO, it might make it too busy though. 
        #print(y,rhcurve)
        rhcurve = 0 
        nrow = int(self.w/2+y) +roadHeightMod + rhcurve
        
        gpen(grassCol)
        gline(0,nrow,32,nrow) # under the road background 

        gpen(self.black) # fill in the black road.. 
        gline(int(leftclip),nrow,int(rightclip),nrow)

        gpen(grassCol)
        gline(0,nrow-bank,int(leftgrass),nrow)
        gline(int(rightgrass),nrow,self.w,nrow-bank)

        gpen(edgeCol)
        gline(int(leftgrass),nrow,int(leftclip),nrow)
        gline(int(rightclip),nrow,int(rightgrass),nrow)

        
        gpen(roadmarker)
        m = int(leftgrass + int((rightgrass-1 - leftgrass+1 )/2))
        gpixel( m, nrow)

        bandBoard = True
        if (self.bBoards):
            bBush = True
            grassCol = self.grassColour2
            if math.sin(20 * pow(1.0 - perspective,3) + self.distance * 0.01) > 0:
                grassCol = self.grassColour1

            edgeCol = self.bushCol
            if math.sin(clipMod * pow(1.0 - perspective,3) + self.distance * 0.1) > 0:
                edgeCol = self.bushCol
                bBush = False
                bandBoard = True

            if bBush and bandBoard:
                bandBoard = False
                bushPos = int(leftgrass-10 - y)  
                bushPos2 = int((rightgrass+6 + y))  
                bushPos = int(leftgrass-3*y)  
                bushPos2 = int((rightgrass+3*y))  
                gpen(edgeCol)
                gfx.rectangle(bushPos-1, nrow, 2+ y, int(y*2)+1)
                gpen(edgeCol)
                gfx.rectangle(bushPos2-1, nrow, 3+ y, int(y*2)+1)


        #Draw some trees  
        if (self.bTrees ):
            bBush = True
            grassCol = self.grassColour2
            if math.sin(40 * pow(1.0 - perspective,3) + self.distance * 0.01) > 0:
                grassCol = self.grassColour1
                bBush = False
            edgeCol = self.edgeCol2
            if math.sin(clipMod * pow(1.0 - perspective,3) + self.distance * 0.1) > 0:
                edgeCol = self.edgeCol

            gpen(self.SCL[3])
            if bBush:
                bushPos = int(leftgrass-1*y)  
                bushPos2 = int((rightgrass+1*y))  

                self.palmTrees = False #FIXME #TODO I want palm trees in vice
                  
                gpen(self.tree2)
                if not self.palmTrees and self.theme != 'desert':
                  gcirc(bushPos, nrow- int(y*2), int(y*0.5)) #Tree canopy left
                  gcirc(bushPos2, nrow- int(y*2), int(y*0.5)) #Tree canopy right

                  gpen(self.black) #tree canpoy shadow
                  gcirc(bushPos, nrow- int(y*2)+1, int(y*0.3))
                  gcirc(bushPos2, nrow-int(y*2)+1, int(y*0.3))

                #else:
                  #Draw palm trees  Todo
                  #self.hillHeight = 0
                  #gpen(self.red)
                  #gline(bushPos-int(y*0.3), nrow- int(y*2.6),  bushPos+int(y*0.8),  nrow -int(y*1.8)) #Tree canopy right
                  #gline(bushPos2-int(y*0.3), nrow- int(y*2.6),  bushPos2+int(y*0.8),  nrow -int(y*1.8)) #Tree canopy right

                gpen(self.tree1)
                gline(bushPos, nrow, bushPos, nrow-int(y*1.5)) #Tree left trunks
                gline(bushPos2, nrow, bushPos2, nrow-int(y*1.5)) #Tree right trunks

                gpen(self.black) #tree trunk shadow
              
                gpen(self.tree1) #more canopy
                gcirc(bushPos, nrow-int(y*1.6), int(y*0.2))
                gcirc(bushPos2, nrow-int(y*1.6), int(y*0.2))

        #Draw some street lights 
        firstLight = True
        if (self.shwStrLgts ):
            bBush = True
            grassCol = self.grassColour2
            if math.sin(20 * pow(1.0 - perspective,3) + self.distance * 0.01) > 0:
                grassCol = self.grassColour1
                bBush = False
            edgeCol = self.edgeCol2
            if math.sin(clipMod * pow(1.0 - perspective,3) + self.distance * 0.1) > 0:
                edgeCol = self.edgeCol
                firstLight = True

            gpen(self.lamppost)
            if bBush and firstLight and self.theme == 'desert':
                gpen(self.cactusColour)
                bushPos = int(leftgrass-1*y)  
                bushPos2 = int((rightgrass+1*y))  
                bx = bushPos
                by = nrow - int(y*1.5)
                bbx = bushPos + 2
                bby = nrow - int(y*2)
                gline(bx, by-4, bx, by+2*y) # left pole 
                gline(bushPos2, by-4, bushPos2, by+2*y) # right pole 
                if nrow > self.w/2: 
                  gline(bushPos2-1, by, bushPos2-int(0.7*y), by)
                  gline(bushPos, by, bushPos+int(0.7*y), by)

            if bBush and firstLight and self.theme != 'desert':
                firstLight = False 
                bushPos = int(leftgrass-1*y)  
                bushPos2 = int((rightgrass+1*y))  
                bx = bushPos
                by = nrow - int(y*2)
                bbx = bushPos + 3
                bby = nrow - int(y*2)
                gline(bx, by-4, bx, by+2*y) # left pole 
                gline(bushPos2, by-4, bushPos2, by+2*y) # right pole 
                gpen(self.streetlamp)
                if nrow > self.w/2: 
                  gline(bushPos2-1, by-4, bushPos2-3, by-4) #right lamp
                  gline(bushPos+1, by-4, bushPos+3, by-4) #left lamp


        bBannerFirst = False
        if (self.bSigns):
            bBanner = True
            grassCol = self.grassColour2
            if math.sin(20 * pow(1.0 - perspective,3) + self.distance * 0.01) > 0:
                grassCol = self.grassColour1
                bBannerFirst = True
            edgeCol = self.edgeCol2
            if math.sin(clipMod * pow(1.0 - perspective,3) + self.distance * 0.1) > 0:
                edgeCol = self.edgeCol

            gpen(self.lamppost)
            if bBanner and bBannerFirst :
                bBannerFirst = False
                bannerPos = int(leftgrass-2)  
                bannerPos2 = int((rightgrass+2))  
                bannerPos = int(leftgrass-1*y)  
                bannerPos2 = int((rightgrass+1*y))  
                gpen(self.banner)
                gline(bannerPos, nrow- int(y*2)+1, bannerPos2, nrow - int(y*2)+1)
                gpen(self.banner2)
                gline(bannerPos, nrow- int(y*2), bannerPos+1, nrow - int(y*2))
                gline(bannerPos, nrow, bannerPos, nrow-int(y*2))
                gline(bannerPos2, nrow, bannerPos2, nrow-int(y*2))
                gline(bannerPos2, nrow- int(y*2), bannerPos2-1, nrow - int(y*2))
                gpen(self.black)
                gline(bannerPos-1, nrow- int(y*2), bannerPos+1, nrow - int(y*2))
                gline(bannerPos-1, nrow, bannerPos-1, nrow-int(y*2))
                gline(bannerPos2-1, nrow, bannerPos2-1, nrow-int(y*2))
                gline(bannerPos2-1, nrow- int(y*2), bannerPos2-1, nrow - int(y*2))
                if(y > 5):
                  gline(bannerPos, nrow- int(y*2), bannerPos2, nrow - int(y*2)+1)

                gpen(self.banner2)
                q = 2
                if(roadwidth > 0.1):
                  for k in range(bannerPos, bannerPos2):  
                      if(k % 2 == 0): 
                         if(y % q == 0):     
                            gpixel(k,int(nrow - y*2)+1)
                      if(k % 2 == 1): 
                         if(y % q == 1):     
                            gpixel(k,int(nrow - y*2)+1)
    self.gfx = gfx
    return gfx



class Game:
  x = 0
  y = 0
  velocity = 1
  last_action = 0
 
  def __init__(self,width,height,cu,graphics ):
    self.cu = cu
    self.gfx = graphics
    self.gfx.clear()
    self.width = width 
    self.height = height 
    self.black = self.gfx.create_pen(0,0,0)
    self.red = self.gfx.create_pen(255,0,0)
    self.road = Road(self.gfx)
    self.car = Car()
    self.themes = self.road.themes

  def debounce(self,button, duration=1000):
    if self.cu.is_pressed(button) and time.ticks_ms() - self.last_action > duration:
        self.last_action = time.ticks_ms()
        return True
    return False


  @micropython.native  # noqa: F821
  def update(self):
    self.handleInput()
  
    self.car.tCurvature = self.road.tCurvature
    self.road.speed = self.car.speed

    self.draw()


  def handleInput(self): 
    c = self.cu
    if c.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_UP):
        c.adjust_brightness(+0.1)

    if c.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_DOWN):
        c.adjust_brightness(-0.1)    

    if(self.road.speed < 1):
        self.road.speed = 0
        self.car.speed = 0
    road = self.road
    car = self.car

    #car buttons
    #print("DISTANCE:" , road.distance)
    if c.is_pressed(CosmicUnicorn.SWITCH_A):
          car.pCurvature -=  0.2 * car.speed/2
          print(road.speed, " ", car.pCurvature)
    if c.is_pressed(CosmicUnicorn.SWITCH_VOLUME_UP):
          car.pCurvature +=  0.2  * car.speed/2
          print(road.speed, " ", car.pCurvature)

    if self.debounce(CosmicUnicorn.SWITCH_D, 400):
        r = int(random.random()*len(self.themes))
        if(road.theme ==self.themes[r]):
          if r == 0:
            r = len(self.themes)-1
          else:
            r = int(random.random()*len(self.themes)-1)
          road.theme = self.themes[max(0,r)]
        else:
          road.theme = self.themes[r]
        road.setupColours()
    if c.is_pressed(CosmicUnicorn.SWITCH_B):
        if(road.speed > 0):
          road.speed -= 1 
          car.speed -= 1 
    if c.is_pressed(CosmicUnicorn.SWITCH_VOLUME_DOWN):
        if(road.speed < 100):
          road.speed += 10 
          car.speed += 10 
          print("SPEED:",car.speed)

    self.road = road
    self.car = car
    #if c.is_pressed(CosmicUnicorn.SWITCH_SLEEP):
    #    machine.reset()


  @micropython.native  # noqa: F821
  def draw(self ):
    gfx = self.gfx

    gfx.set_pen(self.black)
    gfx.clear()
    gfx = self.road.draw(self.gfx, self.car)
    gfx = self.road.gfx
    gfx = self.car.draw(self.gfx)
    gfx = self.car.gfx
   
    if(self.road.rain != None):
      self.road.rain.wind = max(-3, min(3, -self.road.tCurvature))
      gfx = self.road.rain.draw() 
    else:
      if self.road.theme == 'red': #FORCE YELLOW RAIN IN RED THEME
        self.road.raintimer = time.time()
        self.road.rain = Rng(gfx,self.road.edgeCol2,self.width)

    self.cu.update(gfx)




def main():
  cu = CosmicUnicorn()
  cu.set_brightness(0.6)
  gfx = PicoGraphics(DISPLAY_COSMIC_UNICORN, pen_type=PEN_P8)
  width = CosmicUnicorn.WIDTH
  height = CosmicUnicorn.HEIGHT
  game = Game(width,height, cu, gfx)
  gameRunning = True

  while gameRunning:
      start = time.ticks_ms()
      game.update()
      #print("total took: {} ms".format(time.ticks_ms() - start))
      time.sleep(1/60)


if __name__=='__main__':
  main() 

