from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import BigInteger, TIMESTAMP, String
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

Base = declarative_base()

class ImageUploads(Base):
    __tablename__ = "image_upload"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    file_path: Mapped[str] = mapped_column(String(255))
    upload_timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    meta_data: Mapped[dict] = mapped_column(JSONB)
