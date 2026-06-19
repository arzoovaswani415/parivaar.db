from fastapi import FastAPI
from app.database import init_db
from app.routes.user import router as user_router
from app.models.password_reset_token import Password_Reset_Token
from app.routes.auth import router as auth_router
from app.routes.family_member import router as family_member_router
from app.routes.health_record import router as health_record_router
from app.routes.doctors_visit import router as doctors_visit_router
from app.routes.appointment import router as appointment_router
from app.routes.medications import router as medication_router
from app.routes.prescription import router as prescription_router
from app.dependency import oauth2_scheme, get_current_user
from fastapi import Depends

app = FastAPI(title="Personal Health Dashboard")

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
def root():
    return {"status": "API running"}

# Include the user router
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(family_member_router)
app.include_router(health_record_router)
app.include_router(appointment_router)  
app.include_router(doctors_visit_router)
app.include_router(medication_router)
app.include_router(prescription_router)

#username/email : arzoovaswani@gmail.com
#pasword : 123456789

# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4IiwiZXhwIjoxNzgxNjQ4NTQ0fQ.zxR44Ojlb_4FhqbVa9Q8y6GNzKvSu-iKVdd7VPC8POo",
#   "refresh_token": "twRnfSXo4Dx66KyG0Ch50AoYuRZ-5dSd63dU9lgeMrZuclXRbgzbefHA2NGrVEcvzLGKRMcs9_b3IggU5I3pdQ",
#   "token_type": "bearer"
# }