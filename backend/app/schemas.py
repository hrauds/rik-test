from pydantic import BaseModel, Field, validator, constr
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class PersonType(str, Enum):
    INDIVIDUAL = "individual"
    LEGAL = "legal"


# Base Pydantic models
class PersonBase(BaseModel):
    type: PersonType
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    id_code: Optional[str] = None
    legal_name: Optional[str] = None
    legal_code: Optional[str] = None

    @validator('first_name', 'last_name')
    def validate_individual_fields(cls, v, values):
        if 'type' in values and values['type'] == PersonType.INDIVIDUAL:
            if v is None and ('first_name' not in values or 'last_name' not in values):
                raise ValueError('Individual persons must have first_name and last_name')
        return v

    @validator('legal_name', 'legal_code')
    def validate_legal_fields(cls, v, values):
        if 'type' in values and values['type'] == PersonType.LEGAL:
            if v is None and ('legal_name' not in values or 'legal_code' not in values):
                raise ValueError('Legal persons must have legal_name and legal_code')
        return v


class CompanyBase(BaseModel):
    name: str
    reg_code: constr(min_length=1, max_length=7)
    founding_date: date
    capital: Decimal


class ShareholderBase(BaseModel):
    company_id: int
    person_id: int
    share: Decimal
    is_founder: bool = False


# Create models - used for creating new entities
class PersonCreate(PersonBase):
    pass


class CompanyCreate(CompanyBase):
    pass


class ShareholderCreate(ShareholderBase):
    pass


# Response models - used for returning data
class Person(PersonBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Shareholder(ShareholderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Response models with relationships
class ShareholderWithDetails(Shareholder):
    company: Company
    person: Person

    class Config:
        orm_mode = True


class CompanyWithShareholders(Company):
    shareholders: List[Shareholder] = []

    class Config:
        orm_mode = True


class PersonWithShareholdings(Person):
    shareholdings: List[Shareholder] = []

    class Config:
        orm_mode = True
