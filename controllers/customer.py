# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)
import os
import json
import csv

import datetime
import time
import calendar
from datetime import timedelta
from decimal  import Decimal



import random
import string
from string import Template

from applications.my_pms2.modules  import account
from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import mail

from applications.my_pms2.modules  import mdpappointment
from applications.my_pms2.modules  import mdpcustomer



def plans():
    
    regionid = 1
    companyid = 1
    
    
    regionid = common.getid(request.vars.regionid)
        
  
    companyid = common.getid(request.vars.companyid)
        
       
    
    plans = db((db.companyhmoplanrate.is_active == True) & (db.companyhmoplanrate.groupregion==regionid) & (db.companyhmoplanrate.company==companyid) & \
               (db.companyhmoplanrate.relation == 'Self') & (db.hmoplan.is_active==True)).\
        select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
               left=db.hmoplan.on((db.companyhmoplanrate.hmoplan == db.hmoplan.id)&(db.hmoplan.is_active==True)),distinct=True)
    
   
    return dict(plans=plans)


def list_customers():
    
    db = current.globalenv['db']
    
    formheader = "Customer List"
    username = "Admin" 
    
    page = common.getpage1(request.vars.page)
    returnurl = URL('default', 'main')
    db.vw_customer.id.readable = False
    db.vw_customer.customerid.readable = False
    db.vw_customer.customer_ref.readable = False
    fields=(
           
            db.vw_customer.customerid,
       
            db.vw_customer.customername,
            db.vw_customer.address,
            db.vw_customer.cell,
            
            db.vw_customer.appointment_id,
            db.vw_customer.appointment_datetime,
            db.vw_customer.company,
            db.vw_customer.provider,
          
            db.vw_customer.hmoplancode,
            db.vw_customer.status
            )
    
    headers={
             
             'vw_customer.customername':'Name',
             'vw_customer.address':'Customer Address',
             'vw_customer.cell':'Cell',
             'vw_customer.appointment_id':'Appointment ID',
             'vw_customer.appointment_datetime':'Appointment ON',
             
             'vw_customer.provider':'Provider',
             'vw_customer.company': 'Company',
             'vw_customer.hmoplancode':'Plan',
             'vw_customer.status':'Status'
             }
    
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, xml=False)
    
    

    
    links = [lambda row: A('Update',_href=URL("customer","update_customer",vars=dict(page=page,customerid=row.id))),
             
             lambda row: A('Enroll',_href=URL("customer","enroll_customer",
                                              vars=dict(page=page,customerid=row.id)))  if(row.status != 'Enrolled') else "",
             
             lambda row: A('Dependants',_href=URL("customer","list_customer_dependants",vars=dict(customer_id = row.id,page=page))) if(row.status != 'Enrolled') else "" ,
             lambda row: A('Delete',_href=URL("customer","delete_customer",vars=dict(customerid = row.id,customername=row.customername,page=page)))
             ]
    query = ((db.vw_customer.id > 0) & (db.vw_customer.is_active == True))
    
    maxtextlength = 40
    maxtextlengths = {'vw_customer.address':100}
                      
    orderby = ~(db.vw_customer.id)    

    formB = SQLFORM.grid(query=query,
                         headers=headers,
                         fields=fields,
                         links=links,
                         maxtextlengths =maxtextlengths,
                         orderby=orderby,
                         exportclasses=exportlist,
                         links_in_grid=True,
                         searchable=True,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                         )

    return dict(formB = formB, username = username, formheader=formheader, page=page, returnurl = returnurl)


def list_customer_dependants():
    
    db = current.globalenv['db']
    
    formheader = "Customer Dependant List"
    username = "Admin" 
    
    customer_id = int(request.vars.customer_id)
    page = common.getpage1(request.vars.page)
    returnurl = URL('customer', 'list_customers', vars=dict(page=page))
    
    
    fields=(
           
            db.customerdependants.fname,
            db.customerdependants.lname,
            
            db.customerdependants.dependant_ref,
            db.customerdependants.depdob,
            db.customerdependants.gender,
            db.customerdependants.relation
            )
    
    headers={
             
             'customerdependants.fname':'First Name',
             'customerdependants.fname':'LLast Nmae',
             'customerdependants.dependant_ref':'Ref',
             'customerdependants.depdob':'DOB',
             'customerdependants.gender':'Gender',
             
             'customerdependants.relation':'Relation'
             }
    
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, xml=False)
    
    

    
    links = [lambda row: A('Update',_href=URL("customer","update_customer_dependant",vars=dict(page=page,dependant_id=row.id))),
             
          
             
                         
             lambda row: A('Delete',_href=URL("customer","delete_customer_dependant",vars=dict(dependant_id = row.id,page=page)))
             ]
    query = ((db.customerdependants.customer_id == customer_id) & (db.customerdependants.is_active == True))
    
    maxtextlength = 40
    
                      
    orderby = ~(db.customerdependants.id)    

    formB = SQLFORM.grid(query=query,
                         headers=headers,
                         fields=fields,
                         links=links,
                      
                         orderby=orderby,
                         exportclasses=exportlist,
                         links_in_grid=True,
                         searchable=True,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                         )

    return dict(formB = formB, username = username, formheader=formheader, customer_id=customer_id,page=page, returnurl = returnurl)

def new_customer_dependant():
    
    formheader = "Dependant"
    username = "Admin"  
    
    page = common.getpage1(request.vars.page)
    customer_id = int(request.vars.customer_id)
    
    returnurl = URL('customer','list_customer_dependants', vars=dict(page=page,customer_id=customer_id))

   
    c = db((db.customer.id == customer_id) & (db.customer.is_active == True)).select(db.customer.customer_ref, db.customer.fname, db.customer.lname)
    
    if(len(c)!=1):
        redirect(returnurl)
     
    customer_ref = c[0].customer_ref  
    customer_name = c[0].fname + " " + c[0].lname
   
    formA = SQLFORM.factory(
     
       
        Field('fname', 'string',label='First Name', default='', requires=IS_NOT_EMPTY()),
        Field('mname', 'string',label='Middle Name', default=''),
        Field('lname', 'string',label='Last Name', default='', requires=IS_NOT_EMPTY()),
        Field('gender', 'string',label='Gender', default='Male', requires = IS_IN_SET(GENDER)),
        Field('depdob', 'date',label='DOB', default=request.now,  requires=IS_DATE(format=('%d/%m/%Y')),length=20),
        Field('relation', 'string',label='Relation', default='Spouse', requires = IS_IN_SET(RELATIONS)),
    )
    
    if formA.process().accepted:
        dependant_id = db.customerdependants.insert(**db.customerdependants._filter_fields(formA.vars))
        
        db(db.customerdependants.id == dependant_id).update(dependant=str(dependant_id), customer_id = customer_id,dependant_ref = customer_ref + "_" + formA.vars.relation)
        
        redirect(returnurl)

    elif formA.errors:
        response.session.flash = "Error - Creating new customer dependant" + str(formA.errors)

        
    
    return dict(formA=formA,username=username, returnurl=returnurl,formheader=formheader,page=page,customer_ref=customer_ref,customer_name = customer_name,customer_id=customer_id)


def update_customer_dependant():
    
    db = current.globalenv['db']
    
    formheader = "Customer Dependant"
    username = "Admin" 
  
    dependant_id = int(common.getid(request.vars.dependant_id))
    page = common.getpage1(request.vars.page)
    
    ds = db((db.customerdependants.id == dependant_id) & (db.customerdependants.is_active == True)).select()
    customer_id = ds[0].customer_id if(len(ds)==1) else 0
    
    c = db((db.customer.id == customer_id) & (db.customer.is_active == True)).select()
    customer_name = c[0].fname + " " + c[0].lname if len(c)==1 else ""
    customer_ref = c[0].customer_ref if len(c)==1 else ""
    
    returnurl = URL('customer','list_customer_dependants', vars=dict(page=page,customer_id=customer_id))

    if(len(ds) == 1):
        dependant = ds[0].dependant
        dependant_ref = ds[0].dependant_ref
       
        fname = ds[0].fname
        mname = ds[0].mname
        lname = ds[0].lname
        gender = ds[0].gender
        depdob = ds[0].depdob
        relation = ds[0].relation
    else:
        dependant = ''
        dependant_ref = ''
       
        fname = ''
        mname = ''
        lname = ''
        gender = 'Male'
        depdob = request.now
        relation = "Spouse"
        
    formA = SQLFORM.factory(
        Field('dependant', 'string',label='Dependant ID', default=dependant),
        Field('dependant_ref', 'string',label='Dependant Ref', default=dependant_ref),
        Field('fname', 'string',label='First Name', default=fname, requires=IS_NOT_EMPTY()),
        Field('mname', 'string',label='Middle Name', default=mname),
        Field('lname', 'string',label='Last Name', default=lname, requires=IS_NOT_EMPTY()),
        Field('gender', 'string',label='Gender', default=gender, requires = IS_IN_SET(GENDER)),
        Field('depdob', 'date',label='DOB', default=depdob,  requires=IS_DATE(format=('%d/%m/%Y')),length=20),
        Field('relation', 'string',label='Relation', default=relation, requires = IS_IN_SET(RELATIONS)),
        
    )

   

    
    if formA.process().accepted:
        db(db.customerdependants.id == dependant_id).update(
            
            fname = formA.vars.fname,
            mname = formA.vars.mname,
            lname = formA.vars.lname,
            gender = formA.vars.gender,
            depdob = formA.vars.depdob,
            relation = formA.vars.relation,

            modified_on = common.getISTFormatCurrentLocatTime(),
            modified_by =  1 if(auth.user == None) else auth.user.id
                                    
            
        ) 
        
        redirect(returnurl)

    elif formA.errors:
        response.session = "Error - updating customer dependant" + str(formA.errors)

 

    
    return dict(formA=formA,username=username, returnurl=returnurl,formheader=formheader,page=page,customer_ref=customer_ref,customer_name = customer_name,dependant_id=dependant_id)
    
   


#this function helps the customer support to record the 
#customer profile details and appointment time from TPA
#Once all items are confirmed, the customer is enrolled
#@auth.requires_membership('webadmin')
#@auth.requires_login()
def new_customer():

    formheader = "Customer"
    username = "Admin" 

    rows = db(db.company.company == 'B2C_NG').select()
    companyid = rows[0]['company.id'] if(len(rows) > 0) else 0
    company = rows[0]['company'] if(len(rows) > 0) else ""
    name = rows[0]['name'] if(len(rows) > 0) else "" 
    
    planid = 1
    regionid = 1
    providerid = 1
    page = 1
    
    formA = SQLFORM.factory(
        Field('customer', 'string',label='Customer ID', default=''),
        Field('customer_ref', 'string',label='Customer Ref', default=''),
        Field('providerid', default=providerid,requires=IS_IN_DB(db(db.provider.is_active==True), 'provider.id', '%(provider)s : (%(providername)s)')),
        Field('companyid', default=companyid, requires=IS_IN_DB(db(db.company.is_active==True), 'company.id', '%(name)s (%(company)s)')),
        Field('planid', default=planid, requires=IS_IN_DB(db(db.hmoplan.is_active==True), 'hmoplan.id', '%(name)s (%(hmoplancode)s) (%(groupregion)s)')),
        Field('regionid', default=regionid, requires=IS_IN_DB(db(db.groupregion.is_active == True), 'groupregion.id', '%(region)s (%(groupregion)s)')),
        Field('fname', 'string',label='First Name', default='', requires=IS_NOT_EMPTY()),
        Field('mname', 'string',label='Middle Name', default=''),
        Field('lname', 'string',label='Last Name', default='', requires=IS_NOT_EMPTY()),
        Field('gender', 'string',label='Gender', default='Male', requires = IS_IN_SET(GENDER)),
        Field('dob', 'date',label='DOB', default=request.now,  requires=IS_DATE(format=('%d/%m/%Y')),length=20),
        Field('address1', 'string',label='Address1', default='331-332 Ganpati Plaza', requires=IS_NOT_EMPTY()),
        Field('address2', 'string',label='Address2', default='MI Road', requires=IS_NOT_EMPTY()),
        Field('address3', 'string',label='Address3', default=''),
        Field('city', 'string',label='City', default='Jaipur', requires = IS_IN_SET(CITIES)),
        Field('st', 'string',label='State', default='Rajasthan (RJ)',requires = IS_IN_SET(STATES)),
        Field('pin', 'string',label='pin', default='302001',requires=IS_NOT_EMPTY()),
        Field('cell', 'string',label='Cell Phone', default=''),
        Field('telephone', 'string',label='Telephone', default=''),
        Field('email', 'string',label='Email', default='emailid@mydentalplan.in',requires=IS_NOT_EMPTY()),
        Field('pin1','string',default='302001',label='Pin Choice 1'),
        Field('pin2','string',default='302001',label='Pin Choice 2'),
        Field('pin3','string',default='302001',label='Pin Choice 3'),
        Field('appointment_id','string',default='',label='Appointment ID'),
        Field('appointment_datetime', 'datetime',label='DOB', default=request.now,  requires=IS_DATETIME(format=('%d/%m/%Y %H:%M:%S')),length=20),
        Field('notes','text',default='',label='Notes')
    )


    
    if formA.process().accepted:
        customerid = db.customer.insert(**db.customer._filter_fields(formA.vars))
        db(db.customer.id == customerid).update(customer = str(customerid))
        if(formA.vars.customer_ref == ""):
            db(db.customer.id == customerid).update(customer_ref = str(customerid).zfill(3))
        
        redirect(URL('customer','update_customer', vars=dict(customerid=customerid)))

    elif formA.errors:
        response.session.flash = "Error - Creating new customer" + str(formA.errors)

    regionid = 0

    regions = db(db.groupregion.is_active == True).select(db.groupregion.ALL, orderby=db.groupregion.region)  #IB 07042016
    plans   = db((db.companyhmoplanrate.groupregion==regionid) & (db.companyhmoplanrate.company==companyid)).\
        select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
               left=db.hmoplan.on((db.companyhmoplanrate.hmoplan == db.hmoplan.id)&(db.hmoplan.is_active==True)))    
 
    returnurl = URL('customer', 'list_customers',vars=dict(page=page))

    return dict(formA=formA,username=username, returnurl=returnurl,formheader=formheader,regions=regions, plans=plans,page=page)



def update_customer():
    
    db = current.globalenv['db']
    
    formheader = "Customer"
    username = "Admin" 
    status = "No_Attempt"
    
    customerid = int(common.getid(request.vars.customerid))
  
    page = common.getpage1(request.vars.page)
    
    ds = db((db.customer.id == customerid) & (db.customer.is_active == True)).select()
    
    if(len(ds) == 1):
        customer = ds[0].customer
        customer_ref = ds[0].customer_ref
        providerid = ds[0].providerid
        companyid = ds[0].companyid
        planid = ds[0].planid
        regionid = ds[0].regionid
        fname = ds[0].fname
        mname = ds[0].mname
        lname = ds[0].lname
        gender = ds[0].gender
        dob = ds[0].dob
        address1 = ds[0].address1
        address2 = ds[0].address2
        address3 = ds[0].address3
        city = ds[0].city
        st = ds[0].st
        pin = ds[0].pin
        cell = ds[0].cell
        telephone = ds[0].telephone
        email = ds[0].email
        pin1 = ds[0].pin1
        pin2 = ds[0].pin2
        pin3 = ds[0].pin3
        
        appointment_id = ds[0].appointment_id
        appointment_datetime = ds[0].appointment_datetime
        notes = ds[0].notes
        
        status = ds[0].status
        
    else:
        customer = ''
        customer_ref = ''
        providerid = 1
        companyid = 1
        planid = 1
        regionid = 1
        fname = ''
        mname = ''
        lname = ''
        gender = 'Male'
        db = request.now,
        address1 = '331 Ganpati Plaza'
        address2 = 'MI Road'
        address3 = ''
        city = 'Jaipur'
        st = 'Rajasthan (RJ)'
        pin = '302001'
        cell = ''
        telephone = ''
        email = ''
        pin1 = '302001'
        pin2 = '302001'
        pin3 = '302001'     
        appointment_id = ''
        appointment_datetime = request.now
        notes = ''       
        status = "No_Attempt"
        
    formA = SQLFORM.factory(
        Field('customer', 'string',label='Customer ID', default=customer),
        Field('customer_ref', 'string',label='Customer Ref', default=customer_ref),
        Field('providerid', default=providerid,requires=IS_IN_DB(db(db.provider.is_active==True), 'provider.id', '%(provider)s : (%(providername)s)')),
        Field('companyid', default=companyid, requires=IS_IN_DB(db(db.company.is_active==True), 'company.id', '%(name)s (%(company)s)')),
        Field('planid', default=planid, requires=IS_IN_DB(db(db.hmoplan.is_active==True), 'hmoplan.id', '%(name)s (%(hmoplancode)s) (%(groupregion)s)')),
        Field('regionid', default=regionid, requires=IS_IN_DB(db(db.groupregion.is_active == True), 'groupregion.id', '%(region)s (%(groupregion)s)')),
        Field('fname', 'string',label='First Name', default=fname, requires=IS_NOT_EMPTY()),
        Field('mname', 'string',label='Middle Name', default=mname),
        Field('lname', 'string',label='Last Name', default=lname, requires=IS_NOT_EMPTY()),
        Field('gender', 'string',label='Gender', default=gender, requires = IS_IN_SET(GENDER)),
        Field('dob', 'date',label='DOB', default=dob,  requires=IS_DATE(format=('%d/%m/%Y')),length=20),
        Field('address1', 'string',label='Address1', default=address1, requires=IS_NOT_EMPTY()),
        Field('address2', 'string',label='Address2', default=address2, requires=IS_NOT_EMPTY()),
        Field('address3', 'string',label='Address3', default=address3),
        Field('city', 'string',label='City', default=city, requires = IS_IN_SET(CITIES)),
        Field('st', 'string',label='State', default=st,requires = IS_IN_SET(STATES)),
        Field('pin', 'string',label='pin', default=pin,requires=IS_NOT_EMPTY()),
        Field('cell', 'string',label='Cell Phone', default=cell),
        Field('telephone', 'string',label='Telephone', default=telephone),
        Field('email', 'string',label='Email', default=email,requires=IS_NOT_EMPTY()),
        Field('pin1','string',default=pin1,label='Pin Choice 1'),
        Field('pin2','string',default=pin2,label='Pin Choice 2'),
        Field('pin3','string',default=pin3,label='Pin Choice 3'),
        Field('appointment_id','string',default=appointment_id,label='Appointment ID'),
        Field('appointment_datetime', 'datetime',label='DOB', default=appointment_datetime,  requires=IS_DATETIME(format=('%d/%m/%Y %H:%M:%S')),length=20),
        Field('notes','text',default=notes,label='Notes')
        
    )

   

    
    if formA.process().accepted:
        db(db.customer.id == customerid).update(
            
            customer = formA.vars.customer,
            customer_ref = formA.vars.customer_ref,
            providerid = formA.vars.providerid,
            companyid = formA.vars.companyid,
            planid = formA.vars.planid,
            regionid = formA.vars.regionid,
            fname = formA.vars.fname,
            mname = formA.vars.mname,
            lname = formA.vars.lname,
            gender = formA.vars.gender,
            dob = formA.vars.dob,
            address1 = formA.vars.address1,
            address2 = formA.vars.address2,
            address3 = formA.vars.address3,
            city = formA.vars.city,
            st = formA.vars.st,
            pin = formA.vars.pin,
            cell = formA.vars.cell,
            telephone = formA.vars.telephone,
            email = formA.vars.email,
            pin1 = formA.vars.pin1,
            pin2 = formA.vars.pin2,
            pin3 = formA.vars.pin3,
            appointment_id = formA.vars.appointment_id,
            appointment_datetime = formA.vars.appointment_datetime,
            notes = formA.vars.notes,

            modified_on = common.getISTFormatCurrentLocatTime(),
            modified_by =  1 if(auth.user == None) else auth.user.id
            
            
        ) 
        
        redirect(URL('customer','list_customers',vars=dict(page=page)))

    elif formA.errors:
        response.session = "Error - updating customer" + str(formA.errors)

 

    regions = db(db.groupregion.is_active == True).select()  #IB 07042016
    plans   = db((db.companyhmoplanrate.groupregion==regionid) & (db.companyhmoplanrate.company==companyid)).\
        select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
               left=db.hmoplan.on((db.companyhmoplanrate.hmoplan == db.hmoplan.id)&(db.hmoplan.is_active==True)))    
 
    returnurl = URL('customer','list_customers',vars=dict(page=page))
    enrollcustomer = URL('customer','enroll_customer',vars=dict(page=page,customerid=customerid))
    viewprovidercalendar = URL('my_pms2', 'appointment','customer_appointment',vars=dict(page=page,providerid = providerid,customerid=customerid))

    return dict(formA=formA,username=username, returnurl=returnurl,enrollcustomer=enrollcustomer,viewprovidercalendar=viewprovidercalendar,\
                formheader=formheader,regions=regions, plans=plans,regionid=regionid,planid=planid,status=status,page=page)
    
    
def delete_customer_dependant():
    
    db = current.globalenv['db']
    
    formheader = "Delete Dependant"
    username = "Admin" 
  
    dependant_id = int(common.getid(request.vars.dependant_id))
    page = common.getpage1(request.vars.page)
    
    ds = db((db.customerdependants.id == dependant_id) & (db.customerdependants.is_active == True)).select()
    customer_id = ds[0].customer_id if(len(ds)==1) else 0
    dependant_name =  ds[0].fname if(len(ds)==1) else "" + " " + ds[0].lname if(len(ds)==1) else ""
    
    c = db((db.customer.id == customer_id) & (db.customer.is_active == True)).select()
    customer_name = c[0].fname + " " + c[0].lname if len(c)==1 else ""
    customer_ref = c[0].customer_ref if len(c)==1 else ""
    
    returnurl = URL('customer','list_customer_dependants', vars=dict(page=page,customer_id=customer_id))
    
    form = FORM.confirm('Yes?',{'No':returnurl})
    
    if form.accepted:
        
        db(db.customerdependants.id == dependant_id).update(is_active = False,
                                                modified_on = common.getISTFormatCurrentLocatTime(),
                                                modified_by = auth.user.id)
        session.flash = 'Customer Dependant successfully deleted!'
        redirect(returnurl)
    
    elif form.errors:
        session.flash = "Error - deleting customer dependant" + str(formA.errors)
        
        
            
    return dict(form=form, dependant_name = dependant_name, customername=customer_name)

def delete_customer():
    
    customername = common.getstring(request.vars.customername)
    customerid = int(common.getid(request.vars.customerid))
    page = common.getpage1(request.vars.page)
    
    form = FORM.confirm('Yes?',{'No':URL('customer','list_customers',vars=dict(page=page))})
    
    if form.accepted:
        
        db(db.customer.id == customerid).update(is_active = False,
                                                modified_on = common.getISTFormatCurrentLocatTime(),
                                                modified_by = auth.user.id)
        session.flash = 'Customer successfully deleted!'
        redirect(URL('customer','list_customers',vars=dict(page=page)))
    
    elif form.errors:
        session.flash = "Error - deleting customer" + str(formA.errors)
        
        
            
    return dict(form=form,customername=customername)

def enroll_customer():
    
    page = common.getpage1(request.vars.page)
    
    customerid = int(common.getid(request.vars.customerid))
    
    customer = db(db.customer.id == customerid).select()
    providerid = int(common.getid(customer[0].providerid))
    customer_ref = common.getstring(customer[0].customer_ref)
    appointment_id  = common.getstring(customer[0].appointment_id)
    appointment_datetime = customer[0].appointment_datetime
    
    
    custobj = mdpcustomer.Customer(db)
    avars = {"customerid":customerid,"customer_ref":customer_ref}
    patobj  = json.loads(custobj.enroll_customer(avars))
    member = common.getkeyvalue(patobj, "fullname", "")
   
    if(patobj["result"] == "success"):
        appPath = current.globalenv["request"].folder
        mdpappt = mdpappointment.Appointment(db, providerid)
        docs = db((db.doctor.providerid == providerid) & 
                  (db.doctor.practice_owner == True) & 
                  (db.doctor.is_active == True)).select()
        
        if(len(docs)>0):
            doctorid = docs[0].id
            
        else:
            doctorid = 0
        
        db((db.customer.id == customerid) & (db.customer.is_active == True)).update(status = 'Enrolled')
        apptobj = json.loads(mdpappt.newappointment(patobj["primarypatientid"], patobj["patientid"], doctorid, 
                                        "", 
                                        appointment_datetime.strftime("%d/%m/%Y %H:%M"),
                                        30, 
                                        "Auto-Appointment created\nAppointment_ID: " + appointment_id + "\n" + customer[0].notes, 
                                        customer[0].cell, 
                                        appPath
                                        )
                             )
        #email Welcome Kit
        ret = mail.emailWelcomeKit(db,request,patobj["primarypatientid"],providerid)
        message = "Customer " + member + " has been successfully enrolled in MDP\n Welcome Kit has been sent to the registered email address"
        returnurl = URL('customer','list_customers',vars=dict(page=page))
    else:
        message = "ERROR enrolling Customer " + member + " in MDP"
        returnurl = URL('customer','list_customers',vars=dict(page=page))
        
    
    return dict(ret=ret, message=message, returnurl=returnurl)

def import_customers():

    strsql = "Truncate table importcustomers"
    db.executesql(strsql)
    db.commit()    

    count = 0
    form = SQLFORM.factory(
        Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
    )    

    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    

    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'



    error = ""

   
    
   
    
   
   
    
    message = ""
    if form.accepts(request,session,keepvalues=True):
        try:
            xcsvfile = request.vars.csvfile
            code = ""
            with open(xcsvfile, 'r') as csvfile:
                reader = csv.reader(csvfile)
                count = 0
                for row in reader:
                    count = count+1

                    if(count == 1):
                        continue

                    text = "";
                    
                    random.seed(int(time.time()) + 1)
                   
                    for j in range(0,4):
                        text += str(random.randint(0,9))                
                
                    customer_ref = row[2] + "_" + text if(row[2] != "") else text
                    
                    strsql = "INSERT INTO importcustomers(id, customer,customer_ref,fname,mname,lname,\
                    address1,address2,address3,city,st,pin,gender,cell,email,telephone,dob,enrolldate,\
                    status,providercode,companycode,regioncode,plancode,appointment_id, appointment_datetime,notes)\
                    VALUES("\

                    strsql = strsql + row[0] + ","\
                        + "TRIM('" + row[1] + "'),"\
                        + "TRIM('" + customer_ref + "'),"\
                        + "TRIM('" + row[3] + "'),"\
                        + "TRIM('" + row[4] + "'),"\
                        + "TRIM('" + row[5] + "'),"\
                        + "TRIM('" + row[6] + "'),"\
                        + "TRIM('" + row[7] + "'),"\
                        + "TRIM('" + row[8] + "'),"\
                        + "TRIM('" + row[9] + "'),"\
                        + "TRIM('" + row[10] + "'),"\
                        + "TRIM('" + row[11] + "'),"\
                        + "TRIM('" + row[12] + "'),"\
                        + "TRIM('" + row[13] + "'),"\
                        + "TRIM('" + row[14] + "'),"\
                        + "TRIM('" + row[15] + "'),"\
                        + "TRIM('" + row[16] + "'),"\
                        + "TRIM('" + row[17] + "'),"\
                        + "TRIM('" + row[18] + "'),"\
                        + "TRIM('" + row[19] + "'),"\
                        + "TRIM('" + row[20] + "'),"\
                        + "TRIM('" + row[21] + "'),"\
                        + "TRIM('" + row[22] + "'),"\
                        + "TRIM('" + row[23] + "'),"\
                        + "TRIM('" + row[24] + "'),"\
                        + "TRIM('" + row[25] + "')"\
                        +")"
                    #logger.loggerpms2.info("SQL\n" + strsql)
                    db.executesql(strsql)
                    db.commit()
                    
                   
                    
                    
                    strsql = "SELECT id FROM provider WHERE provider = '" + row[19] + "'"
                    ds = db.executesql(strsql)
                    providerid = int(ds[0][0])
                
                    #get company id and company code 
                    strsql = "SELECT id FROM company WHERE company = '" + row[20] + "'"
                    ds = db.executesql(strsql)
                    companyid = int(ds[0][0])
                    
                    #get regionid id 
                    strsql = "SELECT id FROM groupregion WHERE groupregion = '" + row[21] + "'"
                    ds = db.executesql(strsql)
                    regionid = int(ds[0][0])
                    
                
                    strsql = "SELECT id FROM hmoplan WHERE hmoplancode = '" + row[22] + "'"
                    ds = db.executesql(strsql)
                    planid = int(ds[0][0])   
                    
                    #update providerid, companyid, regionid, planid
                    strsql = "UPDATE importcustomers SET providerid = " + str(providerid) + ", companyid = " + str(companyid) + ", planid=" + str(planid) + ", regionid = " + str(regionid)  
                    strsql = strsql + " WHERE id = " + str(row[0])
                    db.executesql(strsql)
                    db.commit()                    

                    strsql = "INSERT INTO `customer`(\
                      `customer`,`customer_ref`,`fname`,`mname`,`lname`,`address1`,`address2`,`address3`,`city`,`st`,`pin`,\
                     `gender`,`telephone`,`cell`,`email`,`dob`,`status`,`providerid`,`companyid`,`regionid`,`planid`,`enrolldate`,`pin1`,`pin2`,`pin3`,\
                     `appointment_id`,`appointment_datetime`,`notes`,`is_active`,`created_on`,`created_by`,`modified_on`,`modified_by`)"
                    
            
                    strsql = strsql +" SELECT\
                    `importcustomers`.`customer`,\
                    `importcustomers`.`customer_ref`,\
                    `importcustomers`.`fname`,\
                    `importcustomers`.`mname`,\
                    `importcustomers`.`lname`,\
                    `importcustomers`.`address1`,\
                    `importcustomers`.`address2`,\
                    `importcustomers`.`address3`,\
                    `importcustomers`.`city`,\
                    `importcustomers`.`st`,\
                    `importcustomers`.`pin`,\
                    `importcustomers`.`gender`,\
                    `importcustomers`.`telephone`,\
                    `importcustomers`.`cell`,\
                    `importcustomers`.`email`,\
                    `importcustomers`.`dob`,\
                    `importcustomers`.`status`,\
                    `importcustomers`.`providerid`,\
                    `importcustomers`.`companyid`,\
                    `importcustomers`.`regionid`,\
                    `importcustomers`.`planid`,\
                    `importcustomers`.`enrolldate`,\
                    `importcustomers`.`pin1`,\
                    `importcustomers`.`pin2`,\
                    `importcustomers`.`pin3`,\
                    `importcustomers`.`appointment_id`,\
                    `importcustomers`.`appointment_datetime`,\
                    `importcustomers`.`notes`,\
                    'T',now(),1,now(),1\
                    FROM `importcustomers`"
                    db.executesql(strsql)
                    db.commit()
                    
                    c = db(db.customer.customer_ref == customer_ref).select()
                    customerid = c[0].id if(len(c)==1) else 0
                    providerid = c[0].providerid if(len(c)==1) else 0
                    appointment_id = c[0].appointment_id if(len(c)==1) else ""
                    
                    custobj = mdpcustomer.Customer(db)
                    avars = {"customerid":customerid,"customer_ref":customer_ref}
                    patobj  = json.loads(custobj.enroll_customer(avars))
                    member = common.getkeyvalue(patobj, "fullname", "") 
                    
                    if(patobj["result"] == "success"):
                        appPath = current.globalenv["request"].folder
                        mdpappt = mdpappointment.Appointment(db, providerid)
                        docs = db((db.doctor.providerid == providerid) & 
                                  (db.doctor.practice_owner == True) & 
                                  (db.doctor.is_active == True)).select()
                        
                        if(len(docs)>0):
                            doctorid = docs[0].id
                            
                        else:
                            doctorid = 0
                        
                        db((db.customer.id == customerid) & (db.customer.is_active == True)).update(status = 'Enrolled')
                        apptobj = json.loads(mdpappt.newappointment(patobj["primarypatientid"], patobj["patientid"], doctorid, 
                                                        "", 
                                                        (c[0].appointment_datetime).strftime("%d/%m/%Y %H:%M"),
                                                        30, 
                                                        "Auto-Appointment created\nAppointment_ID: " + c[0].appointment_id + "\n" + c[0].notes, 
                                                        c[0].cell, 
                                                        appPath
                                                        )
                                             )
                        #email Welcome Kit
                        ret = mail.emailWelcomeKit(db,request,patobj["primarypatientid"],providerid)
                        message += "Customer " + member + " has been successfully enrolled in MDP\n Welcome Kit has been sent to the registered email address\n"
                        
                    else:
                        message += "ERROR enrolling Customer " + member + " in MDP"
                                          
                    
                    


        except Exception as e:
            message = "Import Customers Exception Error - " + str(e)        

    count = 0 if(count==0) else count-1
    return dict(form=form, count=count,error=message)

def customer_report():
    from_date  = request.vars.from_date  #%d/%m/%Y
    to_date = request.vars.to_date
    
    
    from_date = request.vars.from_date  if(from_date != None) else \
        common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y")
    
    to_date = request.vars.to_date  if(to_date != None) else \
        common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y")
                                                                                            
    from_date = common.getdatefromstring(from_date,"%d/%m/%Y")
    to_date = common.getdatefromstring(to_date,"%d/%m/%Y")
    
    username = "Admin"
    formheader = "Customer Report"

    form = SQLFORM.factory(
        Field('fromdate',
              'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='From Date',default=from_date,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),        
        Field('todate',
              'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='To Date',default=to_date,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))
        
    )


    #submit = form.element('input',_type='submit')
    #submit['_style'] = 'display:none;'

    returnurl = URL('customer','list_customers',vars=dict(page=1))
    
    formA = None
    formB = None
    
    #display the top count
    query = (db.vw_customertopcount.id > 0)
    fields = (
        db.vw_customertopcount.company,
        db.vw_customertopcount.customer_count
    )

    headers={
        'vw_customertopcount.company':'Company',
        'vw_customertopcount.customer_count':'Customer Count'
    }
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, xml=False)    

    formA = SQLFORM.grid(query=query,

                         headers=headers,
                         fields=fields,
                         paginate=10,

                         exportclasses=exportlist,
                         searchable=False,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                         )
    
    if form.accepts(request,session,keepvalues=True):

        fromdate = form.vars.fromdate   #datetimeobject
        #fromdate = common.getstringfromdate(fromdate,"%d/%m/%Y")
        
        todate = form.vars.todate
        #todate = common.getstringfromdate(todate,"%d/%m/%Y")
        
        
      
        
        queryB = ((db.vw_customerdetailcount.id > 0) & (db.vw_customerdetailcount.enrolldate >= fromdate) 
                  & (db.vw_customerdetailcount.enrolldate <= todate))
        
        fieldsB = (
               db.vw_customerdetailcount.company,
               db.vw_customerdetailcount.enrolldate,
               db.vw_customerdetailcount.customer_count
               )      
        headersB={
          'vw_customerdetailcount.company':'Company',
          'vw_customerdetailcount.enrolldate':'Enrolled Date',
          'vw_customertopcount.customer_count':'Customer Count'
        }
        exportlistB = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, xml=False)    
        
        orderby = (db.vw_customerdetailcount.company, db.vw_customerdetailcount.enrolldate)
        formB = SQLFORM.grid(query=queryB,
                                
                                    headers=headersB,
                                    fields=fieldsB,
                                    paginate=10,
                                    orderby=orderby,
                                    exportclasses=exportlistB,
                                    searchable=False,
                                    create=False,
                                    deletable=False,
                                    editable=False,
                                    details=False,
                                    user_signature=False
                                    )
        
       
    elif form.errors:
        response.flash = "Error - Customer Report! " + str(form.errors)
        redirect(returnurl)    

    return dict(username=username,returnurl=returnurl,form=form,formheader=formheader,formA=formA,formB=formB)