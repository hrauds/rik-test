from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import traceback

from app.database import get_db
from app import models, schemas

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/persons/", response_model=schemas.Person, status_code=status.HTTP_201_CREATED)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    try:
        person_data = person.dict()
        if hasattr(person_data["type"], "value"):
            person_data["type"] = person_data["type"].value

        db_person = models.Person(**person_data)
        db.add(db_person)
        db.commit()
        db.refresh(db_person)

        return db_person
    except Exception as e:
        logger.error(f"Error creating person: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating person: {str(e)}"
        )


@router.get("/persons/", response_model=List[schemas.Person])
def get_persons(
        type: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)):
    try:
        logger.info(f"Searching persons with type={type}, search={search}")
        query = db.query(models.Person)

        if type:
            try:
                if type in ["individual", "legal"]:
                    query = query.filter(models.Person.type == type)
                else:
                    logger.warning(f"Invalid person type: {type}")
                    return []
            except Exception as e:
                logger.error(f"Error filtering by type: {str(e)}")
                return []

        if search and len(search) >= 2:
            try:
                search_term = f"%{search.lower()}%"

                if type == 'individual':
                    query = query.filter(
                        models.Person.first_name.ilike(search_term) |
                        models.Person.last_name.ilike(search_term) |
                        models.Person.id_code.ilike(search_term)
                    )
                elif type == 'legal':
                    query = query.filter(
                        models.Person.name.ilike(search_term) |
                        models.Person.reg_code.ilike(search_term)
                    )
                else:
                    query = query.filter(
                        models.Person.first_name.ilike(search_term) |
                        models.Person.last_name.ilike(search_term) |
                        models.Person.id_code.ilike(search_term) |
                        models.Person.name.ilike(search_term) |
                        models.Person.reg_code.ilike(search_term)
                    )
            except Exception as e:
                logger.error(f"Error applying search filters: {str(e)}")

        try:
            persons = query.offset(skip).limit(limit).all()
            logger.info(f"Found {len(persons)} persons matching criteria")
            return persons
        except Exception as e:
            logger.error(f"Database error retrieving persons: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    except Exception as e:
        logger.error(f"Unexpected error in get_persons: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/persons/{person_id}", response_model=schemas.PersonWithShareholdings)
def get_person(person_id: int, db: Session = Depends(get_db)):
    try:
        db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
        if db_person is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
        return db_person
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving person {person_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving person: {str(e)}"
        )


@router.put("/persons/{person_id}", response_model=schemas.Person)
def update_person(person_id: int, person: schemas.PersonCreate, db: Session = Depends(get_db)):
    try:
        db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
        if db_person is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

        person_data = person.dict()
        if hasattr(person_data["type"], "value"):
            person_data["type"] = person_data["type"].value

        for key, value in person_data.items():
            setattr(db_person, key, value)

        db.commit()
        db.refresh(db_person)
        return db_person
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating person {person_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating person: {str(e)}"
        )


@router.delete("/persons/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    try:
        db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
        if db_person is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

        db.delete(db_person)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting person {person_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting person: {str(e)}"
        )


@router.post("/companies/", response_model=schemas.Company, status_code=status.HTTP_201_CREATED)
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    try:
        db_company = models.Company(**company.dict())
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return db_company
    except Exception as e:
        logger.error(f"Error creating company: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating company: {str(e)}"
        )


@router.get("/companies/", response_model=List[schemas.Company])
def list_companies(
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        founded_after: Optional[date] = None,
        db: Session = Depends(get_db)
):
    try:
        query = db.query(models.Company)

        if name:
            query = query.filter(models.Company.name.ilike(f"%{name}%"))
        if founded_after:
            query = query.filter(models.Company.founding_date >= founded_after)

        companies = query.offset(skip).limit(limit).all()
        return companies
    except Exception as e:
        logger.error(f"Error retrieving companies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving companies: {str(e)}"
        )


@router.get("/companies/{company_id}", response_model=schemas.CompanyWithShareholders)
def get_company(company_id: int, db: Session = Depends(get_db)):
    try:
        db_company = db.query(models.Company).filter(models.Company.id == company_id).first()
        if db_company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return db_company
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving company {company_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving company: {str(e)}"
        )


@router.put("/companies/{company_id}", response_model=schemas.Company)
def update_company(company_id: int, company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    try:
        db_company = db.query(models.Company).filter(models.Company.id == company_id).first()
        if db_company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        for key, value in company.dict().items():
            setattr(db_company, key, value)

        db.commit()
        db.refresh(db_company)
        return db_company
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating company {company_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating company: {str(e)}"
        )


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    try:
        db_company = db.query(models.Company).filter(models.Company.id == company_id).first()
        if db_company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        db.delete(db_company)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting company {company_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting company: {str(e)}"
        )


@router.post("/shareholdings/", response_model=schemas.Shareholding, status_code=status.HTTP_201_CREATED)
def create_shareholding(shareholding: schemas.ShareholdingCreate, db: Session = Depends(get_db)):
    try:
        company = db.query(models.Company).filter(models.Company.id == shareholding.company_id).first()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        person = db.query(models.Person).filter(models.Person.id == shareholding.person_id).first()
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

        db_shareholding = models.Shareholding(**shareholding.dict())
        db.add(db_shareholding)
        db.commit()
        db.refresh(db_shareholding)
        return db_shareholding
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating shareholding: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating shareholding: {str(e)}"
        )


@router.get("/shareholdings/", response_model=List[schemas.Shareholding])
def list_shareholdings(
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[int] = None,
        person_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    try:
        query = db.query(models.Shareholding)

        if company_id:
            query = query.filter(models.Shareholding.company_id == company_id)
        if person_id:
            query = query.filter(models.Shareholding.person_id == person_id)

        shareholdings = query.offset(skip).limit(limit).all()
        return shareholdings
    except Exception as e:
        logger.error(f"Error retrieving shareholdings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving shareholdings: {str(e)}"
        )


@router.get("/shareholdings/{shareholding_id}", response_model=schemas.ShareholdingWithDetails)
def get_shareholding(shareholding_id: int, db: Session = Depends(get_db)):
    try:
        db_shareholding = db.query(models.Shareholding).filter(models.Shareholding.id == shareholding_id).first()
        if db_shareholding is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shareholding not found")
        return db_shareholding
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving shareholding {shareholding_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving shareholding: {str(e)}"
        )


@router.put("/shareholdings/{shareholding_id}", response_model=schemas.Shareholding)
def update_shareholding(shareholding_id: int, shareholding: schemas.ShareholdingCreate, db: Session = Depends(get_db)):
    try:
        db_shareholding = db.query(models.Shareholding).filter(models.Shareholding.id == shareholding_id).first()
        if db_shareholding is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shareholding not found")

        company = db.query(models.Company).filter(models.Company.id == shareholding.company_id).first()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        person = db.query(models.Person).filter(models.Person.id == shareholding.person_id).first()
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

        for key, value in shareholding.dict().items():
            setattr(db_shareholding, key, value)

        db.commit()
        db.refresh(db_shareholding)
        return db_shareholding
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating shareholding {shareholding_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating shareholding: {str(e)}"
        )


@router.delete("/shareholdings/{shareholding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shareholding(shareholding_id: int, db: Session = Depends(get_db)):
    try:
        db_shareholding = db.query(models.Shareholding).filter(models.Shareholding.id == shareholding_id).first()
        if db_shareholding is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shareholding not found")

        db.delete(db_shareholding)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting shareholding {shareholding_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting shareholding: {str(e)}"
        )
