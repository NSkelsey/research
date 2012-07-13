from django import forms
from table_mapping import *
import datetime
from dbdb import Db, Session, make_dbdb_session

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
        ("date", "date filter"),
        ("device_type", "device type"),
        ("manufacturer", "manufacturer name"),
        ("event_type", "event type"),
        ]

tf =  "table_fields"

event_type_enums =  [(e,e) for e in master_record.__table__.c.event_type.type.enums]

class OutForm(forms.Form):

    input_db = forms.ChoiceField(required=False)
    output_db = forms.CharField(initial="temp_db", max_length=25)
    drop_output_selector = forms.BooleanField(required=False,label="Drop db if already exists?")

    filter_selector = forms.ChoiceField(choices=filters,initial=filters[0][0])
    
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)

    device_type = forms.CharField(initial="infusion pump",)

    manufacturer_name = forms.CharField(required=False)
    event_type = forms.ChoiceField(choices=event_type_enums, required=False)



   
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

class RawForm(forms.Form):
    db_to_select_from = forms.ChoiceField(choices=dbs, required=True)
    select_body = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(RawForm, self).__init__(*args, **kwargs)
        from IPython import embed
        self.fields['select_body'].widget = forms.Textarea()






