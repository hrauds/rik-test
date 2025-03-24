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
    name: Optional[str] = None
    reg_code: Optional[str] = None

    @validator('first_name', 'last_name', 'id_code')
    def validate_individual_fields(cls, v, values):
        if 'type' in values and values['type'] == PersonType.INDIVIDUAL:
            if v is None and values.get('type') == PersonType.INDIVIDUAL:
                field_name = next(
                    (name for name, value in values.items() if value is v),
                    "this field"
                )
                raise ValueError(f'Individual persons must have {field_name}')
        return v

    @validator('name', 'reg_code')
    def validate_legal_fields(cls, v, values):
        if 'type' in values and values['type'] == PersonType.LEGAL:
            if v is None and values.get('type') == PersonType.LEGAL:
                field_name = next(
                    (name for name, value in values.items() if value is v),
                    "this field"
                )
                raise ValueError(f'Legal persons must have {field_name}')
        return v


class CompanyBase(BaseModel):
    name: str
    reg_code: constr(min_length=1, max_length=7)
    founding_date: date
    capital: Decimal


class ShareholdingBase(BaseModel):
    company_id: int
    person_id: int
    share: Decimal


# Create models - used for creating new entities
class PersonCreate(PersonBase):
    pass


class CompanyCreate(CompanyBase):
    pass


class ShareholdingCreate(ShareholdingBase):
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


class Shareholding(ShareholdingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ShareholdingWithDetails(Shareholding):
    company: Company
    person: Person

    class Config:
        orm_mode = True


class CompanyWithShareholders(Company):
    shareholders: List["PersonWithShare"] = []

    class Config:
        orm_mode = True


class PersonWithShare(Person):
    share: Optional[Decimal] = None

    class Config:
        orm_mode = True


class PersonWithShareholdings(Person):
    shareholdings: List[Shareholding] = []

    class Config:
        orm_mode = True
