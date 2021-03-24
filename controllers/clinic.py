# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']
from gluon.tools import Crud
crud = Crud(db)

import string
import random
import json
import datetime
import os

from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import mail
from applications.my_pms2.modules  import mdpuser
from applications.my_pms2.modules  import mdpprospect
from applications.my_pms2.modules  import mdpprovider
from applications.my_pms2.modules  import mdpbank
from applications.my_pms2.modules  import mdpmedia
from applications.my_pms2.modules  import logger



@auth.requires_membership('webadmin')
@auth.requires_login()
def new_image():
    username = auth.user.first_name + ' ' + auth.user.last_name
    page=common.getgridpage(request.vars)
    formheader="New Clinic Image"
    
    authuser = ""
    f = lambda name: name if ((name != "") & (name != None)) else ""
    authuser = f(auth.user.first_name)  + " " + f(auth.user.last_name)

    prev_ref_code = request.vars.prev_ref_code
    prev_ref_id = request.vars.prev_ref_id
    
    ref_code = request.vars.ref_code
    ref_id = request.vars.ref_id
    clinics = db(db.clinic.id == ref_id).select()
    
    form = SQLFORM.factory(
        Field('clinicname','string',label='Clinic Name', default="" if(len(clinics) != 1) else clinics[0].name ),
        Field('browsefile','string',label='File Name',requires= IS_NOT_EMPTY()),
     
        Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY()),
        Field('title','string',label='Title'),
        Field('imagedate','date',default=datetime.date.today(), label='Image Date'),
        Field('description','text',label='Description')
    )    

    submit = form.element('input',_type='submit')
    submit['_value'] = 'Upload Image'    

    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'    
    
    xbrwfile = form.element('input',_id='no_table_browsefile')
    xbrwfile['_type'] =  'file'        
    xbrwfile['_class'] =  'w3-input w3-border w3-small'        

    
    error = ""
    count = 0
    mediaurl = ""
    mediafile = ""
    
    if form.accepts(request,session,keepvalues=True):
        try:
            filename = request.vars.csvfile
            browse = form.vars.browsefile.filename
            filePath = os.path.join("\\","media_files")
            filePath = os.path.join(filePath,browse)
     
            
           
            o = mdpmedia.Media(db, 0, 'image', 'jpg')

            j = {
                "filename":filePath,
                "title":"test",
                "tooth":"1",
                "quadrant":"1",
                "mediadate":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y"),
                "description":form.vars.description,
                "appath":request.folder
            }


            x= json.loads(o.upload_mediafile(j))            

            mediaid = common.getkeyvalue(x,'mediaid',0)

            db.dentalimage_ref.insert(
                
                ref_code = ref_code,
                ref_id = ref_id,
                media_id = mediaid
            
            )
            
            mediaurl = URL('my_dentalplan','media','media_download',\
                           args=[mediaid])



        except Exception as e:
            error = "Upload Image Media File Exception Error - " + str(e)        
    
    returnurl = URL('clinic','list_clinic_images',vars=dict(page=page,ref_code=ref_code,ref_id=ref_id,prev_ref_code=prev_ref_code,prev_ref_id=prev_ref_id))
    return dict(form=form, formheader=formheader,mediaurl=mediaurl,mediafile=mediafile,count=count,error=error,
                ref_code=ref_code,ref_id=ref_id,prev_ref_code=prev_ref_code,prev_ref_id=prev_ref_id,returnurl=returnurl) 

@auth.requires_membership('webadmin')
@auth.requires_login()
def view_image():
    username = auth.user.first_name + ' ' + auth.user.last_name
    page=common.getgridpage(request.vars)
    formheader="Clinic Image"
    
    authuser = ""
    f = lambda name: name if ((name != "") & (name != None)) else ""
    authuser = f(auth.user.first_name)  + " " + f(auth.user.last_name)

    prev_ref_code = request.vars.prev_ref_code
    prev_ref_id = request.vars.prev_ref_id
    
    ref_code = request.vars.ref_code
    ref_id = request.vars.ref_id
 
    
    imageid = 0 if((common.getstring(request.vars.imageid) == "")) else request.vars.imageid
    
    image = db((db.dentalimage.id == imageid) & (db.dentalimage.is_active == True)).select()
    
    
    mediaurl = URL('my_dentalplan','media','media_download',args=[imageid])
    
    
    formA = SQLFORM.factory(
        Field('Image Title','string', default="" if(len(image) != 1) else image[0].title),
        Field('Image date','date', default="" if(len(image) != 1) else image[0].imagedate),
    
    )    
    

    
    returnurl = URL('clinic','list_clinic_images',vars=dict(page=page,ref_code=ref_code,ref_id=ref_id,prev_ref_code=prev_ref_code,prev_ref_id=prev_ref_id))
    return dict(username=username,mediaurl=mediaurl,returnurl=returnurl,formA=formA, formheader=formheader,imageid=imageid,authuser=authuser,page=page)        
    


@auth.requires_membership('webadmin')
@auth.requires_login()
def list_clinic_images():
    
    logger.loggerpms2.info("Enter list_clinic_images")
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    page = common.getpage1(request.vars.page)

    prev_ref_code = "AGN" if (common.getstring(request.vars.prev_ref_code) == "") else request.vars.prev_ref_code
    prev_ref_id = 0 if (common.getstring(request.vars.prev_ref_id) == "") else int(request.vars.prev_ref_id)

    
    ref_code = "CLN" if (common.getstring(request.vars.ref_code) == "") else request.vars.ref_code
    ref_id = 0 if (common.getstring(request.vars.ref_id) == "") else int(request.vars.ref_id)

    clinics = db(db.clinic.id == ref_id).select()
    
    formheader = clinics[0].name + " Images" 
    
     
    query = ((db.dentalimage_ref.ref_code == ref_code)& (db.dentalimage_ref.ref_id == ref_id) & (db.dentalimage.is_active==True))
    
    logger.loggerpms2.info("List Clinic Images " + str(query))
    
    fields=(
                   
            db.dentalimage.id,
            db.dentalimage.title,
            db.dentalimage.image,
            db.dentalimage.imagedate,

            db.dentalimage.description
            )
    
    headers={
       
        
        'dentalimage.id':'ID',
        'dentalimage.title' : 'Title',
        'dentalimage.image' : 'Image',
        'dentalimage.imagedate' : 'Date',
        'dentalimage.description' : 'Description'
       
        }  
    
    left = [db.dentalimage.on(db.dentalimage.id==db.dentalimage_ref.media_id)]
    orderby = (db.dentalimage.imagedate)
    exportlist = dict( csv=False,csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    links = [
             lambda row: A('View',_href=URL("clinic","view_image",vars=dict(page=page,ref_code=ref_code,ref_id=ref_id,imageid=row.id)))
            ]

    
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

    returnurl = URL('clinic','list_clinic',vars=dict(page=page,ref_code=prev_ref_code,ref_id=prev_ref_id))
    return dict(username=username,returnurl=returnurl,form=form, formheader=formheader,page=common.getgridpage(request.vars),ref_code=ref_code,ref_id=ref_id,\
                prev_ref_code=prev_ref_code,prev_ref_id=prev_ref_id)    
    
    
@auth.requires_membership('webadmin')
@auth.requires_login()
def list_clinic():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Clinic List"
    page = common.getpage1(request.vars.page)

    prev_ref_code = "AGN" if (common.getstring(request.vars.prev_ref_code) == "") else request.vars.prev_ref_code
    prev_ref_id = 0 if (common.getstring(request.vars.prev_ref_id) == "") else int(request.vars.prev_ref_id)

    
    ref_code = "PRV" if (common.getstring(request.vars.ref_code) == "") else request.vars.ref_code
    ref_id = 0 if (common.getstring(request.vars.ref_id) == "") else int(request.vars.ref_id)
    
    
    query = ((db.clinic_ref.ref_code == ref_code)& (db.clinic_ref.ref_id == ref_id) & (db.clinic.is_active==True))
    
    fields=(
                   
            db.clinic.id,
            db.clinic.name,
            db.clinic.cell,
            db.clinic.address1,
            db.clinic.address2,
            db.clinic.address3,
            db.clinic.city,
            db.clinic.pin
            )
    
    headers={
       
        
        'clinic.name':'Name',
        'clinic.cell' : 'Cell',
        'clinic.address1' : 'Addr1',
        'clinic.address2' : 'Addr2',
        'clinic.address3' : 'Addr3',
        'clinic.city' : 'Cty',
        'clinic.pin' : 'Pin'
   
       
        }    
    left = [db.clinic.on(db.clinic.id==db.clinic_ref.clinic_id)]
    orderby = (db.clinic.clinic_ref)
    exportlist = dict( csv=False,csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    links = [
             lambda row: A('Update',_href=URL("clinic","update_clinic",vars=dict(page=page,ref_code=ref_code,ref_id=ref_id,clinicid=row.clinic.id))),
             lambda row: A('Bank Details',_href=URL("clinic","bank_clinic",vars=dict(page=page,ref_code=ref_code,ref_id=ref_id,clinicid=row.clinic.id))),
             lambda row: A('Clinic Images',_href=URL("clinic","list_clinic_images",vars=dict(page=page,ref_code="CLN",ref_id=row.clinic.id,prev_ref_code=ref_code,prev_ref_id=ref_id))),
             lambda row: A('Delete',_href=URL("clinic","delete_clinic",vars=dict(page=page,ref_code=ref_code,ref_id=ref_id,clinicid=row.clinic.id)))
            ]

    
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

    returnurl = URL('prospect','list_prospect',vars=dict(page=page,ref_code=prev_ref_code,ref_id=prev_ref_id))
    return dict(username=username,returnurl=returnurl,form=form, formheader=formheader,page=common.getgridpage(request.vars),ref_code=ref_code,ref_id=ref_id,\
                prev_ref_code=prev_ref_code,prev_ref_id=prev_ref_id)    

@auth.requires_membership('webadmin')
@auth.requires_login()
def update_clinic():
    username = auth.user.first_name + ' ' + auth.user.last_name
    page=common.getgridpage(request.vars)
    formheader="ClinicMaintenance"
    
    authuser = ""
    f = lambda name: name if ((name != "") & (name != None)) else ""
    authuser = f(auth.user.first_name)  + " " + f(auth.user.last_name)


    ref_code = request.vars.ref_code
    ref_id = request.vars.ref_id
 
    
    clinicid = 0 if((common.getstring(request.vars.clinicid) == "")) else request.vars.clinicid
    
    clinics = db((db.clinic.id == clinicid) & (db.clinic.is_active == True)).select()
    
    
 
    crud.settings.detect_record_change = False
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('clinic','update_clinic',vars=dict(page=common.getgridpage(request.vars),clinicid=clinicid,ref_code=ref_code,ref_id=ref_id))

    db.clinic.name.default = "" if(len(clinics) != 1 ) else common.getstring(clinics[0].name)
    

    formA = crud.update(db.clinic, clinicid,cast=int)    
    
    returnurl = URL('clinic','list_clinic',vars=dict(page=page,ref_code=ref_code,ref_id=ref_id))
    return dict(username=username,returnurl=returnurl,formA=formA, formheader=formheader,clinicid=clinicid,authuser=authuser,page=page)    

def acceptOnCreate(form):
    
    clinicid = int(form.vars.id)
    ref_code = session.ref_code
    ref_id = int(session.ref_id)
    
    db.clinic_ref.insert(ref_code=ref_code,ref_id=ref_id,clinic_id=clinicid)
    redirect(URL('clinic','update_clinic',vars=dict(page=1,clinicid = clinicid,ref_code=ref_code,ref_id=ref_id)))
    
    
    return


@auth.requires_membership('webadmin')
@auth.requires_login()
def new_clinic():

    username = auth.user.first_name + ' ' + auth.user.last_name
    
    formheader = "New Clinic"
    
    ## Add form - 
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.create_onaccept = acceptOnCreate
   
    ref_code = request.vars.ref_code
    ref_id = request.vars.ref_id  
    
    session.ref_code = ref_code
    session.ref_id = ref_id
        
    returnurl = URL('clinic','list_clinic',vars=dict(page=1,ref_code=ref_code,ref_id=ref_id))
    nexturl = URL('update_clinic/[id]',vars=dict(ref_code=ref_code,ref_id=ref_id))
    formA = crud.create(db.clinic, next='update_clinic/[id]', vars=dict(ref_code=ref_code,ref_id=ref_id),  message='New Clinic Added!')  ## company Details entry form
    formA.add_button("cancel",URL('clinic',returnurl))  ## return to home screen
   


        
                
    
    return dict(username=username,returnurl=returnurl,formA=formA, formheader=formheader,ref_code=ref_code,ref_id=ref_id)



def bank_clinic():

    auth = current.auth

    username = auth.user.first_name + ' ' + auth.user.last_name

    formheader = "Bank Details"    

    authuser = ""
    f = lambda name: name if ((name != "") & (name != None)) else ""
    authuser = f(auth.user.first_name)  + " " + f(auth.user.last_name)


    page=common.getgridpage(request.vars)

    if(len(request.args)>0):   # called with clinicid as URL params
        clinicid = int(request.args[0])
    elif (len(request.vars)>0): # called on grid next page, get the clinicid from session.
        clinicid = 0 if((common.getstring(request.vars.clinicid) == "")) else request.vars.clinicid

    ref_code = request.vars.ref_code
    ref_id = request.vars.ref_id

   

    returnurl = URL('clinic','list_clinic',vars=dict(page=page,clinicid=clinicid,ref_code=ref_code,ref_id=ref_id))
    ds = db((db.clinic.id == clinicid) & (db.clinic.is_active == True)).select(db.clinic.bank_id)
    bankid = 0 if(len(ds)!=1) else common.getid(ds[0].bank_id)
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
                db(db.clinic.id == clinicid).update(bank_id=bankid,
                                                        modified_on = common.getISTFormatCurrentLocatTime(),
                                                        modified_by =1 if(auth.user == None) else auth.user.id        
                                                        )
        else:
            rsp = json.loads(obj.update_account(requestobj))

        redirect(returnurl)

    elif formA.errors:
        response.flash = 'Error adding a Provider Bank Details' + str(formA.errors)        

    return dict(username=username,formA=formA,formheader=formheader,page=page,returnurl=returnurl,\
                providerid=0,provider="",providername="",authuser=authuser)