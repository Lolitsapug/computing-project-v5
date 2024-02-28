from .enemies import Enemy,Spike
from .sprites import getOffset
import pygame,math,random

#boss class WIP

class Boss(Enemy):
    def __init__(self, startx,starty):
        super().__init__(["sprites/Golem.png"], startx, starty,"boss")
        self.projectiles = []
        self.time = 0
        self.phase = 0
        self.health = 5
        self.phaseRepeat = 0
        self.state = 0 #when state is 0 the next phase is attack, when 1 the next phase is hearts
        self.waveHeight = 0
        self.check = False
        self.spikeRepeat = False
        self.direction = "L"

    def checkCollisions(self, rect):
        return False

    def getHealth(self):
        return self.health
    
    def resetPhase(self):
        self.projectiles = []
        self.phase = 0
        self.time = 0
        self.phaseRepeat = 0 
        self.check = False
        self.spikeRepeat = False

    def update(self,dt,player):
        self.time += dt

        if self.phase == 0 and self.time > 2000: #choose new boss phase, 3 second delay
                if self.state <= 1:
                    self.phase = random.randint(3,5)
                    self.state += random.randint(1,2) #randomly chooses to do 2 attack phases or 1 attack phase
                elif self.state >= 2:
                    self.phase = random.randint(1,2) 
                    self.state = 0
                self.time = 0
                self.projectiles = []
                print(f"phase:{self.phase}")
                print(f"state:{self.state}")
        
        if self.phase == 1 or self.phase == 2: #phase 1 and 2 spawns hearts for the player to attack
            if self.time == 0:
                if self.phase == 1:
                    self.spawnHearts(False) #spawns spinning harts
                if self.phase == 2:
                    self.spawnHearts(True) #spawns static hearts
                self.time += 1 #to make sure spawning cannot happen twice
                player.ammo = 5 #player has enough ammo to shoot the hearts
            else:
                if self.time < 5000:
                    for heart in self.projectiles:
                        heart.update(dt)
                if self.time > 5000: #10 seconds till phase automatically ends
                    self.resetPhase()

        if self.phase == 3: #death beams
            if self.time == 0:
                self.spawnBeams()
            elif self.time < 1000:
                for beam in self.projectiles:
                    beam.setAlpha(128)
            elif self.time < 4000:
                for beam in self.projectiles:
                    beam.setAlpha(256)
                    if beam.checkCollisions(player.rect): #player has touched a beam and takes damage
                        player.takeDamage()
            elif self.time < 5000:
                self.projectiles = []
            elif self.time > 5000:
                if self.phaseRepeat == 0:
                    self.spawnBeams()
                    self.time = 1
                    self.phaseRepeat += 1
                elif self.phaseRepeat == 1:
                    self.resetPhase()

        if self.phase == 4: #spike wave
            if self.time < 1000:
                if self.check == False:
                    self.check = True
                    self.waveHeight = (player.rect.y//75)*75 +26
                    self.projectiles.append(Spike((self.rect.x+5),(self.waveHeight)))
                    self.projectiles.append(Spike((self.rect.x+55),(self.waveHeight)))
                    self.projectiles[0].images[0].set_alpha(128)
                    self.projectiles[1].images[0].set_alpha(128)
            elif self.time < 1500:
                self.projectiles[0].images[0].set_alpha(128)
                self.projectiles[1].images[0].set_alpha(128)
                if self.projectiles[0].checkCollisions(player.rect) or self.projectiles[1].checkCollisions(player.rect):
                    player.takeDamage()
                self.check = False
            elif self.time <= 1700:
                if self.check == False:
                    self.phaseRepeat += 1 
                    self.projectiles = []
                    self.projectiles.append(Spike((self.rect.x+5-self.phaseRepeat*50),(self.waveHeight)))
                    self.projectiles.append(Spike((self.rect.x-45-self.phaseRepeat*50),(self.waveHeight)))
                    self.projectiles.append(Spike((self.rect.x+5+self.phaseRepeat*50),(self.waveHeight)))
                    self.projectiles.append(Spike((self.rect.x+55+self.phaseRepeat*50),(self.waveHeight)))
                    self.check = True
                for spike in self.projectiles:
                    if spike.checkCollisions(player.rect):
                        player.takeDamage()
            elif self.time >1700:
                if self.phaseRepeat<15:
                    self.time = 1500
                    self.check = False

                elif self.spikeRepeat == False:
                    self.spikeRepeat = True
                    self.time = 1000
                    self.phaseRepeat = 0
                else:
                    self.resetPhase()

        if self.phase == 5: #projectile circle
            if self.time == 0:
                self.spawnProjectiles()
            elif self.time < 5000:
                if self.time < 2000 and self.time > 1000 and self.phaseRepeat == 1:
                    if self.check == False:
                        self.direction = random.choice(["L","R"])
                        if self.direction =="R":
                            self.rect.x += random.randint(50,150)
                            self.direction = "L"
                        elif self.direction == "L":
                            self.rect.x -= random.randint(50,150)
                            self.direction = "R"
                        self.spawnProjectiles()
                        self.check = True
                elif self.time < 3000 and self.time > 2000 and self.phaseRepeat == 1:
                    if self.check == True:
                        if self.direction =="R":
                            self.rect.x += random.randint(50,150)
                        elif self.direction == "L":
                            self.rect.x -= random.randint(50,150)
                        self.rect.x += random.randint(*random.choice([(-200,-100),(100,200)]))
                        self.spawnProjectiles()
                        self.check = False

                for proj in self.projectiles:
                    proj.move(dt)
                    if proj.checkCollisions(player.rect):
                        player.takeDamage()
                        proj.remove()
            elif self.time > 4000:
                if self.phaseRepeat == 0:
                    self.projectiles = []
                    self.time = 0
                    self.spawnProjectiles()
                    self.phaseRepeat += 1
                else:
                    self.resetPhase()

    def draw(self,screen):
        cameraOffset = getOffset()
        screen.blit(self.images[round(self.animationIndex//15)], (self.rect.x-cameraOffset, self.rect.y))
           
        self.drawProjectiles(screen)
        
        self.drawHealthBar(screen,cameraOffset)

    def drawHealthBar(self,screen,cameraOffset):
        for i in range(self.health):
            screen.blit(pygame.image.load("menuImages/Heart.png"), (40*i+self.rect.x-60-cameraOffset,50))
                  
    def drawProjectiles(self,screen):
        for object in self.projectiles:
            object.draw(screen)

    def spawnHearts(self,static):
        self.projectiles.append(Heart(self.rect.centerx,self.rect.centery,static,0))
        self.projectiles.append(Heart(self.rect.centerx,self.rect.centery,static,180))
       
    def checkHeartCollisions(self,rect):
        collision = False
        for heart in self.projectiles: #checks if boss heart has touched a player attack
            if heart.rect.colliderect(rect) and heart.type == "bossHeart":
                collision = True
                self.projectiles.remove(heart)
                self.health -= 1
                if len(self.projectiles) == 0:
                    self.resetPhase()
        return collision

    def spawnBeams(self):
        #spawn beam at boss position
        self.projectiles.append(Beam(self.rect.centerx))
        #use random to randomly spawn 2 beams to the left of the boss and 2 to the right within ranges
        self.projectiles.append(Beam(self.rect.left-random.randint(10,190)))
        self.projectiles.append(Beam(self.rect.left-random.randint(210,340)))
        self.projectiles.append(Beam(self.rect.left-random.randint(360,540)))
        self.projectiles.append(Beam(self.rect.left-random.randint(560,740)))

        self.projectiles.append(Beam(self.rect.right+random.randint(10,290)))
        self.projectiles.append(Beam(self.rect.right+random.randint(210,340)))
        self.projectiles.append(Beam(self.rect.right+random.randint(360,540)))  
        self.projectiles.append(Beam(self.rect.right+random.randint(560,740)))  

    def spawnProjectiles(self):
        self.projectiles.append(bossProjectile(self.rect.centerx,self.rect.top,0,-1))
        self.projectiles.append(bossProjectile(self.rect.centerx,self.rect.bottom,0,1))
        self.projectiles.append(bossProjectile(self.rect.left,self.rect.top,-1,-1))
        self.projectiles.append(bossProjectile(self.rect.right,self.rect.top,1,-1))
        self.projectiles.append(bossProjectile(self.rect.left,self.rect.centery,-1,0))
        self.projectiles.append(bossProjectile(self.rect.right,self.rect.centery,1,0))
        self.projectiles.append(bossProjectile(self.rect.left,self.rect.bottom,-1,1))
        self.projectiles.append(bossProjectile(self.rect.right,self.rect.bottom,1,1))

class Heart(Enemy):
    def __init__(self, startx,starty,static,angle):
        super().__init__(["menuImages/Heart.png"], startx, starty,"bossHeart")
        self.angle = math.radians(angle) #formula only works in radians
        self.radius = 100 #distance from central point(boss)
        self.omega = 0.1 #change in angle speed
        self.startx = startx
        self.starty = starty
        self.rect.x = startx + self.radius * math.cos(self.angle)
        self.rect.y = starty - self.radius * math.sin(self.angle)
        self.static = static
		
    def update(self,dt):
        if not self.static:
            self.angle += self.omega * dt/100 #increasing the angle from centre
            self.rect.x = self.startx + self.radius * math.cos(self.angle)  # Gets the x and y from centre using trigonometry
            self.rect.y = self.starty + self.radius * math.sin(self.angle)  # x + hcos(angle), y + hsin(angle)

    def draw(self, surface):
        cameraOffset = getOffset() #retrieves cameraoffset from player
        surface.blit(self.images[self.animationIndex], (self.rect.x-cameraOffset, self.rect.y))

class Beam(Enemy):
    def __init__(self, startx):
        super().__init__(["sprites/beam.png"], startx, 360,"beam")
        
    def setAlpha(self,alphaValue):
        self.images[0].set_alpha(alphaValue)
    
    def draw(self, surface):
        cameraOffset = getOffset() #retrieves cameraoffset from player
        surface.blit(self.images[self.animationIndex], (self.rect.x-cameraOffset, self.rect.y))

class bossProjectile(Enemy):
    def __init__(self, startx , starty, xvel,yvel):
        super().__init__(["sprites/bossrock.png"], startx, starty,"bossProjectile")
        self.xVel = xvel/4
        self.yVel = yvel/4
    
    def draw(self,screen):
        cameraOffset = getOffset()
        screen.blit(self.images[0], (self.rect.x-cameraOffset, self.rect.y))
		

