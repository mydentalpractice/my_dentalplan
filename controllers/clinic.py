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


#this method is called from new_customer page to get a list of clinics for the selected provider
def clinic_selector():
    provclinicid = request.vars.provclinicid
    providerid = int(common.getid(request.vars.providerid))
    clinics = db((db.clinic_ref.ref_code == 'PRV') & (db.clinic_ref.ref_id == providerid) & (db.clinic.is_active == True)).\
        select(db.clinic.id,db.clinic.name,left=db.clinic.on(db.clinic.id == db.clinic_ref.clinic_id))
    

    return dict(clinics=clinics,provclinicid=provclinicid)
    
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
    
    
 

    db.clinic.name.default = "" if(len(clinics) != 1 ) else common.getstring(clinics[0].name)
    
    dentalchairs = 0 if(len(clinics) != 1 ) else int(common.getid(clinics[0].dentalchairs))
    
    clinic_ref = "" if(len(clinics) !=1 ) else common.getstring(clinics[0].clinic_ref)
    name = "" if(len(clinics) !=1 ) else common.getstring(clinics[0].name)
    address1 = "" if(len(clinics) !=1 ) else common.getstring(clinics[0].address1)
    address2 = "" if(len(clinics) !=1 ) else common.getstring(clinics[0].address2)
    address3 = "" if(len(clinics) !=1 ) else common.getstring(clinics[0].address3)
    city = "" if(len(clinics) !=1 ) else common.getstring(clinics[0].city)
    st = "" if(len(clinics) !=1 ) else common.getstring(clinics[0].st)
    pin = "" if(len(clinics) !=1 ) else common.getstring(clinics[0].pin)
    
   
  
    
    
    auto_clave = common.getyesno(clinics[0].auto_clave)
 
    
    
    
    
    radiation_protection ="yes" if(len(clinics) == 0) else common.getyesno(clinics[0].radiation_protection)
    implantology = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].implantology)
    intra_oral_camera = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].intra_oral_camera)
    waste_displosal = "" if(len(clinics) == 0) else common.getstring(clinics[0].waste_displosal)
    daily_autoclaved = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].daily_autoclaved)
    
    suction_machine ="yes" if(len(clinics) == 0) else common.getyesno(clinics[0].suction_machine)
    instrument_sterilization = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].instrument_sterilization)
    
    RVG_OPG = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].RVG_OPG)
    
    emergency_drugs = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].emergency_drugs)
    
    rotary_endodontics = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].rotary_endodontics)


    
    patient_consent = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].patient_consent)
    
    patient_traffic = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].patient_traffic)
    
    receptionist = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].receptionist)
    
    air_conditioned = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].air_conditioned)
    
    toilet = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].toilet)
    
    parking_facility = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].parking_facility)
    
    
    backup_power = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].backup_power)
    
    internet = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].internet)
    
    credit_card = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].credit_card)
    
    patient_records = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].patient_records)

    
    water_filter = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].water_filter)
    laser = "" if(len(clinics) == 0) else common.getstring(clinics[0].laser)

    computers = "" if(len(clinics) == 0) else common.getstring(clinics[0].computers)
    
    network = "no" if(len(clinics) == 0) else common.getyesno(clinics[0].network)
   
    waiting_area = "" if(len(clinics) == 0) else common.getstring(clinics[0].waiting_area)
    
    certifcates = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].certifcates)
    
    infection_control = "no" if(len(clinics) == 0) else common.getyesno(clinics[0].infection_control)

    nabh_iso_certifcation = "yes" if(len(clinics) == 0) else common.getyesno(clinics[0].nabh_iso_certifcation)
    state_dental_registration = "yes" if(len(clinics) == 0) else common.getstring(clinics[0].state_dental_registration)
    registration_certificate = "" if(len(clinics) == 0) else common.getstring(clinics[0].registration_certificate)
    notes = "" if(len(clinics) == 0) else common.getstring(clinics[0].notes)

    mdp_registration = "" if(len(clinics) == 0) else common.getstring(clinics[0].mdp_registration)

    cell = "" if(len(clinics) == 0) else common.getstring(clinics[0].cell)
    telephone = "" if(len(clinics) == 0) else common.getstring(clinics[0].telephone)
    email = "" if(len(clinics) == 0) else common.getstring(clinics[0].email)

    website = "" if(len(clinics) == 0) else common.getstring(clinics[0].website)
    gps_location = "" if(len(clinics) == 0) else common.getstring(clinics[0].gps_location)
    whatsapp = "" if(len(clinics) == 0) else common.getstring(clinics[0].whatsapp)
    facebook = "" if(len(clinics) == 0) else common.getstring(clinics[0].facebook)
    twitter = "" if(len(clinics) == 0) else common.getstring(clinics[0].twitter)

    primary_clinic = False if(len(clinics) == 0) else common.getboolean(clinics[0].primary_clinic)
    formA = SQLFORM.factory(
        Field('clinic_ref','string',default=clinic_ref),
            
        Field('name','string',default=name),
        Field('address1','string',default=address1),
        Field('address2','string',default=address2),
        Field('address3','string',default=address3),
        Field('city', 'string',default=city,label='City',length=50,requires = IS_IN_SET(CITIES)),
        Field('st', 'string',default=st,label='State',length=50,requires = IS_IN_SET(STATES)),
        Field('pin','string',default=pin),
        
        Field('cell','string',default=cell),
        Field('telephone','string',default=telephone),
        Field('email','string',default=email),

        Field('website','string',default=website),
        Field('gps_location','string',default=gps_location),
        Field('whatsapp','string',default=whatsapp),
        Field('facebook','string',default=facebook),
        Field('twitter','string',default=twitter),

        Field('status','string',default=status),
        Field('primary_clinic','boolean',default=primary_clinic),
        
        Field('mdp_registration','string',default=mdp_registration),
        Field('dentalchairs','string',default=dentalchairs),
        
        
        Field('auto_clave','string',default=auto_clave,requires=IS_IN_SET(YESNO)),
        Field('implantology','string',default=implantology,requires=IS_IN_SET(YESNO)),
        Field('instrument_sterilization','string',default=instrument_sterilization,requires=IS_IN_SET(YESNO)),
        Field('waste_displosal','string',default=waste_displosal),
        Field('suction_machine','string',default=suction_machine,requires=IS_IN_SET(YESNO)),
        Field('laser','string',default=laser),
        Field('RVG_OPG','string',default=RVG_OPG,requires=IS_IN_SET(YESNO)),
        
        Field('radiation_protection','string',default=radiation_protection,requires=IS_IN_SET(YESNO)),                
        Field('computers','string',default=computers),                
        Field('network','string',default=network,requires=IS_IN_SET(YESNO)),                
        Field('internet','string',default=internet,requires=IS_IN_SET(YESNO)),                
        Field('air_conditioned','string',default=air_conditioned,requires=IS_IN_SET(YESNO)),                
        Field('waiting_area','string',default=waiting_area),                
        Field('backup_power','string',default=backup_power,requires=IS_IN_SET(YESNO)),                
        Field('toilet','string',default=toilet,requires=IS_IN_SET(YESNO)),                
        Field('water_filter','string',default=water_filter,requires=IS_IN_SET(YESNO)),                
        Field('parking_facility','string',default=parking_facility,requires=IS_IN_SET(YESNO)),                
        Field('receptionist','string',default=receptionist,requires=IS_IN_SET(YESNO)),                
        Field('credit_card','string',default=credit_card,requires=IS_IN_SET(YESNO)),                
        Field('certifcates','string',default=certifcates,requires=IS_IN_SET(YESNO)),                
        Field('emergency_drugs','string',default=emergency_drugs,requires=IS_IN_SET(YESNO)),                
        Field('infection_control','string',default=infection_control,requires=IS_IN_SET(YESNO)),                
        Field('daily_autoclaved','string',default=daily_autoclaved,requires=IS_IN_SET(YESNO)),                
        Field('patient_records','string',default=patient_records,requires=IS_IN_SET(YESNO)),                
        Field('patient_consent','string',default=patient_consent,requires=IS_IN_SET(YESNO)),                
        Field('patient_traffic','string',default=patient_traffic,requires=IS_IN_SET(YESNO)),                
        Field('nabh_iso_certifcation','string',default=nabh_iso_certifcation,requires=IS_IN_SET(YESNO)),     
        Field('intra_oral_camera','string',default=intra_oral_camera,requires=IS_IN_SET(YESNO)),     
        Field('rotary_endodontics','string',default=rotary_endodontics,requires=IS_IN_SET(YESNO)),     
        Field('bank_id','integer'), 
        
        Field('state_dental_registration','string',default=state_dental_registration),
        Field('registration_certificate','string',default=registration_certificate),
        
        Field('notes','text',default=notes),
    )  
    
    
    
    
    
    if formA.accepts(request,session,keepvalues=True):
        
        db.clinic.update_or_insert(((db.clinic.id == clinicid) & (db.clinic.is_active == True)),
                        
                        clinic_ref=formA.vars.name if(formA.vars.name != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].name)),
                            
                        name=formA.vars.name if(formA.vars.name != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].name)),
                        address1=formA.vars.address1 if(formA.vars.address1 != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].address1)),
                        address2=formA.vars.address2 if(formA.vars.address2 != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].address2)),
                        address3=formA.vars.address3 if(formA.vars.address3 != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].address3)),
                        city=formA.vars.city if(formA.vars.city != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].city)),
                        st=formA.vars.st if(formA.vars.st != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].st)),
                        pin=formA.vars.pin if(formA.vars.pin != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].pin)),
                        
                        cell=formA.vars.cell if(formA.vars.cell != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].cell)),
                        telephone=formA.vars.telephone if(formA.vars.telephone != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].telephone)),
                        email=formA.vars.email if(formA.vars.email != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].email)),
                
                        website=formA.vars.website if(formA.vars.website != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].website)),
                        gps_location=formA.vars.gps_location if(formA.vars.gps_location != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].gps_location)),
                        whatsapp=formA.vars.whatsapp if(formA.vars.whatsapp != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].whatsapp)),
                        facebook=formA.vars.facebook if(formA.vars.facebook != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].facebook)),
                        twitter=formA.vars.twitter if(formA.vars.twitter != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].twitter)),
                
                        status=formA.vars.status if(formA.vars.status != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].status)),
                        
                        
                        #primary_clinic','boolean'),
                        
                        mdp_registration=formA.vars.mdp_registration if(formA.vars.mdp_registration != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].mdp_registration)),
                        dentalchairs=formA.vars.dentalchairs if(formA.vars.dentalchairs != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].dentalchairs)),
                        
                        
                        auto_clave=common.gettruefalse(formA.vars.auto_clave) if(formA.vars.auto_clave != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].auto_clave)),
                        
                        implantology=common.gettruefalse(formA.vars.auto_clave) if(formA.vars.auto_clave != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].auto_clave)),
                        instrument_sterilization=common.gettruefalse(formA.vars.auto_clave) if(formA.vars.auto_clave != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].auto_clave)),
                        waste_displosal=formA.vars.waste_displosal if(formA.vars.waste_displosal != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].waste_displosal)),
                        
                        suction_machine=formA.vars.suction_machine if(formA.vars.suction_machine != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].suction_machine)),
                        laser=formA.vars.laser if(formA.vars.laser != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].laser)),
                        
                        RVG_OPG=common.gettruefalse(formA.vars.RVG_OPG) if(formA.vars.RVG_OPG != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].RVG_OPG)),
                        
                        radiation_protection=common.gettruefalse(formA.vars.radiation_protection) if(formA.vars.radiation_protection != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].radiation_protection)),
                        computers=int(formA.vars.computers) if(formA.vars.computers != "") else ("" if(len(clinics) == 0) else int(common.getid(clinics[0].computers))),
                        
                        network=common.gettruefalse(formA.vars.network) if(formA.vars.network != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].network)),
                        internet=common.gettruefalse(formA.vars.internet) if(formA.vars.internet != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].internet)),
                        air_conditioned=common.gettruefalse(formA.vars.air_conditioned) if(formA.vars.air_conditioned != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].air_conditioned)),
                        
                        waiting_area=formA.vars.waiting_area if(formA.vars.waiting_area != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].waiting_area)),
                        
                        backup_power=common.gettruefalse(formA.vars.backup_power) if(formA.vars.backup_power != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].backup_power)),
                        toilet=common.gettruefalse(formA.vars.toilet) if(formA.vars.toilet != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].toilet)),
                        water_filter=common.gettruefalse(formA.vars.water_filter) if(formA.vars.water_filter != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].water_filter)),               
                        parking_facility=common.gettruefalse(formA.vars.parking_facility) if(formA.vars.parking_facility != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].parking_facility)),                
                        receptionist=common.gettruefalse(formA.vars.receptionist) if(formA.vars.receptionist != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].receptionist)),              
                        credit_card=common.gettruefalse(formA.vars.credit_card) if(formA.vars.credit_card != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].credit_card)),               
                        certifcates=common.gettruefalse(formA.vars.certifcates) if(formA.vars.certifcates != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].certifcates)),            
                        emergency_drugs=common.gettruefalse(formA.vars.emergency_drugs) if(formA.vars.emergency_drugs != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].emergency_drugs)),                
                        infection_control = common.gettruefalse(formA.vars.infection_control) if(formA.vars.infection_control != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].infection_control)),             
                        daily_autoclaved=common.gettruefalse(formA.vars.daily_autoclaved) if(formA.vars.daily_autoclaved != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].daily_autoclaved)),                
                        patient_records=common.gettruefalse(formA.vars.patient_records) if(formA.vars.patient_records != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].patient_records)),                
                        
                        patient_consent=common.gettruefalse(formA.vars.patient_consent) if(formA.vars.patient_consent != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].patient_consent)),              
                        patient_traffic=common.gettruefalse(formA.vars.patient_traffic) if(formA.vars.patient_traffic != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].patient_traffic)),                 
                        nabh_iso_certifcation=common.gettruefalse(formA.vars.nabh_iso_certifcation) if(formA.vars.nabh_iso_certifcation != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].nabh_iso_certifcation)),      
                        intra_oral_camera=common.gettruefalse(formA.vars.intra_oral_camera) if(formA.vars.intra_oral_camera != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].intra_oral_camera)),       
                        rotary_endodontics=common.gettruefalse(formA.vars.rotary_endodontics) if(formA.vars.rotary_endodontics != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].rotary_endodontics)),   
                        bank_id = formA.vars.bankid,
                        
                        state_dental_registration=formA.vars.rotary_endodontics if(formA.vars.state_dental_registration != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].state_dental_registration)),   
                        registration_certificate=formA.vars.registration_certificate if(formA.vars.registration_certificate != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].registration_certificate)),   
                        
                        notes=formA.vars.notes if(formA.vars.notes != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].notes)),   



                        is_active = True,\
                        modified_on = datetime.date.today(),\
                        modified_by = 1
        )   
        db.commit()
        

    elif formA.errors:
        i  =0
        
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
        Field('pin','string',  default=pin,label='PIN'),


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