from turtle import st
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User


async def orm_get_users(session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_user(session: AsyncSession, product_id: int):
    query = delete(User).where(User.id == product_id)
    await session.execute(query)
    await session.commit()


async def orm_add_user(session: AsyncSession, data: dict):
    obj = User(
        user_id=data["id"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        subscribe=data["subscribe"],
        phone=data["phone"],
        end=data["end"],
        start=data["start"]
    )
    session.add(obj)
    await session.commit()


async def orm_get_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()


# async def orm_update_user(session: AsyncSession, product_id: int, data):
#     query = update(User).where(User.id == product_id).values(
#         name=data["name"],
#         description=data["description"],
#         price=data["price"],
#         image=data["image"],)
#     await session.execute(query)
#     await session.commit()