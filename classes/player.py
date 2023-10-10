from .sprites import *
import pygame, math


idlerange = [0,5] #ranges for animations in the list
runrange = [7,14]
damagerange = 16
jumprange = [18,25]
attackrange = [27,30]
deathrange = [32,37]

#self.images = [pygame.image.load(image) for image in images]

idle = ["animations/idle/idle(1).png", "animations/idle/idle(2).png", "animations/idle/idle(3).png", "animations/idle/idle(4).png", "animations/idle/idle(5).png", "animations/idle/idle(6).png", "animations/idle/idle(6).png"]
run = ["animations/run/run(1).png","animations/run/run(2).png","animations/run/run(3).png","animations/run/run(4).png","animations/run/run(5).png","animations/run/run(6).png","animations/run/run(7).png","animations/run/run(8).png","animations/run/run(8).png"]
damage = ["animations/damage.png","animations/damage.png"]
jump = ["animations/jump/jump(4).png","animations/jump/jump(5).png","animations/jump/jump(6).png","animations/jump/jump(7).png","animations/jump/jump(8).png","animations/jump/jump(9).png","animations/jump/jump(10).png","animations/jump/jump(11).png","animations/jump/jump(11).png"]
death = ["animations/death/death(1).png","animations/death/death(2).png","animations/death/death(3).png","animations/death/death(4).png","animations/death/death(5).png","animations/death/death(6).png","animations/death/death(6).png"]
attack = ["animations/attack/attack(1).png","animations/attack/attack(2).png","animations/attack/attack(3).png","animations/attack/attack(4).png","animations/attack/attack(4).png"]

gravity = 0.001	
friction = 0.97
jumpForce = -0.49
speed = 0.0008

class Player(Sprite):
	def __init__(self, startx, starty):
		super().__init__(idle+run+damage+jump+attack+death, startx, starty,"player")
		self.xVel = 0
		self.yVel = 0
		self.xMaxSpeed = 0.29
		self.yMaxSpeed = 0.40
		self.grounded = True
		self.right = True
		self.weapon = 0 #default weapon 1 (sword)
		self.past = 1000 #cooldown for attacking
		self.attacks = []
		self.fireprojectile = False
		self.health = 5
		self.damagetime = 2000
		self.dead = False
		self.ammo = 5
		self.currentAnim = None
		self.range = [0,0]
		self.loop = False
		self.playing = False

	def getAttacks(self):
		return self.attacks #returns all attacks 
	
	def removeAttack(self,attack):
		self.attacks.remove(attack) #removes attack
	
	def move(self,dt):
		self.rect.move_ip([self.xVel*dt,self.yVel*dt]) 
		#moves player with delta time compenstating for lag
	
	def draw(self, screen):
		global cameraOffset
		x = self.rect.x - cameraOffset
		y = self.rect.y

		if round(self.animationIndex/15)==27: #corrections for some animation frames
			y = y-12
		elif round(self.animationIndex/15)==29:
			y = y-4

		if self.right == False:#flips image if facing left (images default face right)
			screen.blit(pygame.transform.flip(self.images[round(self.animationIndex/15)],True,False), (x,y))
		else: #player moving right
				screen.blit(self.images[round(self.animationIndex/15)], (x,y))
	
	def collisions(self,boxes,dt):
		end = False
		if self.dead == False: #future collision rect using velocities
			temprect = pygame.Rect(self.rect.x+self.xVel,self.rect.y+self.yVel, self.rect.width, self.rect.height)
			for box in boxes:
				left = False
				right = False
				top = False
				bottom = False
				if box.type == "end" and temprect.colliderect(box.rect): #checks if colliding with end box
					end = True
				elif temprect.colliderect(box.rect) and box.type == "ground":
					if self.xVel != 0: #checking player x collisions
						if box.rect.left < temprect.right and box.rect.left > self.rect.centerx: 
							temprect.right = box.rect.left #player moving right collision
							right = True
						elif box.rect.right > temprect.left and box.rect.right < self.rect.centerx:
							temprect.left = box.rect.right+1 #player moving left collision
							left = True	
					if self.yVel != 0: #checking player y collisions
						if box.rect.top < temprect.bottom and box.rect.top > self.rect.top:					
							temprect.bottom = box.rect.top #player bottom collision
							self.grounded = True 
							bottom = True
						elif box.rect.bottom > temprect.top and box.rect.bottom < self.rect.bottom:
							temprect.top = box.rect.bottom #player top collision	
							top = True

					corner = False 
					if self.yVel <0: #jumping corner collisions
						if right and bottom:
							temprect.right = box.rect.left-1
							temprect.y = self.rect.y+self.yVel
							corner = True
							self.yVel = -0.19
						elif left and bottom:
							temprect.left = box.rect.right+1
							temprect.y = self.rect.y+self.yVel
							corner = True
							self.yVel = -0.19
					elif self.yVel >0: #falling corner collisions
						if right and bottom:
							temprect.right = box.rect.left-1
							temprect.y = self.rect.y+self.yVel
							corner = True
						elif left and bottom:
							temprect.left = box.rect.right+1
							temprect.y = self.rect.y+self.yVel
							corner = True
					if corner == False: #sets velocities to be 0 due to collisions
						if top or bottom:
							self.yVel = 0
						if left or right:
							self.xVel = 0
					self.rect = temprect
						
			temprect = pygame.Rect(self.rect.x,self.rect.y+1, self.rect.width, self.rect.height)
			collided = False
			for box in boxes: #check if player is grounded by checking if there is a box beneath
				if temprect.colliderect(box.rect) and box.type=="ground":
					self.rect.bottom = box.rect.top
					collided = True
			if collided == False:
				self.grounded = False


			self.move(dt)
			return end

	def update(self,dt,clock,screen):
		slash = False
		jump = False	
		global cameraOffset
		if self.dead == False:
			self.past += clock.get_time() #attack movement delay
			self.damagetime += clock.get_time() #iframe timer
			self.xVel *= friction #smoothly decreases x velocity (friction)

			key = pygame.key.get_pressed()#keyboard inputs
			if self.past >= 650: #attack movement delay		 
				if key[pygame.K_LEFT] or key[pygame.K_a]:
					if self.xVel > -self.xMaxSpeed:
						self.xVel = self.xVel - speed*dt #adds left velocity
						self.right = False
				if key[pygame.K_RIGHT] or key[pygame.K_d]:
					if self.xVel < self.xMaxSpeed:
						self.xVel = self.xVel + speed*dt #adds right velocity
						self.right = True
				if key[pygame.K_UP] or key[pygame.K_w]:
					if self.grounded == True:
						self.yVel = jumpForce 
						jump = True #calls for jump animation
						self.grounded = False
				if key[pygame.K_DOWN]: #debug & testing
					print("down")
				if key[pygame.K_1]:
					self.weapon = 0 #select slash attack
				if key[pygame.K_2]:
					self.weapon = 1	 #select projectile attack
				if key[pygame.K_SPACE]:
					if self.weapon == 0 and self.grounded == True and self.past >= 1500: #slash attack
						slash = True
						self.slash(clock)
						
					elif self.weapon == 1 and self.past>=900: #projectile attack
						self.past = 650
						self.fireprojectile = True
						self.projectileArc(screen)

			if self.weapon == 1: #projectile prediction arc
				self.projectileArc(screen)		

			if self.grounded == False: #gravity	
				if self.yVel < self.yMaxSpeed:
					self.yVel = self.yVel + gravity*dt
			else:
				
				self.yVel = 0

		self.animation(dt,jump,slash) #player animatioms
			
		if self.xVel >0:
			cameraOffset += 0.75*dt + self.xVel #adjusts cameraoffset smoothly for player moving left
			if cameraOffset >= self.rect.x - 200:
				cameraOffset = self.rect.x - 200
		elif self.xVel <0:
			cameraOffset -= 0.75*dt + self.xVel #player moving right
			if cameraOffset <= self.rect.x - 500:
				cameraOffset = self.rect.x - 500
		adjustOffset(cameraOffset) #sends back cameraoffset to the sprites file

	def resetOffet(self):
		cameraOffset = self.rect.x - 500
		
		adjustOffset(cameraOffset)

	def animation(self,dt,jump,slash):
		if self.playing: #main animation loop
			self.animationIndex = self.animationIndex+0.075*dt #increments the animation
			if self.animationIndex >= (self.range[1]+1)*15:
				if self.loop == True : #if animation loops then it resets back to start
					self.animationIndex = self.range[0]*15
				else: #if animation doesnt loop, waits for next animation to be triggered
					self.playing = False

		if slash == False and self.past >= 650 and self.dead == False:
			if self.grounded == True and abs(self.xVel)<0.05 and self.currentAnim != "idle": #trigger for idle animation
				self.currentAnim = "idle"
				self.range = idlerange
				self.animationIndex == idlerange[0]
				self.loop = True
				self.playing = True	
			if self.grounded == True and abs(self.xVel)>=0.05 and self.currentAnim != "run": #trigger for run animation
				self.currentAnim = "run"
				self.range = runrange
				self.animationIndex = self.range[0]*15
				self.loop = True
				self.playing = True	
			
			if self.grounded == False and self.currentAnim!= "jump" or jump == True: #trigger for jump animation
				self.currentAnim = "jump"
				self.range = jumprange
				self.animationIndex = self.range[0]*15
				self.loop = False
				self.playing = True

		if slash == True and self.dead == False: #trigger slash animation
			self.currentAnim = "slash"
			self.range = attackrange
			self.animationIndex = self.range[0]*15
			self.loop = False
			self.playing = True
		
		if self.damagetime <=1300 and self.dead == False: #trigger for damage animation
			if self.damagetime >0 and self.damagetime<350 or self.damagetime>700 and self.damagetime<1050 :
				self.currentAnim = "damage"	
				self.animationIndex = damagerange*15
				self.loop = False
				self.playing = True

		if self.dead == True and self.currentAnim != "dead":
			self.currentAnim = "dead"
			self.range = deathrange
			self.animationIndex = self.range[0]*15
			self.loop = False
			self.playing = True

	def slash(self,dt):
		if self.past>=1500: #slash cooldown
			self.past = 0
			if self.right == True:
				self.xVel = 0.40
				self.attacks.append(Slash("slash.png", self.rect.right+25, self.rect.centery))
			if self.right == False:
				self.xVel = -0.40
				self.attacks.append(Slash("slash(2).png", self.rect.left-25, self.rect.centery))
			
	def projectileArc(self,screen):
		projectileVel = 0.65
		pX = self.rect.centerx-cameraOffset #gets player position
		pY = self.rect.centery
		mX,mY=pygame.mouse.get_pos() #gets mouse position
		
		if mX >= pX:
			xDirection = 1
		else:
			xDirection = -1
		if mY <= pY:
			yDirection = -1
		else:
			yDirection = 1
		if abs(pY-mY) != 0: #angles from player to the mouse
			angle = math.atan(abs(mX-pX)/abs(pY-mY))
			projYVel = projectileVel * math.cos(angle)*yDirection #trigonometry using angle for the x and y speed so magnitude is always the same
			projXVel = projectileVel * math.sin(angle)*xDirection
			for i in range(10): #prediction arc for attack
				xS = pX + projXVel * i*30 #SUVAT using the angle to calculate predicted position
				yS = pY + projYVel * i*30 + 0.5*0.0007*(i*30)**2
				pygame.draw.rect(screen,(255,0,0),pygame.Rect(xS, yS, 5, 5),  2)
			if self.fireprojectile == True: #spawns projectile
				if self.ammo > 0: #player must have ammo to spawn a projectile
					self.attacks.append(Projectile(self.rect.centerx, self.rect.centery, projXVel, projYVel))
					self.fireprojectile = False 
					self.ammo = self.ammo-1
					print(f"{self.ammo} ammo left")
				else:
					print("no ammo left")

class Slash(Sprite):
	def __init__(self, image, startx , starty):
		super().__init__([image], startx, starty,"slash")
		self.past = 0
	
	def update(self,clock,rect,right,dt):
		if self.type == "slash":
			self.past += clock.get_time() #slash deletes itself after 500 ms
			if self.past >= 500:
				return "remove"
			else:
				if right == True: #slash follows player position
					self.rect.left = rect.right+5
				else:
					self.rect.right = rect.left-5
				self.rect.y = rect.y
				return

	def draw(self,screen):
		pass
			
class Projectile(Sprite):
	def __init__(self,startx,starty,xVel,yVel):
		super().__init__(["rock.png"],startx,starty,"projectile")	
		self.gravity = 0.0007
		self.xVel = xVel
		self.yVel = yVel
	
	def update(self,dt,boxes):
		self.yVel = self.yVel + self.gravity*dt #adds gravity. xvel stays constant
		self.move(dt)
		return self.checkcollisions(boxes)
	
	def checkcollisions(self,boxes): #checks collisions with ground or walls
		for box in boxes:
			if box.type == "ground":
				if self.rect.colliderect(box.rect):
					return "remove"
	
	def move(self,dt):
		self.rect.move_ip([self.xVel*dt,self.yVel*dt])

