from enum import Enum

class ReminderType(str, Enum):
    MEDICATION = "MEDICATION"
    APPOINTMENT = "APPOINTMENT"
    VACCINATION = "VACCINATION"
    INSURANCE = "INSURANCE"
    FOLLOW_UP = "FOLLOW_UP"

class ReminderFrequency(str, Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

class ReminderStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"
    DISABLED = "DISABLED"

class NotificationType(str, Enum):
    REMINDER = "REMINDER"
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    SYSTEM = "SYSTEM"
