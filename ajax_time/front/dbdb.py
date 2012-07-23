from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, create_engine, String, PickleType, Integer, BLOB, ForeignKey
from sqlalchemy.dialects.mysql import TEXT, VARCHAR
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.serializer import loads, dumps
from sqlalchemy import orm
 
Base = declarative_base()

engine = create_engine('mysql://dba@localhost:3306/db_db',echo=True)
Session = sessionmaker(autoflush=True, bind=engine)

from table_mapping import Base as t_m_Base



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
    filter_id = Column(Integer, ForeignKey("vlasic.id"), primary_key=True, autoincrement=True)
    _filter = relationship("Filter", backref="db_relation")
    parent  = relationship("Db", 
            primaryjoin="Db_relation.parent_db_name==Db.name",
            backref="parent_relations",
            )
    child = relationship("Db",
            primaryjoin="Db_relation.child_db_name==Db.name",
            backref="child_relations",
            )

class Filter(Base):
    __tablename__ = "vlasic"

    id = Column(Integer, primary_key = True)
    name = Column(String(30))
    expr_blob = Column(BLOB)

    def __init__(self, expression=None, name=None):
        if expression is not None:
            self.expr = expression
            blob = dumps(expression)
            self.expr_blob = blob
        self.name = name

    @orm.reconstructor
    def unpickle_pickle(self):
        self.expr = loads(self.expr_blob, t_m_Base.metadata, Session)



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
