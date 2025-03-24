from sqlalchemy import Column, String, Integer, Date, Numeric, Boolean, ForeignKey, Enum, func, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
import enum

from app.database import Base


class PersonType(str, enum.Enum):
    INDIVIDUAL = "individual"
    LEGAL = "legal"


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(PersonType), nullable=False)

    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    id_code = Column(String(20), nullable=True, index=True)

    legal_name = Column(String(200), nullable=True)
    legal_code = Column(String(20), nullable=True, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    shareholdings = relationship("Shareholder", back_populates="person", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('id_code', name='uq_person_id_code'),
        UniqueConstraint('legal_code', name='uq_person_legal_code'),
    )

