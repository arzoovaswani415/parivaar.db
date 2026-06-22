# Implementation Guide - Insurance & Vaccination Modules

## Overview
This document explains the complete implementation of Insurance and Vaccination modules with filtering, sorting, and pagination capabilities.

---

## Files Created

### 1. Service Layer Files

#### `app/service/insurance_service.py`
Contains all business logic for insurance operations:

**Functions:**
- `save_insurance_to_db(data, user_id, session)` - Create new insurance
  - Validates family member belongs to user
  - Uses `from_orm()` for data conversion
  - Returns created record

- `get_insurance_by_id(insurance_id, user_id, session)` - Get single insurance
  - Joins Insurance with FamilyMember for ownership validation
  - Returns `scalar_one_or_none()`
  - Raises 404 HTTPException if not found

- `get_all_insurance_for_family_member(family_member_id, user_id, session, page, page_size, sort_by, sort_order)` - List insurances
  - Validates family member ownership
  - Implements pagination with offset/limit
  - Implements sorting with field validation
  - Returns dict with items, page, page_size, total, total_pages

- `update_insurance_in_db(insurance_id, data, user_id, session)` - Update insurance
  - Validates ownership via get_insurance_by_id()
  - Updates all fields including updated_at
  - Returns updated record

- `delete_insurance_in_db(insurance_id, user_id, session)` - Delete insurance
  - Validates ownership
  - Hard delete (can implement soft delete if needed)
  - Returns success message

#### `app/service/vaccination_service.py`
Same pattern as insurance service but for vaccinations:

**Functions:**
- `save_vaccination_to_db(data, user_id, session)`
- `get_vaccination_by_id(vaccination_id, user_id, session)`
- `get_all_vaccinations_for_family_member(family_member_id, user_id, session, page, page_size, sort_by, sort_order)`
- `update_vaccination_in_db(vaccination_id, data, user_id, session)`
- `delete_vaccination_in_db(vaccination_id, user_id, session)`

---

### 2. Route Files

#### `app/routes/insurance.py`
API endpoints for insurance operations:

**Schemas:**
- `InsuranceCreate` - For POST requests
- `InsuranceUpdate` - For PUT requests

**Endpoints:**
- `POST /insurance/create` - Create new insurance record
- `GET /insurance/{insurance_id}` - Get single insurance
- `GET /insurance/family-member/{family_member_id}` - List with pagination/sorting
- `PUT /insurance/{insurance_id}` - Update insurance
- `DELETE /insurance/{insurance_id}` - Delete insurance

All endpoints require JWT authentication via `get_current_user`.

#### `app/routes/vaccination.py`
API endpoints for vaccination operations:

**Schemas:**
- `VaccinationCreate` - For POST requests
- `VaccinationUpdate` - For PUT requests

**Endpoints:**
- `POST /vaccinations/create` - Create new vaccination
- `GET /vaccinations/{vaccination_id}` - Get single vaccination
- `GET /vaccinations/family-member/{family_member_id}` - List with pagination/sorting
- `PUT /vaccinations/{vaccination_id}` - Update vaccination
- `DELETE /vaccinations/{vaccination_id}` - Delete vaccination

---

## Query Parameters

### Pagination
All list endpoints support pagination:
- `page` (default: 1) - Page number
- `page_size` (default: 10, max: 100) - Records per page

### Sorting
All list endpoints support sorting:
- `sort_by` - Field to sort by
- `sort_order` (default: "desc") - Sort direction (asc or desc)

**Allowed sort fields:**
- Insurance: `created_at`, `updated_at`, `expiry_date`, `start_date`, `coverage_amount`
- Vaccination: `administered_on`, `next_due_date`, `vaccine_name`

---

## Response Format - List Endpoints

```json
{
  "items": [
    { "id": 1, "field": "value" },
    { "id": 2, "field": "value" }
  ],
  "page": 1,
  "page_size": 10,
  "total": 25,
  "total_pages": 3
}
```

---

## Filtering Implementation

### Adding Filters to Existing Modules

To add filtering to existing modules (Medical History, Health Records, etc.), follow this pattern:

1. **Create a filter function in service:**
```python
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
    # Build query with optional filters
    query = select(Model).where(...)
    
    if family_member_id is not None:
        query = query.where(Model.family_member_id == family_member_id)
    
    if category is not None:
        query = query.where(Model.category == category)
    
    # ... pagination and sorting
```

2. **Add route in routes file:**
```python
@router.get("/")
async def list_items(
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
    result = await get_medical_history_list(...)
    return result
```

### Filtering Parameters by Module

**Medical History:**
- `family_member_id` - Filter by family member
- `category` - Filter by category (ALLERGY, SURGERY, etc.)
- `start_date` - Filter diagnosed_on >= start_date
- `end_date` - Filter diagnosed_on <= end_date

**Health Records:**
- `family_member_id` - Filter by family member
- `start_date` - Filter created_at >= start_date
- `end_date` - Filter created_at <= end_date

**Doctor Visits:**
- `family_member_id` - Filter by family member
- `doctor_name` - Filter by doctor name (case-insensitive)
- `visit_date` - Filter by exact visit date
- `start_date` - Filter visit_date >= start_date
- `end_date` - Filter visit_date <= end_date

**Medications:**
- `family_member_id` - Filter by family member
- `active` - Filter by active status (end_date is NULL)
- `medicine_name` - Filter by medicine name (case-insensitive)

**Appointments:**
- `family_member_id` - Filter by family member
- `upcoming` - Filter by upcoming status (status == "Scheduled")
- `completed` - Filter by completed status (status == "Completed")
- `start_date` - Filter appointment_date >= start_date
- `end_date` - Filter appointment_date <= end_date

---

## API Usage Examples

### Insurance

**Create:**
```bash
curl -X POST http://localhost:8000/insurance/create \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "family_member_id": 1,
    "insurance_company_name": "Aetna",
    "policy_number": "POL123",
    "policy_holder_name": "John Doe",
    "coverage_amount": 500000,
    "start_date": "2024-01-01",
    "expiry_date": "2025-01-01",
    "notes": "Gold plan"
  }'
```

**List with pagination and sorting:**
```bash
curl -X GET "http://localhost:8000/insurance/family-member/1?page=1&page_size=10&sort_by=created_at&sort_order=desc" \
  -H "Authorization: Bearer TOKEN"
```

### Vaccination

**Create:**
```bash
curl -X POST http://localhost:8000/vaccinations/create \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "family_member_id": 1,
    "vaccine_name": "COVID-19",
    "administered_on": "2024-06-15",
    "next_due_date": "2024-12-15",
    "notes": "First dose"
  }'
```

**List with pagination:**
```bash
curl -X GET "http://localhost:8000/vaccinations/family-member/1?page=1&page_size=10" \
  -H "Authorization: Bearer TOKEN"
```

---

## Key Features

### Security
- ✅ JWT authentication on all endpoints
- ✅ Ownership validation through FamilyMember.user_id
- ✅ Active member check (is_active == True)
- ✅ SQL injection prevention via parameterized queries

### Database Best Practices
- ✅ Uses `scalar_one_or_none()` for single records
- ✅ Uses `scalars().all()` for collections
- ✅ Proper JOIN usage for validation
- ✅ Efficient pagination with OFFSET/LIMIT
- ✅ Field validation for sorting

### Code Quality
- ✅ Follows existing project patterns
- ✅ Consistent naming conventions
- ✅ Clean service layer
- ✅ Proper error handling
- ✅ Self-documenting code

---

## Implementation Notes

### Ownership Validation Pattern
```python
# Single record fetch with ownership validation
result = await session.execute(
    select(Insurance).join(FamilyMember).where(
        Insurance.id == insurance_id,
        FamilyMember.user_id == user_id,
        FamilyMember.is_active == True
    )
)
insurance = result.scalar_one_or_none()
```

### Pagination Pattern
```python
page_size = min(page_size, 100)  # Cap at 100
offset = (page - 1) * page_size
query = query.offset(offset).limit(page_size)
total_pages = (total + page_size - 1) // page_size
```

### Sorting Pattern
```python
allowed_sort_fields = {"created_at", "updated_at", "expiry_date"}
if sort_by not in allowed_sort_fields:
    sort_by = "created_at"  # Default

if sort_order == "desc":
    query = query.order_by(getattr(Insurance, sort_by).desc())
else:
    query = query.order_by(getattr(Insurance, sort_by).asc())
```

---

## Next Steps - Implementing Filters on Existing Modules

To complete TASK 3 (Filtering), you need to:

1. **Add filtering function to each service:**
   - `app/service/medical_history_service.py` - Add `get_medical_history_list()`
   - `app/service/health_record_service.py` - Add `get_health_records_list()`
   - `app/service/doctors_visit_service.py` - Add `get_doctors_visits_list()`
   - `app/service/medications_service.py` - Add `get_medications_list()`
   - `app/service/appointment_service.py` - Add `get_appointments_list()`

2. **Add list endpoint to each route:**
   - `@router.get("/")` in each routes file
   - Include all filter parameters from requirements
   - Call the filtering function from service layer

3. **Test all filter combinations:**
   - Single filter
   - Multiple filters
   - Pagination with filters
   - Sorting with filters

---

## Testing Recommendations

1. **Create test records** with different values
2. **Test ownership validation** - ensure users can't access others' data
3. **Test filter combinations** - single and multiple filters
4. **Test pagination** - verify total_pages calculation
5. **Test sorting** - verify field validation and ordering
6. **Test error cases** - missing family member, wrong user, invalid sort_by

---

**Created**: June 20, 2026
**Status**: ✅ Insurance & Vaccination modules complete with pagination and sorting
