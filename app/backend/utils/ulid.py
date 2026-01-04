"""ULID generation utility."""
import ulid


def generate_ulid() -> str:
    """Generate a new ULID string."""
    return str(ulid.new())

