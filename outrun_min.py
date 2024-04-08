_H='daytoo'
_G='starrynight'
_F='red'
_E='day'
_D='desert'
_C=None
_B=True
_A=False
import gc
from cosmic import CosmicUnicorn,Channel
from picographics import PicoGraphics,DISPLAY_COSMIC_UNICORN,PEN_P8
import random,time,math,machine
machine.freq(200000000)
print('Cosmic Outrun v4 ')
class Rn:
	x=0;y=0;v=1;tv=5;wind=0
	def __init__(A,x=0,h=32):A.x=x;A.h=h;A.y=-int(random.random()*h*10)
	def update(A):
		E=A.x;C=A.y;B=A.v;D=A.h;G=A.tv;H=A.wind;F=random.random
		if B<G:B+=.2
		if B>G:B-=.2
		C+=int(B+H*.8);E+=int(H*.3)
		if C>D:C=-int(F()*D*10);B=1
		if C<-4:C=-int(F()*D*10);B=1
		if E>D:E=-int(F()*D*10);C=int(F()*D);B=1
		if E<-4:E=int(F()*D*10);C=int(F()*D);B=1
		A.tv=G;A.x=E;A.y=C;A.v=B
	def draw(A,gfx,pen,wind=0):B=gfx;A.wind=wind;B.set_pen(pen);B.pixel(int(A.x),int(A.y));A.update();return B
class Rng:
	raindrops=[];wind=0;framecount=0
	def __init__(A,gfx,pen,w=32):A.y=-int(random.random()*100);A.gfx=gfx;A.w=w;A.pen=pen;A.generateRainDrops()
	def generateRainDrops(A):
		A.raindrops=[];B=A.w
		for C in range(B):A.raindrops.append(Rn(C))
	def draw(A):
		B=A.gfx;C=A.pen;D=A.wind
		for E in A.raindrops:B=E.draw(B,C,D)
		return B
class Mountain:
	pointCloud=[];lastPoint=0,16;pCurve=-1;waveMod=-1;gfx=_C;w=32;h=32;yoffset=12;xoffset=0;base=-100;peak=100;currentHillHeight=0
	def __init__(A,gfx,waveMod=4,hm=12,w=32,h=32):A.w=w;A.h=h;A.hm=hm;A.gfx=gfx;A.createPalette();A.generatePointCloud();A.waveMod=waveMod
	@micropython.native
	def generatePointCloud(self,pCurve=0,waveMod=4,yoffset=12):
		G=pCurve;D=yoffset;B=waveMod;A=self;A.base=-1000;A.peak=1000
		if G==A.pCurve and A.waveMod==B:return
		A.waveMod=B
		if B>A.currentHillHeight:A.currentHillHeight+=.01
		if B<A.currentHillHeight:A.currentHillHeight-=.01
		A.yoffset=D;C=[(-1,D)];A.pCurve=G
		for E in range(0,A.w*2):
			H,I=A.lastPoint;F=int(math.cos(A.pCurve*.001+E*.1)*A.currentHillHeight)
			if int(F)<=0:A.lastPoint=E,F+A.yoffset;C.append(A.lastPoint)
			else:A.lastPoint=E,int(-F*.8)+A.yoffset;C.append(A.lastPoint)
		C.append((A.w,D));A.pointCloud=C
	def updatePalette(A,colours):
		for(B,C)in enumerate(A.greens):
			try:A.gfx.update_pen(C,*colours[B])
			except IndexError:D=_B;del D
	@micropython.native
	def createPalette(self):
		A=self;A.black=A.gfx.create_pen(0,0,0);A.white=A.gfx.create_pen(255,255,255);E=[(42,170,138),(26,187,43),(50,205,50),(1,50,32),(150,255,150),(71,135,120)];A.greens=[]
		for F in E:B,C,D=F;A.greens.append(A.gfx.create_pen(B,C,D));del B,C,D
		A.mountain=A.greens
	@micropython.native
	def drawMountains(self,pen=_C,outline=_C,shade=_C):
		H=shade;G=outline;F=pen;A=self
		if F==_C:F=A.white
		if H==_C:H=A.white
		I=-14;J=int(A.w/2);K=0,16;A.gfx.set_pen(F);A.gfx.polygon(A.pointCloud);C=100;D=-100
		for(E,B)in A.pointCloud:
			L,M=A.lastPoint
			if G is not _C and G is not _A:A.gfx.set_pen(G);A.gfx.pixel(E,B)
			A.gfx.set_pen(A.mountain[0])
			if B<C:
				C=B
				if C<A.peak:A.peak=C
			if B>D:
				D=B
				if D>A.base:A.base=D
		for(E,B)in A.pointCloud:
			if B>A.peak+1:A.gfx.set_pen(A.mountain[3]);A.gfx.pixel(E,B)
			if B==A.peak and B<12:A.gfx.set_pen(A.mountain[1]);A.gfx.pixel(E,B+1)
		return A.gfx
class Car:
	red=_C;blue=_C;x=0;y=0;pCurvature=0;tCurvature=0;speed=80;gfx=_C
	@micropython.native
	def draw(self,gfx):
		F=gfx;A=self;gc.collect();C=F.create_pen
		if A.red is _C:A.red=C(255,0,0);A.blue=C(11,82,62);A.grey=C(50,50,80);A.yellow=C(255,255,0);A.red1=C(205,23,0);A.red2=C(105,0,0);A.white=C(255,255,255);A.yellow=C(255,255,0);A.brown=C(160,82,45)
		A.h=32;A.w=32;A.gfx=F;A.curveDiff=int((A.pCurvature-A.tCurvature)*A.speed*.001)
		if abs(A.curveDiff)>A.w*.8:
			if A.speed<1:A.speed=0
		if A.speed<10:A.speed=0
		B=int(A.w/2)+4+A.curveDiff;G=A.tCurvature;H=A.pCurvature
		if B<-4:B=-4
		if B>31:B=31
		if B<-4:B=-4;H=G+A.w;A.curveDiff=int((H-G)*A.speed*.001)
		if B>A.w-1:B=A.w-1;H=G+B;H=G;A.curveDiff=int((H-G)*A.speed*.001)
		C=F.set_pen;D=F.rectangle;E=int(A.h)-3;C(A.red1);D(int(B),E,8,1);C(A.red2);D(int(B),E+1,8,1);D(int(B),E+2,8,1);C(A.white);D(int(B)+3,E+1,2,1);C(A.blue);D(int(B)+1,E-1,6,1);C(A.yellow);D(int(B)+1,E-1,2,2);C(A.brown);D(int(B)+5,E-1,2,2);C(A.grey);D(int(B),E+2,2,1);D(int(B)+6,E+2,2,1);C(A.red);D(int(B),E,2,1);D(int(B)+6,E,2,1);A.gfx=F;return F
class Road:
	distance=1;theme=_E;sceneChangeCount=0;sceneChangeLast=0;bHills=_B;raintimer=1;fcurvature=0
	def __init__(A,graphics,w=32,h=32):A.themes=[_E,'night',_G,'vice',_D,_H,'snow','f32',_F];A.w=w;A.fcurvature=.0;A.sunSizeMod=0;A.mountains=_B;A.bSigns=_A;A.h=h;A.bBoards=_A;A.bMoon=_A;A.bStars=_A;A.bSkyline=_B;A.gfx=graphics;A.initPallette();A.startTime=time.time();A.elapsedTime=0;A.setupColours();A.speed=80;A.roadcurve=0;A.curve=0;A.randomCurve=_B;A.sectionDistance=0;A.sectionLength=4000;A.tCurvature=0;A.pCurvature=0;A.mountain=Mountain(A.gfx,A.pCurvature,w,h);A.rain=_C;A.lastJ=-3;A.skyline=_B;A.bank=0;A.bankTarget=3
	def initStars(A):
		A.greyscale=[(255,255,255),(100,100,100),(205,205,205),(100,80,80)];A.starColours=[];A.stars=[]
		for(K,B)in enumerate(A.greyscale):C,D,E=B;A.starColours.append(A.gfx.create_pen(C,D,E))
		F=A.w;G=int(A.h/3)
		for H in range(-20,F+20):
			I=random.choice(A.starColours);J=int(random.random()*G)
			if random.random()>.5:A.stars.append((H,J,I))
	def initPallette(A):
		B=A.gfx.create_pen;gc.collect();A.white=B(255,255,255);A.black=B(0,0,0);A.red=B(255,0,0);A.blue=B(0,0,255);A.mountains=_A;A.bSun=_B;A.skylineModifier=1.2;A.streetlamp=B(255,155,0);A.banner=B(107,1,125);A.banner2=B(255,205,0);A.bClouds=_A;A.skyColour=B(22,26,164);A.bTrees=_A;A.bSigns=_A;A.bBoards=_A;A.bBushes=_B;A.shwStrLgts=_A;A.tree2=B(245,25,250);A.tree1=B(255,155,100);A.cactusColour=B(0,105,30);A.horizon=B(0,0,0);A.skylineColour=B(10,10,17);A.cloudColour=B(153,153,153);A.horizon=B(51,51,51);A.grassColour1=B(0,255,0);A.grassColour2=B(106,1,125);A.whitelines1=B(0,0,0);A.whitelines2=B(100,100,100);A.edgeCol=B(255,0,0);A.edgeCol2=B(0,0,0);A.grassColour1=B(106,1,125);A.red=B(206,0,0);A.grassColour2=B(93,177,220);A.skyColour=B(255,51,51);A.newSCL=[(238,175,97),(251,144,98),(238,93,108),(206,73,147),(106,13,131),(58,13,51),(68,68,68),(51,51,51),(17,17,17),(0,0,0)];A.hillColours=[(42,170,138),(26,187,43),(50,205,50),(1,50,32),(150,255,150),(71,135,120)];C=[]
		for(G,H)in enumerate(A.newSCL):D,E,F=H;C.append(A.updatePen(G,D,E,F));del D,E,F
		A.SCL=C;A.moonColour=A.gfx.create_pen(255,255,255);A.initStars()
	def hex2rgb(A,h):h=h.replace('#','');return tuple(int(h[A:A+2],16)for A in(0,2,4))
	def setupColoursF32(A):
		B=A.updatePen;A.bSkyline=_A;A.bBoards=_B;A.hillColours=[(50,50,55),(60,60,105),(100,100,120),(115,115,145),(115,120,155)];A.hillHeight=4;A.skylineModifier=2;A.banner=B(A.banner,200,0,0);A.banner2=B(A.banner2,255,255,255);A.mountains=_B;A.bClouds=_B;A.bTrees=_A;A.bBushes=_B;A.shwStrLgts=_A;A.bSigns=_A;A.bMoon=_A;A.bStars=_A;A.lamppost=B(A.lamppost,165,161,221);A.horizon=B(A.horizon,255,255,255);A.bSun=_B;A.sunSizeMod=6;A.skyColour=B(A.skyColour,10,40,255);A.skylineColour=B(A.skylineColour,73,73,73);C=[(38,75,197),(12,70,197),(12,70,197),(98,93,229),(32,67,219),(28,80,197),(28,100,197),(28,50,197),(85,85,85)]
		for(D,E)in enumerate(A.newSCL):F,G,H=E;C[D]=B(D,F,G,H)
		A.SCL=C;A.grassColour1=B(A.grassColour1,0,132,0);A.grassColour2=B(A.grassColour2,0,222,0);A.bushCol=B(A.bushCol,30,30,30);A.cloudColour=B(A.cloudColour,255,255,255);A.moonColour=B(A.moonColour,255,255,255);A.edgeCol=B(A.edgeCol,255,0,0);A.edgeCol2=B(A.edgeCol2,255,255,255);A.tree1=B(A.tree1,130,82,45);A.tree2=B(A.tree2,0,200,40)
	def setupColoursRed(A):
		B=A.updatePen;A.bSkyline=_B;A.bBoards=_A;A.hillColours=[(156,0,1),(126,24,7),(94,18,3),(74,15,0),(55,0,0)];A.hillHeight=2;A.edgeCol=B(A.edgeCol,155,51,0);A.edgeCol2=B(A.edgeCol2,255,255,0);A.skylineModifier=2;A.banner=B(A.banner,100,0,0);A.banner2=B(A.banner2,0,0,0);A.mountains=_B;A.bClouds=_A;A.bTrees=_A;A.bBushes=_A;A.shwStrLgts=_A;A.bSigns=_A;A.bMoon=_A;A.bStars=_A;A.lamppost=B(A.lamppost,0,0,0);A.horizon=B(A.horizon,0,0,0);A.bSun=_B;A.sunSizeMod=0;A.skyColour=B(A.skyColour,255,0,0);A.skylineColour=B(A.skylineColour,73,73,0);A.newSCL=[(0,0,0),(212,107,7),(167,0,0),(219,20,0),(236,83,0),(242,112,6),(255,141,0),(0,0,0)]
		for(C,D)in enumerate(A.newSCL):E,F,G=D;A.SCL[C]=B(C,E,F,G)
		A.grassColour1=B(A.grassColour1,255,13,0);A.grassColour2=B(A.grassColour2,80,0,0);A.bushCol=B(A.bushCol,255,255,0);A.cloudColour=B(A.cloudColour,255,255,255);A.moonColour=B(A.moonColour,255,255,255);A.tree1=B(A.tree1,40,0,0);A.tree2=B(A.tree2,255,155,0);A.raintimer=time.time();A.rain=Rng(A.gfx,A.edgeCol2,A.w)
	def setupColoursSnow(A):
		B=A.updatePen;A.raintimer=time.time();A.rain=Rng(A.gfx,A.white,A.w);A.bSkyline=_B;A.bBoards=_A;A.hillColours=[(106,112,114),(92,103,106),(46,70,78),(46,74,82),(255,255,255)];A.hillHeight=8;A.edgeCol=B(A.edgeCol,51,51,68);A.edgeCol2=B(A.edgeCol2,255,255,0);A.skylineModifier=2;A.banner=B(A.banner,200,0,0);A.banner2=B(A.banner2,255,255,255);A.mountains=_B;A.bClouds=_B;A.bTrees=_A;A.bBushes=_A;A.shwStrLgts=_A;A.bSigns=_A;A.bMoon=_A;A.bStars=_A;A.lamppost=B(A.lamppost,165,161,221);A.horizon=B(A.horizon,255,255,255);A.bSun=_B;A.sunSizeMod=6;A.skyColour=B(A.skyColour,183,208,225);A.skylineColour=B(A.skylineColour,73,73,73);A.newSCL=[(238,175,97),(12,70,197),(12,70,197),(198,193,229),(132,167,219),(128,150,197),(128,150,197),(128,150,197),(185,85,85)]
		for(C,D)in enumerate(A.newSCL):E,F,G=D;A.SCL[C]=B(C,E,F,G)
		A.grassColour1=B(A.grassColour1,95,132,162);A.grassColour2=B(A.grassColour2,202,222,237);A.bushCol=B(A.bushCol,219,236,244);A.cloudColour=B(A.cloudColour,255,255,255);A.moonColour=B(A.moonColour,255,255,255);A.edgeCol=B(A.edgeCol,0,0,0);A.edgeCol2=B(A.edgeCol2,255,255,255);A.tree1=B(A.tree1,160,82,45);A.tree2=B(A.tree2,200,200,240)
	def setupColoursDayToo(A):
		B=A.updatePen;A.bSkyline=_B;A.bBoards=_A;A.hillColours=[(66,139,16),(102,177,11),(139,203,35),(183,233,66)];A.hillHeight=8;A.skylineModifier=2;A.banner=B(A.banner,200,200,200);A.banner2=B(A.banner2,0,0,0);A.mountains=_B;A.bClouds=_B;A.bTrees=_A;A.bBushes=_B;A.shwStrLgts=_A;A.bSigns=_A;A.bMoon=_A;A.bStars=_A;A.lamppost=B(A.lamppost,*(86,61,45));A.horizon=B(A.horizon,51,51,51);A.bSun=_B;A.skyColour=B(A.skyColour,22,26,164);A.skylineColour=B(A.skylineColour,73,73,73);A.newSCL=[(238,175,97),(12,70,197),(12,70,197),(98,193,229),(32,167,219),(28,150,197),(28,150,197),(28,150,197),(85,85,85)]
		for(C,D)in enumerate(A.newSCL):E,F,G=D;A.SCL[C]=B(C,E,F,G)
		A.grassColour1=B(A.grassColour1,255,213,0);A.grassColour2=B(A.grassColour2,145,149,54);A.bushCol=B(A.bushCol,192,182,42);A.cloudColour=B(A.cloudColour,255,255,255);A.moonColour=B(A.moonColour,255,255,255);A.edgeCol=B(A.edgeCol,0,0,0);A.edgeCol2=B(A.edgeCol2,255,255,255);A.tree1=B(A.tree1,160,82,45);A.tree2=B(A.tree2,0,220,10)
	def setupColoursDay(A):
		B=A.updatePen;A.bSkyline=_B;A.bBoards=_A;A.hillColours=[(42,170,138),(26,187,43),(50,205,50),(1,50,32),(150,255,150),(71,135,120)];A.hillHeight=8;A.skylineModifier=2;A.bushCol=B(A.bushCol,0,255,100);A.banner=B(A.banner,200,200,200);A.banner2=B(A.banner2,0,0,0);A.mountains=_B;A.bClouds=_B;A.bTrees=_A;A.bBushes=_B;A.shwStrLgts=_A;A.bSigns=_A;A.bMoon=_A;A.bStars=_A;A.lamppost=B(A.lamppost,45,45,150);A.horizon=B(A.horizon,51,51,51);A.bSun=_B;A.skyColour=B(A.skyColour,22,26,164);A.skylineColour=B(A.skylineColour,73,73,73);A.newSCL=[(238,175,97),(12,70,197),(12,70,197),(98,193,229),(32,167,219),(28,150,197),(28,150,197),(28,150,197),(85,85,85)]
		for(C,D)in enumerate(A.newSCL):E,F,G=D;A.SCL[C]=B(C,E,F,G)
		A.grassColour1=B(A.grassColour1,0,255,17);A.grassColour2=B(A.grassColour2,0,68,0);A.cloudColour=B(A.cloudColour,255,255,255);A.moonColour=B(A.moonColour,255,255,255);A.edgeCol=B(A.edgeCol,0,0,0);A.edgeCol2=B(A.edgeCol2,255,255,255);A.tree1=B(A.tree1,160,82,45);A.tree2=B(A.tree2,0,220,10)
	def updatePen(B,colourIdx,r,g,b):
		A=colourIdx
		if A is _C:C=B.gfx.create_pen(r,g,b)
		elif A>-1:B.gfx.update_pen(A,r,g,b);C=A
		return C
	def setupColoursStarryNight(A):
		B=A.updatePen;A.bSkyline=_B;A.tree1=B(A.tree1,55,55,100);A.tree2=B(A.tree2,45,55,250);A.skylineColour=B(A.skylineColour,10,10,50);A.bClouds=_A;A.bMoon=_B;A.bStars=_B;A.bSun=_A;A.bClouds=_A;A.bushCol=B(A.bushCol,0,255,100);A.edgeCol=B(A.edgeCol,51,51,68);A.edgeCol2=B(A.edgeCol2,255,255,0);A.grassColour1=B(A.grassColour1,12,20,69);A.grassColour2=B(A.grassColour2,51,34,77);A.lamppost=B(A.lamppost,45,45,150);A.skyColourList=[];A.horizon=B(A.horizon,0,0,0);A.skyColourList=[(0,0,0),(17,17,17),(34,34,34),(51,51,51),(68,68,68),(40,40,50),(30,30,40),(20,20,40)];A.hillHeight=7;A.hillColours=[(42,170,138),(26,187,43),(50,205,50),(1,50,32),(150,255,150),(71,135,120)]
		for(C,D)in enumerate(A.skyColourList):A.SCL[C]=B(C,*D)
	def setupColoursDesert(A):
		B=A.updatePen;A.bStars=_A;A.bSun=_B;A.rain=_C;A.bMoon=_A;A.bStars=_A;A.bClouds=_A;A.bSkyline=_A;A.sunSizeMod=4;A.bHills=_B;A.bTrees=_A;A.shwStrLgts=_B;A.hillHeight=0;A.hillColours=[(243,112,49),(247,167,65),(239,222,99),(197,153,96),(145,44,12)];A.cactusColour=B(A.cactusColour,0,105,30);A.tree1=B(A.tree1,84,60,44);A.tree2=B(A.tree2,165,135,122);A.bushCol=B(A.bushCol,84,70,54);A.skylineColour=B(A.skylineColour,120,10,120);A.edgeCol=B(A.edgeCol,255,255,255);A.edgeCol2=B(A.edgeCol2,0,0,0);A.grassColour1=B(A.grassColour1,223,145,94);A.grassColour2=B(A.grassColour2,243,180,139);A.SCL=[];A.skyColourList=[(255,255,0),(230,230,0),(105,189,210),(55,158,183),(66,172,198),(85,180,204),(105,189,210),(125,198,216),(144,206,222),(164,215,228)]
		for(C,D)in enumerate(A.skyColourList):A.SCL.append(B(C,*D))
	def setupColoursNight(A):
		B=A.updatePen;A.bStars=_A;A.bSun=_A;A.bMoon=_B;A.bStars=_B;A.bClouds=_A;A.bSkyline=_B;A.lamppost=B(A.lamppost,45,45,150);A.tree1=B(A.tree1,55,55,100);A.tree2=B(A.tree2,45,55,250);A.bushCol=B(A.bushCol,45,55,150);A.skylineColour=B(A.skylineColour,120,10,120);A.edgeCol=B(A.edgeCol,51,51,68);A.edgeCol2=B(A.edgeCol2,255,255,0);A.grassColour1=B(A.grassColour1,0,0,128);A.grassColour2=B(A.grassColour2,128,0,128);A.skyColourList=[(12,20,69),(76,64,142),(92,84,164),(56,40,92),(51,34,77),(40,25,60),(30,15,40)];A.hillColours=[(132,77,163),(102,59,148),(67,28,118),(34,28,105),(8,9,66)];A.hillHeight=8
		for(C,D)in enumerate(A.skyColourList):A.SCL[C]=B(C,*D)
	def setupColoursVice(A):
		B=A.updatePen;A.hillHeight=3;A.bSkyline=_B;A.bushCol=B(A.bushCol,240,0,240);A.mountains=_A;A.bSun=_B;A.shwStrLgts=_A;A.bMoon=_A;A.bStars=_A;A.bTrees=_A;A.bSigns=_A;A.bBoards=_A;A.bBushes=_B;A.bClouds=_A;A.skylineModifier=1.2;A.streetlamp=B(A.streetlamp,255,155,0);A.lamppost=B(A.lamppost,45,45,150);A.grassColour1=B(A.grassColour1,106,1,105);A.grassColour2=B(A.grassColour2,42,143,194);A.banner=B(A.banner,107,1,125);A.banner2=B(A.banner2,189,140,195);A.skyColour=B(A.skyColour,22,26,164);A.tree2=B(A.tree2,128,0,128);A.tree1=B(A.tree1,255,155,100);A.horizon=B(A.horizon,0,0,0);A.skylineColour=B(A.skylineColour,10,10,17);A.cloudColour=B(A.cloudColour,153,153,153);A.horizon=B(A.horizon,0,0,0);A.moonColour=B(A.moonColour,255,255,255);A.whitelines1=B(A.whitelines1,0,0,0);A.whitelines2=B(A.whitelines2,100,100,100);A.edgeCol=B(A.edgeCol,235,123,120);A.edgeCol2=B(A.edgeCol2,237,191,118);A.hillColours=[(42,170,138),(26,187,43),(50,205,50),(1,50,32),(150,255,150),(71,135,120)];A.skyColour=B(A.skyColour,255,51,51);A.newSCL=[(238,175,97),(251,144,98),(238,93,108),(206,73,147),(106,13,51),(58,13,51),(58,13,41)]
		for(C,D)in enumerate(A.newSCL):E,F,G=D;A.SCL[C]=B(C,E,F,G)
	def setupColours(A):
		A.sceneChangeLast=time.time();print('THEME IS',A.theme);A.hillHeight=8;A.hillColours=[(42,170,138),(26,187,43),(50,205,50),(1,50,32),(150,255,150),(71,135,120)];A.sunSizeMod=0;C=A.theme
		try:
			if A.bushCol is not _C and A.bushCol>0:
				if C==_E:A.setupColoursDay()
				elif C=='snow':A.setupColoursSnow()
				elif C==_F:A.setupColoursRed()
				elif C=='f32':A.setupColoursF32()
				elif C==_H:A.setupColoursDayToo()
				elif C=='night':A.setupColoursNight()
				elif C==_G:A.setupColoursStarryNight()
				elif C=='vice':A.setupColoursVice()
				elif C==_D:A.setupColoursDesert()
				else:print('Unknown Theme',C);A.setupColoursDay()
				return
		except AttributeError:D=_B;del D
		B=A.gfx.create_pen;A.tree1=B(45,45,150);A.tree2=B(0,155,100);A.lamppost=B(45,45,150);A.streetlamp=B(255,205,0);A.black=B(0,0,0);A.whitelines1=B(0,0,0);A.whitelines2=B(100,100,100);A.bushCol=B(240,0,240);A.SCL=[B(238,175,97),B(251,144,98),B(238,93,108),B(206,73,147),B(106,13,131),B(58,13,51),B(0,0,0),B(0,0,0),B(0,0,0)];A.setupColours()
	def banksAndCurves(A):
		if A.roadcurve<A.curve:A.roadcurve+=.01*A.speed/2
		if A.roadcurve>A.curve:A.roadcurve-=.01*A.speed/2
		if A.bank<A.bankTarget:A.bank+=.05
		if A.bank>A.bankTarget:A.bank-=.05
		if abs(A.curve)<3:A.curve=0
	def update(A):
		D=time.time();A.elapsedTime=D-A.startTime;A.distance+=1*A.speed
		if D-A.raintimer>60:A.rain=_C
		A.banksAndCurves()
		if A.sectionDistance>A.sectionLength:
			if A.sectionDistance>0:
				A.curve=int(random.random()*16)-8;A.sectionDistance=0;A.sectionLength=int(1000+random.random()*4000);print(gc.mem_free()/1024);B=A.lastJ
				if A.lastJ<0:A.lastJ+=1;A.hillHeight+=.05
				else:B=int(random.random()*10);A.lastJ=B
				if B==0 and A.theme!=_D and A.theme!=_E:A.lastJ=0;A.shwStrLgts=_A;A.bTrees=_A;A.bBoards=_A;A.bSigns=_B;A.bBushes=_A
				if B>10:A.shwStrLgts=_B;A.bTrees=_A;A.bBoards=_A;A.bSigns=_A;A.bBushes=_A
				if B==1:
					if A.theme!=_D:A.raintimer=time.time();A.rain=Rng(A.gfx,A.white,A.w)
				if B==2:A.lastJ=-3;A.bTrees=_B;A.bBoards=_A;A.bSigns=_A;A.bBushes=_A
				if B==3:A.lastJ=-3;A.bTrees=_B;A.bBushes=_B
				if B==4:
					A.lastJ=-4;A.bankTarget=int(random.random()*5)
					if A.theme==_D:A.bankTarget=0
				if B==5:
					A.sceneChangeLast=time.time();C=random.choice(A.themes)
					while A.theme==C:C=random.choice(A.themes)
					A.theme=C;A.setupColours();A.lastJ=-6;A.bTransition=_B
				if int(B)==6:A.lastJ=-3;A.bBushes=not A.bBushes;A.bBoards=not A.bBushes;A.bSigns=_A
				if int(B)==7:A.lastJ=-3;A.bBoards=_B;A.bBushes=_A;A.bSigns=_A;A.bTrees=_A;A.bBoards=_A
				if B>8:A.lastJ=-3;A.shwStrLgts=not A.shwStrLgts;A.bTrees=not A.shwStrLgts;A.bBoards=_A;A.bSigns=_A
				if A.bTrees or A.shwStrLgts or A.bBoards:A.bSigns=_A
				if A.bTrees:A.shwStrLgts=_A
		A.sectionDistance+=1*A.speed
	tunnelCounter=0
	def drawTunnel():print('tunnel?')
	def draw(A,gfx,car):
		Q=1.;E=gfx;A.update();A.car=car;J=E.set_pen;Z=E.rectangle;U=A.w;J(A.SCL[6]);Z(0,0,int(U),int(U/2));J(A.SCL[5]);Z(0,0,int(U),int(U/3));J(A.SCL[4]);Z(0,0,int(U),int(U/4));J(A.SCL[3]);Z(0,0,int(U),int(U/6));J(A.SCL[2]);Z(0,0,int(U),1);J(A.SCL[0]);V=abs(int(A.w/3)-int(round(-A.tCurvature*.01)+A.w));V=V%48-8
		if A.bSun:
			o=int(A.h/3);p=int(A.h/2);g=6
			if A.theme==_D:o-=g;p-=g
			J(A.SCL[0]);E.circle(V,int(o),8-int(A.sunSizeMod));J(A.SCL[1])
			if A.theme!=_D:E.circle(V,int(p),6-int(A.sunSizeMod))
			J(A.SCL[5])
			for h in range(int(A.h/4-int(g/2)),int(A.w/2)):
				if h%2!=0:E.line(0,h,A.w,h)
		if A.bStars:
			for(v,w,x)in A.stars:J(x);E.pixel(V+v,w)
		if A.bMoon:J(A.moonColour);E.circle(V,5,4);J(A.SCL[5]);E.circle(V+2,5,3)
		y=[(1,3),(9,0),(18,4),(36,1),(22,2),(32,3),(55,-1),(-1,3),(-9,0),(-18,4),(-36,1),(-22,2),(-32,3),(-55,-1)];E.set_pen(A.cloudColour)
		if A.bClouds:
			for(z,b)in y:
				c=V+z
				for W in range(6,3):E.pixel(W+c,0+b)
				for W in range(8,2):E.pixel(W+c,1+b)
				for W in range(14,16):E.pixel(W+c,2+b)
				for W in range(12,18):E.pixel(W+c,3+b)
		i=A.hillHeight;j=15
		if A.bHills:A.mountain.generatePointCloud(-A.tCurvature,i,j);A.mountain.updatePalette(A.hillColours);E=A.mountain.drawMountains(A.mountain.mountain[2]);A.mountain.generatePointCloud(A.tCurvature*.5,i*1.1,j);E=A.mountain.drawMountains(A.mountain.mountain[0]);A.mountain.generatePointCloud(A.tCurvature*2,int(i*.5),j);E=A.mountain.drawMountains(A.mountain.mountain[3])
		A7=A.roadcurve;A0=(A.roadcurve-A.fcurvature)*A.elapsedTime;A.fcurvature+=A0;A.tCurvature+=round(A.roadcurve*A.sectionDistance*.001)*(A.speed*.01);L=_A;D=E.line;k=E.pixel;T=E.circle;F=J;del J
		for B in range(int(A.h/2)):
			K=B/(A.w/2);d=.5+A.roadcurve/10*pow(1-K,3);X=.1+K*.8;q=X*.2;X*=.6;M=(d-X-q)*A.w;r=(d-X)*A.w;s=(d+X)*A.w;R=(d+X+q)*A.w;Y=A.w/8
			if A.speed<20:Y=A.w/16
			Y=A.w;L=_A;S=A.grassColour2
			if math.sin(20*pow(Q-K,3)+A.distance*.01)>0:S=A.grassColour1;L=_B
			N=A.edgeCol2
			if math.sin(Y*pow(Q-K,3)+A.distance*.1)>0:N=A.edgeCol
			l=A.whitelines1
			if math.sin(20*pow(Q-K,3)+A.distance*.01)>0:l=A.whitelines2
			if A.speed<20:
				if math.sin(40*pow(Q-K,2)+A.distance*.01)>0:l=A.whitelines2
			C=int(A.w/2+B)
			if L and A.bBushes:
				G=int(M-4);H=int(R+4)
				if C<26:F(A.black);T(G,C,int(B/2)+1);T(H,C,int(B/2)+1);F(A.bushCol);T(G,C,int(B/2));T(H,C,int(B/2))
			t=int(A.bank);A1=0;A2=0;C=int(A.w/2+B)+A1+A2;F(S);D(0,C,32,C);F(A.black);D(int(r),C,int(s),C);F(S);D(0,C-t,int(M),C);D(int(R),C,A.w,C-t);F(N);D(int(M),C,int(r),C);D(int(s),C,int(R),C);F(l);A3=int(M+int((R-1-M+1)/2));k(A3,C);m=_B
			if A.bBoards:
				L=_B;S=A.grassColour2
				if math.sin(20*pow(Q-K,3)+A.distance*.01)>0:S=A.grassColour1
				N=A.bushCol
				if math.sin(Y*pow(Q-K,3)+A.distance*.1)>0:N=A.bushCol;L=_A;m=_B
				if L and m:m=_A;G=int(M-10-B);H=int(R+6+B);G=int(M-3*B);H=int(R+3*B);F(N);E.rectangle(G-1,C,2+B,int(B*2)+1);F(N);E.rectangle(H-1,C,3+B,int(B*2)+1)
			if A.bTrees:
				L=_B;S=A.grassColour2
				if math.sin(40*pow(Q-K,3)+A.distance*.01)>0:S=A.grassColour1;L=_A
				N=A.edgeCol2
				if math.sin(Y*pow(Q-K,3)+A.distance*.1)>0:N=A.edgeCol
				F(A.SCL[3])
				if L:
					G=int(M-1*B);H=int(R+1*B);A.palmTrees=_A;F(A.tree2)
					if not A.palmTrees and A.theme!=_D:T(G,C-int(B*2),int(B*.5));T(H,C-int(B*2),int(B*.5));F(A.black);T(G,C-int(B*2)+1,int(B*.3));T(H,C-int(B*2)+1,int(B*.3))
					F(A.tree1);D(G,C,G,C-int(B*1.5));D(H,C,H,C-int(B*1.5));F(A.black);F(A.tree1);T(G,C-int(B*1.6),int(B*.2));T(H,C-int(B*1.6),int(B*.2))
			e=_B
			if A.shwStrLgts:
				L=_B;S=A.grassColour2
				if math.sin(20*pow(Q-K,3)+A.distance*.01)>0:S=A.grassColour1;L=_A
				N=A.edgeCol2
				if math.sin(Y*pow(Q-K,3)+A.distance*.1)>0:N=A.edgeCol;e=_B
				F(A.lamppost)
				if L and e and A.theme==_D:
					F(A.cactusColour);G=int(M-1*B);H=int(R+1*B);a=G;I=C-int(B*1.5);A4=G+2;A5=C-int(B*2);D(a,I-4,a,I+2*B);D(H,I-4,H,I+2*B)
					if C>A.w/2:D(H-1,I,H-int(.7*B),I);D(G,I,G+int(.7*B),I)
				if L and e and A.theme!=_D:
					e=_A;G=int(M-1*B);H=int(R+1*B);a=G;I=C-int(B*2);A4=G+3;A5=C-int(B*2);D(a,I-4,a,I+2*B);D(H,I-4,H,I+2*B);F(A.streetlamp)
					if C>A.w/2:D(H-1,I-4,H-3,I-4);D(G+1,I-4,G+3,I-4)
			n=_A
			if A.bSigns:
				A6=_B;S=A.grassColour2
				if math.sin(20*pow(Q-K,3)+A.distance*.01)>0:S=A.grassColour1;n=_B
				N=A.edgeCol2
				if math.sin(Y*pow(Q-K,3)+A.distance*.1)>0:N=A.edgeCol
				F(A.lamppost)
				if A6 and n:
					n=_A;O=int(M-2);P=int(R+2);O=int(M-1*B);P=int(R+1*B);F(A.banner);D(O,C-int(B*2)+1,P,C-int(B*2)+1);F(A.banner2);D(O,C-int(B*2),O+1,C-int(B*2));D(O,C,O,C-int(B*2));D(P,C,P,C-int(B*2));D(P,C-int(B*2),P-1,C-int(B*2));F(A.black);D(O-1,C-int(B*2),O+1,C-int(B*2));D(O-1,C,O-1,C-int(B*2));D(P-1,C,P-1,C-int(B*2));D(P-1,C-int(B*2),P-1,C-int(B*2))
					if B>5:D(O,C-int(B*2),P,C-int(B*2)+1)
					F(A.banner2);u=2
					if X>.1:
						for f in range(O,P):
							if f%2==0:
								if B%u==0:k(f,int(C-B*2)+1)
							if f%2==1:
								if B%u==1:k(f,int(C-B*2)+1)
		A.gfx=E;return E
class Game:
	x=0;y=0;velocity=1;last_action=0
	def __init__(A,width,height,cu,graphics):A.cu=cu;A.gfx=graphics;A.gfx.clear();A.width=width;A.height=height;A.black=A.gfx.create_pen(0,0,0);A.red=A.gfx.create_pen(255,0,0);A.road=Road(A.gfx);A.car=Car();A.themes=A.road.themes
	def debounce(A,button,duration=1000):
		if A.cu.is_pressed(button)and time.ticks_ms()-A.last_action>duration:A.last_action=time.ticks_ms();return _B
		return _A
	@micropython.native
	def update(self):A=self;A.handleInput();A.car.tCurvature=A.road.tCurvature;A.road.speed=A.car.speed;A.draw()
	def handleInput(A):
		D=A.cu
		if D.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_UP):D.adjust_brightness(+.1)
		if D.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_DOWN):D.adjust_brightness(-.1)
		if A.road.speed<1:A.road.speed=0;A.car.speed=0
		B=A.road;C=A.car
		if D.is_pressed(CosmicUnicorn.SWITCH_A):C.pCurvature-=.2*C.speed/2;print(B.speed,' ',C.pCurvature)
		if D.is_pressed(CosmicUnicorn.SWITCH_VOLUME_UP):C.pCurvature+=.2*C.speed/2;print(B.speed,' ',C.pCurvature)
		if A.debounce(CosmicUnicorn.SWITCH_D,400):
			E=int(random.random()*len(A.themes))
			if B.theme==A.themes[E]:
				if E==0:E=len(A.themes)-1
				else:E=int(random.random()*len(A.themes)-1)
				B.theme=A.themes[max(0,E)]
			else:B.theme=A.themes[E]
			B.setupColours()
		if D.is_pressed(CosmicUnicorn.SWITCH_B):
			if B.speed>0:B.speed-=1;C.speed-=1
		if D.is_pressed(CosmicUnicorn.SWITCH_VOLUME_DOWN):
			if B.speed<100:B.speed+=10;C.speed+=10;print('SPEED:',C.speed)
		A.road=B;A.car=C
	@micropython.native
	def draw(self):
		A=self;B=A.gfx;B.set_pen(A.black);B.clear();B=A.road.draw(A.gfx,A.car);B=A.road.gfx;B=A.car.draw(A.gfx);B=A.car.gfx
		if A.road.rain!=_C:A.road.rain.wind=max(-3,min(3,-A.road.tCurvature));B=A.road.rain.draw()
		elif A.road.theme==_F:A.road.raintimer=time.time();A.road.rain=Rng(B,A.road.edgeCol2,A.width)
		A.cu.update(B)
def main():
	A=CosmicUnicorn();A.set_brightness(.6);B=PicoGraphics(DISPLAY_COSMIC_UNICORN,pen_type=PEN_P8);C=CosmicUnicorn.WIDTH;D=CosmicUnicorn.HEIGHT;E=Game(C,D,A,B);F=_B
	while F:G=time.ticks_ms();E.update();time.sleep(1/60)
if __name__=='__main__':main()