from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import uuid4, UUID


class Base(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    