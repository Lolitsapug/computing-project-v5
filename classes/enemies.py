from .sprites import Sprite,getOffset
import pygame,math

class Enemy(Sprite):
	def move(self,dt):
		self.rect.move_ip([self.xVel*dt,self.yVel*dt]) 

	def checkCollisions(self,rect):
		if self.rect.colliderect(rect):
			return True
		
class Slime(Enemy):
	def __init__(self, startx , starty):
		super().__init__(["slime-idle-1.png"], startx, starty,"slime")
		self.xOffset = 0
		self.speed = -0.1
		self.distance = 150
		self.startx = startx
	
	def update(self,dt,player):
		if abs(self.startx - self.rect.centerx) >= self.distance:
			self.speed = -self.speed
			if self.speed == -0.1:
				self.rect.centerx = self.startx+self.distance
			elif self.speed == 0.1:
				self.rect.centerx = self.startx-self.distance

		self.move(dt)

	def move(self,dt):
		self.rect.move_ip([self.speed*dt,0]) 
	
	def draw(self, screen):
		cameraOffset = getOffset()
		if self.speed <0:
			screen.blit(pygame.transform.flip(self.images[self.animationIndex//15],True,False), (self.rect.x-cameraOffset, self.rect.y))
		else:
			screen.blit(self.images[self.animationIndex//15], (self.rect.x-cameraOffset, self.rect.y))

class Bat(Enemy):
	def __init__(self, startx , starty):
		super().__init__(["slime-idle-1.png"], startx, starty,"bat")
		self.xOffset = 0
		self.speed = 0.35
		self.range = 350
		self.startx = startx

	def update(self,dt,player):
		distance = math.hypot(player.rect.centerx-self.rect.centerx, self.rect.centery-player.rect.centery)
		if distance <= self.range:
			self.calcVel(player) #gets distance and checks if player is close enough
		else:
			self.xVel = 0
			self.yVel = 0

	def boxCollisions(self,dt,boxes): #mainly same as player collisions
		
		temprect = pygame.Rect(self.rect.x+self.xVel,self.rect.y+self.yVel, self.rect.width, self.rect.height)
		for box in boxes:
			left = False
			right = False
			top = False
			bottom = False
			if temprect.colliderect(box.rect) and box.type == "ground":
				if self.xVel != 0: 
					if box.rect.left < temprect.right and box.rect.left > self.rect.centerx: 
						temprect.right = box.rect.left 
						right = True
					elif box.rect.right > temprect.left and box.rect.right < self.rect.centerx:
						temprect.left = box.rect.right+1 
						left = True	
				if self.yVel != 0: 
					if box.rect.top < temprect.bottom and box.rect.top > self.rect.top:					
						temprect.bottom = box.rect.top 
						bottom = True
					elif box.rect.bottom > temprect.top and box.rect.bottom < self.rect.bottom:
						temprect.top = box.rect.bottom 	
						top = True
				corner = False 
				if self.yVel <0: 
					if right and bottom:
						temprect.right = box.rect.left-1
						corner = True
						self.yVel = -0.19
					elif left and bottom:
						temprect.left = box.rect.right+1
						corner = True
						self.yVel = -0.19
				elif self.yVel >0: 
					if right and bottom:
						temprect.right = box.rect.left-1
						corner = True
					elif left and bottom:
						temprect.left = box.rect.right+1

						corner = True
				if corner == False: #sets velocities to be 0 due to collisions
					if top or bottom:
						self.yVel = 0
					if left or right:
						self.xVel = 0
				self.rect = temprect
				
		self.move(dt)
	
	def calcVel(self,player): #like projectile calculation moves bat toward player
		if self.rect.centerx >= player.rect.centerx: #gets the directions the mouse is in proportion to the object
			xDirection = -1
		else:
			xDirection = 1
		if self.rect.centery <= player.rect.centery:
			yDirection = 1
		else:
			yDirection = -1
		if abs(player.rect.centery-self.rect.centery) != 0: #makes sure the denominator isnt 0 as cant divide by 0
			#uses arctan of the opposite and adjacent triangle distances to find the angle (trigonometry)
			angle = math.atan(abs(self.rect.centerx-player.rect.centerx)/abs(player.rect.centery-self.rect.centery)) 
			self.yVel = self.speed * math.cos(angle)*yDirection 
			self.xVel = self.speed * math.sin(angle)*xDirection#corrects the speed according to directions

	def draw(self, screen):
		cameraOffset = getOffset()
		if self.xVel <0:
			screen.blit(pygame.transform.flip(self.images[self.animationIndex//15],True,False), (self.rect.x-cameraOffset, self.rect.y))
		else:
			screen.blit(self.images[self.animationIndex//15], (self.rect.x-cameraOffset, self.rect.y))
