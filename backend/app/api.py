from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session, joinedload

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
                        models.Person.legal_name.ilike(search_term) |
                        models.Person.reg_code.ilike(search_term)
                    )
                else:
                    query = query.filter(
                        models.Person.first_name.ilike(search_term) |
                        models.Person.last_name.ilike(search_term) |
                        models.Person.id_code.ilike(search_term) |
                        models.Person.legal_name.ilike(search_term) |
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


@router.get("/companies/", response_model=List[schemas.CompanyWithShareholders])
def list_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        companies = (
            db.query(models.Company)
            .options(
                joinedload(models.Company.shareholdings).joinedload(models.Shareholding.person)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        response_data = []
        for company in companies:
            company_data = schemas.CompanyWithShareholders(
                id=company.id,
                name=company.name,
                reg_code=company.reg_code,
                founding_date=company.founding_date,
                capital=company.capital,
                created_at=company.created_at,
                updated_at=company.updated_at,
                shareholders=[
                    schemas.ShareholdingWithDetails(
                        id=sh.id,
                        company_id=sh.company_id,
                        person_id=sh.person_id,
                        share=sh.share,
                        created_at=sh.created_at,
                        updated_at=sh.updated_at,

                        company=schemas.Company(
                            id=company.id,
                            name=company.name,
                            reg_code=company.reg_code,
                            founding_date=company.founding_date,
                            capital=company.capital,
                            created_at=company.created_at,
                            updated_at=company.updated_at,
                        ),
                        person=schemas.Person(
                            id=sh.person.id,
                            type=sh.person.type.value if hasattr(sh.person.type, "value") else sh.person.type,
                            first_name=sh.person.first_name,
                            last_name=sh.person.last_name,
                            id_code=sh.person.id_code,
                            legal_name=sh.person.legal_name,
                            reg_code=sh.person.reg_code,
                            created_at=sh.person.created_at,
                            updated_at=sh.person.updated_at,
                        )
                    )
                    for sh in company.shareholdings
                ]
            )
            response_data.append(company_data)
        return response_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving companies: {str(e)}"
        )



@router.get("/companies/{company_id}", response_model=schemas.CompanyWithShareholders)
def get_company(company_id: int, db: Session = Depends(get_db)):
    try:
        db_company = (
            db.query(models.Company)
            .options(joinedload(models.Company.shareholdings).joinedload(models.Shareholding.person))
            .filter(models.Company.id == company_id)
            .first()
        )
        if db_company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        company_data = schemas.CompanyWithShareholders(
            id=db_company.id,
            name=db_company.name,
            reg_code=db_company.reg_code,
            founding_date=db_company.founding_date,
            capital=db_company.capital,
            created_at=db_company.created_at,
            updated_at=db_company.updated_at,
            shareholders=[
                schemas.ShareholdingWithDetails(
                    id=sh.id,
                    company_id=sh.company_id,
                    person_id=sh.person_id,
                    share=sh.share,
                    is_founder=sh.is_founder,
                    created_at=sh.created_at,
                    updated_at=sh.updated_at,
                    company=schemas.Company(
                        id=db_company.id,
                        name=db_company.name,
                        reg_code=db_company.reg_code,
                        founding_date=db_company.founding_date,
                        capital=db_company.capital,
                        created_at=db_company.created_at,
                        updated_at=db_company.updated_at,
                    ),
                    person=schemas.Person(
                        id=sh.person.id,
                        type=sh.person.type.value if hasattr(sh.person.type, "value") else sh.person.type,
                        first_name=sh.person.first_name,
                        last_name=sh.person.last_name,
                        id_code=sh.person.id_code,
                        legal_name=sh.person.legal_name,
                        reg_code=sh.person.reg_code,
                        created_at=sh.person.created_at,
                        updated_at=sh.person.updated_at,
                    )
                )
                for sh in db_company.shareholdings
            ]
        )
        return company_data
    except Exception as e:
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

@router.put("/companies/{company_id}/capital_update", response_model=schemas.CompanyWithShareholders)
def update_company_capital(company_id: int, payload: schemas.CapitalIncreaseUpdate, db: Session = Depends(get_db)):
    try:
        with db.begin():
            company = db.query(models.Company).filter(models.Company.id == company_id).first()
            if not company:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

            total_shares = sum(s.share for s in payload.shareholders)
            if total_shares != payload.new_capital:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sum of shareholder shares does not equal the new capital"
                )

            company.capital = payload.new_capital

            for s in payload.shareholders:
                if s.id:
                    sh = db.query(models.Shareholding).filter(
                        models.Shareholding.id == s.id,
                        models.Shareholding.company_id == company_id
                    ).first()
                    if not sh:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shareholding not found")
                    sh.share = s.share
                    sh.is_founder = s.is_founder
                else:
                    if s.type == schemas.PersonType.INDIVIDUAL:
                        new_person = models.Person(
                            type=s.type.value,
                            first_name=s.first_name,
                            last_name=s.last_name,
                            id_code=s.id_code
                        )
                    else:
                        new_person = models.Person(
                            type=s.type.value,
                            legal_name=s.legal_name,
                            reg_code=s.reg_code
                        )
                    db.add(new_person)
                    db.flush()
                    new_sh = models.Shareholding(
                        company_id=company_id,
                        person_id=new_person.id,
                        share=s.share,
                        is_founder=s.is_founder
                    )
                    db.add(new_sh)
            db.refresh(company)
        return company
    except Exception as e:
        db.rollback()
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating company capital: {str(e)}"
        )

@router.post("/companies/registration", response_model=schemas.CompanyWithShareholders, status_code=status.HTTP_201_CREATED)
def register_company(registration: schemas.CompanyRegistration, db: Session = Depends(get_db)):
    try:
        with db.begin():
            company_data = {
                "name": registration.name,
                "reg_code": registration.reg_code,
                "founding_date": registration.founding_date,
                "capital": registration.capital
            }
            db_company = models.Company(**company_data)
            db.add(db_company)
            db.flush()

            for sh in registration.shareholders:
                if sh.id:
                    # Use the existing person id
                    person_id = sh.id
                else:
                    # Create new person
                    if sh.type == schemas.PersonType.INDIVIDUAL:
                        person_data = {
                            "type": sh.type.value,
                            "first_name": sh.first_name,
                            "last_name": sh.last_name,
                            "id_code": sh.id_code
                        }
                    else:
                        person_data = {
                            "type": sh.type.value,
                            "legal_name": sh.legal_name,
                            "reg_code": sh.reg_code
                        }
                    db_person = models.Person(**person_data)
                    db.add(db_person)
                    db.flush()
                    person_id = db_person.id

                db_shareholding = models.Shareholding(
                    company_id=db_company.id,
                    person_id=person_id,
                    share=sh.share,
                    is_founder=True
                )
                db.add(db_shareholding)
        db.refresh(db_company)
        return db_company
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering company: {str(e)}"
        )
