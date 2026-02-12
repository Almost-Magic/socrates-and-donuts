"""Ripple Pulse — Seed data.

Creates sample sales targets and wisdom quotes.
Run: cd backend && python -m app.seeds.pulse_seed
"""

import asyncio
from datetime import date

from sqlalchemy import func, select

from app.database import async_session
from app.models.pulse_wisdom import PulseWisdom
from app.models.sales_target import SalesTarget


WISDOM_QUOTES = [
    {
        "quote": "It is not that we have a short time to live, but that we waste a great deal of it.",
        "author": "Seneca",
        "source": "On the Shortness of Life",
    },
    {
        "quote": "The impediment to action advances action. What stands in the way becomes the way.",
        "author": "Marcus Aurelius",
        "source": "Meditations",
    },
    {
        "quote": "First say to yourself what you would be; and then do what you have to do.",
        "author": "Epictetus",
        "source": "Discourses",
    },
    {
        "quote": "Yesterday I was clever, so I wanted to change the world. Today I am wise, so I am changing myself.",
        "author": "Rumi",
        "source": "Collected Poems",
    },
    {
        "quote": "Your living is determined not so much by what life brings to you as by the attitude you bring to life.",
        "author": "Kahlil Gibran",
        "source": "The Prophet",
    },
    {
        "quote": "It is no measure of health to be well adjusted to a profoundly sick society.",
        "author": "Jiddu Krishnamurti",
        "source": "Think on These Things",
    },
    {
        "quote": "The only way to make sense out of change is to plunge into it, move with it, and join the dance.",
        "author": "Alan Watts",
        "source": "The Wisdom of Insecurity",
    },
    {
        "quote": "A leader is best when people barely know he exists. When his work is done, they will say: we did it ourselves.",
        "author": "Lao Tzu",
        "source": "Tao Te Ching",
    },
    {
        "quote": "We suffer more often in imagination than in reality.",
        "author": "Seneca",
        "source": "Letters from a Stoic",
    },
    {
        "quote": "Waste no more time arguing about what a good man should be. Be one.",
        "author": "Marcus Aurelius",
        "source": "Meditations",
    },
]


async def seed():
    """Insert seed data for Pulse."""
    async with async_session() as db:
        # ── Sales Targets ──────────────────────────────────────────────
        existing = (await db.execute(select(SalesTarget))).scalars().all()
        if not existing:
            monthly = SalesTarget(
                period_type="monthly",
                period_label="February 2026",
                period_start=date(2026, 2, 1),
                period_end=date(2026, 2, 28),
                target_value=50000.0,
                currency="AUD",
                notes="First full month target",
            )
            db.add(monthly)

            quarterly = SalesTarget(
                period_type="quarterly",
                period_label="Q1 2026",
                period_start=date(2026, 1, 1),
                period_end=date(2026, 3, 31),
                target_value=150000.0,
                currency="AUD",
                notes="Launch quarter target",
            )
            db.add(quarterly)
            print("Created 2 sales targets (Feb 2026 monthly + Q1 2026 quarterly)")
        else:
            print(f"Skipped targets: {len(existing)} already exist")

        # ── Wisdom Quotes ──────────────────────────────────────────────
        wisdom_count = (await db.execute(
            select(func.count()).select_from(
                select(PulseWisdom.id).subquery()
            )
        )).scalar() or 0

        if wisdom_count == 0:
            for q in WISDOM_QUOTES:
                db.add(PulseWisdom(**q))
            print(f"Created {len(WISDOM_QUOTES)} wisdom quotes")
        else:
            print(f"Skipped wisdom: {wisdom_count} already exist")

        await db.commit()
        print("Pulse seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
