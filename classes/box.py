from .sprites import Sprite

class Box(Sprite): #ground box
	def __init__(self, startx, starty,num):
		super().__init__(["sprites/ground.png","sprites/ground(2).png"], startx, starty,"ground")
		if num == 1:
			self.animationIndex = 1
		else:
			self.animationIndex = 0	

class Sky(Sprite): #background sky
	def __init__(self, startx, starty):
		super().__init__(["sprites/back.png"], startx, starty,"sky") 

class EndPoint(Sprite):
	def __init__(self,startx,starty):
		super().__init__(["sprites/flagTall.png"],startx,starty,"end") 

class Invisible(Sprite):
	def __init__(self,startx,starty):
		super().__init__(["sprites/back.png"],startx,starty,"ground") 

	def draw(self,surface):
		pass

class Shop(Sprite):
	def __init__(self,startx,starty):
		super().__init__(["sprites/shop.png","sprites/shop(2).png"],startx,starty,"shop") #invisible wall