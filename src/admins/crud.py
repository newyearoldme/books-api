from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.admins.schemas import UserAdminUpdate
from src.shared.crud_base import CRUDBase
from src.users.models import UserModel
from src.users.schemas import UserCreate, UserUpdate


class CRUDAdmin(CRUDBase[UserModel, UserCreate, UserUpdate]):
    async def get_admins(
        self, db: AsyncSession, skip: int, limit: int
    ) -> list[UserModel]:
        result = await db.scalars(
            select(self.model)
            .where(self.model.is_admin, self.model.is_active)
            .offset(skip)
            .limit(limit)
        )
        return result.all()

    async def get_banned_users(
        self, db: AsyncSession, skip: int, limit: int
    ) -> list[UserModel]:
        result = await db.scalars(
            select(self.model)
            .where(self.model.is_banned)
            .offset(skip)
            .limit(limit)
        )
        return result.all()

    async def get_inactive_users(
        self, db: AsyncSession, skip: int, limit: int
    ) -> list[UserModel]:
        result = await db.scalars(
            select(self.model)
            .where(not self.model.is_active)
            .offset(skip)
            .limit(limit)
        )
        return result.all()

    async def _update_admin_status(
        self, db: AsyncSession, user_id: int, is_admin: bool
    ) -> UserModel | None:
        await db.execute(
            update(self.model).where(self.model.id == user_id).values(is_admin=is_admin)
        )
        await db.commit()
        return await self.get(db, user_id)

    async def promote_admin(self, db: AsyncSession, user_id: int) -> UserModel | None:
        return await self._update_admin_status(db, user_id, True)

    async def demote_admin(self, db: AsyncSession, user_id: int) -> UserModel | None:
        return await self._update_admin_status(db, user_id, False)

    async def ban_user(
        self, db: AsyncSession, user_id: int, ban_reason: str | None = None
    ) -> UserModel | None:
        await db.execute(
            update(self.model)
            .where(self.model.id == user_id)
            .values(
                is_banned=True,
                banned_at=datetime.now(timezone.utc),
                ban_reason=ban_reason,
            )
        )
        await db.commit()
        return await self.get(db, user_id)

    async def unban_user(self, db: AsyncSession, user_id: int) -> UserModel | None:
        await db.execute(
            update(self.model)
            .where(self.model.id == user_id)
            .values(is_banned=False, banned_at=None, ban_reason=None)
        )
        await db.commit()
        return await self.get(db, user_id)

    async def deactivate_user(self, db: AsyncSession, user_id: int) -> UserModel | None:
        await db.execute(
            update(self.model).where(self.model.id == user_id).values(is_active=False)
        )
        await db.commit()
        return await self.get(db, user_id)

    async def activate_user(self, db: AsyncSession, user_id: int) -> UserModel | None:
        await db.execute(
            update(self.model).where(self.model.id == user_id).values(is_active=True)
        )
        await db.commit()
        return await self.get(db, user_id)

    async def update_user_admin(
        self, db: AsyncSession, user_id: int, admin_update: UserAdminUpdate
    ) -> UserModel | None:
        update_data = admin_update.model_dump(exclude_unset=True)

        if "password" in update_data:
            from src.auth.utils import get_password_hash

            update_data["password_hash"] = get_password_hash(
                update_data.pop("password")
            )

        if update_data:
            await db.execute(
                update(self.model).where(self.model.id == user_id).values(**update_data)
            )
            await db.commit()

        return await self.get(db, user_id)


admin = CRUDAdmin(UserModel)
