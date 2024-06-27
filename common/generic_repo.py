from sqlalchemy.orm import Session
from functools import lru_cache

class GenericRepository:

    def __init__(self, db:Session, entity:object):
        self.db = db
        self.entity = entity

    def get_all(self):
        return self.db.query(self.entity).all()
    
    def get_by_condition(self, condition):
        return self.db.query(self.entity).filter(condition).all()

    def check_by_condition(self, condition):
        return self.db.query(self.entity).filter(condition).first()

    def add(self, entity):
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)

    def delete_by_condition(self, condition):
        self.db.query(self.entity).filter(condition).delete()
        self.db.commit()
    
    def update_by_condition(self, condition, update_col, update_val):
        self.db.query(self.entity).filter(condition).update({update_col: update_val})
        self.db.commit()


class CreateRepo:
    def __init__(self, entity, ses) -> None:
        self.db: Session = ses
        self.entity = entity

    @lru_cache
    def __call__(self):
        return GenericRepository(self.db, self.entity)