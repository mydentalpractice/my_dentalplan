# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']
from gluon.tools import Crud
crud = Crud(db)

import string
import random
import json
import datetime
import time
import os


from datetime import date, timedelta

from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import mail
from applications.my_pms2.modules  import mdpuser
from applications.my_pms2.modules  import mdpprospect
from applications.my_pms2.modules  import mdpprovider
from applications.my_pms2.modules  import mdpbank
from applications.my_pms2.modules  import mdpmedia
from applications.my_pms2.modules  import mdptimings
from applications.my_pms2.modules  import logger


#this method is called from new_customer page to get a list of clinics for the selected provider
def clinic_selector():
    provclinicid = request.vars.provclinicid
    providerid = int(common.getid(request.vars.providerid))
    clinics = db((db.clinic_ref.ref_code == 'PRV') & (db.clinic_ref.ref_id == providerid) & (db.clinic.is_active == True)).\
        select(db.clinic.id,db.clinic.name,left=db.clinic.on(db.clinic.id == db.clinic_ref.clinic_id))
    

    return dict(clinics=clinics,provclinicid=provclinicid)


def new_media():
    
    logger.loggerpms2.info("Enter Clinic New Media")

    mediatype = request.vars.mediatype
    mediaformat = request.vars.mediaformat
    
    source = common.getstring(request.vars.source)
    page     = common.getpage1(request.vars.page)

    providerid  = int(common.getid(request.vars.providerid))
    patientid   = int(common.getid(request.vars.patientid))
    memberid    = int(common.getid(request.vars.memberid))    

    logger.loggerpms2.info("Get all Members " + str(memberid))

    members = db(db.patientmember.id == memberid).select()
    memberref = common.getstring(members[0].patientmember)

    providerdict = common.getproviderfromid(db, providerid)
    providername = providerdict["providername"]

    treatmentid = int(common.getid(request.vars.treatmentid))

    tplanid = 0
    tplan = "Treatment Plan"


    #logger.loggerpms2.info("Get all Members1 " + str(memberid))

    rows = db((db.patientmember.id == memberid)&(db.patientmember.is_active == True)).select()
    membername = rows[0].fname + ' ' + rows[0].mname + ' ' + rows[0].lname    

    if(memberid == patientid):
        patienttype = 'P'
        patientname = membername
    else:
        patienttype = 'D'
        rows = db((db.patientmemberdependants.id == patientid)&(db.patientmemberdependants.is_active == True)).select()    
        if(len(rows) > 0):
            patientname = rows[0].fname + ' ' + rows[0].mname + ' ' + rows[0].lname    
    #logger.loggerpms2.info("Log a") 

    db.dentalimage.treatmentplan.default = tplanid
    db.dentalimage.treatmentplan.writable = False
    db.dentalimage.treatment.default = treatmentid
    db.dentalimage.treatment.writable = False    
    db.dentalimage.patientmember.default = memberid
    db.dentalimage.patientmember.writable = False
    db.dentalimage.patient.default = patientid
    db.dentalimage.patient.writable = False
    db.dentalimage.patienttype.default = patienttype
    db.dentalimage.patienttype.writable = False
    db.dentalimage.patientname.default = patientname
    db.dentalimage.patientname.writable = False

    db.dentalimage.provider.default = providerid
    db.dentalimage.provider.writable = False



    db.dentalimage.title.widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small')
    db.dentalimage.tooth.widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small')
    db.dentalimage.quadrant.widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small')
    db.dentalimage.imagedate.widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='w3-input w3-border w3-small date')
    db.dentalimage.patient.widget = lambda field, value:SQLFORM.widgets.options.widget(field, value,_style="width:100%;height:35px",_class='w3-input w3-border w3-small')

    #logger.loggerpms2.info("Provider id " + str(providerid)) 

    rows = db((db.provider.id == providerid)).select()
    provider = rows[0].provider

    strSQL = "select 0, '' AS patienttype, '-Select-' as fname, '' as lname"    
    strSQL = strSQL + " UNION "
    strSQL = strSQL + " select id , 'P' AS patienttype,fname,lname from patientmember where id = " + str(memberid)
    strSQL = strSQL + " UNION "
    strSQL = strSQL + " select id,'D' AS patienttype, patientmemberdependants.fname,patientmemberdependants.lname from patientmemberdependants where  patientmemberdependants.patientmember = " + str(memberid)
    dspatients = db.executesql(strSQL)    

    #logger.loggerpms2.info("dspatients " + len(dspatients)) 

    if(source == "treatment"):
        returnurl = URL('treatment', 'update_treatment', vars=dict(page=page,imagepage=0,providerid=providerid,treatmentid=treatmentid))
    else:
        returnurl = URL('media', 'list_media', vars=dict(providerid = providerid,memberid=memberid,patientid=patientid,page=page,memberref=memberref,mediatype=mediatype))


    formA = SQLFORM.factory(
        Field('title','string'),
        Field('media','string'),
        Field('uploadfolder','string'),
        Field('tooth','string'),
        Field('quadrant','string'),
        Field('description','text'),
        Field('patienttype','string'),
        Field('patientname','string'),
        Field('mediafile','string'),
        Field('mediatype','string'),
        Field('mediaformat','string'),


        Field('mediadate','date', default=request.now,requires = IS_DATE(format=T('%d/%m/%Y'))),

        Field('treatmentplan','integer'),
        Field('treatment','integer'),
        Field('patientmember','integer'),
        Field('patient','integer'),  
        Field('provider','integer'),

        Field('mediasize','double'),

        Field('imagedata','text', length=50e+6, label='Image Data')


    )




    formA.element('textarea[name=description]')['_style'] = 'height:50px;line-height:1.0;'
    formA.element('textarea[name=description]')['_rows'] = 5   
    formA.element('textarea[name=description]')['_cols'] = 50
    formA.element('textarea[name=description]')['_class'] = 'form-control'


    xtitle = formA.element('#no_table_title')
    xtitle['_class'] = 'form-control'
    xtitle['_placeholder'] = 'Title'
    xtitle['_autocomplete'] = 'off'   

    xtooth = formA.element('#no_table_tooth')
    xtooth['_class'] = 'form-control'
    xtooth['_placeholder'] = 'Tooth'
    xtooth['_autocomplete'] = 'off'   

    xquad = formA.element('#no_table_quadrant')
    xquad['_class'] = 'form-control'
    xquad['_placeholder'] = 'Quadrant'
    xquad['_autocomplete'] = 'off'   

    xdate = formA.element('#no_table_mediadate')
    xdate['_class'] = 'input-group form-control form-control-inline date-picker'
    xdate['_placeholder'] = 'Date'
    xdate['_autocomplete'] = 'off'   

    submit = formA.element('input',_type='submit')
    submit['_value'] = 'Save' 
    submit["_class"] = "btn green"
    
    error = ""
    count = 0
    mediaurl = ""
    mediafile = ""
    mediaid = 0

    if formA.accepts(request,session,keepvalues=True):

        try:

            #upload image
            if(len(request.vars.imagedata)>0):
                file_content = None
                file_content = request.vars.imagedata
                
                o = mdpmedia.Media(db, providerid, mediatype, mediaformat)
                j = {
                    "mediadata":file_content,
                    "memberid":str(memberid),
                    "patientid":str(patientid),
                    "treatmentid":str(treatmentid),
                    "title":request.vars.title,
                    "tooth":request.vars.tooth,
                    "quadrant":request.vars.quadrant,
                    "mediadate":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y"),
                    "description":request.vars.description,
                    "appath":request.folder,
                    "mediatype":mediatype,
                    "mediaformat":mediaformat
                }

                x= json.loads(o.upload_media(j)) 

                mediaid = common.getkeyvalue(x,'mediaid',0)
                mediaurl = URL('my_dentalplan','media','media_download',\
                               args=[mediaid])  

           
        except Exception as e:
            error = "Upload Audio Exception Error - " + str(e)             
    elif formA.errors:
        x = str(formA.errors)
    else:
        i = 0

    return dict(formA=formA, returnurl=returnurl, providername=providername,memberid=memberid, memberref=memberref,\
                providerid=providerid,membername=membername,patientname=patientname,dspatients=dspatients,\
                treatmentid=treatmentid, tplanid=tplanid, tplan=tplan,page=page,patientid=patientid,\
                source=source,error=error,count=count,\
                mediatype=mediatype, mediaformat=mediaformat, mediafile=mediafile,mediaurl=mediaurl)   




@auth.requires_membership('webadmin')
@auth.requires_login()
def new_image():
    username = auth.user.first_name + ' ' + auth.user.last_name
    page=common.getgridpage(request.vars)
    formheader="New Clinic Image"
    
    authuser = ""
    f = lambda name: name if ((name != "") & (name != None)) else ""
    authuser = f(auth.user.first_name)  + " " + f(auth.user.last_name)

    providerid = int(common.getkeyvalue(request.vars,'providerid',0))
    prev_ref_code = request.vars.prev_ref_code
    prev_ref_id = request.vars.prev_ref_id
    
    ref_code = request.vars.ref_code
    ref_id = request.vars.ref_id
    clinics = db(db.clinic.id == ref_id).select()
    
    form = SQLFORM.factory(
        Field('clinicname','string',label='Clinic Name', default="" if(len(clinics) != 1) else clinics[0].name ),
        #Field('browsefile','string',label='File Name'),
     
        #Field('csvfile','string',label='CSV File'),
        Field('title','string',label='Title'),
        Field('imagedate','date',default=datetime.date.today(), label='Image Date'),
        Field('description','text',label='Description'),
        Field('imagedata','text', length=50e+6, label='Image Data')
    )    

    submit = form.element('input',_type='submit')
    submit['_value'] = 'Upload Image'    

    #xcsvfile = form.element('input',_id='no_table_csvfile')
    #xcsvfile['_class'] =  'w3-input w3-border w3-small'    
    
    #xbrwfile = form.element('input',_id='no_table_browsefile')
    #xbrwfile['_type'] =  'file'        
    #xbrwfile['_class'] =  'w3-input w3-border w3-small'        

    
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
                    "description":request.vars.description,
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

           
        except Exception as e:
            error = "Upload Audio Exception Error - " + str(e)             
    elif form.errors:
        x = str(form.errors)
    else:
        i = 0    
    
    
    
    #if form.accepts(request,session,keepvalues=True):
        #try:
            #filename = request.vars.csvfile
            #browse = form.vars.browsefile.filename
            
            #x = os.path.abspath(browse)
            #filePath = os.path.join("\\","media_files")
            #filePath = os.path.join(filePath,browse)
     
            
           
            #o = mdpmedia.Media(db, 0, 'image', 'jpg')

            #j = {
                #"filename":filePath,
                #"title":"test",
                #"tooth":"1",
                #"quadrant":"1",
                #"mediadate":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y"),
                #"description":form.vars.description,
                #"appath":request.folder
            #}


            #x= json.loads(o.upload_mediafile(j))            

            #mediaid = common.getkeyvalue(x,'mediaid',0)

            #db.dentalimage_ref.insert(
                
                #ref_code = ref_code,
                #ref_id = ref_id,
                #media_id = mediaid
            
            #)
            
            #mediaurl = URL('my_dentalplan','media','media_download',\
                           #args=[mediaid])



        #except Exception as e:
            #error = "Upload Image Media File Exception Error - " + str(e)        
    
    returnurl = URL('clinic','list_clinic_images',vars=dict(page=page,ref_code=ref_code,ref_id=ref_id,prev_ref_code=prev_ref_code,prev_ref_id=prev_ref_id))
    return dict(form=form, formheader=formheader,mediaurl=mediaurl,mediafile=mediafile,count=count,error=error,
                ref_code=ref_code,ref_id=ref_id,prev_ref_code=prev_ref_code,prev_ref_id=prev_ref_id,returnurl=returnurl) 

@auth.requires_membership('webadmin')
@auth.requires_login()
def new_image():
    username = auth.user.first_name + ' ' + auth.user.last_name
    page=common.getgridpage(request.vars)
    formheader="New Clinic Image"
    
    authuser = ""
    f = lambda name: name if ((name != "") & (name != None)) else ""
    authuser = f(auth.user.first_name)  + " " + f(auth.user.last_name)

    providerid = int(common.getkeyvalue(request.vars,'providerid',0))
    prev_ref_code = request.vars.prev_ref_code
    prev_ref_id = request.vars.prev_ref_id
    
    ref_code = request.vars.ref_code
    ref_id = request.vars.ref_id
    clinics = db(db.clinic.id == ref_id).select()
    
    form = SQLFORM.factory(
        Field('clinicname','string',label='Clinic Name', default="" if(len(clinics) != 1) else clinics[0].name ),
        #Field('browsefile','string',label='File Name'),
     
        #Field('csvfile','string',label='CSV File'),
        Field('title','string',label='Title'),
        Field('imagedate','date',default=datetime.date.today(), label='Image Date'),
        Field('description','text',label='Description'),
        Field('imagedata','text', length=50e+6, label='Image Data')
    )    

    submit = form.element('input',_type='submit')
    submit['_value'] = 'Upload Image'    

    #xcsvfile = form.element('input',_id='no_table_csvfile')
    #xcsvfile['_class'] =  'w3-input w3-border w3-small'    
    
    #xbrwfile = form.element('input',_id='no_table_browsefile')
    #xbrwfile['_type'] =  'file'        
    #xbrwfile['_class'] =  'w3-input w3-border w3-small'        

    
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
                    "description":request.vars.description,
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

           
        except Exception as e:
            error = "Upload Audio Exception Error - " + str(e)             
    elif form.errors:
        x = str(form.errors)
    else:
        i = 0    
    
    
    
    #if form.accepts(request,session,keepvalues=True):
        #try:
            #filename = request.vars.csvfile
            #browse = form.vars.browsefile.filename
            
            #x = os.path.abspath(browse)
            #filePath = os.path.join("\\","media_files")
            #filePath = os.path.join(filePath,browse)
     
            
           
            #o = mdpmedia.Media(db, 0, 'image', 'jpg')

            #j = {
                #"filename":filePath,
                #"title":"test",
                #"tooth":"1",
                #"quadrant":"1",
                #"mediadate":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y"),
                #"description":form.vars.description,
                #"appath":request.folder
            #}


            #x= json.loads(o.upload_mediafile(j))            

            #mediaid = common.getkeyvalue(x,'mediaid',0)

            #db.dentalimage_ref.insert(
                
                #ref_code = ref_code,
                #ref_id = ref_id,
                #media_id = mediaid
            
            #)
            
            #mediaurl = URL('my_dentalplan','media','media_download',\
                           #args=[mediaid])



        #except Exception as e:
            #error = "Upload Image Media File Exception Error - " + str(e)        
    
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
def new_logo():
    page=common.getgridpage(request.vars)
    clinicid = int(common.getkeyvalue(request.vars,"ref_id",0))
    
    isMDP = common.getboolean(common.getkeyvalue(request.vars,'isMDP','True'))
    prev_ref_code = "PST" if (common.getstring(request.vars.prev_ref_code) == "") else request.vars.prev_ref_code
    prev_ref_id = 0 if (common.getstring(request.vars.prev_ref_id) == "") else int(request.vars.prev_ref_id)

    ref_code = common.getkeyvalue(request.vars,"ref_code","CLN")
    ref_id = common.getkeyvalue(request.vars,"ref_id",0)

    r = db(db.clinic.id == ref_id).select()
    clinic_ref = r[0].clinic_ref if(len(r)>=0) else ""
    
    form = SQLFORM.factory(
        Field('clinic','string',label='Clinic Code', default=clinic_ref ),
     
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
                
                o = mdpmedia.Media(db, 0, mediatype, mediaformat)
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
                
                db(db.clinic.id == clinicid).update(logo_id = mediaid, logo_file = common.getkeyvalue(x,"mediafilename",""))

           
        except Exception as e:
            error = "Upload Audio Exception Error - " + str(e)             
    elif form.errors:
        x = str(form.errors)
    else:
        i = 0    
    
    

           
    
    returnurl = URL('clinic','update_clinic',vars=dict(isMPD=isMDP, page=page,ref_code=prev_ref_code,ref_id=prev_ref_id,clinicid=ref_id))
    return dict(form=form, pae=page,mediaurl=mediaurl,mediafile=mediafile,count=count,error=error,
                ref_code=ref_code,ref_id=ref_id,returnurl=returnurl) 

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
    


def list_all_clinics():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Clinic List"
    page = common.getpage1(request.vars.page)

    query = ((db.clinic.is_active==True))
    
    
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
    
    left = None
    orderby = (db.clinic.clinic_ref)
    exportlist = dict( csv=False,csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    links = [
             lambda row: A('Update',_href=URL("clinic","update_clinic",vars=dict(page=page,clinicid=row.id))),
             lambda row: A('Bank Details',_href=URL("clinic","bank_clinic",vars=dict(page=page,clinicid=row.id))),
             lambda row: A('Clinic Images',_href=URL("clinic","list_clinic_images",vars=dict(page=page,ref_code="CLN",ref_id=row.id))),
             lambda row: A('Clinic Timings',_href=URL("clinic","list_clinic_timings",vars=dict(page=page,ref_code="CLN",ref_id=row.id))),
             lambda row: A('Delete',_href=URL("clinic","delete_clinic",vars=dict(page=page,clinicid=row.id)))
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

    returnurl = URL('clinic','list_all_clinics')
    return dict(username=username,returnurl=returnurl,form=form, formheader=formheader,page=common.getgridpage(request.vars),ref_code=ref_code,ref_id=ref_id,\
                prev_ref_code=prev_ref_code,prev_ref_id=prev_ref_id)    


@auth.requires_membership('webadmin')
@auth.requires_login()
def list_clinic():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Clinic List"
    page = common.getpage1(request.vars.page)
    isMDP = common.getboolean(common.getkeyvalue(request.vars,'isMDP','True'))

    prev_ref_code = "PRV" if (common.getstring(request.vars.prev_ref_code) == "") else request.vars.prev_ref_code
    prev_ref_id = 0 if (common.getstring(request.vars.prev_ref_id) == "") else int(request.vars.prev_ref_id)

    
    ref_code = "PRV" if (common.getstring(request.vars.ref_code) == "") else request.vars.ref_code
    ref_id = 0 if (common.getstring(request.vars.ref_id) == "") else int(request.vars.ref_id)
    
    if(ref_id == 0):
        query = ((db.clinic_ref.ref_code == ref_code) & (db.clinic.is_active==True))
    else:
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
             lambda row: A('Update',_href=URL("clinic","update_clinic",vars=dict(isMDP=isMDP,page=page,ref_code=ref_code,ref_id=ref_id,prev_ref_code=prev_ref_code,prev_ref_id=prev_ref_id,clinicid=row.clinic.id))),
             lambda row: A('Bank Details',_href=URL("clinic","bank_clinic",vars=dict(isMDP=isMDP,page=page,ref_code=ref_code,ref_id=ref_id,prev_ref_code=ref_code,prev_ref_id=ref_id,clinicid=row.clinic.id))),
             lambda row: A('Clinic Images',_href=URL("clinic","list_clinic_images",vars=dict(isMDP=isMDP,page=page,ref_code="CLN",ref_id=row.clinic.id,prev_ref_code=ref_code,prev_ref_id=ref_id))),
             lambda row: A('Clinic Logo',_href=URL("clinic","new_logo",vars=dict(isMDP=isMDP,page=page,ref_code="CLN",ref_id=row.clinic.id,prev_ref_code=ref_code,prev_ref_id=ref_id))),
             lambda row: A('Delete',_href=URL("clinic","delete_clinic",vars=dict(isMDP=isMDP,page=page,ref_code=ref_code,ref_id=ref_id,clinicid=row.clinic.id)))
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

    returnurl = ""
    if(ref_code == "PST"):
        returnurl = URL('prospect','list_prospect',vars=dict(isMDP=isMDP,page=page,ref_code="AGN",ref_id=0))
    else:
        returnurl = URL('provider','list_provider',vars=dict(isMDP=isMDP,page=page,ref_code="PRV",ref_id=0)) 
       
    return dict(username=username,returnurl=returnurl,form=form, formheader=formheader,page=common.getgridpage(request.vars),ref_code=ref_code,ref_id=ref_id,\
                prev_ref_code=prev_ref_code,prev_ref_id=prev_ref_id)    

@auth.requires_membership('webadmin')
@auth.requires_login()
def list_provider_clinics():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Clinic List"
    page = common.getpage1(request.vars.page)

    prev_ref_code = "PRV" if (common.getstring(request.vars.prev_ref_code) == "") else request.vars.prev_ref_code
    prev_ref_id = 0 if (common.getstring(request.vars.prev_ref_id) == "") else int(request.vars.prev_ref_id)

    
    ref_code = "PRV" if (common.getstring(request.vars.ref_code) == "") else request.vars.ref_code
    ref_id = 0 if (common.getstring(request.vars.ref_id) == "") else int(request.vars.ref_id)
    
    if(ref_id == 0):
        query = ((db.clinic_ref.ref_code == ref_code) & (db.clinic.is_active==True))
    else:
        query = ((db.clinic_ref.ref_code == ref_code)& (db.clinic_ref.ref_id == ref_id) & (db.clinic.is_active==True))
    
    fields=(
            db.clinic.id,       
            db.provider.provider,
            db.provider.providername,
            db.clinic.name,
            db.clinic.cell,
            db.clinic.city,
            db.clinic.pin
            
            
            )
    
    db.clinic.id.readonly = False
    
    headers={
       
        'provider.provider' : 'Provider',
        'provider.providername' : 'Provider Name',
        'clinic.name':'Clinic Name',
        'clinic.cell' : 'Cell',
        'clinic.city' : 'Cty',
        'clinic.pin' : 'Pin'
        
   
       
        }    
    left = [db.clinic.on(db.clinic.id==db.clinic_ref.clinic_id),db.provider.on(db.provider.id == db.clinic_ref.ref_id)]
    orderby = (db.clinic.clinic_ref)
    exportlist = dict( csv=False,csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    links = [
             lambda row: A('Update',_href=URL("clinic","update_clinic",vars=dict(page=page,ref_code=ref_code,ref_id=ref_id,clinicid=row.clinic.id))),
             lambda row: A('Bank Details',_href=URL("clinic","bank_clinic",vars=dict(page=page,ref_code=ref_code,ref_id=ref_id,clinicid=row.clinic.id))),
             lambda row: A('Clinic Images',_href=URL("clinic","list_clinic_images",vars=dict(page=page,ref_code="CLN",ref_id=row.clinic.id,prev_ref_code=ref_code,prev_ref_id=ref_id))),
             lambda row: A('Clinic Logo',_href=URL("clinic","new_logo",vars=dict(page=page,ref_code="CLN",ref_id=row.clinic.id,prev_ref_code=ref_code,prev_ref_id=ref_id))),
             lambda row: A('Clinic Timings',_href=URL("clinic","clinic_prov_timings",vars=dict(page=page,ref_code="CLN",ref_id=row.clinic.id,prev_ref_code=ref_code,prev_ref_id=ref_id))),
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
def clinic_prov_timings():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Clinic List"
    page = common.getpage1(request.vars.page)
    source = common.getkeyvalue(request.vars,"source","")
    
    ref_code = request.vars.ref_code
    ref_id = int(common.getid(request.vars.ref_id))  #clinic id
    logger.loggerpms2.info("Enter clinic prov timings " + ref_code + " " + str(ref_id))
    
    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]

    doctorname = ""
    
    if(source=="home"):
        returnurl = URL('my_pms2','admin', 'providerhome',vars=dict(providerid=providerid,clinicid=ref_id,clinicname=session.clinicname))
    else:    
        returnurl = URL('clinic', 'list_provider_clinics')

    page = 1

    mon_day_chk = False
    mon_lunch_chk = False
    mon_del_chk = False
    mon_starttime_1 = ""
    mon_endtime_1 = ""
    mon_starttime_2 = ""
    mon_endtime_2 = ""
    mon_visitinghours = ""

    tue_day_chk = False
    tue_lunch_chk = False
    tue_del_chk = False
    tue_starttime_1 = ""
    tue_endtime_1 = ""
    tue_starttime_2 = ""
    tue_endtime_2 = ""
    tue_visitinghours = ""

    wed_day_chk = False
    wed_lunch_chk = False
    wed_del_chk = False
    wed_starttime_1 = ""
    wed_endtime_1 = ""
    wed_starttime_2 = ""
    wed_endtime_2 = ""
    wed_visitinghours = ""

    thu_day_chk = False
    thu_lunch_chk = False
    thu_del_chk = False
    thu_starttime_1 = ""
    thu_endtime_1 = ""
    thu_starttime_2 = ""
    thu_endtime_2 = ""
    thu_visitinghours = ""

    fri_day_chk = False
    fri_lunch_chk = False
    fri_del_chk = False
    fri_starttime_1 = ""
    fri_endtime_1 = ""
    fri_starttime_2 = ""
    fri_endtime_2 = ""
    fri_visitinghours = ""

    sat_day_chk = False
    sat_lunch_chk = False
    sat_del_chk = False
    sat_starttime_1 = ""
    sat_endtime_1 = ""
    sat_starttime_2 = ""
    sat_endtime_2 = ""
    sat_visitinghours = ""

    sun_day_chk = False
    sun_lunch_chk = False
    sun_del_chk = False
    sun_starttime_1 = ""
    sun_endtime_1 = ""
    sun_starttime_2 = ""
    sun_endtime_2 = ""
    sun_visitinghours = ""
    
    mon_id_1 = 0
    mon_id_2 = 0
    
    tue_id_1 = 0
    tue_id_2 = 0

    wed_id_1 = 0
    wed_id_2 = 0

    thu_id_1 = 0
    thu_id_2 = 0

    fri_id_1 = 0
    fri_id_2 = 0

    sat_id_1 = 0
    sat_id_2 = 0
    

    visitinghours = 'Not Set'
    lunchbreak = 'Not Set'

    #todays date
    today_date = datetime.date.today()   #yyyy-mm-dd

    #weeks start date
    week_start = today_date - timedelta(days=today_date.weekday())

    #weeks end date
    week_end = week_start + timedelta(days=6)
    
    if(ref_id > 0):
        # need to get information from database and set the defauls
        
        
        
        #clinic details
        cln = db((db.clinic.id == ref_id) & (db.clinic.is_active == True)).select()
        clinicname = cln[0].name if(len(cln) > 0) else ""
        
        cts = db((db.ops_timing_ref.ref_code == 'CLN') & (db.ops_timing_ref.ref_id == ref_id) &\
                 (db.ops_timing.calendar_date >= week_start) &\
                 (db.ops_timing.calendar_date <= week_end) &\
                 (db.ops_timing.day_of_week != 'Sun') & (db.ops_timing.is_active == True)).\
            select(db.ops_timing.ALL, orderby=[db.ops_timing.day_of_week, db.ops_timing.open_time], left=db.ops_timing.on(db.ops_timing_ref.ops_timing_id == db.ops_timing.id))
        
        
        for ct in cts:
            if(ct.day_of_week == 'Mon'):
                mon_day_chk = not common.getboolean(ct.is_holiday)
                mon_lunch_chk = common.getboolean(ct.is_lunch)
                mon_del_chk = False

              
                
                
                if((ct.open_time >= datetime.time(0,0,0)) & (ct.open_time <= datetime.time(14,0,0))):

                    mon_starttime_1 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    mon_endtime_1 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    mon_id_1 = ct.id
                else:   
                    mon_starttime_2 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    mon_endtime_2 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    mon_id_2 = ct.id
                    
                mon_visitinghours = ""
        
            if(ct.day_of_week == 'Tue'):
                tue_day_chk =not common.getboolean(ct.is_holiday)
                tue_lunch_chk = common.getboolean(ct.is_lunch)
                tue_del_chk = False

              
                
                if((ct.open_time >= datetime.time(0,0,0)) & (ct.open_time <= datetime.time(14,0,0))):
                    tue_starttime_1 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    tue_endtime_1 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    tue_id_1 = ct.id
                    
                else:   
                    tue_starttime_2 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    tue_endtime_2 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    tue_id_2 = ct.id
                    
                tue_visitinghours = ""

            if(ct.day_of_week == 'Wed'):
                wed_day_chk = not common.getboolean(ct.is_holiday)
                wed_lunch_chk = common.getboolean(ct.is_lunch)
                wed_del_chk = False

         
                
                if((ct.open_time >= datetime.time(0,0,0)) & (ct.open_time <= datetime.time(14,0,0))):
                    wed_starttime_1 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    wed_endtime_1 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    wed_id_1 = ct.id
                else:   
                    wed_starttime_2 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    wed_endtime_2 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    wed_id_2 = ct.id
                    
                wed_visitinghours = ""

            if(ct.day_of_week == 'Thu'):
                thu_day_chk = not common.getboolean(ct.is_holiday)
                thu_lunch_chk = common.getboolean(ct.is_lunch)
                thu_del_chk = False

            
                if((ct.open_time >= datetime.time(0,0,0)) & (ct.open_time <= datetime.time(14,0,0))):
                    thu_starttime_1 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    thu_endtime_1 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    thu_id_1 = ct.id
                    
                else:   
                    thu_starttime_2 = common.getstringfromtime(ct.open_time ,"%I:%M %p")
                    thu_endtime_2 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    thu_id_2 = ct.id
                    
                thu_visitinghours = ""

            if(ct.day_of_week == 'Fri'):
                fri_day_chk = not common.getboolean(ct.is_holiday)
                fri_lunch_chk = common.getboolean(ct.is_lunch)
                fri_del_chk = False

             
                
                if((ct.open_time >= datetime.time(0,0,0)) & (ct.open_time <= datetime.time(14,0,0))):
                    fri_starttime_1 = common.getstringfromtime(ct.open_time ,"%I:%M %p")
                    fri_endtime_1 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    fri_id_1 = ct.id
                else:   
                    fri_starttime_2 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    fri_endtime_2 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    fri_id_2 = ct.id
                    
                fri_visitinghours = ""

            if(ct.day_of_week == 'Sat'):
                sat_day_chk = not common.getboolean(ct.is_holiday)
                sat_lunch_chk = common.getboolean(ct.is_lunch)
                sat_del_chk = False

                
                if((ct.open_time >= datetime.time(0,0,0)) & (ct.open_time <= datetime.time(14,0,0))):
                    sat_starttime_1 = common.getstringfromtime(ct.open_time ,"%I:%M %p")
                    sat_endtime_1 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    sat_id_1 = ct.id
                else:   
                    sat_starttime_2 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    sat_endtime_2 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    sat_id_2 = ct.id
                    
                sat_visitinghours = ""




    formA = SQLFORM.factory(
        Field('mon_day_chk', 'boolean', default=mon_day_chk),        
        Field('mon_lunch_chk', 'boolean', default=mon_lunch_chk),        
        Field('mon_del_chk', 'boolean', default=mon_del_chk),        
        Field('mon_starttime_1', 'string', default=mon_starttime_1,requires=IS_IN_SET(AMS)),
        Field('mon_endtime_1', 'string', default=mon_endtime_1,requires=IS_IN_SET(AMS)),
        Field('mon_starttime_2', 'string', default=mon_starttime_2,requires=IS_IN_SET(AMS)),
        Field('mon_endtime_2', 'string', default=mon_endtime_2,requires=IS_IN_SET(AMS)),
        Field('mon_visitinghours', 'string', default=mon_visitinghours),
        Field('mon_id_1', 'integer', default=mon_id_1),
        Field('mon_id_2', 'integer', default=mon_id_2),
        

        Field('tue_day_chk', 'boolean', default=tue_day_chk),        
        Field('tue_lunch_chk', 'boolean', default=tue_lunch_chk),        
        Field('tue_del_chk', 'boolean', default=tue_del_chk),        
        Field('tue_starttime_1', 'string', default=tue_starttime_1,requires=IS_IN_SET(AMS)),
        Field('tue_endtime_1', 'string', default=tue_endtime_1,requires=IS_IN_SET(AMS)),
        Field('tue_starttime_2', 'string', default=tue_starttime_2,requires=IS_IN_SET(AMS)),
        Field('tue_endtime_2', 'string', default=tue_endtime_2,requires=IS_IN_SET(AMS)),
        Field('tue_visitinghours', 'string', default=tue_visitinghours),
        Field('tue_id_1', 'integer', default=tue_id_1),
        Field('tue_id_2', 'integer', default=tue_id_2),

        Field('wed_day_chk', 'boolean', default=wed_day_chk),        
        Field('wed_lunch_chk', 'boolean', default=wed_lunch_chk),        
        Field('wed_del_chk', 'boolean', default=wed_del_chk),        
        Field('wed_starttime_1', 'string', default=wed_starttime_1,requires=IS_IN_SET(AMS)),
        Field('wed_endtime_1', 'string', default=wed_endtime_1,requires=IS_IN_SET(AMS)),
        Field('wed_starttime_2', 'string', default=wed_starttime_2,requires=IS_IN_SET(AMS)),
        Field('wed_endtime_2', 'string', default=wed_endtime_2,requires=IS_IN_SET(AMS)),
        Field('wed_visitinghours', 'string', default=wed_visitinghours),
        Field('wed_id_1', 'integer', default=wed_id_1),
        Field('wed_id_2', 'integer', default=wed_id_2),

        Field('thu_day_chk', 'boolean', default=thu_day_chk),        
        Field('thu_lunch_chk', 'boolean', default=thu_lunch_chk),        
        Field('thu_del_chk', 'boolean', default=thu_del_chk),        
        Field('thu_starttime_1', 'string', default=thu_starttime_1,requires=IS_IN_SET(AMS)),
        Field('thu_endtime_1', 'string', default=thu_endtime_1,requires=IS_IN_SET(AMS)),
        Field('thu_starttime_2', 'string', default=thu_starttime_2,requires=IS_IN_SET(AMS)),
        Field('thu_endtime_2', 'string', default=thu_endtime_2,requires=IS_IN_SET(AMS)),
        Field('thu_visitinghours', 'string', default=thu_visitinghours),
        Field('thu_id_1', 'integer', default=thu_id_1),
        Field('thu_id_2', 'integer', default=thu_id_2),

        Field('fri_day_chk', 'boolean', default=fri_day_chk),        
        Field('fri_lunch_chk', 'boolean', default=fri_lunch_chk),        
        Field('fri_del_chk', 'boolean', default=fri_del_chk),        
        Field('fri_starttime_1', 'string', default=fri_starttime_1,requires=IS_IN_SET(AMS)),
        Field('fri_endtime_1', 'string', default=fri_endtime_1,requires=IS_IN_SET(AMS)),
        Field('fri_starttime_2', 'string', default=fri_starttime_2,requires=IS_IN_SET(AMS)),
        Field('fri_endtime_2', 'string', default=fri_endtime_2,requires=IS_IN_SET(AMS)),
        Field('fri_visitinghours', 'string', default=fri_visitinghours),
        Field('fri_id_1', 'integer', default=fri_id_1),
        Field('fri_id_2', 'integer', default=fri_id_2),

        Field('sat_day_chk', 'boolean', default=sat_day_chk),        
        Field('sat_lunch_chk', 'boolean', default=sat_lunch_chk),        
        Field('sat_del_chk', 'boolean', default=sat_del_chk),        
        Field('sat_starttime_1', 'string', default=sat_starttime_1,requires=IS_IN_SET(AMS)),
        Field('sat_endtime_1', 'string', default=sat_endtime_1,requires=IS_IN_SET(AMS)),
        Field('sat_starttime_2', 'string', default=sat_starttime_2,requires=IS_IN_SET(AMS)),
        Field('sat_endtime_2', 'string', default=sat_endtime_2,requires=IS_IN_SET(AMS)),
        Field('sat_visitinghours', 'string', default=sat_visitinghours),
        Field('sat_id_1', 'integer', default=sat_id_1),
        Field('sat_id_2', 'integer', default=sat_id_2),

        #Field('sun_day_chk', 'boolean', default=sun_day_chk),        
        #Field('sun_lunch_chk', 'boolean', default=sun_lunch_chk),        
        #Field('sun_del_chk', 'boolean', default=sun_del_chk),        
        #Field('sun_starttime_1', 'string', default=sun_starttime_1,requires=IS_IN_SET(AMS)),
        #Field('sun_endtime_1', 'string', default=sun_endtime_1,requires=IS_IN_SET(AMS)),
        #Field('sun_starttime_2', 'string', default=sun_starttime_2,requires=IS_IN_SET(AMS)),
        #Field('sun_endtime_2', 'string', default=sun_endtime_2,requires=IS_IN_SET(AMS)),
        #Field('sun_visitinghours', 'string', default=sun_visitinghours),

        #Field('visitinghours', 'string', default=visitinghours),
        #Field('lunchbreak', 'string', default=lunchbreak)


    )

    if formA.accepts(request,session,keepvalues=True):

        visitinghours = ""
        lunchbreaks = ""

        ##Monday
        t1 = common.gettimefromstring(formA.vars.mon_starttime_1,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.mon_endtime_1,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)
        
        if(common.getboolean(formA.vars.mon_day_chk) == True):
            db(db.ops_timing.id == mon_id_1).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.mon_day_chk))
        else:
            db(db.ops_timing.id == mon_id_1).update(is_holiday = not common.getboolean(formA.vars.mon_day_chk))

        t1 = common.gettimefromstring(formA.vars.mon_starttime_2,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.mon_endtime_2,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)

        if(common.getboolean(formA.vars.mon_day_chk) == True):
            db(db.ops_timing.id == mon_id_2).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.mon_day_chk))
        else:
            db(db.ops_timing.id == mon_id_2).update(is_holiday = not common.getboolean(formA.vars.mon_day_chk))


        ##Tue
        t1 = common.gettimefromstring(formA.vars.tue_starttime_1,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.tue_endtime_1,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)
        
        if(common.getboolean(formA.vars.tue_day_chk) == True):
            db(db.ops_timing.id == tue_id_1).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.tue_day_chk))
        else:
            db(db.ops_timing.id == tue_id_1).update(is_holiday = not common.getboolean(formA.vars.tue_day_chk))

        t1 = common.gettimefromstring(formA.vars.tue_starttime_2,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.tue_endtime_2,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)

        if(common.getboolean(formA.vars.tue_day_chk) == True):
            db(db.ops_timing.id == tue_id_2).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.tue_day_chk))
        else:
            db(db.ops_timing.id == tue_id_2).update(is_holiday = not common.getboolean(formA.vars.tue_day_chk))

        ##Wed
        t1 = common.gettimefromstring(formA.vars.wed_starttime_1,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.wed_endtime_1,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)
        
        if(common.getboolean(formA.vars.wed_day_chk) == True):
            db(db.ops_timing.id == wed_id_1).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.wed_day_chk))
        else:
            db(db.ops_timing.id == wed_id_1).update(is_holiday = not common.getboolean(formA.vars.wed_day_chk))

        t1 = common.gettimefromstring(formA.vars.wed_starttime_2,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.wed_endtime_2,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)

        if(common.getboolean(formA.vars.wed_day_chk) == True):
            db(db.ops_timing.id == wed_id_2).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.wed_day_chk))
        else:
            db(db.ops_timing.id == wed_id_2).update(is_holiday = not common.getboolean(formA.vars.wed_day_chk))


        ##Thu
        t1 = common.gettimefromstring(formA.vars.thu_starttime_1,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.thu_endtime_1,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)
        
        if(common.getboolean(formA.vars.thu_day_chk) == True):
            db(db.ops_timing.id == thu_id_1).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.thu_day_chk))
        else:
            db(db.ops_timing.id == thu_id_1).update(is_holiday = not common.getboolean(formA.vars.thu_day_chk))

        t1 = common.gettimefromstring(formA.vars.thu_starttime_2,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.thu_endtime_2,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)

        if(common.getboolean(formA.vars.thu_day_chk) == True):
            db(db.ops_timing.id == thu_id_2).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.thu_day_chk))
        else:
            db(db.ops_timing.id == thu_id_2).update(is_holiday = not common.getboolean(formA.vars.thu_day_chk))
        
        ##Fri
        t1 = common.gettimefromstring(formA.vars.fri_starttime_1,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.fri_endtime_1,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)
        
        if(common.getboolean(formA.vars.fri_day_chk) == True):
            db(db.ops_timing.id == fri_id_1).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.fri_day_chk))
        else:
            db(db.ops_timing.id == fri_id_1).update(is_holiday = not common.getboolean(formA.vars.fri_day_chk))

        t1 = common.gettimefromstring(formA.vars.fri_starttime_2,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.fri_endtime_2,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)

        if(common.getboolean(formA.vars.fri_day_chk) == True):
            db(db.ops_timing.id == fri_id_2).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.fri_day_chk))
        else:
            db(db.ops_timing.id == fri_id_2).update(is_holiday = not common.getboolean(formA.vars.fri_day_chk))

        ##Sat
        t1 = common.gettimefromstring(formA.vars.sat_starttime_1,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.sat_endtime_1,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec) if(t1 != None) else datetime.time(0, 0, 0)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec) if(t2 != None) else datetime.time(0, 0, 0)
        
        if(common.getboolean(formA.vars.sat_day_chk) == True):
            db(db.ops_timing.id == sat_id_1).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.sat_day_chk))
        else:
            db(db.ops_timing.id == sat_id_1).update(is_holiday = not common.getboolean(formA.vars.sat_day_chk))

        t1 = common.gettimefromstring(formA.vars.sat_starttime_2,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.sat_endtime_2,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec) if(t1 != None) else datetime.time(0, 0, 0)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec) if(t2 != None) else datetime.time(0, 0, 0)

        if(common.getboolean(formA.vars.sat_day_chk) == True):
            db(db.ops_timing.id == sat_id_2).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.sat_day_chk))
        else:
            db(db.ops_timing.id == sat_id_2).update(is_holiday = not common.getboolean(formA.vars.sat_day_chk))


        db.commit()
        session.flash = 'Clinic timings added!'
        redirect(returnurl)                                  

    elif formA.errors:

        session.flash = 'Error in updating Doctor timings! ' + str(formA.errors)


    return dict(username=username,formheader=formheader,formA=formA, mon_day_chk=mon_day_chk,tue_day_chk=tue_day_chk,wed_day_chk=wed_day_chk,thu_day_chk=thu_day_chk,fri_day_chk=fri_day_chk,sat_day_chk=sat_day_chk,
                returnurl=returnurl, page=page, providerid=providerid, providername=providername,clinicname=clinicname,doctorname=doctorname,
                today_date = today_date, week_start=week_start, week_end=week_end 
                
                )

@auth.requires_membership('webadmin')
@auth.requires_login()
def clinic_pst_timings():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Clinic List"
    page = common.getpage1(request.vars.page)

    
    ref_code = request.vars.ref_code
    ref_id = int(common.getid(request.vars.ref_id))  #clinic id
    logger.loggerpms2.info("Enter clinic prospect timings " + ref_code + " " + str(ref_id))
    
    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]

    doctorname = ""
    
    returnurl = URL('clinic', 'list_prospect_clinics')

    page = 1

    mon_day_chk = False
    mon_lunch_chk = False
    mon_del_chk = False
    mon_starttime_1 = ""
    mon_endtime_1 = ""
    mon_starttime_2 = ""
    mon_endtime_2 = ""
    mon_visitinghours = ""

    tue_day_chk = False
    tue_lunch_chk = False
    tue_del_chk = False
    tue_starttime_1 = ""
    tue_endtime_1 = ""
    tue_starttime_2 = ""
    tue_endtime_2 = ""
    tue_visitinghours = ""

    wed_day_chk = False
    wed_lunch_chk = False
    wed_del_chk = False
    wed_starttime_1 = ""
    wed_endtime_1 = ""
    wed_starttime_2 = ""
    wed_endtime_2 = ""
    wed_visitinghours = ""

    thu_day_chk = False
    thu_lunch_chk = False
    thu_del_chk = False
    thu_starttime_1 = ""
    thu_endtime_1 = ""
    thu_starttime_2 = ""
    thu_endtime_2 = ""
    thu_visitinghours = ""

    fri_day_chk = False
    fri_lunch_chk = False
    fri_del_chk = False
    fri_starttime_1 = ""
    fri_endtime_1 = ""
    fri_starttime_2 = ""
    fri_endtime_2 = ""
    fri_visitinghours = ""

    sat_day_chk = False
    sat_lunch_chk = False
    sat_del_chk = False
    sat_starttime_1 = ""
    sat_endtime_1 = ""
    sat_starttime_2 = ""
    sat_endtime_2 = ""
    sat_visitinghours = ""

    sun_day_chk = False
    sun_lunch_chk = False
    sun_del_chk = False
    sun_starttime_1 = ""
    sun_endtime_1 = ""
    sun_starttime_2 = ""
    sun_endtime_2 = ""
    sun_visitinghours = ""
    
    mon_id_1 = 0
    mon_id_2 = 0
    
    tue_id_1 = 0
    tue_id_2 = 0

    wed_id_1 = 0
    wed_id_2 = 0

    thu_id_1 = 0
    thu_id_2 = 0

    fri_id_1 = 0
    fri_id_2 = 0

    sat_id_1 = 0
    sat_id_2 = 0
    

    visitinghours = 'Not Set'
    lunchbreak = 'Not Set'

    if(ref_id > 0):
        # need to get information from database and set the defauls
        
        
        #todays date
        today_date = datetime.date.today()   #yyyy-mm-dd
        
        #weeks start date
        week_start = today_date - timedelta(days=today_date.weekday())
        
        #weeks end date
        week_end = week_start + timedelta(days=6)
        
        #clinic details
        cln = db((db.clinic.id == ref_id) & (db.clinic.is_active == True)).select()
        clinicname = cln[0].name if(len(cln) > 0) else ""
        
        cts = db((db.ops_timing_ref.ref_code == 'CLN') & (db.ops_timing_ref.ref_id == ref_id) &\
                 (db.ops_timing.calendar_date >= week_start) &\
                 (db.ops_timing.calendar_date <= week_end) &\
                 (db.ops_timing.day_of_week != 'Sun') & (db.ops_timing.is_active == True)).\
            select(db.ops_timing.ALL, orderby=[db.ops_timing.day_of_week, db.ops_timing.open_time], left=db.ops_timing.on(db.ops_timing_ref.ops_timing_id == db.ops_timing.id))
        
        
        for ct in cts:
            if(ct.day_of_week == 'Mon'):
                mon_day_chk = not common.getboolean(ct.is_holiday)
                mon_lunch_chk = common.getboolean(ct.is_lunch)
                mon_del_chk = False

              
                
                
                if((ct.open_time >= datetime.time(0,0,0)) & (ct.open_time <= datetime.time(14,0,0))):

                    mon_starttime_1 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    mon_endtime_1 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    mon_id_1 = ct.id
                else:   
                    mon_starttime_2 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    mon_endtime_2 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    mon_id_2 = ct.id
                    
                mon_visitinghours = ""
        
            if(ct.day_of_week == 'Tue'):
                tue_day_chk =not common.getboolean(ct.is_holiday)
                tue_lunch_chk = common.getboolean(ct.is_lunch)
                tue_del_chk = False

              
                
                if((ct.open_time >= datetime.time(0,0,0)) & (ct.open_time <= datetime.time(14,0,0))):
                    tue_starttime_1 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    tue_endtime_1 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    tue_id_1 = ct.id
                    
                else:   
                    tue_starttime_2 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    tue_endtime_2 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    tue_id_2 = ct.id
                    
                tue_visitinghours = ""

            if(ct.day_of_week == 'Wed'):
                wed_day_chk = not common.getboolean(ct.is_holiday)
                wed_lunch_chk = common.getboolean(ct.is_lunch)
                wed_del_chk = False

         
                
                if((ct.open_time >= datetime.time(0,0,0)) & (ct.open_time <= datetime.time(14,0,0))):
                    wed_starttime_1 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    wed_endtime_1 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    wed_id_1 = ct.id
                else:   
                    wed_starttime_2 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    wed_endtime_2 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    wed_id_2 = ct.id
                    
                wed_visitinghours = ""

            if(ct.day_of_week == 'Thu'):
                thu_day_chk = not common.getboolean(ct.is_holiday)
                thu_lunch_chk = common.getboolean(ct.is_lunch)
                thu_del_chk = False

            
                if((ct.open_time >= datetime.time(0,0,0)) & (ct.open_time <= datetime.time(14,0,0))):
                    thu_starttime_1 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    thu_endtime_1 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    thu_id_1 = ct.id
                    
                else:   
                    thu_starttime_2 = common.getstringfromtime(ct.open_time ,"%I:%M %p")
                    thu_endtime_2 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    thu_id_2 = ct.id
                    
                thu_visitinghours = ""

            if(ct.day_of_week == 'Fri'):
                fri_day_chk = not common.getboolean(ct.is_holiday)
                fri_lunch_chk = common.getboolean(ct.is_lunch)
                fri_del_chk = False

             
                
                if((ct.open_time >= datetime.time(0,0,0)) & (ct.open_time <= datetime.time(14,0,0))):
                    fri_starttime_1 = common.getstringfromtime(ct.open_time ,"%I:%M %p")
                    fri_endtime_1 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    fri_id_1 = ct.id
                else:   
                    fri_starttime_2 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    fri_endtime_2 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    fri_id_2 = ct.id
                    
                fri_visitinghours = ""

            if(ct.day_of_week == 'Sat'):
                sat_day_chk = not common.getboolean(ct.is_holiday)
                sat_lunch_chk = common.getboolean(ct.is_lunch)
                sat_del_chk = False

                
                if((ct.open_time >= datetime.time(0,0,0)) & (ct.open_time <= datetime.time(14,0,0))):
                    sat_starttime_1 = common.getstringfromtime(ct.open_time ,"%I:%M %p")
                    sat_endtime_1 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    sat_id_1 = ct.id
                else:   
                    sat_starttime_2 = common.getstringfromtime(ct.open_time ,"%I:%M %p") 
                    sat_endtime_2 = common.getstringfromtime(ct.close_time ,"%I:%M %p")
                    sat_id_2 = ct.id
                    
                sat_visitinghours = ""




    formA = SQLFORM.factory(
        Field('mon_day_chk', 'boolean', default=mon_day_chk),        
        Field('mon_lunch_chk', 'boolean', default=mon_lunch_chk),        
        Field('mon_del_chk', 'boolean', default=mon_del_chk),        
        Field('mon_starttime_1', 'string', default=mon_starttime_1,requires=IS_IN_SET(AMS)),
        Field('mon_endtime_1', 'string', default=mon_endtime_1,requires=IS_IN_SET(AMS)),
        Field('mon_starttime_2', 'string', default=mon_starttime_2,requires=IS_IN_SET(AMS)),
        Field('mon_endtime_2', 'string', default=mon_endtime_2,requires=IS_IN_SET(AMS)),
        Field('mon_visitinghours', 'string', default=mon_visitinghours),
        Field('mon_id_1', 'integer', default=mon_id_1),
        Field('mon_id_2', 'integer', default=mon_id_2),
        

        Field('tue_day_chk', 'boolean', default=tue_day_chk),        
        Field('tue_lunch_chk', 'boolean', default=tue_lunch_chk),        
        Field('tue_del_chk', 'boolean', default=tue_del_chk),        
        Field('tue_starttime_1', 'string', default=tue_starttime_1,requires=IS_IN_SET(AMS)),
        Field('tue_endtime_1', 'string', default=tue_endtime_1,requires=IS_IN_SET(AMS)),
        Field('tue_starttime_2', 'string', default=tue_starttime_2,requires=IS_IN_SET(AMS)),
        Field('tue_endtime_2', 'string', default=tue_endtime_2,requires=IS_IN_SET(AMS)),
        Field('tue_visitinghours', 'string', default=tue_visitinghours),
        Field('tue_id_1', 'integer', default=tue_id_1),
        Field('tue_id_2', 'integer', default=tue_id_2),

        Field('wed_day_chk', 'boolean', default=wed_day_chk),        
        Field('wed_lunch_chk', 'boolean', default=wed_lunch_chk),        
        Field('wed_del_chk', 'boolean', default=wed_del_chk),        
        Field('wed_starttime_1', 'string', default=wed_starttime_1,requires=IS_IN_SET(AMS)),
        Field('wed_endtime_1', 'string', default=wed_endtime_1,requires=IS_IN_SET(AMS)),
        Field('wed_starttime_2', 'string', default=wed_starttime_2,requires=IS_IN_SET(AMS)),
        Field('wed_endtime_2', 'string', default=wed_endtime_2,requires=IS_IN_SET(AMS)),
        Field('wed_visitinghours', 'string', default=wed_visitinghours),
        Field('wed_id_1', 'integer', default=wed_id_1),
        Field('wed_id_2', 'integer', default=wed_id_2),

        Field('thu_day_chk', 'boolean', default=thu_day_chk),        
        Field('thu_lunch_chk', 'boolean', default=thu_lunch_chk),        
        Field('thu_del_chk', 'boolean', default=thu_del_chk),        
        Field('thu_starttime_1', 'string', default=thu_starttime_1,requires=IS_IN_SET(AMS)),
        Field('thu_endtime_1', 'string', default=thu_endtime_1,requires=IS_IN_SET(AMS)),
        Field('thu_starttime_2', 'string', default=thu_starttime_2,requires=IS_IN_SET(AMS)),
        Field('thu_endtime_2', 'string', default=thu_endtime_2,requires=IS_IN_SET(AMS)),
        Field('thu_visitinghours', 'string', default=thu_visitinghours),
        Field('thu_id_1', 'integer', default=thu_id_1),
        Field('thu_id_2', 'integer', default=thu_id_2),

        Field('fri_day_chk', 'boolean', default=fri_day_chk),        
        Field('fri_lunch_chk', 'boolean', default=fri_lunch_chk),        
        Field('fri_del_chk', 'boolean', default=fri_del_chk),        
        Field('fri_starttime_1', 'string', default=fri_starttime_1,requires=IS_IN_SET(AMS)),
        Field('fri_endtime_1', 'string', default=fri_endtime_1,requires=IS_IN_SET(AMS)),
        Field('fri_starttime_2', 'string', default=fri_starttime_2,requires=IS_IN_SET(AMS)),
        Field('fri_endtime_2', 'string', default=fri_endtime_2,requires=IS_IN_SET(AMS)),
        Field('fri_visitinghours', 'string', default=fri_visitinghours),
        Field('fri_id_1', 'integer', default=fri_id_1),
        Field('fri_id_2', 'integer', default=fri_id_2),

        Field('sat_day_chk', 'boolean', default=sat_day_chk),        
        Field('sat_lunch_chk', 'boolean', default=sat_lunch_chk),        
        Field('sat_del_chk', 'boolean', default=sat_del_chk),        
        Field('sat_starttime_1', 'string', default=sat_starttime_1,requires=IS_IN_SET(AMS)),
        Field('sat_endtime_1', 'string', default=sat_endtime_1,requires=IS_IN_SET(AMS)),
        Field('sat_starttime_2', 'string', default=sat_starttime_2,requires=IS_IN_SET(AMS)),
        Field('sat_endtime_2', 'string', default=sat_endtime_2,requires=IS_IN_SET(AMS)),
        Field('sat_visitinghours', 'string', default=sat_visitinghours),
        Field('sat_id_1', 'integer', default=sat_id_1),
        Field('sat_id_2', 'integer', default=sat_id_2),

        #Field('sun_day_chk', 'boolean', default=sun_day_chk),        
        #Field('sun_lunch_chk', 'boolean', default=sun_lunch_chk),        
        #Field('sun_del_chk', 'boolean', default=sun_del_chk),        
        #Field('sun_starttime_1', 'string', default=sun_starttime_1,requires=IS_IN_SET(AMS)),
        #Field('sun_endtime_1', 'string', default=sun_endtime_1,requires=IS_IN_SET(AMS)),
        #Field('sun_starttime_2', 'string', default=sun_starttime_2,requires=IS_IN_SET(AMS)),
        #Field('sun_endtime_2', 'string', default=sun_endtime_2,requires=IS_IN_SET(AMS)),
        #Field('sun_visitinghours', 'string', default=sun_visitinghours),

        #Field('visitinghours', 'string', default=visitinghours),
        #Field('lunchbreak', 'string', default=lunchbreak)


    )

    if formA.accepts(request,session,keepvalues=True):

        visitinghours = ""
        lunchbreaks = ""

        ##Monday
        t1 = common.gettimefromstring(formA.vars.mon_starttime_1,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.mon_endtime_1,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)
        
        if(common.getboolean(formA.vars.mon_day_chk) == True):
            db(db.ops_timing.id == mon_id_1).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.mon_day_chk))
        else:
            db(db.ops_timing.id == mon_id_1).update(is_holiday = not common.getboolean(formA.vars.mon_day_chk))

        t1 = common.gettimefromstring(formA.vars.mon_starttime_2,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.mon_endtime_2,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)

        if(common.getboolean(formA.vars.mon_day_chk) == True):
            db(db.ops_timing.id == mon_id_2).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.mon_day_chk))
        else:
            db(db.ops_timing.id == mon_id_2).update(is_holiday = not common.getboolean(formA.vars.mon_day_chk))


        ##Tue
        t1 = common.gettimefromstring(formA.vars.tue_starttime_1,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.tue_endtime_1,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)
        
        if(common.getboolean(formA.vars.tue_day_chk) == True):
            db(db.ops_timing.id == tue_id_1).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.tue_day_chk))
        else:
            db(db.ops_timing.id == tue_id_1).update(is_holiday = not common.getboolean(formA.vars.tue_day_chk))

        t1 = common.gettimefromstring(formA.vars.tue_starttime_2,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.tue_endtime_2,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)

        if(common.getboolean(formA.vars.tue_day_chk) == True):
            db(db.ops_timing.id == tue_id_2).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.tue_day_chk))
        else:
            db(db.ops_timing.id == tue_id_2).update(is_holiday = not common.getboolean(formA.vars.tue_day_chk))

        ##Wed
        t1 = common.gettimefromstring(formA.vars.wed_starttime_1,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.wed_endtime_1,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)
        
        if(common.getboolean(formA.vars.wed_day_chk) == True):
            db(db.ops_timing.id == wed_id_1).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.wed_day_chk))
        else:
            db(db.ops_timing.id == wed_id_1).update(is_holiday = not common.getboolean(formA.vars.wed_day_chk))

        t1 = common.gettimefromstring(formA.vars.wed_starttime_2,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.wed_endtime_2,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)

        if(common.getboolean(formA.vars.wed_day_chk) == True):
            db(db.ops_timing.id == wed_id_2).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.wed_day_chk))
        else:
            db(db.ops_timing.id == wed_id_2).update(is_holiday = not common.getboolean(formA.vars.wed_day_chk))


        ##Thu
        t1 = common.gettimefromstring(formA.vars.thu_starttime_1,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.thu_endtime_1,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)
        
        if(common.getboolean(formA.vars.thu_day_chk) == True):
            db(db.ops_timing.id == thu_id_1).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.thu_day_chk))
        else:
            db(db.ops_timing.id == thu_id_1).update(is_holiday = not common.getboolean(formA.vars.thu_day_chk))

        t1 = common.gettimefromstring(formA.vars.thu_starttime_2,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.thu_endtime_2,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)

        if(common.getboolean(formA.vars.thu_day_chk) == True):
            db(db.ops_timing.id == thu_id_2).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.thu_day_chk))
        else:
            db(db.ops_timing.id == thu_id_2).update(is_holiday = not common.getboolean(formA.vars.thu_day_chk))
        
        ##Fri
        t1 = common.gettimefromstring(formA.vars.fri_starttime_1,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.fri_endtime_1,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)
        
        if(common.getboolean(formA.vars.fri_day_chk) == True):
            db(db.ops_timing.id == fri_id_1).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.fri_day_chk))
        else:
            db(db.ops_timing.id == fri_id_1).update(is_holiday = not common.getboolean(formA.vars.fri_day_chk))

        t1 = common.gettimefromstring(formA.vars.fri_starttime_2,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.fri_endtime_2,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec)

        if(common.getboolean(formA.vars.fri_day_chk) == True):
            db(db.ops_timing.id == fri_id_2).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.fri_day_chk))
        else:
            db(db.ops_timing.id == fri_id_2).update(is_holiday = not common.getboolean(formA.vars.fri_day_chk))

        ##Sat
        t1 = common.gettimefromstring(formA.vars.sat_starttime_1,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.sat_endtime_1,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec) if(t1 != None) else datetime.time(0, 0, 0)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec) if(t2 != None) else datetime.time(0, 0, 0)
        
        if(common.getboolean(formA.vars.sat_day_chk) == True):
            db(db.ops_timing.id == sat_id_1).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.sat_day_chk))
        else:
            db(db.ops_timing.id == sat_id_1).update(is_holiday = not common.getboolean(formA.vars.sat_day_chk))

        t1 = common.gettimefromstring(formA.vars.sat_starttime_2,"%I:%M %p")
        t2 = common.gettimefromstring(formA.vars.sat_endtime_2,"%I:%M %p")
        dt1 = datetime.time(t1.tm_hour, t1.tm_min, t1.tm_sec) if(t1 != None) else datetime.time(0, 0, 0)
        dt2 = datetime.time(t2.tm_hour, t2.tm_min, t2.tm_sec) if(t2 != None) else datetime.time(0, 0, 0)

        if(common.getboolean(formA.vars.sat_day_chk) == True):
            db(db.ops_timing.id == sat_id_2).update(open_time =dt1, close_time = dt2, is_holiday = not common.getboolean(formA.vars.sat_day_chk))
        else:
            db(db.ops_timing.id == sat_id_2).update(is_holiday = not common.getboolean(formA.vars.sat_day_chk))


        db.commit()
        session.flash = 'Clinic timings added!'
        redirect(returnurl)                                  

    elif formA.errors:

        session.flash = 'Error in updating Doctor timings! ' + str(formA.errors)


    return dict(username=username,formheader=formheader,formA=formA, mon_day_chk=mon_day_chk,tue_day_chk=tue_day_chk,wed_day_chk=wed_day_chk,thu_day_chk=thu_day_chk,fri_day_chk=fri_day_chk,sat_day_chk=sat_day_chk,
                returnurl=returnurl, page=page, providerid=providerid, providername=providername,clinicname=clinicname,doctorname=doctorname,
                today_date = today_date, week_start=week_start, week_end=week_end 
                )


@auth.requires_membership('webadmin')
@auth.requires_login()
def list_prospect_clinics():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Clinic List"
    page = common.getpage1(request.vars.page)

    prev_ref_code = "PRV" if (common.getstring(request.vars.prev_ref_code) == "") else request.vars.prev_ref_code
    prev_ref_id = 0 if (common.getstring(request.vars.prev_ref_id) == "") else int(request.vars.prev_ref_id)

    
    ref_code = "PRV" if (common.getstring(request.vars.ref_code) == "") else request.vars.ref_code
    ref_id = 0 if (common.getstring(request.vars.ref_id) == "") else int(request.vars.ref_id)
    
    if(ref_id == 0):
        query = ((db.clinic_ref.ref_code == ref_code) & (db.clinic.is_active==True))
    else:
        query = ((db.clinic_ref.ref_code == ref_code)& (db.clinic_ref.ref_id == ref_id) & (db.clinic.is_active==True))
    
    fields=(
            db.clinic.id,       
            db.provider.provider,
            db.provider.providername,
            db.clinic.name,
            db.clinic.cell,
            db.clinic.city,
            db.clinic.pin
            
            
            )
    
    db.clinic.id.readonly = False
    
    headers={
       
        'provider.provider' : 'Prospect',
        'provider.providername' : 'Prospect Name',
        'clinic.name':'Clinic Name',
        'clinic.cell' : 'Cell',
        'clinic.city' : 'Cty',
        'clinic.pin' : 'Pin'
        
   
       
        }    
    left = [db.clinic.on(db.clinic.id==db.clinic_ref.clinic_id),db.provider.on(db.provider.id == db.clinic_ref.ref_id)]
    orderby = (db.clinic.clinic_ref)
    exportlist = dict( csv=False,csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    links = [
             lambda row: A('Update',_href=URL("clinic","update_clinic",vars=dict(page=page,ref_code=ref_code,ref_id=ref_id,clinicid=row.clinic.id))),
             lambda row: A('Bank Details',_href=URL("clinic","bank_clinic",vars=dict(page=page,ref_code=ref_code,ref_id=ref_id,clinicid=row.clinic.id))),
             lambda row: A('Clinic Images',_href=URL("clinic","list_clinic_images",vars=dict(page=page,ref_code="CLN",ref_id=row.clinic.id,prev_ref_code=ref_code,prev_ref_id=ref_id))),
             lambda row: A('Clinic Logo',_href=URL("clinic","new_logo",vars=dict(page=page,ref_code="CLN",ref_id=row.clinic.id,prev_ref_code=ref_code,prev_ref_id=ref_id))),
             lambda row: A('Clinic Timings',_href=URL("clinic","clinic_pst_timings",vars=dict(page=page,ref_code="CLN",ref_id=row.clinic.id,prev_ref_code=ref_code,prev_ref_id=ref_id))),
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
    isMDP = common.getboolean(common.getkeyvalue(request.vars,'isMDP','True'))

    ref_code = request.vars.ref_code
    ref_id = request.vars.ref_id
 
    prev_ref_code = common.getkeyvalue(request.vars,"prev_ref_code",ref_code)
    prev_ref_id = int(common.getid(common.getkeyvalue(request.vars,"prev_ref_id","0")))
    
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
    latitude = "" if(len(clinics) !=1 ) else common.getstring(clinics[0].latitude)
    longitude = "" if(len(clinics) !=1 ) else common.getstring(clinics[0].longitude)
    
    bank_id = 0 if(len(clinics) != 1) else int(common.getid(clinics[0].bank_id))
  
    
    
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
    
    #isMDP = True if(len(clinics) == 0) else common.getboolean(clinics[0].isMDP)
    
    formA = SQLFORM.factory(
        Field('clinic_ref','string',default=clinic_ref),
            
        Field('name','string',default=name),
        Field('address1','string',default=address1),
        Field('address2','string',default=address2),
        Field('address3','string',default=address3),
        Field('city', 'string',default=city,label='City',length=50,requires = IS_IN_SET(CITIES)),
        Field('st', 'string',default=st,label='State',length=50,requires = IS_IN_SET(STATES)),
        Field('pin','string',default=pin),

        Field('latitude','string',default=latitude),
        Field('longitude','string',default=longitude),
        
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
        
        Field('state_dental_registration','string',default=state_dental_registration),
        Field('registration_certificate','string',default=registration_certificate),
        
        Field('notes','text',default=notes),
        Field('bank_id','integer',default=bank_id),
        Field('isMDP','boolean', default=isMDP)
    )  
    
    
    mediaid = int(common.getid(clinics[0].logo_id if(len(clinics) > 0) else 0))
    mediaurl = URL('my_dentalplan','media','media_download',args=[mediaid])        
    
    
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

                        latitude=formA.vars.latitude if(formA.vars.latitude != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].latitude)),
                        longitude=formA.vars.longitude if(formA.vars.longitude != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].longitude)),
                        
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
                        computers=formA.vars.computers if(formA.vars.computers != "") else ("" if(len(clinics) == 0) else clinics[0].computers),
                        
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
                        bank_id = formA.vars.bank_id,
                        
                        state_dental_registration=formA.vars.rotary_endodontics if(formA.vars.state_dental_registration != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].state_dental_registration)),   
                        registration_certificate=formA.vars.registration_certificate if(formA.vars.registration_certificate != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].registration_certificate)),   
                        
                        notes=formA.vars.notes if(formA.vars.notes != "") else ("" if(len(clinics) == 0) else common.getstring(clinics[0].notes)),   

                        isMDP = common.getboolean(formA.vars.isMDP) if(formA.vars.isMDP != "") else (True if(len(clinics) == 0) else common.getboolean(clinics[0].isMDP)), 

                        is_active = True,\
                        modified_on = datetime.date.today(),\
                        modified_by = 1
        )   
        db.commit()
        

    elif formA.errors:
        i  =0
        logger.loggerpms2.info("Clinic Form A Rejected " + str(formA.errors))
        response.flash = 'Clinic formA has errors ' + str(formA.errors)
        
        
    returnurl = URL('clinic','list_clinic',vars=dict(isMDP=isMDP,page=page,ref_code=ref_code,ref_id=ref_id,prev_ref_code=prev_ref_code,prev_ref_id=prev_ref_id))
    return dict(username=username,returnurl=returnurl,formA=formA, formheader=formheader,clinicid=clinicid,authuser=authuser,page=page,mediaid=mediaid,mediaurl=mediaurl)    

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


def default_all_clinic_timing():
    
    logger.loggerpms2.info("default_all_clinic_timing")

    count = 0
    try:
        form = SQLFORM.factory(
            Field('fromyear','string',label='From Year', requires= IS_NOT_EMPTY(),default=common.getstringfromdate(datetime.datetime.today(),"%Y")),
            Field('toyear','string',label='To Year', requires= IS_NOT_EMPTY(),default=common.getstringfromdate(datetime.datetime.today(),"%Y")),
            Field('time1','string',label='From Time', requires= IS_NOT_EMPTY()),
            Field('time2','string',label='To Time', requires= IS_NOT_EMPTY())
            )    
    
        submit = form.element('input',_type='submit')
        submit['_value'] = 'Submit'    
    
        xfromyear = form.element('input',_id='no_table_fromyear')
        xfromyear['_class'] =  'w3-input w3-border w3-small'    
    
        xtoyear = form.element('input',_id='no_table_toyear')
        xtoyear['_class'] =  'w3-input w3-border w3-small'    
        days = ['Mon','Tue','Wed','Thu','Fri','Sat']
        
        error = 0
        if form.accepts(request,session,keepvalues=True):
                error = 0
                xfromyear = request.vars.fromyear
                xtoyear = request.vars.toyear
                timingObj = mdptimings.OPS_Timing(db)
                avars={}
                
                clns = db(db.clinic.is_active == True).select()
                
                for cln in clns:
                    avars = {}
                    avars["action"] = "new_all_ops_timing"
                    avars["ref_code"] = "CLN"
                    avars["ref_id"] = cln.id
                    avars["from_year"] = xfromyear
                    avars["to_year"] = xfromyear
                    daylst = []
                    dayobj = {}
                    dayobj["open_time"]=request.vars.time1
                    dayobj["close_time"]=request.vars.time2
                    daylst.append(dayobj)
                    
                    for day in days:
                        avars[day] = daylst

                    timinobj = mdptimings.OPS_Timing(db)
                    respobj = timingObj.new_all_ops_timing(avars)
                    db.commit()
                    
                        
    except Exception as e:
        logger.loggerpms2.info("default_all_clinic_timing Exception Error - " + str(e) + "\n" + str(e.message))
        error = "default_all_clinic_timing Exception Error - " + str(e)    
    
    
    
    return dict(form = form, error = error)



