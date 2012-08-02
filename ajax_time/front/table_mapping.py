from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer,  ForeignKey, Enum, Date, create_engine
from sqlalchemy.dialects.mysql import TEXT, VARCHAR, TINYTEXT 
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session
from sqlalchemy.sql import and_


class FOI_text(Base):
    __tablename__ = 'text_table'

    MDR_report_key = Column(Integer)
    text_key = Column(Integer, primary_key=True)
    text_type_code = Column(Enum('N','D','E'))
    patient_sequence_number = Column(Integer)
    date_report = Column(Date, nullable=True)
    text = Column(TEXT)



class device(Base):
    __tablename__ = 'device_table'

    MDR_report_key = Column(Integer, primary_key=True)
    device_event_key = Column(Integer, primary_key=True) 
    implant_flag = Column(Enum("Y", "N", ""), nullable = True)
    date_removed_flag = Column(VARCHAR(20))
    date_sequence_num = Column(Integer, primary_key=True)

    date_recieved = Column(TINYTEXT)
    brand_name = Column(TINYTEXT)
    generic_name = Column(TINYTEXT)
    manufacturer_name = Column(TINYTEXT)
    manufacturer_address_1 = Column(TINYTEXT)
    manufacturer_address_2 = Column(TINYTEXT)
    manufacturer_city = Column(TINYTEXT)
    manufacturer_state_code = Column(VARCHAR(2))
    manufacturer_zip_code = Column(Integer)
    manufacturer_zip_code_ext = Column(Integer)
    manufacturer_country_code = Column(VARCHAR(20))
    manufacturer_postal_code = Column(VARCHAR(30))
    expiration_date_of_device = Column(VARCHAR(30))
    model_number = Column(TINYTEXT)
    lot_number = Column(VARCHAR(30))
    catalog_number = Column(VARCHAR(100))
    other_id_number = Column(VARCHAR(100))
    device_operator = Column(VARCHAR(10))
    device_availability = Column(Enum("Y","N","R","*"), nullable = True)
    date_returned_to_manufacturer = Column(VARCHAR(30))
    device_report_product_code = Column(VARCHAR(40))
    device_age = Column(VARCHAR(30))
    device_evaluated_by_manufacturer = Column(Enum("Y", "N", "R"), nullable = True)
    baseline_brand_name = Column(TINYTEXT)
    baseline_generic_name = Column(TINYTEXT)
    baseline_mode_no = Column(VARCHAR(30))
    baseline_catalog_no = Column(VARCHAR(30))
    baseline_other_id_no = Column(VARCHAR(30))
    baseline_device_family = Column(VARCHAR(256))
    baseline_shelf_life = Column(VARCHAR(3))
    baseline_shelf_life_months = Column(Integer)
    baseline_PMA_flag = Column(VARCHAR(3))
    baseline_PMA_no = Column(VARCHAR(30))
    baseline_510k_flag = Column(VARCHAR(3))
    baseline_510k_no = Column(VARCHAR(30))
    baseline_preamendment = Column(TINYTEXT)
    baseline_transitional = Column(VARCHAR(30))
    baseline_510kexempt_flag = Column(VARCHAR(10))
    baseline_first_marketed = Column(VARCHAR(30))
    baseline_stop_marketed = Column(VARCHAR(30))

class master_record(Base):
    __tablename__ = 'master_table'


    MDR_report_key = Column(Integer, primary_key=True, autoincrement=False)
    event_key = Column(Integer)
    report_number = Column(VARCHAR(20)) #NOT AN INT ANYMORE
    report_source_code = Column(Enum('P','U','D','M'))
    manufacturer_link_flag = Column(Enum('Y','N'), nullable=True)
    num_devices_in_event = Column(Integer, nullable=True)
    num_patients_in_event = Column(Integer, nullable=True)
    date_recieved = Column(Date, nullable=True)
    adverse_event_flag = Column(VARCHAR(2))
    product_problem_flag = Column(VARCHAR(2))
    date_report = Column(Date, nullable=True)
    date_event = Column(Date, nullable=True)
    single_use_flag = Column(Enum('Y', 'N', ''))
    reporter_occupation_code = Column(Integer, nullable=True)
    health_profesional = Column(TINYTEXT)
    intial_report = Column(VARCHAR(2))
    distributor_name = Column(VARCHAR(2255))
    distributor_address_1 = Column(TINYTEXT)
    distributor_address_2 = Column(TINYTEXT)
    distributor_city = Column(TINYTEXT)
    distributor_state_code = Column(VARCHAR(2))
    distributor_zip_code = Column(VARCHAR(10))
    distributor_zip_code_ext = Column(VARCHAR(10))
    date_facility_aware = Column(VARCHAR(40))
    report_type = Column(VARCHAR(20))
    report_date = Column(Date, nullable=True)
    report_to_FDA =  Column(Enum('Y','N',''), nullable=True)
    report_date_FDA = Column(Date, nullable=True) #LAST DATE
    event_location = Column(TINYTEXT)
    report_manufacturer = Column(VARCHAR(30))
    date_report_to_manufacturer = Column(VARCHAR(20))
    manufacturer_name = Column(TINYTEXT)
    manufacturer_address_1 = Column(TINYTEXT)
    manufacturer_address_2 = Column(TINYTEXT)
    manufacturer_city = Column(TINYTEXT)
    manufacturer_state_code = Column(VARCHAR(2))
    manufacturer_zip_code = Column(VARCHAR(20))
    manufacturer_zip_code_ext = Column(VARCHAR(10))
    manufacturer_country_code = Column(VARCHAR(20))
    manufacturer_postal_code = Column(VARCHAR(30))
    manufacturer_contact_Title_Name = Column(VARCHAR(30))
    manufacturer_contact_First_Name = Column(VARCHAR(50))
    manufacturer_contact_Last_Name = Column(VARCHAR(50))
    manufacturer_contact_Street_1 = Column(VARCHAR(2000))
    manufacturer_contact_Street_2 = Column(VARCHAR(2000))
    manufacturer_contact_City = Column(VARCHAR(400))
    manufacturer_contact_State_Code = Column(VARCHAR(10))
    manufacturer_contact_Zip_Code = Column(VARCHAR(30))
    manufacturer_contact_Zip_Code_Ext = Column(VARCHAR(10))
    manufacturer_contact_Country_Code = Column(VARCHAR(10))
    manufacturer_contact_Postal_Code = Column(VARCHAR(20))
    manufacturer_contact_Phone_No_Area_Code = Column(VARCHAR(20))
    manufacturer_contact_Phone_No_Exchange = Column(VARCHAR(20))
    manufacturer_contact_Phone_No = Column(VARCHAR(20))
    manufacturer_contact_Phone_No_Ext = Column(VARCHAR(10))
    manufacturer_contact_Phone_No_Country_Code = Column(VARCHAR(10))
    manufacturer_contact_Phone_No_City_Code = Column(VARCHAR(15))
    manufacturer_contact_Phone_No_Local = Column(VARCHAR(20))
    manufacturer_g1_Name = Column(VARCHAR(500))
    manufacturer_g1_Street_1 = Column(VARCHAR(500))
    manufacturer_g1_Street_2 = Column(VARCHAR(500))
    manufacturer_g1_City = Column(VARCHAR(50))
    manufacturer_g1_State_Code = Column(VARCHAR(10))
    manufacturer_g1_Zip_Code = Column(VARCHAR(10))
    manufacturer_g1_Zip_Code_Ext = Column(VARCHAR(10))
    manufacturer_g1_Country_Code = Column(VARCHAR(10))
    manufacturer_g1_Postal_Code = Column(VARCHAR(10))
    source_type = Column(VARCHAR(10))
    date_manufacturer_recd = Column(VARCHAR(20))
    device_date_manufacture = Column(VARCHAR(20))
    single_use_flag_2 = Column(VARCHAR(2))
    remedial_action = Column(VARCHAR(10)) #promising
    prev_use_code = Column(VARCHAR(20))
    removal_correction_num = Column(VARCHAR(20))

    e = Enum('D','IN','IL','IJ','M','O','*','')

    event_type = Column(e, nullable=True)

class patient(Base):
    __tablename__ = "patient_table"

    MDR_report_key = Column(Integer, primary_key=True) 
    patient_sequence_number = Column(Integer, primary_key=True, autoincrement=False)
    date_recieved = Column(VARCHAR(20))
    sequence_num_treatment = Column(VARCHAR(200))
    sequence_num_outcome = Column(VARCHAR(200))

class problem_code(Base):
    __tablename__ = "problem_code_table"

    device_problem_code = Column(Integer, primary_key=True)
    problem_description = Column(TINYTEXT)


class  device_problem(Base):
    __tablename__ = "device_problem_table"

    MDR_report_key = Column(Integer, primary_key=True)
    problem_code_key = Column(Integer, primary_key=True, autoincrement=False )




# relations among tables
patient.master_record = relationship(
        "master_record",
        foreign_keys=[patient.MDR_report_key],
        primaryjoin=and_(patient.MDR_report_key==master_record.MDR_report_key),
        backref=backref(
            "patients", 
            uselist=True,
            lazy="joined",
            ),
        uselist=False
        )





device_problem.device = relationship(
        "device",
        foreign_keys=[device_problem.MDR_report_key],
        primaryjoin=and_(device.MDR_report_key==device_problem.MDR_report_key),
        backref=backref(
            "problems",
            uselist=True,
            ),
        uselist=False
        )
"""
device.problems = relationship(
        "device_problem",
        primaryjoin=and_(device.MDR_report_key==device_problem.MDR_report_key),
        foreign_keys=[device.MDR_report_key],
        uselist=True,
        backref=backref(
            "device",
            foreign_keys=[device_problem.MDR_report_key],
            ),
        )
"""

device.master_record = relationship(
            "master_record",
            primaryjoin=and_(device.MDR_report_key==master_record.MDR_report_key),
            foreign_keys=[device.MDR_report_key],
            uselist=False,
            backref=backref(
                "devices", 
                uselist=True,
                ),
            )



problem_code.device_problems = relationship(
        "device_problem",
        foreign_keys=[problem_code.device_problem_code],
        primaryjoin=and_(device_problem.problem_code_key==problem_code.device_problem_code),
        backref=backref(
            "problem_code",
            uselist=False,
            lazy="joined",
            ),
        uselist=True,
        )

FOI_text.master_record = relationship("master_record",
        primaryjoin=and_(FOI_text.MDR_report_key==master_record.MDR_report_key),
        foreign_keys=[FOI_text.MDR_report_key],
        backref=backref(
            'text_records', 
            uselist=True,
            lazy="joined",
            )
        )

if __name__ == "__main__":
    engine = create_engine('mysql://dba@localhost:3306/orm_fun',echo=True)
    DBSession = scoped_session(sessionmaker(autoflush=True, bind=engine))
    DBSession = sessionmaker(autoflush=True, bind=engine)
    Base.metadata.create_all(bind=engine)
