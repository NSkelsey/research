import time
from datetime import datetime
from datetime import date

import matplotlib.pyplot as plt
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.template.defaultfilters import escape
from django.forms.formsets import formset_factory
from sqlalchemy.orm import subqueryload, joinedload, sessionmaker
from sqlalchemy.orm.session import make_transient
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Insert
from sqlalchemy import (
        and_,
        or_,
        not_,
        func,
        create_engine,
        )
from sqlalchemy.sql import select, bindparam
from IPython import embed

from dbdb import (
        verify_db_name,
        make_dbdb_session,
        Db,
        Db_relation,
        db_deny_set,
        Filter,
        Filter_form,
        )
from forms import (
        SimpleForm,
        GenDev_FailType,
        OutForm,
        RawForm,
        SelectForm,
        DBForm,
        FilterForm
        )
from table_mapping import (
        FOI_text,
        Base,
        device_problem,
        device,
        master_record,
        problem_code,
        patient,
        )
from usefulfunctions import make_input_db_session, make_filter_with_forms

ECHO = True


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
        OutFormSet = formset_factory(OutForm)
        outformset = OutFormSet(request.POST)
        if not outformset.is_valid():
            HttpResponse("formset is not valid")
        db_form = DBForm(request.POST)
        s = make_dbdb_session()
        ret_prox = s.query(Db).all()
        dbs = [(i.name, i.name) for i in ret_prox]
        s.close()
        del ret_prox
        db_form.fields['input_db'].choices = dbs
        db_form.full_clean()
        input_db_name = db_form.cleaned_data["input_db"]
        if not verify_db_name(input_db_name):
            return HttpResponse("need a real dbname")
        session = make_input_db_session(input_db_name, echo=ECHO)

        start = time.time()
        base_q = session.query(device).join("master_record")

        filter_dict_li = [i.cleaned_data for i in outformset.forms]

        filter_to_commit = make_filter_with_forms(filter_dict_li,
                {"name":db_form.cleaned_data["filter_name"]})

        base_q = base_q.filter(filter_to_commit.expression)
        base_q = base_q.\
                        options(joinedload(device.problems), joinedload(device.master_record))
        ret_o = base_q.all()

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
        db_name = db_form.cleaned_data["output_db"]
        engine1 = create_engine("mysql://root@localhost:3306/mysql")
        if db_name in db_deny_set:
            return HttpResponse("You can't play with that db")

        if " " in db_name:
            return HttpResponse("no spaces here")

        dbdb_session = make_dbdb_session()
        ret_prox = dbdb_session.query(Db).all()
        dbli = [i.name for i in ret_prox]
        if db_name in dbli:
            if db_form.cleaned_data["drop_output_selector"]:
                engine1.execute("drop database " + db_name)
                engine1.execute("create database " + db_name)

            i = dbli.index(db_name)
            db_entry = ret_prox[i]
            db_entry.date_created = datetime.now()
            relation = Db_relation(child_db_name=db_name,parent_db_name=input_db_name)
        else:
            db_entry = Db(name=db_name, date_created=datetime.now())
            relation = Db_relation(parent_db_name=input_db_name, child_db_name=db_name)
            engine1.execute("create database " + db_name)
        dbdb_session.add(filter_to_commit)
        dbdb_session.commit()
        relation._filter = filter_to_commit
        db_entry.child_relations.append(relation)
        dbdb_session.add(db_entry)
        dbdb_session.commit()
        dbdb_session.close()
        del engine1

        engine1b = create_engine('mysql://root@localhost:3306/' + db_name)
        Base.metadata.create_all(bind=engine1b)
        del engine1b

        engine2 = create_engine('mysql://root@localhost:3306/' + db_name, echo=ECHO)
        nDBSesh = sessionmaker(bind=engine2)()
        #adds on duplicate key... to the mass inserts for the newly created db
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
        nDBSesh.execute("CREATE INDEX date_index ON master_table (date_report)")
        nDBSesh.execute("CREATE INDEX mdr_key_index ON text_table (MDR_report_key)")
        nDBSesh.close()
        del engine2
        #redefining add_string prevents insert dying on other things
        @compiles(Insert)
        def add_string(insert, compiler, **kw):
            s = compiler.visit_insert(insert, **kw)
            return s

        stop = time.time()
        dif = stop - start
        return HttpResponse("inserted this many records into new db: " + str(len(ret_o)) + "<br>"  + str(dif)+ "<br><br>" +
                "====The expression made looked like this==== <br>" + str(filter_to_commit.expression) + "")

    else:
        return HttpResponse("You gotta post")


def simple_form(request):
    OFset = formset_factory(OutForm,)
    ofset = OFset()
    form = OutForm()
    db_form  = DBForm()
    if request.method == "POST":
        return HttpResponse(o)


    s = make_dbdb_session()
    ret_prox = s.query(Db).all()
    dbs = [(i.name, i.name) for i in ret_prox]
    db_form.fields['input_db'].choices = dbs
    s.close()
    return render_to_response('simple_f.html',
            {'formset': ofset, "db_form" : db_form},
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


def present_dbs(request):
    session = make_dbdb_session()

    topdb =  session.query(Db).filter_by(name="orm_fun").first()

    def display_filters(topdb):
        ret = escape(topdb.name) + "<ul>"
        if topdb.parent_relations:
            ret += "<div class=subf>Filters:"
        for i in topdb.parent_relations:
            ret += "<li class=filter >" + escape(i._filter.name)
            ret += "<a href=/filter/" + escape(i._filter.name) + ">link</a>"
            ret += "<div style=\"margin-left: 10px; display: inline;\">" + "    " + escape(i.child_db_name) + "</div>"
            ret += "</li>"
        ret += "</div>"
        return ret + "</ul>"

    def recurse_dbs(topdb, li):
        child_db_li = topdb.children
        li.append(display_filters(topdb))
        topdb.__setattr__("visited", True)
        subli = []
        for i in child_db_li:
            try:
                i.__getattribute__("visited")
                return "bottom"
            except (AttributeError):
                recurse_dbs(i, subli)
        if subli != []:
            li.append(subli)
        return li

    li = []
    db_tree = recurse_dbs(topdb, li)
    alldbs = session.query(Db).filter(Db.name != "orm_fun").all()
    for db in alldbs:
        if len(db.parents) == 0:
            li = []
            li = recurse_dbs(db, li)
            if len(li) < 2:
                db_tree.append(*li)
            else: 
                db_tree.append(li[0])
                db_tree.append(li[1])

    f_li = session.query(Filter).outerjoin("db_relation").filter(Db_relation.filter_name == None).all()
    filters = f_li
    session.close()
    return render_to_response("db_structure.html",
            {"db_tree" : db_tree, "filters" : filters},
            context_instance=RequestContext(request),
            )


def show_filter(request, filter_name=None):
    if request.method == "GET":
        s = make_dbdb_session()
        fil_to_show = s.query(Filter).filter_by(name=filter_name).scalar()
        _dict = {}
        if fil_to_show is None:
            fil_to_show = Filter(name=filter_name)
            _dict["msg"] = "Save this filter to persist it"
        if len(fil_to_show.forms) == 0:
            OFormSet = formset_factory(OutForm, extra=1)
            _dict["msg"] = "This filter was empty fill out the form to make an expression"
        else:
            OFormSet = formset_factory(OutForm, extra=0)
        formset = OFormSet(initial=[ i.value_dict for i in fil_to_show.forms])
        ff = FilterForm(initial={"name": filter_name, "comment":fil_to_show.comment})
        _dict["formset"] = formset
        _dict["ff"] = ff
        s.close()
        return render_to_response("just_filter.html",
                _dict,
                context_instance=RequestContext(request),
                )

def save_filter(request, filter_name=None):
    if request.method == "POST":
        OutFormSet = formset_factory(OutForm)
        outformset = OutFormSet(request.POST)
        filterform = FilterForm(request.POST)

        if not outformset.is_valid() or not filterform.is_valid():
            return HttpResponse("invalid form")
        filter_name=filterform.cleaned_data["name"]
        form_li = [i.cleaned_data for i in outformset.forms]
        if len(form_li) > 0:
            form_li[-1]["logical_operation"] = "none"
        dname = {"name" : filter_name}
        if filterform.cleaned_data.get("comment") is "":
            dname["comment"] = filterform.cleaned_data["comment"]
        _filter = make_filter_with_forms(form_li, dname)

        s = make_dbdb_session()
        ret = s.query(Filter).filter_by(name=filter_name).scalar()
        if ret is not None:
            s.delete(ret)
            s.commit()
        s.add(_filter)
        s.commit()
        s.close()

        return HttpResponse("%(name)s has been saved<br>======it looks like======<br> %(expr)s" % {'name' : filter_name, 'expr': _filter.expression})


def show_expression(request, filter_name):
    s = make_dbdb_session()
    ret = s.query(Filter).filter_by(name=filter_name).first()
    expr = ret.expression
    s.close()
    return HttpResponse("%(name)s  expression looks like this<br> %(expression)s" % {'name' : filter_name, 'expression' : expr})

def delete_filter(request, filter_name):
    s = make_dbdb_session()
    ret = s.query(Filter).filter_by(name=filter_name).scalar()
    s.add(ret)
    s.delete(ret)
    s.commit()
    s.close()
    return HttpResponse("%(name)s was deleted" % {'name' : filter_name})




from graphs import segment_mr_month, make_img_tag
import table_mapping_no_eager_loading
import matplotlib.dates as mdates
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook
import numpy as np


def make_naive_graphs(request, db_name):
    s = make_input_db_session(db_name, echo=True)
    mrs_ret = s.query(table_mapping_no_eager_loading.master_record).all()
    start = date(1996,10,1)
    end = date(2012,12,12)
    x, y = segment_mr_month(mrs_ret, start, end)
    plt.bar(x, y, width=10, color="black")
    ax = plt.subplot(111)
    years    = mdates.YearLocator()   # every year
    months   = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)

    ax.set_xlim(start, end)
    ax.grid(True)
    
    labels = ax.get_xticklabels() 
    for label in labels: 
        label.set_rotation(30) 



    fig = plt.gcf()
    html = make_img_tag(fig)
    fig.autofmt_xdate()
    plt.close()

    ret = s.query(problem_code).all()

    ret.sort(key=lambda x: len(x.device_problems))
    top_25 = ret[::-1][:25]
    counts = [len(i.device_problems) for i in top_25]
    labels = [i.problem_description for i in top_25]
    pos = range(len(top_25))
    plt.barh(pos, counts, color="green")
    ax = plt.subplot(111)
    ax.grid(True)
    plt.yticks(pos, labels)
    fig = plt.gcf()
    fig.set_figwidth(20)
    fig.set_figheight(12)







    html = html + "<br> <br>" + make_img_tag(fig)
    plt.close()

    event_type_dict = {}
    for m_r in mrs_ret:
        if event_type_dict.get(m_r.event_type):
            event_type_dict[m_r.event_type] += 1
        else:
            event_type_dict[m_r.event_type] = 1

    labels = event_type_dict.keys()
    counts = [event_type_dict[i] for i in labels]
    pos = range(len(labels))
    plt.bar(pos, counts, color="teal")
    plt.xticks(pos, labels)
    fig = plt.gcf()
    html = html + "<br>" + make_img_tag(fig)
    plt.close()

    s.close()



    html = html + "<br>" + str(y)
    return render_to_response("db_graph.html",
            {"html" : html},
            context_instance=RequestContext(request),
            )



