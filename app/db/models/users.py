from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Users(Base):
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool]
    
    workouts: Mapped[list["Workout"]] = relationship(back_populates="user", cascade="delete")
