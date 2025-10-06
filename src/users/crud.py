from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.utils import get_password_hash, verify_password
from src.shared.crud_base import CRUDBase
from src.users.models import UserModel
from src.users.schemas import UserCreate, UserUpdate


class CRUDUser(CRUDBase[UserModel, UserCreate, UserUpdate]):
    async def create(self, db: AsyncSession, obj_in: UserCreate) -> UserModel:
        hashed_password = get_password_hash(obj_in.password)
        db_obj = UserModel(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=hashed_password,
            is_active=True,
            is_admin=False,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_user(
        self, db: AsyncSession, id: int, obj_in: UserUpdate | dict
    ) -> UserModel | None:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(
                update_data.pop("password")
            )

        if update_data:
            await db.execute(
                update(UserModel).where(UserModel.id == id).values(**update_data)
            )
            await db.commit()

        return await self.get(db, id)

    async def get_by_username(
        self, db: AsyncSession, username: str
    ) -> UserModel | None:
        result = await db.execute(
            select(self.model).where(
                self.model.username == username, self.model.is_active
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> UserModel | None:
        result = await db.execute(
            select(self.model).where(
                self.model.email == email, self.model.is_active
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession, skip: int, limit: int) -> list[UserModel]:
        result = await db.scalars(
            select(self.model)
            .where(self.model.is_active)
            .offset(skip)
            .limit(limit)
        )
        return result.all()

    async def authenticate(
        self, db: AsyncSession, username: str, password: str
    ) -> UserModel | None:
        user = await self.get_by_username(db, username)
        if not user or not verify_password(password, user.password_hash):
            return None

        if not user.is_active or user.is_banned:
            return None

        return user


user = CRUDUser(UserModel)
