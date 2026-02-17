def euros_to_cents(euros: float) -> int:
    return int(round(euros * 100))

def cents_to_euros_str(cents: int) -> str:
    euros = cents / 100.0
    return f"{euros:.2f} €"
