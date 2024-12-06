import time
from PIL import Image, ImageOps
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
asset_path = os.path.join(current_dir, 'assets')

class Player:
    def __init__(self, joystick, game):
        self.joystick = joystick
        self.game = game
        self.x = 0
        self.y = 0
        self.width = 16
        self.height = 16
        self.speed = 0.5
        self.lasers = []
        self.last_laser_time = 0
        self.laser_cooldown = 2.5
        self.dig_time = 0
        self.dig_duration = 0.5
        self.facing_right = True
        self.move_images = [make_transparent(Image.open(os.path.join(asset_path, f'player/move/{i}.png')).resize((16, 16)).convert('RGBA')) for i in range(1, 8)]
        self.move_images_right = [ImageOps.mirror(img) for img in self.move_images]
        self.dig_images = [make_transparent(Image.open(os.path.join(asset_path, f'player/dig/d{i}.png')).resize((16, 16)).convert('RGBA')) for i in range(1, 3)]
        self.dig_images_right = [ImageOps.mirror(img) for img in self.dig_images]
        self.is_digging = False
        self.dig_direction = None
        self.laser_direction = None
        self.current_image = self.move_images[0]
        self.animation_index = 0

    def reset(self):
        # 플레이어 위치 및 상태 초기화
        self.x = 0
        self.y = 0
        self.lasers = []
        self.is_digging = False
        
    def flip_image(self):
        # 플레이어 이미지 좌우 반전
        if not self.facing_right:
            self.current_image = ImageOps.mirror(self.current_image)

    def update_image(self):
        # 플레이어 이미지 업데이트
        current_time = time.time()
        if self.is_digging and current_time - self.dig_time < self.dig_duration:
            dig_index = int((current_time - self.dig_time) / (self.dig_duration / 2))
            if self.facing_right:
                self.current_image = self.dig_images_right[dig_index % 2]
            else:
                self.current_image = self.dig_images[dig_index % 2]
        else:
            if self.facing_right:
                self.current_image = self.move_images_right[self.animation_index]
            else:
                self.current_image = self.move_images[self.animation_index]

    def move(self, direction):
        # 플레이어 이동
        new_x, new_y = self.x, self.y
        if direction == 'up' and self.y > 0:
            new_y -= self.speed
        elif direction == 'down' and self.y < 13:
            new_y += self.speed
        elif direction == 'left' and self.x > 0:
            new_x -= self.speed
            self.facing_right = False
        elif direction == 'right' and self.x < 14:
            new_x += self.speed
            self.facing_right = True

        if self.game.can_move(int(new_x), int(new_y)):
            self.x, self.y = new_x, new_y
    
        self.animation_index = (self.animation_index + 1) % len(self.move_images)
        self.dig_direction = direction
        self.laser_direction = direction
        self.update_image()

    def shoot_laser(self):
        # 레이저 발사
        current_time = time.time()
        if current_time - self.last_laser_time >= self.laser_cooldown and self.laser_direction:
            self.lasers.append(Laser(self.x, self.y, self.laser_direction))
            self.last_laser_time = current_time

    def dig(self):
        # 블록 파괴
        if self.dig_direction:
            dig_x, dig_y = self.x, self.y
            if self.dig_direction == 'up':
                dig_y -= 1
            elif self.dig_direction == 'down':
                dig_y += 1
            elif self.dig_direction == 'left':
                dig_x -= 1
            elif self.dig_direction == 'right':
                dig_x += 1

            if self.game.can_dig(dig_x, dig_y):
                self.game.destroy_block(dig_x, dig_y)
                self.dig_time = time.time()
                self.is_digging = True

    def update(self):
        # 플레이어 상태 업데이트
        current_time = time.time()
        if self.is_digging and current_time - self.dig_time >= self.dig_duration:
            self.is_digging = False

        for laser in self.lasers:
            laser.update()
            if laser.x > 14 or laser.x < 0 or laser.y > 13 or laser.y < 0:
                self.lasers.remove(laser)

        self.update_image()

    def draw(self, image):
        # 플레이어 및 레이저 그리기
        image.paste(self.current_image, (int(self.x * 16), int(self.y * 16 + 16)), self.current_image)
        for laser in self.lasers:
            laser.draw(image)

    def collides_with(self, other):
        # 다른 객체와의 충돌 검사
        return (self.x == other.x and self.y == other.y)

class Laser:
    def __init__(self, x, y, direction):
        # 레이저 초기화
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 0.3
        current_dir = os.path.dirname(os.path.abspath(__file__))
        missile_path = os.path.join(asset_path, 'missile.png')
        self.image = make_transparent(Image.open(missile_path).convert("RGBA").resize((8, 8)))

    def update(self):
        # 레이저 위치 업데이트
        if self.direction == 'up':
            self.y -= self.speed
        elif self.direction == 'down':
            self.y += self.speed
        elif self.direction == 'left':
            self.x -= self.speed
        elif self.direction == 'right':
            self.x += self.speed

    def draw(self, image):
        # 레이저 그리기
        image.paste(self.image, (int(self.x * 16 + 4), int(self.y * 16 + 20)), self.image)

    def collides_with(self, other):
        # 다른 객체와의 충돌 검사
        return (abs(self.x - other.x) < 1 and abs(self.y - other.y) < 1)

    def collides_with_hive(self, hive_x, hive_y):
        # 적의 본거지와의 충돌 검사
        return (abs(self.x - hive_x) < 1 and abs(self.y - hive_y) < 1)
    
def make_transparent(image):
    # 이미지 배경을 투명하게 만듦
    image = image.convert("RGBA")
    data = image.getdata()
    new_data = []
    for item in data:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:  # 검은색인 경우
            new_data.append((0, 0, 0, 0))  # 완전 투명으로 설정
        else:
            new_data.append(item)
    image.putdata(new_data)
    return image