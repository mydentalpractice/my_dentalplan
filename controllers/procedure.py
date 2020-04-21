# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)



#import sys
#sys.path.append('modules')
from applications.my_pms2.modules  import common
#from gluon.contrib import common 

#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def list_procedure():
    
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    formheader = "Procedure List"

    selectable = None

    fields=(db.dentalprocedure.dentalprocedure,db.dentalprocedure.shortdescription,db.dentalprocedure.procedurefee)

    headers={'dentalprocedure.dentalprocedure':'Procedure Code',
             'dentalprocedure.shortdescription':'Description',
             'dentalprocedure.procedurefee':'UCR Fee'
             }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)
    
    
    links = [lambda row: A('Update',_href=URL("procedure","update_procedure",vars=dict(page=common.getgridpage(request.vars)),args=[row.id])), lambda row: A('Delete',_href=URL("procedure","delete_procedure",args=[row.id]))]
    
    query = (db.dentalprocedure.is_active==True)
    
    form = SQLFORM.grid(query=query,
                                 headers=headers,
                                 fields=fields,
                                 links=links,
                                 exportclasses=exportlist,
                                 links_in_grid=True,
                                 create=False,
                                 deletable=False,
                                 editable=False,
                                 details=False,
                                 user_signature=True
                                )
    returnurl = URL('default','index')    
    return dict(username=username,returnurl=returnurl,form=form, formheader=formheader,page=common.getgridpage(request.vars))
    
    
    
#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login() 
def create_procedure():
    username = auth.user.first_name + ' ' + auth.user.last_name
    ## Add Prcoedure form - 
    crud.settings.formstyle='table2cols'
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.create_next = URL('procedure','list_procedure',vars=dict(page=common.getgridpage(request.vars)),args='')
    formA = crud.create(db.dentalprocedure)  

    ## redirect on Cancel    
    if session.create_procedure_url == None:
        formA.add_button("cancel",URL('default','index', args=''))  ## return to home screen
    else:
        formA.add_button("cancel",session.create_procedurecode_url)     ## return cancel_returnURL
        session.create_procedure_url = None                         ## reset session key
    
    ## redirect on Items, with PO ID and return URL
    procedurecodeid = formA.vars.id
    session.procedure_returnURL = URL("procedure","create_procedure")
    session.mode = "lookup"
    page = common.getgridpage(request.vars)
    returnurl=URL('procedure','list_procedure', vars=dict(page=1))
    return dict(username=username,returnurl=returnurl,formA=formA,page=page)   
    
    
#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def update_procedure():
    if(auth.is_logged_in()):
        username = auth.user.first_name + ' ' + auth.user.last_name
    else:
        raise HTTP(400, "Error: User not logged - update_procedure")    
    
    procedurecodeid = int(request.args[0])
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('procedure','list_procedure',vars=dict(page=common.getgridpage(request.vars)),args='')

    
    formA = crud.update(db.dentalprocedure, request.args[0],cast=int)
    formA.add_button("cancel",URL('procedure','list_procedure',vars=dict(page=common.getgridpage(request.vars)),args=''))     ## return cancel_returnURL
    
    ## redirect on Items, with PO ID and returnURL
    page = common.getgridpage(request.vars)
    returnurl=URL('procedure','list_procedure', vars=dict(page=page))
    
    return dict(username=username,returnurl=returnurl,formA=formA, procedurecodeid=procedurecodeid,page=page)

@auth.requires_login() 
def view_procedure():
    
        
    procedurecodeid = int(request.args[0])
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('procedure','list_procedure',args='')

    db.dentalprocedure.dentalprocedure.writable = False
    db.dentalprocedure.shortdescription.writable = False
    db.dentalprocedure.description.writable = False
    db.dentalprocedure.procedurefee.writable = False
    
    formA = crud.update(db.dentalprocedure, request.args[0],cast=int)
    formA.add_button("Cancel",URL('procedure','list_procedure',args=''))     ## return cancel_returnURL
    
    
  
    return dict(formA=formA, procedurecodeid=procedurecodeid)

@auth.requires_login()   
def delete_procedure():
    if(len(request.args[0]) == 0):
        raise HTTP(400,"Nothing to delete ")
    name = None
    try:
        procedureid = int(request.args[0])
        rows = db(db.dentalprocedure.id == procedureid).select()
        if(len(rows) == 0):
            raise HTTP(400,"Nothing to delete ")
        name = rows[0].dentalprocedure
    except Exception, e:
        raise HTTP(400,e.message)
    
    form = FORM.confirm('Yes?',{'No':URL('procedure','list_procedure')})
    
    
    if form.accepted:
        db(db.dentalprocedure.id == procedureid).update(is_active=False)
        redirect(URL('procedure','list_procedure'))
    
    return dict(form=form,name=name)    



@auth.requires_login()
def import_procedure():

    if ((request.vars.csvfile != None) & (request.vars.csvfile != "")):
        # set values
        table = db[request.vars.table]
        file = request.vars.csvfile.file
        # import csv file
        table.import_from_csv_file(file)   
        response.flash = 'Procedure Codes Uploaded'
   



    return dict()