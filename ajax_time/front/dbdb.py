from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, create_engine
from sqlalchemy.dialects.mysql import TEXT, VARCHAR
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine('mysql://dba@localhost:3306/db_db',echo=False)
Session = sessionmaker(autoflush=True, bind=engine)

class Db(Base):
    __tablename__ = 'db_table'

    name = Column(VARCHAR(100), primary_key=True)
    comment = Column(TEXT, nullable=True)
    date_created = Column(DateTime)


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
