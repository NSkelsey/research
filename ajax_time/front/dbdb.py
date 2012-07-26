from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
        Column, DateTime, create_engine,
        String, PickleType, Integer, Date, 
        BLOB, ForeignKey, Boolean,
        Enum, Text
        )
from sqlalchemy.dialects.mysql import TEXT, VARCHAR
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.serializer import loads, dumps
from sqlalchemy import orm
Base = declarative_base()

engine = create_engine('mysql://dba@localhost:3306/db_db',echo=False)
Session = sessionmaker(autoflush=True, bind=engine)

from table_mapping import Base as t_m_Base
from table_mapping import master_record
import pickle


db_deny_set = set([
    "information_schema",
    "fda_data",
    "mysql",
    "performance_schema",
    "fda_data",
    "test_bed",
    "nothankyou",
    ])


class Db(Base):
    __tablename__ = 'db_table'

    name = Column(VARCHAR(100), primary_key=True)
    comment = Column(TEXT, nullable=True)
    date_created = Column(DateTime)
    children = relationship("Db",
            secondary="db_relation_table",
            primaryjoin="Db_relation.parent_db_name==Db.name",
            secondaryjoin="Db_relation.child_db_name==Db.name",
            backref="parents"
            )

class Db_relation(Base):
    __tablename__ = "db_relation_table"
    parent_db_name = Column(String(100), ForeignKey("db_table.name"), primary_key=True)
    child_db_name = Column(String(100), ForeignKey("db_table.name"), primary_key=True )
    filter_name = Column(String(30), ForeignKey("filter_table.name"), primary_key=True, autoincrement=True)
    _filter = relationship("Filter", 
            backref=backref("db_relation", cascade="all, delete"),
            )
    parent  = relationship("Db", 
            primaryjoin="Db_relation.parent_db_name==Db.name",
            backref="parent_relations",
            )
    child = relationship("Db",
            primaryjoin="Db_relation.child_db_name==Db.name",
            backref="child_relations",
            )

class Filter(Base):
    __tablename__ = "filter_table"

    name = Column(String(30), primary_key=True)
    comment = Column(Text)
    expr_blob = Column(BLOB)

    def __init__(self, expression=None, name=None):
        if expression is not None:
            self.expression = expression
            blob = dumps(expression)
            self.expr_blob = blob
        self.name = name

    @orm.reconstructor
    def unpickle_pickle(self):
        self.expression = loads(self.expr_blob, t_m_Base.metadata, Session)



class Filter_form(Base):
    __tablename__ = "filter_form_table"

    filter_name = Column(String(30), ForeignKey("filter_table.name"), primary_key=True)
    pos = Column(Integer, primary_key=True, autoincrement=False)
    form_blob = Column(BLOB)
    _filter = relationship("Filter",
            backref=backref("forms",
                    cascade="all, delete", 
                    order_by="Filter_form.pos",),
            )

    def __init__(self, value_dict={}, pos=0):
        self.value_dict = value_dict
        self.pos = pos
        blob = pickle.dumps(value_dict)
        self.form_blob = blob

    @orm.reconstructor
    def unpickle_pickle(self):
        self.value_dict = pickle.loads(self.form_blob)

def verify_db_name(db_name):
    session = Session()
    dbs = session.query(Db).all()
    db_names = [i.name for i in dbs]
    if db_name in db_names:
        return True
    else:
        return False

def make_dbdb_session():
    return Session()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
