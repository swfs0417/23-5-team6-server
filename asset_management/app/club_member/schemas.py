from pydantic import BaseModel, Field

class ClubMemberBase(BaseModel):
    user_id: str
    club_id: int
    permission: int

class ClubMemberResponse(ClubMemberBase):
    id: int

class ClubMemberCreate(ClubMemberBase):
    pass

class ClubMemberUpdate(BaseModel):
    id: int
    permission: int