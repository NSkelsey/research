from sqlalchemy import not_, and_, or_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from IPython import embed
from table_mapping import (
        master_record,
        device,
        )
import dbdb


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

open_conns = {}

def make_input_db_session(input_db_name, echo=False):
    if open_conns.get(input_db_name) is None:
        s = 'mysql://dba@localhost:3306/%s' % input_db_name
        engine = create_engine(s, echo=echo)
        Session = sessionmaker(bind=engine)
        open_conns[input_db_name] = Session
    else:
        Session = open_conns[input_db_name]
    return Session()


def make_expression(filter_dict , name):
    if filter_dict["filter_choice"] != "new_form" and filter_dict["filter_choice"] != name:
        s = dbdb.make_dbdb_session()
        f = s.query(dbdb.Filter).filter_by(name=filter_dict["filter_choice"]).scalar()
        s.close()
        return f.expression.unique_params()
    filter_sel = filter_dict["filter_selector"]
    if filter_sel == "device_type":
        d_t = filter_dict["device_type"]
        if filter_dict.get("device_contains"):
            ret = device.generic_name.contains(d_t)
        else:
            ret = device.generic_name==d_t
    if filter_sel == "date_report":
        date_to = filter_dict["date_to"]
        date_from = filter_dict["date_from"]
        ret = master_record.date_report.between(date_from, date_to)
    if filter_sel == "date_event":
        date_to = filter_dict["date_to"]
        date_from = filter_dict["date_from"]
        ret = master_record.date_event.between(date_from, date_to)
    if filter_sel == "manufacturer":
        man_name = filter_dict["manufacturer_name"]
        ret = device.manufacturer_name.contains(man_name)
    if filter_sel == "event_type":
        e_t = filter_dict["event_type"]
        ret = master_record.event_type==e_t
    if filter_dict["not_op"]:
        ret = not_(ret)
    return ret


def make_filter_with_forms(filter_dict_li, filter_args={}):
    num_filters = len(filter_dict_li)
    and_flag = False
    and_buffer = []
    or_buffer = []
    name = filter_args.get("filter_name")
    filt_ops = [i["logical_operation"] for i in filter_dict_li]
    for i in range(num_filters):
        ex = make_expression(filter_dict_li[i], name)
        if filt_ops[i] == "and":
            and_flag = True
            and_buffer.append(ex)
            #solves case of only ands with a last and
            if i == range(num_filters)[-1]:
                ex = and_(*and_buffer)
                or_buffer.append(ex)
        elif filt_ops[i] == "or":
            if and_flag == True:
                and_buffer.append(ex)
                ex = and_(*and_buffer)
                and_buffer = []
                and_flag = False
                or_buffer.append(ex)
            else:
                or_buffer.append(ex)
        else:
            if and_flag == True:
                and_buffer.append(ex)
                ex = and_(*and_buffer)
            or_buffer.append(ex)
    expression = or_(*or_buffer)
    ctr = 0
    ff_li = []
    for i in filter_dict_li:
        f = dbdb.Filter_form(value_dict=i, pos=ctr)
        ff_li.append(f)
        ctr += 1

    filter_to_commit = dbdb.Filter(expression=expression,
            name=filter_args["name"])
    filter_to_commit.forms = ff_li
    if filter_args.get("comment") is not None:
        filter_to_commit.comment = filter_args["comment"]
    return filter_to_commit

