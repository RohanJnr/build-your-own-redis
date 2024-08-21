from enum import Enum


class State(Enum):
    RESTORING = "restoring"


class RespFirstByte:
    SIMPLE_STRING = "+"
    BULK_STRING = "$"



class Settings:
    AOF_ENABLED = False
    STATE = 1
