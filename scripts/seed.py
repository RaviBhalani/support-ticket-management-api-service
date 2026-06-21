"""
Seed the database with 100 agents and 10 000 customers.

Not idempotent — running twice will violate the email unique constraint.
Truncate the users table before re-seeding:
    docker compose exec postgres psql -U <user> -d <db> -c "TRUNCATE users RESTART IDENTITY CASCADE;"
"""
import os

import utils

utils.setup_path()
utils.load_envs()

import bcrypt
from faker import Faker
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.constants import DB_ASYNC_DRIVER, DB_DRIVER
from src.users.constants import UserRole
from src.users.models import User

_AGENT_COUNT = 100
_CUSTOMER_COUNT = 10_000
_BCRYPT_ROUNDS = 4  # Low work factor for seed data only — default of 12 would take ~50 min for 10 100 records


def _build_user(fake: Faker, index: int, role: UserRole) -> User:
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{first_name.lower()}.{last_name.lower()}.{index}@example.com"
    password = f"{first_name.lower()}_{last_name.lower()}"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)).decode()
    return User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        hashed_password=hashed,
        role=role,
    )


async def main() -> None:
    Faker.seed(0)  # Fixed seed — reproducible data across runs
    fake = Faker()

    print(f"Generating {_AGENT_COUNT} agents...")
    agents = [_build_user(fake, i, UserRole.AGENT) for i in range(_AGENT_COUNT)]

    print(f"Generating {_CUSTOMER_COUNT} customers...")
    customers = [_build_user(fake, i, UserRole.CUSTOMER) for i in range(_CUSTOMER_COUNT)]

    db_url = (
        f"{DB_DRIVER}+{DB_ASYNC_DRIVER}://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
        f"@localhost:{os.environ.get('POSTGRES_PORT', '5432')}"
        f"/{os.environ['POSTGRES_DB']}"
    )
    engine = create_async_engine(db_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    print("Inserting into database...")
    async with factory() as session:
        session.add_all(agents + customers)
        await session.commit()

    await engine.dispose()
    print(f"Done — seeded {len(agents)} agents and {len(customers)} customers.")


if __name__ == "__main__":
    utils.run_async(main())
