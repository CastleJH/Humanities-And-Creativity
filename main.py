import pygame
import numpy as np
import copy

FPS = 60 
CROWD_SIZE = 2
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800

global my_font

def DrawText(screen, text, red = False):
    global my_font
    gap = 10
    color = (255, 255, 255)
    if red: color = (255, 0, 0)
    target = my_font.render(text, True, color)
    pygame.draw.rect(screen, (10, 10, 10), (WINDOW_WIDTH // 2 - target.get_width() // 2 - gap, WINDOW_HEIGHT - 100 - target.get_height() // 2 - gap * 0.5, target.get_width() + gap * 2, target.get_height() + gap))
    screen.blit(target, (WINDOW_WIDTH // 2 - target.get_width() // 2, WINDOW_HEIGHT - 100 - target.get_height() // 2))

class Crowd():
    def __init__(self, x, y):
        self.radius = CROWD_SIZE
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
        self.bDraw = True
        self.special = False

    def SetRadius(self, max_rad):
        self.max_rad = max_rad
        
    def SetVelocity(self, vel, bSetRandomVector = False):
        if vel < self.max_rad / 3.0:
            self.vel = vel
            if bSetRandomVector:
                self.SetRandomVector()
        else:
            self.vel = 0
            self.max_rad = 0.1
            print("wrong velocity.     rad:{}      new_vel:{}".format(self.max_rad, vel))

    def SetRandomVector(self):
        if self.vel < self.max_rad / 3.0:
            while True:
                if self.vel == 0 or self.max_rad == 0: break
                self.vector = np.random.randn(2)
                self.vector = self.vector / np.linalg.norm(self.vector) * self.vel
                if abs(self.mod_x + self.vector[0]) <= self.max_rad and abs(self.mod_y + self.vector[1]) <= self.max_rad:
                    break

    def Update(self):
        if self.color_change_timer > 0:
            self.color_change_timer -= 1
            self.float_color = (self.float_color[0] + self.color_change_ammount[0],
                                self.float_color[1] + self.color_change_ammount[1],
                                self.float_color[2] + self.color_change_ammount[2],)
            self.color = (round(self.float_color[0]), round(self.float_color[1]), round(self.float_color[2]))
        if self.vel == 0 and not self.special: return
        tmp_mod_x = 0
        tmp_mod_y = 0
        while True:
            if self.vel == 0 or self.max_rad == 0: break
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

    def Draw(self, screen):
        if self.bDraw:
            pygame.draw.circle(screen, self.color, (self.base_x + self.mod_x, self.base_y + self.mod_y), self.radius)

    def SetBase(self, x, y, seconds):
        seconds = max(seconds, 0.0001)
        self.target_x = x
        self.target_y = y
        self.base_vector = ((x - self.base_x) / (seconds * FPS), (y - self.base_y) / (seconds * FPS))
        self.base_move_timer = seconds * FPS

    def SetColor(self, color, seconds):
        seconds = max(seconds, 0.0001)
        self.target_color = color
        self.color_change_timer = max(seconds * FPS, 1)
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
                self.crowds[i * self.col + j].Draw(screen)
    
    def Update(self):
        for i in range(self.row):
            for j in range(self.col):
                self.crowds[i * self.col + j].Update()

    def SetCrowdFormation(self, center_x, center_y, gap, row, col, seconds):
        seconds = max(seconds, 0.0001)
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
                self.crowds[i * self.col + j].SetBase(start_x + j * gap, start_y + i * gap, seconds)

    def SetCrowdMovement(self, vibe_radius, vibe_velocity):
        for i in range(self.row):
            for j in range(self.col):
                self.crowds[i * self.col + j].SetRadius(vibe_radius)
                self.crowds[i * self.col + j].SetVelocity(vibe_velocity, True)

    def SetCrowdColor(self, color, seconds):
        seconds = max(seconds, 0.0001)
        for i in range(self.row):
            for j in range(self.col):
                self.crowds[i * self.col + j].SetColor(color, seconds)

    def OnOffCrowd(self, row, col, bDraw):
        if row * self.col + col <= len(self.crowds):
            self.crowds[row * self.col + col].bDraw = bDraw
        else:
            print("wrong index")

def RenderAll(screen, crowd, bRenderCrowd, talker, bRenderTalker, dictator, bRenderDictator, questioner = None, bRenderQuestioner = False, bRenderQuestionerFirst = False):
    if bRenderQuestioner and bRenderQuestionerFirst == True:
        questioner.Update()
        questioner.Draw(screen)
    if bRenderCrowd:
        crowd.Update()
        crowd.Draw(screen)
    if bRenderTalker:
        talker.Update()
        talker.Draw(screen)
    if bRenderDictator:
        dictator.Update()
        dictator.Draw(screen)
    if bRenderQuestioner and bRenderQuestionerFirst == False:
        questioner.Update()
        questioner.Draw(screen)


def main():
    global my_font
    pygame.init() 

    screen = pygame.display.set_mode( (WINDOW_WIDTH, WINDOW_HEIGHT) )
    my_font = pygame.font.Font("HANDotum.ttf", 20)

    clock = pygame.time.Clock()

    crowd = CrowdController()
    crowd.SetCrowdFormation(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 15, 60, 100, 3)
    #crowd.SetCrowdColor((200, 200, 200), 3)
    crowd.SetCrowdMovement(2, 0.1)
    talker = Crowd(WINDOW_WIDTH // 2, 120)
    talker.SetBase(WINDOW_WIDTH // 2, 120, 0.01)
    talker.SetColor((255, 255, 255), 1)
    talker.radius = 5
    dictator = Crowd(WINDOW_WIDTH // 2, 70)
    dictator.SetBase(WINDOW_WIDTH // 2, 70, 0.01)
    dictator.SetColor((255, 255, 255), 1)
    dictator.radius = 10
    dictator.special = True
    questioner = Crowd(WINDOW_WIDTH // 3 * 2, WINDOW_HEIGHT // 3 * 2)
    questioner.SetBase(WINDOW_WIDTH // 3 * 2, WINDOW_HEIGHT // 3 * 2, 0.01)
    questioner.SetColor((255, 255, 255), 1)
    questioner.special = True

    for i in range(16):
        for j in range(8):
            crowd.OnOffCrowd(i, j + 46, False)

    done = False
    sequence = 0

    sound = pygame.mixer.Sound('voice.mp3')
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    sound.play(loops = -1)
                elif event.key == pygame.K_SPACE: 
                    sequence += 1

        screen.fill((0, 0, 0))
        print(sequence)
        if sequence == 0:
            print('hello')
            crowd.Update()
            talker.Update()
            dictator.Update()
            crowd.Draw(screen)
            talker.Draw(screen)
            dictator.Draw(screen)

        elif sequence == 1:
            # 사회자가 외쳤다
            crowd.SetCrowdMovement(10, 0.000001)
            crowd.SetCrowdColor((80, 80, 80), 0.1)
            sequence += 1
        elif sequence == 2:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "사회자가 외쳤다")
        elif sequence == 3:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "여기 일생 동안 이웃을 위해 산 분이 계시다")
        elif sequence == 4:
            crowd.SetCrowdMovement(5, 0.01)
            crowd.SetCrowdColor((255, 255, 255), 20)
            sequence += 1
        elif sequence == 5:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "이웃의 슬픔은 이분의 슬픔이었고")
        elif sequence == 6:
            crowd.SetCrowdMovement(5, 0.02)
            crowd.SetCrowdColor((255, 255, 255), 20)
            sequence += 1
        elif sequence == 7:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "이분의 슬픔은 이글거리는 빛이었다")
        elif sequence == 8:
            crowd.SetCrowdMovement(5, 0.04)
            talker.SetRadius(3)
            talker.SetVelocity(0.04, True)
            sequence += 1
        elif sequence == 9:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "사회자는 하늘을 걸고 맹세했다")
        elif sequence == 10:
            crowd.SetCrowdMovement(5, 0.08)
            talker.SetRadius(3)
            talker.SetVelocity(0.08)
            sequence += 1
        elif sequence == 11:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "이분은 자신을 위해 푸성귀 하나 심지 않았다")
        elif sequence == 12:
            crowd.SetCrowdMovement(5, 0.12)
            talker.SetRadius(3)
            talker.SetVelocity(0.12)
            sequence += 1
        elif sequence == 13:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "눈물 한 방울도 자신을 위해 흘리지 않았다")

        elif sequence == 14:
            # 
            crowd.SetCrowdMovement(5, 0.16)
            talker.SetRadius(3)
            talker.SetVelocity(0.16)
            sequence += 1
        elif sequence == 15:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "사회자는 흐느꼈다")

        elif sequence == 16:
            # 
            crowd.SetCrowdMovement(5, 0.16)
            talker.SetRadius(3)
            talker.SetVelocity(0.16)
            sequence += 1
        elif sequence == 17:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "보라, 이분은 당신들을 위해 청춘을 버렸다")
        elif sequence == 18:
            # 
            crowd.SetCrowdMovement(7, 0.2)
            talker.SetRadius(3)
            talker.SetVelocity(0.2)
            sequence += 1
        elif sequence == 19:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "당신들을 위해 죽을 수도 있다")

        elif sequence == 20:
            # 
            crowd.SetCrowdMovement(7, 0.3)
            sequence += 1
        elif sequence == 21:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "그분은 일어서서 흐느끼는 사회자를 제지했다")

        elif sequence == 22:
            # 군중들은 일제히 그분에게 박수를 쳤다
            crowd.SetCrowdMovement(7, 0.5)
            sequence += 1
        elif sequence == 23:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "군중들은 일제히 그분에게 박수를 쳤다")

        elif sequence == 24:
            # 사내들은 울먹였고 감동한 여인들은 실신했다
            crowd.SetCrowdMovement(7, 0.8)
            sequence += 1
        elif sequence == 25:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "사내들은 울먹였고 감동한 여인들은 실신했다")

        elif sequence == 26:
            # 
            crowd.SetCrowdMovement(5, 0)
            crowd.SetCrowdColor((150, 150, 150), 0.01)
            talker.SetVelocity(0)
            sequence += 1
        elif sequence == 27:
            RenderAll(screen, crowd, True, talker, True, dictator, True, questioner, True)
            DrawText(screen, "그때 누군가 그분에게 물었다, 당신은 신인가")

        elif sequence == 28:
            # 그분은 목소리를 향해 고개를 돌렸다
            # 당신은 유령인가, 목소리가 물었다
            dictator.SetColor((255, 0, 0), 10)
            talker.SetColor((50, 50, 50), 0.01)
            crowd.SetCrowdColor((25, 25, 25), 0.01)
            sequence += 1
        elif sequence == 29:
            RenderAll(screen, crowd, True, talker, True, dictator, True, questioner, True)
            DrawText(screen, "그분은 목소리를 향해 고개를 돌렸다")
        elif sequence == 30:
            RenderAll(screen, crowd, True, talker, True, dictator, True, questioner, True)
            DrawText(screen, "당신은 유령인가, 목소리가 물었다")

        elif sequence == 31:
            # 저 미치광이를 끌어내, 사회자가 소리쳤다
            talker.SetColor((255, 0, 0), 0.01)
            talker.SetRadius(5)
            talker.SetVelocity(1.3, True)
            sequence += 1
        elif sequence == 32:
            RenderAll(screen, crowd, True, talker, True, dictator, True, questioner, True)
            DrawText(screen, "저 미치광이를 끌어내, 사회자가 소리쳤다", True)

        elif sequence == 33:
            # 사내들은 달려갔고 분노한 여인들은 날뛰었다
            crowd.SetCrowdColor((255, 0, 0), 2)
            crowd.SetCrowdFormation(WINDOW_WIDTH // 3 * 2, WINDOW_HEIGHT // 3 * 2, 0.2, 60, 100, 2)
            crowd.SetCrowdMovement(40, 3)
            sequence += 1
        elif sequence == 34:
            RenderAll(screen, crowd, True, talker, True, dictator, True, questioner, True, True)
            DrawText(screen, "사내들은 달려갔고 분노한 여인들은 날뛰었다", True)

        elif sequence == 35:
            # 그분은 성난 사회자를 제지했다
            # 군중들은 일제히 그분에게 박수를 쳤다
            # 사내들은 울먹였고 감동한 여인들은 실신했다
            # 그분의 답변은 군중들의 아우성 때문에 들리지 않았다
            crowd.SetCrowdColor((255, 150, 150), 3)
            crowd.SetCrowdFormation(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 15, 60, 100, 3)
            crowd.SetCrowdMovement(40, 0.7)
            sequence += 1
        elif sequence == 36:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "그분은 성난 사회자를 제지했다", True)
        elif sequence == 37:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "군중들은 일제히 그분에게 박수를 쳤다", True)
        elif sequence == 38:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "사내들은 울먹였고 감동한 여인들은 실신했다", True)
        elif sequence == 39:
            RenderAll(screen, crowd, True, talker, True, dictator, True)
            DrawText(screen, "그분의 답변은 군중들의 아우성 때문에 들리지 않았다", True)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()