from enum import IntEnum

class ProcessingStatus(IntEnum):
    UPLOADED = 0
    PROCESSING = 1
    COMPLETED = 2

class UserStatus(IntEnum):
    INACTIVE = 0
    ACTIVE = 1
    CREATED = 2