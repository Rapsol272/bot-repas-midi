from dataclasses import dataclass

@dataclass(frozen=True)
class Meal:
    meal_id: int
    meal_date: str
    title: str
    description: str
    price_cents: int
    status: str
