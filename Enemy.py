import time
from PIL import Image, ImageOps
from queue import PriorityQueue
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
asset_path = os.path.join(current_dir, 'assets')

class Enemy:
    def __init__(self, joystick, x, y, speed_multiplier, game):
        self.joystick = joystick
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.speed = 0.5 * speed_multiplier
        self.game = game
        self.move_images = [make_transparent(Image.open(os.path.join(asset_path, f'enemy/move/e{i:02d}.png')).resize((16, 16)).convert('RGBA')) for i in range(12)]
        self.move_images_left = [ImageOps.mirror(img) for img in self.move_images]
        self.die_images = [make_transparent(Image.open(os.path.join(asset_path, f'enemy/die/d{i:02d}.png')).resize((16, 16)).convert('RGBA')) for i in range(1, 9)]
        self.die_images_left = [ImageOps.mirror(img) for img in self.die_images]
        self.current_image = self.move_images[0]
        self.path = []
        self.current_path_index = 0
        self.facing_right = True
        self.animation_index = 0
        self.is_dying = False
        self.die_time = 0
        self.die_duration = 1.0

    def update(self, player_x, player_y, avoid_positions):
        # 적 상태 업데이트
        if self.is_dying:
            current_time = time.time()
            if current_time - self.die_time >= self.die_duration:
                return True 
            die_index = int((current_time - self.die_time) / self.die_duration * len(self.die_images))
            self.current_image = self.die_images[min(die_index, len(self.die_images) - 1)] if self.facing_right else self.die_images_left[min(die_index, len(self.die_images) - 1)]
        else:
            if not self.path or self.current_path_index >= len(self.path):
                self.path = self.find_path_to_player(player_x, player_y)
                self.current_path_index = 0

            if self.path:
                next_x, next_y = self.path[self.current_path_index]
                dx = next_x - self.x
                dy = next_y - self.y
                distance = ((dx ** 2) + (dy ** 2)) ** 0.5

                if distance > 0:
                    move_distance = min(self.speed, distance)
                    move_x = (dx / distance) * move_distance
                    move_y = (dy / distance) * move_distance

                    new_x = self.x + move_x
                    new_y = self.y + move_y

                    # 90도 꺾임 감지 및 추가 이동
                    if self.current_path_index < len(self.path) - 1:
                        next_next_x, next_next_y = self.path[self.current_path_index + 1]
                        if (abs(next_x - next_next_x) == 1 and abs(next_y - next_next_y) == 1):
                            threshold = 0.1 + (self.speed - 0.15) * 0.3  # 속도에 따라 임계값 조정
                            if abs(new_x - int(new_x)) < threshold and abs(new_y - int(new_y)) < threshold:
                                self.current_path_index += 1
                                dx = next_next_x - new_x
                                dy = next_next_y - new_y
                                remaining_distance = ((dx ** 2) + (dy ** 2)) ** 0.5
                                if remaining_distance > 0:
                                    move_x += (dx / remaining_distance) * min(self.speed * 0.5, remaining_distance)
                                    move_y += (dy / remaining_distance) * min(self.speed * 0.5, remaining_distance)

                    self.x += move_x
                    self.y += move_y

                    if move_x > 0:
                        self.facing_right = True
                    elif move_x < 0:
                        self.facing_right = False

                    self.animation_index = (self.animation_index + 1) % len(self.move_images)
                    self.current_image = self.move_images[self.animation_index] if self.facing_right else self.move_images_left[self.animation_index]

                if abs(self.x - next_x) < 0.1 and abs(self.y - next_y) < 0.1:
                    self.current_path_index += 1

        return False

    def find_path_to_player(self, player_x, player_y):
        # A* 알고리즘을 사용하여 플레이어까지의 경로 찾기
        start = (int(self.x), int(self.y))
        goal = (int(player_x), int(player_y))
        
        open_set = PriorityQueue()
        open_set.put((0, start))
        
        came_from = {}
        
        g_score = {start: 0}
        
        while not open_set.empty():
            _, current = open_set.get()
            
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            neighbors = [(current[0] + dx, current[1] + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
            
            for neighbor in neighbors:
                if not (0 <= neighbor[0] < len(self.game.map.grid[0]) and 
                        0 <= neighbor[1] < len(self.game.map.grid)):
                    continue
                
                if not (self.game.map.grid[neighbor[1]][neighbor[0]] == 0): 
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    
                    f_score = tentative_g_score + abs(goal[0] - neighbor[0]) + abs(goal[1] - neighbor[1])
                    open_set.put((f_score, neighbor))
        
        return None

    def draw(self, image):
        # 적 그리기
        image.paste(self.current_image, (int(self.x * 16), int(self.y * 16 + 16)), self.current_image)

    def die(self):
        # 적 사망 처리
        if not self.is_dying:
            self.is_dying = True
            self.die_time = time.time()
            self.current_image = self.die_images[0] if self.facing_right else self.die_images_left[0]

def make_transparent(image):
    # 이미지 배경을 투명하게 만듦
    data = image.getdata()
    new_data = []
    for item in data:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:  # 검은색인 경우
            new_data.append((0, 0, 0, 0))  # 완전 투명으로 설정
        else:
            new_data.append(item)
    image.putdata(new_data)
    return image