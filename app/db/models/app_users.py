from pydantic import EmailStr
from sqlalchemy import BigInteger, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, declarative_base

Base = declarative_base()

class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[EmailStr] = mapped_column(String(500), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool]= mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return (
            f"<AppUser(id={self.id!r}, name={self.name!r}, "
            f"email={self.email!r}, is_active={self.is_active!r})>"
        )