# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)

CRYPT = current.globalenv["CRYPT"]

import json
import string
import random


#import sys
#sys.path.append('modules')
from applications.my_pms2.modules  import account
from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import mail
from applications.my_pms2.modules  import states
from applications.my_pms2.modules  import mdpbank
from applications.my_pms2.modules  import mdpmedia
from applications.my_pms2.modules  import mdpCRM
from applications.my_pms2.modules  import logger


#from gluon.contrib import account
#from gluon.contrib import common #IB 05292016
#from gluon.contrib import mail

import datetime


def MDP_service_provider_agreement():
    
    return dict()




def emailconfirm():
    ret = False
    providername = None
    providerid = None
    if(len(request.args)>0):
        ret = bool(request.args[0])
        providername = request.args[2]
        providerid = int(request.args[1])

    return dict(ret=ret,providername=providername,providerid=providerid)

def assignedmembersconfirm():

    ret = False
    providername = None
    providerid = None
    if(len(request.args)>0):
        ret = bool(request.args[0])
        providername = request.args[2]
        providerid = int(request.args[1])

    return dict(ret=ret,providername=providername,providerid=providerid)

def randomGen():

    text = "";
    charset = "abcdefghijklmnopqrstuvwxyz0123456789"
    text += charset.charAt(Math.floor(Math.random() * charset.length));
    return text


def random_password(self):

    password = ''
    specials=r'!#$*?'
    for i in range(0,19):
        password += random.choice(string.lowercase)
        password += random.choice(string.uppercase)
        password += random.choice(string.digits)
        #password += random.choice(specials)
    return ''.join(random.sample(password,len(password)))

#users = db((db.auth_user.email==email) & (db.auth_user.sitekey == sitekey)).select()
    #if users:
	##logger.loggerpms2.info("before CRYPT_1")
	#my_crypt = CRYPT(key=auth.settings.hmac_key)
	##logger.loggerpms2.info("after CRYPT_1")
	#crypt_pass = my_crypt(str(password))[0]  
	##logger.loggerpms2.info("after CRYPT_PASS_1")
	#db(db.auth_user.id == users[0].id).update(first_name=providername,username=username,password=crypt_pass)
	#db.commit()
	##logger.loggerpms2.info("after UPDATE_1")  
def emailcredentials():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    providerid = int(common.getid(request.vars.providerid))    
    page = common.getpage1(request.vars.page)
    
    p = db((db.provider.id == providerid)&(db.provider.is_active == True)).select()
    sitekey = p[0].sitekey if(len(p)==1) else ""
    provider = p[0].provider if(len(p) == 1) else ""
    email = p[0].email if(len(p) == 1) else ""
    providername = p[0].providername if(len(p) == 1) else ""
    
    a = db((db.auth_user.email==email) & (db.auth_user.sitekey == sitekey)).select()
    username = a[0].username if(len(a) == 1) else None
    retval = False
    
    if(username == None):
	
	message = "Provider " + providername + " (" + provider + ") " + " is not registered with MDP"
    else:
	i = 0
	logger.loggerpms2.info("Email Credentidal before CRYPT_1")
	my_crypt = CRYPT(key=auth.settings.hmac_key)
	logger.loggerpms2.info("Email Credentidal after CRYPT_1")
	crypt_pass = my_crypt(str(provider))[0]  
	logger.loggerpms2.info("Email Credentidal after CRYPT_PASS_1")
	db(db.auth_user.id == a[0].id).update(username=username,password=crypt_pass)
	db.commit()
	logger.loggerpms2.info("Email Credentidal after UPDATE_1")  	
	retval = mail.emailProviderLoginDetails(db,request,sitekey,email,username,provider)
	message = "Provider " + providername + " (" + provider + ") " + "- Username and Password emailed to registered email " + email
    
    
    returnurl = URL('provider', 'list_provider', vars=dict(page=page))
    return dict(username=username, returnurl=returnurl, retval=retval, providername=providername,email=email,message=message)
    
    
def emailregister():
    username = auth.user.first_name + ' ' + auth.user.last_name
    providerid = int(common.getid(request.vars.providerid))
    
    r = db(db.provider.id == providerid).select()
    
    
    retval = mail.emailRegistrationLink(db, request, r[0].sitekey, r[0].email)
    returnurl = URL('provider', 'list_provider')
    return dict(username=username, returnurl=returnurl, retval=retval, providername=r[0].providername)


def emailpa():
    username = auth.user.first_name + ' ' + auth.user.last_name
    providerid = int(common.getid(request.vars.providerid))
    
    r = db(db.provider.id == providerid).select()
    
    
    retval = mail.emailPALink(db, request, r[0].sitekey, providerid, r[0].email)
    returnurl = URL('provider', 'list_provider')
    return dict(username=username, returnurl=returnurl, retval=retval, providername=r[0].providername)


def xviewprovideragreement():
    
    username = ""
    providerid = int(common.getstring(request.vars.providerid))
    
    prv = db(db.provider.id == providerid).select()
    
    pa_providername = prv[0].pa_providername
    pa_parent = prv[0].pa_providername
    pa_address = prv[0].pa_address
    pa_pan = prv[0].pa_pan
    pa_regno = prv[0].pa_regno
    pa_day = prv[0].pa_day
    pa_month = prv[0].pa_month
    pa_location = prv[0].pa_location
    pa_dob = prv[0].pa_dob
    pa_date = prv[0].pa_date
    pa_accepted = prv[0].pa_accepted
    pa_approved = prv[0].pa_approved
    pa_approvedby = prv[0].pa_approvedby
    pa_approvedon = prv[0].pa_approvedon
    
    pa_practicename = prv[0].practicename
    pa_practiceaddress = prv[0].p_address1
    pa_practicepin     = prv[0].p_pin
    
    
    form = SQLFORM.factory(
            Field('pa_providername','string',default=pa_providername),
            Field('pa_parent','string',default=pa_parent),
            Field('pa_address','string',default=pa_address),
            Field('pa_pan','string',default=pa_pan),
            Field('pa_regno','string',default=pa_regno),
            Field('pa_dob', 'date', default=pa_dob,requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            Field('pa_date', 'datetime',default=pa_date,requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
            
            Field('pa_day','string',default=pa_day),
            Field('pa_month','string',default=pa_month),
            Field('pa_location','string',default=pa_location),
            
            Field('pa_practicename','string',default=pa_practicename),
            Field('pa_practiceaddress','string',default=pa_practiceaddress),
            Field('pa_practicepin','string',default=pa_practicepin),
            
            Field('pa_accepted','boolean',default=pa_accepted, requires=IS_NOT_EMPTY(error_message="Please accept the agreement!")),
            Field('pa_approved','boolean',default=pa_approved),
            Field('pa_approvedby','integer',default=pa_approvedby),
            Field('pa_approvedon','datetime',default=datetime.date.today(),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y %H:%M'))))
            )
    
    
    if form.accepts(request,session,keepvalues=True):
        
        db.provider.update_or_insert(db.provider.id == providerid, \
                                     pa_approvedon = datetime.date.today(),\
                                     pa_approvedby=auth.user.id,
                                     pa_approved = common.getboolean(form.vars.pa_approved)
                                     )
        
        redirect(URL('provider','emailregister',vars=dict(providerid=providerid)))
    elif form.errors:
        i = 0
        
    returnurl=URL('default','logout')
    
    return dict(username=username,returnurl=returnurl,form=form,page=1)

def viewprovideragreement():
    isMDP = common.getboolean(common.getkeyvalue(request.vars,'isMDP','True'))
    username = ""
    providerid = int(common.getstring(request.vars.providerid))
    
    prv = db(db.provider.id == providerid).select()
    
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


    
    if form.accepts(request,session,keepvalues=True):
        
        id = db.provider.update_or_insert(db.provider.id == providerid, \
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
            redirect(URL('provider','emailregister',vars=dict(isMDP=isMDP,providerid=providerid)))
        else:
            session.flash = 'Agreement not approved!'
            i = 0
            
    elif form.errors:
        session.flash = 'Error in Agreement approval!'
        i = 0
        
    returnurl=URL('default','logout')
    
    return dict(username=username,returnurl=returnurl,form=form,page=1,todaydate=todaydate,xpa_providername=pa_providername)


def provideragreement():
    
    username = ""
    providerid = int(common.getstring(request.vars.providerid))
    isMDP = common.getboolean(common.getkeyvalue(request.vars,'isMDP','True'))
    prv = db(db.provider.id == providerid).select()
    
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
        
        id = db.provider.update_or_insert(db.provider.id == providerid, \
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


#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def list_provider():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Provider List"
    selectable = None
    page = common.getpage1(request.vars.page)
    isMDP = common.getboolean(common.getkeyvalue(request.vars,'isMDP','True'))
    
    
    ref_code = "PRV" if (common.getstring(request.vars.ref_code) == "") else request.vars.ref_code
    ref_id = 0 if (common.getstring(request.vars.ref_id) == "") else int(request.vars.ref_id)
    
    
    query = ((db.provider.is_active == True) & (db.provider.isMDP == isMDP))
   
	    
    
    fields=(db.provider.provider,
            db.provider.providername,
            db.provider.practicename,
            db.provider.address1,
            db.provider.address2,
            db.provider.address3,
            db.provider.city,
            db.provider.pin,
            db.provider.pa_pan,
            db.provider.registration,
            db.provider.cell,
            db.provider.email,
            db.provider.pa_accepted,
            db.provider.pa_approved)
    
    headers={
        'provider.provider':'Provider',
        'provider.providername':'Name',
        'provider.practicename' : 'Practice',
        'provider.address1' : 'address1',
        'provider.address2' : 'address2',
        'provider.address3' : 'address3',
        'provider.city':'City',
        'provider.pin' : 'PIN',
        'provider.pa_pan' : 'PAN',
        'provider.registration' : 'RegNo',
        'provider.cell' : 'Cell',
        'provider.emial' : 'Email',
        'provider.pa_accepted':'Acpt',
        'provider.pa_approved': 'Apr'
        }    
    #maxtextlengths = {'provider.email':50,'provider.cell':15,'provider.registration':20}
    db.provider.address1.searchable = False
    db.provider.address1.listable = False
    
    
 
    
	
    orderby = (~db.provider.id)
    exportlist = dict( csv=False,csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    links = [lambda row: A('Update',_href=URL("provider","update_provider",vars=dict(isMDP=isMDP,page=common.getgridpage(request.vars)),args=[row.id])),\
             lambda row: A('Clincs',_href=URL("clinic","list_clinic",vars=dict(isMDP=isMDP,page=common.getgridpage(request.vars),prev_ref_code="PRV", prev_ref_id =row.id,ref_code="PRV",ref_id=row.id))),
             lambda row: A('Logo',_href=URL("provider","new_logo",vars=dict(isMDP=isMDP,page=common.getgridpage(request.vars),prev_ref_code="PRV", prev_ref_id =row.id,ref_code="PRV",ref_id=row.id))),
             lambda row: A('Assigned',_href=URL("report","assignedmembersreportparam",vars=dict(isMDP=isMDP,providerid=row.id))),\
             #lambda row: A('Captiation Report',_href=URL("report","providercapitationreportparam",vars=dict(providerid=row.id))),\
             lambda row: A('Register',_href=URL("provider","emailregister",vars=dict(isMDP=isMDP,providerid=row.id))),\
             lambda row: A('EmailPA',_href=URL("provider","emailpa",vars=dict(isMDP=isMDP,providerid=row.id))),\
             lambda row: A('ApprovePA',_href=URL("provider","viewprovideragreement",vars=dict(isMDP=isMDP,providerid=row.id))),\
             lambda row: A('Login Details',_href=URL("provider","emailcredentials",vars=dict(isMDP=isMDP,providerid=row.id,page=page))),\
             lambda row: A('Bank',_href=URL("provider","providerbankdetails",vars=dict(isMDP=isMDP,page=common.getgridpage(request.vars)),args=[row.id])),
             lambda row: A('Delete',_href=URL("provider","delete_provider",vars=dict(isMDP=isMDP,providerid=row.id))),\
            ]


    
    form = SQLFORM.grid(query=query,
                 headers=headers,
                 fields=fields,
                 links=links,
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

    #searchable=lambda f, k: db.provider.providername.like("%" + k + "%") | db.provider.provider.like("%" + k + "%")

    #search_input = form.element('#w2p_keywords')
    #search_input.attributes.pop('_onfocus')   
  
   
    returnurl=URL('default','index')
    return dict(username=username,returnurl=returnurl,form=form, formheader=formheader,page=common.getgridpage(request.vars))

@auth.requires_login()
def list_assigned():



    providerid = session.providerid

    ## Display Co-Pay List for this plan
    fields=(db.webmember.webmember,db.webmember.fname,db.webmember.lname,db.webmember.webdob,db.webmember.status,db.company.company)

    headers={
        'webmember.fname': 'First Name',
        'webmember.lname': 'Last Name',
        'webmember.webdob':'DOB',
        'webmember.status':'Status',
        'webmember.webmember':'Member ID',
        'company.company':'Group(Company)',
             }

    exportlist =  dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)


    links = [lambda row: A('View',_href=URL("plan","view_plancopay",args=[row.copay.id,planid])),lambda row: A('Update',_href=URL("plan","update_plancopay",args=[row.copay.id,planid])), lambda row: A('Delete',_href=URL("plan","delete_plancopay",args=[row.copay.id,planid]))]
    links = None

    query =  ((db.webmember.provider == providerid) & (db.webmember.is_active==True) & (db.webmember.status == 'Enrolled'))

    left =    [db.company.on(db.company.id==db.webmember.company)]

    orderby = [db.company.company, db.webmember.status]
    ## called from menu
    form = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=None,
                             left=left,
                             orderby=orderby,
                             exportclasses=exportlist,
                             paginate=20,
                             links_in_grid=True,
                             searchable=True,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )

    return dict(form=form)

def getProviderCode():
    
    sql = "UPDATE providercount SET providercount = providercount + 1;"
    db.executesql(sql)
    db.commit()
    
    xrows = db(db.providercount.id >0).select()
    providercount = int(xrows[0].providercount)    

    providercode = "P" + str(providercount).zfill(5)
    return providercode

#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def create_provider():

    
    username = auth.user.first_name + ' ' + auth.user.last_name

    formheader = "New Provider"
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.create_onaccept = acceptOnCreate
    

    ## Add form -
    if((request.vars.sitekey == None)|(request.vars.sitekey == "")):
        db.provider.st.default='None'
    
        password = ''
        specials=r'!#$*?'
        for i in range(0,2):
            password += random.choice(string.lowercase)
            password += random.choice(string.uppercase)
            password += random.choice(string.digits)
            #password += random.choice(specials)
    
        text = password
    
    
        db.provider.sitekey.default = text
        db.provider.capitationytd.writable = False
        db.provider.captiationmtd.writable = False
        db.provider.assignedpatientmembers.writable = False
        db.provider.taxid.readable = True
        db.provider.taxid.writable = True
        db.provider.groupregion.default = 1
        db.provider.provider.default = getProviderCode()
	db.provider.isMDP.default = True
	
    db.provider.speciality.requires = IS_IN_DB(db((db.speciality_default.id>0)),db.speciality_default.id, '%(speciality)s')
    
    crud.settings.create_next = URL('provider','list_provider',vars=dict(page=common.getgridpage(request.vars)),args='')
    formA = crud.create(db.provider)  ## company Details entry form
    

   

    ## redirect on Cancel
    if session.create_provider_url == None:
        formA.add_button("cancel",URL('default','index', vars=dict(page=common.getgridpage(request.vars)),args=''))  ## return to home screen
    else:
        formA.add_button("cancel",session.create_company_url)     ## return cancel_returnURL
        session.create_company_url = None                         ## reset session key

    ## redirect on Items, with company ID and return URL
    provider = formA.vars.id
    isMDP = formA.vars.isMDP
    page=common.getgridpage(request.vars)
    returnurl = URL('provider','list_provider',vars=dict(isMDP=isMDP,page=1))
    
        
    return dict(username=username, returnurl=returnurl,formA=formA, formheader=formheader,page=page)

def acceptOnCreate(form):
    
    i = 0
    #new CRM Provider
    #{
	#"provider_id":<3308>
    #}          

    u = db(db.urlproperties.id > 0).select()
    crm = bool(common.getboolean(u[0].crm_integration)) if(len(u) >0) else False
    
    crm_avars = {}


    if(crm==True):
	crm_avars["provider_id"] = form.vars.id
	crmobj = mdpCRM.CRM(db)
	rsp = crmobj.mdp_crm_createprovider(crm_avars)
	
    return

def acceptOnUpdate(form):
    
    i = 0
    
    
    pan = form.vars.taxid
    regno = form.vars.registration
    isMDP = form.vars.isMDP
    
    db(db.provider.provider==form.vars.provider).update(pa_pan = pan, pa_regno = regno,isMDP=isMDP)
    
    i = 0
    #new CRM Provider
    #{
	#"provider_id":<3308>
    #}          

    u = db(db.urlproperties.id > 0).select()
    crm = bool(common.getboolean(u[0].crm_integration)) if(len(u) >0) else False
    
    crm_avars = {}


    if(crm==True):
	crm_avars["provider_id"] = form.vars.id
	crmobj = mdpCRM.CRM(db)
	rsp = crmobj.mdp_crm_updateprovider(crm_avars)
	

    return



#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def update_provider():
    

    username = auth.user.first_name + ' ' + auth.user.last_name
    


    formheader="Provider Maintenance"

    authuser = ""
    f = lambda name: name if ((name != "") & (name != None)) else ""
    authuser = f(auth.user.first_name)  + " " + f(auth.user.last_name)
    isMDP = common.getboolean(common.getkeyvalue(request.vars,'isMDP','True'))

    if(len(request.args)>0):   # called with providerid as URL params
        providerid = int(request.args[0])
        session.providerid = providerid
    elif (len(request.vars)>0): # called on grid next page, get the providerid from session.
	providerid = int(request.vars.providerid)
        #providerid = session.providerid



    text = ''
    rows = db(db.provider.id == providerid).select()
    if((rows[0].sitekey == '1234') | (rows[0].sitekey == '') | (rows[0].sitekey == None)):
        password = ''
        specials=r'!#$*?'
        for i in range(0,2):
            password += random.choice(string.lowercase)
            password += random.choice(string.uppercase)
            password += random.choice(string.digits)
            #password += random.choice(specials)

        text = password
    else:
        text = rows[0].sitekey

    YTD = account.capitationYTD(db,providerid)
    MTD = account.capitationMTD(db,providerid)
    PATS = account.assignedPatients(db,providerid)

    db(db.provider.id == providerid).update(capitationytd = YTD, captiationmtd = MTD, assignedpatientmembers = PATS, sitekey = text)

    crud.settings.update_onaccept = acceptOnUpdate
    crud.settings.detect_record_change = False
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('provider','update_provider',vars=dict(page=common.getgridpage(request.vars)),args=[providerid])

    db.provider.sitekey.writable = False
    db.provider.capitationytd.writable = False
    db.provider.captiationmtd.writable = False
    db.provider.assignedpatientmembers.writable = False
    db.provider.taxid.readable = True
    db.provider.taxid.writable = True
    db.provider.speciality.requires = IS_IN_DB(db((db.speciality_default.id>0)),db.speciality_default.id, '%(speciality)s')

    mediaid = int(common.getid(rows[0].logo_id if(len(rows) > 0) else 0))
    mediaurl = URL('my_dentalplan','media','media_download',args=[mediaid])         



    
    formA = crud.update(db.provider, providerid,cast=int)

    # Bank Details
    bank = db(db.providerbank.providerid == providerid).select()
    
    
    formBank = SQLFORM.factory(
              Field('bankname', 'string',  label='Patient', default =bank[0].bankname  if(len(bank) > 0) else "" ,writable=False),
              Field('bankbranch', 'string',  label='Patient', default =bank[0].bankbranch  if(len(bank) > 0) else "" ,writable=False),
              Field('bankaccountno', 'string',  label='Patient', default =bank[0].bankaccountno  if(len(bank) > 0) else "" ,writable=False),
                        
	      Field('bankaccounttype', 'string',  label='Patient', default =bank[0].bankaccounttype  if(len(bank) > 0) else "" ,writable=False),
			    
	      Field('bankmicrno', 'string',  label='Patient', default =bank[0].bankmicrno  if(len(bank) > 0) else "" ,writable=False),
	  
	      Field('bankifsccode', 'string',  label='Patient', default =bank[0].bankifsccode  if(len(bank) > 0) else "" ,writable=False)
              )
  
    #query = (db.providerbank.providerid == providerid)
    #fields = (db.providerbank.bankname,db.providerbank.bankbranch,db.providerbank.bankaccountno,db.providerbank.bankaccounttype,db.providerbank.bankmicrno,db.providerbank.bankifsccode)
    #headers={
              #'providerbank.bankname':'Bank',
              #'providerbank.bankbranch':'Branch',
              #'providerbank.bankaccountno':'Account No',
              #'providerbank.bankaccounttype':'Account Type',
              #'providerbank.bankmicrno':'MICR',
              #'providerbank.bankifsccode':'IFSC Code'
          #} 
    
    #formBank1 = SQLFORM.grid(query=query,
                     #headers=headers,
                     #fields=fields,
                     #links=None,
                     #paginate=10,
                     #maxtextlengths=None,
                     #orderby=None,
                     #exportclasses=None,
                     #links_in_grid=False,
                     #searchable=False,
                     #create=False,
                     #deletable=False,
                     #editable=False,
                     #details=False,
                     #user_signature=True
                    #)         

 

    ## redirect on Items, with PO ID and return URL
    page=common.getgridpage(request.vars)
    returnurl = URL('provider','list_provider',vars=dict(isMDP=isMDP,page=page))
    return dict(username=username,returnurl=returnurl,formA=formA, formBank=formBank,formheader=formheader,providerid=providerid,authuser=authuser,page=page,mediaurl=mediaurl)


@auth.requires_login()
def view_provider():

    formheader="Provider Data"
    providerid = int(request.args[0])

    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('provider','list_provider',args='')

    db.provider.provider.writable = False
    db.provider.sitekey.writable = False
    db.provider.capitationytd.writable = False
    db.provider.captiationmtd.writable = False
    db.provider.assignedpatientmembers.writable = False
    db.provider.taxid.writable = False
    db.provider.sitekey.writable = False
    db.provider.providername.writable = False
    db.provider.practicename.writable = False
    db.provider.address1.writable = False
    db.provider.address2.writable = False
    db.provider.address3.writable = False
    db.provider.city.writable = False
    db.provider.st.writable = False
    db.provider.pin.writable = False
    db.provider.cell.writable = False
    db.provider.telephone.writable = False
    db.provider.email.writable = False
    db.provider.fax.writable = False
    db.provider.enrolleddate.writable = False
    db.provider.assignedpatientmembers.writable = False
    db.provider.captguarantee.writable = False
    db.provider.schedulecapitation.writable = False
    db.provider.capitationytd.writable = False
    db.provider.captiationmtd.writable = False
    db.provider.languagesspoken.writable = False
    db.provider.specialization.writable = False

    formA = crud.update(db.provider, request.args[0],cast=int)

    formA.add_button("cancel",URL('provider','list_provider',args=''))     ## return cancel_returnURL


    ## Display Co-Pay List for this plan
    fields=(db.patientmember.patientmember,db.patientmember.fname,db.patientmember.lname,db.patientmember.dob,db.company.company)

    headers={
        'patientmember.fname': 'First Name',
        'patientmember.lname': 'Last Name',
        'patientmember.dob':'DOB',
        'patientmember.patientmember':'Member ID',
        'company.company':'Group(Company)',
             }

    exportlist =  dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)


    links = [lambda row: A('View',_href=URL("plan","view_plancopay",args=[row.copay.id,planid])),lambda row: A('Update',_href=URL("plan","update_plancopay",args=[row.copay.id,planid])), lambda row: A('Delete',_href=URL("plan","delete_plancopay",args=[row.copay.id,planid]))]
    links = None

    query =  (db.patientmember.provider == providerid) & (db.patientmember.is_active==True) & (db.patientmember.hmopatientmember==True)

    left =    [db.company.on(db.company.id==db.patientmember.company)]

    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             left=left,
                             exportclasses=exportlist,
                             links_in_grid=True,
                             searchable=False,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )



    ## redirect on Items, with PO ID and return URL
    return dict(formA=formA, formB=formB, formheader=formheader,providerid=providerid)

@auth.requires_login()
def delete_provider():
 
    name = None
    isMDP = common.getboolean(common.getkeyvalue(request.vars,'isMDP','True'))
    try:
        providerid = int(common.getid(request.vars.providerid))
        rows = db(db.provider.id == providerid).select()
        if(len(rows) == 0):
            raise HTTP(400,"Nothing to delete ")
        name = rows[0].providername
    except Exception, e:
        raise HTTP(400,e.message)

    form = FORM.confirm('Yes?',{'No':URL('provider','list_provider',vars=dict(isMDP=isMDP))})


    if form.accepted:
        db(db.provider.id == providerid).update(is_active=False)
        redirect(URL('provider','list_provider',vars=dict(isMDP=isMDP)))

    return dict(form=form,name=name)

@auth.requires_login()
def import_provider():

    if ((request.vars.csvfile != None) & (request.vars.csvfile != "")):
        # set values
        table = db[request.vars.table]
        file = request.vars.csvfile.file
        # import csv file
        table.import_from_csv_file(file)
        response.flash = 'Providers Uploaded'




    return dict()

def providerbankdetails():
    
    auth = current.auth
    
    username = auth.user.first_name + ' ' + auth.user.last_name
   
    formheader = "Bank Details"    

    authuser = ""
    f = lambda name: name if ((name != "") & (name != None)) else ""
    authuser = f(auth.user.first_name)  + " " + f(auth.user.last_name)
    isMDP = common.getboolean(common.getkeyvalue(request.vars,'isMDP','True'))

    page=common.getgridpage(request.vars)
    
    if(len(request.args)>0):   # called with providerid as URL params
	providerid = int(request.args[0])
	session.providerid = providerid
    elif (len(request.vars)>0): # called on grid next page, get the providerid from session.
	providerid = session.providerid    
	 

    
    provdict = common.getproviderfromid(db, providerid)
    providername = provdict["providername"]
    provider = provdict["provider"]
    
    returnurl = URL('provider','list_provider',vars=dict(isMDP=isMDP,page=page))
    ds = db((db.provider.id == providerid) & (db.provider.is_active == True)).select(db.provider.bankid)
    bankid = 0 if(len(ds)!=1) else common.getid(ds[0].bankid)
    obj = mdpbank.Bank(db)
    banks = json.loads(obj.get_account({"bankid":str(bankid)}))
    
    

    
    bankname = common.getkeyvalue(banks,"bankname","")
    bankbranch = common.getkeyvalue(banks,"bankbranch","")
    bankaccountname = common.getkeyvalue(banks,"bankaccountname","")
    bankaccountno = common.getkeyvalue(banks,"bankaccountno","")
    bankaccounttype = common.getkeyvalue(banks,"bankaccounttype","")
    bankmicrno = common.getkeyvalue(banks,"bankmicrno","")
    bankifsccode = common.getkeyvalue(banks,"bankifsccode","")
    address1 = common.getkeyvalue(banks,"address1","")
    address2 = common.getkeyvalue(banks,"address2","")
    address3 = common.getkeyvalue(banks,"address3","")
    city = common.getkeyvalue(banks,"city","--Select City--")
    st = common.getkeyvalue(banks,"st","--Select State--")
    pin = common.getkeyvalue(banks,"pin","")

    
    formA = SQLFORM.factory(
        Field('bankname','string',  default=bankname,label='Bank Name'),
        Field('bankbranch','string',  default=bankbranch,label='Bank Branch'),
        Field('bankaccountname','string',  default=bankaccountname,label='Bank Account'),
        Field('bankaccountno','string',  default=bankaccountno,label='Account No'),
        Field('bankaccounttype','string',  default=bankaccounttype,label='Account Type'),
        Field('bankmicrno','string',  default=bankmicrno,label='MICR'),
        Field('bankifsccode','string',  default=bankifsccode,label='IFS'),
        
        Field('address1','string',  default=address1,label='ADDR1'),
        Field('address2','string',  default=address2,label='ADDR2'),
        Field('address3','string',  default=address3,label='ADDR3'),
        Field('city', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '), default=city,label='City',requires = IS_EMPTY_OR(IS_IN_SET(states.CITIES))),
        Field('st', 'string', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control '), default=st,label='State',requires = IS_EMPTY_OR(IS_IN_SET(states.STATES))),
        Field('pin','string',  default=bankifsccode,label='PIN'),
    
    
    )
    
    if formA.accepts(request,session,keepvalues=True):
	
	
	requestobj = {}
	requestobj["bankid"] = str(bankid)
        requestobj["bankname"] = formA.vars.bankname
        requestobj["bankbranch"] = formA.vars.bankbranch
	requestobj["bankaccountname"] = formA.vars.bankaccountname
        requestobj["bankaccountno"] = formA.vars.bankaccountno
        requestobj["bankaccounttype"] = formA.vars.bankaccounttype
        requestobj["bankmicrno"] = formA.vars.bankmicrno
        requestobj["bankifsccode"] = formA.vars.bankifsccode
        
	requestobj["address1"] = formA.vars.address1
	requestobj["address2"] = formA.vars.address2
	requestobj["address3"] = formA.vars.address3
	requestobj["city"] = formA.vars.city
	requestobj["st"] = formA.vars.st
	requestobj["pin"] = formA.vars.pin
        
        if(bankid == 0):
	    rsp = json.loads(obj.new_account(requestobj))
	    result = common.getkeyvalue(rsp,"result","fail")
	    if(result == "success"):
		bankid = int(common.getkeyvalue(rsp,"bankid","0"))
		db(db.provider.id == providerid).update(bankid=bankid,
		                                        modified_on = common.getISTFormatCurrentLocatTime(),
		                                        modified_by =1 if(auth.user == None) else auth.user.id        
		                                        )
        else:
	    rsp = json.loads(obj.update_account(requestobj))

        redirect(returnurl)
        
    elif formA.errors:
        response.flash = 'Error adding a Provider Bank Details' + str(formA.errors)        
        
    return dict(username=username,formA=formA,formheader=formheader,page=page,returnurl=returnurl,\
                providerid=providerid,provider=provider,providername=providername,authuser=authuser)

def xproviderbankdetails():
    
    auth = current.auth
    
    username = auth.user.first_name + ' ' + auth.user.last_name
   
    formheader = "Bank Details"    

    authuser = ""
    f = lambda name: name if ((name != "") & (name != None)) else ""
    authuser = f(auth.user.first_name)  + " " + f(auth.user.last_name)


    page=common.getgridpage(request.vars)
    
    if(len(request.args)>0):   # called with providerid as URL params
	providerid = int(request.args[0])
	session.providerid = providerid
    elif (len(request.vars)>0): # called on grid next page, get the providerid from session.
	providerid = session.providerid    

    
    provdict = common.getproviderfromid(db, providerid)
    providername = provdict["providername"]
    provider = provdict["provider"]
    
    returnurl = URL('provider','list_provider',vars=dict(page=page))
    
    banks = db((db.providerbank.providerid == providerid) & (db.providerbank.is_active == True)).select()
    
    bankname = "" if(len(banks) == 0) else common.getstring(banks[0].bankname)
    bankbranch = "" if(len(banks) == 0) else common.getstring(banks[0].bankbranch)
    bankaccountno = "" if(len(banks) == 0) else common.getstring(banks[0].bankaccountno)
    bankaccounttype = "" if(len(banks) == 0) else common.getstring(banks[0].bankaccounttype)
    bankmicrno = "" if(len(banks) == 0) else common.getstring(banks[0].bankmicrno)
    bankifsccode = "" if(len(banks) == 0) else common.getstring(banks[0].bankifsccode)
    
    formA = SQLFORM.factory(
        Field('bankname','string',  default=bankname,label='Bank Name'),
        Field('bankbranch','string',  default=bankbranch,label='Bank Branch'),
        Field('bankaccountno','string',  default=bankaccountno,label='Account No'),
        Field('bankaccounttype','string',  default=bankaccounttype,label='Account Type'),
        Field('bankmicrno','string',  default=bankmicrno,label='MICR'),
        Field('bankifsccode','string',  default=bankifsccode,label='IFS')
    
    
    )
    
    if formA.accepts(request,session,keepvalues=True):
        bankname = formA.vars.bankname
        bankbranch = formA.vars.bankbranch
        bankaccountno = formA.vars.bankaccountno
        bankaccounttype = formA.vars.bankaccounttype
        bankmicrno = formA.vars.bankmicrno
        bankifsccode = formA.vars.bankifsccode
        
        if(len(banks) == 0):
            bankid = db.providerbank.insert(providerid = providerid,
                                            bankname=bankname,
                                            bankbranch=bankbranch,
                                            bankaccountno=bankaccountno,
                                            bankaccounttype=bankaccounttype,
                                            bankmicrno=bankmicrno,
                                            bankifsccode=bankifsccode,
                                            is_active = True,
                                            created_on = common.getISTFormatCurrentLocatTime(),
                                            created_by = 1 if(auth.user == None) else auth.user.id,
                                            modified_on = common.getISTFormatCurrentLocatTime(),
                                            modified_by =1 if(auth.user == None) else auth.user.id        
                                            )
            
            db(db.provider.id == providerid).update(bankid=bankid,
                                                    modified_on = common.getISTFormatCurrentLocatTime(),
                                                    modified_by =1 if(auth.user == None) else auth.user.id        
                                                    )
        else:
            db(db.providerbank.providerid == providerid).update(
                bankname=bankname,
                bankbranch=bankbranch,
                bankaccountno=bankaccountno,
                bankaccounttype=bankaccounttype,
                bankmicrno=bankmicrno,
                bankifsccode=bankifsccode,
                modified_on = common.getISTFormatCurrentLocatTime(),
                modified_by =1 if(auth.user == None) else auth.user.id        
            )
        
        redirect(returnurl)
        
    elif formA.errors:
        response.flash = 'Error adding a Provider Bank Details' + str(formA.errors)        
        
    return dict(username=username,formA=formA,formheader=formheader,page=page,returnurl=returnurl,\
                providerid=providerid,provider=provider,providername=providername,authuser=authuser)

@auth.requires_membership('webadmin')
@auth.requires_login()
def new_logo():
    page=common.getgridpage(request.vars)
    providerid = int(common.getkeyvalue(request.vars,"ref_id",0))
    isMDP = common.getboolean(common.getkeyvalue(request.vars,'isMDP','True'))

    ref_code = common.getkeyvalue(request.vars,"ref_code","PST")
    ref_id = common.getkeyvalue(request.vars,"ref_id",0)

    r = db(db.provider.id == ref_id).select()
    provider_code = r[0].provider if(len(r)>=0) else ""

    form = SQLFORM.factory(
        Field('provider','string',label='Provider Code', default=provider_code ),

        Field('title','string',label='Title'),
        Field('imagedate','date',default=datetime.date.today(), label='Image Date'),

        Field('imagedata','text', length=50e+6, label='Image Data')
    )    

    submit = form.element('input',_type='submit')
    submit['_value'] = 'Upload Image'    




    error = ""
    count = 0
    mediaurl = ""
    mediafile = ""
    mediatype = "image"
    mediaformat = "jpg"

    if form.accepts(request,session,keepvalues=True):

	try:

	    #upload image
	    if(len(request.vars.imagedata)>0):
		file_content = None
		file_content = request.vars.imagedata

		o = mdpmedia.Media(db, providerid, mediatype, mediaformat)
		j = {
		    "mediadata":file_content,

		    "title":request.vars.title,

		    "mediadate":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y"),
		    "appath":request.folder,
		    "mediatype":mediatype,
		    "mediaformat":mediaformat,

		    "ref_code":ref_code,
		    "ref_id":ref_id
		}

		x= json.loads(o.upload_media(j)) 

		mediaid = common.getkeyvalue(x,'mediaid',0)

		mediaurl = URL('my_dentalplan','media','media_download',\
		               args=[mediaid])  

		db(db.provider.id == providerid).update(logo_id = mediaid, logo_file = common.getkeyvalue(x,"mediafilename",""))


	except Exception as e:
	    error = "Upload Audio Exception Error - " + str(e)             
    elif form.errors:
	x = str(form.errors)
    else:
	i = 0    





    returnurl = URL('provider','update_provider',vars=dict(isMDP=isMDP,page=page,ref_code=ref_code,ref_id=ref_id,providerid=ref_id))
    return dict(form=form, pae=page,mediaurl=mediaurl,mediafile=mediafile,count=count,error=error,
                ref_code=ref_code,ref_id=ref_id,returnurl=returnurl) 
