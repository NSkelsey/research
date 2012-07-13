from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.core.context_processors import request as r
import sqlalchemy
from table_mapping import (
        FOI_text,
        Base,
        device_problem,
        device,
        master_record,
        problem_code,
        patient,
        )
from forms import (
        SimpleForm,
        GenDev_FailType,
        OutForm,
        RawForm,
        SelectForm,
        )
from sqlalchemy.sql import select, bindparam, and_
from sqlalchemy import func, create_engine

from usefulfunctions import make_input_db_session
from dbdb import verify_db_name, make_dbdb_session, Db
from datetime import datetime
from IPython import embed


db_deny_set = set([
    "information_schema",
    "fda_data",
    "mysql",
    "performance_schema",
    "fda_data",
    "test_bed",
    ])

def raw_req(request):
    if request.method == "POST":
        form = RawForm(request.POST)
        db = form.data["db_to_select_from"]
        session = make_input_db_session(db)
        statement = form.data["select_body"]
        ret = session.execute(statement).fetchall()
        return render_to_response("raw_req_form.html", 
                {"form":form, "ret" : ret},
                context_instance=RequestContext(request))
        
    else:
        form = RawForm()
        return render_to_response("raw_req_form.html", 
                {"form":form},
                context_instance=RequestContext(request))


# returns a query object made to order by the vals in the form
def simple_query(form, session, sub=False):
    f = form.cleaned_data
    n = f['number']
    o = Base.metadata.tables[f['obj']] #name of table queried
    if f['id'] is not None:
        the_q = session.query(o).filter_by(MDR_report_key=f['id'])
    else:
        the_q = session.query(o).limit(n)
    if not sub:
        return the_q
    else:
        return the_q.subquery()

def make_select_cols(type_name, fields_list):
    ret_li = []
    type_ = globals()[type_name]
    t_t = type_.__table__
    if len(fields_list) == 1:
        if fields_list[0] == "all":
            return [t_t]
        return [t_t.c.get(fields_list[0])]
    else:
        for col in fields_list:
            if col == "all" or col == "none":
                pass
            else:
                ret_li.append(t_t.c.get(col))
    return ret_li

def out_form(request):
    if request.method== "POST":
        form = OutForm(request.POST)
        s = make_dbdb_session()
        ret_prox = s.query(Db).all()
        dbs = [(i.name, i.name) for i in ret_prox]
        s.close()
        form.fields['input_db'].choices = dbs
        form.full_clean()
        ff = form.fields["input_db"]
        ff.validate(form.data["input_db"])



        input_db_name = form.cleaned_data["input_db"]
        if not verify_db_name(input_db_name):
            return HttpResponse("need a real dbname")
        session = make_input_db_session(input_db_name, echo=True)

        from sqlalchemy.orm import subqueryload, joinedload
        from sqlalchemy.orm.session import make_transient
        embed()
        """
        #the_q = session.query(device).from_statement(sel).options(joinedload(device.master_records))
        the_q = session.query(device).\
                filter_by(generic_name=form.cleaned_data["device_type"]).\
                outerjoin(device_problem, device.problems).limit(100).\
                options(joinedload(device.problems), joinedload(device.problems.problem_code))
        import time
        start = time.time()
        base_q = session.query(device).filter_by(generic_name="infusion pump").\
                limit(1000).\
                options(joinedload(device.problems), joinedload(device.master_record))

        ret_o = base_q.all()
        """
        li_to_commit = ret_o
        for i in ret_o:

            def span_left_from_dev(j):
                if j.text_records:
                    [make_transient(i) for i in j.text_records]
                if j.patients:
                    [make_transient(i) for i in j.patients]
                make_transient(j)

            def span_right_from_dev(j):
                if j.problem_code: make_transient(j.problem_code)
                make_transient(j)

            [span_right_from_dev(j) for j in i.problems]
            span_left_from_dev(i.master_record)
            make_transient(i)
        session.close()
        db_name = form.cleaned_data["output_db"]
        engine1 = create_engine("mysql://root@localhost:3306/mysql")
        if db_name in db_deny_set:
            return HttpResponse("You can't play with that db")

        if " " in db_name:
            return HttpResponse("no spaces here")

        dbdb_session = make_dbdb_session()
        ret_prox = dbdb_session.query(Db).all()
        dbli = [i.name for i in ret_prox]
        if db_name in dbli:
            #engine1.execute("drop database " + db_name)
            i = dbli.index(db_name)
            db_entry = ret_prox[i]
            db_entry.date_created = datetime.now()
            dbdb_session.add(db_entry)
        else:
            db_entry = Db(name=db_name, date_created=datetime.now())
            dbdb_session.add(db_entry)

        #engine1.execute("create database " + db_name)
        dbdb_session.commit()

        engine1b = create_engine('mysql://root@localhost:3306/' + db_name)
        Base.metadata.create_all(bind=engine1b)

        engine2 = create_engine('mysql://root@localhost:3306/' + db_name, echo=True)
        nDBSesh = sqlalchemy.orm.sessionmaker(bind=engine2)()

        from sqlalchemy.ext.compiler import compiles
        from sqlalchemy.sql.expression import Insert
        @compiles(Insert)
        def add_string(insert, compiler, **kw):
            s = compiler.visit_insert(insert, **kw)
            MDR_tables = [
                    "master_table",
                    "text_table",
                    "patient_table",
                    "device_problem_table",
                    "device_table",
                    ]
            rems = ""
            if insert.table.name == "problem_code_table":
                rems = "device_problem_code = device_problem_code"
            elif insert.table.name in MDR_tables:
                rems = "MDR_report_key = MDR_report_key"
            return s + " ON DUPLICATE KEY UPDATE " + rems

        nDBSesh.add_all(li_to_commit)
        nDBSesh.commit()

        @compiles(Insert)
        def add_string(insert, compiler, **kw):
            s = compiler.visit_insert(insert, **kw)
            return s



        stop = time.time()
        dif = stop - start
        return HttpResponse("inserted this many records into new db: " + str(len(ret_o)) + "<br>"  + str(dif)+ "<br>")

    else:
        return HttpResponse("You gotta post")



def simple_form(request):
    form = OutForm()
    if request.method == "POST":
        return HttpResponse(o)


    s = make_dbdb_session()
    ret_prox = s.query(Db).all()
    dbs = [(i.name, i.name) for i in ret_prox]
    form.fields['input_db'].choices = dbs
    return render_to_response('simple_f.html',
            {'outform': form,},
            context_instance=RequestContext(request))



def home(request):
    form = SimpleForm()
    gdft_form = SimpleForm()
    return render_to_response('index.html', {'form' : form, 'gdft' : gdft_form },  context_instance=RequestContext(request))

def xhr(request):
    if request.method == 'POST':
        form = SimpleForm(request.POST)
        if form.is_valid():
            session = DBSession()
            query = simple_query(form, session)
            o = query.all()
            return HttpResponse(o)
    return HttpResponse("Error in form")

def gdft_query(form, session):
    pass



def gdft_xhr(request):
    if request.method == 'POST':
        form = GenDev_FailType(request.POST)
        if form.is_valid():
            conn = engine.connect()


            d = select([device.brand_name, func.count(device.MDR_report_key),
                problem_code.problem_description, master_record.manufacturer_name],
                and_(
                    device.MDR_report_key==master_record.MDR_report_key,
                    master_record.event_type==bindparam("event_type"),
                    device_problem.MDR_report_key==master_record.MDR_report_key,
                    device_problem.problem_code_key==problem_code.device_problem_code,
                    device.generic_name.contains(bindparam("generic_name")),
                    master_record.date_recieved > bindparam("date_after"),
                    )).group_by(device_problem.problem_code_key)

            res = conn.execute(d, generic_name=form.cleaned_data["gendev"], event_type=form.cleaned_data["failtype"],
                    date_after=form.cleaned_data["date_after"])
            li = res.fetchall()
            li = sorted(li, key=lambda x: x[1], reverse=True)
            s= ""
            for i in li:
                s = s + str(i) + "<br>"
            return HttpResponse(s)

    return HttpResponse("Error in form")



def hit_js(request):
    return render_to_response("jsfun.html")



def select_builder(request):
    if request.method == "POST":
        type_name = form.cleaned_data["type_selector"]

        fields_list = form.data.getlist(type_name + "_field_selector")
        col_li = make_select_cols(type_name, fields_list)
        #ret_o = engine.execute(select(col_li,).limit(5))

        filter_selector = form.cleaned_data["filter_selector"]
        where_clause = ""
        if filter_selector == "device_type":
            where_clause = device.generic_name==form.cleaned_data["device_type"]


        sel = select([device.__table__], where_clause).limit(10)

        return HttpResponse("Not implmented go away")
    
    else:
        form = SelectForm()
        return render_to_response("select_form.html",
                {'form': form},
                context_instance=RequestContext(request))
