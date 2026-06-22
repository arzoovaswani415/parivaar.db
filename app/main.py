from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes.user import router as user_router
from app.routes.auth import router as auth_router
from app.routes.family_member import router as family_member_router
from app.routes.health_record import router as health_record_router
from app.routes.doctors_visit import router as doctors_visit_router
from app.routes.appointment import router as appointment_router
from app.routes.medications import router as medication_router
from app.routes.prescription import router as prescription_router
from app.routes.insurance import router as insurance_router
from app.routes.vaccination import router as vaccination_router
from app.routes.family import router as family_router
from app.routes.medical_history import router as medical_history_router
from app.routes.reminder import router as reminder_router
from app.routes.notification import router as notification_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (creates new tables on startup)
    await init_db()
    # Start the background reminder scheduler
    from app.service.reminder_scheduler import start_scheduler, stop_scheduler
    await start_scheduler()
    yield
    # Shutdown scheduler
    await stop_scheduler()

app = FastAPI(title="Personal Health Dashboard", lifespan=lifespan)

@app.get("/")
def root():
    return {"status": "API running"}

# 🌐 CORS setup
origins = [
    "http://localhost:4200",     # Standard Angular local development port
    "http://127.0.0.1:4200",     # Alternative local address for Angular
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allows your Angular app access
    allow_credentials=True,           # Required if you send cookies or authorization headers
    allow_methods=["*"],              # Allows all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],              # Allows all headers (like Content-Type and Authorization)
)

# Include Routers
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(family_member_router)
app.include_router(health_record_router)
app.include_router(appointment_router)  
app.include_router(doctors_visit_router)
app.include_router(medication_router)
app.include_router(prescription_router)
app.include_router(insurance_router)
app.include_router(vaccination_router)
app.include_router(family_router)
app.include_router(medical_history_router)
app.include_router(reminder_router)
app.include_router(notification_router)