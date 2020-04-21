# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)


import os;


#import sys
#sys.path.append('modules')
from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import logger
#from gluon.contrib import common

@auth.requires_membership('webadmin')
@auth.requires_login()
def list_procedurepriceplan():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    providerid = int(common.getid(request.vars.providerid))
    
    fields=(db.vw_hmoprocedurepriceplan.procedurepriceplancode,db.vw_hmoprocedurepriceplan.procedurecode,db.vw_hmoprocedurepriceplan.shortdescription,\
            db.vw_hmoprocedurepriceplan.ucrfee,db.vw_hmoprocedurepriceplan.procedurefee,db.vw_hmoprocedurepriceplan.copay,\
            db.vw_hmoprocedurepriceplan.inspays,db.vw_hmoprocedurepriceplan.companypays)
    
    headers={
             'vw_hmoprocedurepriceplan.procedurepriceplancode':'Price Plan Code',
             'vw_hmoprocedurepriceplan.procedurecode':'Procedure',
             'vw_hmoprocedurepriceplan.shortdescription':'Description',
             'vw_hmoprocedurepriceplan.ucrfee':'UCR',
             'vw_hmoprocedurepriceplan.procedurefee':'Procedure Fee',
             'vw_hmoprocedurepriceplan.copay':'Copay',
             'vw_hmoprocedurepriceplan.inspays':'Ins. Pays',
             'vw_hmoprocedurepriceplan.companypays':'Co. Pays',
            }


    maxtextlengths = {'vw_hmoprocedurepriceplan.shortdescription':128}
    
    db.vw_hmoprocedurepriceplan.id.readable = False
    db.vw_hmoprocedurepriceplan.providerid.readable = False
    db.vw_hmoprocedurepriceplan.hmoplancode.readable = False
    #db.vw_hmoprocedurepriceplan.shortdescription.readable = False
    #db.vw_hmoprocedurepriceplan.ucrfee.readable = False
    #db.vw_hmoprocedurepriceplan.procedurefee.readable = False
    #db.vw_hmoprocedurepriceplan.copay.readable = False
    db.vw_hmoprocedurepriceplan.companypays.readable = False
    #db.vw_hmoprocedurepriceplan.inspays.readable = False
    db.vw_hmoprocedurepriceplan.is_active.readable = False
    

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    if(providerid == 0):
        query = (db.vw_hmoprocedurepriceplan.is_active==True)
    else:
        query = ((db.vw_hmoprocedurepriceplan.providerid == providerid) & (db.vw_hmoprocedurepriceplan.is_active==True))

    orderby = (db.vw_hmoprocedurepriceplan.procedurepriceplancode)

    links = [lambda row: A('Edit',_href=URL("plan","update_procedurepriceplan",vars=dict(procedurepriceplanid=row.id,providerid=providerid))), \
             lambda row: A('Delete',_href=URL("plan","del_procedurepriceplan",vars=dict(procedurepriceplanid=row.id,providerid=providerid)))]

    form = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             exportclasses=exportlist,
                             maxtextlengths=maxtextlengths,
                             orderby=orderby,
                             links_in_grid=True,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=True
                            )
    returnurl = URL('default','index')
    return dict(username=username, returnurl=returnurl,form=form)
    


@auth.requires_membership('webadmin')
@auth.requires_login()
def new_procedurepriceplan():
    username = auth.user.first_name + ' ' + auth.user.last_name
    providerid = int(common.getid(request.vars.providerid))
    
    formA = SQLFORM.factory(
          Field('procedurepriceplancode',  'string', unique=True, default="", requires=[IS_NOT_EMPTY()]),
          Field('procedurecode', 'string', requires=IS_IN_DB(db(db.dentalprocedure.is_active == True),db.dentalprocedure.dentalprocedure, '%(shortdescription)s (%(dentalprocedure)s)')),
          Field('ucrfee', 'double', default=0),
          Field('procedurefee', 'double', default=0),
          Field('copay', 'double', default=0),
          Field('companypays', 'double', default=0),
          Field('inspays', 'double', default=0)
      )
    
    if formA.process().accepted:
        xid = db.procedurepriceplan.insert(providerid=providerid, procedurepriceplancode=request.vars.procedurepriceplancode,\
            procedurecode=request.vars.procedurecode, ucrfee=request.vars.ucrfee,procedurefee=request.vars.procedurefee,\
            copay=request.vars.copay,companypays=request.vars.companypays,inspays=request.vars.inspays,is_active = True,\
            created_by=1, created_on = datetime.date.today(), modified_by=1, modified_on = datetime.date.today())
        redirect(URL('plan','new_procedurepriceplan',vars=dict(providerid = providerid)))
        response.flash = "Procedure Price Plan added!"
    else:
        response.flash = "Error adding Procedure Price Plan"
    
    returnurl = URL('plan', 'list_procedurepriceplan', vars=dict(providerid=providerid))    
    return dict(formA=formA, username=username, returnurl=returnurl, providerid=providerid)

@auth.requires_membership('webadmin')
@auth.requires_login()
def update_procedurepriceplan():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    procedurepriceplanid = int(common.getid(request.vars.procedurepriceplanid))
    
    providerid = int(common.getid(request.vars.providerid))
    
    rows = None
    if(providerid == 0):
        rows = db((db.procedurepriceplan.id == procedurepriceplanid) & (db.procedurepriceplan.is_active == True)).select()
    else:
        rows = db((db.procedurepriceplan.id == procedurepriceplanid) & (db.procedurepriceplan.providerid == providerid) & (db.procedurepriceplan.is_active == True)).select()

    procedurepriceplancode = ""
    procedurecode = ""
  
    ucrfee = 0
    procedurefee= 0
    inspays = 0
    copay = 0
    companypays = 0
    
    if(len(rows)>0):
        procedurepriceplancode = common.getstring(rows[0].procedurepriceplancode)
        procedurecode = common.getstring(rows[0].procedurecode)
        ucrfee = float(common.getvalue(rows[0].ucrfee))
        procedurefee = float(common.getvalue(rows[0].procedurefee))
        copay = float(common.getvalue(rows[0].copay))
        inspays = float(common.getvalue(rows[0].inspays))
        companypays = float(common.getvalue(rows[0].companypays))
        
    formA = SQLFORM.factory(
          Field('procedurepriceplancode',  'string', unique=True, default=procedurepriceplancode, requires=[IS_NOT_EMPTY()]),
          Field('procedurecode', 'string', default =procedurecode, requires=IS_IN_DB(db(db.dentalprocedure.is_active == True),db.dentalprocedure.dentalprocedure, '%(shortdescription)s (%(dentalprocedure)s)')),
          Field('ucrfee', 'double', default=ucrfee),
          Field('procedurefee', 'double', default=procedurefee),
          Field('copay', 'double', default=copay),
          Field('companypays', 'double', default=companypays),
          Field('inspays', 'double', default=inspays)
      )
    

    if formA.process().accepted:
        db(db.procedurepriceplan.id == procedurepriceplanid).update(procedurepriceplancode=request.vars.procedurepriceplancode,\
            procedurecode=request.vars.procedurecode, ucrfee=request.vars.ucrfee,procedurefee=request.vars.procedurefee,\
            copay=request.vars.copay,companypays=request.vars.companypays,inspays=request.vars.inspays)
        db.commit()
        
        redirect(URL('plan','list_procedurepriceplan',vars=dict(providerid = providerid)))
        response.flash = "Procedure Price Plan update!"
    else:
        response.flash = "Error update Procedure Price Plan"
    
    returnurl = URL('plan', 'list_procedurepriceplan', vars=dict(providerid=providerid))    
    return dict(formA=formA, username=username, returnurl=returnurl)

@auth.requires_membership('webadmin')
@auth.requires_login()
def del_procedurepriceplan():
    
    procedurepriceplanid = int(common.getid(request.vars.procedurepriceplanid))
    providerid = int(common.getid(request.vars.providerid))
    
    rows = db(db.procedurepriceplan.id == procedurepriceplanid).select()
    if(len(rows) == 0):
        raise HTTP(400,"Nothing to delete ")

    name = rows[0].procedurepriceplancode
    
    form = FORM.confirm('Yes?',{'No':URL('plan','list_procedurepriceplan', vars=dict(providerid=providerid))})


    if form.accepted:
        db(db.procedurepriceplan.id == procedurepriceplanid).update(is_active=False)
        redirect(URL('plan','list_procedurepriceplan', vars=dict(providerid=providerid)))
    
    return dict(form=form,name=name)
    


#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def list_plan():
    username = ""
    returnurl  = ""
    form = None
    formheader = ""
    
   
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Plan List"


    fields=(db.hmoplan.hmoplancode,db.hmoplan.groupregion,db.hmoplan.name)
    headers={'hmoplan.hmoplancode':'Plan Code',
             #'hmoplan.groupregion':'Region',
             'hmoplan.name':'Name'
            }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)
    selectable = None
    links = [lambda row: A('Update',_href=URL("plan","update_plan",args=[row.id])), lambda row: A('Delete',_href=URL("plan","delete_plan",args=[row.id]))]
    
    
    
    query = (db.hmoplan.is_active==True)
    #left  = [db.groupregion.on(db.groupregion.id==db.hmoplan.groupregion)]
    orderby = (db.hmoplan.hmoplancode|db.hmoplan.groupregion)
    
    db.hmoplan.planfile.readable = False
    db.hmoplan.welcomeletter.readable = False
    db.hmoplan.groupregion.readable = False
    #db.groupregion.id.readable = False
    #db.groupregion.groupregion.readable = False
    #db.groupregion.region.readable = False
        
    try:    
        form = SQLFORM.grid(query=query,
                                 headers=headers,
                                 fields=fields,
                                 links=links,
                                 exportclasses=exportlist,
                                 orderby=orderby,
                                 links_in_grid=True,
                                 create=False,
                                 deletable=False,
                                 editable=False,
                                 details=False,
                                 user_signature=True
                                )
        
        returnurl = URL('default','index')
        
    except AttributeError, Argument:
        formheader = "AttributeError Error " + str(Argument)
        logger.logger.info("AttributeError Errorr " + str(Argument))
        
        
    return dict(username=username, returnurl=returnurl,form=form, formheader=formheader)

    
    
#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def create_plan():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    files = os.listdir(os.path.join(request.folder, 'templates/plans'))
    options=[planfile for planfile in files] 
    
    letters = os.listdir(os.path.join(request.folder, 'templates/welcomeletter'))
    letteroptions=[welcomeletter for welcomeletter in letters] 
    
    
    formA = SQLFORM.factory(
          Field('groupregion',  default=1, requires=IS_IN_DB(db(db.groupregion.is_active == True),db.groupregion.id, '%(region)s (%(groupregion)s)')),
          Field('hmoplancode', 'string', length=20, unique=True, requires=IS_NOT_EMPTY(error_message='cannot be empty!'), label='Plan Code'),
          Field('name', 'string',  default='',  label='Plan'),
          Field('planfile',  'list:string', requires=IS_IN_SET(options)),
          Field('welcomeletter',  'list:string', default='MyDentalPlanMemberWelcomeLetter.html' ,requires=IS_IN_SET(letteroptions))
      )
    
    if formA.process().accepted:
        x = db.hmoplan.insert(hmoplancode=request.post_vars.hmoplancode,name=request.post_vars.name,groupregion=request.post_vars.groupregion,
                              planfile=request.post_vars.planfile,welcomeletter=request.post_vars.welcomeletter)
        redirect(URL('plan','update_plan',args=[x]))
    elif formA.errors:
        response.flash = 'form has errors'
    
    returnurl = URL('plan','list_plan')
    return dict(username=username, returnurl=returnurl, formA=formA)   

#IB 05292016
@auth.requires_membership('webadmin')    
@auth.requires_login()
def update_plan():
   
    username = auth.user.first_name + ' ' + auth.user.last_name

    if(len(request.args) == 0):
        raise HTTP(403,"Error in Plan Update - No Plan to update-1")

    
    planid = int(common.getid(request.args[0]))
    
    plans = db(db.hmoplan.id == planid).select()
    if(len(plans)==0):
        raise HTTP(403,"Error in Plan Update - No Plan to update-2")
    
    files = os.listdir(os.path.join(request.folder, 'templates/plans'))
    options=[planfile for planfile in files] 

    letters = os.listdir(os.path.join(request.folder, 'templates/welcomeletter'))
    letteroptions=[welcomeletter for welcomeletter in letters] 
    
    
    formA = SQLFORM.factory(
          Field('groupregion',  default=plans[0]["hmoplan.groupregion"], requires=IS_IN_DB(db(db.groupregion.is_active == True),db.groupregion.id, '%(region)s (%(groupregion)s)')),
          Field('hmoplancode', 'string', default=plans[0]["hmoplan.hmoplancode"],length=20, unique=True, requires=IS_NOT_EMPTY(error_message='cannot be empty!'), label='Plan Code'),
          Field('name', 'string',  default=plans[0]["hmoplan.name"],  label='Plan'),
          Field('procedurepriceplancode', 'string',  default=plans[0]["hmoplan.procedurepriceplancode"],  label='Procedure Price Plan',\
                requires=IS_IN_DB(db(db.vw_procedurepriceplancode.id >0),db.vw_procedurepriceplancode.procedurepriceplancode, '%(procedurepriceplancode)s')),
          Field('planfile',  'list:string', default=plans[0]["hmoplan.planfile"],requires=IS_IN_SET(options)),
          Field('welcomeletter',  'list:string',  default=plans[0]["hmoplan.welcomeletter"], requires=IS_IN_SET(letteroptions))
          
      )    
    
    #formA.element('select[name=planfile]')['_style']='height:50px'
    
    if formA.process(keepvalues=True).accepted:
        db(db.hmoplan.id == planid).update(hmoplancode=request.post_vars.hmoplancode,name=request.post_vars.name,\
                                           groupregion=request.post_vars.groupregion, planfile=request.post_vars.planfile,\
                                           procedurepriceplancode=request.vars.procedurepriceplancode,\
                                           welcomeletter=request.post_vars.welcomeletter)
        db.commit()
    elif formA.errors:
        response.flash = 'form has errors'    
           
    ## Display Co-Pay List for this plan
    fields=(db.copay.region,db.dentalprocedure.dentalprocedure,db.copay.procedureucrfee,db.copay.procedurefee,db.hmoplan.hmoplancode,db.copay.copay)

    headers={
             'copay.region':'Region',
             'dentalprocedure.dentalprocedure':'Procedure Code',
             'copay.procedureucrfee': 'UCR Fee',
             'copay.procedurefee': 'Procedure Fee',
             'copay.copay':'Co-Pay'
             }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)
    
    
    links = [lambda row: A('Update',_href=URL("plan","update_plancopay",vars=dict(copayid=row.copay.id,planid=planid))), lambda row: A('Delete',_href=URL("plan","delete_plancopay",vars=dict(copayid=row.copay.id,planid=planid)))]
   
    query = (db.copay.hmoplan == planid) & (db.copay.is_active==True)
    
    left =    [db.hmoplan.on(db.hmoplan.id==db.copay.hmoplan), db.dentalprocedure.on(db.dentalprocedure.id==db.copay.dentalprocedure)]
    
    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             left=left,
                             exportclasses=exportlist,
                             selectable=False,
                             searchable = False,
                             links_in_grid=True,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )

    
    
    ## redirect on Items, with PO ID and return URL
    returnurl = URL('plan','list_plan')
    return dict(username=username,returnurl=returnurl,formA=formA, formB=formB, planid=planid)




@auth.requires_membership('webadmin') 
@auth.requires_login()
def delete_plan():
    if(len(request.args[0]) == 0):
        raise HTTP(400,"Nothing to delete ")
    name = None
    try:
        planid = int(request.args[0])
        rows = db(db.hmoplan.id == planid).select()
        if(len(rows) == 0):
            raise HTTP(400,"Nothing to delete ")
        name = rows[0].name
    except Exception, e:
        raise HTTP(400,e.message)

    form = FORM.confirm('Yes?',{'No':URL('plan','list_plan')})


    if form.accepted:
        db(db.hmoplan.id == planid).update(is_active=False)
        redirect(URL('plan','list_plan'))

    return dict(form=form,name=name)










#IB 05292016
@auth.requires_membership('webadmin')    
@auth.requires_login()   
def create_plancopay():
    ## Add Prcoedure form - 
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    planid = int(common.getid(request.vars.planid))
    plans = db(db.hmoplan.id == planid).select()
    regionid = int(common.getid(plans[0].groupregion))
    
    
    db.copay.region.requires = IS_IN_DB(db(db.groupregion.is_active == True),db.groupregion.id, '%(region)s (%(groupregion)s)')
    db.copay.region.default = regionid
    
    db.copay.hmoplan.default = planid

    db.copay.procedureucrfee.writable = True
    db.copay.procedureucrfee.readable = False

    crud.settings.formstyle='table2cols'
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.create_next = URL('plan','create_plancopay',vars=dict(planid=planid))
    formA = crud.create(db.copay)  
    formA.add_button("cancel",URL('plan','update_plan',args=[planid]))

    
  
    
    ds = db(db.dentalprocedure.is_active == True).select(orderby='dentalprocedure')
    rows = db(db.dentalprocedure.dentalprocedure == 'Select').select()
    if(len(rows)>0):
        procedureid = int(rows[0].id)
    else:
        procedureid = 0
        
    returnurl = URL('plan','list_plan')    
    return dict(username=username,returnurl=returnurl,formA=formA,planid=planid,ds=ds,procedureid=procedureid)  

#IB 05292016
@auth.requires_membership('webadmin')    
@auth.requires_login()   
def update_plancopay():
    ## Add Prcoedure form - 
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    
    copayid = int(common.getid(request.vars.copayid))
    planid = int(common.getid(request.vars.planid))
    plans    = db(db.hmoplan.id == planid).select()
    regionid = int(common.getid(plans[0].groupregion))        
    
    
    db.copay.region.requires = IS_IN_DB(db(db.groupregion.is_active == True),db.groupregion.id, '%(region)s (%(groupregion)s)')
    db.copay.region.default = regionid
    db.copay.region.writable = False
    
    db.copay.hmoplan.default = planid
    db.copay.hmoplan.writable = False
    
    db.copay.procedureucrfee.writable = False
    db.copay.shortdescription.writable = False
    db.copay.dentalprocedure.writable = False
    
    
    crud.settings.formstyle='table2cols'
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('plan','update_plan',args=[planid])
    formA = crud.update(db.copay, copayid,cast=int) 
    formA.add_button("cancel",URL('plan','update_plan',args=[planid]))     ## return cancel_returnURL    
 
    
    ds = db(db.dentalprocedure.is_active == True).select(orderby='dentalprocedure')
    
    rows = db(db.copay.id == copayid).select()
    if(len(rows)>0):
        procedureid = int(rows[0].dentalprocedure)
    else:
        procedureid = 0
    
    returnurl = URL('plan','list_plan')
    return dict(username=username, returnurl=returnurl,formA=formA,planid=planid,ds=ds,procedureid=procedureid)


@auth.requires_membership('webadmin')    
@auth.requires_login()
def delete_plancopay():

    username = auth.user.first_name + ' ' + auth.user.last_name
    copayid = int(common.getid(request.vars.copayid))
    planid = int(common.getid(request.vars.planid))

    form = FORM.confirm('Yes?',{'No':URL('plan','update_plan',args=[planid])})


    if form.accepted:
        db(db.copay.id == copayid).update(is_active=False)
        redirect(URL('plan','update_plan',args=[planid]))

    return dict(form=form)


@auth.requires_login()
def xplanname():

    i = 10;

    return dict(form=form)

@auth.requires_login()
def xview_plancopay():
    ## Add Prcoedure form -
    copayid = 0
    planid = 0
    if(len(request.args)>0):
        copayid = request.args[0]
        planid = request.args[1]

    crud.settings.formstyle='table2cols'
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.create_next = URL('plan','view_plan',args=[planid])
    formA = crud.update(db.copay, request.args[0],cast=int)

    ## redirect on Cancel
    if session.create_plan_url == None:
        formA.add_button("cancel",URL('default','index', args=''))  ## return to home screen
    else:
        formA.add_button("cancel",session.create_plancode_url)     ## return cancel_returnURL
        session.create_plan_url = None                         ## reset session key

    ## redirect on Items, with PO ID and return URL
    plancodeid = formA.vars.id
    session.plan_returnURL = URL("plan","list_plan")
    session.mode = "lookup"
    return dict(formA=formA,planid=planid)

@auth.requires_login()
def xdelete_copay():
    row = db.copay[request.args[0]]
    if request.vars.confirm:
        db(db.copay.id == row.id).delete()
        form=None
    else:
        form = BUTTON('really delete',_onclick='document.location="%s"'%URL(vars=dict(confirm=True),args=[row.id]))

    return dict(form=form)

@auth.requires_login()
def xview_copay():
    ## Add Prcoedure form -
    crud.settings.formstyle='table2cols'
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.create_next = URL('plan','list_copay',args='')
    formA = crud.update(db.copay, request.args[0],cast=int)

    ## redirect on Cancel
    if session.create_plan_url == None:
        formA.add_button("cancel",URL('default','index', args=''))  ## return to home screen
    else:
        formA.add_button("cancel",session.create_plancode_url)     ## return cancel_returnURL
        session.create_plan_url = None                         ## reset session key

    ## redirect on Items, with PO ID and return URL
    plancodeid = formA.vars.id
    session.plan_returnURL = URL("plan","list_copay")
    session.mode = "lookup"
    return dict(formA=formA)

@auth.requires_login()
def xview_plan():


    planid = int(request.args[0])
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('plan','list_plan',args='')

    db.hmoplan.hmoplancode.writable = False
    db.hmoplan.name.writable = False

    formA = crud.update(db.hmoplan, request.args[0],cast=int)
    formA.add_button("Cancel",URL('plan','list_plan',args=''))     ## return cancel_returnURL

    fields=(db.dentalprocedure.dentalprocedure,db.dentalprocedure.procedurefee,db.hmoplan.hmoplancode,db.copay.copay)

    headers={'dentalprocedure.dentalprocedure':'Procedure Code',
             'hmoplan.hmoplancode': 'Plan',
             'dentalprocedure.procedurefee': 'Standard Fee',
             'copay.copay':'Co-Pay'
             }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)


    links = [lambda row: A('View',_href=URL("plan","view_plancopay",args=[row.copay.id,planid])),lambda row: A('Update',_href=URL("plan","update_plancopay",args=[row.copay.id,planid])), lambda row: A('Delete',_href=URL("plan","delete_plancopay",args=[row.copay.id,planid]))]
    links=None
    query =   query = (db.copay.hmoplan == planid) & (db.copay.is_active==True)

    left =    [db.hmoplan.on(db.hmoplan.id==db.copay.hmoplan), db.dentalprocedure.on(db.dentalprocedure.id==db.copay.dentalprocedure)]

    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             left=left,
                             exportclasses=exportlist,
                             links_in_grid=True,
                             selectable=False,
                             searchable=False,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )

    return dict(formA=formA, formB=formB, planid=planid)


@auth.requires_login()
def xlist_copay():



    formheader = "Copay List"

    selectable = None

    fields=(db.dentalprocedure.dentalprocedure,db.dentalprocedure.procedurefee,db.hmoplan.hmoplancode,db.copay.copay)

    headers={'dentalprocedure.dentalprocedure':'Procedure Code',
             'hmoplan.hmoplancode': 'Plan',
             'dentalprocedure.procedurefee': 'Standard Fee',
             'copay.copay':'Co-Pay'
             }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)


    links = [lambda row: A('View',_href=URL("plan","view_copay",args=[row.copay.id]))]

    query = (db.copay.is_active==True)


    left =    [db.hmoplan.on(db.hmoplan.id==db.copay.hmoplan), db.dentalprocedure.on(db.dentalprocedure.id==db.copay.dentalprocedure)]

    ## called from menu
    if len(request.args) == 0:
        if request.vars.selectable:
            selectable = lambda ids : redirect(URL('plan','update_plan',args=ids))

        form = SQLFORM.grid(query=query,
                                 headers=headers,
                                 fields=fields,
                                 links=links,
                                 left=left,
                                 exportclasses=exportlist,
                                 links_in_grid=True,
                                 create=False,
                                 deletable=False,
                                 editable=False,
                                 details=False,
                                 user_signature=True
                                )

        return dict(form=form, formheader=formheader)


    elif len(request.args) >= 3:
        if request.args[1] == 'new':
            ## redirect to create_po
            redirect(URL('plan','create_plan',args=''))
        elif request.args[1]  == 'edit':
            ## redirect to create_po
            redirect(URL('plan','update_plan',args=request.args[3]))
        elif request.args[1] == 'view':
            ## redirect to create_po
            redirect(URL('plan','view_plan',args=request.args[3]))
        elif request.args[1] == 'delete':
            ## redirect to create_po
            redirect(URL('plan','delete_plan',args=''))
        else:
            form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            left=left,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            user_signature=True
                           )


            return dict(form=form, formheader=formheader)
    else:
        form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            left=left,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            user_signature=True
                           )





        return dict(form=form, formheader=formheader)


@auth.requires_login()
def xcreate_copay():
    ## Add Prcoedure form -
    crud.settings.formstyle='table2cols'
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.create_next = URL('plan','create_copay',args='')
    formA = crud.create(db.copay)

    ## redirect on Cancel
    if session.create_plan_url == None:
        formA.add_button("cancel",URL('default','index', args=''))  ## return to home screen
    else:
        formA.add_button("cancel",session.create_plancode_url)     ## return cancel_returnURL
        session.create_plan_url = None                         ## reset session key

    ## redirect on Items, with PO ID and return URL
    plancodeid = formA.vars.id
    session.plan_returnURL = URL("plan","create_copay")
    session.mode = "lookup"
    return dict(formA=formA)

@auth.requires_login()
def xupdate_copay():
    ## Add Prcoedure form -
    copayid = int( request.args[0])
    crud.settings.formstyle='table2cols'
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('plan','update_copay',args=[copayid])
    formA = crud.update(db.copay, request.args[0],cast=int)

    ## redirect on Cancel
    if session.create_plan_url == None:
        formA.add_button("cancel",URL('default','index', args=''))  ## return to home screen
    else:
        formA.add_button("cancel",session.create_plancode_url)     ## return cancel_returnURL
        session.create_plan_url = None                         ## reset session key

    ## redirect on Items, with PO ID and return URL
    plancodeid = formA.vars.id
    session.plan_returnURL = URL("plan","list_copay")
    session.mode = "lookup"
    return dict(formA=formA)
