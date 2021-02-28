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
    
    clinicid = 0 if((common.getstring(request.vars.clinicid))) else request.vars.clinicid
    
    rows = db(db.clinic.id == clinicid).select()
    
    
 
    crud.settings.detect_record_change = False
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('clinic','update_clinic',vars=dict(page=common.getgridpage(request.vars),clinicid=clinicid))

    db.prospect.sitekey.writable = False

    formA = crud.update(db.clinic, clinicid,cast=int)    
    
    returnurl = URL('clinic','list_clinic',vars=dict(page=page,ref_code=ref_code,ref_id=ref_id))
    return dict(username=username,returnurl=returnurl,formA=formA, formheader=formheader,clinicid=clinicid,authuser=authuser,ref_code=ref_code,ref_id=ref_id,page=page)    