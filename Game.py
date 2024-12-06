import time
import random
from PIL import Image, ImageDraw, ImageFont
from Player import Player
from Enemy import Enemy
from Map import Map
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
asset_path = os.path.join(current_dir, 'assets')

class Game:
    def __init__(self, joystick):
        self.joystick = joystick
        self.map = Map(joystick)
        self.player = Player(joystick, self)
        self.enemies = []
        self.enemies_spawned = 0
        self.enemy_spawn_timer = 0
        self.hive_destroyed = False
        self.score = 0
        self.lives = 3
        self.difficulty = None
        self.game_over = False
        self.game_clear = False
        self.clear_background = Image.open(os.path.join(asset_path, 'clear.png')).resize((240, 240))
        self.over_background = Image.open(os.path.join(asset_path, 'over.png')).resize((240, 240))
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)

    def start(self, difficulty):
        # 게임 시작 시 초기화
        self.difficulty = difficulty
        self.map.generate_map()
        self.map.hive_state = 1
        self.map.enemies_spawned = 0 
        self.player.reset()
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_clear = False

        # 난이도에 따른 게임 설정
        if difficulty == 'easy':
            self.player.laser_cooldown = 2.5
            self.enemy_speed_multiplier = 0.3
        elif difficulty == 'medium':
            self.player.laser_cooldown = 3.5
            self.enemy_speed_multiplier = 0.9
        else:  # hard
            self.player.laser_cooldown = 4.5
            self.enemy_speed_multiplier = 1.2

    def run(self):
        # 게임 메인 루프
        while not self.game_over and not self.game_clear:
            self.handle_input()
            self.update()
            self.draw()
            time.sleep(0.05)

        if self.game_over:
            self.draw_game_over()
            return 'game_over'
        elif self.game_clear:
            self.draw_game_clear()
            return 'game_clear'
        
    def can_dig(self, x, y):
        # 해당 위치가 파괴 가능한 블록인지 확인
        x, y = int(x), int(y)
        if x < 0 or y < 0 or y >= len(self.map.grid) or x >= len(self.map.grid[0]):
            return False
        return self.map.grid[y][x] in [1, 2]  # 1: 일반 블럭, 2: 특수 블럭

    def destroy_block(self, x, y):
        # 블록 파괴 및 점수 추가
        x, y = int(x), int(y)
        if self.can_dig(x, y):
            block_type = self.map.grid[y][x]
            self.map.grid[y][x] = 0
            if block_type == 1:
                self.score += 100
            elif block_type == 2:
                self.score += 300

    def handle_input(self):
        # 사용자 입력 처리
        if not self.joystick.button_U.value:
            self.player.move('up')
        elif not self.joystick.button_D.value:
            self.player.move('down')
        elif not self.joystick.button_L.value:
            self.player.move('left')
        elif not self.joystick.button_R.value:
            self.player.move('right')

        if not self.joystick.button_A.value:
            self.player.shoot_laser()
        if not self.joystick.button_B.value:
            self.player.dig()

    def update(self):
        # 게임 상태 업데이트
        self.player.update()
        self.check_collisions()
        self.spawn_enemy()
        
        if self.map.hive_state == 0:
            self.hive_destroyed = True

        # 적 업데이트 및 죽은 적 제거
        self.enemies = [enemy for enemy in self.enemies if not enemy.update(self.player.x, self.player.y, avoid_positions=[(e.x, e.y) for e in self.enemies if e != enemy])]

        # 레이저 업데이트 및 충돌 검사
        for laser in self.player.lasers[:]:
            laser.update()
            x, y = int(laser.x * 16), int(laser.y * 16)
            if x < -8 or x >= self.map.width * 16 - 8 or y < -8 or y >= self.map.height * 16 - 8 or self.map.grid[y // 16][x // 16] in [1, 2]:
                self.player.lasers.remove(laser)
            elif self.map.grid[y // 16][x // 16] in [1, 2]:
                self.destroy_block(x // 16, y // 16)
                self.player.lasers.remove(laser)
        
        # 게임 클리어 체크
        if self.map.hive_state == 0 and len(self.enemies) == 0:
            self.game_clear = True
            self.score += 5000
                
    def update_enemies(self):
        # 적 업데이트
        for enemy in self.enemies:
            enemy.update(self.player.x, self.player.y, avoid_positions=[(e.x, e.y) for e in self.enemies if e != enemy])

    def check_collisions(self):
        # 충돌 검사
        for enemy in self.enemies[:]:
            if abs(self.player.x - enemy.x) < 1 and abs(self.player.y - enemy.y) < 1:
                self.player_hit()

        # 레이저-적 충돌
        for laser in self.player.lasers[:]: 
            for enemy in self.enemies[:]:
                if laser.collides_with(enemy):
                    enemy.die()
                    self.player.lasers.remove(laser)
                    self.score += 300
                    break

        # 레이저-적의 본거지 충돌
        if self.map.hive_state == 2:
            for laser in self.player.lasers[:]:
                if laser.collides_with_hive(self.map.hive_x, self.map.hive_y):
                    self.map.destroy_hive()
                    self.player.lasers.remove(laser)
                    self.score += 1000
                    break

    def spawn_enemy(self):
        # 적 생성
        current_time = time.time()
        if (current_time - self.enemy_spawn_timer >= 3 and len(self.enemies) < 15 and self.map.hive_state > 0):
            spawn_x, spawn_y = self.map.hive_x, self.map.hive_y
            new_enemy = Enemy(self.joystick, spawn_x, spawn_y, self.enemy_speed_multiplier, self)
            self.enemies.append(new_enemy)
            self.enemy_spawn_timer = current_time
            self.enemies_spawned += 1
            self.map.enemies_spawned += 1
            if (self.enemies_spawned >= 10):
                self.map.upgrade_hive()
            
    def player_hit(self):
        # 플레이어 피격 처리
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            # 모든 적 제거
            self.enemies.clear()
            # 플레이어 초기화
            self.player.reset()
            
    def can_move(self, x, y):
        # 해당 위치로 이동 가능한지 확인
        x, y = int(x), int(y)
        if x < 0 or y < 0 or y >= len(self.map.grid) or x >= len(self.map.grid[0]):
            return False
        return self.map.grid[y][x] == 0

    def draw(self):
        # 게임 화면 그리기
        image = Image.new('RGBA', (self.joystick.width, self.joystick.height), (0, 0, 0, 255))
        self.map.draw(image)
        self.player.draw(image)
        for enemy in self.enemies:
            enemy.draw(image)
        self.draw_hud(image)
        self.joystick.disp.image(image.convert('RGB')) 

    def draw_hud(self, image):
        # HUD(점수, 생명) 그리기
        draw = ImageDraw.Draw(image)
        score_text = f'{self.score:05d}'
        life_text = f'Lives: {self.lives}'
        draw.text((0, 0), score_text, fill=(255, 255, 255))
        draw.text((180, 0), life_text, fill=(255, 255, 255))

    def draw_game_over(self):
        # 게임 오버 화면 그리기
        image = self.over_background.copy()
        draw = ImageDraw.Draw(image)
        text = 'GAME OVER'
        text_width, text_height = draw.textsize(text, font=self.font)
        position = ((240 - text_width) // 2, (240 - text_height) // 2)
        draw.text(position, text, font=self.font, fill=(255, 0, 0))
        self.joystick.disp.image(image)
        time.sleep(3)

    def draw_game_clear(self):
        # 게임 클리어 화면 그리기
        image = self.clear_background.copy()
        draw = ImageDraw.Draw(image)
        text = 'GAME CLEAR'
        text_width, text_height = draw.textsize(text, font=self.font)
        position = ((240 - text_width) // 2, (240 - text_height) // 2)
        draw.text(position, text, font=self.font, fill=(0, 255, 0))
        self.joystick.disp.image(image)
        time.sleep(3)