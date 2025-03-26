from pydantic import BaseModel, Field, validator, constr, model_validator
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
    reg_code: Optional[str] = None

    class Config:
        orm_mode = True

# Create models - used for creating new entities
class PersonCreate(PersonBase):
    @validator('first_name', 'last_name', 'id_code')
    def validate_individual_fields(cls, v, values):
        if 'type' in values and values['type'] == PersonType.INDIVIDUAL:
            if v is None:
                field_name = next(
                    (name for name, value in values.items() if value is v),
                    "this field"
                )
                raise ValueError(f'Individual persons must have {field_name}')
        return v

    @validator('legal_name', 'reg_code')
    def validate_legal_fields(cls, v, values):
        if 'type' in values and values['type'] == PersonType.LEGAL:
            if v is None:
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

    class Config:
        orm_mode = True

class ShareholdingBase(BaseModel):
    company_id: int
    person_id: int
    share: Decimal
    is_founder: bool = False

    class Config:
        orm_mode = True

class CompanyCreate(CompanyBase):
    pass

class ShareholdingCreate(ShareholdingBase):
    pass

# Response models - used for returning data
class Person(PersonBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Shareholding(ShareholdingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ShareholdingWithDetails(Shareholding):
    company: Company
    person: Person

    class Config:
        orm_mode = True

class CompanyShareholder(BaseModel):
    id: int
    type: PersonType
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    id_code: Optional[str] = None
    legal_name: Optional[str] = None
    reg_code: Optional[str] = None
    share: Decimal
    is_founder: Optional[bool] = False

    class Config:
        orm_mode = True

class CompanyWithShareholders(Company):
    shareholders: List[ShareholdingWithDetails] = []

    class Config:
        orm_mode = True

class PersonWithShareholdings(Person):
    shareholdings: List[Shareholding] = []

    class Config:
        orm_mode = True

class CapitalShareholderUpdate(BaseModel):
    id: Optional[int] = None
    type: PersonType
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    id_code: Optional[str] = None
    legal_name: Optional[str] = None
    reg_code: Optional[str] = None
    share: Decimal
    is_founder: bool

    class Config:
        orm_mode = True

class CapitalIncreaseUpdate(BaseModel):
    new_capital: Decimal
    original_capital: Decimal
    shareholders: List[CapitalShareholderUpdate]

    class Config:
        orm_mode = True

class ShareholderRegistration(BaseModel):
    id: Optional[int] = None  # if provided this person already exists
    type: PersonType
    # Fields for individuals:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    id_code: Optional[str] = None
    # Fields for legal entities:
    legal_name: Optional[str] = None
    reg_code: Optional[str] = None
    share: Decimal

    @model_validator(mode="after")
    def check_required_fields(self) -> "ShareholderRegistration":
        if self.id is None:
            if self.type == PersonType.INDIVIDUAL:
                if not self.first_name or not self.last_name or not self.id_code:
                    raise ValueError("For an individual shareholder without an id, first_name, last_name, and id_code are required")
            elif self.type == PersonType.LEGAL:
                if not self.legal_name or not self.reg_code:
                    raise ValueError("For a legal shareholder without an id, legal_name and reg_code are required")
        return self

    class Config:
        orm_mode = True


class CompanyRegistration(BaseModel):
    name: str
    reg_code: constr(min_length=1, max_length=7)
    founding_date: date
    capital: Decimal
    shareholders: List[ShareholderRegistration]

    class Config:
        orm_mode = True
