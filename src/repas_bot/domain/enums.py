from enum import StrEnum

class MealStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

class ParticipationStatus(StrEnum):
    YES = "YES"
    NO = "NO"

class EntryType(StrEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
    ADJUST = "ADJUST"

class EntryStatus(StrEnum):
    POSTED = "POSTED"
    PENDING = "PENDING"
