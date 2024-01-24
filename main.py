import pygame, sqlite3 #imports
from classes.player import Player
from classes.box import Box,Sky,EndPoint,Invisible,Shop
from classes.enemies import Sword, Bat, Shooter,Spike
from classes.coin import Coin
from classes.textbox import Text
from classes.boss import Boss

print("\n\u001b[31;1mTO COMMIT ON GITHUB ON PYCHARM \nTOP BAR - GIT - COMMIT \nTHEN GIT - PUSH - SELECT COMMITS\n\u001b[0m")

pygame.init()
pygame.mixer.init()
pygame.font.init()

WIDTH = 1280
HEIGHT = 720
BACKGROUND = (69,127,187) #blue

done = False
custom = False
player = None
boxes = []
enemies = []
coins = []
gameTime = 0 #game timer (miliseconds)
score = 0
level = 0 #indicates what level to load
levels = [] #stores game level text file names
menuAnimation = 0

userID = None
textbox = Text(10,40)

fonts = [pygame.font.SysFont('freesanbold.ttf', 60),pygame.font.SysFont('freesanbold.ttf', 50),pygame.font.SysFont('freesanbold.ttf', 40),pygame.font.Font("robotoMono.ttf", 25)]

def createTables():
	connection = sqlite3.connect('Database.db')
	cursor = connection.cursor()
	sqlLeaderboard = '''
	CREATE TABLE IF NOT EXISTS "Leaderboard" (
		"scoreId"	INTEGER UNIQUE,
		"userID"	INTEGER,
		"Time"	INTEGER,
		"Score"	INTEGER,
		"Level"	INTEGER,
		PRIMARY KEY("scoreId" AUTOINCREMENT),
		FOREIGN KEY("userID") REFERENCES "User"("UserID")
	)'''
	#IF NOT EXISTS only creates a table if it doesnt exist.
	sqlUser = '''
	CREATE TABLE IF NOT EXISTS "User" (
	"UserID"	INTEGER UNIQUE,
	"Name"	TEXT,
	PRIMARY KEY("UserID" AUTOINCREMENT)
	)'''
	try:
		cursor.execute(sqlLeaderboard)
		cursor.execute(sqlUser)
		connection.commit()
	except Exception as e:
		print("Error Message :", str(e))
		connection.rollback()

def createUser(name):
	global userID
	connection = sqlite3.connect('Database.db')
	cursor = connection.cursor()
	rec = (name,)
	sql = '''
        INSERT INTO User (Name) VALUES (?)
        '''
	try:
		cursor.execute(sql, rec)
		connection.commit()
	except Exception as e:
		print("Error Message :", str(e))
		connection.rollback()

	sql = '''
	        SELECT UserID FROM User ORDER BY UserID DESC LIMIT 1;
	        '''
	try:
		cursor.execute(sql)
		connection.commit()
		rows = cursor.fetchall()
		userID = rows[0][0]

	except Exception as e:
		print("Error Message :", str(e))
		connection.rollback()
	
	print(f"created user {name}")
	print(f"ID {userID}")

def readData():
	connection = sqlite3.connect('Database.db')
	rows = []
	# preparing a cursor object
	cursor = connection.cursor()
	sql = '''
	        SELECT Score, Time, Level, Name 
	        FROM Leaderboard, User
	        WHERE Leaderboard.userID = User.UserID 
	        ORDER BY Score DESC, Time DESC, scoreId ASC
	        LIMIT 10;
	        '''
	# executing sql statement with try and except incase of errors
	try:
		cursor.execute(sql)
		connection.commit()
		rows = cursor.fetchall()

	except Exception as e:
		print("Error Message :", str(e))
		connection.rollback()
		return "error"

	return rows

def insertData():
	if userID != None and not custom:
		connection = sqlite3.connect('Database.db')
		cursor = connection.cursor()
		rec = (userID, gameTime//1000, score, level)
		sql = '''
			INSERT INTO Leaderboard (userID, Time, Score, Level) VALUES (?, ?, ?, ?)
			'''
		try:
			cursor.execute(sql, rec)
			connection.commit()
		except Exception as e:
			print("Error Message :", str(e))
			connection.rollback()

def createMap(fileName,player):
	global boxes,enemies,coins
	boxes = [] #resets boxes and enemies lists
	enemies = []
	coins = []
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
			elif map[row][column] == "X":#invisible wall
				boxes.append(Invisible(column*75, row*75))
			else:
				boxes.append(Sky(column*75, row*75)) #background sky for all sprites

			if map[row][column] == "/":#sword skeleton
				enemies.append(Sword((column*75)+16, (row*75)+18)) #+29 for height correction
			elif map[row][column] == ">":#bat
				enemies.append(Bat((column*75+5), (row*75)+5)) 
			elif map[row][column] == "+":#shooter
				enemies.append(Shooter((column*75+5), (row*75)+18)) 
			elif map[row][column] == "^":#spike
				enemies.append(Spike((column*75+5), (row*75)+26)) 
			elif map[row][column] == "#":#END
				boxes.append(EndPoint(column*75, 380))#flag goes from base to top
			elif map[row][column] == "@":#player
				player.rect.x,player.rect.y = column*75,row*75+20
			elif map[row][column] == "0":#coin
				coins.append(Coin((column*75), (row*75)+21)) 
			elif map[row][column] == "$":#shop
				boxes.append(Shop((column*75-12), (row*75-6)))
			elif map[row][column] == "B":#boss
				enemies.append(Boss(column*75,row*75)) 

def LoadNextLevel(player): #loads future levels
	global level
	print("starting next level")
	pygame.display.flip()
	player.attacks = []
	player.xVel,player.yVel,player.grounded = 0.00001,0,True #resets player values, v != 0 to reset cameraoffset
	level += 1 #increments level by 1
	if level >= len(levels):
		return True
	createMap(levels[level],player)
	return False

def gameLoop(dt,surface,clock):	
		global gameTime,done, score,coins

		pygame.event.pump()
		for events in pygame.event.get():#quit game event
			if events.type == pygame.QUIT:
				done = True
				pygame.quit() 
			if player.dead == True and pygame.key.get_pressed()[pygame.K_RETURN]: #redirect to deathloop when enter key pressed
				return "gameOver"
	#----------------- GAME LOGIC START--------------------------------
		if player.dead == False:
			gameTime += clock.get_time()
		#onscreen text statistics
		timeText,scoreText,ammoText,moneyText = fonts[1].render(str(gameTime//1000),True,(0,255,0)),fonts[2].render(str(f"score:{score}"),True,(255,255,0)),fonts[2].render(f"ammo:{player.ammo}",True,(255,255,0)),fonts[2].render(f"coins:{player.money}",True,(255,255,0))
		timeRect,scoreRect,ammoRect,moneyRect = timeText.get_rect(),scoreText.get_rect(),ammoText.get_rect(),moneyText.get_rect()
		timeRect.right,timeRect.y = WIDTH-10,10
		scoreRect.x,scoreRect.y = 15,105
		ammoRect.x,ammoRect.y = 15,45
		moneyRect.x,moneyRect.y = 15,75
	
		surface.fill(BACKGROUND)
		for box in boxes:
			box.draw(surface) #draws background so it doesnt cover up projectile arc

		if player.update(dt,clock,surface):
			return "shop"
		IDs = player.collisions(boxes,dt)

		if IDs[0]:#if collision with end flag loads next level
			print("flag collision?")
			if LoadNextLevel(player):
				return "gameOver" #player has reached end of levels#
		
		if IDs[1] == None: #touching a box to trigger different image
			for box in boxes:
				if box.type == "shop":
					box.animationIndex = 0
		else:  # touching a shop
			IDs[1].animationIndex = 1

		for enemy in enemies: #interactions with all enemies
			enemy.update(dt,player) #updates enemies for movement/calculations
			if enemy.type == "bat":
				enemy.boxCollisions(dt,boxes) #collide with the terrain and moves the bat enemy
			if enemy.type == "shooter":
				if enemy.updateProjectiles(dt,boxes,player) == "playerCollision":
					player.takeDamage()
			if enemy.checkCollisions(player.rect) == True: #check enemy collisions with player 
				player.takeDamage()
				if enemy.type != "sword" and enemy.type != "spike" and enemy.type != "shooter": 
					enemies.remove(enemy)
					break
					#enemies like bats die but not the sword, spike or shooter enemy
			for attack in player.getAttacks(): #collisions with player attacks
				if enemy.checkCollisions(attack.rect) == True and enemy.type != "spike" and enemy.type != "boss": #player kills an enemy. adds 10 to score
					enemies.remove(enemy)
					score += 10
					if attack.type == "projectile":
						player.removeAttack(attack)
					break
				if enemy.type == "boss":
					if enemy.checkHeartCollisions(attack.rect):
						player.removeAttack(attack)
					if enemy.getHealth() == 0:
						boxes.append(EndPoint(enemy.rect.centerx, 380))
						enemies.remove(enemy)

		for attack in player.getAttacks():#updates player attack for movement/removal
			if attack.type == "projectile":
				update = attack.update(dt,boxes) #player projectile attack
			else:
				update = attack.update(clock,player.rect,player.right, dt) #player slash attack
			if update == "remove":
				player.removeAttack(attack)

		#check coins
		for coin in coins:
			if coin.checkCollisions(player):
				score += 10
				player.money += 1
				coins.remove(coin)
			else:
				coin.animation(dt)

		if player.dead == True: #gameover screen - redirects to deathLoop()
			GameOver = fonts[1].render("Game Over",True,(255,255,255))
			GameOverRect = GameOver.get_rect()
			GameOverRect.centerx,GameOverRect.centery = WIDTH//2,HEIGHT//3
			surface.blit(GameOver,GameOverRect)

			inputText = fonts[2].render("Press any button to continue",True,(255,255,255))
			inputTextRect = inputText.get_rect()
			inputTextRect.centerx,inputTextRect.top = WIDTH//2,GameOverRect.bottom + 5
			surface.blit(inputText,inputTextRect)

	#----------------- DRAWING START-----------------------------------
		for enemy in enemies:
			enemy.draw(surface)

		for coin in coins:
			coin.draw(surface)

		player.draw(surface)

		for attack in player.getAttacks():
			attack.draw(surface)
		
		surface.blit(timeText,timeRect) #time top right
		surface.blit(scoreText,scoreRect) #score top left
		surface.blit(ammoText,ammoRect) #ammo top left
		surface.blit(moneyText,moneyRect) #money top left

		return "game"

def shopLoop(surface,buttons):
	global done
	pygame.event.pump()
	clicked = None
	for events in pygame.event.get():
		if events.type == pygame.QUIT:
			done = True
			pygame.quit()
		if events.type == pygame.MOUSEBUTTONDOWN and events.button == 1:
			pos = pygame.mouse.get_pos()
			for b in buttons:
				if buttons[b][1].collidepoint(pos) == True:
					print(b + " was clicked")
					clicked = b

	ammoText,moneyText,topText = fonts[2].render(f"ammo:{player.ammo}",True,(255,255,0)),fonts[2].render(f"coins:{player.money}",True,(255,255,0)),fonts[0].render("Shop", True, (255,255,255))

	if clicked == "ammo" and player.money >= 1:
		player.ammo += 3
		player.money -= 1

	elif clicked == "heart" and player.money >= 1:
		player.health += 1
		player.money -= 1
	
	elif clicked == "exit":
		return "game"

	if player.money <= 0:
		moneyText = fonts[2].render(f"coins:{player.money}",True,(255,75,75))
	
	ammoRect,moneyRect,topTextRect = ammoText.get_rect(),moneyText.get_rect(),topText.get_rect()
	ammoRect.x,ammoRect.y = 15,45
	moneyRect.x,moneyRect.y = 15,75
	topTextRect.centerx, topTextRect.centery = WIDTH // 2, 80

	surface.fill(BACKGROUND)

	surface.blit(ammoText,ammoRect) #ammo top left
	surface.blit(moneyText,moneyRect) #money top left
	surface.blit(topText,topTextRect) #money top left

	player.drawHealth(surface)

	for b in buttons:
		surface.blit(buttons[b][0],buttons[b][1]) #blits to surface (button image,button rect)

	return "shop"

def menuLoop(dt,surface,buttons,images,title):
	global done,level,levels,player,gameTime,menuAnimation,custom
	pygame.event.pump()
	
	#check for mouse button click
	clicked = None
	for events in pygame.event.get():
		if events.type == pygame.QUIT:
			done = True
			pygame.quit()
		if events.type == pygame.MOUSEBUTTONDOWN and events.button == 1:
			pos = pygame.mouse.get_pos()
			for b in buttons:
				if buttons[b][1].collidepoint(pos) == True:
					print(b + " was clicked")
					clicked = b

		if events.type == pygame.KEYDOWN:
			textbox.update(events)
			if events.key == pygame.K_RETURN and textbox.value != "":
				textbox.setGreen()
				createUser(textbox.value)

	if clicked == "start": #BUTTON FUNCTIONS
		levels = ["Level0.txt","Level1.txt","Level2.txt","Level3.txt","Level4.txt","Level5.txt"]
		level = 0
		player = Player(100,100)
		gameTime = 0
		custom = False
		createMap(levels[level],player)
		return "game"
	elif clicked == "loadTxt":
		print("loading custom map")
		levels = ["custom.txt"]
		level = 0
		player = Player(100, 100)
		gameTime = 0
		createMap(levels[level],player)
		custom = True #so score doesnt get added to leaderboard
		return "game"	
	elif clicked == "leaderboard":
		return "leaderboard" #load a leaderboard page
	elif clicked == "exit":
		print("quitting game")
		done = True
		pygame.quit()

	menuAnimation = menuAnimation+0.15*dt
	if menuAnimation >= 6*15:
		menuAnimation = 0		
	#------------------ DRAWING SURFACE ---------------------
	surface.blit(images[round(menuAnimation//15)],(0,0))
	surface.blit(title,(0,0))

	textbox.draw(surface,(10,12))

	for b in buttons:
		surface.blit(buttons[b][0],buttons[b][1]) #blits to surface (button image,button rect)
	
	return "menu"

def deathLoop(surface,buttons):
	global done
	pygame.event.pump()
	clicked = None
	for events in pygame.event.get():
		if events.type == pygame.QUIT:
			pygame.quit()
			done = True
		if events.type == pygame.MOUSEBUTTONDOWN and events.button == 1:
			pos = pygame.mouse.get_pos()
			for b in buttons:
				if buttons[b][1].collidepoint(pos) == True:
					print(b + " was clicked")
					clicked = b
	if clicked == "title":
		insertData() #adds data to leaderboard
		return "menu"	
	elif clicked == "leaderboard":
		insertData()
		return "leaderboard"

	textColour = (255,255,255)

	GameOver = fonts[0].render("Game Over!",True,textColour)
	GameOverRect = GameOver.get_rect()
	GameOverRect.centerx,GameOverRect.centery = WIDTH//2,HEIGHT//4+50

	scoreText = fonts[2].render(f"Total Score: {score}",True,textColour)
	scoreRect = scoreText.get_rect()
	scoreRect.x,scoreRect.centery = WIDTH//3,HEIGHT//3+50

	time = fonts[2].render(f"Time: {gameTime//1000}",True,textColour)
	timeRect = time.get_rect()
	timeRect.x,timeRect.centery = WIDTH//3,HEIGHT//3 +100

	levelText = fonts[2].render(f"Level: {level+1}",True,textColour)
	levelRect = levelText.get_rect()
	levelRect.x,levelRect.centery = WIDTH//3,HEIGHT//3 +150

	surface.fill(BACKGROUND)
	for b in buttons:
		surface.blit(buttons[b][0],buttons[b][1]) #blits to surface (button image,button rect)
	
	surface.blit(GameOver,GameOverRect)
	surface.blit(scoreText,scoreRect)
	surface.blit(time,timeRect)
	surface.blit(levelText,levelRect)

	return "gameOver"

def leaderboardLoop(surface):
	global done
	pygame.event.pump()

	for events in pygame.event.get():
		if events.type == pygame.QUIT:
			pygame.quit()
			done = True
		if events.type == pygame.MOUSEBUTTONDOWN and events.button == 1:
			pos = pygame.mouse.get_pos()
			if pygame.Rect(50,580,250,100).collidepoint(pos):
				print("title " + " was clicked")

				return "menu"

	topText = fonts[0].render("Leaderboard", True, (255,255,255))
	topTextRect = topText.get_rect()
	topTextRect.centerx, topTextRect.centery = WIDTH // 2, 100

	surface.fill(BACKGROUND)
	surface.blit(topText, topTextRect)

	rows = readData()
	if rows == "error":
		print("error fetching leaderboard data - returning to menu")
		return "menu"

	for i in range(len(rows)):
		text = fonts[3].render(f"{(str(i+1) + '.').ljust(3,' ')}{rows[i][3].ljust(10,' ')[:10]} | \
Score: {str(rows[i][0]).ljust(4,' ')} | \
Time: {str(rows[i][1]).ljust(4,' ')} | \
Level:{str(rows[i][2]).ljust(2,' ')}", True, (255,255,255))
		rect = text.get_rect()
		rect.x,rect.y = WIDTH/2 - 380,150 + i*40
		surface.blit(text, rect)

	surface.blit(pygame.image.load("menuImages/MENUbutton.png"), pygame.Rect(50,580,250,100))

	return "leaderboard"

#-------------------- MAIN LOOP -----------------------
def main():#initial game initialisation
	global player
	createTables() #creates Leaderboard and User table if they dont exist
	surface = pygame.Surface((WIDTH, HEIGHT)) #seperate surface to potentially add screen scaling.
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	clock = pygame.time.Clock()
	dt = 0 #Time between each frame Delta Time
	player = Player(500, 100)

	menubuttons = { 
		"start":[pygame.image.load("menuImages/PLAYbutton.png"),pygame.Rect(160,250,250,100)],
		"loadTxt":[pygame.image.load("menuImages/LOADbutton.png"),pygame.Rect(160,400,250,100)],
		"leaderboard":[pygame.image.load("menuImages/SCOREbutton.png"),pygame.Rect(870,250,250,100)],
		"exit":[pygame.image.load("menuImages/EXITbutton.png"),pygame.Rect(870,400,250,100)]}

	deathbuttons = {
		"title":[pygame.image.load("menuImages/MENUbutton.png"),pygame.Rect(300,450,250,100)],
		"leaderboard":[pygame.image.load("menuImages/SCOREbutton.png"),pygame.Rect(WIDTH-250-300,450,250,100)]}

	shopbuttons = { 
		"ammo":[pygame.image.load("menuImages/AMMObutton.png"),pygame.Rect(250,250,250,100)],
		"heart":[pygame.image.load("menuImages/HEARTbutton.png"),pygame.Rect(780,250,250,100)],
		"exit":[pygame.image.load("menuImages/EXITbutton.png"), pygame.Rect(150,500,250,100)]}
	
	title = pygame.image.load("menuImages/catlegendstitle.png")
	loadimages = ["menuImages/bg1.png","menuImages/bg2.png","menuImages/bg3.png",\
				"menuImages/bg4.png","menuImages/bg5.png","menuImages/bg6.png","menuImages/bg6.png"]
	images = [pygame.image.load(image) for image in loadimages]

	pygame.mixer.music.load("Grasslands Theme.mp3")
	pygame.mixer.music.set_volume(0.25)
	pygame.mixer.music.play(loops=-1)

	loop = "menu" #switches between menus and game

#----------------- MAIN GAME LOOP START----------------------------	
	while done == False:
		if loop == "game":
			loop = gameLoop(dt,surface,clock)
		elif loop == "shop":
			loop = shopLoop(surface,shopbuttons)
		elif loop == "menu":
			loop = menuLoop(dt,surface,menubuttons,images,title)
		elif loop == "gameOver":
			loop = deathLoop(surface,deathbuttons)
		elif loop == "leaderboard":
			loop = leaderboardLoop(surface)

		scaledSurface = pygame.transform.scale(surface, (1280, 720))  # screen scaling
		screen.blit(scaledSurface, (0, 0))

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
