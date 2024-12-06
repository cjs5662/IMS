from PIL import Image, ImageDraw, ImageFont
import time
import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
asset_path = os.path.join(current_dir, 'assets')

class Scoreboard:
    def __init__(self, joystick):
        self.joystick = joystick
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        self.small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        self.scores = {'easy': [], 'medium': [], 'hard': []}
        self.background = Image.open(os.path.join(asset_path, 'score.png')).resize((240, 240))
        self.load_scores()

    def load_scores(self):
        # 저장된 점수 불러오기
        if os.path.exists('scores.json'):
            with open('scores.json', 'r') as f:
                self.scores = json.load(f)

    def save_scores(self):
        # 점수 저장
        with open('scores.json', 'w') as f:
            json.dump(self.scores, f)

    def add_score(self, score, difficulty):
        # 새 점수 추가
        self.scores[difficulty].append(score)
        self.scores[difficulty].sort(reverse=True)
        self.scores[difficulty] = self.scores[difficulty][:5]
        self.save_scores()

    def display(self, score, difficulty):
        # 스코어보드 표시 및 사용자 입력 처리
        self.add_score(score, difficulty)
        while True:
            image = self.background.copy()
            draw = ImageDraw.Draw(image)

            # 타이틀 그리기
            title = f"{difficulty.upper()} SCORES"
            title_width, _ = draw.textsize(title, font=self.font)
            draw.text(((240 - title_width) // 2, 10), title, font=self.font, fill=(0, 0, 255))

            # 점수 그리기
            for i, score in enumerate(self.scores[difficulty][:5]):
                draw.text((10, 40 + i * 30), f"{i+1}. {score}", font=self.small_font, fill=(0, 0, 255))

            # 안내 메시지 그리기
            draw.text((10, 200), "Press 5: Menu", font=self.small_font, fill=(0, 0, 255))
            draw.text((10, 220), "Press 6: Other Difficulties", font=self.small_font, fill=(0, 0, 255))

            self.joystick.disp.image(image)

            # 사용자 입력 처리
            if not self.joystick.button_A.value:
                time.sleep(0.2)
                return True
            elif not self.joystick.button_B.value:
                time.sleep(0.2)
                difficulties = ['easy', 'medium', 'hard']
                current_index = difficulties.index(difficulty)
                difficulty = difficulties[(current_index + 1) % 3]

            time.sleep(0.1)