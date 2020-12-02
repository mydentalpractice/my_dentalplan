# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)
import os
import json

import datetime
import time
import calendar
from datetime import timedelta
from decimal  import Decimal


import os
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
    username = auth.user.first_name + ' ' + auth.user.last_name   
    
    page = common.getpage(request.vars.page)
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
                                              vars=dict(page=page,customerid=row.id))),
             lambda row: A('Delete',_href=URL("customer","delete_customer",vars=dict(customerid = row.id,customername=row.customername)))
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

#this function helps the customer support to record the 
#customer profile details and appointment time from TPA
#Once all items are confirmed, the customer is enrolled
#@auth.requires_membership('webadmin')
#@auth.requires_login()
def new_customer():

    formheader = "Customer"
    username = auth.user.first_name + ' ' + auth.user.last_name

    rows = db(db.company.company == 'B2C_NG').select()
    companyid = rows[0]['company.id'] if(len(rows) > 0) else 0
    company = rows[0]['company'] if(len(rows) > 0) else ""
    name = rows[0]['name'] if(len(rows) > 0) else "" 
    
    planid = 1
    regionid = 1
    providerid = 1
   
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

    regions = db(db.groupregion.is_active == True).select()  #IB 07042016
    plans   = db((db.companyhmoplanrate.groupregion==regionid) & (db.companyhmoplanrate.company==companyid)).\
        select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
               left=db.hmoplan.on((db.companyhmoplanrate.hmoplan == db.hmoplan.id)&(db.hmoplan.is_active==True)))    
 
    returnurl = URL('customer', 'list_customers')

    return dict(formA=formA,username=username, returnurl=returnurl,formheader=formheader,regions=regions, plans=plans,page=1)

def update_customer():
    
    db = current.globalenv['db']
    
    formheader = "Customer"
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    customerid = int(common.getid(request.vars.customerid))
  
    page = common.getpage(request.vars.page)
    
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
            notes = formA.vars.notes
        ) 
        
        redirect(URL('customer','list_customers',vars=dict(page=page)))

    elif formA.errors:
        response.session.flash = "Error - updating customer" + str(formA.errors)

 

    regions = db(db.groupregion.is_active == True).select()  #IB 07042016
    plans   = db((db.companyhmoplanrate.groupregion==regionid) & (db.companyhmoplanrate.company==companyid)).\
        select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
               left=db.hmoplan.on((db.companyhmoplanrate.hmoplan == db.hmoplan.id)&(db.hmoplan.is_active==True)))    
 
    returnurl = URL('customer','list_customers',vars=dict(page=page))
    enrollcustomer = URL('customer','enroll_customer',vars=dict(page=page,customerid=customerid))

    return dict(formA=formA,username=username, returnurl=returnurl,enrollcustomer=enrollcustomer,formheader=formheader,regions=regions, plans=plans,regionid=regionid,planid=planid,page=1)
    
    
def delete_customer():
    
    customername = common.getstring(request.vars.customername)
    customerid = int(common.getid(request.vars.customerid))
    
    form = FORM.confirm('Yes?',{'No':URL('customer','list_customers')})
    
    if form.accepted:
        
        db(db.customer.id == customerid).update(is_active = False,
                                                modified_on = common.getISTFormatCurrentLocatTime(),
                                                modified_by = auth.user.id)
        session.flash = 'Customer successfully deleted!'
        redirect(URL('customer','list_customers'))
    
    elif form.errors:
        session.flash = "Error - deleting customer" + str(formA.errors)
        
        
            
    return dict(form=form,customername=customername)

def enroll_customer():
    
    page = request.vars.page
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
                                        "Auto-Appointment created\nAppointment_ID: " + appointment_id, 
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

