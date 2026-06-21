"""
Print a random sample of seeded agents and customers for manual testing.
Run after seed.py to get login credentials for review.
"""
import os

import utils

utils.setup_path()
utils.load_envs()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.sql.expression import func

from src.core.constants import DB_ASYNC_DRIVER, DB_DRIVER
from src.users.constants import UserRole
from src.users.models import User

_AGENT_SAMPLE = 5
_CUSTOMER_SAMPLE = 20
_WIDTH = 72
_THICK = "=" * _WIDTH
_THIN = "-" * _WIDTH


def _print_section(title: str, users: list[User]) -> None:
    print(_THICK)
    print(f"  {title} ({len(users)})")
    print(_THICK)
    for i, user in enumerate(users, start=1):
        name = f"{user.first_name} {user.last_name}"
        print(f"  {i:>2}.  {name:<24}  {user.email}")
    print()


async def main() -> None:
    db_url = (
        f"{DB_DRIVER}+{DB_ASYNC_DRIVER}://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
        f"@localhost:{os.environ.get('POSTGRES_PORT', '5432')}"
        f"/{os.environ['POSTGRES_DB']}"
    )
    engine = create_async_engine(db_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as session:
        agent_result = await session.execute(
            select(User)
            .where(User.role == UserRole.AGENT.value)
            .order_by(func.random())
            .limit(_AGENT_SAMPLE)
        )
        agents = list(agent_result.scalars().all())

        customer_result = await session.execute(
            select(User)
            .where(User.role == UserRole.CUSTOMER.value)
            .order_by(func.random())
            .limit(_CUSTOMER_SAMPLE)
        )
        customers = list(customer_result.scalars().all())

    await engine.dispose()

    _print_section("AGENTS", agents)
    _print_section("CUSTOMERS", customers)

    print(_THIN)
    print("  Password format : {first_name}_{last_name} in lowercase")
    print("  Example         : 'John Smith'  →  'john_smith'")
    print(_THIN)


if __name__ == "__main__":
    utils.run_async(main())
