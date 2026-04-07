import os
import pytest

from school_database import SchoolDatabase


def test_postgres_init_skipped_without_env():
    if not os.environ.get('DATABASE_URL'):
        pytest.skip('DATABASE_URL not set; skipping Postgres init test')

    db = SchoolDatabase()
    assert getattr(db, 'use_postgres', False) is True
    # If no exceptions were raised during init, we consider this a success
    assert db.verify_data_integrity_on_startup()['status'] in ('valid', 'empty', 'incomplete')
