from .sprites import Sprite,getOffset
import pygame,math,random

class Enemy(Sprite):
	def move(self,dt):
		self.rect.move_ip([self.xVel*dt,self.yVel*dt]) 

	def checkCollisions(self,rect):
		if self.rect.colliderect(rect):
			return True
	
	def draw(self,screen):
		cameraOffset = getOffset()
		if self.xVel <0:
			screen.blit(pygame.transform.flip(self.images[round(self.animationIndex//15)],True,False), (self.rect.x-cameraOffset, self.rect.y))
		else:
			screen.blit(self.images[round(self.animationIndex//15)], (self.rect.x-cameraOffset, self.rect.y))

	def animation(self,dt):
		self.animationIndex = self.animationIndex+0.075*dt
		if self.animationIndex >= len(self.images)*15:
			self.animationIndex = 0
		
class Sword(Enemy):
	def __init__(self, startx , starty, static):
		images = ["animations/sword/run1.png","animations/sword/run2.png","animations/sword/run3.png","animations/sword/run4.png","animations/sword/run5.png"]
		super().__init__(images, startx, starty,"sword")
		if static:
			self.speed = 0
		else:
			self.speed = -0.1
		self.distance = 150
		self.startx = startx
	
	def update(self,dt,player): #make enemy detect player distance from center point and then chase player within range??? WIP!!!
		if abs(self.startx - self.rect.centerx) >= self.distance: #enemy only moves left and right
			self.speed = -self.speed
			if self.speed == -0.1:
				self.rect.centerx = self.startx+self.distance
			elif self.speed == 0.1:
				self.rect.centerx = self.startx-self.distance

		self.animation(dt)
		self.move(dt)

	def move(self,dt):
		self.rect.move_ip([self.speed*dt,0]) #enemy has no y velocity
	
	def draw(self, screen):
		cameraOffset = getOffset()
		if self.speed <0:
			screen.blit(pygame.transform.flip(self.images[round(self.animationIndex//15)],True,False), (self.rect.x-cameraOffset, self.rect.y))
		else:
			screen.blit(self.images[round(self.animationIndex//15)], (self.rect.x-cameraOffset, self.rect.y))

class Bat(Enemy):
	def __init__(self, startx , starty):
		images = ["animations/bat/bat(1).png","animations/bat/bat(2).png","animations/bat/bat(1).png"]
		super().__init__(images, startx, starty,"bat")
		self.speed = 0.35
		self.range = 350

	def update(self,dt,player):
		distance = math.sqrt((player.rect.centerx-self.rect.centerx)**2 + (self.rect.centery-player.rect.centery)**2)
		if distance <= self.range:
			self.calcVel(player) #gets distance and checks if player is close enough
		else:
			self.xVel = 0
			self.yVel = 0

		self.animation(dt)
	
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
			self.yVel = self.speed * math.cos(angle)*yDirection #corrects the speed according to directions
			self.xVel = self.speed * math.sin(angle)*xDirection 

	def boxCollisions(self,dt,boxes): #simple box collisions
		self.rect.move_ip([self.xVel*dt,0]) #x axis collisions
		for box in boxes:
			if self.rect.colliderect(box.rect) and box.type == "ground":
				self.rect.move_ip([-self.xVel*dt,0])
				self.xVel = 0

		self.rect.move_ip([0,self.yVel*dt])   #y axis collisions

		for box in boxes:
			if self.rect.colliderect(box.rect) and box.type == "ground":
				self.rect.move_ip([0,-self.yVel*dt]) 
				self.yvel = 0			

idle = ["animations/bow/idle1.png","animations/bow/idle2.png","animations/bow/idle3.png","animations/bow/idle4.png","animations/bow/idle5.png","animations/bow/idle6.png"]
shoot = ["animations/bow/shoot1.png","animations/bow/shoot2.png","animations/bow/shoot3.png","animations/bow/shoot4.png","animations/bow/shoot5.png","animations/bow/shoot6.png","animations/bow/shoot7.png","animations/bow/shoot8.png","animations/bow/shoot9.png","animations/bow/shoot10.png"]
idlerange = [0,5]
shootrange = [6,15]
			 
class Shooter(Enemy):
	def __init__(self, startx , starty):
		super().__init__(idle+shoot, startx, starty,"shooter")
		self.range = 1000
		self.cooldown = 0
		self.projectiles = []
		self.direction = "Right"
		self.currentAnim = "idle"
		self.animRange = idlerange
		self.fire = False

	def update(self,dt,player):
		self.cooldown += dt
		distance = math.sqrt((player.rect.centerx-self.rect.centerx)**2 + (self.rect.centery-player.rect.centery)**2)
		if player.rect.x < self.rect.x:
			self.direction = "Left"
		elif player.rect.x > self.rect.x:
			self.direction = "Right"
		if distance <= self.range and self.cooldown >= 2500:
			self.cooldown = 0
			self.fire = True

		self.animation(dt)

		#time the projectile creation with the animation correctly
		if self.animationIndex > 13*15 and self.animationIndex < 14*15 and self.fire == True:
			self.shoot()
			self.fire = False

	def shoot(self):
		if self.direction == "Right":
			self.projectiles.append(enemyProjectile(self.rect.centerx, self.rect.centery+5+random.randint(-5,5), 0.15)) 
													#random.randint adds slight vertical deviation for visual effect
		else: 
			self.projectiles.append(enemyProjectile(self.rect.centerx, self.rect.centery+5+random.randint(-5,5), -0.15))
	
	def animation(self,dt):
		self.animationIndex = self.animationIndex+0.1*dt #increments the animation
		if self.animationIndex >= (self.animRange[1]+1)*15:
			self.animationIndex = self.animRange[0]*15

		if self.cooldown <1500 and self.currentAnim != "shoot" and self.fire:
			self.currentAnim = "shoot"
			self.animRange = shootrange
			self.animationIndex = self.animRange[0]*15
		
		elif self.cooldown >=1500 and self.currentAnim != "idle":
			self.currentAnim = "idle"
			self.animRange = idlerange
			self.animationIndex = self.animRange[0]*15

	def draw(self,screen):
		cameraOffset = getOffset()
		if self.direction == "Left":
			screen.blit(pygame.transform.flip(self.images[round(self.animationIndex//15)],True,False),\
				(self.rect.x-cameraOffset, self.rect.y))
		else:
			screen.blit(self.images[round(self.animationIndex//15)], (self.rect.x-cameraOffset, self.rect.y))
		
		for proj in self.projectiles:
			proj.draw(screen)

	def updateProjectiles(self,dt,boxes,player):
		for proj in self.projectiles:
			proj.update(dt,player)
			collision = proj.checkcollisions(boxes,player)
			if collision == "remove":
				self.projectiles.remove(proj)
			elif collision == "playerCollision":
				self.projectiles.remove(proj)
				return "playerCollision"

class enemyProjectile(Enemy):
	def __init__(self, startx , starty, speed):
		super().__init__(["sprites/arrow.png"], startx, starty,"shooterProjectile")
		self.xVel = speed
		self.distance = 0
		
	def update(self,dt,player):
		self.rect.x += self.xVel*dt
		self.distance += self.xVel*dt

	def checkcollisions(self,boxes,player): #checks collisions with ground or walls
		for box in boxes:
			if box.type == "ground":
				if self.rect.colliderect(box.rect) or self.distance >= 1000:
					return "remove"
		if self.rect.colliderect(player.rect):
			return "playerCollision"

class Spike(Enemy):
		def __init__(self, startx , starty):
			super().__init__(["sprites/spike.png"], startx, starty,"spike")
			self.xVel = 0
		


