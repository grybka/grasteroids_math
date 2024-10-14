
import pygame
from enum import Enum
from engine.GameEngine import GameEngine
from gui.GUI import *


class GameState(Enum):
    SELECT_SHIP = 1
    PLAY = 2

class PlayGameState:
    def __init__(self,manager,engine):
        self.game_state = GameState.PLAY
        self.engine=engine
        self.manager=manager

    def update(self,ticks):
        #if there is no player, then we need to select a ship
        if self.engine.my_ship is None and self.game_state!=GameState.SELECT_SHIP:
            self.game_state=GameState.SELECT_SHIP
            ship_names=["ship1","ship2","ship3","ship4","ship5","ship6","ship7","battleship_cruiser"]            
            select_ship_window=SelectShipWindow(self.manager,ship_names,self.engine)            
        elif self.engine.my_ship is not None:
            self.game_state=GameState.PLAY                    