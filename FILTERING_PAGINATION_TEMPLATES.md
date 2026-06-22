# Filtering & Pagination Implementation Guide

This document provides templates and examples for adding filtering and pagination to existing modules.

---

## Medical History - Filtering Template

### Service Function Template
```python
# Add to app/service/medical_history_service.py

async def get_medical_history_list(
    user_id: int,
    session: AsyncSession,
    family_member_id: int | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    allowed_sort_fields = {"created_at", "updated_at", "diagnosed_on"}
    if sort_by not in allowed_sort_fields:
        sort_by = "created_at"
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    query = select(MedicalHistory).join(FamilyMember).where(
        FamilyMember.user_id == user_id,
        FamilyMember.is_active == True
    )

    if family_member_id is not None:
        query = query.where(MedicalHistory.family_member_id == family_member_id)

    if category is not None:
        query = query.where(MedicalHistory.category == category)

    if start_date is not None:
        query = query.where(MedicalHistory.diagnosed_on >= start_date)

    if end_date is not None:
        query = query.where(MedicalHistory.diagnosed_on <= end_date)

    total_result = await session.execute(
        select(func.count(MedicalHistory.id)).select_from(MedicalHistory).join(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    total = total_result.scalar()

    if sort_order == "desc":
        query = query.order_by(getattr(MedicalHistory, sort_by).desc())
    else:
        query = query.order_by(getattr(MedicalHistory, sort_by).asc())

    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    query = query.offset(offset).limit(page_size)
    result = await session.execute(query)
    items = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }
```

### Route Endpoint Template
```python
# Add to app/routes/medical_history.py

@router.get("/")
async def list_medical_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    family_member_id: int | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    result = await get_medical_history_list(
        current_user.id,
        session,
        family_member_id,
        category,
        start_date,
        end_date,
        page,
        page_size,
        sort_by,
        sort_order
    )
    return result
```

---

## Health Records - Filtering Template

### Service Function
```python
# Add to app/service/health_record_service.py

async def get_health_records_list(
    user_id: int,
    session: AsyncSession,
    family_member_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    allowed_sort_fields = {"created_at"}
    if sort_by not in allowed_sort_fields:
        sort_by = "created_at"
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    query = select(HealthRecord).join(FamilyMember).where(
        FamilyMember.user_id == user_id,
        FamilyMember.is_active == True
    )

    if family_member_id is not None:
        query = query.where(HealthRecord.family_member_id == family_member_id)

    if start_date is not None:
        query = query.where(HealthRecord.created_at >= start_date)

    if end_date is not None:
        query = query.where(HealthRecord.created_at <= end_date)

    total_result = await session.execute(
        select(func.count(HealthRecord.id)).select_from(HealthRecord).join(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    total = total_result.scalar()

    if sort_order == "desc":
        query = query.order_by(getattr(HealthRecord, sort_by).desc())
    else:
        query = query.order_by(getattr(HealthRecord, sort_by).asc())

    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    query = query.offset(offset).limit(page_size)
    result = await session.execute(query)
    items = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }
```

### Route Endpoint
```python
# Add to app/routes/health_record.py

@router.get("/")
async def list_health_records(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    family_member_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    result = await get_health_records_list(
        current_user.id,
        session,
        family_member_id,
        start_date,
        end_date,
        page,
        page_size,
        sort_by,
        sort_order
    )
    return result
```

---

## Doctor Visits - Filtering Template

### Service Function
```python
# Add to app/service/doctors_visit_service.py

async def get_doctors_visits_list(
    user_id: int,
    session: AsyncSession,
    family_member_id: int | None = None,
    doctor_name: str | None = None,
    visit_date: date | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "visit_date",
    sort_order: str = "desc"
):
    allowed_sort_fields = {"visit_date", "doctor_name", "hospital_name"}
    if sort_by not in allowed_sort_fields:
        sort_by = "visit_date"
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    query = select(DoctorsVisit).join(FamilyMember).where(
        FamilyMember.user_id == user_id,
        FamilyMember.is_active == True
    )

    if family_member_id is not None:
        query = query.where(DoctorsVisit.family_member_id == family_member_id)

    if doctor_name is not None:
        query = query.where(DoctorsVisit.doctor_name.ilike(f"%{doctor_name}%"))

    if visit_date is not None:
        query = query.where(DoctorsVisit.visit_date == visit_date)

    if start_date is not None:
        query = query.where(DoctorsVisit.visit_date >= start_date)

    if end_date is not None:
        query = query.where(DoctorsVisit.visit_date <= end_date)

    total_result = await session.execute(
        select(func.count(DoctorsVisit.id)).select_from(DoctorsVisit).join(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    total = total_result.scalar()

    if sort_order == "desc":
        query = query.order_by(getattr(DoctorsVisit, sort_by).desc())
    else:
        query = query.order_by(getattr(DoctorsVisit, sort_by).asc())

    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    query = query.offset(offset).limit(page_size)
    result = await session.execute(query)
    items = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }
```

### Route Endpoint
```python
# Add to app/routes/doctors_visit.py

@router.get("/")
async def list_doctors_visits(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    family_member_id: int | None = None,
    doctor_name: str | None = None,
    visit_date: date | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "visit_date",
    sort_order: str = "desc"
):
    result = await get_doctors_visits_list(
        current_user.id,
        session,
        family_member_id,
        doctor_name,
        visit_date,
        start_date,
        end_date,
        page,
        page_size,
        sort_by,
        sort_order
    )
    return result
```

---

## Medications - Filtering Template

### Service Function
```python
# Add to app/service/medications_service.py

async def get_medications_list(
    user_id: int,
    session: AsyncSession,
    family_member_id: int | None = None,
    active: bool | None = None,
    medicine_name: str | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "start_date",
    sort_order: str = "desc"
):
    allowed_sort_fields = {"start_date", "end_date", "medicine_name"}
    if sort_by not in allowed_sort_fields:
        sort_by = "start_date"
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    query = select(Medications).join(FamilyMember).where(
        FamilyMember.user_id == user_id,
        FamilyMember.is_active == True
    )

    if family_member_id is not None:
        query = query.where(Medications.family_member_id == family_member_id)

    if medicine_name is not None:
        query = query.where(Medications.medicine_name.ilike(f"%{medicine_name}%"))

    if active is not None:
        if active:
            query = query.where(Medications.end_date.is_(None))
        else:
            query = query.where(Medications.end_date.isnot(None))

    total_result = await session.execute(
        select(func.count(Medications.id)).select_from(Medications).join(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    total = total_result.scalar()

    if sort_order == "desc":
        query = query.order_by(getattr(Medications, sort_by).desc())
    else:
        query = query.order_by(getattr(Medications, sort_by).asc())

    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    query = query.offset(offset).limit(page_size)
    result = await session.execute(query)
    items = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }
```

### Route Endpoint
```python
# Add to app/routes/medications.py

@router.get("/")
async def list_medications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    family_member_id: int | None = None,
    active: bool | None = None,
    medicine_name: str | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "start_date",
    sort_order: str = "desc"
):
    result = await get_medications_list(
        current_user.id,
        session,
        family_member_id,
        active,
        medicine_name,
        page,
        page_size,
        sort_by,
        sort_order
    )
    return result
```

---

## Appointments - Filtering Template

### Service Function
```python
# Add to app/service/appointment_service.py

async def get_appointments_list(
    user_id: int,
    session: AsyncSession,
    family_member_id: int | None = None,
    upcoming: bool | None = None,
    completed: bool | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "appointment_date",
    sort_order: str = "desc"
):
    allowed_sort_fields = {"appointment_date", "doctor_name"}
    if sort_by not in allowed_sort_fields:
        sort_by = "appointment_date"
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    query = select(Appointment).join(FamilyMember).where(
        FamilyMember.user_id == user_id,
        FamilyMember.is_active == True
    )

    if family_member_id is not None:
        query = query.where(Appointment.family_member_id == family_member_id)

    if upcoming is not None and upcoming:
        query = query.where(Appointment.status == "Scheduled")

    if completed is not None and completed:
        query = query.where(Appointment.status == "Completed")

    if start_date is not None:
        query = query.where(Appointment.appointment_date >= start_date)

    if end_date is not None:
        query = query.where(Appointment.appointment_date <= end_date)

    total_result = await session.execute(
        select(func.count(Appointment.id)).select_from(Appointment).join(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    total = total_result.scalar()

    if sort_order == "desc":
        query = query.order_by(getattr(Appointment, sort_by).desc())
    else:
        query = query.order_by(getattr(Appointment, sort_by).asc())

    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    query = query.offset(offset).limit(page_size)
    result = await session.execute(query)
    items = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }
```

### Route Endpoint
```python
# Add to app/routes/appointment.py

@router.get("/")
async def list_appointments(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    family_member_id: int | None = None,
    upcoming: bool | None = None,
    completed: bool | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "appointment_date",
    sort_order: str = "desc"
):
    result = await get_appointments_list(
        current_user.id,
        session,
        family_member_id,
        upcoming,
        completed,
        start_date,
        end_date,
        page,
        page_size,
        sort_by,
        sort_order
    )
    return result
```

---

## Usage Examples

### Medical History with Filters
```bash
GET /medical_history/?family_member_id=1&category=ALLERGY&page=1&page_size=10&sort_by=diagnosed_on&sort_order=desc
```

### Health Records with Date Range
```bash
GET /health_records/?family_member_id=1&start_date=2024-01-01&end_date=2024-06-30&page=1
```

### Doctor Visits with Doctor Search
```bash
GET /doctors-visits/?doctor_name=Smith&start_date=2024-01-01&sort_by=visit_date
```

### Medications - Active Only
```bash
GET /medications/?family_member_id=1&active=true&sort_by=start_date
```

### Appointments - Upcoming
```bash
GET /appointments/?family_member_id=1&upcoming=true&start_date=2024-06-20&sort_by=appointment_date&sort_order=asc
```

---

## Important Notes

1. **Import `func` from sqlmodel:**
   ```python
   from sqlmodel import select, func
   ```

2. **Date Import:**
   ```python
   from datetime import date
   ```

3. **Page Size Limiting:**
   Always cap page_size at 100 to prevent excessive data transfer

4. **Field Validation:**
   Always validate sort_by against allowed_sort_fields to prevent SQL injection

5. **Ownership Validation:**
   Always join with FamilyMember and check user_id and is_active

---

**Created**: June 20, 2026
**Status**: Ready to implement on existing modules
