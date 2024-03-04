import pygame

class Text():
    def __init__(self,x,y):
        self.rect = pygame.Rect(x,y,100,40)
        self.value = ""
        self.font = pygame.font.SysFont('freesanbold.ttf', 40)
        self.text = self.font.render(f"name:{self.value}",True,(255,255,0))
        self.rect.width = self.text.get_width() + 10
        self.maxsize = 20

    
    def update(self,event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.key != pygame.K_RETURN and len(self.value) <= self.maxsize:
                self.value += event.unicode #grabs the unicode letter for the button pressed

            self.text = self.font.render(f"name:{self.value}",True,(255,255,0)) #re-renders new text and sets back to default colour (yellow)

            self.rect.width = self.text.get_width() + 10 #resizes the outer bordering rectangle

    def draw(self,screen,rect):
        pygame.draw.rect(screen, (0,0,0), self.rect, 3)       #draws bordering rectangle
        screen.blit(self.text,(self.rect.x+5,self.rect.y+5))  #draws text

        font = pygame.font.SysFont('freesanbold.ttf', 30)
        text = font.render("press enter to set name",True,(255,255,0))
        screen.blit(text,rect)
    
    def getText(self):
        return self.value
    
    def setGreen(self):
        #sets text green for visual confirmation of user creation
        self.text = self.font.render(f"name:{self.value}",True,(0,255,0)) 