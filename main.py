import pygame

from classes.player import Player
from classes.box import Box,Sky,EndPoint,Invisible
from classes.enemies import Slime, Bat

player = None
boxes = []
enemies = []
level = 0 #indicates what level to load
levels = ["Level1.txt","Level2.txt","Level3.txt"] #prebuilt game levels
gameTime = 0 #timer for leaderboard? WIP to implement
done = False
bg = pygame.image.load("menuImages/catlegendsbackground.png")

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
				boxes.append(EndPoint(column*75, 380))#flag goes from base to top
			elif map[row][column] == "@":#player
				boxes.append(Sky(column*75, row*75))
				player.rect.x,player.rect.y = column*75,row*75+20
			elif map[row][column] == "X":#invisible wall
				boxes.append(Invisible(column*75, row*75))

def LoadNextLevel(player): #loads future levels
	global level
	print("starting next level")
	pygame.display.flip()
	player.attacks = []
	player.xVel,player.yVel,player.grounded = 0.00001,0,True #resets player values, v != 0 to reset cameraoffset
	level += 1 #increments level by 1
	createMap(levels[level],player)

def gameLoop(dt,surface,screen,clock,player):	
		global gameTime,done
		for events in pygame.event.get():
			if events.type == pygame.QUIT:
				done = True
				pygame.quit()

		pygame.event.pump()
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
						#"click a button to exit"
						#check for any button press
						#load death menu, show score & time,"do you want to update leaderboard", redirect to menu page
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

	#----------------- DRAWING START-----------------------------------
		for enemy in enemies:
			enemy.draw(surface)

		player.draw(surface)

		for attack in player.getAttacks():
			attack.draw(surface)
		
		scaledSurface = pygame.transform.scale(surface, (1280, 720)) #screen scaling
		screen.blit(scaledSurface, (0, 0))

	#------------------ END OF GAME LOOP --------------------------------

def shopLoop(screen,player):
	pygame.event.pump()
	#shop pages, buttons, coin counter

def menuLoop(surface,screen,buttons):
	global done,level,levels
	pygame.event.pump()
	
	#check for mouse button click
	clicked = None
	for events in pygame.event.get():
		if events.type == pygame.QUIT:
			pygame.quit()
		if events.type == pygame.MOUSEBUTTONDOWN and events.button == 1:
			pos = pygame.mouse.get_pos()
			for b in buttons:
				if buttons[b][1].collidepoint(pos) == True:
					print(b + " was clicked")
					clicked = b

	if clicked == "start": #MAKE THESE LINK TO THEIR FUNCTIONS
		levels = ["Level1.txt","Level2.txt","Level3.txt"]
		level = 0
		createMap(levels[level],player)
		return "game"
	elif clicked == "loadTxt":
		#txt = input("map txt name"),createmap(txt), levels = [txt,bossfight], loop = "game"
		#levels = ["customMap.txt","BossLevel.txt"]
		level = 0
		createMap(levels[level],player)
		return "game"	
	elif clicked == "leaderboard":
		print("3") #load a leaderboard page
	elif clicked == "exit":
		print("quitting game")
		done = True
		pygame.quit()		
	#------------------ DRAWING SURFACE ---------------------
	surface.blit(bg,(0,0))
	for b in buttons:
		#pygame.draw.rect(surface,(0,0,0),buttons[b][1])
		surface.blit(buttons[b][0],buttons[b][1]) #blits to surface (button image,button rect)
	
	scaledSurface = pygame.transform.scale(surface, (1280, 720)) #screen scaling
	screen.blit(scaledSurface, (0, 0))
	return "menu"
	#------------------ END OF MENU LOOP ---------------------

def deathLoop(screen,gameTime):
	pygame.event.pump()
	#death screen, your score, time taken, update leaderboard


#-------------------- MAIN LOOP -----------------------
WIDTH = 1280
HEIGHT = 720
BACKGROUND = (69,127,187) #blue

def main():#initial game initialisation
	global player
	print("starting game")
	pygame.init()

	dt = 0
	loop = "menu" #switches between menus and game
	surface = pygame.Surface((WIDTH, HEIGHT))
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	clock = pygame.time.Clock()
	player = Player(100, 100) 
	menubuttons = { #ADD IMAGE FILES
		"start":[pygame.image.load("menuImages/PLAYbutton.png"),pygame.Rect(160,200,250,100)],
		"loadTxt":[pygame.image.load("menuImages/LOADbutton.png"),pygame.Rect(160,400,250,100)],
		"leaderboard":[pygame.image.load("menuImages/SCOREbutton.png"),pygame.Rect(870,200,250,100)],
		"exit":[pygame.image.load("menuImages/EXITbutton.png"),pygame.Rect(870,400,250,100)]
	}

#----------------- MAIN GAME LOOP START----------------------------	
	while done == False:
		
		if loop == "game":
			gameLoop(dt,surface,screen,clock,player)
		elif loop == "shop":
			shopLoop(surface,screen,player)
		elif loop == "menu":
			loop = menuLoop(surface,screen,menubuttons)
		elif loop == "gameOver":
			deathLoop(surface,screen,gameTime)

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