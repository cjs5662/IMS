import time
from Game import Game
from Menu import Menu
from Scoreboard import Scoreboard
from Joystick import Joystick



joystick = Joystick()
menu = Menu(joystick)
game = Game(joystick)
scoreboard = Scoreboard(joystick)

# 현재 화면 상태를 'menu'로 설정
current_screen = 'menu'

while True:
    if current_screen == 'menu':
        difficulty = menu.display()
        if difficulty == 'exit':
            # 종료 선택 시 루프 종료
            break
        elif difficulty in ['easy', 'medium', 'hard']:
            # 난이도 선택 시 게임 화면으로 전환
            current_screen = 'game'
            game.start(difficulty)
            
    elif current_screen == 'game':
        result = game.run()
        if result == 'game_over' or result == 'game_clear':
            # 게임 종료 시 스코어보드 화면으로 전환
            current_screen = 'scoreboard'
    elif current_screen == 'scoreboard':
        if scoreboard.display(game.score, game.difficulty):
            # 메뉴로 돌아가기 선택 시 메뉴 화면으로 전환
            current_screen = 'menu'

    time.sleep(0.1)

# 게임 종료 시 화면 초기화
joystick.disp.fill(0)
joystick.disp.show()