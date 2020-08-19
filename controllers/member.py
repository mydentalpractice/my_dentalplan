# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)

import datetime
import time
import calendar
from datetime import timedelta
from decimal  import Decimal



#import sys
#sys.path.append('modules')
from applications.my_pms2.modules  import account
from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import mail

#from gluon.contrib import account
#from gluon.contrib import mail
#from gluon.contrib import common 

import os
import random
import string
from string import Template


def plans():
    
    regionid = 1
    companyid = 1
    
    #if(len(request.vars.groupregion) > 1):
        #regionid = common.getid(request.vars.groupregion[0])
    #else:
    regionid = common.getid(request.vars.groupregion)
        
    #if(len(request.vars.company) > 1):
        #companyid = common.getid(request.vars.company[0])
    #else:
    companyid = common.getid(request.vars.company)
        
       
    
    plans = db((db.companyhmoplanrate.is_active == True) & (db.companyhmoplanrate.groupregion==regionid) & (db.companyhmoplanrate.company==companyid) & \
               (db.companyhmoplanrate.relation == 'Self') & (db.hmoplan.is_active==True)).\
        select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
               left=db.hmoplan.on((db.companyhmoplanrate.hmoplan == db.hmoplan.id)&(db.hmoplan.is_active==True)),distinct=True)
    
   
    return dict(plans=plans)
    
def enrollment_error():

    returnURL = URL('member','member_enrollment')
    errMssg = "Enrollment Error : Please contact My Dental Plan"
    if(len(request.args)>0):
        returnRUL = URL('member',request.args[0])
        errMssg   = request.args[1]

    return dict(returnURL=returnURL, errMssg=errMssg)


def import_member_csv_0():
    return dict()

@auth.requires_login()
def import_member_csv_1():

    form = None

    if ((request.vars.csvfile != None) & (request.vars.csvfile != "")):
        # set values
        table = db[request.vars.table]
        file = request.vars.csvfile.file
        # import csv file
        table.import_from_csv_file(file)


        rows = db((db.company.company == request.args[1]) & (db.company.is_active == True)).select()

        companyid = 0
        if(len(rows) > 0):
            companyid = int(rows[0].id)
            if(companyid > 0):

                #formheader = "Group Enrollment Status"

                #selectable = None

                #fields=(db.webmember.fname,db.webmember.lname,db.webmember.webmember,db.webmember.email,db.webmember.status,db.webmember.webdob)

                #headers={'webmember.webmember':'Member ID',
                         #'webmember.fname':'First Name',
                         #'webmember.lname':'Last Name',
                         #'webmember.webdob':'Date of Birth',
                         #'webmember.email':'Email',
                         #'webmember.status':'Status',
                        #}


                #exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)

                #rows= db((db.webmember.is_active==True) & (db.webmember.company == companyid)).select()

                #query = ((db.webmember.is_active==True) & (db.webmember.company == companyid) & (db.webmember.imported==False))

                #left = None

                #a = 'my_dentalplan'
                #c = 'member'


                #form = SQLFORM.grid(query=query,
                                    #headers=headers,
                                    #fields=fields,
                                    #links=None,
                                    #left=left,
                                    #selectable=None,
                                    #exportclasses=exportlist,
                                    #links_in_grid=False,
                                    #searchable=False,
                                    #create=False,
                                    #deletable=False,
                                    #editable=False,
                                    #details=False,
                                    #user_signature=False)


                providerid = 1
                provs = db(db.provider.provider == ' ').select();
                if(len(provs)>0):
                    providerid = provs[0].id


                groupregionid = 1
                rgns = db(db.groupregion.groupregion == ' ').select();
                if(rgns > 0):
                    groupregionid = rgns[0].id

                db((db.company.id == companyid) & (db.company.is_active == True)).update(groupkey=(request.vars.webkey).strip())
                db((db.webmember.id > 0) & (db.webmember.imported==False) & (db.webmember.is_active == True)).update(company=companyid,webkey=(request.vars.webkey).strip(),imported=True,provider=providerid,groupregion=groupregionid)



        response.flash = 'Data uploaded'

    return dict()

@auth.requires_login()
def import_member_csv():
    
    if request.vars.csvfile != None:
        # set values
        table = db[request.vars.table]
        file = request.vars.csvfile.file
    
        # import csv file
        table.import_from_csv_file(file)
    
        # transfer importdata to webmember
        rows = db(db.importdata.id > 0).select()
        for row in rows:
            rowid = db.webmember.insert(webmember = row.memberid,
                                        groupref = row.employeeid,
                                        fname = row.firstname,
                                        lname = row.lastname,
                                        address1 = row.address1,
                                        address2 = row.address2,
                                        address3 = row.address3,
                                        city = row.city,
                                        st = row.st,
                                        pin = row.pin,
                                        webdob = row.webdob,
                                        gender = row.gender,
                                        email = row.email,
                                        cell = 'xxxxxxxxxx',
                                        webkey = row.webkey,
                                        startdate = row.startdate,
                                        webenrolldate = row.enrolldate,
                                        webenrollcompletedate = row.enrolldate,
                                        status = row.status,
                                        imported = row.imported,
                                        company = row.company,
                                        provider = row.provider,
                                        groupregion = row.groupregion,
                                        hmoplan = row.hmoplan,
                                        paid = False,
                                        upgraded = False,
                                        is_active = row.is_active,
                                        created_on = row.created_on,
                                        created_by = row.created_by,
                                        modified_on = row.modified_on,
                                        modified_by = row.modified_by
                                        
                                        )
            companyid = row.company
            cmps = db(db.company.id == companyid).select()
            companycode = cmps[0].company
            db(db.webmember.id == rowid).update(webmember = cmps[0].company + str(rowid))        
        
        #db.importdata.truncate()
        db.commit()

        response.flash = 'Data uploaded'

    return dict()   

    

 
def download():
    if(len(request.args)>0):
        filename = request.args[0]
    return response.download(request, db)


#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def export_members():

    #IB 05292016
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    page=common.getgridpage(request.vars)

    formheader = "Export Member List"

    selectable = None

    fields=(
               db.patientmember.id,
               db.patientmember.patientmember,
               db.patientmember.groupref,
               db.patientmember.fname,
               db.patientmember.mname,
               db.patientmember.lname,
               db.patientmember.address1,
               db.patientmember.address2,
               db.patientmember.address3,
               db.patientmember.city,
               db.patientmember.st,
               db.patientmember.pin,
               db.patientmember.cell,
               db.patientmember.email,
               db.patientmember.gender,
               db.patientmember.dob,
               db.patientmember.enrollmentdate,
               db.patientmember.terminationdate,
               db.patientmember.created_on,
               db.patientmember.modified_on,
               db.provider.provider,
               db.company.company,
               db.groupregion.groupregion,
               db.hmoplan.hmoplancode
    )    
   

    
   
    
    
   
    db.patientmember.telephone.readable = False
    db.patientmember.pan.readable = False
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
    db.patientmember.paid.readable = False
    db.patientmember.upgraded.readable = False
    db.patientmember.renewed.readable = False
    db.patientmember.webkey.readable = False
    db.patientmember.company.readable = False
    db.patientmember.hmoplan.readable = False
    db.patientmember.startdate.readable = False
    db.patientmember.webmember.readable = False    
    
    db.company.name.readable = False
    db.company.name.writable = False
    db.company.contact.readable = False
    db.company.address1.readable = False
    db.company.address2.readable = False
    db.company.address3.readable = False
    db.company.address1.writable = False
    db.company.address2.writable = False
    db.company.address3.writable = False
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
    
    

    headers={
            'patientmember.id':'ID',
            'patientmember.patientmember':'Member ID',
            'patientmember.groupref':'Customer ID',
            'patientmember.fname':'First Name',
            'patientmember.mname':'Middle Name',
            'patientmember.lname':'Last Name',            
            'patientmember.address1':'Address 1',            
            'patientmember.address2':'Address 2',            
            'patientmember.address3':'Address 3',            
            'patientmember.city':'City',            
            'patientmember.st':'State',            
            'patientmember.pin':'Pin',            
            'patientmember.cell':'Cell',            
            'patientmember.gender':'Gender',
            
            'patientmember.dob':'DOB',            
            'patientmember.email':'Email',
            
            'patientmember.enrollmentdate':'Enrolled On',
            'patientmember.terminationdate':'Terminated On',
            'patientmember.created_on':'created_on',
            'patientmember.modified_on':'modified_on',
            'provider.provider':'Provider',
            'company.company':'Company',
            'groupregion.groupregion':'Region',
            'hmoplan.hmoplancode':'Plan',
            
            }




    exportlist = dict( csv=False,csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)

    #IB 05292016
    links = None

    query = ((db.patientmember.is_active==True) & (db.patientmember.hmopatientmember==True))

    left =    [db.company.on(db.company.id==db.patientmember.company),\
               db.provider.on(db.provider.id == db.patientmember.provider),\
               db.groupregion.on(db.groupregion.id == db.patientmember.groupregion),\
               db.hmoplan.on(db.hmoplan.id == db.patientmember.hmoplan)]

    orderby = ~(db.patientmember.id)


    form = SQLFORM.grid(query=query,
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
                        user_signature=False
                       )
    returnurl = URL('member','list_member',vars=dict(page=1))
    return dict(username=username, returnurl=returnurl, form=form, formheader=formheader,page=page) #IB 05292016

#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def list_member():

    #IB 05292016
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    page=common.getgridpage(request.vars)

    formheader = "Member List"

    selectable = None

    fields=(db.patientmember.fname,db.patientmember.mname,db.patientmember.lname,db.patientmember.patientmember,db.company.company)
   
    db.patientmember.mname.readable = False
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
    db.patientmember.paid.readable = False
    db.patientmember.upgraded.readable = False
    db.patientmember.renewed.readable = False
    db.patientmember.webkey.readable = False
    db.patientmember.company.readable = False
    db.patientmember.hmoplan.readable = False
    db.patientmember.startdate.readable = False
    db.patientmember.webmember.readable = False    
    
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




    exportlist = dict( csv=False,csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)

    #IB 05292016
    links = [lambda row: A('Member Card',_href=URL("member","member_card_links",vars=dict(page=common.getgridpage(request.vars),memberid=row.patientmember.id),args=[row.patientmember.id])),lambda row: A('Welcome Kit',_href=URL("default","emailwelcomekit_0",vars=dict(page=common.getgridpage(request.vars)),args=[row.patientmember.id])),lambda row: A('Update',_href=URL("member","update_member",vars=dict(page=common.getgridpage(request.vars)), args=[row.patientmember.id])), lambda row: A('Delete',_href=URL("member","delete_member",args=[row.patientmember.id]))]

    query = ((db.patientmember.is_active==True) & (db.patientmember.hmopatientmember==True))

    left =    [db.company.on(db.company.id==db.patientmember.company)]

    orderby = ~(db.patientmember.id)


    form = SQLFORM.grid(query=query,
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
                        user_signature=False
                       )
    returnurl = URL('member','list_member',vars=dict(page=1))
    return dict(username=username, returnurl=returnurl, form=form, formheader=formheader,page=page) #IB 05292016

@auth.requires_login()
def create_member():
    ## Add PO form -
    formheader = "Add New Member"
    crud.settings.keepvalues = True
    crud.settings.showid = True

    db.patientmember.st.default='--Select State--'
    db.patientmember.city.default='--Select City--'

    formA = crud.create(db.patientmember, next='update_member/[id]',message="New Member Added!")  ## Broker Details entry form

    ds = db(db.provider.is_active == True).select()

    return dict(formA=formA,  formheader=formheader,ds=ds,providerid = 0)

#ib 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def update_member():


    username = auth.user.first_name + ' ' + auth.user.last_name


    formheader = "Member Maintenance"
    subscribers = 1
    maxsubscribers = 1
    webkey = ''
    ds = ''
    pin = ''
    pin1 = ''
    pin2 = ''
    pin3 = ''

    page = common.getgridpage(request.vars)
    
    memberid = int(request.args[0])
    rows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    
    companyid = int(rows[0].company)
    providerid = int(rows[0].provider)
   
    
    rows1 = db(db.webmember.webmember == rows[0].patientmember).select()
    if(len(rows1) > 0):
        pin = common.getstring(rows1[0].pin).strip()
        pin1 = common.getstring(rows1[0].pin1).strip()
        pin2 = common.getstring(rows1[0].pin2).strip()
        pin3 = common.getstring(rows1[0].pin3).strip()


    provrows = db(db.provider.id == providerid).select()
    providername = provrows[0].providername

    if(rows[0].hmoplan == None):
        planid = None
    else:
        planid = int(rows[0].hmoplan)

    x = db(db.company.id == companyid).select()
    if(len(x)>0):
        maxsubscribers = int(x[0].maxsubscribers)



    subscribers = subscribers + db((db.patientmemberdependants.patientmember == memberid) & (db.patientmemberdependants.is_active == True)).count()

    if(len(rows) > 0):
        webkey = rows[0].webkey
        imageFile = rows[0].image
        #db.patientmember.company.writable = False
        #db.patientmember.provider.writable = False
        #db.patientmember.webkey.writable = False
        #db.patientmember.status.writable = False
        #db.patientmember.memberorder.writable = False


    db.patientmember.hmoplan.writable = False
    db.patientmember.groupregion.writable = False

    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('member','update_member',args=[memberid],vars=dict(page=common.getgridpage(request.vars)))
  
    db.patientmember.dob.writable=True
    db.patientmember.upgraded.readable = True

    formA = crud.update(db.patientmember, memberid,cast=int,message="Member Information Updated!")
 
    if(formA.accepted):
	i = 0;
    else:
	i = 0;


    ## Display Dependant List for this member
    fields=(db.patientmemberdependants.fname,db.patientmemberdependants.lname,db.patientmemberdependants.gender,db.patientmemberdependants.depdob,db.patientmemberdependants.relation)

    headers={'patientmemberdependants.fname':'First Name',
             'patientmemberdependants.lname': 'Last Name',
             'patientmemberdependants.depdob': 'DOB',
             'patientmemberdependants.gender': 'Gender',
             'patientmemberdependants.relation':'Relation'
             }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)

    left = None
    links = [lambda row: A('Update',_href=URL("member","update_dependant", vars=dict(page=common.getgridpage(request.vars)),args=[row.id,memberid])), lambda row: A('Delete',_href=URL("member","delete_dependant",args=[row.id,memberid]))]

    query = (db.patientmemberdependants.patientmember == memberid) & (db.patientmemberdependants.is_active==True)


    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             left=left,
                             exportclasses=exportlist,
                             links_in_grid=True,
                             searchable=False,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )


    #ds = db((db.provider.id == 1) | ((db.provider.id != 1) & (db.provider.is_active == True))).select()
    if(((pin1 == '')|(pin1==None)) & ((pin2 == '')|(pin2==None)) & ((pin3 == '')|(pin3==None))):
        ds = db((db.provider.id == 1 ) | ((db.provider.id != 1) & (db.provider.is_active == True))).select()
    else:
        ds = db((db.provider.id == 1) | ((pin1 != '') & (db.provider.pin== pin1) & (db.provider.is_active == True)) | \
        ((pin2 != '')&(db.provider.pin == pin2) & (db.provider.is_active == True)) | \
        ((pin3 != '')&(db.provider.pin == pin3) & (db.provider.is_active == True))).select()
        if(len(ds) <= 1):
            ds = db((db.provider.id == 1) | ((pin != '') & (db.provider.pin == pin))).select()
        if(len(ds) <= 1):
            ds = db((db.provider.id == 1 ) | ((db.provider.id != 1) & (db.provider.is_active == True))).select()


    sql = "select provider.id, IFNULL(AAA.providercount,0) AS providercount from provider left join "
    sql = sql + "(select provider, count(provider) AS providercount from patientmember group by provider) AS AAA ON provider.id = AAA.provider"
    dsprovs = db.executesql(sql)

    #get company subscribed list of plans
    sql = "SELECT 1 AS hmoplanid, '--Select--' AS Plan "
    sql = sql + " UNION "
    sql = sql + "SELECT hmoplan.id AS hmoplanid, CONCAT(hmoplan.hmoplancode,' ', hmoplan.name) AS Plan from companyhmoplanrate "
    sql = sql + " LEFT JOIN hmoplan on hmoplan.id = companyhmoplanrate.hmoplan"
    sql = sql + " WHERE companyhmoplanrate.company = " + str(companyid )
    sql = sql + " GROUP BY hmoplan.id"

    dsplans = db.executesql(sql)
    returnurl = URL('member','list_member', vars=dict(page=page))
    return dict(username=username,returnurl=returnurl, formA=formA, formB=formB, rows=rows, ds=ds, providerid = providerid, providername=providername,formheader=formheader, memberid=memberid,webkey=webkey,subscribers=subscribers, maxsubscribers=maxsubscribers,dsprovs=dsprovs,dsplans=dsplans,planid=planid,page=page)





@auth.requires_membership('webadmin')
@auth.requires_login()
def delete_webmember():

    address = None
    name = None
    enrollmentdate = None
    terminationdate = None

    webmemberid = 0
    webmember = None

    webkey = None
    email  = None

    memberid = 0

    fnocomma = lambda name: name   if ((name != "") & (name != None)) else ""
    f = lambda name: name + ", "  if ((name != "") & (name != None)) else ""

    if(len(request.args[0]) == 0):
        raise HTTP(403,"No Member to delete")
    name = None
    try:
        webmemberid = int(request.args[0])
        rows = db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).\
            select(db.webmember.ALL, db.provider.ALL, db.company.ALL, db.hmoplan.ALL,\
            left=[db.company.on(db.company.id == db.webmember.company), db.provider.on(db.provider.id == db.webmember.provider),\
                  db.hmoplan.on(db.hmoplan.id == db.webmember.hmoplan)])

        if(len(rows) == 0):
            raise HTTP(403,"No Member to delete ")



        name = f(rows[0]['webmember.fname'])  + fnocomma(rows[0]['webmember.lname'])
        webmember = fnocomma(rows[0]['webmember.webmember'])

        address = f(rows[0]['webmember.address1']) +   f(rows[0]['webmember.address2'])  + f(rows[0]['webmember.address3'])  + \
            f(rows[0]['webmember.city']) +  f(rows[0]['webmember.st']) +  fnocomma(rows[0]['webmember.pin'])

        webkey = rows[0]['webmember.webkey']
        email  = rows[0]['webmember.email']

        provider = fnocomma(rows[0]['provider.providername'])
        providercode = fnocomma(rows[0]['provider.provider'])
        company  = fnocomma(rows[0]['company.name'])
        plan  = fnocomma(rows[0]['hmoplan.name'])

        pats = db((db.patientmember.patientmember == webmember) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
        if(len(pats)>0):
            memberid = pats[0].id
            enrollmentdate =  pats[0].enrollmentdate
            terminationdate = datetime.date.today()
        else:
            enrollmentdate = rows[0]['webmember.webenrollcompletedate']
            terminationdate = datetime.date.today()

        sql = "SELECT SUM(paymentamount) as premiumtotal, MAX(paymentdate) AS lastpremiumdate "
        sql = sql + " FROM paymenttxlog WHERE webmember = " + str(webmemberid) + " AND responsecode = " + str(0)
        sql = sql + " GROUP BY webmember"
        ds = db.executesql(sql)

        premiumtotal = 0.00
        lastpremiumdate = ""
        if(len(ds) > 0):
            premiumtotal    = ds[0][0]
            lastpremiumdate = ds[0][1]


    except Exception, e:
        raise HTTP(403,e.message)

    form = FORM.confirm('Yes?',{'No':URL('member','list_webmember')})



    if form.accepted:
        db((db.patientmember.id == memberid)  & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).update(is_active = False, terminationdate  = datetime.date.today(), \
                                                                                                                                           email = 'del_' + email, status = 'Revoked')
        db(db.webmember.id == webmemberid).update(is_active = False,status = 'Revoked',enrollstatus = 'Revoked', email = 'del_' + email, webkey = 'del_' + webkey)
        db(db.patientmemberdependants.patientmember == memberid).update(is_active = False)
        db(db.webmemberdependants.webmember == webmemberid).update(is_active = False)

        rows = db((db.auth_user.sitekey == webkey) & (db.auth_user.email == email)).select()
        if(len(rows)>0):
            userid = rows[0].id
            username = rows[0].username
            db(db.auth_user.id == userid).update(email = 'del_' + email, sitekey = 'del_' + webkey,username = 'del_' + username )



        redirect(URL('member','list_webmember'))

    return dict(form=form,webmemberid=webmemberid,webmember=webmember, name=name, address=address, company=company, provider=provider, providercode=providercode,plan=plan,\
                enrollmentdate=enrollmentdate,terminationdate=terminationdate,premiumtotal=premiumtotal,lastpremiumdate=lastpremiumdate)

@auth.requires_membership('webadmin')
@auth.requires_login()
def delete_member():

    patientmember = None
    address = None
    name = None
    enrollmentdate = None
    terminationdate = None

    webmemberid = 0
    webkey = None
    email  = None


    fnocomma = lambda name: name   if ((name != "") & (name != None)) else ""
    f = lambda name: name + ", "  if ((name != "") & (name != None)) else ""

    if(len(request.args[0]) == 0):
        raise HTTP(403,"No Member to delete")
    name = None
    try:
        memberid = int(common.getid(request.args[0]))
        rows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember==True)).\
            select(db.patientmember.ALL, db.provider.ALL, db.company.ALL, db.hmoplan.ALL,db.webmember.ALL,\
            left=[db.company.on(db.company.id == db.patientmember.company), db.provider.on(db.provider.id == db.patientmember.provider),\
                  db.hmoplan.on(db.hmoplan.id == db.patientmember.hmoplan), db.webmember.on(db.webmember.id == db.patientmember.webmember)])

        if(len(rows) == 0):
            raise HTTP(403,"No Member to delete ")


        webmemberid = int(common.getid(rows[0]['webmember.id']))
        name = f(rows[0]['patientmember.fname'])  + fnocomma(rows[0]['patientmember.lname'])
        patientmember = fnocomma(rows[0]['patientmember.patientmember'])

        webkey = rows[0]['patientmember.webkey']
        email  = rows[0]['patientmember.email']

        address = f(rows[0]['patientmember.address1']) +   f(rows[0]['patientmember.address2'])  + f(rows[0]['patientmember.address3'])  + \
            f(rows[0]['patientmember.city']) +  f(rows[0]['patientmember.st']) +  fnocomma(rows[0]['patientmember.pin'])

        provider = fnocomma(rows[0]['provider.providername'])
        providercode = fnocomma(rows[0]['provider.provider'])
        company  = fnocomma(rows[0]['company.name'])
        plan  = fnocomma(rows[0]['hmoplan.name'])
        enrollmentdate = rows[0]['patientmember.enrollmentdate']
        terminationdate = datetime.date.today()

        sql = "SELECT SUM(paymentamount) as premiumtotal, MAX(paymentdate) AS lastpremiumdate "
        sql = sql + " FROM paymenttxlog WHERE webmember = " + str(webmemberid) + " AND responsecode = " + str(0)
        sql = sql + " GROUP BY webmember"
        ds = db.executesql(sql)

        premiumtotal = 0.00
        lastpremiumdate = ""
        if(len(ds) > 0):
            premiumtotal    = ds[0][0]
            lastpremiumdate = ds[0][1]


    except Exception, e:
        raise HTTP(403,e.message)

    form = FORM.confirm('Yes?',{'No':URL('member','list_member')})



    if form.accepted:
        db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).update(is_active = False, terminationdate  = datetime.date.today(), status = 'Revoked')
	db(db.patientmemberdependants.patientmember == memberid).update(is_active = False)
	
	if(webmemberid > 0):
	    db(db.webmember.id == webmemberid).update(is_active = False,status = 'Revoked',enrollstatus = 'Revoked')
	    db(db.webmemberdependants.webmember == webmemberid).update(is_active = False)
        

        rows = db((db.auth_user.sitekey == webkey) & (db.auth_user.email == email)).select()
        if(len(rows)>0):
            userid = rows[0].id
            username = rows[0].username
            db(db.auth_user.id == userid).update(email = 'x' + email, sitekey = 'x' + webkey,username = 'x' + username )

        redirect(URL('member','list_member'))

    return dict(form=form,memberid=memberid,patientmember=patientmember, name=name, address=address, company=company, provider=provider, providercode=providercode,plan=plan,\
                enrollmentdate=enrollmentdate,terminationdate=terminationdate,premiumtotal=premiumtotal,lastpremiumdate=lastpremiumdate)







@auth.requires_membership('webadmin')
@auth.requires_login()
def update_dependant():
    formheader="Dependant Data"
    dependantid = int(request.args[0])
    memberid = int(request.args[1])
    companyid = 0
    hmoplanid = 0


    rows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    fname = rows[0].fname
    lname = rows[0].lname
    companyid = rows[0].company
    rows = db(db.company.id == companyid).select()
    if(len(rows)>0):
        maxsubscribers = int(rows[0].maxsubscribers)
        hmoplanid = int(rows[0].hmoplan)
    else:
        raise HTTP(403,"Company not assigned for these dependants")


    relations = db((db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.hmoplan == hmoplanid) & (db.companyhmoplanrate.is_active == True) & (db.companyhmoplanrate.relation.lower() != 'self')).select(db.companyhmoplanrate.relation)

    rows = db(db.patientmemberdependants.id == dependantid).select()
    if(len(rows)>0):
        relation = rows[0].relation
    else:
         raise HTTP(403,"Dependant do not relations")

    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('member','update_member',args=[memberid])
    db.patientmemberdependants.patientmember.default = memberid
    db.patientmemberdependants.patientmember.writable = False
    db.patientmemberdependants.paid.writable = False
    formA = crud.update(db.patientmemberdependants, dependantid,cast=int,message="Member Dependant Information Updated!")

    return dict(formA=formA, formheader=formheader, memberid=memberid, dependantid=dependantid,fname=fname,lname=lname,relations=relations,selectedrelation=relation)

@auth.requires_membership('webadmin')
@auth.requires_login()
def delete_dependant():

    if(len(request.args[0]) == 0):
        raise HTTP(400,"Nothing to delete ")
    name = None
    memberid = int(request.args[1])
    depid = int(request.args[0])


    rows = db(db.patientmemberdependants.id == depid).select()
    if(len(rows) == 0):
        raise HTTP(400,"Nothing to delete ")
    name = rows[0].fname + ' ' + rows[0].lname


    form = FORM.confirm('Yes?',{'No':URL('member','update_member',args=[memberid])})




    if form.accepted:
        members = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select(db.patientmember.webmember)
        webmemberid = int(common.getid(members[0].webmember))
        webmembers = db(db.patientmemberdependants.id == depid).select(db.patientmemberdependants.fname,db.patientmemberdependants.lname)
        fname = webmembers[0].fname
        lname = webmembers[0].lname        
        db(db.patientmemberdependants.id == depid).delete()
        db((db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.fname == fname) \
                  & (db.webmemberdependants.lname == lname)).delete()        
        redirect(URL('member','update_member',args=[memberid]))

    return dict(form=form,memberid=memberid,name=name)



#IB 05292016
def acceptupdatewebmember_1(form):

    if(form.request_vars.action == 'addphoto'):
        redirect(URL('member','member_picture_1',vars=dict(page=common.getgridpage(request.vars)),args=[form.vars.id]))
    if(form.request_vars.action == 'adddependant'):
        redirect(URL('member','create_webdependant_0',vars=dict(page=common.getgridpage(request.vars)),args=[form.vars.id,1]))
    if(form.request_vars.action == 'enrollment'):
        redirect(URL('member','enroll_webmember',vars=dict(page=common.getgridpage(request.vars)),args=[form.vars.id,form.vars.company,form.vars.fname,form.vars.webdob]))
    if(form.request_vars.action == 'makepayment'):
        redirect(URL('member','new_webmember_premiumpayment',vars=dict(page=common.getgridpage(request.vars)),args=[form.vars.id]))

    return dict()

#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def update_webmember_1():

   
    username = auth.user.first_name + ' ' + auth.user.last_name
   
    formheader = "Pending Member Enrollment"

    webmemberid  = 0
    companyid    = 0
    providerid   = 0
    planid = 0
   
    
    providername = None
    ds = None
    memberrows = None
    deprows = None

    subscribers = 0
    maxsubscribers = 1
    memberpin = None
    status = "No_Attempt"
    pin1 = ''
    pin2 = ''
    pin3 = ''

    if(len(request.args) == 0):
        raise HTTP(400, "No Web Member : Error Updating Web Member")

    webmemberid = request.args[0]
    webmemberrows = db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).\
           select(db.webmember.ALL, db.provider.ALL, db.company.ALL, db.hmoplan.ALL,db.groupregion.ALL,\
           left=[db.company.on(db.company.id == db.webmember.company), db.provider.on(db.provider.id == db.webmember.provider),\
                 db.hmoplan.on(db.hmoplan.id == db.webmember.hmoplan), db.groupregion.on(db.groupregion.id == db.webmember.groupregion)])

    if(len(webmemberrows)==0):
        response.flash = 'Error in  Web Member Information'
        return dict()

    companyid      = int(common.getid(webmemberrows[0]['company.id']))
    #maxsubscribers = int(common.getid(webmemberrows[0]['company.maxsubscribers']))
    planid    = int(common.getid(webmemberrows[0]['hmoplan.id']))

    providerid = int(common.getid(webmemberrows[0]['provider.id']))
    providername = webmemberrows[0]['provider.providername']

    status    = webmemberrows[0]['webmember.status']
    memberpin = webmemberrows[0]['webmember.pin']
    pin1 = common.getstring(webmemberrows[0]['webmember.pin1']).strip()
    pin2 = common.getstring(webmemberrows[0]['webmember.pin2']).strip()
    pin3 = common.getstring(webmemberrows[0]['webmember.pin3']).strip()
    
    regionid  = int(common.getid(webmemberrows[0]['webmember.groupregion']))
    if(regionid == 0):
        regionid = 1
    db.webmember.groupregion.default = regionid
    
    x = db((db.companyhmoplanrate.company==companyid) & \
           (db.companyhmoplanrate.hmoplan==planid) &  \
           (db.companyhmoplanrate.groupregion==regionid) & \
           (db.companyhmoplanrate.is_active==True)).select()
       
    if(len(x)>0):
        maxsubscribers = int(len(x))
    else:
        maxsubscribers = 1
           

    deprows = db(db.webmemberdependants.webmember == webmemberid).select()
    subscribers = subscribers + len(webmemberrows) + len(deprows)
    relations = 0
    relations = db((db.companyhmoplanrate.company == companyid) & \
                   (db.companyhmoplanrate.hmoplan == planid) & \
                   (db.companyhmoplanrate.relation != 'Self') & \
                   (db.companyhmoplanrate.is_active == True)).count(db.companyhmoplanrate.relation)
    
    
    #if(int(companyid) > 0):
        
    if((planid != '') & (planid != None) & (planid != 0)):
        sql = "UPDATE webmember SET hmoplan = " + str(planid) + " WHERE id = " + str(webmemberid) + ";"
        db.executesql(sql)
        db.commit()
    else:
        sql = "UPDATE webmember SET hmoplan = NULL WHERE id = " + str(webmemberid) + ";"
        db.executesql(sql)
        db.commit()

    db.webmember.hmoplan.default = planid
    
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('member','update_webmember_1',args=[webmemberid],vars=dict(page=common.getgridpage(request.vars)))
    crud.settings.update_onaccept = acceptupdatewebmember_1


    db.webmember.webkey.writable = False
    #db.webmember.company.writable = False
    db.webmember.provider.writable = True
    db.webmember.webmember.writable = False

    db.webmember.status.writable = True
    db.webmember.imported.writable = False
    db.webmember.memberorder.writable = False
    db.webmember.imported.readable = False
    db.webmember.memberorder.readable = False

    db.webmember.paid.writable = False


    #if((reg == None) | (reg == 1)):
    if(((pin1 == '')|(pin1==None)) & ((pin2 == '')|(pin2==None)) & ((pin3 == '')|(pin3==None))):
        ds = db((db.provider.id == 1 ) | ((db.provider.id != 1) & (db.provider.is_active == True))).select()
    else:
        ds = db((db.provider.id == 1) | ((pin1 != '') & (db.provider.pin == pin1) & (db.provider.is_active == True)) | \
        ((pin2 != '')&(db.provider.pin == pin2) & (db.provider.is_active == True)) | \
        ((pin3 != '')&(db.provider.pin == pin3) & (db.provider.is_active == True))).select()
        if(len(ds) <= 1):
            ds = db((db.provider.id == 1) | ((memberpin != '') & (db.provider.pin == memberpin) & (db.provider.is_active == True) )).select()
        if(len(ds) <= 1):
            ds = db((db.provider.id == 1 ) | ((db.provider.id != 1) & (db.provider.is_active == True) )).select()
    

    formA = crud.update(db.webmember, webmemberid,cast=int, message='Member Information Updated!')

  
    if formA.accepted:
	i = 0
    elif formA.errors:
	u = 0
	

    ## Display Dependant List for this member
    fields=(db.webmemberdependants.fname,db.webmemberdependants.lname,db.webmemberdependants.gender,db.webmemberdependants.depdob,db.webmemberdependants.relation)

    headers={'webmemberdependants.fname':'First Name',
             'webmemberdependants.lname': 'Last Name',
             'webmemberdependants.depdob': 'DOB',
             'webmemberdependants.gender': 'Gender',
             'webmemberdependants.relation':'Relation'
             }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)

    left = None
    links = [lambda row: A('Update',_href=URL("member","update_webdependant_0",vars=dict(page=common.getgridpage(request.vars)),args=[row.id,webmemberid,1])), lambda row: A('Delete',_href=URL("member","delete_webdependant_0",args=[row.id,webmemberid,1]))]

    query = (db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.is_active==True)


    ## called from menu
    formB = SQLFORM.grid(query=query,
                         headers=headers,
                         fields=fields,
                         links=links,
                         left=left,
                         exportclasses=exportlist,
                         links_in_grid=True,
                         searchable=False,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                         )


    sql = "select provider.id, IFNULL(AAA.providercount,0) AS providercount from provider left join "
    sql = sql + "(select provider, count(provider) AS providercount from webmember group by provider) AS AAA ON provider.id = AAA.provider"
    sql = sql + " where (provider.is_active = 'T'  OR provider.id = 1)"
    dsprovs = db.executesql(sql)

    #get company subscribed list of plans

    #if((planid != '') & (planid != None) & (planid != 1)):
        #sql = "SELECT 1 AS hmoplanid, '--Select--' AS Plan "
        #sql = sql + " UNION "
        #sql = sql + "SELECT hmoplan.id AS hmoplanid, CONCAT(hmoplan.hmoplancode,' ', hmoplan.name) AS Plan from hmoplan "
        #sql = sql + " WHERE hmoplan.id = " + str(planid )
    #else:
        #sql = "SELECT 1 AS hmoplanid, '--Select--' AS Plan "
        #sql = sql + " UNION "
        #sql = sql + "SELECT hmoplan.id AS hmoplanid, CONCAT(hmoplan.hmoplancode,' ', hmoplan.name) AS Plan from hmoplan "
        ##sql = sql + " WHERE hmoplan.id = " + str(0)

    #dsplans = db.executesql(sql)
    regions = db(db.groupregion.is_active == True).select()  #IB 07042016
    plans = db((db.companyhmoplanrate.is_active == True) & (db.companyhmoplanrate.groupregion==regionid) & \
               (db.companyhmoplanrate.company==companyid) & (db.companyhmoplanrate.relation == 'Self')).\
           select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
                  left=db.hmoplan.on(db.companyhmoplanrate.hmoplan == db.hmoplan.id))    
    returnurl = URL('member','list_webmember', vars=dict(page=common.getgridpage(request.vars)))
    showenrollment=checkenrollment(formA,status)
    page = common.getgridpage(request.vars)
    return dict(username=username, returnurl=returnurl,formA=formA, formB=formB, formheader=formheader, \
                webmemberid=webmemberid,providername=providername,providerid=providerid, \
                regionid=regionid, regions=regions,ds=ds,rows=webmemberrows,subscribers=subscribers, \
                maxsubscribers=maxsubscribers,showenrollment=showenrollment,\
                dsprovs=dsprovs,plans=plans, planid=planid,relations=relations,page=page)





def checkenrollment(form,status):

    retval = False
    if ((form.vars.fname == '') | (form.vars.lname == '') |  (form.vars.address1 == '')|  (form.vars.address2 == '')|  (form.vars.city == '')|  (form.vars.st == '')|  (form.vars.pin == '')|(form.vars.provider == '')|(form.vars.groupregion == '')):
        retval = False
    elif ((form.record.fname == '') | (form.record.lname == '') |  (form.record.address1 == '')|  (form.record.address2 == '')|  (form.record.city == '')|  (form.record.st == '')|  (form.record.pin == '')| (form.record.provider == '') | (form.record.provider == 1) | (form.record.groupregion == None) | (form.record.groupregion == '')):
        retval = False
    else:
        if((status == 'Completed')|(status=='Enrolled')|(status=='Revoked')):
            retval = True

    return retval

def checkout(form,status,planid):

    retval = False
    if ((form.vars.fname == '') | (form.vars.lname == '') |  (form.vars.address1 == '')|  (form.vars.address2 == '')|  (form.vars.city == '')|  (form.vars.st == '')|  (form.vars.pin == '')):
        retval = False
    elif ((form.record.fname == '') | (form.record.lname == '') |  (form.record.address1 == '')|  (form.record.address2 == '')|  (form.record.city == '')|  (form.record.st == '')|  (form.record.pin == '')):
        retval = False
    elif ((planid == None) | (planid == 1) | (planid == '')):
        retval = False
    else:
        if((status == 'No_Attempt')|(status == 'Attempting')):
            retval = True

    return retval

#IB 05292016
def member_picture_1():

    formheader = "Member Picture"

    webkey = None
    status = 'No_Attempt'
    webmemberrows = None
    subscribers = 1
    maxsubscribers = 1
    companyid = 0
    planid = 0
    webmemberid = 0
    subscribererrmssg = None

    if(len(request.args) == 0):
        raise HTTP(400, "No Web Member : Error Updating Web Member")

    webmemberid = request.args[0]
    webmemberrows = db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).\
           select(db.webmember.ALL, db.provider.ALL, db.company.ALL, db.hmoplan.ALL,db.groupregion.ALL,\
           left=[db.company.on(db.company.id == db.webmember.company), db.provider.on(db.provider.id == db.webmember.provider),\
                 db.hmoplan.on(db.hmoplan.id == db.webmember.hmoplan), db.groupregion.on(db.groupregion.id == db.webmember.groupregion)])

    if(len(webmemberrows)==0):
        response.flash = 'Error in  Web Member Information'
        return dict()

    webkey = webmemberrows[0]['webmember.webkey']

    status = webmemberrows[0]['webmember.status']
    if((status == 'No_Attempt')|(status == None)):
        status = 'Attempting'

    subscribers = subscribers + db((db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.is_active == True)).count()

    maxsubscribers = webmemberrows[0]['company.maxsubscribers']
    if(subscribers > maxsubscribers):
            subscribererrmssg = "You have more subscribers than allowed " + str(maxsubscribers) + ". Please delete additional subscribers."

    planid = webmemberrows[0]['hmoplan.id']

    companyid = webmemberrows[0]['company.id']
    companyname = webmemberrows[0]['company.name']
    companycode = webmemberrows[0]['company.company']
    maxsubscribers = webmemberrows[0]['company.maxsubscribers']


    providerid = webmemberrows[0]['provider.id']
    providername = webmemberrows[0]['provider.providername']

    status    = webmemberrows[0]['webmember.status']



    crud.settings.keepvalues = True
    crud.settings.showid     = True
    crud.settings.update_next = URL('member','member_picture_1',vars=dict(page=common.getgridpage(request.vars)),args=[webmemberid]) #IB 05292016
    crud.messages.submit_button = 'Submit'




    db.webmember.webmember.writable = False
    db.webmember.groupregion.writable = True

    db.webmember.webmember.writable = False
    db.webmember.webenrolldate.writable = False
    db.webmember.webenrollcompletedate.writable = False
    db.webmember.company.writable = False
    db.webmember.webkey.writable=False
    db.webmember.provider.writable = False
    db.webmember.groupregion.writable = True
    db.webmember.status.writable = True
    db.webmember.imported.writable = False
    db.webmember.memberorder.writable = False
    db.webmember.imported.readable = False
    db.webmember.memberorder.readable = False
    db.webmember.lname.readable = True

    formA = crud.update(db.webmember, webmemberid,cast=int)
    
        

    
    db.commit()

    sql = "select provider.id, IFNULL(AAA.providercount,0) AS providercount from provider left join "
    sql = sql + "(select provider, count(provider) AS providercount from webmember group by provider) AS AAA ON provider.id = AAA.provider"
    dsprovs = db.executesql(sql)

    ds = db(db.provider.is_active == True).select()

    sql = "SELECT 1 AS hmoplanid, '--Select--' AS Plan "
    sql = sql + " UNION "
    sql = sql + "SELECT hmoplan.id AS hmoplanid, CONCAT(hmoplan.hmoplancode,' ', hmoplan.name) AS Plan from companyhmoplanrate "
    sql = sql + " LEFT JOIN hmoplan on hmoplan.id = companyhmoplanrate.hmoplan"
    sql = sql + " WHERE companyhmoplanrate.company = " + str(companyid )
    sql = sql + " GROUP BY hmoplan.id"

    dsplans = db.executesql(sql)

    return dict(formA=formA, formheader=formheader, webmemberid=webmemberid,companyid=companyid,companyname = companyname,companycode=companycode,providername=providername,providerid=providerid, ds=ds,status=status,rows=webmemberrows,subscribers=subscribers, maxsubscribers=maxsubscribers,dsprovs=dsprovs,dsplans=dsplans, planid=planid,page=common.getgridpage(request.vars))



def member_picture_0():

    formheader = "Member Picture"

    ## Initialization
    webkey = None
    status = 'No_Attempt'
    webmemberrows = None
    subscribers = 1
    maxsubscribers = 1
    companyid = 0
    planid = 0
    webmemberid = 0
    subscribererrmssg = None

    if(len(request.args) == 0):
        raise HTTP(400, "No Web Member : Error Updating Web Member")

    webmemberid = request.args[0]
    webmemberrows = db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).\
           select(db.webmember.ALL, db.provider.ALL, db.company.ALL, db.hmoplan.ALL,db.groupregion.ALL,\
           left=[db.company.on(db.company.id == db.webmember.company), db.provider.on(db.provider.id == db.webmember.provider),\
                 db.hmoplan.on(db.hmoplan.id == db.webmember.hmoplan), db.groupregion.on(db.groupregion.id == db.webmember.groupregion)])

    if(len(webmemberrows)==0):
        response.flash = 'Error in  Web Member Information'
        return dict()

    webkey = webmemberrows[0]['webmember.webkey']

    status = webmemberrows[0]['webmember.status']
    if((status == 'No_Attempt')|(status == None)):
        status = 'Attempting'

    subscribers = subscribers + db((db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.is_active == True)).count()

    maxsubscribers = webmemberrows[0]['company.maxsubscribers']
    if(subscribers > maxsubscribers):
            subscribererrmssg = "You have more subscribers than allowed " + str(maxsubscribers) + ". Please delete additional subscribers."

    planid = webmemberrows[0]['hmoplan.id']

    companyid = webmemberrows[0]['company.id']

    crud.settings.keepvalues = True
    crud.settings.showid     = True
    crud.settings.update_next = URL('member','member_picture_0',args=[webmemberid])
    crud.messages.submit_button = 'Submit'
    #crud.settings.update_onaccept = acceptupdatewebmember


    db.webmember.hmoplan.default = planid
    db.webmember.webmember.writable = False
    db.webmember.webenrolldate.writable = False
    db.webmember.webenrollcompletedate.writable = False
    db.webmember.company.writable = False
    db.webmember.webkey.writable=False
    db.webmember.provider.writable = False
    db.webmember.status.writable = False
    db.webmember.imported.writable = False
    db.webmember.memberorder.writable = False
    db.webmember.imported.readable = False
    db.webmember.memberorder.readable = False
    db.webmember.webenrolldate.readable = False
    db.webmember.hmoplan.writable = True
    db.webmember.hmoplan.readable = True
    db.webmember.groupregion.writable = False
    db.webmember.webenrollcompletedate.readable = False




    formA = crud.update(db.webmember, webmemberid,cast=int)
    db.commit()





    #get company subscribed list of plans
    sql = "SELECT 1 AS hmoplanid, '--Select--' AS Plan "
    sql = sql + " UNION "
    sql = sql + "SELECT hmoplan.id AS hmoplanid, CONCAT(hmoplan.hmoplancode,' ', hmoplan.name) AS Plan from companyhmoplanrate "
    sql = sql + " LEFT JOIN hmoplan on hmoplan.id = companyhmoplanrate.hmoplan"
    sql = sql + " WHERE companyhmoplanrate.company = " + str(companyid )
    sql = sql + " GROUP BY hmoplan.id"

    dsplans = db.executesql(sql)


    return dict(formA=formA, formheader=formheader, webmemberid=webmemberid,webkey=webkey,fname=None,dob=None,status=None,rows=webmemberrows,dsplans=dsplans,planid=planid)

def member_picture():

    formheader = "Member Picture"

    memberid = request.args[0]
    rows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    status = rows[0].status
    fname = rows[0].fname
    lname = rows[0].lname
    dob = rows[0].dob

    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('member','update_member',args=[memberid])


    #db.patientmember.patientmember.writable = False
    #db.patientmember.groupregion.writable = False

    #db.patientmember.enrollmentdate.writable = False
    #db.patientmember.duedate.writable = False
    #db.patientmember.company.writable = False
    #db.patientmember.webkey.writable=False
    #db.patientmember.provider.writable = False
    #db.patientmember.groupregion.writable = False
    #db.patientmember.status.writable = False

    #db.patientmember.memberorder.writable = False
    #db.patientmember.memberorder.readable = False
    #db.patientmember.lname.readable = True


    formA = crud.update(db.patientmember, memberid,cast=int)
    db.commit()



    return dict(formA=formA,  formheader=formheader, memberid=memberid,fname=fname,dob=dob,status=status,page=common.getgridpage(request.vars))


def acceptupdate_webdependant_0(form):

    page = request.vars.page
    webdepid = int(common.getid(form.vars.id))
    sourceid = int(common.getid(form.vars.sourceid))
    webdeps  = db((db.webmemberdependants.id == webdepid) & (db.webmemberdependants.is_active == True)).select()
    webememberid = 0
    patdepid = 0
    webstatus = "Attempting"
    if(len(webdeps) > 0):
        webmemberid = int(common.getid(webdeps[0].webmember))
        patdepid = int(common.getid(webdeps[0].patdepid))
        webmembers = db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).select()
        if(len(webmembers)>0):
            webstatus = webmembers[0].status
        
        if(webstatus == 'Enrolled'):
            db(db.patientmemberdependants.id == patdepid).update(\
                fname = webdeps[0].fname,\
                mname = webdeps[0].mname,\
                lname = webdeps[0].lname,\
                depdob = webdeps[0].depdob,\
                gender = webdeps[0].gender,\
                relation = webdeps[0].relation,\
                paid = webdeps[0].paid,\
                modified_by = webdeps[0].modified_by,\
                modified_on = webdeps[0].modified_on)
            
    if(sourceid == 0):
        redirect(URL('member','update_webmember_0',vars=dict(page=page),args=[webmemberid]))
    else:
        crud.settings.update_next = URL('member','update_webmember_1',vars=dict(page=page),args=[webmemberid])

    return dict()


def acceptupdatewebmember_0(form):

    if(form.request_vars.action == 'addphoto'):
        redirect(URL('member','member_picture_0',args=[form.vars.id]))
    if(form.request_vars.action == 'adddependant'):
        redirect(URL('member','create_webdependant_0',args=[form.vars.id,0]))
    if(form.request_vars.action == 'checkout'):
        redirect(URL('member','create_checkout',args=[form.vars.id,form.vars.webkey,form.vars.fname,form.vars.webdob]))
    

    
    return dict()

def update_webmember_0():

    formheader = "Member Enrollment"

    ## Initialization
    webkey = None
    status = 'No_Attempt'
    webmemberrows = None
    subscribers = 1
    maxsubscribers = 1
    companyid = 0
    planid = 0
    regionid = 0
    webmemberid = 0
    subscribererrmssg = None
    paid = False

    if(len(request.args) == 0):
        raise HTTP(400, "No Web Member : Error Updating Web Member")

            


    webmemberid = request.args[0]
    webmemberrows = db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).\
           select(db.webmember.ALL, db.provider.ALL, db.company.ALL, db.hmoplan.ALL,db.groupregion.ALL,\
           left=[db.company.on(db.company.id == db.webmember.company), db.provider.on(db.provider.id == db.webmember.provider),\
                 db.hmoplan.on(db.hmoplan.id == db.webmember.hmoplan), db.groupregion.on(db.groupregion.id == db.webmember.groupregion)])

    if(len(webmemberrows)==0):
        response.flash = 'Error in  Web Member Information'
        return dict()

    webkey = webmemberrows[0]['webmember.webkey']

    status = webmemberrows[0]['webmember.status']
    if((status == 'No_Attempt')|(status == None)):
        status = 'Attempting'

    subscribers = subscribers + db((db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.is_active == True)).count()

    maxsubscribers = webmemberrows[0]['company.maxsubscribers']
    if(subscribers > maxsubscribers):
            subscribererrmssg = "You have more subscribers than allowed " + str(maxsubscribers) + ". Please delete additional subscribers."

    relations = -1
    companyid = int(common.getid(webmemberrows[0]['webmember.company']))
    planid = int(common.getid(webmemberrows[0]['webmember.hmoplan']))
    regionid = int(common.getid(webmemberrows[0]['webmember.groupregion']))
    paid = common.getbool(webmemberrows[0]['webmember.paid'])
    
    if((planid != '') & (planid != None)):
        sql = "UPDATE webmember SET hmoplan = " + str(planid) + " WHERE id = " + str(webmemberid) + ";"
        db.executesql(sql)
        db.commit()

        relations = db((db.companyhmoplanrate.company == companyid) & \
                       (db.companyhmoplanrate.hmoplan == planid) & \
                       (db.companyhmoplanrate.relation != 'Self') & \
                       (db.companyhmoplanrate.is_active == True)).count(db.companyhmoplanrate.relation)
        if(planid == 1):
            relations = -1
    else:
        sql = "UPDATE webmember SET hmoplan = NULL WHERE id = " + str(webmemberid) + ";"
        db.executesql(sql)
        db.commit()

    providerid = webmemberrows[0]['provider.id']
    providername = webmemberrows[0]['provider.providername']
    
    crud.settings.keepvalues = True
    crud.settings.showid     = True
    crud.settings.update_next = URL('member','update_webmember_0',args=[webmemberid])
    crud.messages.submit_button = 'Submit'
    crud.settings.update_onaccept = acceptupdatewebmember_0
    
    
    db.webmember.company.requires= IS_IN_DB(db(db.company.id==companyid), 'company.id', '%(name)s (%(company)s)')

    db.webmember.hmoplan.default = planid
    db.webmember.groupregion.default = regionid
    db.webmember.company.default = companyid
    
    db.webmember.webmember.writable = False
    db.webmember.webenrolldate.writable = False
    db.webmember.webenrollcompletedate.writable = False
    #db.webmember.company.writable = False
   
    db.webmember.webkey.writable=False
    db.webmember.provider.writable = False
    db.webmember.status.writable = False
    db.webmember.imported.writable = False
    db.webmember.memberorder.writable = False
    db.webmember.imported.readable = False
    db.webmember.memberorder.readable = False
    db.webmember.webenrolldate.readable = False
    #db.webmember.hmoplan.writable = False
    #db.webmember.hmoplan.readable = True
    #db.webmember.groupregion.writable = False
    db.webmember.webenrollcompletedate.readable = False
    db.webmember.paid.writable = False

    db.webmember.fname.requires = [IS_NOT_EMPTY()]
    db.webmember.lname.requires = [IS_NOT_EMPTY()]
    db.webmember.address1.requires = [IS_NOT_EMPTY()]
    db.webmember.address2.requires = [IS_NOT_EMPTY()]
    db.webmember.pin.requires = [IS_NOT_EMPTY()]
    db.webmember.cell.requires = [IS_NOT_EMPTY()]
    db.webmember.email.requires = [IS_NOT_EMPTY(),IS_EMAIL()]
    
    db.webmember.cell.length = 10
    
    
    
    formA = crud.update(db.webmember, webmemberid,cast=int, message='Member Information Updated!')
    formA.record.hmoplan = planid
    formA.record.groupregion = regionid
    
    formB = None
    
    
    
    ## Display Dependant List for this member
    fields=(db.webmemberdependants.fname,db.webmemberdependants.lname,db.webmemberdependants.gender,db.webmemberdependants.depdob,db.webmemberdependants.relation)

    headers={'webmemberdependants.fname':'First Name',
             'webmemberdependants.lname': 'Last Name',
             'webmemberdependants.depdob': 'DOB',
             'webmemberdependants.gender': 'Gender',
             'webmemberdependants.relation':'Relation'
             }

    exportlist =  dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)

    left  = None
    links = [lambda row: A('Update',_href=URL("member","update_webdependant_0",args=[row.id,webmemberid,0])), lambda row: A('Delete',_href=URL("member","delete_webdependant_0",args=[row.id,webmemberid,0]))]

    query = (db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.is_active==True)


    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             left=left,
                             exportclasses=exportlist,
                             links_in_grid=True,
                             searchable=False,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )



    #regions = db(db.groupregion.is_active == True).select()
    
    regions = db((db.groupregion.is_active == True) & (db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.is_active == True)).\
               select(db.groupregion.ALL,\
                      left=db.companyhmoplanrate.on((db.companyhmoplanrate.groupregion==db.groupregion.id)  ), distinct=True, orderby=db.groupregion.id)    
    
    plans = db((db.companyhmoplanrate.is_active == True) & (db.companyhmoplanrate.groupregion==regionid) & \
               (db.companyhmoplanrate.company==companyid) & (db.companyhmoplanrate.relation == 'Self')).\
           select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
                  left=db.hmoplan.on((db.companyhmoplanrate.hmoplan == db.hmoplan.id)&(db.hmoplan.is_active==True)))   
    
    ## redirect on Items, with PO ID and return URL
    showcheckout=checkout(formA,status,planid)
    login = "login"
    
    
	
    return dict(db=db, formA=formA, formB=formB, formheader=formheader, webmemberid=webmemberid,webkey=webkey,fname=None,dob=None,status=None,rows=webmemberrows,providername=providername,subscribers=subscribers, maxsubscribers = maxsubscribers, showcheckout=showcheckout,logmode=login,\
                plans=plans,regions=regions,regionid=regionid,planid=planid,relations=relations,paid=paid)



@auth.requires_membership('webadmin')
@auth.requires_login()
def create_webdependant_1():
    
    if(len(request.args) == 0):
        raise HTTP(400, "Error creating a dependant as there is no primary member")
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    page=common.getgridpage(request.vars)
    webmemberid  = request.args[0]
    sourceid     = request.args[1]

    fname = None
    lname = None
    formheader   = "Add New Dependant"

    companyid = 0
    hmoplanid = 0
    relations = None

    webmemberrows = db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).\
        select(db.webmember.ALL,db.company.ALL, db.hmoplan.ALL,\
        left=[db.company.on(db.company.id == db.webmember.company),\
        db.hmoplan.on(db.hmoplan.id == db.webmember.hmoplan)])

    if(len(webmemberrows)==0):
        raise HTTP(400, "Error creating a dependant as there is no assigned primary member")

    fname = webmemberrows[0]['webmember.fname']
    lname = webmemberrows[0]['webmember.lname']
    hmoplanid = webmemberrows[0]['hmoplan.id']
    companyid = webmemberrows[0]['company.id']


    relations = db((db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.hmoplan == hmoplanid) & (db.companyhmoplanrate.is_active == True) & (db.companyhmoplanrate.relation.lower() != 'self')).select(db.companyhmoplanrate.relation)
    rows = db(db.webmemberdependants.webmember == webmemberid).select()
    dependantnumber = len(rows) + 2


    crud.settings.keepvalues = True
    crud.settings.showid = True
    db.webmemberdependants.webmember.default = webmemberid
    db.webmemberdependants.memberorder.default = dependantnumber
    db.webmemberdependants.webmember.writable = False
    db.webmemberdependants.memberorder.writable = False
    if(len(relations) > 0):
        db.webmemberdependants.relation.default = relations[0].relation
        
    #IB 05292016
    crud.settings.create_next = URL('member','create_webdependant_1',vars=dict(page=page),args=[webmemberid,sourceid])

    formA = crud.create(db.webmemberdependants, message='New Member Dependant Added!')

    fields=(db.webmemberdependants.fname,db.webmemberdependants.lname,db.webmemberdependants.gender,db.webmemberdependants.depdob,db.webmemberdependants.relation)

    headers={'webmemberdependants.fname':'First Name',
             'webmemberdependants.lname': 'Last Name',
             'webmemberdependants.depdob': 'DOB',
             'webmemberdependants.gender': 'Gender',
             'webmemberdependants.relation':'Relation'
             }

    exportlist =  dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)

    left  = None
    links = None

    query = (db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.is_active==True)


    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             left=left,
                             exportclasses=exportlist,
                             links_in_grid=True,
                             searchable=False,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )


    returnurl = URL('member', 'update_webmember_1',vars=dict(page=page), args=[webmemberid])
    return dict(username=username,formA=formA,  formB=formB, formheader=formheader,returnurl=returnurl, webmemberid=webmemberid,fname=fname,lname=lname,rows=rows,sourceid=sourceid,logmode=session.logmode,relations=relations,page=page)



#IB 05292016
def create_webdependant_0():



    if(len(request.args) == 0):
        raise HTTP(400, "Error creating a dependant as there is no primary member")

    page=common.getgridpage(request.vars)
    webmemberid  = request.args[0]
    sourceid     = request.args[1]

    fname = None
    lname = None
    formheader   = "Add New Dependant"

    companyid = 0
    hmoplanid = 0
    relations = None

    webmemberrows = db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).\
        select(db.webmember.ALL,db.company.ALL, db.hmoplan.ALL,\
        left=[db.company.on(db.company.id == db.webmember.company),\
        db.hmoplan.on(db.hmoplan.id == db.webmember.hmoplan)])

    if(len(webmemberrows)==0):
        raise HTTP(400, "Error creating a dependant as there is no assigned primary member")

    fname = webmemberrows[0]['webmember.fname']
    lname = webmemberrows[0]['webmember.lname']
    hmoplanid = webmemberrows[0]['webmember.hmoplan']
    regionid = webmemberrows[0]['webmember.groupregion']
    companyid = webmemberrows[0]['company.id']
 
    dependantmode = False
    ds = db(db.company.id == companyid).select()
    if(len(ds)>0):
        dependantmode = common.getbool(ds[0]['dependantmode'])
    

    relations = db((db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.hmoplan == hmoplanid) & (db.companyhmoplanrate.groupregion == regionid) & (db.companyhmoplanrate.is_active == True) & (db.companyhmoplanrate.relation.lower() != 'self')).select(db.companyhmoplanrate.relation)
    rows = db(db.webmemberdependants.webmember == webmemberid).select()
    dependantnumber = len(rows) + 2


    crud.settings.keepvalues = True
    crud.settings.showid = True
    
    if(dependantmode == True):
        db.webmemberdependants.relation.requires = IS_IN_SET(PLANRDEPENDANTS)    

    db.webmemberdependants.webmember.default = webmemberid
    db.webmemberdependants.memberorder.default = dependantnumber
    db.webmemberdependants.webmember.writable = False
    db.webmemberdependants.memberorder.writable = False
    if(len(relations) > 0):
        db.webmemberdependants.relation.default = relations[0].relation
        
    #IB 05292016
    crud.settings.create_next = URL('member','create_webdependant_0',vars=dict(page=page),args=[webmemberid,sourceid])
  
    
    formA = crud.create(db.webmemberdependants, message='New Member Dependant Added!')
    
   

    fields=(db.webmemberdependants.fname,db.webmemberdependants.lname,db.webmemberdependants.gender,db.webmemberdependants.depdob,db.webmemberdependants.relation)

    headers={'webmemberdependants.fname':'First Name',
             'webmemberdependants.lname': 'Last Name',
             'webmemberdependants.depdob': 'DOB',
             'webmemberdependants.gender': 'Gender',
             'webmemberdependants.relation':'Relation'
             }

    exportlist =  dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)

    left  = None
    links = None

    query = (db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.is_active==True)


    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             links=links,
                             left=left,
                             exportclasses=exportlist,
                             links_in_grid=True,
                             searchable=False,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )


    
    return dict(formA=formA,  formB=formB, formheader=formheader,webmemberid=webmemberid,fname=fname,lname=lname,rows=rows,sourceid=sourceid,logmode=session.logmode,relations=relations,page=page)

#IB 05292016
def update_webdependant_0():

    companyid = 0
    hmoplanid = 0
    relations = 0

    formheader="Dependant Data"

    webdependantid = request.args[0]
    webmemberid    = request.args[1]
    sourceid       = int(request.args[2])

    webmemberrows = db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).\
        select(db.webmember.ALL,  db.company.ALL, db.hmoplan.ALL,\
        left=[db.company.on(db.company.id == db.webmember.company),\
        db.hmoplan.on(db.hmoplan.id == db.webmember.hmoplan)])

    if(len(webmemberrows)==0):
        raise HTTP(400, "Error updating a dependant as there is no dependant")

    fname = webmemberrows[0]['webmember.fname']
    lname = webmemberrows[0]['webmember.lname']
    companyid = webmemberrows[0]['company.id']
    hmoplanid = webmemberrows[0]['hmoplan.id']

    dependantmode = False
    ds = db(db.company.id == companyid).select()
    if(len(ds)>0):
	dependantmode = common.getbool(ds[0]['dependantmode'])

    relations = db((db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.hmoplan == hmoplanid) & (db.companyhmoplanrate.is_active == True) & (db.companyhmoplanrate.relation.lower() != 'self')).select(db.companyhmoplanrate.relation)

    rows = db(db.webmemberdependants.id == webdependantid).select()
    if(len(rows)>0):
        relation = rows[0].relation
    else:
         raise HTTP(403,"There are no relations")

    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_onaccept = acceptupdate_webdependant_0

     
    
    #IB 05292016
    if(sourceid == 0):
        crud.settings.update_next = URL('member','update_webmember_0',vars=dict(page=common.getgridpage(request.vars)),args=[webmemberid])
    else:
        crud.settings.update_next = URL('member','update_webmember_1',vars=dict(page=common.getgridpage(request.vars)),args=[webmemberid])

    
    if(dependantmode == True):
	db.webmemberdependants.relation.requires = IS_IN_SET(PLANRDEPENDANTS) 
	
    db.webmemberdependants.webmember.default = webmemberid
    db.webmemberdependants.relation.default = relations[0].relation
    db.webmemberdependants.paid.writable = False
    db.webmemberdependants.webmember.writable = False
    db.webmemberdependants.memberorder.writable = False    
    
    formA = crud.update(db.webmemberdependants, webdependantid,cast=int, message='Member Dependant Information Updated!')

    return dict(formA=formA, formheader=formheader, webmemberid=webmemberid, webdependantid=webdependantid,rows=rows,fname=fname,lname=lname,sourceid = sourceid,logmode=session.logmode,relations=relations,selectedrelation=relation,page=common.getgridpage(request.vars))


@auth.requires_login()
def delete_webdependant_0():



    if(len(request.args[0]) == 0):
        raise HTTP(400,"Nothing to delete ")
    name = None
    try:
        webmemberid = int(request.args[1])
        webdepid = int(request.args[0])
        sourceid = int(request.args[2])

        rows = db(db.webmemberdependants.id == webdepid).select()
        if(len(rows) == 0):
            raise HTTP(400,"Nothing to delete ")
        name = rows[0].fname + ' ' + rows[0].lname
    except Exception, e:
        raise HTTP(400,e.message)

    if(sourceid == 0):
        form = FORM.confirm('Yes?',{'No':URL('member','update_webmember_0',args=[webmemberid])})
    else:
        form = FORM.confirm('Yes?',{'No':URL('member','update_webmember_1',args=[webmemberid])})



    if form.accepted:
        db(db.webmemberdependants.id == webdepid).delete()
        db.commit() 
        ds = db((db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.is_active == True)).select()
    
	
	
	for i in xrange(0, len(ds)):
	    db((db.webmemberdependants.id == int(common.getid(ds[i]["id"]))) & (db.webmemberdependants.is_active == True)).update(memberorder = (i+2))
     
	    
        if(sourceid == 0):
            redirect(URL('member','update_webmember_0',args=[webmemberid]))
        else:
            redirect(URL('member','update_webmember_1',args=[webmemberid]))

    return dict(form=form,webmemberid=webmemberid,name=name,sourceid=sourceid,logmode=session.logmode)




def update_webdependant():
    formheader="Dependant Data"
    webdependantid = int(request.args[0])
    webmemberid = int(request.args[1])
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('member','update_webdependant',args=[webdependantid,webmemberid])
    db.webmemberdependants.webmember.default = webmemberid
    db.webmemberdependants.webmember.writable = False

    
    formA = crud.update(db.webmemberdependants, webdependantid,cast=int)

    return dict(formA=formA, formheader=formheader, webmemberid=webmemberid, webdependantid=webdependantid)

@auth.requires_membership('webadmin')
@auth.requires_login()
def delete_webdependant():
    row = db.webmemberdependants[request.args[0]]
    if request.vars.confirm:
        db(db.webmemberdependants.id == row.id).delete()
        form=None
    else:
        form = BUTTON('really delete',_onclick='document.location="%s"'%URL(vars=dict(confirm=True),args=[row.id]))

    return dict(form=form)


#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def enroll_webmember():

    ## Add records in POITEM tables
    if(len(request.args) == 0):
        raise HTTP(400, "No Web Member : Error Enrolling Web Member")

    webmemberid = request.args[0]
    webmemberrows = db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).\
           select(db.webmember.ALL, db.company.ALL, db.hmoplan.ALL,\
           left=[db.company.on(db.company.id == db.webmember.company), \
                 db.hmoplan.on(db.hmoplan.id == db.webmember.hmoplan)])

    if(len(webmemberrows)==0):
        response.flash = 'Error in  Web Member Information'
        return dict()


    r = webmemberrows[0]
    companyid   = webmemberrows[0]['company.id']
    companycode = webmemberrows[0]['company.company']
    companyname = webmemberrows[0]['company.name']
    fname       =  webmemberrows[0]['webmember.fname']
    webkey      =  webmemberrows[0]['webmember.webkey']
    dob         =  webmemberrows[0]['webmember.webdob']
    memberid    =  webmemberrows[0]['webmember.webmember']
    providerid  = webmemberrows[0]['webmember.provider']
    regionid    = webmemberrows[0]['webmember.groupregion']
    premstartdt = webmemberrows[0]['webmember.webenrollcompletedate']
    startdate   = webmemberrows[0]['webmember.startdate']
    if(premstartdt == None):
            premstartdt =webmemberrows[0]['webmember.webenrolldate']
        
    day  = timedelta(days = 1)
    
    if(calendar.isleap(premstartdt.year + 1)):
        if(premstartdt > datetime.date(premstartdt.year,02,28)):
            year            = timedelta(days=366)
        else:
            year = timedelta(days=365)
    elif(calendar.isleap(premstartdt.year)):
        if(premstartdt <= datetime.date(premstartdt.year,02,29)):
            year            = timedelta(days=366)
        else:
            year            = timedelta(days=365)
    else:
        year            = timedelta(days=365)

    premenddt = (premstartdt + year) - day
    
    terminationdate = (premstartdt) + year
    renewaldate     = premenddt


    if(db((db.patientmember.patientmember == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).count() == 0):

        yrows = db(db.groupregion.id == regionid).select()
        groupregion = yrows[0].groupregion
        sql = "UPDATE membercount SET membercount = membercount + 1 WHERE company = " + str(companyid) + ";"
        db.executesql(sql)
        db.commit()

        xrows = db(db.membercount.company == companyid).select()
        membercount = int(xrows[0].membercount)
        groupref = memberid
        memberid = groupregion + companycode[:3] + str(companyid).zfill(3) + str(membercount)
        db(db.webmember.id == webmemberid).update(webmember = memberid, groupref=groupref,status = 'Enrolled')
        

        db.patientmember.update_or_insert(((db.patientmember.patientmember == memberid) & (db.patientmember.webkey == webkey) & (db.patientmember.fname == fname) & (db.patientmember.dob == dob) & \
                                           (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember==True)),
                                          patientmember = memberid,
                                          groupref = r.webmember.groupref,
                                          dob = r.webmember.webdob,
                                          fname = r.webmember.fname,
                                          mname = r.webmember.mname,
                                          lname = r.webmember.lname,
                                          address1 = r.webmember.address1,
                                          address2 = r.webmember.address2,
                                          address3 = r.webmember.address3,
                                          city = r.webmember.city,
                                          st = r.webmember.st,
                                          pin = r.webmember.pin,
                                          pan = r.webmember.webpan,
                                          webkey = r.webmember.webkey,
                                          gender = r.webmember.gender,
                                          telephone = r.webmember.telephone,
                                          cell = r.webmember.cell,
                                          email = r.webmember.email,
                                          status = 'Enrolled',
                                          image = r.webmember.image,
                                          paid = r.webmember.paid,
                                          enrollmentdate = premstartdt,
                                          terminationdate = terminationdate,
                                          duedate = premenddt,
                                          provider = r.webmember.provider,
                                          company = r.webmember.company,
                                          memberorder = r.webmember.memberorder,
                                          groupregion = r.webmember.groupregion,
                                          hmoplan = r.webmember.hmoplan,
                                          premstartdt = premstartdt,
                                          premenddt = premenddt,
                                          webmember = webmemberid,
                                          startdate = startdate,
                                          is_active = True
                                          )
    else:
        db(db.webmember.id == webmemberid).update(status = 'Enrolled')
        db.patientmember.update_or_insert(((db.patientmember.patientmember == memberid) & (db.patientmember.webkey == webkey) & (db.patientmember.fname == fname) & (db.patientmember.dob == dob) & \
                                           (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember==True)),
                                          patientmember = memberid,
                                          groupref = r.webmember.groupref,
                                          dob = r.webmember.webdob,
                                          fname = r.webmember.fname,
                                          mname = r.webmember.mname,
                                          lname = r.webmember.lname,
                                          address1 = r.webmember.address1,
                                          address2 = r.webmember.address2,
                                          address3 = r.webmember.address3,
                                          city = r.webmember.city,
                                          st = r.webmember.st,
                                          pin = r.webmember.pin,
                                          pan = r.webmember.webpan,
                                          webkey = r.webmember.webkey,
                                          gender = r.webmember.gender,
                                          telephone = r.webmember.telephone,
                                          cell = r.webmember.cell,
                                          email = r.webmember.email,
                                          status = 'Enrolled',
                                          image = r.webmember.image,
                                          paid = r.webmember.paid,
                                          provider = r.webmember.provider,
                                          company = r.webmember.company,
                                          memberorder = r.webmember.memberorder,
                                          groupregion = r.webmember.groupregion,
                                          hmoplan = r.webmember.hmoplan,
                                          webmember = webmemberid,
                                          startdate = startdate,
                                          is_active = True
                                          )

    #determine premium paid by this patient
    db.commit()
    premium = 0.00
    rows1 = db((db.patientmember.patientmember == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    patientid = rows1[0].id    
    r = db(db.paymenttxlog.webmember == webmemberid).select()
    if(len(r) > 0):
        premium = round(Decimal(common.getvalue(r[0].total)),2)
    db(db.paymenttxlog.webmember == webmemberid).update(patientmember = patientid)
    db((db.patientmember.id == patientid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).update(premium = premium)
    db.commit()
    
    deprows = db(db.webmemberdependants.webmember == webmemberid).select()
    for r in deprows:
        db.patientmemberdependants.update_or_insert(((db.patientmemberdependants.fname == r.fname) & (db.patientmemberdependants.lname == r.lname) & (db.patientmemberdependants.patientmember == patientid) & (db.patientmemberdependants.is_active == True)),
                                                    fname = r.fname,
                                                    mname = r.mname,
                                                    lname = r.lname,
                                                    depdob = r.depdob,
                                                    gender = r.gender,
                                                    relation = r.relation,
                                                    paid = r.paid,
                                                    patientmember = patientid,
                                                    memberorder = r.memberorder,
                                                    is_active = True
                                                    )
    redirect(URL('default', 'emailwelcomekit', vars=dict(page=common.getgridpage(request.vars)),args=[patientid,providerid]))



#IB 05292016
@auth.requires_membership('webadmin')
@auth.requires_login()
def list_webmember():

    username   = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "List of Web Members"
    page       = common.getgridpage(request.vars)

    
    
    fields=(db.webmember.fname,db.webmember.mname, db.webmember.lname,db.webmember.webmember,db.webmember.groupref,\
            db.webmember.email,db.webmember.status,db.webmember.webdob,\
            db.company.id,db.company.company,db.company.name)

    
   
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
    db.webmember.paid.readable = False
    db.webmember.webkey.readable = False
    db.webmember.company.readable = False
    db.webmember.company.writeable = False
    db.webmember.hmoplan.readable = False
    db.webmember.upgraded.readable = False    
    db.webmember.renewed.readable = False    
    db.webmember.mname.readable = False    
    db.webmember.cell.readable = False    
    db.webmember.startdate.readable = False

    db.company.id.readable = False
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
             'webmember.groupref' : 'Employee ID',
             'webmember.fname':'First Name',
             'webmember.mname':'Middle Name',
             'webmember.lname':'Last Name',
             'webmember.webdob':'Date of Birth',
             'webmember.email':'Email',
             'company.company': 'Company',
             'webmember.status':'Status'
            }



    selectable = None
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    links = [lambda row: A('Process',_href=URL("member","update_webmember_1",vars=dict(page=page), args=[row.webmember.id,row.company.id,row.company.company,row.company.name])),  lambda row: A('Delete',_href=URL("member","delete_webmember",args=[row.webmember.id]))]
    query = ((db.webmember.is_active==True))
    left =    [db.company.on(db.company.id==db.webmember.company)]
    orderby = ~(db.webmember.id)
    
    form = SQLFORM.grid(query=query,
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

    
 


    returnurl = URL('member','list_webmember', vars=dict(page=1))
    return dict(username=username, returnurl=returnurl, form=form, formheader=formheader,page=page)




def create_checkout():

    formheader = "Payment Details"
    webkey = None
    fname = None
    dob = None
    status = None
    webmemberid = 0
    companyid = 0
    hmoplanid = 0

    if(len(request.args) == 0):
        raise HTTP(403,"Error in Proceed Checkout - No Member")
        return dict()

    webmemberid = request.args[0]
    rows   = db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).select()
    if(len(rows)==0):
            raise HTTP(403,"Error in Proceed Checkout - Invalid Member 0")

    webkey = rows[0].webkey
    fname  = rows[0].fname
    dob    = rows[0].webdob
    status = rows[0].status
    companyid = int(common.getid(rows[0].company))
    
    rows = db(db.company.id == companyid).select()
    dependantmode = common.getbool(rows[0].dependantmode)
    
    rows     = db((db.companyhmoplanrate.company == db.webmember.company) & (db.webmember.id == webmemberid)).select()
    deprows  = db(db.webmemberdependants.webmember == webmemberid).select()
   
    if(dependantmode == True):
	if(len(rows) > 0):
	    if(len(deprows)>0):
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob, CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
		                    CASE WHEN companypays IS NOT NULL THEN companypays ELSE 0.0 END AS companypays, \
		                    CASE WHEN (premium IS NOT NULL) AND (companypays IS NOT NULL) THEN premium - companypays \
		                    WHEN (premium IS NOT NULL) AND (companypays IS NULL) THEN premium \
		                    WHEN (premium IS NULL) AND (companypays IS NOT NULL) THEN companypays \
		                    ELSE 0.00 END AS youpay FROM webmember \
		                    LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                    LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                    companyhmoplanrate.relation = "Self"  AND companyhmoplanrate.is_Active = "T"  AND \
		                    companyhmoplanrate.hmoplan = webmember.hmoplan \
		                    WHERE \
		                    webmember.id = ' + str(webmemberid) +
		                                 ' UNION ' +
		                    'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob,\
		                    CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium, \
		                    CASE WHEN companypays IS NOT NULL THEN companypays ELSE 0.0 END AS companypays, \
		                    CASE WHEN (premium IS NOT NULL) AND (companypays IS NOT NULL) THEN premium - companypays \
		                    WHEN (premium IS NOT NULL) AND (companypays IS NULL) THEN premium \
		                    WHEN (premium IS NULL) AND (companypays IS NOT NULL) THEN companypays \
		                    ELSE 0.00 END  AS youpay FROM  webmember   \
		                    LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                    LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
		                    LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND companyhmoplanrate.is_Active = "T"  AND  \
		                    webmemberdependants.memberorder = companyhmoplanrate.covered AND \
		                    companyhmoplanrate.hmoplan = webmember.hmoplan \
		                    where webmemberdependants.is_active = "T" AND webmember.id = ' + str(webmemberid))
	    else:
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob, \
		                    CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
		                    CASE WHEN companypays IS NOT NULL THEN companypays ELSE 0.0 END AS companypays,\
		                    CASE WHEN (premium IS NOT NULL) AND (companypays IS NOT NULL) THEN premium - companypays \
		                    WHEN (premium IS NOT NULL) AND (companypays IS NULL) THEN premium \
		                    WHEN (premium IS NULL) AND (companypays IS NOT NULL) THEN companypays \
		                    ELSE 0.00 END AS youpay FROM webmember \
		                    LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                    LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                    companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND companyhmoplanrate.is_Active = "T"  \
		                    WHERE \
		                    webmember.id = ' + str(webmemberid))
	else:
	    if(len(deprows)>0):
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay FROM webmember \
		                    LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                    LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                    companyhmoplanrate.hmoplan = webmember.hmoplan AND\
		                    companyhmoplanrate.relation = "Self" AND companyhmoplanrate.is_Active = "T"  \
		                    WHERE webmember.id = ' + str(webmemberid) +
		                                 ' UNION ' +
		                    'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob, 0 AS premium, \
		                     0 AS companypays, 0 AS youpay FROM  webmember  \
		                     LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                     LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
		                     LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                     webmemberdependants.memberorder = companyhmoplanrate.covered AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
		                     companyhmoplanrate.is_Active = "T" \
		                     WHERE webmember.id = ' + str(webmemberid))
	    else:
    
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay \
		                   FROM webmember \
		                   LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                   LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                   companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
		                   companyhmoplanrate.is_Active = "T" \
		                   WHERE webmember.id = ' + str(webmemberid))
    else:
	if(len(rows) > 0):
	    if(len(deprows)>0):
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob, CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
	                            CASE WHEN companypays IS NOT NULL THEN companypays ELSE 0.0 END AS companypays, \
	                            CASE WHEN (premium IS NOT NULL) AND (companypays IS NOT NULL) THEN premium - companypays \
	                            WHEN (premium IS NOT NULL) AND (companypays IS NULL) THEN premium \
	                            WHEN (premium IS NULL) AND (companypays IS NOT NULL) THEN companypays \
	                            ELSE 0.00 END AS youpay FROM webmember \
	                            LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
	                            LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
	                            companyhmoplanrate.relation = "Self"  AND companyhmoplanrate.is_Active = "T"  AND \
	                            companyhmoplanrate.hmoplan = webmember.hmoplan \
	                            WHERE \
	                            webmember.id = ' + str(webmemberid) +
	                                         ' UNION ' +
	                            'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob,\
	                            CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium, \
	                            CASE WHEN companypays IS NOT NULL THEN companypays ELSE 0.0 END AS companypays, \
	                            CASE WHEN (premium IS NOT NULL) AND (companypays IS NOT NULL) THEN premium - companypays \
	                            WHEN (premium IS NOT NULL) AND (companypays IS NULL) THEN premium \
	                            WHEN (premium IS NULL) AND (companypays IS NOT NULL) THEN companypays \
	                            ELSE 0.00 END  AS youpay FROM  webmember   \
	                            LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
	                            LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
	                            LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND companyhmoplanrate.is_Active = "T"  AND  \
	                            webmemberdependants.relation = companyhmoplanrate.relation AND \
	                            companyhmoplanrate.hmoplan = webmember.hmoplan \
	                            where webmemberdependants.is_active = "T" AND webmember.id = ' + str(webmemberid))
	    else:
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob, \
	                            CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
	                            CASE WHEN companypays IS NOT NULL THEN companypays ELSE 0.0 END AS companypays,\
	                            CASE WHEN (premium IS NOT NULL) AND (companypays IS NOT NULL) THEN premium - companypays \
	                            WHEN (premium IS NOT NULL) AND (companypays IS NULL) THEN premium \
	                            WHEN (premium IS NULL) AND (companypays IS NOT NULL) THEN companypays \
	                            ELSE 0.00 END AS youpay FROM webmember \
	                            LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
	                            LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
	                            companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND companyhmoplanrate.is_Active = "T"  \
	                            WHERE \
	                            webmember.id = ' + str(webmemberid))
	else:
	    if(len(deprows)>0):
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay FROM webmember \
	                            LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
	                            LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
	                            companyhmoplanrate.hmoplan = webmember.hmoplan AND\
	                            companyhmoplanrate.covered = "Self" AND companyhmoplanrate.is_Active = "T"  \
	                            WHERE webmember.id = ' + str(webmemberid) +
	                                         ' UNION ' +
	                            'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob, 0 AS premium, \
	                             0 AS companypays, 0 AS youpay FROM  webmember  \
	                             LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
	                             LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
	                             LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
	                             webmemberdependants.relation = companyhmoplanrate.relation AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
	                             companyhmoplanrate.is_Active = "T" \
	                             WHERE webmember.id = ' + str(webmemberid))
	    else:
    
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay \
	                           FROM webmember \
	                           LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
	                           LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
	                           companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
	                           companyhmoplanrate.is_Active = "T" \
	                           WHERE webmember.id = ' + str(webmemberid))

    # Calculate amount to pay

    totpremium = 0
    totcompanypays = 0
    totyoupay = 0
    servicetaxes = 0
    swipecharges = 0
    total = 0
    servicetax = 0
    swipecharge = 0

    if(len(ds)>0):
        for i in xrange(0,len(ds)):
            totpremium = totpremium + round(Decimal(ds[i][4]),2)
            totcompanypays = totcompanypays + round(Decimal(ds[i][5]),2)
            totyoupay = totpremium - totcompanypays

        if(totyoupay <= 0):
            db(db.webmember.id == webmemberid).update(status = 'Completed')

        if(totyoupay > 0):
            r = db(db.urlproperties).select()
            if(len(r)>0):
                servicetax = round(Decimal(r[0].servicetax),2)
                swipecharge = round(Decimal(r[0].swipecharge),2)
            servicetaxes = round(totyoupay * servicetax / 100,2)
            swipecharges = round(totyoupay * swipecharge/ 100,2)
            total = totyoupay + servicetaxes + swipecharges

   
    txdatetime = datetime.datetime.now()
    txno = str(webmemberid) + "_" + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S")
    db.paymenttxlog.insert(txno=txno,txdatetime=txdatetime,webmember=webmemberid,txamount=totyoupay,total=total,servicetax=servicetaxes,swipecharge=swipecharges )

    webkey = webkey.replace("#","1")
    return dict(ds=ds, formheader=formheader, webmemberid=webmemberid,webkey=webkey,fname=fname,dob=dob,txno=txno,status=status,servicetax=servicetaxes,swipecharge=swipecharges,total=total,logmode=session.logmode)

def member_payment():

    #secret_key='d67fa952ec2f66c394d3192f17e01550'
    #account_id='16428'
    #address='A-16 Indraprasth Apartments'
    #amount='12.34'
    #channel='10'
    #city='Bengalaru'
    #country='IND'
    #currency='INR'
    #description='Test Payment'
    #email='test@gmail.com'
    #mode='LIVE'
    #name='imtiazbengali@hotmail.com'
    #phone='9819877579'
    #postal_code='560004'
    #reference_no='IMB001'
    #return_url='http://turningcloud.com/response.jsp'
    #ship_address='test'
    #ship_city='Mumbai'
    #ship_country='IND'
    #ship_name='test'
    #ship_phone='9840123456'
    #ship_postal_code='410251'
    #ship_state='Mumbai'
    #state='test'


    #secret_key='d67fa952ec2f66c394d3192f17e01550'
    #account_id='16428'
    #address='A-16 Indraprasth Apartments'
    #amount='120.34'
    #channel='10'
    #city='Bengalaru'
    #country='IND'
    #currency='INR'
    #description='Test Payment'
    #email='imtiazbengali@hotmail.com'
    #mode='LIVE'
    #name='Imtiyaz Bengali'
    #phone='9819877579'
    #postal_code='560004'
    #reference_no='IMB001'
    #return_url='http://turningcloud.com/response.jsp'
    #ship_address='A-16 Indraprasth Apartments'
    #ship_city='Bengalaru'
    #ship_country='IND'
    #ship_name='Imtiyaz Bengali'
    #ship_phone='9819877579'
    #ship_postal_code='560004'
    #ship_state='Karnataka'
    #state='Karnataka'

    webmemberid = 0
    webkey = None
    fname = None
    dob = None
    rows = None
    txrows = None
    txno = None
    txamount = 0.00

    if(len(request.args)>0):
        webmemberid = int(request.args[0])
        webkey = request.args[1]
        fname = request.args[2]
        txno = request.args[4]
        if(webmemberid > 0):
            rows = db(db.webmember.id == webmemberid).select();
            dob = rows[0].webdob
            txrows = db((db.paymenttxlog.txno == txno) & (db.paymenttxlog.webmember == webmemberid)).select()
            if(len(txrows)>0):
                txamount = txrows[0].total


    if(len(rows) > 0):

        urls = db(db.urlproperties.id > 0).select()


        secret_key='d67fa952ec2f66c394d3192f17e01550'
        account_id='16428'
        address=rows[0].address1
        if((address == None)|(address=='')):
            address = " "
        amount=str(txamount)
        channel='10'
        city=rows[0].city
        if(city == None):
            city = " "
        country='IND'
        currency='INR'
        description='Payment'
        email=rows[0].email
        if((email == None)|(email=='')):
            email = " "
        mode='LIVE'
        name=rows[0].fname + ' ' + rows[0].lname
        phone=rows[0].cell
        if((phone == None)|(phone=='')):
            phone = " "
        postal_code=rows[0].pin
        if((postal_code == None)|(postal_code=='')):
            postal_code = " "
        reference_no = txno
        return_url=urls[0].callbackurl
        if((return_url == None)|(return_url=='')):
            return_url = " "
        ship_address=rows[0].address1
        if((ship_address == None)|(ship_address=='')):
            ship_address = " "
        ship_city=rows[0].city
        if((ship_city == None)|(ship_city=='')):
            ship_city = " "
        ship_country='IND'
        ship_name=rows[0].fname + ' ' + rows[0].lname
        ship_phone=rows[0].cell
        if((ship_phone == None)|(ship_phone=='')):
            ship_phone = " "
        ship_postal_code=rows[0].pin
        if((ship_postal_code == None)|(ship_postal_code=='')):
            ship_postal_code = " "
        ship_state=rows[0].st
        if((ship_state == None)|(ship_state=='')):
            ship_state = " "
        state=rows[0].st
        if((state == None)|(state=='')):
            state = " "


        hashkey = account.generateHash(secret_key,account_id,address,amount,channel,city,country,currency,description,email,mode, \
                         name,phone,postal_code,reference_no,return_url,ship_address,ship_city,ship_country,ship_name,ship_phone,ship_postal_code,ship_state,state)

        return dict(\
            secret_key=secret_key,\
            account_id=account_id,\
            address=address,\
            amount=amount,\
            channel=channel,\
            city=city,\
            country=country,\
            currency=currency,\
            description=description,\
            email=email,\
            mode=mode,\
            name=name,\
            phone=phone,\
            postal_code=postal_code,\
            reference_no=reference_no,\
            return_url=return_url,\
            ship_address=ship_address,\
            ship_city=ship_city,\
            ship_country=ship_country,\
            ship_name=ship_name,\
            ship_phone=ship_phone,\
            ship_postal_code=ship_postal_code,\
            ship_state=ship_state,\
            state=state,\
            secure_hash=hashkey\
            )
    else:
        return dict()

def add_webmember_provider():
    ## Add records in POITEM tables
    providerid = 0
    webmemberid = 0
    companyname = ''
    companycode = ''
    companyid = 0
    if(len(request.args)>0):
        providerid = request.args[0]
        webmemberid = request.args[1]
        companyid = request.args[2]
        companycode = request.args[3]
        companyname = request.args[4]


    redirectURL = URL('member','update_webmember_1',args=[webmemberid, companyid, companycode, companyname])

    db(db.webmember.id == webmemberid).update(provider=providerid)

    redirect(redirectURL)

    return dict()


def medi_member_card():

    #this method is called with url https://<server>/my_dentalplan/member/member_card 
    #vars = page, returnurl, pattype, memberid, patientid
    
    page      = common.getpage(request.vars.page)
    returnurl = request.vars.returnurl if(request.vars.returnurl != "") else URL('default','index')
    
    pattype = request.vars.pattype if((request.vars.pattype != None) & (request.vars.pattype != "None") & (request.vars.pattype != "")) else "P"
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))

    pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select()

    patientname = common.getstring(pats[0].fullname)
    
    
    dob = pats[0].dob.strftime("%d/%m/%Y") if(pats[0].dob !=None) else "00/00/0000"
    relation = common.getstring(pats[0].relation)
    patientimage = common.getstring(pats[0].image)
    groupref = pats[0].groupref
    
    mems = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == memberid)).select()    
    membername = common.getstring(mems[0].fullname)
    patientmember = common.getstring(mems[0].patientmember)
    validfrom = mems[0].premstartdt.strftime("%d/%m/%Y") if(mems[0].premstartdt !=None) else "00/00/0000"
    validtill = mems[0].premenddt.strftime("%d/%m/%Y") if(mems[0].premenddt !=None) else "00/00/0000"
    groupref = mems[0].groupref
    
    comp = db(db.company.id == int(common.getid(mems[0].company))).select()
    companyname = common.getstring(comp[0].name) if(len(comp)>0) else ""

    plans = db(db.hmoplan.id == int(common.getstring(mems[0].hmoplan))).select()
    planname = common.getstring(plans[0].name) if(len(plans)>0) else ""
    
    providername = ""
    practicename = ""
    practiceaddress = ""
    provs = db(db.provider.id == int(common.getstring(mems[0].providerid))).select()
    if(len(provs)>0):
	providername = common.getstring(provs[0].pa_providername)
	practicename = common.getstring(provs[0].pa_practicename)
	practiceaddress = common.getstring(provs[0].pa_practiceaddress)
	practicephone = common.getstring(provs[0].telephone) if(common.getstring(provs[0].telephone) != "") else common.getstring(provs[0].cell)
	practiceemail = common.getstring(provs[0].email)
	
    props = db(db.urlproperties.id>0).select()
    httpserver = props[0].mydp_ipaddress  # this has to be populated    
   
    return dict(page=page,returnurl=returnurl,patientname=patientname, patientmember=patientmember,groupref=groupref,\
                relation=relation,dob=dob,\
                membername=membername,companyname=companyname,planname=planname,validfrom=validfrom,validtill=validtill,\
                patientimage=patientimage,providername=providername,\
                practicename=practicename,practiceaddress=practiceaddress,\
                practicephone=practicephone,practiceemail=practiceemail,httpserver=httpserver)


def member_card():

    #this method is called with url https://<server>/my_dentalplan/member/member_card 
    #vars = page, returnurl, pattype, memberid, patientid
    
    page      = common.getpage(request.vars.page)
    returnurl = request.vars.returnurl if(request.vars.returnurl != "") else URL('default','index')
    
    pattype = request.vars.pattype if((request.vars.pattype != None) & (request.vars.pattype != "None") & (request.vars.pattype != "")) else "P"
    memberid = int(common.getid(request.vars.memberid))
    patientid = int(common.getid(request.vars.patientid))

    pats = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == patientid)).select()

    patientname = common.getstring(pats[0].fullname)
    
    dob="00/00/0000"
    if(pats[0].dob != None):
	dob = pats[0].dob.strftime("%d/%m/%Y")
    relation = common.getstring(pats[0].relation)
    patientimage = common.getstring(pats[0].image)
    
    mems = db((db.vw_memberpatientlist.primarypatientid == memberid) & (db.vw_memberpatientlist.patientid == memberid)).select()
    membername = common.getstring(mems[0].fullname)
    patientmember = common.getstring(mems[0].patientmember)
    validfrom = mems[0].premstartdt.strftime("%d/%m/%Y") if(mems[0].premstartdt !=None) else "00/00/0000"
    validtill = mems[0].premenddt.strftime("%d/%m/%Y") if(mems[0].premenddt !=None) else "00/00/0000"
    
    
    comp = db(db.company.id == int(common.getid(mems[0].company))).select()
    companyname = common.getstring(comp[0].name) if(len(comp)>0) else ""

    plans = db(db.hmoplan.id == int(common.getstring(mems[0].hmoplan))).select()
    planname = common.getstring(plans[0].name) if(len(plans)>0) else ""
    
    providername = ""
    practicename = ""
    practiceaddress = ""
    provs = db(db.provider.id == int(common.getstring(mems[0].providerid))).select()
    if(len(provs)>0):
	providername = common.getstring(provs[0].pa_providername)
	practicename = common.getstring(provs[0].pa_practicename)
	practiceaddress = common.getstring(provs[0].pa_practiceaddress)
	practicephone = common.getstring(provs[0].telephone) if(common.getstring(provs[0].telephone) != "") else common.getstring(provs[0].cell)
	practiceemail = common.getstring(provs[0].email)
	
    props = db(db.urlproperties.id>0).select()
    httpserver = props[0].mydp_ipaddress  # this has to be populated 
    return dict(page=page,returnurl=returnurl,patientname=patientname, patientmember=patientmember,relation=relation,dob=dob,\
                membername=membername,companyname=companyname,planname=planname,validfrom=validfrom,validtill=validtill,\
                patientimage=patientimage,providername=providername,\
                practicename=practicename,practiceaddress=practiceaddress,\
                practicephone=practicephone,practiceemail=practiceemail,httpserver=httpserver)

def member_card_current():

    
    memberid  = request.args[0]
    returnurl = request.vars.returnurl

    rows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select(db.patientmember.id,db.patientmember.patientmember,db.patientmember.fname,db.patientmember.mname,db.patientmember.lname, db.hmoplan.hmoplancode, db.hmoplan.name, db.patientmember.enrollmentdate,\
                                                      db.patientmember.pan, db.patientmember.address1, db.patientmember.address2, db.patientmember.address3,db.patientmember.duedate,db.patientmember.premstartdt, db.patientmember.premenddt,\
                                                      db.patientmember.city, db.patientmember.st, db.patientmember.pin,db.patientmember.dob,db.patientmember.email,db.patientmember.cell,db.patientmember.gender,db.patientmember.upgraded,\
                                                      db.patientmember.image,db.company.company, db.company.name,\
                                                      db.provider.provider, db.provider.providername, db.provider.address1, db.provider.address2, db.provider.address3, db.provider.st, db.provider.city,db.provider.pin, db.provider.cell,db.provider.email,\
                                                      left=[db.company.on(db.company.id == db.patientmember.company), \
                                                            db.hmoplan.on(db.hmoplan.id == db.patientmember.hmoplan),\
                                                            db.provider.on(db.provider.id == db.patientmember.provider)\
                                                            ])
    
    if(rows[0].company.company == "MEDI"):
	redirect(URL('member','medi_member_card', vars=dict(memberid=memberid, returnurl=returnurl)))
    
    today = datetime.date.today()
    year  = today.year
    dob   = rows[0].patientmember.dob
    year0 = dob.year
    age = year - year0

    
    fields=(db.patientmemberdependants.fname,db.patientmemberdependants.lname,db.patientmemberdependants.gender,db.patientmemberdependants.depdob,db.patientmemberdependants.relation,)

    headers={'patientmemberdependants.fname':'First Name',
             'patientmemberdependants.lname': 'Last Name',
             'patientmemberdependants.depdob': 'DOB',
             'patientmemberdependants.gender': 'Gender',
             'patientmemberdependants.relation':'Relation'
             }

    exportlist =  dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)


    query = (db.patientmemberdependants.patientmember == memberid) & (db.patientmemberdependants.is_active==True)


    ## called from menu
    formB = SQLFORM.grid(query=query,
                             headers=headers,
                             fields=fields,
                             exportclasses=exportlist,
                             searchable=False,
                             create=False,
                             deletable=False,
                             editable=False,
                             details=False,
                             user_signature=False
                            )

    return dict(rows=rows, formB=formB, age=age,page=common.getgridpage(request.vars), returnurl=returnurl)


def member_card_0():
    
    
    patientmemberid = int(common.getid(request.args[0]))
    returnurl = URL('default','main')
    redirect(URL('member','member_card',vars=dict(page=1,returnurl=returnurl),args=[patientmemberid]))

    #rows = db()(db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select(db.patientmember.id,db.patientmember.patientmember,db.patientmember.fname,db.patientmember.mname,db.patientmember.lname, db.hmoplan.hmoplancode, db.hmoplan.name, db.patientmember.enrollmentdate,\
                                                      #db.patientmember.pan, db.patientmember.address1, db.patientmember.address2, db.patientmember.address3,\
                                                      #db.patientmember.city, db.patientmember.st, db.patientmember.pin,db.patientmember.dob,db.patientmember.email,db.patientmember.cell,db.patientmember.gender,\
                                                      #db.patientmember.image,db.company.company, db.company.name,\
                                                      #left=[db.company.on(db.company.id == db.patientmember.company), \
                                                            #db.hmoplan.on(db.hmoplan.id == db.patientmember.hmoplan)
                                                            #])

    #deprows = db(db.patientmemberdependants.patientmember == memberid).select(db.patientmemberdependants.fname, db.patientmemberdependants.lname, db.patientmemberdependants.depdob, db.patientmemberdependants.relation)
    return dict(rows=rows,deprows=deprows)

def member_card_links():
    
    memberid = int(common.getid(request.vars.memberid))
    pats = db(db.vw_memberpatientlist.primarypatientid == memberid).select()
    
    returnurl = URL('member','list_member')
    page = common.getpage(request.vars.page)
       
    links = []
    names = []
    
    medibuddy = False
    
    if(len(pats)>0):
	comp = db(db.company.id == int(pats[0].company)).select()
	if(len(comp)>0):
	    if(comp[0].company == "MEDI"):
		medibuddy = True
    
    
    if(len(pats)==1):
	link = URL('member', 'member_card', vars=dict(page=page,returnurl=returnurl,memberid=pats[0].primarypatientid,patientid=pats[0].patientid,pattype=pats[0].patienttype)) if(medibuddy == False) else URL('member', 'medi_member_card', vars=dict(page=page,returnurl=returnurl,memberid=pats[0].primarypatientid,patientid=pats[0].patientid,pattype=pats[0].patienttype))
	redirect(link)
    else:
	for i in xrange(0, len(pats)):
	    link = URL('member', 'member_card', vars=dict(page=page,returnurl=returnurl,memberid=pats[i].primarypatientid,patientid=pats[i].patientid,pattype=pats[i].patienttype)) if(medibuddy == False) else URL('member', 'medi_member_card', vars=dict(page=page,returnurl=returnurl,memberid=pats[i].primarypatientid,patientid=pats[i].patientid,pattype=pats[i].patienttype))	    
	    #if(medibuddy == False):
		#link = URL('member', 'member_card', vars=dict(page=page,returnurl=returnurl,memberid=pats[i].primarypatientid,patientid=pats[i].patientid,pattype=pats[i].patienttype))
	    #else:
		#link = URL('member', 'medi_member_card', vars=dict(page=page,returnurl=returnurl,memberid=pats[i].primarypatientid,patientid=pats[i].patientid,pattype=pats[i].patienttype))	    
		
	    links.insert(i,link)
	    names.insert(i, common.getstring(pats[i].fullname))
    
    

    return dict(links=links,page=page,names=names)


def member_card_welcomekit():

    #just for resolving welcome kit link in the email
    #username = "MDP"
    #return dict(username=username)
   
   
    encodedmemberid = request.args[0]


    decodestr  = encodedmemberid.decode('base64','strict')
    splits = decodestr.split('_')
    
    memberid = splits[1]
    patientid = splits[2]
    pattype = splits[3]

    medibuddy = False
    mems = db(db.patientmember.id == memberid).select()
    if(len(mems)>0):
	comp = db(db.company.id == int(mems[0].company)).select()
	if(len(comp)>0):
	    if(comp[0].company == "MEDI"):
		medibuddy = True
	    
    returnurl = URL('member', 'list_member')
    
    if(medibuddy == False):
	redirect(URL('member','member_card',vars=dict(page=1,returnurl=returnurl,memberid=memberid,patientid=patientid,pattype=pattype)))
    else:
	redirect(URL('member','medi_member_card',vars=dict(page=1,returnurl=returnurl,memberid=memberid,patientid=patientid,pattype=pattype)))
	

    return dict()


def xmember_card_welcomekit():


    encodedmemberid = request.args[0]


    decodestr  = encodedmemberid.decode('base64','strict')
    splits = decodestr.split('_')
    patientmember = splits[1]
    
    r = db((db.patientmember.patientmember == patientmember) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    patientmemberid = int(common.getid(r[0].id))
    
    
    returnurl = "noreturn"
    redirect(URL('member','member_card',vars=dict(page=1,returnurl=returnurl),args=[patientmemberid]))
    
    
    return dict(rows=rows, formB=formB, age=age)

@auth.requires_membership('webadmin')
@auth.requires_login()
def new_webmember():
    companyid   = 0
    planid = 0
    company = ''
    name = ''

    formheader = "New Member"
    username = auth.user.first_name + ' ' + auth.user.last_name
     
    rows = db(db.company.company == 'B2C_NG').select()
    if(len(rows)>0):
        companyid = rows[0]['company.id']
        company   = rows[0]['company']
        name      = rows[0]['name']
      
    planid = 1
    regionid = 1

    formA = SQLFORM.factory(
        Field('webmember', 'string',label='Member ID', default=''),
        Field('company', default=companyid, requires=IS_IN_DB(db(db.company.is_active==True), 'company.id', '%(name)s (%(company)s)')),
        Field('hmoplan', default=planid, requires=IS_IN_DB(db(db.hmoplan.is_active==True), 'hmoplan.id', '%(name)s (%(hmoplancode)s) (%(groupregion)s)')),
        Field('groupregion', default=1, requires=IS_IN_DB(db(db.groupregion.is_active == True), 'groupregion.id', '%(region)s (%(groupregion)s)')),
        Field('fname', 'string',label='First Name', default='', requires=IS_NOT_EMPTY()),
        Field('mname', 'string',label='Middle Name', default=''),
        Field('lname', 'string',label='Last Name', default='', requires=IS_NOT_EMPTY()),
        Field('gender', 'string',label='Gender', default='Male', requires = IS_IN_SET(GENDER)),
        Field('webdob', 'date',label='DOB', default=request.now,  requires=IS_DATE(format=('%d/%m/%Y')),length=20),
        Field('address1', 'string',label='Address1', default='', requires=IS_NOT_EMPTY()),
        Field('address2', 'string',label='Address2', default='', requires=IS_NOT_EMPTY()),
        Field('address3', 'string',label='Address3', default=''),
        Field('city', 'string',label='City', default='--Select City--', requires = IS_IN_SET(CITIES)),
        Field('st', 'string',label='State', default='--Select State--',requires = IS_IN_SET(STATES)),
        Field('pin', 'string',label='pin', default='',requires=IS_NOT_EMPTY()),
        Field('cell', 'string',label='Cell Phone', default=''),
        Field('telephone', 'string',label='Telephone', default=''),
        Field('email', 'string',label='Email', default='emailid@mydentalplan.in',requires=IS_NOT_EMPTY()),
        Field('webpan', 'string', default='',label='Pan Card',length=50),
        Field('pin1','string',default='',label='Pin Choice 1'),
        Field('pin2','string',default='',label='Pin Choice 2'),
        Field('pin3','string',default='',label='Pin Choice 3'))

    if formA.process().accepted:
        memberid = db.webmember.insert(**db.webmember._filter_fields(formA.vars))
        db(db.webmember.id == memberid).update(webmember = memberid,status = "Attempting", webenrollcompletedate=db.webmember.webenrolldate)
        redirect(URL('member','update_webmember_1', args=[memberid,companyid,company,name]))

    elif formA.errors:
        response.flash = 'form has errors'

    regionid = 0
    
    regions = db(db.groupregion.is_active == True).select()  #IB 07042016
    plans   = db((db.companyhmoplanrate.groupregion==regionid) & (db.companyhmoplanrate.company==companyid)).\
                select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
                  left=db.hmoplan.on((db.companyhmoplanrate.hmoplan == db.hmoplan.id)&(db.hmoplan.is_active==True)))    
    page = 1
    returnurl = URL('default', 'main')
    
    return dict(formA=formA,username=username, returnurl=returnurl,formheader=formheader,regions=regions, plans=plans,page=page)


def new_webmember_premiumpayment():

    formheader = "Payment Details"
    username = auth.user.first_name + ' ' + auth.user.last_name
    webkey = None
    fname = None
    dob = None
    status = None
    webmemberid = 0
    companyid = 0
    hmoplanid = 0

    if(len(request.args) == 0):
        raise HTTP(403,"Error in Premium Payment - No Member")

    webmemberid = request.args[0]
    rows   = db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).select()
    if(len(rows)==0):
            raise HTTP(403,"Error in Premium Payment - Invalid Member")


    fname  = rows[0].fname
    dob    = rows[0].webdob
    status = rows[0].status
    companyid = int(common.getid(rows[0].company))
    rows = db(db.company.id == companyid).select()
    dependantmode = common.getbool(rows[0].dependantmode)
    
    rows     = db((db.companyhmoplanrate.company == db.webmember.company) & (db.webmember.id == webmemberid)).select()
    deprows  = db(db.webmemberdependants.webmember == webmemberid).select()


    if(dependantmode == True):
	if(len(rows) > 0):
	    if(len(deprows)>0):
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob, CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
		                    CASE WHEN companypays IS NOT NULL THEN companypays ELSE 0.0 END AS companypays, \
		                    CASE WHEN (premium IS NOT NULL) AND (companypays IS NOT NULL) THEN premium - companypays \
		                    WHEN (premium IS NOT NULL) AND (companypays IS NULL) THEN premium \
		                    WHEN (premium IS NULL) AND (companypays IS NOT NULL) THEN companypays \
		                    ELSE 0.00 END AS youpay FROM webmember \
		                    LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                    LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                    companyhmoplanrate.relation = "Self"  AND companyhmoplanrate.is_Active = "T"  AND \
		                    companyhmoplanrate.hmoplan = webmember.hmoplan \
		                    WHERE \
		                    webmember.id = ' + str(webmemberid) +
		                                 ' UNION ' +
		                    'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob,\
		                    CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium, \
		                    CASE WHEN companypays IS NOT NULL THEN companypays ELSE 0.0 END AS companypays, \
		                    CASE WHEN (premium IS NOT NULL) AND (companypays IS NOT NULL) THEN premium - companypays \
		                    WHEN (premium IS NOT NULL) AND (companypays IS NULL) THEN premium \
		                    WHEN (premium IS NULL) AND (companypays IS NOT NULL) THEN companypays \
		                    ELSE 0.00 END  AS youpay FROM  webmember   \
		                    LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                    LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
		                    LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND companyhmoplanrate.is_Active = "T"  AND  \
		                    webmemberdependants.memberorder = companyhmoplanrate.covered AND \
		                    companyhmoplanrate.hmoplan = webmember.hmoplan \
		                    where webmemberdependants.is_active = "T" AND webmember.id = ' + str(webmemberid))
	    else:
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob, \
		                    CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
		                    CASE WHEN companypays IS NOT NULL THEN companypays ELSE 0.0 END AS companypays,\
		                    CASE WHEN (premium IS NOT NULL) AND (companypays IS NOT NULL) THEN premium - companypays \
		                    WHEN (premium IS NOT NULL) AND (companypays IS NULL) THEN premium \
		                    WHEN (premium IS NULL) AND (companypays IS NOT NULL) THEN companypays \
		                    ELSE 0.00 END AS youpay FROM webmember \
		                    LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                    LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                    companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND companyhmoplanrate.is_Active = "T"  \
		                    WHERE \
		                    webmember.id = ' + str(webmemberid))
	else:
	    if(len(deprows)>0):
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay FROM webmember \
		                    LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                    LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                    companyhmoplanrate.hmoplan = webmember.hmoplan AND\
		                    companyhmoplanrate.relation = "Self" AND companyhmoplanrate.is_Active = "T"  \
		                    WHERE webmember.id = ' + str(webmemberid) +
		                                 ' UNION ' +
		                    'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob, 0 AS premium, \
		                     0 AS companypays, 0 AS youpay FROM  webmember  \
		                     LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                     LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
		                     LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                     webmemberdependants.memberorder = companyhmoplanrate.covered AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
		                     companyhmoplanrate.is_Active = "T" \
		                     WHERE webmember.id = ' + str(webmemberid))
	    else:
    
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay \
		                   FROM webmember \
		                   LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                   LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                   companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
		                   companyhmoplanrate.is_Active = "T" \
		                   WHERE webmember.id = ' + str(webmemberid))
	
    else:
	if(len(rows) > 0):
	    if(len(deprows)>0):
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob, \
		                    CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
		                    CASE WHEN companyhmoplanrate.companypays IS NOT NULL THEN companyhmoplanrate.companypays ELSE 0.0 END AS companypays, \
		                    CASE WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN premium - companypays \
		                    WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NULL) THEN premium \
		                    WHEN (companyhmoplanrate.premium IS NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companypays \
		                    ELSE 0.00 END AS youpay FROM webmember \
		                    LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                    LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND  webmember.groupregion = companyhmoplanrate.groupregion AND\
		                    companyhmoplanrate.relation = "Self"  AND companyhmoplanrate.is_Active = "T"  AND \
		                    companyhmoplanrate.hmoplan = webmember.hmoplan \
		                    WHERE \
		                    webmember.paid = "F" AND webmember.id = ' + str(webmemberid) +
		                                 ' UNION ' +
		                    'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob,\
		                    CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium, \
		                    CASE WHEN companyhmoplanrate.companypays IS NOT NULL THEN companyhmoplanrate.companypays ELSE 0.0 END AS companypays, \
		                    CASE WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.premium - companyhmoplanrate.companypays \
		                    WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NULL) THEN companyhmoplanrate.premium \
		                    WHEN (companyhmoplanrate.premium IS NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.companypays \
		                    ELSE 0.00 END  AS youpay FROM  webmember   \
		                    LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                    LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
		                    LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND webmember.groupregion = companyhmoplanrate.groupregion AND companyhmoplanrate.is_Active = "T"  AND  \
		                    webmemberdependants.relation = companyhmoplanrate.relation AND \
		                    companyhmoplanrate.hmoplan = webmember.hmoplan \
		                    where webmemberdependants.is_active = "T"  AND webmemberdependants.paid = "F" AND webmember.id = ' + str(webmemberid))
	    else:
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob, \
		                    CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
		                    CASE WHEN companyhmoplanrate.companypays IS NOT NULL THEN companyhmoplanrate.companypays ELSE 0.0 END AS companypays,\
		                    CASE WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.premium - companyhmoplanrate.companypays \
		                    WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NULL) THEN companyhmoplanrate.premium \
		                    WHEN (companyhmoplanrate.premium IS NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.companypays \
		                    ELSE 0.00 END AS youpay FROM webmember \
		                    LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                    LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                    companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND webmember.groupregion = companyhmoplanrate.groupregion AND  companyhmoplanrate.is_Active = "T"  \
		                    WHERE \
		                    webmember.paid = "F" AND webmember.id = ' + str(webmemberid))
	else:
	    if(len(deprows)>0):
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay FROM webmember \
		                    LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                    LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                    companyhmoplanrate.hmoplan = webmember.hmoplan AND\
		                    companyhmoplanrate.covered = "Self" AND companyhmoplanrate.is_Active = "T"  \
		                    WHERE webmember.paid = "F" AND webmember.id = ' + str(webmemberid) +
		                                 ' UNION ' +
		                    'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob, 0 AS premium, \
		                     0 AS companypays, 0 AS youpay FROM  webmember  \
		                     LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                     LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
		                     LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                     webmemberdependants.relation = companyhmoplanrate.relation AND companyhmoplanrate.hmoplan = webmember.hmoplan AND webmember.groupregion = companyhmoplanrate.groupregion AND \
		                     companyhmoplanrate.is_Active = "T" \
		                     WHERE webmember.paid = "F" AND webmember.id = ' + str(webmemberid))
	    else:
    
		ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay \
		                   FROM webmember \
		                   LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
		                   LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
		                   companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
		                   companyhmoplanrate.is_Active = "T" \
		                   WHERE webmember.paid = "F" AND webmember.id = ' + str(webmemberid))


    # Calculate amount to pay

    totpremium = 0
    totcompanypays = 0
    totyoupay = 0
    servicetaxes = 0
    swipecharges = 0
    total = 0
    servicetax = 0
    swipecharge = 0

    if(len(ds)>0):
        for i in xrange(0,len(ds)):
            totpremium = totpremium + round(Decimal(ds[i][4]),2)
            totcompanypays = totcompanypays + round(Decimal(ds[i][5]),2)
            totyoupay = totpremium - totcompanypays

        #if(totyoupay <= 0):
            #db(db.webmember.id == webmemberid).update(status = 'Completed')

        if(totyoupay > 0):
            r = db(db.urlproperties).select()
            if(len(r)>0):
                servicetax = round(Decimal(r[0].servicetax),2)
                swipecharge = round(Decimal(r[0].swipecharge),2)
            servicetaxes = round(totyoupay * servicetax / 100,2)
            swipecharges = round(totyoupay * swipecharge/ 100,2)
            total = totyoupay + servicetaxes + swipecharges


    #txdatetime = datetime.datetime.now()
    #txno = str(webmemberid) + "_" + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S")
    #db.paymenttxlog.insert(txno=txno,txdatetime=txdatetime,webmember=webmemberid,txamount=totyoupay,total=total,servicetax=servicetaxes,swipecharge=swipecharges )

    txno = "None"

    returnurl = URL('default','main')
    return dict(username=username,returnurl=returnurl,ds=ds, formheader=formheader, webmemberid=webmemberid,webkey=webkey,fname=fname,dob=dob,txno=txno,status=status,servicetax=servicetaxes,swipecharge=swipecharges,total=total)


def new_webmember_processpayment():

    if(len(request.args) == 0):
        raise HTTP(403,"Error in Process Payment - No Member")

    webmemberid = request.args[0]

    txdatetime = datetime.datetime.now()
    txno = str(webmemberid) + "_" + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S")

    totyoupay = request.vars.totyoupay
    total  = request.vars.total
    servicetax = request.vars.servicetax
    swipecharge = request.vars.swipecharge
    paymentdetails = request.vars.paymentdetails
    responsecode = "B2C_Payment"
    db.paymenttxlog.insert(txno=txno,txdatetime=txdatetime,webmember=webmemberid,txamount=totyoupay,total=total,servicetax=servicetax,swipecharge=swipecharge,responsecode=responsecode,responsemssg=paymentdetails )
    
    db(db.webmember.id == webmemberid).update(webenrollcompletedate = datetime.date.today(),paid=True,status='Completed')
    db(db.webmemberdependants.webmember == webmemberid).update(paid=True)


    redirect(URL('member','update_webmember_1', args=[webmemberid]))

    return dict()


