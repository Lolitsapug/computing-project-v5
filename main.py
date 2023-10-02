import pygame

from classes.player import Player
from classes.box import Box,Sky,EndPoint,Invisible
from classes.enemies import Slime, Bat

player = None
boxes = []
enemies = []
level = 0 #indicates what level to load

def createMap(fileName,player):
	global boxes,enemies
	boxes = [] #resets boxes and enemies lists
	enemies = []
	print("creating map.....")
	file = open(fileName, "r")
	map = []
	
	for line in file:#converts text map into a 2d array of characters
		map.append(list(line))
	file.close()
	
	for column in range(len(map[0])): #appends through the array and places the tilesd
		for row in range(len(map)-1):
			if map[row][column] == "=":#grass
				boxes.append(Box(column*75, row*75,0))
			elif map[row][column] == "-":#dirt
				boxes.append(Box(column*75, row*75,1))
			elif map[row][column] == ".":#sky
				boxes.append(Sky(column*75, row*75))
			elif map[row][column] == "^":#slime
				boxes.append(Sky(column*75, row*75))
				enemies.append(Slime((column*75)+16, (row*75)+29)) #+29 for height correction
			elif map[row][column] == ">":#bat
				boxes.append(Sky(column*75, row*75))
				enemies.append(Bat((column*75+5), (row*75)+5)) 
			elif map[row][column] == "#":#END
				boxes.append(Sky(column*75, row*75))
				boxes.append(EndPoint(column*75, 380))
			elif map[row][column] == "@":#player
				boxes.append(Sky(column*75, row*75))
				player.rect.x,player.rect.y = column*75,row*75+20
			elif map[row][column] == "X":#invisible wall
				boxes.append(Invisible(column*75, row*75))

def LoadNextLevel(player,levels):
	global level
	print("starting next level")
	pygame.display.flip()
	player.attacks = []
	player.xVel,player.yVel,player.grounded = 0.00001,0,True #resets player values, v != 0 to reset cameraoffset
	level += 1
	createMap(levels[level],player)

#-----------SETTING UP THE GAME SCREEN-----------------

WIDTH = 1280
HEIGHT = 720
BACKGROUND = (69,127,187) #blue

def main():
	gameTime = 0
	print("starting game")
	surface = pygame.Surface((WIDTH, HEIGHT))
	dt = 0
	pygame.init()
	done = False
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	clock = pygame.time.Clock()
	player = Player(100, 100) #fix camera offset
	levels = ["Level1.txt","Level2.txt","Level3.txt"]

	createMap(levels[level],player)


#----------------- MAIN GAME LOOP START----------------------------	
	while done == False:
#----------------- CHECK FOR EVENTS START--------------------------
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
				
		pygame.event.pump()
		
#----------------- CHECK FOR EVENTS END----------------------------

#----------------- GAME LOGIC START--------------------------------
		gameTime += clock.get_time()
		surface.fill(BACKGROUND)
		for box in boxes:
			box.draw(surface) #draws background so it doesnt cover up projectile arc

		player.update(dt,clock,surface)
		if player.collisions(boxes,dt):
			print("flag collision?")
			LoadNextLevel(player,levels) #if collision with end flag loads next level

		for enemy in enemies: #player collisions with enemy
			enemy.update(dt,player)
			if enemy.type == "bat":
				enemy.boxCollisions(dt,boxes)#collide with the terrain
			if enemy.checkCollisions(player.rect) == True: 
				if player.damagetime >=1300: 
					player.damagetime = 0
					player.health = player.health-1 #player takes damage
					print(f"player health:{player.health}")
					if player.health == 0: # player dies at 0 health
						player.dead = True
					if enemy.type == "bat": 
						enemies.remove(enemy)
						break #enemies like bats die
			for attack in player.getAttacks():
				if enemy.checkCollisions(attack.rect) == True: #player attacks
					enemies.remove(enemy)
					print("enemy killed")
					if attack.type == "projectile":
						player.removeAttack(attack)

		for attack in player.getAttacks():	
			if attack.type == "projectile":
				update = attack.update(dt,boxes) #player projectile attack
			else:
				update = attack.update(clock,player.rect,player.right, dt) #player slash attack
			if update == "remove":
				player.removeAttack(attack)
		

#----------------- GAME LOGIC END ---------------------------------

#----------------- DRAWING START-----------------------------------

		for enemy in enemies:
			enemy.draw(surface)

		player.draw(surface)

		for attack in player.getAttacks():
			attack.draw(surface)
		
		scaledSurface = pygame.transform.scale(surface, (1280, 720)) #screen scaling
		screen.blit(scaledSurface, (0, 0))

		if player.rect.x == 1920 and player.rect.y == 1080:
			LoadNextLevel(boxes,enemies,player)

		pygame.display.flip()
		
#----------------- DRAWING END-------------------------------------
		
		dt = clock.tick(60)
		pygame.display.set_caption("Platformer (xVelocity:"+("%.0f"%(player.xVel*100))+",yVelocity:"+("%.0f"% (player.yVel*100)) + ",fps:" + str(int(clock.get_fps())) + ")") #shows player velocities
		
		

#----------------- MAIN GAME LOOP END ----------------------------
	pygame.quit()

if __name__ == "__main__":
    main()

#https://www.pygame.org/project-Pygame+Text+Input-3013-.html
#text box input for the debugging?