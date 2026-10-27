from sqlalchemy import BigInteger, Boolean, CheckConstraint
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from tag7.models import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('reader', 'staff)",
            name="ck_users_role"
        ),    
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="reader")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    

class AccessToken(Base):
    __tablename__ = "access_tokens"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[int] = mapped_column(BigInteger) # seconds anstelle eines datums