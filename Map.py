import random
from PIL import Image
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
asset_path = os.path.join(current_dir, 'assets')

class Map:
    def __init__(self, joystick):
        self.joystick = joystick
        self.width = 15
        self.height = 14
        self.grid = []
        self.block_images = {
            0: Image.open(os.path.join(asset_path, 'blocks/noblock.png')).resize((16, 16)),
            1: Image.open(os.path.join(asset_path, 'blocks/normal_block.png')).resize((16, 16)),
            2: Image.open(os.path.join(asset_path, 'blocks/special_block.png')).resize((16, 16))
        }
        self.hive_images = [
            Image.open(os.path.join(asset_path, 'hive1.png')).resize((16, 16)),
            Image.open(os.path.join(asset_path, 'hive2.png')).resize((16, 16))
        ]
        self.hive_x = self.width - 1
        self.hive_y = self.height - 1
        self.hive_state = 1
        self.enemies_spawned = 0

    def generate_map(self):
        # 맵 생성
        self.grid = [
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]
        ]
        # 30%의 확률로 1을 2로 무작위 변환
        for row in self.grid:
            for i in range(len(row)):
                if row[i] == 1 and random.random() < 0.3:
                    row[i] = 2

    def draw(self, image):
        # 맵 그리기
        for y in range(self.height):
            for x in range(self.width):
                block_type = self.grid[y][x]
                image.paste(self.block_images[block_type], (x * 16, y * 16 + 16))

        if self.hive_state > 0:
            hive_image = self.hive_images[self.hive_state - 1]
            image.paste(hive_image, (self.hive_x * 16, self.hive_y * 16 + 16), hive_image)

    def destroy_block(self, x, y):
        # 블록 파괴
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = 0

    def upgrade_hive(self):
        # 적의 본거지 사냥 가능화
        if self.enemies_spawned >= 10 and self.hive_state == 1:
            self.hive_state = 2

    def destroy_hive(self):
        # 적의 본거지 파괴
        self.hive_state = 0
        self.grid[self.hive_y][self.hive_x] = 0