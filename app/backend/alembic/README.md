# Alembic Migrations

## Initial Setup

If Alembic is not initialized, run:

```bash
cd app/backend
alembic init alembic
```

Then update `alembic.ini` to set the database URL or use environment variables.

## Running Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base
```

## Total Manager Tables

The migration `001_add_total_manager_tables.py` creates:
- `tm_groups` table
- `tm_collections` table
- `tm_member_status` table
- `tm_event_logs` table
- Required indexes
- PostgreSQL ENUM types

