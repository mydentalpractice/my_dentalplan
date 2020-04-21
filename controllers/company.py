# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)

import string
import random

#import sys
#sys.path.append('modules')
from applications.my_pms2.modules  import account
from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import relations

#from gluon.contrib import account
#from gluon.contrib import common  
#from gluon.contrib import relations

    
def cprs():
    
    companyid = 3
    plancode = request.vars.plancode
    
    cprs = db((db.companyhmoplanrate.company == companyid) & (db.hmoplan.hmoplancode == plancode) & (db.companyhmoplanrate.is_active==True) & (db.hmoplan.is_active==True)).\
           select(db.companyhmoplanrate.ALL,db.hmoplan.hmoplancode,db.hmoplan.name,db.groupregion.groupregion, \
                  left=[db.hmoplan.on(db.hmoplan.id==db.companyhmoplanrate.hmoplan),db.groupregion.on(db.groupregion.id==db.companyhmoplanrate.groupregion)],\
                  limitby=limitby)    

    
    return dict(cprs=cprs)
    
def plans():
    
    #if(len(request.vars.groupregion)>1):
        #plans = db(db.hmoplan.groupregion==common.getid(request.vars.groupregion[0])).select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name)
    #else:
    plans = db((db.hmoplan.groupregion==common.getid(request.vars.groupregion))&(db.hmoplan.is_active == True)).select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name)
        
    return dict(plans=plans)


#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def list_groupregion():
    
    username = auth.user.first_name + ' ' + auth.user.last_name   

    formheader = "Region List"

    selectable = None

    fields=(db.groupregion.groupregion,db.groupregion.region)

    headers={'groupregion.groupregion':'Region',
             'groupregion.region':'Name',
             }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)


    links = [lambda row: A('Update',_href=URL("company","update_groupregion",args=[row.id])), lambda row: A('Delete',_href=URL("company","delete_groupregion",args=[row.id]))]

    query = (db.groupregion.is_active==True)

    left=None
    ## called from menu
    if len(request.args) == 0:
        if request.vars.selectable:
            selectable = lambda ids : redirect(URL('company','update_groupregion',args=ids))

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

        returnurl=URL('default','index')
        return dict(username=username,returnurl=returnurl,form=form, formheader=formheader)


    elif len(request.args) >= 3:
        if request.args[1] == 'new':
            ## redirect to create_po
            redirect(URL('company','create_groupregion',args=''))
        elif request.args[1]  == 'edit':
            ## redirect to create_po
            redirect(URL('company','update_groupregion',args=request.args[3]))
        elif request.args[1] == 'view':
            ## redirect to create_po
            redirect(URL('company','view_groupregion',args=request.args[3]))
        elif request.args[1] == 'delete':
            ## redirect to create_po
            redirect(URL('company','delete_groupregion',args=''))
        else:
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


            return dict(username=username,form=form, formheader=formheader)
    else:
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


        return dict(username=username,form=form, formheader=formheader)

#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def create_groupregion():

    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "New Region"

    ## Add form -
    crud.settings.keepvalues = True
    crud.settings.showid = True

    formA = crud.create(db.groupregion, message='New Region Added!', next='update_groupregion/[id]')  ## company Details entry form



    returnurl=URL('company','list_groupregion')
    return dict(username=username,returnurl=returnurl,formA=formA, formheader=formheader)


#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def update_groupregion():


    username = auth.user.first_name + ' ' + auth.user.last_name
    
    formheader = "Region Details"

    ## redirect on Items, with company ID and return URL
    groupregionid = 0

    if(len(request.args) > 0):
        groupregionid = int(request.args[0])

    ## Add form -
    crud.settings.keepvalues = True
    crud.settings.showid = True


    crud.settings.update_next = URL('company','update_groupregion', args=groupregionid)
    formA = crud.update(db.groupregion, request.args[0],cast=int, message='Region Information Updated!')

    returnurl=URL('company','list_groupregion')
    return dict(username=username,returnurl=returnurl,formA=formA,  formheader=formheader, groupregionid=groupregionid)

#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def list_company():

    username = auth.user.first_name + ' ' + auth.user.last_name
    
    formheader = "Group(Company) List"
    
    selectable = None

    fields=(db.company.company,db.company.name)


    headers={'company.company':'Group(Company) Code',
             'company.name':'Group(Company) Name'
             
            }
       
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)

    links = [lambda row: A('Update',_href=URL("company","update_company",vars=dict(page=common.getgridpage(request.vars),pagecprs=0),args=[row.id])), lambda row: A('Delete',_href=URL("company","delete_company",args=[row.id]))]

    query = (db.company.is_active==True)
 
    left =  None #[db.hmoplan.on(db.hmoplan.id==db.company.hmoplan)]

    # list of fields to hide in search list
    db.company.contact.readable=False
    db.company.address1.readable=False
    db.company.address2.readable=False
    db.company.address3.readable=False
    db.company.city.readable=False
    db.company.st.readable=False
    db.company.pin.readable=False
    db.company.telephone.readable=False
    db.company.cell.readable=False
    db.company.fax.readable=False
    db.company.email.readable=False
    db.company.enrolleddate.readable=False
    db.company.terminationdate.readable=False
    db.company.renewaldate.readable=False
    db.company.capcycle.readable=False
    db.company.premcycle.readable=False
    db.company.adminfee.readable=False
    db.company.minsubscribers.readable=False
    db.company.maxsubscribers.readable=False
    db.company.minsubsage.readable=False
    db.company.maxsubsage.readable=False
    db.company.mindependantage.readable=False
    db.company.maxdependantage.readable=False
    db.company.maxdependantage.readable=False
    db.company.notes.readable=False
    db.company.commission.readable=False
    db.company.hmoplan.readable=False
    db.company.agent.readable=False
    db.company.groupkey.readable=False

    
    
    
    
 
    form = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        left=left,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=False)
                       
    returnurl=URL('default','index')
    return dict(username=username,returnurl=returnurl,form=form, formheader=formheader,page=common.getgridpage(request.vars),pagecprs=0)


    ### called from menu
    #if len(request.args) == 0:  
        #session.create_company_url = URL('company','create_company',args='')
        #if request.vars.selectable:
            #selectable = lambda ids : redirect(URL('company','update_company',args=ids))
        
        #form = SQLFORM.grid(query=query,
                            #headers=headers,
                            #fields=fields,
                            #links=links,
                            #left=left,
                            #exportclasses=exportlist,
                            #links_in_grid=True,
                            #searchable=True,
                            #create=False,
                            #deletable=False,
                            #editable=False,
                            #details=False,
                            #user_signature=False)
                           
        
        #return dict(username=username,form=form, formheader=formheader,page=common.getgridpage(request.vars),pagecprs=0)
    
    
    #elif len(request.args) >= 3:
        #if request.args[1] == 'new':
            ### redirect to create_po
            #redirect(URL('company','create_company',args=''))
        #elif request.args[1]  == 'edit':
            ### redirect to create_po
            #redirect(URL('company','update_company',args=request.args[3]))
        #elif request.args[1] == 'view':
            ### redirect to create_po
            #redirect(URL('company','view_company',args=request.args[3]))
        #elif request.args[1] == 'delete':
            ### redirect to create_po
            #redirect(URL('jaimini','company','delete_company',args=''))
        #else:
            #form = SQLFORM.grid(query=query,
                                #headers=headers,
                                #fields=fields,
                                #links=links,
                                #left=left,
                                #exportclasses=exportlist,
                                #links_in_grid=True,
                                #create=False,
                                #deletable=False,
                                #editable=False,
                                #details=False,
                                #user_signature=True
                               #)
                   
            
            #return dict(username=username,form=form, formheader=formheader,page=common.getgridpage(request.vars),pagecprs=0)
    #else:
        
        #form = SQLFORM.grid(query=query,
                            #headers=headers,
                            #fields=fields,
                            #links=links,
                            #left=left,
                            #exportclasses=exportlist,
                            #links_in_grid=True,
                            #create=False,
                            #deletable=False,
                            #editable=False,
                            #details=False,
                            #user_signature=True
                           #)
          
        #return dict(username=username,form=form, formheader=formheader,page=common.getgridpage(request.vars),pagecprs=0)

#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def create_company():

    username = auth.user.first_name + ' ' + auth.user.last_name
    
    formheader = "New Company"
    
    ## Add form - 
    crud.settings.keepvalues = True
    crud.settings.showid = True
    db.company.st.default='None'
    db.company.hmoplan.default = 1
   
    
    formA = crud.create(db.company, next='update_company/[id]', message='New Company Added!')  ## company Details entry form
    formA.add_button("cancel",URL('company','list_company'))  ## return to home screen
    formA.element('textarea[name=notes]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=notes]')['_rows'] = 5

    companyid = formA.vars.id    
    db.membercount.insert(company=companyid,dummy1= 'X')
        
                
    returnurl=URL('company','list_company',vars=dict(page=1))
    return dict(username=username,returnurl=returnurl,formA=formA, formheader=formheader)

@auth.requires_login()
def updateAgentCommission(companyid, planid, agentid, commmission, effectivedate):

    rows = db(db.agentcommission.company == companyid & db.agentcommission.hmoplan == planid & db.agentcommission.agent == agentid).select()
    if (len(rows) > 0):
        xid = int(rows[0])
        db(db.agentcommission.id == xid).update(commission=commission, effectivedate=effectivedate)
    else:
        db.agentcommission.insert(commission = commission, effectivedate=effectivedate, agent = agentid, company = companyid, hmoplan = planid)

    return dict()

#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def update_company():

    username = auth.user.first_name + ' ' + auth.user.last_name
    
    formheader = "Group(Company) Details"
    
    ## redirect on Items, with company ID and return URL
    companyid = 0
    planid = 0
    agentid = 0
    agentname = None
    planname = None
    siteky = None
    page = common.getgridpage(request.vars)
    pagecprs = int(common.getpage(request.vars.pagecprs))
    
    if(len(request.args) > 0):
        companyid = int(request.args[0])
        rows = db(db.company.id == companyid).select()
        planid = rows[0].hmoplan
        agentid = rows[0].agent
        sitekey = rows[0].groupkey
        
        if((sitekey == None)|(sitekey == '')):
            password = ''
            specials=r'!#$*?'         
            #specials = r'$-_.+!*()'   - these are safe chars
            for i in range(0,2):
                password += random.choice(string.lowercase)
                password += random.choice(string.uppercase)
                password += random.choice(string.digits)
                #password += random.choice(specials)            
    
            text = password                
            db(db.company.id == companyid).update(groupkey = text)
        
        plans = db(db.hmoplan.id == planid).select()
        if(len(plans)>0):
            planname = plans[0].name
        
        agents = db(db.agent.id == agentid).select()
        if(len(agents)>0):
            agentname = agents[0].name
    
    db.membercount.update_or_insert(company=companyid,dummy1= 'X')
    ## Add form - 
    crud.settings.keepvalues = True
    crud.settings.showid = True

    db.company.st.default='None'
    db.company.groupkey.writable = False
    
    crud.settings.update_next = URL('company','update_company',  vars=dict(page=common.getgridpage(request.vars)),args=companyid)
    formA = crud.update(db.company, request.args[0],cast=int,message='Company Information Updated!')    
    formA.element('textarea[name=notes]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=notes]')['_rows'] = 5
    formA.add_button("cancel",URL('company','list_company', vars=dict(page=page)))     ## return cancel_returnURL
                       ## reset session key
   
    ## Display Co-Pay List for this plan
    fields=(db.companyhmoplanrate.hmoplan,db.companyhmoplanrate.groupregion,db.companyhmoplanrate.relation,db.companyhmoplanrate.premium,db.companyhmoplanrate.capitation,db.companyhmoplanrate.companypays)

    headers={'companyhmoplanrate.hmoplan':'Plan (Code)',          
             'companyhmoplanrate.groupregion':'Region',             
             'companyhmoplanrate.relation':'Relation',             
             'companyhmoplanrate.premium': 'Premium',
             'companyhmoplanrate.companypays': 'Company Pays',
             'companyhmoplanrate.capitation': 'Capitation'
             }
    db.companyhmoplanrate.covered.writable = False
    db.companyhmoplanrate.covered.readable = False
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)
    
    
    links = [lambda row: A('Update',_href=URL("company","update_companyplanrate",vars=dict(page=common.getgridpage(request.vars)), args=[row.id,companyid,planid])), lambda row: A('Delete',_href=URL("company","delete_companyplanrate",args=[row.id,companyid,planid]))]
   
    query = (db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.is_active==True)
    
    left = None
    
    orderby = (db.companyhmoplanrate.groupregion | db.companyhmoplanrate.hmoplan)
    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             left=left,
                             orderby=orderby,
                             searchable = False,
                             exportclasses=exportlist,
                             links_in_grid=True,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )

    
    items_per_page = 5
    limitby = (pagecprs*items_per_page,(pagecprs+1)*items_per_page+1)     
    cprs = db((db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.is_active==True)).\
           select(db.companyhmoplanrate.ALL,db.hmoplan.hmoplancode,db.hmoplan.name,db.groupregion.groupregion,\
           left=[db.hmoplan.on(db.hmoplan.id==db.companyhmoplanrate.hmoplan),db.groupregion.on(db.groupregion.id==db.companyhmoplanrate.groupregion)],\
           limitby=limitby)

    #cprs = db((db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.is_active==True)).\
           #select(db.companyhmoplanrate.ALL,db.hmoplan.hmoplancode,db.hmoplan.name,db.groupregion.groupregion,\
           #left=[db.hmoplan.on(db.hmoplan.id==db.companyhmoplanrate.hmoplan),db.groupregion.on(db.groupregion.id==db.companyhmoplanrate.groupregion)],\
           #orderby=db.companyhmoplanrate.hmoplan | db.companyhmoplanrate.groupregion,limitby=limitby)

    
    returnurl=URL('company','list_company',vars=dict(page=page))
    return dict(username=username,returnurl=returnurl,formA=formA, formB=formB, formheader=formheader, companyid=companyid, planid=planid, agentname=agentname, planname = planname,page=page,pagecprs=pagecprs,cprs=cprs,items_per_page=items_per_page,limitby=limitby)


@auth.requires_login()
def view_company():

    formheader = "Group(Company) Details"

    ## redirect on Items, with company ID and return URL
    companyid = 0
    planid = 0
    agentid = 0
    agentname = None
    planname = None

    if(len(request.args) > 0):
        companyid = int(request.args[0])
        rows = db(db.company.id == companyid).select()
        planid = rows[0].hmoplan
        agentid = rows[0].agent

        plans = db(db.hmoplan.id == planid).select()
        planname = plans[0].name

        agents = db(db.agent.id == agentid).select()
        agentname = agents[0].name

    ## Add form -
    crud.settings.keepvalues = True
    crud.settings.showid = True

    db.company.st.default='None'

    crud.settings.update_next = URL('company','list_company',args='')
    formA = crud.update(db.company, request.args[0],cast=int)



    ## redirect on Cancel
    if session.create_company_url == None:
        formA.add_button("cancel",URL('default','index', args=''))  ## return to home screen
    else:
        formA.add_button("cancel",session.create_company_url)     ## return cancel_returnURL
        session.create_company_url = None                         ## reset session key

    ## Display Co-Pay List for this plan
    fields=(db.companyhmoplanrate.hmoplan,db.companyhmoplanrate.covered,db.companyhmoplanrate.relation,db.companyhmoplanrate.premium,db.companyhmoplanrate.capitation,db.companyhmoplanrate.companypays)

    headers={'companyhmoplanrate.hmoplan':'Plan',
             'companyhmoplanrate.relation':'Relation',
             'companyhmoplanrate.premium': 'Premium',
             'companyhmoplanrate.companypays': 'Company Pays',
             'companyhmoplanrate.capitation': 'Capitation'
             }
    db.companyhmoplanrate.covered.writable = False
    db.companyhmoplanrate.covered.readable = False

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)


    links = [lambda row: A('View',_href=URL("company","view_companyplanrate",args=[row.id,companyid,planid])),lambda row: A('Update',_href=URL("company","update_companyplanrate",args=[row.id,companyid,planid])), lambda row: A('Delete',_href=URL("company","delete_companyplanrate",args=[row.id,companyid,planid]))]

    query = (db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.hmoplan == planid) & (db.companyhmoplanrate.is_active==True)

    left = None

    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             left=left,
                             searchable = False,
                             exportclasses=exportlist,
                             links_in_grid=True,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )


    return dict(formA=formA, formB=formB, formheader=formheader, companyid=companyid, planid=planid, agentname=agentname, planname = planname)



@auth.requires_login()
def delete_company():
    if(len(request.args[0]) == 0):
        raise HTTP(400,"Nothing to delete ")
    name = None
    try:
        companyid = int(request.args[0])
        rows = db(db.company.id == companyid).select()
        if(len(rows) == 0):
            raise HTTP(400,"Nothing to delete ")
        name = rows[0].name
    except Exception, e:
        raise HTTP(400,e.message)

    form = FORM.confirm('Yes?',{'No':URL('company','list_company')})


    if form.accepted:
        db(db.company.id == companyid).update(is_active=False)
        redirect(URL('company','list_company'))

    return dict(form=form,name=name)

@auth.requires_login()
def delete_groupregion():
    if(len(request.args[0]) == 0):
        raise HTTP(400,"Nothing to delete ")
    name = None
    try:
        regionid = int(request.args[0])
        rows = db(db.groupregion.id == regionid).select()
        if(len(rows) == 0):
            raise HTTP(400,"Nothing to delete ")
        name = rows[0].groupregion
    except Exception, e:
        raise HTTP(400,e.message)

    form = FORM.confirm('Yes?',{'No':URL('company','list_groupregion')})


    if form.accepted:
        db(db.groupregion.id == regionid).update(is_active=False)
        redirect(URL('company','list_groupregion'))

    return dict(form=form,name=name)



def create_onvalidation_companyhmoplanrate(form):
    
    
    companyid = int(common.getid(form.vars.company))
    hmoplanid = int(common.getid(form.vars.hmoplan))
    regionid = int(common.getid(form.vars.groupregion))
    covered = int(common.getid(form.vars.covered))
    
    rows = db((db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.groupregion == regionid) & (db.companyhmoplanrate.hmoplan == hmoplanid) & \
              (db.companyhmoplanrate.covered == covered) & (db.companyhmoplanrate.is_active==True)).select()
    if(len(rows) > 0):
        mssg = "This dependant level has already been covered!"
        redirect(URL('company', 'create_companyplanrate',args=[companyid],vars=dict(covered=covered,coverederror=mssg)))
    else:
        return True
    return dict()

#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def create_companyplanrate():

    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "New Plan Rates"

    coverederror = common.getstring(request.vars.coverederror)
    
    planid     = 1
    region     = 1
    covered    = int(common.getid(request.vars.covered))
    if(covered == 0):
        covered = 1
    
        
    dependantmode = False
    companyid = 0
    if(len(request.args) > 0):
        if(request.args[0] != 'static'):
            companyid   = request.args[0]
            ds = db((db.company.is_active==True) & (db.company.id == companyid)).select()
            if(len(ds)>0):
                dependantmode = common.getbool(ds[0]['dependantmode'])
        
    else:
        companyid = 0

    if(dependantmode == True):
        db.companyhmoplanrate.relation.requires = IS_IN_SET(PLANRDEPENDANTS)
        
    db.companyhmoplanrate.covered.default = covered
    db.companyhmoplanrate.company.default = companyid
    db.companyhmoplanrate.hmoplan.default = planid
    db.companyhmoplanrate.relation.default = 'Self'
    db.companyhmoplanrate.groupregion.default = region

    #db.companyhmoplanrate.covered.writable = False
    #db.companyhmoplanrate.covered.readable = False
        
    regions = db(db.groupregion.is_active == True).select(db.groupregion.id, db.groupregion.groupregion)
    plans   = db((db.hmoplan.groupregion == region)&(db.hmoplan.is_active == True)).select(db.hmoplan.id, db.hmoplan.hmoplancode,db.hmoplan.name)
    page = common.getgridpage(request.vars)
    pagecprs = common.getpage(request.vars.pagecprs)
    crud.settings.formstyle='table2cols'
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.create_onvalidation = create_onvalidation_companyhmoplanrate
    crud.settings.create_next = URL('company','create_companyplanrate',vars=dict(page=page,pagecprs=pagecprs),args=[companyid])

    formA = crud.create(db.companyhmoplanrate, message='New Company Plan Rate Added!')      
 
    formA.add_button("cancel", URL('company','update_company',vars=dict(page=page,pagecprs=pagecprs),args=[companyid]))
    
    fields=(db.companyhmoplanrate.hmoplan,db.companyhmoplanrate.groupregion,db.companyhmoplanrate.relation,db.companyhmoplanrate.premium,db.companyhmoplanrate.capitation,db.companyhmoplanrate.companypays)

    headers={'companyhmoplanrate.hmoplan':'Plan',             
             'companyhmoplanrate.groupregion':'Region',             
             'companyhmoplanrate.relation':'Relation',             
             'companyhmoplanrate.premium': 'Premium',
             'companyhmoplanrate.companypays': 'Company Pays',
             'companyhmoplanrate.capitation': 'Capitation'
             }
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)
    links = None # [lambda row: A('Update',_href=URL("company","update_companyplanrate",vars=dict(page=common.getgridpage(request.vars)), args=[row.id,companyid,planid])), lambda row: A('Delete',_href=URL("company","delete_companyplanrate",args=[row.id,companyid,planid]))]
    query = (db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.is_active==True)
    left = None
    
    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             left=left,
                             searchable = False,
                             exportclasses=exportlist,
                             links_in_grid=True,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )
    returnurl=URL('company','list_company',vars=dict(page=1))
    return dict(username=username,returnurl=returnurl,formA=formA, formB=formB, formheader=formheader, regions=regions, plans=plans, planid=planid, companyid=companyid,page=common.getgridpage(request.vars),pagecprs=pagecprs,coverederror = coverederror)

#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def update_companyplanrate():
    username = auth.user.first_name + ' ' + auth.user.last_name
     
    formheader = "Plan Rate"
    if(len(request.args)>0):
        companyhmoplanid = common.getid(request.args[0])
    else:
        companyhmoplanid = 0
    
    companyhmoplan = db(db.companyhmoplanrate.id == companyhmoplanid).select()
    if(len(companyhmoplan) > 0):
        companyid = common.getid(companyhmoplan[0].company)
        planid    = common.getid(companyhmoplan[0].hmoplan)
        regionid  = common.getid(companyhmoplan[0].groupregion)
    else:
        companyid = 1
        planid = 1
        regionid = 1
    
    dependantmode = False
    ds = db((db.company.is_active==True) & (db.company.id == companyid)).select()
    if(len(ds)>0):
        dependantmode = common.getbool(ds[0]['dependantmode'])
    
    if(dependantmode == True):
          db.companyhmoplanrate.relation.requires = IS_IN_SET(PLANRDEPENDANTS) 
              
    db.companyhmoplanrate.company.default = companyid
    db.companyhmoplanrate.hmoplan.default = planid
    db.companyhmoplanrate.groupregion.default = regionid
        
    regions = db(db.groupregion.is_active == True).select(db.groupregion.id, db.groupregion.groupregion)
    plans = db(db.hmoplan.groupregion==regionid).select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name)
    pagecprs  = int(common.getpage(request.vars.pagecprs))
    page = common.getgridpage(request.vars)
    crud.settings.formstyle='table2cols'
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('company','update_companyplanrate',vars=dict(page=page,pagecprs=pagecprs),args=[companyhmoplanid,companyid,planid])
    formA = crud.update(db.companyhmoplanrate, request.args[0],cast=int, message='Company Plan Rate Updated!') 

    ## redirect on Cancel    
    if session.create_plan_url == None:
        formA.add_button("cancel",URL('default','index', args=''))  ## return to home screen
    else:
        formA.add_button("cancel",session.create_plancode_url)     ## return cancel_returnURL
        session.create_plan_url = None                         ## reset session key
    
    returnurl=URL('company','list_company',vars=dict(page=page))   
    return dict(username=username, returnurl=returnurl,formA=formA, regions=regions,plans=plans,regionid=regionid, formheader=formheader,companyid=companyid,planid=planid,page=page,pagecprs=pagecprs)

@auth.requires_login()
def view_companyplanrate():
    ## Add Prcoedure form -

    formheader = "Plan Rate"
    companyid = 0
    planrateid = 0
    planid = 0
    if(len(request.args)>0):
        planrateid = request.args[0]
        companyid = request.args[1]
        planid = request.args[2]

    db.companyhmoplanrate.company.default = companyid
    db.companyhmoplanrate.hmoplan.default = planid

    crud.settings.formstyle='table2cols'
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('company','view_company',args=[companyid])
    formA = crud.update(db.companyhmoplanrate, request.args[0],cast=int)

    ## redirect on Cancel
    if session.create_plan_url == None:
        formA.add_button("cancel",URL('default','index', args=''))  ## return to home screen
    else:
        formA.add_button("cancel",session.create_plancode_url)     ## return cancel_returnURL
        session.create_plan_url = None                         ## reset session key



    return dict(formA=formA,formheader=formheader,companyid=companyid,planid=planid)


@auth.requires_login()
def delete_companyplanrate():
    row = db.companyhmoplanrate[request.args[0]]
    if request.vars.confirm:
        db(db.companyhmoplanrate.id == row.id).delete()
        form=None
    else:
        form = BUTTON('really delete',_onclick='document.location="%s"'%URL(vars=dict(confirm=True),args=[row.id]))

    return dict(form=form)


@auth.requires_login()
def delete_companyplanrate():
    if(len(request.args[0]) == 0):
        raise HTTP(400,"Nothing to delete ")
    name = None
    try:
        rateid = int(request.args[0])
        companyid = int(request.args[1])
        rows = db(db.companyhmoplanrate.id == rateid).select()
        if(len(rows) == 0):
            raise HTTP(400,"Nothing to delete ")
        name = None
    except Exception, e:
        raise HTTP(400,e.message)

    form = FORM.confirm('Yes?',{'No':URL('company','update_company', args=[companyid])})


    if form.accepted:
        db(db.companyhmoplanrate.id == rateid).update(is_active=False)
        redirect(URL('company','update_company', args=[companyid]))

    return dict(form=form,name=name)