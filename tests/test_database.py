"""
Тесты утилит базы данных
"""

import pytest
from app.database import get_db


class TestDatabase:
    
    def test_get_db(self):
        db_gen = get_db()
        db = next(db_gen)
        
        assert db is not None
        
        try:
            next(db_gen)
        except StopIteration:
            pass
