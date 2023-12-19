import pygame

class Text():
    def __init__(self,x,y):
        self.rect = pygame.Rect(x,y,100,40)
        self.value = ""
        self.font = pygame.font.SysFont('freesanbold.ttf', 40)
        self.text = self.font.render(f"name:{self.value}",True,(255,255,0))
        self.rect.width = self.text.get_width() + 10

    
    def update(self,event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.key != pygame.K_RETURN:
                self.value += event.unicode #grabs the unicode letter for the button pressed

            self.text = self.font.render(f"name:{self.value}",True,(255,255,0))

            self.rect.width = self.text.get_width() + 10

    def draw(self,screen):
        pygame.draw.rect(screen, (0,0,0), self.rect, 3)
        screen.blit(self.text,(self.rect.x+5,self.rect.y+5))

        font = pygame.font.SysFont('freesanbold.ttf', 30)
        text = font.render("press enter to set name",True,(255,255,0))
        screen.blit(text,(10,12))
    
    def getText(self):
        return self.value
    
    def setGreen(self):
        self.text = self.font.render(f"name:{self.value}",True,(0,255,0))