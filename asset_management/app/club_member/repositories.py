from asset_management.database.session import get_session
from typing import Annotated, List
from sqlalchemy.orm import Session
from fastapi import Depends
from asset_management.app.user.models import UserClublist
from sqlalchemy_pagination import paginate

class ClubMemberRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_session)]):
        self.db_session = db_session

    def get_club_members(self, club_id: int, permission: int, page: int, size: int) -> List[UserClublist]:
        query = self.db_session.query(UserClublist).filter(UserClublist.club_id == club_id)
        return paginate(query, page, size)

    def edit_club_member(self, member_id: int, club_id: int, new_permission: int) -> UserClublist | None:
        member = self.db_session.query(UserClublist).filter(
            UserClublist.user_id == member_id,
            UserClublist.club_id == club_id
        ).first()
        if member:
            member.permission = new_permission
            self.db_session.commit()
        return member
    
    def delete_club_member(self, member_id: int, club_id: int) -> bool:
        member = self.db_session.query(UserClublist).filter(
            UserClublist.user_id == member_id,
            UserClublist.club_id == club_id
        ).first()
        if member:
            self.db_session.delete(member)
            self.db_session.commit()
            return True
        return False