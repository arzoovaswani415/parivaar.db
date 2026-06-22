from fastapi import HTTPException
from sqlmodel import select
from sqlalchemy import func
from app.models.health_record import HealthRecord
from app.models.family_member import FamilyMember
from app.models.user import User
from sqlmodel.ext.asyncio.session import AsyncSession
from app.dependency import get_current_user
from datetime import date


async def save_health_record_to_db(data: HealthRecord, user_id: int, session: AsyncSession):
    # health_record = HealthRecord(
    #     family_member_id=data.family_member_id,
    #     blood_pressure=data.blood_pressure,
    #     heart_rate=data.heart_rate,
    #     weight=data.weight,
    #     body_temperature=data.body_temperature,
    #     sugar_level=data.sugar_level,
    #     note=data.note
    # )

    # we need to check if the family member belongs to the current user before creating a health record for that family member. otherwise, a user could potentially create health records for family members that do not belong to them if they know the family_member_id. By checking that the family member belongs to the current user, we ensure that users can only create health records for their own family members.

    family_member_id = data.family_member_id
    #  family_member_id is a foreign key referencing the FamilyMember table
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.id == family_member_id,
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    family_member = result.scalar_one_or_none()
    # result.scalar_one_or_none() is used to get a single result from the query. If there is no result, it returns None. If there are multiple results, it raises an exception. In this case, we expect either one family member or none, so scalar_one_or_none() is appropriate.

    if not family_member:
        raise HTTPException(status_code=404, detail="Family member not found")

    new_health_record = HealthRecord.from_orm(data)
    # new_health_record = HealthRecord.from_orm(data) this line creates a new instance of the HealthRecord model using the data from the HealthRecordCreate model.  This allows us to easily convert the data from the request body into a format that can be saved to the database.

    # we can also do new_health_record = HealthRecord(**data.dict()) which does the same thing but we need to make sure that the field names in the HealthRecordCreate model match the field names in the HealthRecord model. The from_orm method is more flexible and allows us to have different field names in the request body and the database model if needed.

    # here HealthRecord and HealthRecordCreate are different models, HealthRecord is the SQLModel model that represents the health_records table in the database, while HealthRecordCreate is a Pydantic model that represents the data we expect to receive in the request body when creating a new health record. The from_orm method allows us to easily convert the data from the HealthRecordCreate model into an instance of the HealthRecord model that can be saved to the database.

    session.add(new_health_record)
    await session.commit()
    await session.refresh(new_health_record)
    return new_health_record


async def get_health_record_db(health_record_id: int, user_id: int, session: AsyncSession):
    result = await session.execute(
        select(HealthRecord).join(FamilyMember).where(
            HealthRecord.id == health_record_id,
            # HealthRecord.family_member_id == FamilyMember.id,

            # we can use the join method to join the HealthRecord table with the FamilyMember table based on the foreign key relationship between them, and then we can filter the results based on the user_id of the family member to ensure that the health record belongs to a family member of the current user.

            #  we seperate the join condition and the where condition. The join method is used to specify how the tables should be joined, while the where method is used to filter the results based on specific conditions.

            #  we dont link user table here because we have family_member_id as foreign key in health record and we can link family member to user through that. If we link user table directly then we would have to link it through family member table anyway, so it's more efficient to just link family member table and then filter based on user_id in the where clause.

            #  every user is a family member so joining with family member is sufficient to get the user information we need to filter the health records based on the user_id.

            #  what if we dont write this join and just do select(HealthRecord).where(HealthRecord.id == health_record_id) ? We would get the health record with the specified id, but we would not be able to verify that the health record belongs to a family member of the current user. This could potentially allow a user to access health records that do not belong to them if they know the id of the health record. By joining with the FamilyMember table and filtering based on user_id, we ensure that users can only access health records that belong to their family members.
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    health_record = result.scalars().all()


    if not health_record:
        raise HTTPException(status_code=404, detail="Health record not found")

    return health_record

async def delete_health_record_db(health_record_id: int, user_id: int, session: AsyncSession):

    health_record = await get_health_record_db(health_record_id, user_id, session)
    await session.delete(health_record)
    await session.commit()  

async def update_health_record_db(health_record_id: int, data: HealthRecord, user_id: int, session: AsyncSession):
    health_record = await get_health_record_db(health_record_id, user_id, session)

    health_record.blood_pressure = data.blood_pressure
    health_record.heart_rate = data.heart_rate
    health_record.weight = data.weight
    health_record.body_temperature = data.body_temperature
    health_record.sugar_level = data.sugar_level
    health_record.note = data.note

    session.add(health_record)
    await session.commit()
    await session.refresh(health_record)
    # we refresh the health_record instance after committing the changes to the database to ensure that we have the most up-to-date data from the database, including any changes that may have been made by triggers or other processes in the database. This is especially important if there are any fields in the HealthRecord model that are automatically updated by the database, such as a last_updated timestamp or an auto-incrementing version number. By refreshing the instance, we can ensure that we have the latest values for all fields in the health record before returning it to the client.
    return health_record    


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
