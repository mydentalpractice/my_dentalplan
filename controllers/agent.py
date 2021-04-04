# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)


import datetime

#import sys
#sys.path.append('modules')

from applications.my_pms2.modules  import account
#from gluon.contrib import account




#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def list_agent():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
 

    formheader = "Agent List"

    selectable = None

    fields=(db.agent.agent,db.agent.name,db.agent.city,db.agent.st)

    headers={'agent.agent':'Agent',
             'agent.name':'Name',
             'agent.city':'City',
             'agent.st':'St',
             }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)


    links = [lambda row: A('Update',_href=URL("agent","update_agent",args=[row.id])), 
             lambda row: A('Prospects',_href=URL("prospect","list_prospect",vars=dict(ref_code="AGN", ref_id=row.id))),         
             lambda row: A('Providers',_href=URL("prospect","list_provider",vars=dict(ref_code="AGN", ref_id=row.id))),         
             lambda row: A('Delete',_href=URL("agent","delete_agent",args=[row.id]))]

    query = (db.agent.is_active==True)
    
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
    return dict(username=username,returnurl=returnurl,form=form, formheader=formheader)

   

#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def create_agent():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
      
    
    ## Add Prcoedure form -
    formheader="Add Agent"
    crud.settings.formstyle='table2cols'
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.create_next = URL('agent','list_agent',args='')
    db.agent.st.default='None'
    db.agent.commissionYTD.writable = False
    db.agent.commissionMTD.writable = False
    db.agent.TotalCompanies.writable = False
    formA = crud.create(db.agent)


    ## redirect on Cancel
    if session.create_plan_url == None:
        formA.add_button("cancel",URL('default','index', args=''))  ## return to home screen
    else:
        formA.add_button("cancel",session.create_plancode_url)     ## return cancel_returnURL
        session.create_plan_url = None                         ## reset session key

    ## redirect on Items, with PO ID and return URL
    agentid = formA.vars.id
    session.plan_returnURL = URL("agent","create_agent")
    session.mode = "lookup"
    returnurl = URL('agent','list_agent')
    return dict(username=username,returnurl=returnurl,formA=formA,formheader=formheader)

#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def update_agent():


    username = auth.user.first_name + ' ' + auth.user.last_name


    formheader="Agent Maintenance"
    agentid = int(request.args[0])

    ds = account.setmemberpremiumdatesbyagent(db,agentid, datetime.date(2015,1,1), datetime.date(2015,12,31))

    YTD = account.agentYTD(db,agentid)
    MTD = account.agentMTD(db,agentid)
    GRPS = account.assignedGroups(db,agentid)

    db(db.agent.id == agentid).update(commissionYTD = YTD, commissionMTD = MTD, TotalCompanies = GRPS)


    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.detect_record_change = False
    crud.settings.update_next = URL('agent','list_agent',args='')
    db.agent.commissionYTD.writable = False
    db.agent.commissionMTD.writable = False
    db.agent.TotalCompanies.writable = False


    formA = crud.update(db.agent, request.args[0],cast=int)
    formA.add_button("cancel",URL('agent','list_agent',args=''))     ## return cancel_returnURL
    formA.vars.commissionYTD = YTD


    ## Display Co-Pay List for this plan
    fields=(db.company.company,db.company.name, db.hmoplan.hmoplancode)

    headers={'company.company':'Company',
             'company.name' : 'Name',
             'hmoplan.hmoplancode': 'Plan',
             }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)



    links = None

    query = (db.company.agent == agentid) & (db.company.is_active==True)

    left =    [db.hmoplan.on(db.hmoplan.id==db.company.hmoplan)]

    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             left=left,
                             exportclasses=exportlist,
                             links_in_grid=False,
                             searchable=False,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )



    ## redirect on Items, with PO ID and return URL
    returnurl = URL('agent', 'list_agent')
    return dict(username=username,returnurl=returnurl,formA=formA, formB=formB, formheader=formheader, agentid=agentid)

@auth.requires_login()
def view_agent():

    formheader="Agent Data"
    agentid = int(request.args[0])
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('agent','list_agent',args='')

    db.agent.commissionYTD.writable = False
    db.agent.commissionMTD.writable = False
    db.agent.TotalCompanies.writable = False
    formA = crud.update(db.agent, request.args[0],cast=int)
    formA.add_button("cancel",URL('agent','list_agent',args=''))     ## return cancel_returnURL



    ## Display Co-Pay List for this plan
    fields=(db.company.company,db.company.name,db.hmoplan.hmoplancode)

    headers={'company.company':'Company',
             'hmoplan.hmoplancode': 'Plan',
             'company.name': 'Name'
             }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)


    links = [lambda row: A('View',_href=URL("plan","view_plancopay",args=[row.copay.id,planid])),lambda row: A('Update',_href=URL("plan","update_plancopay",args=[row.copay.id,planid])), lambda row: A('Delete',_href=URL("plan","delete_plancopay",args=[row.copay.id,planid]))]
    links = None

    query = (db.company.agent == agentid) & (db.company.is_active==True)

    left =    [db.hmoplan.on(db.hmoplan.id==db.company.hmoplan)]

    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             left=left,
                             exportclasses=exportlist,
                             links_in_grid=False,
                             searchable=False,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )



    ## redirect on Items, with PO ID and return URL
    return dict(formA=formA, formB=formB, formheader=formheader,agentid=agentid)

@auth.requires_login()
def delete_agent():
    if(len(request.args[0]) == 0):
        raise HTTP(400,"Nothing to delete ")
    name = None
    try:
        agentid = int(request.args[0])
        rows = db(db.agent.id == agentid).select()
        if(len(rows) == 0):
            raise HTTP(400,"Nothing to delete ")
        name = rows[0].name
    except Exception, e:
        raise HTTP(400,e.message)

    form = FORM.confirm('Yes?',{'No':URL('my_dentalplan','agent','list_agent')})


    if form.accepted:
        db(db.agent.id == agentid).update(is_active=False)
        redirect(URL('agent','list_agent'))

    return dict(form=form,name=name)