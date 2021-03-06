from django import forms
from table_mapping import *
import datetime
from dbdb import Db, Session, make_dbdb_session, Filter
from IPython import embed

class SimpleForm(forms.Form):
    obj = forms.ChoiceField(choices=[
        ('text_table', 'Text records'),
        ('device_table', 'Device records'),
        ('master_table', 'Master records'),
        ('patient_table', 'Patient records'),
        ], label="Select type of record to search")

    id = forms.IntegerField(required=False, label = "Primary key")
    number = forms.IntegerField(required=True, initial=1)
    order = forms.IntegerField(initial=2)

class GenDev_FailType(forms.Form):
    gendev = forms.CharField(initial = "infusion pump", 
            label="Specify the generic device name")

    e = master_record.e
    li = [ (b, b) for b in e.enums ]
    failtype = forms.ChoiceField(choices = li, 
            label="Pick a failure type")
    failtype2 = forms.ChoiceField(choices = li, 
            label="(Optional) Pick another failure type", required=False)
    date_after = forms.DateField(initial=datetime.date(2010,6,1),
            label="Search after given date", required=False)
    order = forms.IntegerField(initial=1)


p_li = [ (i,i) for i in patient.__table__.c.keys()]
mr_li = [ (i,i) for i in master_record.__table__.c.keys()]
dev_li = [ (i,i) for i in device.__table__.c.keys()]
prob_li = [ (i,i) for i in problem_code.__table__.c.keys()]
text_li = [ (i, i) for i in FOI_text.__table__.c.keys()]
all_li = [p_li, mr_li, dev_li, prob_li, text_li]

for i in all_li:
    i.insert(0, ("all", "All fields"))
    i.insert(0, ("none", "Leave all fields out"))

type_li = [
        ("master_record", "master_record"),
        ("device", "device"),
        ("patient","patient"),
        ("problem_code","problem_code",),
        ("FOI_text", "text records"),
        ]

filters = [
        ("date_report", "date of report"),
        ("date_event", "date of event"),
        ("device_type", "device type"),
        ("manufacturer", "manufacturer name"),
        ("event_type", "event type"),
        ]

tf =  "table_fields"

event_type_enums =  [(e,e) for e in master_record.__table__.c.event_type.type.enums]

logical_ops = [
        ("none", "None (use for last filter)"),
        ("and", "and"),
        ("or", "or"),
        ]

class DBForm(forms.Form):
    input_db = forms.ChoiceField(required=False)
    output_db = forms.CharField(initial="temp_db", max_length=25)
    drop_output_selector = forms.BooleanField(required=False,label="Drop db if already exists?")
    filter_name = forms.CharField(initial="test", max_length=100)


class FilterForm(forms.Form):
    name = forms.CharField(max_length=100)
    comment = forms.CharField(widget=forms.widgets.Textarea(), required=False)
    
    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
class OutForm(forms.Form):
    filter_choice = forms.ChoiceField(required=False, label="Use filter:")
    filter_selector = forms.ChoiceField(choices=filters,initial="device_type",
                                        required=False,
                                        )
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)

    device_type = forms.CharField(initial="infusion pump",
                            required=False,)
    t = "Use Contains for device type?"
    device_contains = forms.BooleanField(required=False, label=t)

    manufacturer_name = forms.CharField(required=False)
    event_type = forms.ChoiceField(choices=event_type_enums, required=False)
    logical_operation = forms.ChoiceField(choices=logical_ops,
            label="Logical operation for next filter block",
            widget=forms.Select(attrs={'onchange': "duplicate_table()", "class" : "notfilter"}),
            required=False,
            )
    not_op = forms.BooleanField(required=False,
            label="Check to not",
            )

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        self.fields['date_from'].widget.attrs['class'] = "date_report date_event"
        self.fields['date_to'].widget.attrs['class'] = "date_report date_event"
        self.fields['device_type'].widget.attrs['class'] = "device_type"
        self.fields['device_contains'].widget.attrs['class'] = "device_type"
        self.fields['manufacturer_name'].widget.attrs['class'] = "manufacturer"
        self.fields['event_type'].widget.attrs['class'] = "event_type"
        self.fields['logical_operation'].widget.attrs['class'] = "notfilter"
        self.fields['not_op'].widget.attrs['class'] = "notfilter"
        self.fields['filter_selector'].widget.attrs['class'] = "filter_selector"
        s = make_dbdb_session()
        f_li =  [(i.name,i.name) for i in s.query(Filter).all()]
        f_li.append(("new_form", "New generic form"))
        f_li = f_li[::-1]
        self.fields["filter_choice"].choices = f_li
        self.fields['filter_choice'].widget.attrs['class'] = "filter_choice"
        s.close()



   
class SelectForm(forms.Form):
    type_selector = forms.ChoiceField(choices=type_li, initial="patient", required=True)
    patient_field_selector = forms.ChoiceField(choices=p_li, initial="all")
    master_record_field_selector = forms.ChoiceField(choices=mr_li)
    device_field_selector = forms.ChoiceField(choices=dev_li)
    problem_code_field_selector = forms.ChoiceField(choices=prob_li)
    FOI_text_field_selector = forms.ChoiceField(choices=text_li, label="Text field selector")

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        self.fields['patient_field_selector'].widget.attrs['class'] = tf
        self.fields['master_record_field_selector'].widget.attrs['class'] = tf
        self.fields['device_field_selector'].widget.attrs['class'] = tf
        self.fields['problem_code_field_selector'].widget.attrs['class'] = tf
        self.fields['FOI_text_field_selector'].widget.attrs['class'] = tf







s = make_dbdb_session()
ret_prox = s.query(Db).all()
dbs = [(i.name, i.name) for i in ret_prox]
s.close()

class RawForm(forms.Form):
    db_to_select_from = forms.ChoiceField(choices=dbs, required=True)
    select_body = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(RawForm, self).__init__(*args, **kwargs)
        self.fields['select_body'].widget = forms.Textarea()






