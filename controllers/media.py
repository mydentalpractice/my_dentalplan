# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']
#CRYPT = current.globalenv["CRYPT"]

import requests
import urllib

import base64
import string
import random
import json

import datetime
import time
import calendar
from datetime import timedelta
from decimal import Decimal

import csv

from string import Template
import os;
import uuid
from uuid import uuid4


#import sys
#sys.path.append('modules')
from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import mail
from applications.my_pms2.modules  import mdpuser
from applications.my_pms2.modules  import mdpimage
from applications.my_pms2.modules  import mdpcustomer
from applications.my_pms2.modules  import mdpmedia

#from gluon.contrib import common
#from gluon.contrib import mail

from applications.my_pms2.modules import logger



def media_download():
    logger.loggerpms2.info("Enter media_download " + request.args(0))
    mediaid = int(common.getid(request.args(0)))
    ms = db(db.dentalimage.id == mediaid).select(db.dentalimage.uploadfolder,db.dentalimage.image)
    fullpath = "" if (len(ms) == 0) else os.path.join(ms[0].uploadfolder,ms[0].image)
    logger.loggerpms2.info("Exit Media download " + fullpath)
    response.stream(fullpath)

def my_download():
    base_path = request.args(0) # /images
    sub1 = request.args(1) # /provcode
    sub2 = subdirectory = request.args(2) # /patmember

    filename = request.args(3)

    fullpath = os.path.join(base_path,sub1,sub2, filename)
    #response.stream(os.path.join(request.folder, fullpath))
    response.stream(os.path.join(request.folder, request.args(0),request.args(1), request.args(2), request.args(3)))

def upload_media():
    
   
    return dict()

    
def upload_imagefile():


    form = SQLFORM.factory(
        Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY()),
        Field('icsvfile','input',label='CSV File'),
        Field('fcsvfile','file',label='CSV File')
        
    )    

    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    

    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'



    error = ""
    count = 0
    mediaurl = ""
    mediafile = ""

    if form.accepts(request,session,keepvalues=True):
        try:
            filename = request.vars.csvfile
            ifilename = request.vars.icsvfile
            ffilename = request.vars.fcsvfile
            redirect(URL('my_pms2', 'mdpapi','preupload', vars=dict(imagefile=filename)))
            o = mdpmedia.Media(db, 523, 'image', 'jpg')

            j = {
                "filename":filename,
                "memberid":str(1469),
                "patientid":str(1469),
                "treatmentid":str(24),
                "title":"test",
                "tooth":"1",
                "quadrant":"1",
                "mediadate":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y"),
                "description":"XXX",
                "appath":request.folder
                }

            #x= json.loads(o.upload_mediafile(filename, 1469, 1469, 24, "test", "1", 
                                             #"2", "03/12/2020","description", request.folder))
            
            x= json.loads(o.upload_mediafile(j))            

            mediaid = common.getkeyvalue(x,'mediaid',0)






            mediaurl = URL('my_dentalplan','media','media_download',\
                           args=[mediaid])



        except Exception as e:
            error = "Upload Audio Media File Exception Error - " + str(e)        



    return dict(form=form, mediaurl=mediaurl,mediafile=mediafile,count=count,error=error)   

def upload_videofile():


    form = SQLFORM.factory(
        Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
    )    

    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    

    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'



    error = ""
    count = 0
    mediaurl = ""
    mediafile = ""

    if form.accepts(request,session,keepvalues=True):
        try:
            filename = request.vars.csvfile


            o = mdpmedia.Media(db, 523, 'video', 'mp4')

            j = {
                "filename":filename,
                "memberid":str(1469),
                "patientid":str(1469),
                "treatmentid":str(24),
                "title":"test",
                "tooth":"1",
                "quadrant":"1",
                "mediadate":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y"),
                "description":"XXX",
                "appath":request.folder
                }

            #x= json.loads(o.upload_mediafile(filename, 1469, 1469, 24, "test", "1", 
                                             #"2", "03/12/2020","description", request.folder))
            
            x= json.loads(o.upload_mediafile(j))            


            mediaid = common.getkeyvalue(x,'mediaid',0)






            mediaurl = URL('my_dentalplan','media','media_download',\
                           args=[mediaid])



        except Exception as e:
            error = "Upload Audio Media File Exception Error - " + str(e)        



    return dict(form=form, mediaurl=mediaurl,mediafile=mediafile,count=count,error=error)    


def upload_audiofile():


    form = SQLFORM.factory(
        Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
    )    
 
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    

    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'
    xcsvfile['_type'] =  'file'

    

    error = ""
    count = 0
    mediaurl = ""
    mediafile = ""

    if form.accepts(request,session,keepvalues=True):
        try:
            filename = request.vars.csvfile
            

            o = mdpmedia.Media(db, 523, 'audio', 'mp3')
            
            j = {
                "filename":filename,
                "memberid":str(1469),
                "patientid":str(1469),
                "treatmentid":str(24),
                "title":"test",
                "tooth":"1",
                "quadrant":"1",
                "mediadate":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y"),
                "description":"XXX",
                "appath":request.folder
                }

            #x= json.loads(o.upload_mediafile(filename, 1469, 1469, 24, "test", "1", 
                                             #"2", "03/12/2020","description", request.folder))
            
            x= json.loads(o.upload_mediafile(j))            

            mediaid = common.getkeyvalue(x,'mediaid',0)






            mediaurl = URL('my_dentalplan','media','media_download',\
                           args=[mediaid])



        except Exception as e:
            error = "Upload Audio Media File Exception Error - " + str(e)        



    return dict(form=form, mediaurl=mediaurl,mediafile=mediafile,count=count,error=error)    


def upload_image():


    form = SQLFORM.factory(
        #Field('csvfile','string',label='CSV File'),
        Field('imagedata','text',label='Image Data')
    )    

    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    

    #xcsvfile = form.element('input',_id='no_table_csvfile')
    #xcsvfile['_class'] =  'w3-input w3-border w3-small'
 
    #ximgfile = form.element('input',_id='no_table_imagefile')
    #ximgfile['_class'] =  'w3-input w3-border w3-small'
    #ximgfile['_type'] =  'file'

 

    error = ""
    count = 0
    mediaurl = ""
    mediafile = ""

    if form.accepts(request,session,keepvalues=True):
        try:
            #filename = request.vars.csvfile

            file_content = None
            file_content = request.vars.imagedata
            #with open(filename, "rb") as imageFile:
                #file_content = base64.b64encode(imageFile.read())   	    

            o = mdpmedia.Media(db, 523, 'image', 'jpg')
            
            j = {
                        "mediadata":file_content,
                        "xmemberid":str(1469),
                        "xpatientid":str(1469),
                        "xtreatmentid":str(24),
                        "title":"test",
                        "xtooth":"1",
                        "xquadrant":"1",
                        "mediadate":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y"),
                        "description":"XXX",
                        "appath":request.folder,
                        "ref_code":"DOC",
                        "ref_id":str(26)
                        
                        }
            
            x= json.loads(o.upload_media(j)) 
            
            mediaid = common.getkeyvalue(x,'mediaid',0)
            mediaurl = URL('my_dentalplan','media','media_download',\
                           args=[mediaid])


        except Exception as e:
            error = "Upload Audio Exception Error - " + str(e)        


    return dict(form=form, mediafile=mediafile, mediaurl=mediaurl,count=count,error=error)  

def upload_video():


    form = SQLFORM.factory(
        Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY()),
        Field('videodata','textarea',label='Video Data')
    )    

    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    

    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'

    xtextarea = form.element('input',_id='no_table_videodata')
    xtextarea['_name'] =  'videodata'
    xtextarea["_maxlength"] = 100000

    error = ""
    count = 0
    mediaurl = ""
    mediafile = ""

    if form.accepts(request,session,keepvalues=True):
        try:
            filename = request.vars.csvfile

            file_content = None
        
            file_content = request.vars.videodata   
            #with open(filename, "rb") as imageFile:
                #file_content = base64.b64encode(imageFile.read())   	    

            o = mdpmedia.Media(db, 523, 'video', 'mp4')
            
            j = {
                "mediadata":file_content,
                "memberid":str(1469),
                "patientid":str(1469),
                "treatmentid":str(24),
                "title":"test",
                "tooth":"1",
                "quadrant":"1",
                "mediadate":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y"),
                "description":"XXX",
                "appath":request.folder
                }

                      
            #x= json.loads(o.upload_media(file_content, 1469, 1469, 24, "test", "1", 
                                         #"2", "03/12/2020","description", request.folder))
            
            x= json.loads(o.upload_media(j))         
            mediaid = common.getkeyvalue(x,'mediaid',0)







            mediaurl = URL('my_dentalplan','media','media_download',\
                           args=[mediaid])


        except Exception as e:
            error = "Upload Audio Exception Error - " + str(e)        


    return dict(form=form, mediafile=mediafile, mediaurl=mediaurl,count=count,error=error)    


def upload_audio():


    form = SQLFORM.factory(
        Field('csvfile','string',label='CSV File'),
        
        Field('audiodata','textarea',label='Audio Data')
        
    )    

    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    

    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'
  
    xtextarea = form.element('input',_id='no_table_audiodata')
    xtextarea['_name'] =  'audiodata'
    xtextarea["_maxlength"] = 100000

    error = ""
    count = 0
    mediaurl = ""
    mediafile = ""

    if form.accepts(request,session,keepvalues=True):
        try:
            filename = request.vars.csvfile

            file_content = None
        
            file_content = request.vars.audiodata            
            #with open(filename, "rb") as imageFile:
                #file_content = base64.b64encode(imageFile.read())   	    

            o = mdpmedia.Media(db, 523, 'audio', 'mp3')
            j = {
                "mediadata":file_content,
                "xmemberid":str(1469),
                "xpatientid":str(1469),
                "xtreatmentid":str(24),
                "title":"test",
                "xtooth":"1",
                "xquadrant":"1",
                "mediadate":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y"),
                "description":"XXX",
                "appath":request.folder,
                "ref_code":"DOC",
                "ref_id":str(25)
                
                }            
            
           
            
            #x= json.loads(o.upload_media(file_content, 1469, 1469, 24, "test", "1", 
                                         #"2", "03/12/2020","description", request.folder))
            
            x= json.loads(o.upload_media(j))            

            mediaid = common.getkeyvalue(x,'mediaid',0)
            mediaurl = URL('my_dentalplan','media','media_download',\
                           args=[mediaid])


        except Exception as e:
            error = "Upload Audio Exception Error - " + str(e)        


    return dict(form=form, mediafile=mediafile, mediaurl=mediaurl,count=count,error=error)   



def new_media():
    
    logger.loggerpms2.info("Enter New Media - for Prospect, Provider, Clinic Images (MyDentalPlan")
    
    mediatype = common.getkeyvalue(request.vars, 'mediatype','image')
    mediaformat = common.getkeyvalue(request.vars, 'mediaformat','jpg')

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
