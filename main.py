import pygame
import numpy as np
import copy

FPS = 60 

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800

class Crowd():
    def __init__(self, x, y):
        self.radius = 2
        self.color = (0, 0, 0)
        self.target_x = x
        self.target_y = y
        self.base_vector = (0, 0)
        self.base_x = x
        self.base_y = y
        self.mod_x = 0
        self.mod_y = 0
        self.max_rad = 0
        self.vector = (0, 0)
        self.vel = 0
        self.base_move_timer = 0
        self.color_change_timer = 0
        self.float_color = (0, 0, 0)
        self.target_color = (0, 0, 0)
        self.color_change_ammount = (0, 0, 0)

    def SetRadius(self, max_rad):
        self.max_rad = max_rad
        
    def SetVelocity(self, vel, bSetRandomVector = False):
        if vel < self.max_rad / 3.0:
            self.vel = vel
            if bSetRandomVector:
                self.SetRandomVector()
        else:
            print("wrong velocity.     rad:{}      new_vel:{}".format(self.max_rad, vel))

    def SetRandomVector(self):
        if self.vel < self.max_rad / 3.0:
            while True:
                self.vector = np.random.randn(2)
                self.vector = self.vector / np.linalg.norm(self.vector) * self.vel
                if abs(self.mod_x + self.vector[0]) <= self.max_rad and abs(self.mod_y + self.vector[1]) <= self.max_rad:
                    break

    def Update(self):
        tmp_mod_x = 0
        tmp_mod_y = 0
        while True:
            tmp_mod_x = self.mod_x + self.vector[0]
            tmp_mod_y = self.mod_y + self.vector[1]
            if tmp_mod_x ** 2 + tmp_mod_y ** 2 > self.max_rad ** 2:
                self.SetRandomVector()
            else: break
        self.mod_x = tmp_mod_x
        self.mod_y = tmp_mod_y
        if self.base_move_timer > 0:
            self.base_move_timer -= 1
            self.base_x += self.base_vector[0]
            self.base_y += self.base_vector[1]
        if self.color_change_timer > 0:
            self.color_change_timer -= 1
            self.float_color = (self.float_color[0] + self.color_change_ammount[0],
                                self.float_color[1] + self.color_change_ammount[1],
                                self.float_color[2] + self.color_change_ammount[2],)
            self.color = (round(self.float_color[0]), round(self.float_color[1]), round(self.float_color[2]))

    def Draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.base_x + self.mod_x, self.base_y + self.mod_y), self.radius)

    def SetBase(self, x, y, seconds):
        self.target_x = x
        self.target_y = y
        self.base_vector = ((x - self.base_x) / (seconds * FPS), (y - self.base_y) / (seconds * FPS))
        self.base_move_timer = seconds * FPS

    def SetColor(self, color, seconds):
        self.target_color = color
        self.color_change_timer = seconds * FPS
        self.color_change_ammount = ((self.target_color[0] - self.color[0]) / self.color_change_timer, 
                                     (self.target_color[1] - self.color[1]) / self.color_change_timer, 
                                     (self.target_color[2] - self.color[2]) / self.color_change_timer)


class CrowdController():
    def __init__(self):
        self.crowds = [Crowd(0, 0)]
        self.row = 0
        self.col = 0
        self.gap = 0

    def Draw(self, screen):
        for i in range(self.row):
            for j in range(self.col):
                self.crowds[i * self.row + j].Draw(screen)
    
    def Update(self):
        for i in range(self.row):
            for j in range(self.col):
                self.crowds[i * self.row + j].Update()

    def SetCrowdFormation(self, center_x, center_y, gap, row, col, seconds = 0.001):
        tmp_index = 0
        while row * col > len(self.crowds):
            instance = copy.deepcopy(self.crowds[tmp_index])
            self.crowds.append(instance)
            tmp_index += 1
        self.row = row
        self.col = col
        start_x = center_x - (col - 1) * gap * 0.5
        start_y = center_y - (row - 1) * gap * 0.5
        for i in range(self.row):
            for j in range(self.col):
                self.crowds[i * self.row + j].SetBase(start_x + (j - 1) * gap, start_y + (i - 1) * gap, seconds)

    def SetCrowdMovement(self, vibe_radius, vibe_velocity):
        for i in range(self.row):
            for j in range(self.col):
                self.crowds[i * self.row + j].SetRadius(vibe_radius)
                self.crowds[i * self.row + j].SetVelocity(vibe_velocity, True)

    def SetCrowdColor(self, color, seconds = 0.001):
        for i in range(self.row):
            for j in range(self.col):
                self.crowds[i * self.row + j].SetColor(color, seconds)

def main():
    pygame.init() 

    screen = pygame.display.set_mode( (WINDOW_WIDTH, WINDOW_HEIGHT) )
    clock = pygame.time.Clock()

    crowd = CrowdController()
    crowd.SetCrowdFormation(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 30, 10, 10, 10)
    crowd.SetCrowdColor((255, 255, 255), 10)
    crowd.SetCrowdMovement(5, 1)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if 0x31 <= event.key & event.key <= 0x36:
                    print("hello")

        screen.fill((0, 0, 0))

        crowd.Update()
        crowd.Draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()