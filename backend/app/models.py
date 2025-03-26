from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum, Numeric, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

Base = declarative_base()


class PersonType(enum.Enum):
    individual = "individual"
    legal = "legal"


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(PersonType), nullable=False)

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    id_code = Column(String, nullable=True, index=True)

    legal_name = Column(String, nullable=True)
    reg_code = Column(String, nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    shareholdings = relationship("Shareholding", back_populates="person")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    reg_code = Column(String(7), nullable=False, index=True, unique=True)
    founding_date = Column(Date, nullable=False)
    capital = Column(Numeric(precision=10, scale=2), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    shareholdings = relationship("Shareholding", back_populates="company")


class Shareholding(Base):
    __tablename__ = "shareholdings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    person_id = Column(Integer, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False)
    share = Column(Numeric(precision=10, scale=2), nullable=False)
    is_founder = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="shareholdings")
    person = relationship("Person", back_populates="shareholdings")