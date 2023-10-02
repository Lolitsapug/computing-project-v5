from .sprites import Sprite

class Box(Sprite):
	def __init__(self, startx, starty,num):
		super().__init__(["ground.png","ground(2).png"], startx, starty,"ground")
		if num == 1:
			self.animationIndex = 1
		else:
			self.animationIndex = 0	

class Sky(Sprite):
	def __init__(self, startx, starty):
		super().__init__(["back.png"], startx, starty,"sky")	

class EndPoint(Sprite):
	def __init__(self,startx,starty):
		super().__init__(["flagTall.png"],startx,starty,"end") #temporary flag image

class Invisible(Sprite):
	def __init__(self,startx,starty):
		super().__init__(["back.png"],startx,starty,"ground") #invisible wall

	def draw(self,surface):
		pass
