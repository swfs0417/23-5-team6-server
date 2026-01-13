from asset_management.app.club_member.schemas import ClubMemberResponse
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from asset_management.app.club_member.repositories import ClubMemberRepository
from asset_management.database.session import get_session

class ClubMemberService:
    def __init__(self, db_session: Session = Depends(get_session)):
        self.repository = ClubMemberRepository(db_session)

    def get_club_members(self, club_id: int, permission: int) -> List[ClubMemberResponse]:
        members = self.repository.get_club_members(club_id)
        if permission not in [member.permission for member in members]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return [ClubMemberResponse(
            id=member.id,
            user_id=member.user_id,
            club_id=member.club_id,
            permission=member.permission
        ) for member in members]

    def edit_club_member(self, member_id: int, club_id: int, new_permission: int) -> ClubMemberResponse:
        member = self.repository.edit_club_member(member_id, club_id, new_permission)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        return ClubMemberResponse(
            id=member.id,
            user_id=member.user_id,
            club_id=member.club_id,
            permission=member.permission
        )
    
    def delete_club_member(self, member_id: int, club_id: int) -> None:
        success = self.repository.delete_club_member(member_id, club_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")