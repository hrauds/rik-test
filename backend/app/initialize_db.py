from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import logging
from datetime import date, datetime
from decimal import Decimal
import random

from app.models import Base, Person, Company, Shareholding, PersonType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/company_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

estonian_first_names = [
    "Andres", "Jaan", "Tiit", "Mart", "Peeter", "Rein", "Tõnu", "Mati", "Aivar", "Toomas",
    "Tiina", "Anne", "Kadri", "Liis", "Kati", "Mari", "Kristi", "Piret", "Liisa", "Riina"
]

estonian_last_names = [
    "Tamm", "Saar", "Sepp", "Kask", "Mägi", "Rebane", "Lepik", "Lepp", "Kukk", "Ilves",
    "Kaasik", "Oja", "Pärn", "Raudsepp", "Kuusk", "Koppel", "Laur", "Lipp", "Põder", "Vaher"
]

estonian_company_prefixes = [
    "Eesti", "Tallinna", "Tartu", "Pärnu", "Põhja", "Lõuna", "Ida", "Lääne", "Baltika", "Meri"
]

estonian_company_mids = [
    "Ehitus", "Puit", "Metall", "Kaubandus", "Transport", "Energia", "Info", "Tootmine", "Teenindus", "Arendus"
]

estonian_company_suffixes = ["OÜ"]


def generate_estonian_id_code():
    gender_century = random.choice([3, 4, 5, 6])

    if gender_century in [3, 4]:
        year = random.randint(40, 99)
    else:
        year = random.randint(0, 23)

    month = random.randint(1, 12)
    day = random.randint(1, 28)
    serial = random.randint(0, 999)

    id_code = f"{gender_century}{year:02d}{month:02d}{day:02d}{serial:03d}"
    return f"{id_code}1"


def generate_estonian_reg_code():
    return str(random.randint(10000000, 99999999))


def generate_company_reg_code():
    return str(random.randint(1000000, 9999999))


def generate_company_name():
    prefix = random.choice(estonian_company_prefixes)
    mid = random.choice(estonian_company_mids)
    suffix = random.choice(estonian_company_suffixes)
    return f"{prefix} {mid} {suffix}"


def initialize_database():
    logger.info("Starting database initialization")
    db = SessionLocal()

    try:
        existing_companies = db.query(Company).count()
        if existing_companies > 0:
            logger.info("Database already contains data. Initialization skipped.")
            return
    except Exception as e:
        logger.error(f"Error checking existing companies: {e}")
        db.close()
        raise

    try:
        individuals = []
        for i in range(20):
            person = Person(
                type=PersonType.individual,
                first_name=random.choice(estonian_first_names),
                last_name=random.choice(estonian_last_names),
                id_code=generate_estonian_id_code(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(person)
            individuals.append(person)

        legal_entities = []
        for i in range(10):
            entity_name = f"{random.choice(estonian_last_names)} Investeeringud"
            person = Person(
                type=PersonType.legal,
                legal_name=entity_name,
                reg_code=generate_estonian_reg_code(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(person)
            legal_entities.append(person)

        db.commit()

        companies = []
        for i in range(15):
            founding_year = random.randint(1990, 2023)
            founding_month = random.randint(1, 12)
            founding_day = random.randint(1, 28)

            capital = Decimal(random.randint(2500, 1000000))

            company = Company(
                name=generate_company_name(),
                reg_code=generate_company_reg_code(),
                founding_date=date(founding_year, founding_month, founding_day),
                capital=capital,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(company)
            companies.append(company)

        db.commit()

        for company in companies:
            num_shareholders = random.randint(2, 4)
            shareholders = random.sample(individuals + legal_entities, num_shareholders)

            if company.capital % num_shareholders != 0:
                adjusted_capital = (company.capital // num_shareholders) * num_shareholders
                company.capital = adjusted_capital
                db.add(company)

            equal_share = company.capital / num_shareholders

            for i, shareholder in enumerate(shareholders):
                is_founder = (i == 0)

                shareholding = Shareholding(
                    company_id=company.id,
                    person_id=shareholder.id,
                    share=equal_share,
                    is_founder=is_founder,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(shareholding)

        db.commit()

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()