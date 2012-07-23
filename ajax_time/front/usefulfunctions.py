from sqlalchemy import not_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from table_mapping import (
        master_record,
        device,
        )


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


def make_expression(filter_dict):
    filter_sel = filter_dict["filter_selector"]
    if filter_sel == "device_type":
        d_t = filter_dict["device_type"]
        if filter_dict.get("device_contains"):
            ret = device.generic_name.contains(d_t)
        else:
            ret = device.generic_name==d_t
    if filter_sel == "date":
        date_to = filter_dict["date_to"]
        date_from = filter_dict["date_from"]
        ret = master_record.date_report.between(date_from, date_to)
    if filter_sel == "manufacturer":
        man_name = filter_dict["manufacturer_name"]
        ret = device.manufacturer_name.contains(man_name)
    if filter_sel == "event_type":
        e_t = filter_dict["event_type"]
        ret = master_record.event_type==e_t

    if filter_dict["not_op"]:
        ret = not_(ret)
    return ret
