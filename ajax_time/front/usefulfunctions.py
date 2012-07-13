from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def print_state(obj):
    from sqlalchemy.orm import object_session 
    from sqlalchemy.orm.util import has_identity 
    obj = obj
    if object_session(obj) is None and not has_identity(obj):
        print "transient:" 
    if object_session(obj) is not None and not has_identity(obj):
        print "pending: "
    if object_session(obj) is None and has_identity(obj):
        print "# detached: "
    if object_session(obj) is not None and has_identity(obj):
        print "# persistent: "


    print type(obj)

def make_input_db_session(input_db_name, echo=False):
    s = 'mysql://dba@localhost:3306/%s' % input_db_name
    engine = create_engine(s, echo=echo)
    Session = sessionmaker(bind=engine)
    return Session()
