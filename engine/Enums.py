from enum import Enum

class PointingNavigationMode(Enum):
    MANUAL=1
    SET_DIRECTION=2
    ZERO_ANGULAR_VELOCITY=3

class VelocityNavigationMode(Enum):
    MANUAL=1
    SET_VELOCITY=2
    SET_THRUST=3

class BTreeResponse(Enum):
    SUCCESS=1
    FAILURE=2
    RUNNING=3

