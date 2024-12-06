from PIL import Image, ImageDraw, ImageFont
import time
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
asset_path = os.path.join(current_dir, 'assets')

class Menu:
    def __init__(self, joystick):
        self.joystick = joystick
        self.background = Image.open(os.path.join(asset_path, 'background.png')).resize((240, 240))
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        self.small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        self.options = ['easy', 'medium', 'hard', 'exit']
        self.selected = 0
        self.text_color = (0, 0, 139)
        self.highlight_color = (255, 255, 0) 

    def display(self):
        # 메뉴 표시
        while True:
            image = self.background.copy()
            draw = ImageDraw.Draw(image)

            # 타이틀 그리기
            title = "Underground Expedition"
            title_width, title_height = draw.textsize(title, font=self.font)
            title_position = ((240 - title_width) // 2, 40)
            draw.text(title_position, title, font=self.font, fill=self.text_color)

            # 옵션 그리기
            for i, option in enumerate(self.options):
                color = self.highlight_color if i == self.selected else self.text_color
                option_width, option_height = draw.textsize(option, font=self.small_font)
                option_position = ((240 - option_width) // 2, 120 + i * 30)
                draw.text(option_position, option, font=self.small_font, fill=color)

            self.joystick.disp.image(image)

            # 사용자 입력 처리
            if not self.joystick.button_U.value:
                self.selected = (self.selected - 1) % len(self.options)
                time.sleep(0.2)
            elif not self.joystick.button_D.value:
                self.selected = (self.selected + 1) % len(self.options)
                time.sleep(0.2)
            elif not self.joystick.button_A.value:
                if self.selected == 0:
                    return 'easy'
                elif self.selected == 1:
                    return 'medium'
                elif self.selected == 2:
                    return 'hard'
                elif self.selected == 3:
                    return 'exit'
                time.sleep(0.2)

            time.sleep(0.1)