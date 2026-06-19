from .user import User
from .family_member import FamilyMember
from .health_record import HealthRecord
from .doctors_visit import DoctorsVisit
from .appointment import Appointment
from .medications import Medications
from .password_reset_token import Password_Reset_Token
from .prescription import PrescriptionDocument, PrescriptionMedicine


# __init__.py file is used to mark a directory as a Python package and to define what is available for import when the package is imported. In this case, it imports all the models defined in the app/models directory, making them accessible when the package is imported.
