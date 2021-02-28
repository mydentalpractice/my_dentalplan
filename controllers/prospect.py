# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']
from gluon.tools import Crud
crud = Crud(db)

import string
import random
import json
import datetime

from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import mail
from applications.my_pms2.modules  import mdpuser
from applications.my_pms2.modules  import mdpprospect
from applications.my_pms2.modules  import mdpprovider
from applications.my_pms2.modules  import logger



def acceptOnUpdate(form):
    
    i = 0
    
    
    pan = form.vars.taxid
    regno = form.vars.registration
    
    db(db.prospect.provider==form.vars.provider).update(pa_pan = pan, pa_regno = regno)
    
    return

@auth.requires_membership('webadmin')
@auth.requires_login()
def list_prospect():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Prospect List"
    page = common.getpage1(request.vars.page)
    
    ref_code = "AGN" if (common.getstring(request.vars.ref_code) == "") else request.vars.ref_code
    ref_id = 0 if (common.getstring(request.vars.ref_id) == "") else int(request.vars.ref_id)
    
    
    query = ((db.prospect_ref.ref_code == ref_code)& (db.prospect_ref.ref_id == ref_id) & (db.prospect.is_active==True))
    
    fields=(db.prospect.provider,
            db.prospect.providername,
            db.prospect.practicename,
      
            db.prospect.city,
            db.prospect.pin,
            db.prospect.cell,
            db.prospect.email,
            db.prospect.pa_accepted,
            db.prospect.pa_approved)
    
    headers={
        'prospect.provider':'Prospect',
        'prospect.providername':'Name',
        'prospect.practicename' : 'Practice',
   
        'prospect.city':'City',
        'prospect.pin' : 'PIN',
        'prospect.cell' : 'Cell',
        'prospect.emial' : 'Email',
        'prospect.pa_accepted':'Acpt',
        'prospect.pa_approved': 'Apr'
        }    
    
    orderby = (db.prospect.provider)
    exportlist = dict( csv=False,csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    links = [lambda row: A('Update',_href=URL("prospect","update_prospect",vars=dict(page=common.getgridpage(request.vars)),args=[row.id])),
             lambda row: A('Clincs',_href=URL("clinic","list_clinic",vars=dict(page=common.getgridpage(request.vars),prev_ref_code=ref_code, prev_ref_id =ref_id,ref_code="PST",ref_id=row.id))),
             lambda row: A('EmailPA',_href=URL("prospect","emailpa",vars=dict(prospectid=row.id))),
             lambda row: A('ApprovePA',_href=URL("prospect","viewprovideragreement",vars=dict(prospectid=row.id))),
             lambda row: A('EnrollPA',_href=URL("prospect","enroll_prospect",vars=dict(prospectid=row.id))),
             lambda row: A('Delete',_href=URL("prospect","delete_prospect",vars=dict(prospectid=row.id)))
            ]


    left = [db.prospect.on(db.prospect.id==db.prospect_ref.prospect_id)]
    form = SQLFORM.grid(query=query,
                 headers=headers,
                 fields=fields,
                 links=links,
                 left=left,
                 orderby=orderby,
                 exportclasses=exportlist,
                 paginate=10,
                 links_in_grid=True,
                 searchable=True,
                 create=False,
                 deletable=False,
                 editable=False,
                 details=False,
                 user_signature=False
                )            

    returnurl=URL('default','index')
    return dict(username=username,returnurl=returnurl,form=form, formheader=formheader,page=common.getgridpage(request.vars))    


@auth.requires_membership('webadmin')
@auth.requires_login()
def update_prospect():


    username = auth.user.first_name + ' ' + auth.user.last_name



    formheader="Prospect Maintenance"

    authuser = ""
    f = lambda name: name if ((name != "") & (name != None)) else ""
    authuser = f(auth.user.first_name)  + " " + f(auth.user.last_name)


    if(len(request.args)>0):   # called with prospectid as URL params
        prospectid = int(request.args[0])
        session.prospectid = prospectid
    elif (len(request.vars)>0): # called on grid next page, get the prospectid from session.
        prospectid = session.prospectid



    text = ''
    bankid = 0
    rows = db(db.prospect.id == prospectid).select()
    if((rows[0].sitekey == '1234') | (rows[0].sitekey == '') | (rows[0].sitekey == None)):
        password = ''
        specials=r'!#$*?'
        for i in range(0,2):
            password += random.choice(string.lowercase)
            password += random.choice(string.uppercase)
            password += random.choice(string.digits)
            #password += random.choice(specials)

        text = password
        bankid = int(common.getid(rows[0].bankid))
    else:
        text = rows[0].sitekey
        bankid = int(common.getid(rows[0].bankid))
  
    db(db.prospect.id == prospectid).update( sitekey = text)





    crud.settings.update_onaccept = acceptOnUpdate
    crud.settings.detect_record_change = False
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('prospect','update_prospect',vars=dict(page=common.getgridpage(request.vars)),args=[prospectid])

    db.prospect.sitekey.writable = False
   
    db.prospect.taxid.readable = True
    db.prospect.taxid.writable = True
    db.prospect.speciality.requires = IS_IN_DB(db((db.speciality_default.id>0)),db.speciality_default.id, '%(speciality)s')






    formA = crud.update(db.prospect, prospectid,cast=int)

    # Bank Details
    bank = db(db.bank_details.id == bankid).select()


    formBank = SQLFORM.factory(
        Field('bankname', 'string',  label='Patient', default =bank[0].bankname  if(len(bank) > 0) else "" ,writable=False),
        Field('bankbranch', 'string',  label='Patient', default =bank[0].bankbranch  if(len(bank) > 0) else "" ,writable=False),
        Field('bankaccountno', 'string',  label='Patient', default =bank[0].bankaccountno  if(len(bank) > 0) else "" ,writable=False),

        Field('bankaccounttype', 'string',  label='Patient', default =bank[0].bankaccounttype  if(len(bank) > 0) else "" ,writable=False),

        Field('bankmicrno', 'string',  label='Patient', default =bank[0].bankmicrno  if(len(bank) > 0) else "" ,writable=False),

        Field('bankifsccode', 'string',  label='Patient', default =bank[0].bankifsccode  if(len(bank) > 0) else "" ,writable=False)
    )

   



    ## redirect on Items, with PO ID and return URL
    page=common.getgridpage(request.vars)
    returnurl = URL('prospect','list_prospect',vars=dict(page=page))
    return dict(username=username,returnurl=returnurl,formA=formA, formBank=formBank,formheader=formheader,prospectid=prospectid,authuser=authuser,page=page)

@auth.requires_membership('webadmin')
@auth.requires_login()
def delete_prospect():

    name = None
    try:
        prospectid = int(common.getid(request.vars.prospectid))
        rows = db(db.prospect.id == prospectid).select()
        if(len(rows) == 0):
            raise HTTP(400,"Nothing to delete ")
        name = rows[0].providername
    except Exception, e:
        raise HTTP(400,e.message)

    form = FORM.confirm('Yes?',{'No':URL('prospect','list_prospect')})


    if form.accepted:
        db(db.prospect.id == prospectid).update(is_active=False)
        redirect(URL('prospect','list_prospect'))

    return dict(form=form,name=name)

def emailpa():
    username = auth.user.first_name + ' ' + auth.user.last_name
    prospectid = int(common.getid(request.vars.prospectid))
    
    r = db(db.prospect.id == prospectid).select()
    
    
    retval = mail.emailProspectAgreementink(db, request, r[0].sitekey, prospectid, r[0].email)
    returnurl = URL('prospect', 'list_prospect')
    return dict(username=username, returnurl=returnurl, retval=retval, prospectname=r[0].providername)

def prospectagreement():
    
    username = ""
    prospectid = int(common.getstring(request.vars.prospectid))
    
    prv = db(db.prospect.id == prospectid).select()
    
    #if pa name is not null, then use it else providername
    pa_providername = common.getstring(prv[0].pa_providername) if  (common.getstring(prv[0].pa_providername) != "") else prv[0].providername

    #practice address        
    address=""

    if(common.getstring(prv[0].address1) != ""):
        address=address + prv[0].address1 + ","
        
    if(common.getstring(prv[0].address2) != ""):
        address=address + prv[0].address2 + ","
        
    if(common.getstring(prv[0].address3) != ""):
        address=address + prv[0].address3 + ","

    if(common.getstring(prv[0].city) != ""):
        address=address + prv[0].city + ","

    if(common.getstring(prv[0].st) != ""):
        address=address + prv[0].st + ","

    if(common.getstring(prv[0].pin) != ""):
        address=address + prv[0].pin + ","

    address = address.rstrip(',')
    pa_practicename = common.getstring(prv[0].pa_practicename) if  (common.getstring(prv[0].pa_practicename) != "") else  prv[0].practicename
    pa_practiceaddress = common.getstring(prv[0].pa_practiceaddress) if  (common.getstring(prv[0].pa_practiceaddress) != "") else  address
    pa_practicepin     =  common.getstring(prv[0].pa_practicepin) if  (common.getstring(prv[0].pa_practicepin) != "") else  prv[0].pin

    
    #residential address
    pa_address = prv[0].pa_address

    pa_parent = prv[0].pa_parent
    
    pa_pan = common.getstring(prv[0].pa_pan) if  (common.getstring(prv[0].pa_pan) != "") else prv[0].taxid
    
    pa_regno =common.getstring(prv[0].pa_regno) if  (common.getstring(prv[0].pa_regno) != "") else prv[0].registration
    pa_day = prv[0].pa_day
    pa_month = prv[0].pa_month
    
    pa_location = common.getstring(prv[0].pa_location) if  (common.getstring(prv[0].pa_location) != "") else prv[0].city
    
    pa_dob =  prv[0].pa_dob
    pa_date = prv[0].pa_date
    pa_accepted = prv[0].pa_accepted
    pa_approved = prv[0].pa_approved
    pa_approvedby = prv[0].pa_approvedby
    pa_approvedon = prv[0].pa_approvedon


    
    dttodaydate = datetime.date.today()
    todaydate = dttodaydate.strftime("%d/%m/%Y")
    
    form = SQLFORM.factory(
            Field('pa_providername','string',default=pa_providername,requires=IS_NOT_EMPTY()),
            Field('pa_parent','string',default=pa_parent,requires=IS_NOT_EMPTY()),
            Field('pa_address','text',default=pa_address,requires=IS_NOT_EMPTY()),
            Field('pa_pan','string',default=pa_pan,requires=IS_NOT_EMPTY()),
            Field('pa_regno','string',default=pa_regno,requires=IS_NOT_EMPTY()),
            Field('pa_dob', 'date', default=pa_dob,requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            Field('pa_date', 'datetime',default=pa_date,requires=IS_DATE(format=('%d/%m/%Y'),error_message="Please enter correct date in dd/mm/yyyy format!")),
            
            Field('pa_day','string',default=pa_day),
            Field('pa_month','string',default=pa_month),
            Field('pa_location','string',default=pa_location,requires=IS_NOT_EMPTY()),
            
            Field('pa_practicename','string',default=pa_practicename,requires=IS_NOT_EMPTY()),
            Field('pa_practiceaddress','text',default=pa_practiceaddress,requires=IS_NOT_EMPTY()),
            Field('pa_practicepin','string',default=pa_practicepin,requires=IS_NOT_EMPTY()),
            
            Field('pa_accepted','boolean',default=pa_accepted, requires=IS_NOT_EMPTY(error_message="Please check the box to accept the agreement!")),
            Field('pa_approved','boolean',default=pa_approved),
            Field('pa_approvedby','integer',default=pa_approvedby),
            Field('pa_approvedon','datetime',default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y %H:%M'))))
            )
    
    
    pa_date =  form.element('#no_table_pa_date')
    #pa_date['_class'] =  'input-group form-control form-control-inline date-picker'
    #pa_date['_data-date-format'] = 'dd/mm/yyyy'
    pa_date['_placeholder'] = 'dd/mm/yyyy'
    pa_date['_autocomplete'] = 'off'  

    
    
    pa_providername = form.element('#no_table_pa_providername')
    pa_providername['_class'] = 'w3-input'
    pa_providername['_style'] = 'border:0px'
    pa_providername['_placeholder'] = 'Enter Provider Name'
    pa_providername['_autocomplete'] = 'off'    

    pa_parent = form.element('#no_table_pa_parent')
    pa_parent['_class'] = 'w3-input'
    pa_parent['_style'] = 'border:0px'
    pa_parent['_placeholder'] = 'Enter Parent\'s Name'
    pa_parent['_autocomplete'] = 'off'    

    form.element('textarea[name=pa_address]')['_class'] = 'form-control'
    form.element('textarea[name=pa_address]')['_style'] = 'height:100px;line-height:1.0;padding:0px;'
    form.element('textarea[name=pa_address]')['_rows'] = 3
    form.element('textarea[name=pa_address]')['_placeholder'] = 'Enter Address'
    form.element('textarea[name=pa_address]')['_autocomplete'] = 'Off'

    #pa_address = form.element('#no_table_pa_address')
    #pa_address['_class'] = 'w3-input'
    #pa_address['_style'] = 'border:0px'
    #pa_address['_placeholder'] = 'Enter Address'
    #pa_address['_autocomplete'] = 'off'    

    pa_pan = form.element('#no_table_pa_pan')
    pa_pan['_class'] = 'w3-input'
    pa_pan['_style'] = 'border:0px'
    pa_pan['_placeholder'] = 'Enter PAN'
    pa_pan['_autocomplete'] = 'off'    

    pa_dob = form.element('#no_table_pa_dob')
    pa_dob['_class'] = 'w3-input'
    pa_dob['_style'] = 'border:0px'
    pa_dob['_placeholder'] = 'Enter DOB'
    pa_dob['_autocomplete'] = 'off'    

    pa_location = form.element('#no_table_pa_location')
    #pa_providername['_class'] = 'form-control'
    pa_location['_style'] = 'border:0px'
    pa_location['_placeholder'] = 'Enter City'
    pa_location['_autocomplete'] = 'off'    

    pa_regno = form.element('#no_table_pa_regno')
    pa_regno['_class'] = 'w3-input'
    pa_regno['_style'] = 'border:0px'
    pa_regno['_placeholder'] = 'Enter Registration No.'
    pa_regno['_autocomplete'] = 'off'    

    pa_practicename = form.element('#no_table_pa_practicename')
    pa_practicename['_class'] = 'w3-input'
    pa_practicename['_style'] = 'border:0px'
    pa_practicename['_placeholder'] = 'Enter Practice Name.'
    pa_practicename['_autocomplete'] = 'off'    


    form.element('textarea[name=pa_practiceaddress]')['_class'] = 'form-control'
    form.element('textarea[name=pa_practiceaddress]')['_style'] = 'height:100px;line-height:1.0;padding:0px;'
    form.element('textarea[name=pa_practiceaddress]')['_rows'] = 3
    form.element('textarea[name=pa_practiceaddress]')['_placeholder'] = 'Enter Practice Address'
    form.element('textarea[name=pa_practiceaddress]')['_autocomplete'] = 'Off'


    #pa_practiceaddress = form.element('#no_table_pa_practiceaddress')
    #pa_practiceaddress['_class'] = 'w3-input'
    #pa_practiceaddress['_style'] = 'border:0px'
    #pa_practiceaddress['_placeholder'] = 'Enter Practice Address.'
    #pa_practiceaddress['_autocomplete'] = 'off'    

    pa_practicepin = form.element('#no_table_pa_practicepin')
    pa_practicepin['_class'] = 'w3-input'
    pa_practicepin['_style'] = 'border:0px'
    pa_practicepin['_placeholder'] = 'Enter Practice Address.'
    pa_practicepin['_autocomplete'] = 'off'    


    
    if form.accepts(request,session,keepvalues=True):
        
        id = db.prospect.update_or_insert(db.prospect.id == prospectid, \
                                     pa_providername = common.getstring(form.vars.pa_providername),\
                                     pa_parent = common.getstring(form.vars.pa_parent),\
                                     pa_address = common.getstring(form.vars.pa_address),\
                                     pa_pan = common.getstring(form.vars.pa_pan),\
                                     pa_regno = common.getstring(form.vars.pa_regno),\
                                     registration = common.getstring(form.vars.pa_regno),\
                                     taxid = common.getstring(form.vars.pa_pan),\
                                     pa_day = common.getstring(form.vars.pa_day),\
                                     pa_month = common.getstring(form.vars.pa_month),\
                                     pa_location = common.getstring(form.vars.pa_location),\
                                     pa_dob = form.vars.pa_dob,\
                                     pa_date= form.vars.pa_date,\
                                     pa_practicename = common.getstring(form.vars.pa_practicename),\
                                     pa_practiceaddress = common.getstring(form.vars.pa_practiceaddress),\
                                     pa_practicepin = common.getstring(form.vars.pa_practicepin),\
                                     pa_approvedon= datetime.date.today(),\
                                     is_active = True,
                                     pa_accepted = common.getboolean(form.vars.pa_accepted),
                                     pa_approved = common.getboolean(form.vars.pa_approved)
                                     )
        
        #redirect(URL('default','logout'))
        session.flash = 'Agreement accepted!'
    elif form.errors:
        i = 0
        session.flash = 'Error in Agreement acceptance==' + str(form.errors)
        
    returnurl=URL('default','logout')
    
    return dict(username=username,returnurl=returnurl,form=form,page=1,todaydate=todaydate,xpa_providername=pa_providername)




def MDP_service_provider_agreement():
    
    return dict()


def emailregister():
    username = auth.user.first_name + ' ' + auth.user.last_name
    prospectid = int(common.getid(request.vars.prospectid))
    
    r = db((db.prospect.id == prospectid) & (db.prospect.is_active == True)).select()
    providername = "" if len(r) != 1 else r[0].providername + " " + r[0].practicename
    
    retval = mail.emailRegistrationLink(db, request, r[0].sitekey, r[0].email)
    returnurl = URL('prospect', 'list_prospect')
    return dict(username=username, returnurl=returnurl, retval=retval, providername=providername)

def viewprovideragreement():
    
    username = ""
    prospectid = int(common.getstring(request.vars.prospectid))
    
    prv = db((db.prospect.id == prospectid)&(db.prospect.is_active == True)).select()
    
    pa_providername = prv[0].pa_providername
        

    pa_address = prv[0].pa_address

    pa_parent = prv[0].pa_parent
    pa_pan = prv[0].pa_pan
    
    pa_regno =prv[0].pa_regno
    pa_day = prv[0].pa_day
    pa_month = prv[0].pa_month
    pa_location = prv[0].pa_location
    pa_dob =  prv[0].pa_dob
    pa_date = prv[0].pa_date
    pa_accepted = prv[0].pa_accepted
    pa_approved = prv[0].pa_approved
    pa_approvedby = prv[0].pa_approvedby
    pa_approvedon = prv[0].pa_approvedon

    pa_practicename = prv[0].pa_practicename
    pa_practiceaddress = prv[0].pa_practiceaddress
    pa_practicepin     = prv[0].pa_practicepin

    
    dttodaydate = datetime.date.today()
    todaydate = dttodaydate.strftime("%d/%m/%Y")
    
    form = SQLFORM.factory(
            Field('pa_providername','string',default=pa_providername),
            Field('pa_parent','string',default=pa_parent),
            Field('pa_address','text',default=pa_address),
            Field('pa_pan','string',default=pa_pan),
            Field('pa_regno','string',default=pa_regno),
            Field('pa_dob', 'date', default=pa_dob,requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            Field('pa_date', 'datetime',default=pa_date,requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            
            Field('pa_day','string',default="pa_day"),
            Field('pa_month','string',default="pa_month"),
            Field('pa_location','string',default=pa_location),
            
            Field('pa_practicename','string',default=pa_practicename,requires=IS_NOT_EMPTY()),
            Field('pa_practiceaddress','text',default=pa_practiceaddress,requires=IS_NOT_EMPTY()),
            Field('pa_practicepin','string',default=pa_practicepin,requires=IS_NOT_EMPTY()),
            
            Field('pa_accepted','boolean',default=pa_accepted),
            Field('pa_approved','boolean',default=pa_approved),
            Field('pa_approvedby','integer',default=pa_approvedby),
            Field('pa_approvedon','datetime',default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y %H:%M'))))
            )
    
    
    pa_date =  form.element('#no_table_pa_date')
    #pa_date['_class'] =  'input-group form-control form-control-inline date-picker'
    #pa_date['_data-date-format'] = 'dd/mm/yyyy'
    pa_date['_autocomplete'] = 'off'  

    
    
    pa_providername = form.element('#no_table_pa_providername')
    pa_providername['_class'] = 'w3-input'
    pa_providername['_style'] = 'border:0px'
    pa_providername['_placeholder'] = 'Enter Provider Name'
    pa_providername['_autocomplete'] = 'off'    

    pa_parent = form.element('#no_table_pa_parent')
    pa_parent['_class'] = 'w3-input'
    pa_parent['_style'] = 'border:0px'
    pa_parent['_placeholder'] = 'Enter Parent\'s Name'
    pa_parent['_autocomplete'] = 'off'    

    form.element('textarea[name=pa_address]')['_class'] = 'form-control'
    form.element('textarea[name=pa_address]')['_style'] = 'height:100px;line-height:1.0;'
    form.element('textarea[name=pa_address]')['_rows'] = 3
    form.element('textarea[name=pa_address]')['_placeholder'] = 'Enter Address'
    form.element('textarea[name=pa_address]')['_autocomplete'] = 'Off'

    #pa_address = form.element('#no_table_pa_address')
    #pa_address['_class'] = 'w3-input'
    #pa_address['_style'] = 'border:0px'
    #pa_address['_placeholder'] = 'Enter Address'
    #pa_address['_autocomplete'] = 'off'    

    pa_pan = form.element('#no_table_pa_pan')
    pa_pan['_class'] = 'w3-input'
    pa_pan['_style'] = 'border:0px'
    pa_pan['_placeholder'] = 'Enter PAN'
    pa_pan['_autocomplete'] = 'off'    

    pa_dob = form.element('#no_table_pa_dob')
    pa_dob['_class'] = 'w3-input'
    pa_dob['_style'] = 'border:0px'
    pa_dob['_placeholder'] = 'Enter DOB'
    pa_dob['_autocomplete'] = 'off'    

    pa_location = form.element('#no_table_pa_location')
    #pa_providername['_class'] = 'form-control'
    pa_location['_style'] = 'border:0px'
    pa_location['_placeholder'] = 'Enter City'
    pa_location['_autocomplete'] = 'off'    

    pa_regno = form.element('#no_table_pa_regno')
    pa_regno['_class'] = 'w3-input'
    pa_regno['_style'] = 'border:0px'
    pa_regno['_placeholder'] = 'Enter Registration No.'
    pa_regno['_autocomplete'] = 'off'    



    pa_practicename = form.element('#no_table_pa_practicename')
    pa_practicename['_class'] = 'w3-input'
    pa_practicename['_style'] = 'border:0px'
    pa_practicename['_placeholder'] = 'Enter Practice Name.'
    pa_practicename['_autocomplete'] = 'off'    

    form.element('textarea[name=pa_practiceaddress]')['_class'] = 'form-control'
    form.element('textarea[name=pa_practiceaddress]')['_style'] = 'height:100px;line-height:1.0;'
    form.element('textarea[name=pa_practiceaddress]')['_rows'] = 3
    form.element('textarea[name=pa_practiceaddress]')['_placeholder'] = 'Enter Practice Address'
    form.element('textarea[name=pa_practiceaddress]')['_autocomplete'] = 'Off'


    #pa_practiceaddress = form.element('#no_table_pa_practiceaddress')
    #pa_practiceaddress['_class'] = 'w3-input'
    #pa_practiceaddress['_style'] = 'border:0px'
    #pa_practiceaddress['_placeholder'] = 'Enter Practice Address.'
    #pa_practiceaddress['_autocomplete'] = 'off'    

    pa_practicepin = form.element('#no_table_pa_practicepin')
    pa_practicepin['_class'] = 'w3-input'
    pa_practicepin['_style'] = 'border:0px'
    pa_practicepin['_placeholder'] = 'Enter Practice Address.'
    pa_practicepin['_autocomplete'] = 'off'    

    returnurl = URL('prospect', 'list_prospect')
    
    if form.accepts(request,session,keepvalues=True):
        
        id = db.prospect.update_or_insert(db.prospect.id == prospectid, \
                                            pa_providername = common.getstring(form.vars.pa_providername),\
                                            pa_parent = common.getstring(form.vars.pa_parent),\
                                            pa_address = common.getstring(form.vars.pa_address),\
                                            pa_pan = common.getstring(form.vars.pa_pan),\
                                            pa_regno = common.getstring(form.vars.pa_regno),\
                                            registration = common.getstring(form.vars.pa_regno),\
                                            taxid = common.getstring(form.vars.pa_pan),\
                                            pa_day = common.getstring(form.vars.pa_day),\
                                            pa_month = common.getstring(form.vars.pa_month),\
                                            pa_location = common.getstring(form.vars.pa_location),\
                                            pa_dob = form.vars.pa_dob,\
                                            pa_date= form.vars.pa_date,\
                                            pa_practicename = common.getstring(form.vars.pa_practicename),\
                                            pa_practiceaddress = common.getstring(form.vars.pa_practiceaddress),\
                                            pa_practicepin = common.getstring(form.vars.pa_practicepin),\
                                            pa_approvedon= datetime.date.today(),\
                                            pa_approvedby= 1,\
                                            is_active = True,
                                            pa_accepted = common.getboolean(form.vars.pa_accepted),
                                            pa_approved = common.getboolean(form.vars.pa_approved)
                                            )        
        
        
      
        if(common.getboolean(form.vars.pa_approved == True))     :
            
            ppt = mdpprospect.Prospect(db)
            
            rspobj = json.loads(ppt.approve_prospect({"prospectid":prospectid}))
            
            redirect(returnurl)
            
        else:
            session.flash = 'Agreement not approved!'
            i = 0
            
    elif form.errors:
        session.flash = 'Error in Agreement approval!'
        i = 0
        
    returnurl = URL('prospect', 'list_prospect')
    
    return dict(username=username,returnurl=returnurl,form=form,page=1,todaydate=todaydate,xpa_providername=pa_providername)

def enroll_prospect():
    username = auth.user.first_name + ' ' + auth.user.last_name
    prospectid = int(common.getstring(request.vars.prospectid))
    s = db(db.prospect.id == prospectid).select(db.prospect.providername, db.prospect.practicename)
    providername = "" if(len(s)!=1) else s[0].providername
    practicename = "" if(len(s)!=1) else s[0].practicename
    
    ppt = mdpprospect.Prospect(db)
    rspobj = json.loads(ppt.get_prospect({"prospectid":str(prospectid)}))
    rspobj = json.loads(ppt.enroll_prospect(rspobj))
    
    providerid = int(common.getkeyvalue(rspobj,"providerid","0"))
    
    
    prv = mdpprovider.Provider(db,providerid)
    rspobj = prv.get_provider({"providerid":str(providerid)})
    rspobj = json.loads(rspobj)
    
    if(rspobj["result"] == "fail"):
        rspobj["error_message"] = rspobj["error_message"] + "\n" + "Error in Enroll Prospect - get Provider"
        return json.dumps(rspobj)
    
    sitekey = common.getkeyvalue(rspobj,"sitekey","")
    email = common.getkeyvalue(rspobj,"email","")
    username = common.getkeyvalue(rspobj,"provider","")
    password = common.getkeyvalue(rspobj,"provider","")

    usr = mdpuser.User(db, auth, rspobj["provider"], rspobj["provider"])
    rspobj = usr.provider_registration(request, rspobj["providername"], rspobj["sitekey"], rspobj["email"], 
                                      rspobj["cell"], 
                                      rspobj["registration"],
                                      rspobj["provider"],
                                      rspobj["provider"],
                                      "Provider")
    
    rspobj = json.loads(rspobj)
    returnurl = URL('prospect', 'list_prospect')
    retval = False
    error_message = ""

    if(rspobj["result"] == "success"):
        retval = True
        retval = mail.emailProviderLoginDetails(db,request,siteky,email,username,password)
       
    else:
        retval = False
        error_message = rspobj["error_message"]
    
    return dict(username=username,returnurl=returnurl,providername=providername, practicename=practicename,retval=retval,error_message=error_message)

