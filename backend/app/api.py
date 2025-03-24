from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import models, schemas

router = APIRouter()


@router.post("/persons/", response_model=schemas.Person, status_code=status.HTTP_201_CREATED)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    db_person = models.Person(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)

    return db_person


@router.get("/persons/", response_model=List[schemas.Person])
def list_persons(
        skip: int = 0,
        limit: int = 100,
        type: Optional[str] = None,
        db: Session = Depends(get_db)
):
    query = db.query(models.Person)

    if type:
        query = query.filter(models.Person.type == type)

    persons = query.offset(skip).limit(limit).all()
    return persons


@router.get("/persons/{person_id}", response_model=schemas.PersonWithShareholdings)
def get_person(person_id: int, db: Session = Depends(get_db)):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if db_person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    return db_person


@router.put("/persons/{person_id}", response_model=schemas.Person)
def update_person(person_id: int, person: schemas.PersonCreate, db: Session = Depends(get_db)):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if db_person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    for key, value in person.dict().items():
        setattr(db_person, key, value)

    db.commit()
    db.refresh(db_person)
    return db_person


@router.delete("/persons/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if db_person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    db.delete(db_person)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/companies/", response_model=schemas.Company, status_code=status.HTTP_201_CREATED)
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@router.get("/companies/", response_model=List[schemas.Company])
def list_companies(
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        founded_after: Optional[date] = None,
        db: Session = Depends(get_db)
):
    query = db.query(models.Company)

    if name:
        query = query.filter(models.Company.name.ilike(f"%{name}%"))
    if founded_after:
        query = query.filter(models.Company.founding_date >= founded_after)

    companies = query.offset(skip).limit(limit).all()
    return companies


@router.get("/companies/{company_id}", response_model=schemas.CompanyWithShareholders)
def get_company(company_id: int, db: Session = Depends(get_db)):
    db_company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return db_company


@router.put("/companies/{company_id}", response_model=schemas.Company)
def update_company(company_id: int, company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    db_company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    for key, value in company.dict().items():
        setattr(db_company, key, value)

    db.commit()
    db.refresh(db_company)
    return db_company


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    db_company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    db.delete(db_company)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
