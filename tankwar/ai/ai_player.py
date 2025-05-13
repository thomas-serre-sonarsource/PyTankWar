from tankwar.ai.black_player import BlackPlayer
from tankwar.ai.blue_player import BluePlayer
from tankwar.ai.green_player import GreenPlayer
from tankwar.ai.orange_player import OrangePlayer
from tankwar.ai.purple_player import PurplePlayer
from tankwar.ai.red_player import RedPlayer


if __name__ == '__main__':
    ai_players = [ BluePlayer(), OrangePlayer(), RedPlayer(), BlackPlayer(), PurplePlayer(), GreenPlayer()]
    while True:
        for ai_player in ai_players:
            ai_player.play()