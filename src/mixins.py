#! python3

""" Collection of mixins for additional functionality """

# Built-in libraries
import math
import json
from copy import deepcopy
from abc import ABCMeta, abstractmethod

# 3rd-party libraries
import toml

# Local libraries
from settings import *


class DataFileMixin(metaclass=ABCMeta):
    """ Contains methods for getting game data from files """

    @staticmethod
    def _get_by_ID(ID: int, obj_type: str, file: str, file_format=DATA_FORMAT) -> dict:
        """ 'Low-level' access to filedata """
        with open(file) as f:
            if file_format == "json":
                data = json.load(f, parse_int=int, parse_float=float)
            elif file_format == "toml":
                data = toml.load(f)
            else:
                raise NotImplementedError(f"Missing support for opening files of type: {file_format}")
        return data[obj_type][str(ID)]

    def get_item_by_ID(self, ID: int, file=ITEM_FILE) -> dict:
        """ Returns a dictionary representation of a given item ID """
        return self._get_by_ID(ID, 'items', file)

    def get_enemy_by_ID(self, ID: int, file=ENEMY_FILE) -> dict:
        """ Returns a dictionary representation of a given enemy ID """
        return self._get_by_ID(ID, 'enemies', file)

    def get_npc_by_ID(self, ID: int, file=NPC_FILE) -> dict:
        """ Returns a dictionary representation of a given NPC ID """
        return self._get_by_ID(ID, 'NPCs', file)

    def get_entity_by_ID(self, ID: int, file=ENTITY_FILE) -> dict:
        """ Returns a dictionary representation of a given entity ID """
        return self._get_by_ID(ID, 'entities', file)


class ReprMixin(metaclass=ABCMeta):
    """ Automatically generates a __repr__-method for any class """

    def __repr__(self):
        """ Automatically generated __repr__-method """

        attributes = [f"{key}={value}" if type(value) != str
                     else f'{key}="{value}"'
                     for key, value in vars(self).items()]
        v_string = ", ".join(attributes)
        class_name = self.__class__.__name__
        return f"{class_name}({v_string})"


class LevelMixin(metaclass=ABCMeta):
    """ Gives standard level-up mechanics for the child class """
    def __init__(self, **kwargs):
        """
        Initialises the child class' attributes

        Accepted kwargs:
        - level: combat level, defaults to 1
        - max_level: sets a level cap for the object, defaults to None
        - exp: current experience points, defaults to 0
        - exponent: modifies the XP curve required to level-up, defaults to 1.6
        - base_exp: sets the EXP required to reach level 2, defaults to 85
        """
        super(LevelMixin, self).__init__()
        self.level      = int(kwargs.get("level", 1))
        self.experience = int(kwargs.get("exp", 0))
        self.exponent   = float(kwargs.get("exponent", 1.6))
        self.base_exp   = int(kwargs.get("base_exp", 85))
        self.max_level  = kwargs.get("max_level", None)
        self.max_level  = int(self.max_level) if self.max_level is not None else None

    @property
    def next_level(self):
        """
        Returns the amount of EXP needed for the next level.

        No built-in level cap.
        """

        return math.floor(self.base_exp * (self.level**self.exponent))

    def level_up(self, print_exp=False):
        """
        Checks if object has acquired enough EXP to level up.

        If it has, levelup() will increment the player's level and run again until
        the object's EXP isn't enough for the next level, or until max_level is reached
        (unless max_level is None).

        Ends by printing the amount of EXP required to reach the next level.
        If max_level has been set and level >= max_level, nothing is printed.

        This method has an optional argument, print_exp, which will determine if
        the EXP is printed in the end. By default, it will be printed if a level is gained.
        By changing it to True, the EXP required is printed regardless.
        By changing it to None, the EXP is never printed.
        """
        while self.next_level <= self.experience:
            if self.max_level is None or self.level < self.max_level:
                self.level += 1
                if print_exp is not None:
                    print_exp = True
        if print_exp and (self.max_level is None or self.level < self.max_level):
            return f"EXP required for next level: {int(self.next_level-self.experience)}"

    def give_exp(self, amount: int, check_level_up=True, print_exp=False):
        """
        Give the object experience points.

        Automatically checks for level-up unless set to False.
        """
        self.experience += amount
        if check_level_up:
            self.level_up(print_exp)
