# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
# checking for git 
#   xxxxx   YYYY
#ZZZZ
from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)

from decimal import Decimal
from gluon.tools import Mail
from string import Template

import urllib
import os
import datetime 
import re

#import sys
#sys.path.append('modules')
from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import mail
from applications.my_pms2.modules  import mdppreregister

from applications.my_pms2.modules import logger
#from gluon.contrib import mail
#from gluon.contrib import common  



#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################


def sitehasmoved():
    
    return dict()

def decrypt(encoded):
    
    result = ''
    for i in range(0, len(encoded)):
            result = result + chr(ord(encoded[i]) + 2)    
    
    return result

def showerror():

    errorheader = request.vars.errorheader
    errormssg   = request.vars.errormssg
    returnURL   = request.vars.returnURL
    
   
    
    return dict(errorheader=errorheader,errormssg=errormssg,returnURL=returnURL,buttontext='Return')

# IB 05292016
def register():
    formheader = "New Member"
    formA = SQLFORM.factory(
              Field('email', 'string', label='xEmail',requires=[IS_EMAIL(),IS_NOT_IN_DB(db, 'auth_user.password')]),
              Field('fname', 'string',  label='xFirst Name',requires=IS_NOT_EMPTY()),
              Field('lname', 'string',  label='xLast Name',requires=IS_NOT_EMPTY()),
              Field('username', 'string',  label='xUser Name',requires=IS_NOT_EMPTY()),
              Field('password', 'password',  label='xPassword',requires=[IS_NOT_EMPTY(),CRYPT(key=auth.settings.hmac_key)]),
          )        
    if formA.process().accepted:
        memberid = db.webmember.insert(**db.webmember._filter_fields(formA.vars))
        db(db.webmember.id == memberid).update(webmember = memberid,status = "Attempting", webenrollcompletedate=db.webmember.webenrolldate)
        redirect(URL('member','update_webmember_1', args=[memberid,companyid,company,name]))
        
    elif formA.errors:
        response.flash = 'form has errors'        

    return dict(formA=formA,formheader=formheader)    


def preregisterlookup():
  
    #form = SQLFORM.factory(
        #Field('cell', 'string',  widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _style='width:500px'), label='Cell',requires=[IS_NOT_EMPTY()])
    #)
    
    #cell = form.element('#no_table_cell')
    #cell['_class'] = 'form-control'
    #cell['_placeholder'] = 'Enter registered mobile number or email'
    
  
    errormssg = None
    preregid = 0
 
 
    # grid
    query = ((db.preregister.is_active==True))
    left =  [db.company.on(db.company.id==db.preregister.company)]    

    fields=(db.preregister.id, \
               db.preregister.fname, db.preregister.lname,db.preregister.city,db.preregister.pin,db.preregister.cell, db.preregister.oemail,\
               db.company.company)
    
    headers={
          'preregister.id':'ID',
          'preregister.fname':'First',
          'preregister.lname':'Last',
          'preregister.city':'City',
          'preregister.pin':'Pin',          
          'preregister.cell':'Cell',
          'preregister.oemail':'Email',
          'company.company':'Company'
      }    

    #exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, xml=False)
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
	
    links = [\
             lambda row: A('Dental Case Sheet',_href=URL("default","dentalcasesheet",vars=dict(preregid=row.preregister.id))),\
             lambda row: A('Email Dental Case Sheet',_href=URL("default","emaildentalcasesheet",vars=dict(preregid=row.preregister.id))),\
             lambda row: A('Update',_href=URL("default","preregisterupdate",vars=dict(preregid=row.preregister.id)))]
    
    orderby = ~(db.preregister.id)

    formA = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        left=left,
                        orderby=orderby,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )

    
    
    #if form.accepts(request,session,keepvalues=True):
        #preregs = db((db.preregister.cell.replace('-','').replace('/','').replace(' ','').replace('+','') == request.vars.cell.replace('-','').replace('/','').replace(' ','').replace('+',''))|(db.preregister.oemail == request.vars.cell)).select()
        #if(len(preregs) > 0):
            #preregid = int(common.getid(preregs[0].id))
            #redirect(URL('default','preregisterupdate',vars=dict(preregid=preregid)))
        #else:
            #errormssg = "Invalid value "
       
    #elif form.errors:
        #response.flash = 'form has errors'        
    errormssg=""
    returnurl = URL('default','index')
    return dict(formA=formA,returnurl=returnurl,errormssg=errormssg)


def dentalcasesheet():
    
    rows = db((db.preregister.id == common.getid(request.vars.preregid))).select()
    
    preregid = 0
    companyid = 0
    companys = 9
    pin = ""
    st = ""
    address = ""
    city = ""
    if(len(rows) > 0):
        preregid = common.getid(rows[0].id)
        companyid = common.getid(rows[0].company)
        companys = db(db.company.id == companyid).select()
    
    return dict(companys=companys, companyid = companyid, fname = rows[0].fname,lname=rows[0].lname,cell=rows[0].cell,company=rows[0].company,email=rows[0].oemail,\
                image=rows[0].image,desc=rows[0].description,tplans=rows[0].treatmentplandetails,address=address,city=city,st=st,pin=pin)

def emaildentalcasesheet():
    
    email = ""
    fname  = ""
    lname = ""
    
    preregid = common.getid(request.vars.preregid)
    rows = db(db.preregister.id == preregid).select()
    if(len(rows) > 0):
        email = common.getstring(rows[0].oemail)
        fname = common.getstring(rows[0].fname)
        lname = common.getstring(rows[0].lname)
        
    retval = mail.emailDentalCaseSheet(db, request, preregid, email)
    
    return dict(ret=retval, fname = fname, lname=lname,email=email )


def xpreregisterupdate():
    
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    cellno = ""
    cellno = common.getstring(request.vars.cellno)
    regs = db(db.preregister.cell == cellno).select()

    fname  = ""
    lname  = ""
    oemail = ""
    pemail = ""
    desc  = ""
    priority = "low"
    
    if(len(regs)>=1):
        fname = common.getstring(regs[0].fname)
        lname = common.getstring(regs[0].lname)
        oemail = common.getstring(regs[0].oemail)
        pemail = common.getstring(regs[0].pemail)
        
        desc = common.getstring(regs[0].description)
        priority = common.getstring(regs[0].priority).lower()
    
     
        
    db.preregister.fname.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control')
    db.preregister.lname.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control')
    db.preregister.oemail.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control')
    db.preregister.pemail.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control')
    db.preregister.cell.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control')
    db.preregister.description.widget = widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control')
    db.preregister.description.widget = widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_class='form-control')
    
    returnurl = URL('default','index')
    page=0
    
    crud.settings.update_next = URL('default','index')
    form = crud.update(db.preregister, regs[0].id,cast=int, message='Member Information Updated!')

    return dict(form=form,priority=priority,username=username,returnurl=returnurl,page=0) 



def ypreregisterimage():
    
    preregid = request.vars.preregid
    
    form = SQLFORM.factory(
        Field('title', 'string'),
        Field('image', 'upload', uploadfolder=os.path.join(request.folder,'uploads')))
    if form.process().accepted:
        response.flash = 'form accepted'
	db(db.preregister.id == preregid).update(image=form.vars.image)
	redirect(URL('default', 'preregisterupdate', vars=dict(preregid=preregid)))
    elif form.errors:
        response.flash = 'form has errors'
	      
	
    return dict(form=form)    



def download(): return response.download(request,db)
def link(): return response.download(request,db,attachment=False)
 
 
def preregisterimage():
    
    preregid = request.vars.preregid
    image_form = FORM(
            INPUT(_name='image_title',_type='text'),
            INPUT(_name='image_file',_type='file')
            )
	
    if image_form.accepts(request.vars,formname='image_form'):
	
	#image = db.preregister.image.store(image_form.vars.image_file.file)
	image = 'C:\\mydp\\xray1.jpg'
	redirect(URL('my_pms2', 'mdpapi','preupload', vars=dict(imagefile=image)))
	
	db(db.preregister.id == preregid).update(image = image)
	redirect(URL('default','preregisterupdate', vars=dict(preregid=preregid)))
    
    images = db(db.preregister.id == preregid).select(db.preregister.image)
    
    return dict(images=images)

    
def xpreregisterimage():
    
    preregid = request.vars.preregid

    regs = db(db.preregister.id == preregid).select()
    
   
    
    crud.settings.update_next = URL('default','preregisterupdate', vars=dict(preregid = preregid))
    crud.settings.showid     = True
    
    db.preregister.fname.default = regs[0].fname 
    db.preregister.lname.default = regs[0].lname
    db.preregister.pemail.default = regs[0].pemail
    db.preregister.oemail.default = regs[0].oemail
    db.preregister.cell.default = regs[0].cell
    db.preregister.description.default = regs[0].description
    db.preregister.treatmentplandetails.default = regs[0].treatmentplandetails
    db.preregister.priority.default = regs[0].priority
    db.preregister.image.default = regs[0].image
    db.preregister.company.default = regs[0].company
    
    form = crud.update(db.preregister,preregid,cast=int)
    
     
	   
 
    return dict(form=form,preregid=preregid)

def preregisterupdate():
    
    #cellno = ""
    #cellno = common.getstring(request.vars.cellno)
    #regs = db(db.preregister.cell == cellno).select()
    
    preregid = int(common.getid(request.vars.preregid))
    regs = db(db.preregister.id == preregid).select()
    
    fname  = ""
    lname  = ""
    oemail = ""
    pemail = ""
    desc  = ""
    priority = "low"
    imagex = ''
    cellno = ""
    company = 0
    
    if(len(regs)>=1):
        fname = common.getstring(regs[0].fname)
        lname = common.getstring(regs[0].lname)
        oemail = common.getstring(regs[0].oemail)
        pemail = common.getstring(regs[0].pemail)
        imagex = common.getstring(regs[0].image)
        cellno = common.getstring(regs[0].cell)
        company = common.getid(regs[0].company)
        desc = common.getstring(regs[0].description)
        priority = common.getstring(regs[0].priority).lower()
        tplans = common.getstring(regs[0].treatmentplandetails)
        
    rows = None
    if(company == 0):
        rows = db((db.company.is_active == True))._select(db.company.id)
    else:
        rows = db((db.company.is_active == True) & ((db.company.id == company)))._select(db.company.id)
        
    form = None
    
        
    form = SQLFORM.factory(
        Field('fname', 'string',  default=fname,label='First Name',requires=IS_NOT_EMPTY()),
        Field('lname', 'string',  default=lname, label='Last Name',requires=IS_NOT_EMPTY()),
        Field('oemail', 'string',  default=oemail, label='Office Email ID',requires=[IS_EMPTY_OR(IS_EMAIL())]),
        Field('pemail', 'string',  default=pemail, label='Personal Email ID'),
        Field('cell', 'string',  default = cellno, label='Cell'),
        Field('company',  'integer', default=company, represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'), \
              requires=IS_IN_DB(db(db.company.id.belongs(rows)),db.company.id, '%(name)s (%(company)s)')),
        Field('description','text', label='Description', default=desc),
        Field('treatmentplandetails','text',  default=tplans)
        
    )                    
 
        
    form.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    form.element('textarea[name=description]')['_rows'] = 5   
    form.element('textarea[name=description]')['_cols'] = 50
    form.element('textarea[name=description]')['_class'] = 'form-control'
    
    form.element('textarea[name=treatmentplandetails]')['_style'] = 'height:100px;line-height:1.0;'
    form.element('textarea[name=treatmentplandetails]')['_rows'] = 5   
    form.element('textarea[name=treatmentplandetails]')['_cols'] = 50
    form.element('textarea[name=treatmentplandetails]')['_class'] = 'form-control'
    
    fname = form.element('#no_table_fname')
    fname['_class'] = 'form-control'
    fname['_placeholder'] = 'Enter First Name'
    fname['_type'] = 'text'
    
    
    lname = form.element('#no_table_lname')
    lname['_class'] = 'form-control'
    lname['_placeholder'] = 'Enter Last Name'
    lname['_type'] = 'text'
    
    cellf = form.element('#no_table_cell')
    cellf['_class'] = 'form-control'
    cellf['_placeholder'] = 'Enter Mobile Number'
    
    oemail = form.element('#no_table_oemail')
    oemail['_class'] = 'form-control'
    oemail['_placeholder'] = 'Enter Mobile Number'

    pemail = form.element('#no_table_pemail')
    pemail['_class'] = 'form-control'
    pemail['_placeholder'] = 'Enter Mobile Number'
    
  
    
    if form.process().accepted:  
        memberid = db(db.preregister.id == preregid).update(fname = common.getstring(request.vars.fname),\
                                                          lname = common.getstring(request.vars.lname),\
	                                                  cell = common.getstring(request.vars.cell),\
                                                          oemail = common.getstring(request.vars.oemail),\
                                                          pemail = common.getstring(request.vars.pemail),\
                                                          company = common.getid(request.vars.company),\
                                                          description = common.getstring(request.vars.description),\
                                                          treatmentplandetails = common.getstring(request.vars.treatmentplandetails),\
                                                          priority = common.getstring(request.vars.priority)\
                                                          )
       
        redirect(URL('default','preregisterlookup'))

    elif form.errors:
        response.flash = 'form has errors'        

    return dict(form=form,priority=priority,imagex=imagex,preregid=preregid) 
    
    
def preregistersuccess():
    
    memberid = common.getstring(request.vars.memberid)
    fname = common.getstring(request.vars.fname)
    lname = common.getstring(request.vars.lname)
    cell = common.getstring(request.vars.cell)
    mssg = ""
    retVal = False;
    
    if(cell != "None"):
        if(cell.startswith("91") == True):
            cell = cell
        else:
            cell =  "91" + cell
        
        mssg = "Thank you for registering with My Dental Plan Healthcare Pvt Ltd for Dental Check-up. You will receive the details of date and time for the Dental check up through registered mobile number or to your email id shortly."
        retVal = mail.sendSMS2Email(db,cell,mssg)
    else:
        mssg = "Thank you for registering with My Dental Plan Healthcare Pvt Ltd for Dental Check-up. You will receive the details of date and time for the Dental check up through registered mobile number or to your email id shortly."
        retVal = False;
        
    return dict(memberid=memberid,fname=fname,lname=lname,cell=cell,retVal=retVal,mssg=mssg)



def preregister():
    
    providerid = int(common.getid(request.vars.providerid))
    provdict = common.getproviderfromid(db, providerid)
    providername = provdict["providername"]
    
    
   
    companycode = common.getstring(request.vars.companycode).lower()
    rows = None
    companyid = 0
    
    if(companycode == ""):
        rows = db((db.company.is_active == True) & ((db.company.company.lower() == 'ibm') | (db.company.company.lower() == "infy")| (db.company.company.lower() == "cgi"))).select(db.company.id)
    else:
        rows = db((db.company.is_active == True) & ((db.company.company.lower() == companycode))).select(db.company.id)
	
    if(len(rows)>0):
	companyid = int(common.getid(rows[0].id))
	
    form = None
        
    form = SQLFORM.factory(
        Field('employeeid', 'string',  label='Employee ID'),
        Field('fname', 'string',  label='First Name'),
        Field('lname', 'string',  label='Last Name'),
        Field('address', 'text',  label='Address'),
        Field('city', 'string',represent=lambda v, r: '' if v is None else v, default='--Select City',label='City',length=50,requires = IS_IN_SET(CITIES)),
        Field('st', 'string',represent=lambda v, r: '' if v is None else v, default='--Select State',label='State',length=50,requires = IS_IN_SET(STATES)),
        Field('pin', 'string',  label='Pin'),
        Field('oemail', 'string',  label='Office Email ID',requires=[IS_EMPTY_OR(IS_EMAIL()),IS_EMPTY_OR(IS_NOT_IN_DB(db, 'preregister.oemail'))]),
        Field('pemail', 'string',  label='Personal Email ID'),
        Field('company',  'integer', represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'), \
               default=companyid,requires=IS_IN_DB(db(db.company.id.belongs(rows)),db.company.id, '%(name)s (%(company)s)')),
        Field('cell', 'string',  label='Cell',requires=[IS_EMPTY_OR(IS_NOT_IN_DB(db, 'preregister.cell'))]),
        Field('treatmentplandetails', 'text',  label='Treatment Details'),
        Field('description', 'text',  label='Notes'),
        Field('gender','string',represent=lambda v, r: '' if v is None else v,default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
        Field('dob','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),
        
        Field('provider','integer',default=providerid),
        Field('priority','string',default='High'),
        Field('employeephoto','string',default=''),
        Field('image','string',default=''),
        
        
    )        
        
   
    form.element('textarea[name=address]')['_style'] = 'height:100px;line-height:1.0;'
    form.element('textarea[name=address]')['_rows'] = 5 
    form.element('textarea[name=address]')['_class'] = 'form-control'

    form.element('textarea[name=treatmentplandetails]')['_style'] = 'height:100px;line-height:1.0;'
    form.element('textarea[name=treatmentplandetails]')['_rows'] = 5 
    form.element('textarea[name=treatmentplandetails]')['_class'] = 'form-control'

    form.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    form.element('textarea[name=description]')['_rows'] = 5 
    form.element('textarea[name=description]')['_class'] = 'form-control'


    feid = form.element('#no_table_employeeid')
    feid['_class'] = 'form-control'
    feid['_placeholder'] = 'Enter Patient ID'

	
    fname = form.element('#no_table_fname')
    fname['_class'] = 'form-control'
    fname['_placeholder'] = 'Enter First Name'
    
    lname = form.element('#no_table_lname')
    lname['_class'] = 'form-control'
    lname['_placeholder'] = 'Enter Last Name'
    
    cell = form.element('#no_table_cell')
    cell['_class'] = 'form-control'
    cell['_placeholder'] = 'Enter Mobile Number'
    
    oemail = form.element('#no_table_oemail')
    oemail['_class'] = 'form-control'
    oemail['_placeholder'] = 'Enter Email'

    pemail = form.element('#no_table_pemail')
    pemail['_class'] = 'form-control'
    pemail['_placeholder'] = 'Enter Personal Email ID'

    city = form.element('#no_table_city')
    city['_class'] = 'form-control'
    
    st = form.element('#no_table_st')
    st['_class'] = 'form-control'

    pin = form.element('#no_table_pin')
    pin['_class'] = 'form-control'
    pin['_placeholder'] = 'Enter PIN'

    gen = form.element('#no_table_gender')
    gen['_class'] = 'form-control'

    dob = form.element('#no_table_dob')
    dob['_class'] = 'form-control'

    returnurl=URL('my_pms2', 'admin','providerhome')
    
    if form.process().accepted:
	
	obj = mdppreregister.Preregister(db, providerid, companycode)
	
       
        memberid = db.preregister.insert(**db.preregister._filter_fields(form.vars))
      
        redirect(URL('default', 'preregistersuccess', vars=dict(memberid=memberid,fname=form.vars.fname, lname=form.vars.lname,cell=form.vars.cell)))
        response.flash = 'Success'

    elif form.errors:
        response.flash = 'form has errors'        

    return dict(form=form,returnurl=returnurl) 




def login():
    return dict(form=auth.login())

def change_password():
    return dict(form=auth.change_password())

def member_resetpassword():
    props = db(db.urlproperties.id>0).select()

    server = props[0].mailserver + ":"  + props[0].mailserverport
    sender = props[0].mailsender
    login  = props[0].mailusername + ":" + props[0].mailpassword
    port = int(props[0].mailserverport)
    if((port != 25) & (port != 26)):
        tls = True
    else:
        tls = False

    if((props[0].mailusername == 'None')):
        login = None

    mail = auth.settings.mailer
    mail.settings.server = server
    mail.settings.sender = sender
    mail.settings.login =  login
    mail.settings.tls = tls

    auth.settings.reset_password_next = URL('default', 'member_login')  #IB 05292016
    auth.settings.request_reset_password_next = URL('default', 'member_login')  #IB 05292016
    
    form = auth.request_reset_password()

    username = common.getstring(request.vars.username)
    
    xusername =form.element('input',_id='auth_user_username')
    xusername['_value'] =  username
    xusername['_class'] = 'w3-input w3-border  w3-small'

    
        
    return dict(form=form)

def index():
    sitekey = None

    if(auth.user == None):
        sitekey = None
    else:
        if(auth.user.sitekey == ''):
            sitekey = None
        elif(auth.user.sitekey == None):
            sitekey = None
        else:
            sitekey = auth.user.sitekey

    if(auth.is_logged_in() & (sitekey == None)):
        redirect(URL('default','main'))    #IB 05292016
    elif (auth.is_logged_in() & (sitekey != None)):
        redirect(URL('default','user', args=['logout'], vars=dict(_next=URL('default','index')))) #IB 05292016
        #redirect(URL('default','user', args=['logout'], vars=dict(_next='/my_dentalplan/default/index'))) #IB 05292016
    else:
        #redirect(URL('my_dentalplan','default','user'))
        formlogin = auth.login()
        return dict(formlogin=formlogin)

    #auth.settings.login_onaccept.append(redirect_after_adminlogin)
    #auth.settings.login_onfail.append(login_adminerror)
    #formlogin = auth.login()
    #return dict(formlogin=formlogin)

def login_error(form):
    redirect(URL('default','member_login_error'))  #IB 05292016

def member_login_error():
    return dict()

def redirect_after_login(form):
    ret = auth.is_logged_in()
    if(ret == True):
        webmemberid = auth.user_id
        rows = db((db.webmember.webkey == auth.user.sitekey) & (db.webmember.email == auth.user.email)).select()
        if(len(rows)>0):
            webmemberid = rows[0].id
            db((db.webmember.id == webmemberid) & (db.webmember.status == 'No_Attempt') & (db.webmember.is_active==True)).update(status = 'Attempting')
            redirect(URL('member', 'update_webmember_0', args=[webmemberid]))  #IB 05292016
        else:
            raise HTTP(403,"Error in Login Redirection")

def member_login():
    session.logmode = 'login'
    formlogin = SQLFORM.factory(
                Field('username', 'string',  label='User Name',requires=IS_NOT_EMPTY()),
                Field('password', 'password',  label='Password',requires=[IS_NOT_EMPTY(),CRYPT(key=auth.settings.hmac_key)])
        )
    
    xusername = formlogin.element('input',_id='no_table_username')
    xusername['_class'] =  'form-control'
    xusername['_placeholder'] =  'Username'
    xusername['_autocomplete'] =  'off'
    
    xpassword = formlogin.element('input',_id='no_table_password')
    xpassword['_class'] =  'form-control'
    xpassword['_placeholder'] =  'Password'
    xpassword['_autocomplete'] =  'off'

    if formlogin.process().accepted:

        logger.loggerpms2.info("MyDentalPlan Login ==>>" + formlogin.vars.username + " " + formlogin.vars.password.password)
        user = auth.login_bare(formlogin.vars.username, formlogin.vars.password.password)
        
        
        if(user==False):
	    logger.loggerpms2.info("MyDentalPlan Login Error")
	    redirect(URL('default','member_login_error'))
        else:
	    webmemberid = auth.user_id
	    rows = db((db.webmember.webkey == auth.user.sitekey) & (db.webmember.email == auth.user.email)).select()
	    if(len(rows)>0):
		webmemberid = rows[0].id
		db((db.webmember.id == webmemberid) & (db.webmember.status == 'No_Attempt') & (db.webmember.is_active==True)).update(status = 'Attempting')
		redirect(URL('member', 'update_webmember_0', args=[webmemberid]))  
	    else:
		raise HTTP(403,"Error in Login Redirection")	    
	    
    elif formlogin.errors:
        logmssg = "Login Error " + str(formlogin.errors)
        response.flash = "Login Error " + str(formlogin.errors)
        
            
    return dict(formlogin = formlogin)
    
    
def xmember_login():

    session.logmode = 'login'
    sitekey = None
    if(len(request.args)>0):
        sitekey = request.args[0]

    auth.settings.login_next = URL('default','member_register') #IB 05292016
    #if request.env.http_referer:
        #redirect(URL('my_dentalplan','default','member_register'))
    auth.settings.login_onaccept.append(redirect_after_login)

    auth.settings.login_onfail.append(login_error)

    formlogin = auth.login()
    submit = formlogin.element('input',_type='submit')
    submit['_style'] = 'display:none;'
    return dict(formlogin=formlogin)

def verifymember(form):
    sitekey = form.vars.sitekey
    email   = form.vars.email
    
    # This block of code commented to remove ibm specific registration condition
    #if(sitekey == 'mY6mC0'):
        ## only for ibm domain
        #regexp = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@in.ibm.com'
        #if(re.match(regexp,email) == None):
            #redirect(URL('default','showerror',vars=dict(errorheader='Registration Error',errormssg='Please enter your official IBM Email ID only.', returnURL=URL('member_register'))))

    #check whether company exists
    rows = db((db.company.groupkey == sitekey) & (db.company.is_active == True)).select()
    if(len(rows) == 0):
        redirect(URL('default','member_register_error', args=['companynotregistered'])) #IB 05292016
    else:
        #check whether company-hmoplan rate defiend
        rows1 = db((db.companyhmoplanrate.company == int(rows[0].id)) & (db.companyhmoplanrate.is_active == True)).select()
        if(len(rows1) == 0):
            redirect(URL('default','member_register_error', args=['planrateerror'])) #IB 05292016

def member_register_error():
    if(len(request.args)>0):
        return dict(error = request.args[0])
    else:
        return dict(error = "registrationerror")

def member_register_success():
    ret = True
    if(request.args[0] == "True"):
        ret = True
    else:
        ret = False

    email = request.args[1]

    return dict(ret=ret, email=email)

def member_register():

    session.logmode = 'register'
    sitekey = None

    if(len(request.vars)>0):
        sitekey = request.vars["promocode"]
        db.auth_user.sitekey.default = sitekey
        #if(sitekey == 'vP8eQ6'): # IB12172016 - needs to be set to actual site key for CAMPUS
            #db.auth_user.password.default = 'password'
            #db.auth_user.password.default = 'password'
        
    region = common.getstring(request.vars.region)
    plan   = common.getstring(request.vars.plan)

    #if(len(request.args)>0):
    #    sitekey = request.args[0]
    #    db.auth_user.sitekey.default = sitekey

    db.auth_user.sitekey.writable = True
    db.auth_user.sitekey.readable = True
    db.auth_user.sitekey.label = "Promotion Code"
    db.auth_user.last_name.writable = False
    db.auth_user.last_name.readable = False
    db.auth_user.first_name.writable = False
    db.auth_user.first_name.readable = False
    db.auth_user.username.writable = True
    db.auth_user.username.readable = True
    db.auth_user.sitekey.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)

    db.auth_user.email.requires = (IS_EMAIL(error_message=auth.messages.invalid_email),
                                          IS_NOT_IN_DB(db, db.auth_user.email))

    
    # This block of code commented to remove ibm specific registration condition
    #if(sitekey == 'mY6mC0'):
        ## only for ibm domain
        #regexp = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@in.ibm.com'
        #db.auth_user.email.requires = (IS_EMAIL(error_message=auth.messages.invalid_email),
                                       #IS_NOT_IN_DB(db, db.auth_user.email),IS_MATCH(regexp,error_message='Please enter your official IBM Email ID only.'))
    #else:
        #db.auth_user.email.requires = (IS_EMAIL(error_message=auth.messages.invalid_email),
                                       #IS_NOT_IN_DB(db, db.auth_user.email))
        
    
    

    auth.settings.logged_url = None #URL('user', args='profile')

    form = auth.register()
    submit = form.element('input',_type='submit')
    submit['_style'] = 'display:none;'


    if form.process(onvalidation=verifymember).accepted:
        sitekey = form.vars.sitekey
        email   = form.vars.email
        cellno   = form.vars.registration_id
       
        
        source = common.getstring(request.vars.source)
        if ((sitekey == 'mc3b1q2o') & (source != "")):
            source = decrypt(source)
        

        db((db.auth_user.sitekey==sitekey) & (db.auth_user.email == email)).update(registration_key = '')


        # create new member
        rows = db(db.company.groupkey == sitekey).select()
        companyid = rows[0].id
        companycode = rows[0].company
        webid = db.webmember.insert(email=email,webkey=sitekey,status='No_Attempt',cell=cellno,webenrolldate = datetime.date.today(),company=companyid,provider=1,hmoplan=1,imported=True)
        db(db.webmember.id == webid).update(webmember = companycode + str(webid))
        
        #set default region and plan
        regionid = 0
        planid = 0
        
        rows=db((db.groupregion.groupregion == region)&(db.groupregion.is_active == True)).select()
        if(len(rows)==1):
            regionid = rows[0].id
            db(db.webmember.id == webid).update(groupregion = regionid)
            
            rows = db((db.companyhmoplanrate.groupregion==regionid) & (db.companyhmoplanrate.company==companyid) & \
                      (db.companyhmoplanrate.relation == 'Self') & (db.hmoplan.hmoplancode == plan)& (db.hmoplan.is_active == True)).\
                   select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
                          left=db.hmoplan.on(db.companyhmoplanrate.hmoplan == db.hmoplan.id),distinct=True)            

            
            if(len(rows)==1):
                planid = rows[0].id
                db(db.webmember.id == webid).update(hmoplan = planid)


        if(sitekey == 'vP8eQ6'):   #IB 12172016 : The key has to be replaced with CAMPUS Key
            redirect(URL('default','member_resetpassword',vars=dict(username=form.vars.username)))
        elif ((sitekey == 'mc3b1q2o') & (source == 'mydentalplan')):
            redirect(URL('default','member_login'))
        else:
            ret = mail.emailLoginDetails(db,request,sitekey,email)

        redirect(URL('default','member_register_success', args=[ret,email])) #IB 05292016



    return dict(form=form)



def HDFC_Callback():
    requestvars = request.vars
    webmemberid = 0

    responseheader = ''
    txamount = 0.00
    servicetax = 0.00
    swipecharge = 0.00
    total = 0.00
    fname = ''
    lname = ''
    MerchantRefNo =  request.vars.MerchantRefNo
    
    txdate = datetime.date.today()
    
    #MerchantRefNo = '5295_20160830_060732'  #TEST
    
    rows = db(db.paymenttxlog.txno == MerchantRefNo).select()
    if(len(rows)>0):
        webmemberid = int(rows[0].webmember)
        txdate = rows[0].txdatetime
    else:
        raise HTTP(403,"Error in Payment Callback " + MerchantRefNo)

    txamount = round(Decimal(rows[0].txamount,2))
    servicetax = round(Decimal(rows[0].servicetax),2)
    swipecharge = round(Decimal(rows[0].swipecharge),2)
    total = round(Decimal(rows[0].total),2)

    if(request.vars.ResponseCode == None):
        responsecode = '999'
    else:
        responsecode = request.vars.ResponseCode



    responsemssg = request.vars.ResponseMessage
    paymentid = request.vars.PaymentID
    paymentdate = request.vars.DateCreated
    if(request.vars.Amount == None):
        paymentamount = 0.00
    else:
        paymentamount = round(Decimal(request.vars.Amount),2)
    paymenttxid = request.vars.TransactionID
    accountid = request.vars.TransactionIDAccountID



    BillingName = request.vars.BillingName
    BillingAddress = request.vars.BillingAddress

    ##TEST
    #total = 124.56
    #responsecode = "0"
    #responsemssg = "Success"
    #paymentid ="Payment_ID"
    #paymentdate = "20015-06-20"
    #paymentamount = 124.56
    #paymenttxid = "Payment_TXID"
    #BillingName = "Billing_Name"
    #BillingAddress= "Billing_Addr"

    ##& (total == paymentamount)
    if((responsecode == '0') & (total == paymentamount)):
        #TEST - comment the update when testing
        db(db.webmember.id == webmemberid).update(status = 'Completed',webenrollcompletedate = datetime.date.today(),paid=True)
        db(db.webmemberdependants.webmember == webmemberid).update(paid=True)

        responseheader = "Thank you for your Payment!"
        #TEST - comment the update when testing
        db(db.paymenttxlog.txno == MerchantRefNo).update(responsecode=responsecode,
                                                         responsemssg=responsemssg,
                                                         paymentid=paymentid,
                                                         paymentdate=paymentdate,
                                                         paymentamount = paymentamount,
                                                         paymenttxid=paymenttxid,
                                                         accountid = accountid)
        props = db(db.urlproperties.id>0).select(db.urlproperties.autoemailreceipt)
        if(common.getbool(props[0].autoemailreceipt) == True):
            autoEmailReceipt(db,request,webmemberid, paymentid, paymenttxid, MerchantRefNo, BillingName, BillingAddress,txamount,servicetax,swipecharge,\
                            paymentamount,paymentdate,responsecode,responsemssg,txdate)       
    else:
        responseheader = "Payment Failure!"
        paymentamount = 'Error'

        if((responsemssg != '') & (responsemssg != None)):
            responsemssg = "Transaction Failure - " + responsemssg
        else:
            responsemssg = "Transaction Failure"

        if((responsecode != '') & (responsecode != None)):
            responsecode =  responsecode
        else:
            responsecode = "999"

        db(db.paymenttxlog.txno == MerchantRefNo).update(responsecode=responsecode,
                                                         responsemssg=responsemssg,
                                                         paymentid=paymentid,
                                                         paymentdate=paymentdate,
                                                         paymenttxid=paymenttxid,
                                                         accountid = accountid)
        #retrieve raw post data
        #xml = request.body.read()  # retrieve the raw POST data
        #if(len(xml)>0):
            #appPath = request.folder
            #rawdatafile = paymenttxid + "_" + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S") + ".log"
            #rawdatafile = os.path.join(appPath, 'private',rawdatafile)
            #flog = open(rawdatafile, 'w')
            #flog.write(xml)
            #flog.close()

    
    return dict(PaymentID=paymentid, TransactionID=paymenttxid, MerchantRefNo=MerchantRefNo, BillingName=BillingName,BillingAddress=BillingAddress,Amount=paymentamount,txamount=txamount,servicetax=servicetax,swipecharge=swipecharge,ResponseMessage=responsemssg,DateCreated=paymentdate,ResponseCode=responsecode,ResponseHeader=responseheader)


def xHDFC_Callback():
    requestvars = request.vars
    webmemberid = 0

    responseheader = ''
    txamount = 0.00
    servicetax = 0.00
    swipecharge = 0.00
    total = 0.00
    fname = ''
    lname = ''
    MerchantRefNo =  request.vars.MerchantRefNo

    #MerchantRefNo = '2_20150518_061600'  #TEST

    rows = db(db.paymenttxlog.txno == MerchantRefNo).select()
    if(len(rows)>0):
        webmemberid = int(rows[0].webmember)

    else:
        raise HTTP(403,"Error in Payment Callback " + MerchantRefNo)

    txamount = round(Decimal(rows[0].txamount,2))
    servicetax = round(Decimal(rows[0].servicetax),2)
    swipecharge = round(Decimal(rows[0].swipecharge),2)
    total = round(Decimal(rows[0].total),2)

    if(request.vars.ResponseCode == None):
        responsecode = '999'
    else:
        responsecode = request.vars.ResponseCode



    responsemssg = request.vars.ResponseMessage
    paymentid = request.vars.PaymentID
    paymentdate = request.vars.DateCreated
    if(request.vars.Amount == None):
        paymentamount = 0.00
    else:
        paymentamount = round(Decimal(request.vars.Amount),2)
    paymenttxid = request.vars.TransactionID
    accountid = request.vars.TransactionIDAccountID


    BillingName = request.vars.BillingName
    BillingAddress = request.vars.BillingAddress

    ##TEST
    #total = 124.56
    #responsecode = "0"
    #responsemssg = "Success"
    #paymentid ="Payment_ID"
    #paymentdate = "20015-06-20"
    #paymentamount = 124.56
    #paymenttxid = "Payment_TXID"
    #BillingName = "Billing_Name"
    #BillingAddress= "Billing_Addr"

    ##& (total == paymentamount)
    if((responsecode == '0') & (total == paymentamount)):
        #TEST - comment the update when testing
        db(db.webmember.id == webmemberid).update(status = 'Completed',webenrollcompletedate = datetime.date.today())
        responseheader = "Thank you for your Payment!"
        #TEST - comment the update when testing
        db(db.paymenttxlog.txno == MerchantRefNo).update(responsecode=responsecode,
                                                         responsemssg=responsemssg,
                                                         paymentid=paymentid,
                                                         paymentdate=paymentdate,
                                                         paymentamount = paymentamount,
                                                         paymenttxid=paymenttxid,
                                                         accountid = accountid)

    else:
        responseheader = "Payment Failure!"
        paymentamount = 'Error'

        if((responsemssg != '') & (responsemssg != None)):
            responsemssg = "Transaction Failure - " + responsemssg
        else:
            responsemssg = "Transaction Failure"

        if((responsecode != '') & (responsecode != None)):
            responsecode =  responsecode
        else:
            responsecode = "999"

        db(db.paymenttxlog.txno == MerchantRefNo).update(responsecode=responsecode,
                                                         responsemssg=responsemssg,
                                                         paymentid=paymentid,
                                                         paymentdate=paymentdate,
                                                         paymenttxid=paymenttxid,
                                                         accountid = accountid)
        #retrieve raw post data
        #xml = request.body.read()  # retrieve the raw POST data
        #if(len(xml)>0):
            #appPath = request.folder
            #rawdatafile = paymenttxid + "_" + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S") + ".log"
            #rawdatafile = os.path.join(appPath, 'private',rawdatafile)
            #flog = open(rawdatafile, 'w')
            #flog.write(xml)
            #flog.close()

    return dict(PaymentID=paymentid, TransactionID=paymenttxid, MerchantRefNo=MerchantRefNo, BillingName=BillingName,BillingAddress=BillingAddress,Amount=paymentamount,txamount=txamount,servicetax=servicetax,swipecharge=swipecharge,ResponseMessage=responsemssg,DateCreated=paymentdate,ResponseCode=responsecode,ResponseHeader=responseheader)

def autoEmailReceipt(db, request, webmemberid, paymentid, paymenttxid, MerchantRefNo, BillingName, BillingAddress,txamount,servicetax,swipecharge,\
                     paymentamount,paymentdate,responsecode,responsemssg,txdate):
 
    ret = mail.emailPaymentReceipt(db,request,webmemberid,
                                    paymentid,
                                    paymenttxid,
                                    MerchantRefNo,
                                    BillingName,
                                    BillingAddress,
                                    txamount,
                                    servicetax,
                                    swipecharge,
                                    paymentamount,
                                    paymentdate,
                                    responsecode,
                                    responsemssg,
                                    txdate
                                    )

    return ret

def emailpaymentreceipt():

    ret = False
    if(len(request.args)>0):

        paymentid = request.args[0]
        paymenttxid= request.args[1]
        MerchantRefNo= request.args[2]
        BillingName= request.args[3]
        BillingAddress= request.args[4]
        txamount= request.args[5]
        servicetax= request.args[6]
        swipecharge= request.args[7]
        paymentamount= request.args[8]
        paymentdate= request.args[9]
        responsecode= request.args[10]
        responsemssg = request.args[11]

        rows = db(db.paymenttxlog.txno == MerchantRefNo).select()
        if(len(rows) > 0):
            webmemberid = int(rows[0].webmember)
            txdate = rows[0].txdatetime
        else:
            raise HTTP(403,"Error in sending payment receipt by email: Member Not Found")

        ret = mail.emailPaymentReceipt(db,request,webmemberid,
                                        paymentid,
                                        paymenttxid,
                                        MerchantRefNo,
                                        BillingName,
                                        BillingAddress,
                                        txamount,
                                        servicetax,
                                        swipecharge,
                                        paymentamount,
                                        paymentdate,
                                        responsecode,
                                        responsemssg,
                                        txdate
                                        )
    else:
        raise HTTP(403,"Error in sending payment receipt by email: Error in payment receipt data")

    return dict(ret=ret,logmode="login")

def emailwelcomekit():
    membername = ""
    memberid = 0
    ret = False
    if(len(request.args)>0):

        memberid = int(request.args[0])
        rows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
        if(len(rows)>0):
            membername = rows[0].fname + " " + rows[0].lname
            providerid = int(rows[0].provider)
        else:
            raise HTTP(403,"Error in sending Welcome Kit by email: Invalid Patient Name")
        ret = mail.emailWelcomeKit(db,request,memberid,providerid)
        if(ret == False):
            raise HTTP(403,"Error in sending Welcome Kit by email: Error in sending email")
    else:
        raise HTTP(403,"Error in sending Welcome Kit by email: Invalid arguments")

    return dict(ret=ret, member = membername,page=common.getgridpage(request.vars)) #IB 05292016

def emailwelcomekit_0():
    #logger.loggerpms2.info("Enter email welcomekit_0")
    memberid = 0
    providerid = 0
    membername = ""
    returnurl = request.vars.returnurl
    ret = False
    if(len(request.args)>0):
        memberid = int(request.args[0])
        rows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
        if(len(rows)>0):
            patientmember = rows[0].patientmember
            providerid = int(rows[0].provider)
            membername = rows[0].fname + " " + rows[0].lname
	    #logger.loggerpms2.info("Before mail.emailwelcomkit")
            ret = mail.emailWelcomeKit(db,request,memberid,providerid)
	    #logger.loggerpms2.info("After mail.emailwelcomkit")
            if(ret == False):
                raise HTTP(403,"Error in sending Welcome Kit by email")

        else:
            raise HTTP(403,"Error in sending Welcome Kit by email: Invalid Patient Member")
    else:
        raise HTTP(403,"Error in sending Welcome Kit by email: No Patient Member")

    return dict(ret=ret, member = membername,page=common.getgridpage(request.vars),returnurl=returnurl)   #IB 05292016

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/request_reset_password
    http://..../[app]/default/user/reset_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    auth.settings.reset_password_next = URL('default', 'member_login')  #IB 05292016
    auth.settings.prevent_password_reset_attacks = True
    auth.settings.login_onaccept.append(redirect_after_adminlogin)
    auth.settings.login_onfail.append(login_adminerror)
    form = auth()
    xnew =form.element('input',_id='no_table_new_password')
    if(xnew != None):
        xnew['_class'] = 'w3-input w3-border  w3-small'    
    xver =form.element('input',_id='no_table_new_password2')
    if(xver != None):
        xver['_class'] = 'w3-input w3-border  w3-small'    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Reset Password'    
 
    return dict(form=form)


def download():
    if(len(request.args)>0):
        filename = request.args[0]
    return response.download(request, db)



@cache.action()
def xdownload():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@auth.requires_login()
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)

def test():
    return dict()

@auth.requires_membership('webadmin')
@auth.requires_login()
def urlproperties():

    crud.settings.keepvalues = True
    crud.settings.showid = True

    crud.settings.update_next = URL('default','index')
    crud.messages.submit_button = 'Submit'
    rows = db(db.urlproperties.id > 0).select()
    propid = int(rows[0].id)
    formA = crud.update(db.urlproperties, propid,cast=int, message='Properties Information Updated!')

    return dict(formA=formA)

def ibm():

    return dict()

def dps():

    return dict()

def termsandconditions():

    return dict()


def login_adminerror(form):
    return()

def redirect_after_adminlogin(form):
    ret = auth.is_logged_in()

    if(ret == True):
        webmemberid = auth.user_id
        rows = db((db.webmember.webkey == auth.user.sitekey) & (db.webmember.email == auth.user.email)).select()
        if((len(rows)>0) | (auth.user.sitekey != None)):
            redirect(URL('default', 'user')) #IB 05292016

        else:
            redirect(URL('default', 'main')) #IB 05292016

#IB 05292016
@auth.requires_login()
def logout():
    """ Logout handler """
    auth.settings.logout_next = URL('default','index')
    auth.logout()
    return dict()

#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def main():
    if(auth.is_logged_in()):
        username = auth.user.first_name + ' ' + auth.user.last_name
    else:
        raise HTTP(400, "Error: User not logged - main")
    
    # List of completed members
    formregistered = list_registeredmembers()
    formcompleted  = list_completedmembers()
    formenrolled   = list_enrolledmembers()
    returnurl = URL('default','main')
    return dict(username=username,returnurl=returnurl,formregistered=formregistered,formcompleted=formcompleted,formenrolled=formenrolled,
                total=common.gettotalmembers(db), newregistrations = common.getregisteredmembers(db,7,0), 
                pastregistrations = common.getregisteredmembers(db,7,None), completed = common.getcompletedmembers(db), enrolled =  common.getenrolledmembers(db),
                companies = common.getcompanies(db), providers = common.getproviders(db), plans = common.getplans(db),
                renewals30=common.getrenewals(db,0,30),renewals60=common.getrenewals(db,30,60),renewals90=common.getrenewals(db,60,90))


#IB 05292016
def list_registeredmembers():
    selectable = None

    fields=(db.webmember.fname,db.webmember.mname,db.webmember.lname,db.webmember.webmember,db.webmember.email,db.webmember.status,db.webmember.webdob,db.company.id,db.company.company,db.company.name)

    db.webmember.gender.readable = False
    db.webmember.gender.writeable = False
    db.webmember.address1.readable = False
    db.webmember.address1.writeable = False
    db.webmember.address2.readable = False
    db.webmember.address2.writeable = False
    db.webmember.address3.readable = False
    db.webmember.address3.writeable = False
    db.webmember.st.readable = False
    db.webmember.st.writeable = False
    db.webmember.city.readable = False
    db.webmember.city.writeable = False
    db.webmember.pin.readable = False
    db.webmember.pin.writeable = False
    db.webmember.telephone.readable = False
    db.webmember.telephone.writeable = False
    db.webmember.cell.readable = False
    db.webmember.cell.writeable = False
    db.webmember.email.readable = False
    db.webmember.email.writeable = False
    db.webmember.webpan.readable = False
    db.webmember.webpan.writeable = False
    db.webmember.webdob.readable = False
    db.webmember.webdob.writeable = False
    db.webmember.enrollstatus.readable = False
    db.webmember.enrollstatus.writeable = False
    db.webmember.image.readable = False
    db.webmember.image.writeable = False
    db.webmember.pin1.readable = False
    db.webmember.pin1.writeable = False
    db.webmember.pin2.readable = False
    db.webmember.pin2.writeable = False
    db.webmember.pin3.readable = False
    db.webmember.pin3.writeable = False
    db.webmember.webenrolldate.readable = False
    db.webmember.webenrolldate.writeable = False
    db.webmember.webenrollcompletedate.readable = False
    db.webmember.webenrollcompletedate.writeable = False
    db.webmember.imported.readable = False
    db.webmember.imported.writeable = False
    db.webmember.provider.readable = False
    db.webmember.provider.writeable = False
    db.webmember.groupregion.readable = False
    db.webmember.groupregion.writeable = False
    db.webmember.memberorder.readable = False
    db.webmember.memberorder.writeable = False


    db.company.name.readable = False
    db.company.contact.readable = False
    db.company.address1.readable = False
    db.company.address2.readable = False
    db.company.address3.readable = False
    db.company.st.readable = False
    db.company.city.readable = False
    db.company.pin.readable = False
    db.company.telephone.readable = False
    db.company.cell.readable = False
    db.company.fax.readable = False
    db.company.email.readable = False
    db.company.enrolleddate.readable = False
    db.company.terminationdate.readable = False
    db.company.renewaldate.readable = False
    db.company.capcycle.readable = False
    db.company.premcycle.readable = False
    db.company.adminfee.readable = False
    db.company.minsubscribers.readable = False
    db.company.maxsubscribers.readable = False
    db.company.minsubsage.readable = False
    db.company.maxsubsage.readable = False
    db.company.mindependantage.readable = False
    db.company.maxdependantage.readable = False
    db.company.maxdependantage.readable = False
    db.company.notes.readable = False
    db.company.commission.readable = False
    db.company.hmoplan.readable = False
    db.company.agent.readable = False
    db.company.groupkey.readable = False


    headers={'webmember.webmember':'Member ID',
             'webmember.fname':'First Name',
             'webmember.mname':'Middle Name',
             'webmember.lname':'Last Name',
             'webmember.webdob':'Date of Birth',
             'webmember.email':'Email',
             'company.company': 'Company',
             'webmember.status':'Status',
            }

    db.company.name.readable = False
    db.company.id.readable = False

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)

    links = [lambda row: A('Process',_href=URL("member","update_webmember_1",args=[row.webmember.id,row.company.id,row.company.company,row.company.name])), lambda row: A('Delete',_href=URL("member","delete_webmember",args=[row.webmember.id]))]


    query = ((db.webmember.is_active==True)&((db.webmember.status == 'No_Attempt')|(db.webmember.status == 'Attempting')))

    left =    [db.company.on(db.company.id==db.webmember.company)]

    orderby = ~(db.webmember.id)    

    form = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        left=left,
                        orderby=orderby,
                        selectable=selectable,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        paginate=5,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=False)



  

    return form

#IB 05292016
def list_completedmembers():
    selectable = None

    fields=(db.webmember.fname,db.webmember.mname,db.webmember.lname,db.webmember.webmember,db.webmember.email,db.webmember.status,db.webmember.webdob,db.company.id,db.company.company,db.company.name)

    db.webmember.gender.readable = False
    db.webmember.gender.writeable = False
    db.webmember.address1.readable = False
    db.webmember.address1.writeable = False
    db.webmember.address2.readable = False
    db.webmember.address2.writeable = False
    db.webmember.address3.readable = False
    db.webmember.address3.writeable = False
    db.webmember.st.readable = False
    db.webmember.st.writeable = False
    db.webmember.city.readable = False
    db.webmember.city.writeable = False
    db.webmember.pin.readable = False
    db.webmember.pin.writeable = False
    db.webmember.telephone.readable = False
    db.webmember.telephone.writeable = False
    db.webmember.cell.readable = False
    db.webmember.cell.writeable = False
    db.webmember.email.readable = False
    db.webmember.email.writeable = False
    db.webmember.webpan.readable = False
    db.webmember.webpan.writeable = False
    db.webmember.webdob.readable = False
    db.webmember.webdob.writeable = False
    db.webmember.enrollstatus.readable = False
    db.webmember.enrollstatus.writeable = False
    db.webmember.image.readable = False
    db.webmember.image.writeable = False
    db.webmember.pin1.readable = False
    db.webmember.pin1.writeable = False
    db.webmember.pin2.readable = False
    db.webmember.pin2.writeable = False
    db.webmember.pin3.readable = False
    db.webmember.pin3.writeable = False
    db.webmember.webenrolldate.readable = False
    db.webmember.webenrolldate.writeable = False
    db.webmember.webenrollcompletedate.readable = False
    db.webmember.webenrollcompletedate.writeable = False
    db.webmember.imported.readable = False
    db.webmember.imported.writeable = False
    db.webmember.provider.readable = False
    db.webmember.provider.writeable = False
    db.webmember.groupregion.readable = False
    db.webmember.groupregion.writeable = False
    db.webmember.memberorder.readable = False
    db.webmember.memberorder.writeable = False


    db.company.name.readable = False
    db.company.contact.readable = False
    db.company.address1.readable = False
    db.company.address2.readable = False
    db.company.address3.readable = False
    db.company.st.readable = False
    db.company.city.readable = False
    db.company.pin.readable = False
    db.company.telephone.readable = False
    db.company.cell.readable = False
    db.company.fax.readable = False
    db.company.email.readable = False
    db.company.enrolleddate.readable = False
    db.company.terminationdate.readable = False
    db.company.renewaldate.readable = False
    db.company.capcycle.readable = False
    db.company.premcycle.readable = False
    db.company.adminfee.readable = False
    db.company.minsubscribers.readable = False
    db.company.maxsubscribers.readable = False
    db.company.minsubsage.readable = False
    db.company.maxsubsage.readable = False
    db.company.mindependantage.readable = False
    db.company.maxdependantage.readable = False
    db.company.maxdependantage.readable = False
    db.company.notes.readable = False
    db.company.commission.readable = False
    db.company.hmoplan.readable = False
    db.company.agent.readable = False
    db.company.groupkey.readable = False


    headers={'webmember.webmember':'Member ID',
             'webmember.fname':'First Name',
             'webmember.mname':'Middle Name',
             'webmember.lname':'Last Name',
             'webmember.webdob':'Date of Birth',
             'webmember.email':'Email',
             'company.company': 'Company',
             'webmember.status':'Status',
            }

    db.company.name.readable = False
    db.company.id.readable = False

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)

    links = [lambda row: A('Process',_href=URL("member","update_webmember_1",args=[row.webmember.id,row.company.id,row.company.company,row.company.name])), lambda row: A('Delete',_href=URL("member","delete_webmember",args=[row.webmember.id]))]


    query = ((db.webmember.is_active==True)&(db.webmember.status == 'Completed'))

    left =    [db.company.on(db.company.id==db.webmember.company)]

    orderby = ~(db.webmember.id)    
    

    form = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        left=left,
                        orderby=orderby,
                        selectable=selectable,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        paginate=5,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=False)



  

    return form

#IB 05292016
def list_enrolledmembers():


    selectable = None

    fields=(db.patientmember.fname,db.patientmember.mname,db.patientmember.lname,db.patientmember.patientmember,db.company.company)
    db.patientmember.gender.readable = False
    db.patientmember.address1.readable = False
    db.patientmember.address2.readable = False
    db.patientmember.address3.readable = False
    db.patientmember.st.readable = False
    db.patientmember.city.readable = False
    db.patientmember.pin.readable = False
    db.patientmember.telephone.readable = False
    db.patientmember.cell.readable = False
    db.patientmember.email.readable = False
    db.patientmember.pan.readable = False
    db.patientmember.dob.readable = False
    db.patientmember.enrollmentdate.readable = False
    db.patientmember.terminationdate.readable = False
    db.patientmember.duedate.readable = False
    db.patientmember.premstartdt.readable = False
    db.patientmember.premenddt.readable = False
    db.patientmember.premium.readable = False
    db.patientmember.hmopatientmember.readable = False
    db.patientmember.image.readable = False
    db.patientmember.provider.readable = False
    db.patientmember.groupregion.readable = False
    db.patientmember.memberorder.readable = False


    db.company.name.readable = False
    db.company.contact.readable = False
    db.company.address1.readable = False
    db.company.address2.readable = False
    db.company.address3.readable = False
    db.company.st.readable = False
    db.company.city.readable = False
    db.company.pin.readable = False
    db.company.telephone.readable = False
    db.company.cell.readable = False
    db.company.fax.readable = False
    db.company.email.readable = False
    db.company.enrolleddate.readable = False
    db.company.terminationdate.readable = False
    db.company.renewaldate.readable = False
    db.company.capcycle.readable = False
    db.company.premcycle.readable = False
    db.company.adminfee.readable = False
    db.company.minsubscribers.readable = False
    db.company.maxsubscribers.readable = False
    db.company.minsubsage.readable = False
    db.company.maxsubsage.readable = False
    db.company.mindependantage.readable = False
    db.company.maxdependantage.readable = False
    db.company.maxdependantage.readable = False
    db.company.notes.readable = False
    db.company.commission.readable = False
    db.company.hmoplan.readable = False
    db.company.agent.readable = False
    db.company.groupkey.readable = False


    headers={'patientmember.fname':'First Name',
             'patientmember.mname':'Middle Name',
            'patientmember.lname':'Last Name',
            'patientmember.patientmember':'Member ID',
            'company.company':'Group Code'
            }




    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)

    links = [lambda row: A('Member Card',_href=URL("member","member_card",args=[row.patientmember.id])),lambda row: A('Welcome Kit',_href=URL("default","emailwelcomekit_0",args=[row.patientmember.id])),lambda row: A('Update',_href=URL("member","update_member",args=[row.patientmember.id])), lambda row: A('Delete',_href=URL("member","delete_member",args=[row.patientmember.id]))]

    query = ((db.patientmember.is_active==True)&(db.patientmember.status == 'Enrolled') & (db.patientmember.hmopatientmember == True))

    left =    [db.company.on(db.company.id==db.patientmember.company)]
    
    orderby = ~(db.patientmember.id)
    
    form = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        left=left,
                        orderby=orderby,
                        exportclasses=exportlist,
                        paginate=5,
                        links_in_grid=True,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )

    return form

