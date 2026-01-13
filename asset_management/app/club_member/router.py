from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from asset_management.app.club_member.schemas import ClubMemberResponse
from asset_management.app.user.models import UserClublist

router = APIRouter(prefix="/club_members", tags=["club_members"])

@router.get("{club_id}")
def get_club_members(club_id: int, member_id: int | None = None, user_id: str | None = None, permission: int | None = None, page: int = Query(1, ge=1), size: int = Query(10, ge=1)) -> List[ClubMemberResponse]:
    pass
  

@router.post("{club_id}")
def new_club_member(member_id: int, club_id: int):
    pass

@router.delete("{member_id}")
def delete_club_member(member_id: int, club_id: int):
    pass

@router.put("{member_id}")
def update_club_member(member_id: int, permission: int):
    pass