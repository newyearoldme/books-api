from fastapi import APIRouter

from src.admins.crud import admin as admin_crud
from src.admins.schemas import AdminUserResponse, UserBanRequest
from src.auth.dependencies import AdminDep
from src.shared.database import DatabaseDep
from src.shared.exceptions import NotFoundException, ValidationException
from src.shared.pagination import PaginationDep

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/users/admins",
    response_model=list[AdminUserResponse],
    summary="Get paginated list of admins",
    responses={
        200: {"description": "List of admins retrieved successfully"},
        400: {"description": "Invalid pagination parameters"},
        403: {"description": "Permission denied"},
        500: {"description": "Internal server error"},
    },
)
async def list_admins(
    db: DatabaseDep, current_admin: AdminDep, pagination: PaginationDep
):
    """
    ## Retrieve a paginated list of all admins in the system

    **Query parameters:**
    - **skip**: Number of records to skip (min 0)
    - **limit**: Number of records to return (1-100), default: 10

    <u>Note: only admins can make this request.</u>
    """
    return await admin_crud.get_admins(db, pagination.skip, pagination.limit)


@router.get(
    "/users/banned",
    response_model=list[AdminUserResponse],
    summary="Get paginated list of banned users",
    responses={
        200: {"description": "List of banned users retrieved successfully"},
        400: {"description": "Invalid pagination parameters"},
        403: {"description": "Permission denied"},
        500: {"description": "Internal server error"},
    },
)
async def list_banned_users(
    db: DatabaseDep, current_admin: AdminDep, pagination: PaginationDep
):
    """
    ## Retrieve a paginated list of all banned users in the system

    **Query parameters:**
    - **skip**: Number of records to skip (min 0)
    - **limit**: Number of records to return (1-100), default: 10

    <u>Note: only admins can make this request.</u>
    """
    return await admin_crud.get_banned_users(db, pagination.skip, pagination.limit)


@router.get(
    "/users/inactive",
    response_model=list[AdminUserResponse],
    summary="Get paginated list of inactive users",
    responses={
        200: {"description": "List of inactive users retrieved successfully"},
        400: {"description": "Invalid pagination parameters"},
        403: {"description": "Permission denied"},
        500: {"description": "Internal server error"},
    },
)
async def list_inactive_users(
    db: DatabaseDep, current_admin: AdminDep, pagination: PaginationDep
):
    """
    ## Retrieve a paginated list of all inactive users in the system

    **Query parameters:**
    - **skip**: Number of records to skip (min 0)
    - **limit**: Number of records to return (1-100), default: 10

    <u>Note: only admins can make this request.</u>
    """
    return await admin_crud.get_inactive_users(db, pagination.skip, pagination.limit)


@router.post(
    "/users/{user_id}/promote",
    response_model=AdminUserResponse,
    summary="Promote user to admin",
    responses={
        200: {"description": "User was successfully promoted to admin"},
        400: {"description": "Invalid pagination parameters"},
        403: {"description": "Permission denied"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def promote_admin(db: DatabaseDep, current_admin: AdminDep, user_id: int):
    """
    ## Grant administrator privileges to a user

    **Permissions:**
    - Only existing administrators can promote users
    - Cannot promote yourself

    <u>Returns: updated user object with administrator privileges.</u>
    """
    if user_id == current_admin.id:
        raise ValidationException("Cannot promote yourself")

    user = await admin_crud.promote_admin(db, user_id)
    if not user:
        raise NotFoundException(
            detail="User not found", resource_type="user", resource_id=user_id
        )
    return user


@router.post(
    "/users/{user_id}/demote",
    response_model=AdminUserResponse,
    summary="Demote admin to regular user",
    responses={
        200: {"description": "Admin was successfully demoted to regular user"},
        400: {"description": "Invalid pagination parameters"},
        403: {"description": "Permission denied"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def demote_admin(db: DatabaseDep, current_admin: AdminDep, user_id: int):
    """
    ## Remove administrator privileges from a user

    **Permissions:**
    - Only administrators can demote other admins
    - Cannot demote yourself
    - At least one administrator must remain in the system

    <u>Returns: updated user object without administrator privileges.</u>
    """
    if user_id == current_admin.id:
        raise ValidationException("Cannot demote yourself")

    user = await admin_crud.demote_admin(db, user_id)
    if not user:
        raise NotFoundException(
            detail="User not found", resource_type="user", resource_id=user_id
        )
    return user


@router.post(
    "/users/{user_id}/ban",
    response_model=AdminUserResponse,
    summary="Ban a user",
    responses={
        200: {"description": "User was successfully banned"},
        400: {"description": "Invalid pagination parameters"},
        403: {"description": "Permission denied"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def ban_user(
    db: DatabaseDep, current_admin: AdminDep, user_id: int, ban_data: UserBanRequest
):
    """
    ## Permanently ban a user from the system

    **Permissions:**
    - Only administrators can ban users
    - Cannot ban yourself
    - Cannot ban other administrators

    **Parameters:**
    - **ban_reason**: Reason for the ban (required)

    **Returns:** Updated user object with ban status
    """
    if user_id == current_admin.id:
        raise ValidationException("Cannot ban yourself")

    target_user = await admin_crud.get(db, user_id)
    if target_user and target_user.is_admin:
        raise ValidationException("Cannot ban other administrators")

    user = await admin_crud.ban_user(db, user_id, ban_data.ban_reason)
    if not user:
        raise NotFoundException(
            detail="User not found", resource_type="user", resource_id=user_id
        )
    return user


@router.post(
    "/users/{user_id}/unban",
    response_model=AdminUserResponse,
    summary="Unban a user",
    responses={
        200: {"description": "User was successfully unbanned"},
        400: {"description": "Invalid pagination parameters"},
        403: {"description": "Permission denied"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def unban_user(db: DatabaseDep, current_admin: AdminDep, user_id: int):
    """
    ## Remove ban from a previously banned user

    **Permissions:**
    - Only administrators can unban users

    **Returns:** Updated user object with ban status removed
    """
    user = await admin_crud.unban_user(db, user_id)
    if not user:
        raise NotFoundException(
            detail="User not found", resource_type="user", resource_id=user_id
        )
    return user


@router.post(
    "/users/{user_id}/deactivate",
    response_model=AdminUserResponse,
    summary="Deactivate user account",
    responses={
        200: {"description": "User was successfully deactivated"},
        400: {"description": "Invalid pagination parameters"},
        403: {"description": "Permission denied"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def deactivate_user(user_id: int, db: DatabaseDep, current_admin: AdminDep):
    """
    ## Deactivate a user account (soft delete)

    **Permissions:**
    - Only administrators can deactivate users
    - Cannot deactivate yourself

    <u>Note: user data is preserved but user cannot login.</u>

    **Returns:** Updated user object with inactive status
    """
    if user_id == current_admin.id:
        raise ValidationException("Cannot deactivate yourself")

    user = await admin_crud.deactivate_user(db, user_id)
    if not user:
        raise NotFoundException(
            detail="User not found", resource_type="user", resource_id=user_id
        )
    return user


@router.post(
    "/users/{user_id}/activate",
    response_model=AdminUserResponse,
    summary="Activate user account",
    responses={
        200: {"description": "User was successfully deactivated"},
        400: {"description": "Invalid pagination parameters"},
        403: {"description": "Permission denied"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def activate_user(user_id: int, db: DatabaseDep, current_admin: AdminDep):
    """
    ## Reactivate a previously deactivated user account

    **Permissions:**
    - Only administrators can activate users

    **Returns:** Updated user object with active status restored
    """
    user = await admin_crud.activate_user(db, user_id)
    if not user:
        raise NotFoundException(
            detail="User not found", resource_type="user", resource_id=user_id
        )
    return user
