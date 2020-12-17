# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']

import datetime
from datetime import timedelta



#import sys
#sys.path.append('modules')

from applications.my_pms2.modules import account
from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import mail
from applications.my_pms2.modules  import cycle
from applications.my_pms2.modules  import logger

from applications.my_pms2.modules  import mdpabhicl

#from gluon.contrib import account
#from gluon.contrib import mail
#from gluon.contrib import common
#from gluon.contrib import cycle
#from gluon.contrib import logger



import os
import urllib2
import calendar
import time

months = ['January','February','March','April','May','June','July','August','September','October','November','December']

def migrate_dependants(webmemberid, companyid, planid, regionid):
    
    logger.logger.info("===================Enter migrate_dependants=======================================")
    
    webdeps = db(db.webmemberdependants.webmember == webmemberid).select()
    for webdep in webdeps:
        logger.logger.info("========Migrate : DepWebmember(%d) Company(%d) Plan(%d) Region(%d) Relation(%s)", webdep.id, companyid, planid, regionid,webdep.relation)    
        
        depcpr = db((db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.hmoplan == planid) & \
                    (db.companyhmoplanrate.relation == webdep.relation) ).select()
        if(len(depcpr) > 0):  # record exists
            if((depcpr[0].groupregion == None)|(depcpr[0].groupregion == '')):
                db((db.companyhmoplanrate.id == depcpr[0].id)).update(groupregion = regionid)
            elif((depcpr[0].groupregion != regionid)):
                db.companyhmoplanrate.insert(covered=1, 
                                             premium = 0,
                                             capitation = 0,
                                             companypays = 0,
                                             company = companyid,
                                             hmoplan = planid,
                                             groupregion = regionid,
                                             relation = webdep.relation,
                                             is_active = True,
                                             created_by = 1,
                                             created_on = datetime.datetime.now(),
                                             modified_by = 1,
                                             modified_on = datetime.datetime.now()
                                             
                                             )
            
        else: #record does not exist
            db.companyhmoplanrate.insert(covered=1, 
                                         premium = 0,
                                         capitation = 0,
                                         companypays = 0,
                                         company = companyid,
                                         hmoplan = planid,
                                         groupregion = regionid,
                                         relation = webdep.relation,
                                         is_active = True,
                                         created_by = 1,
                                         created_on = datetime.datetime.now(),
                                         modified_by = 1,
                                         modified_on = datetime.datetime.now()
                                         
                                         )
    db.commit()
    logger.logger.info("===================Exit migrate_dependants=======================================")
    return

def memberregion_equal_planregion(webmemberid, companyid, planid, regionid):
    
    logger.logger.info("===================Enter memberregion_equal_planregion=======================================")
    logger.logger.info("========Migrate : Webmember(%d) Company(%d) Plan(%d) Region(%d) Relation(Self)", webmemberid, companyid, planid, regionid)    
    cpr = db((db.companyhmoplanrate.company == companyid) & \
             (db.companyhmoplanrate.hmoplan == planid) & (db.companyhmoplanrate.relation == 'Self') & \
             (db.companyhmoplanrate.is_active==True)).select()
    
    if(len(cpr) > 0):  # record exists, Update region
        if((cpr[0].groupregion == None)|(cpr[0].groupregion == '')): #D
            db((db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.hmoplan == planid) & (db.companyhmoplanrate.relation == 'Self')).update(groupregion = regionid)
        elif ((cpr[0].groupregion != regionid)): # insert a new record
            db.companyhmoplanrate.insert(covered=1, 
                                             premium = int(common.getvalue(cpr[0].premium)),
                                             capitation = int(common.getvalue(cpr[0].capitation)),
                                             companypays = int(common.getvalue(cpr[0].companypays)),
                                             company = companyid,
                                             hmoplan = planid,
                                             groupregion = regionid,
                                             relation = 'Self',
                                             is_active = True,
                                             created_by = 1,
                                             created_on = datetime.datetime.now(),
                                             modified_by = 1,
                                             modified_on = datetime.datetime.now()
                                             )
    else: # record does not exists, add a record
        db.companyhmoplanrate.insert(covered=1, 
                                         premium = 0,
                                         capitation = 0,
                                         companypays = 0,
                                         company = companyid,
                                         hmoplan = planid,
                                         groupregion = regionid,
                                         relation = 'Self',
                                         is_active = True,
                                         created_by = 1,
                                         created_on = datetime.datetime.now(),
                                         modified_by = 1,
                                         modified_on = datetime.datetime.now()
                                         )
                                
    db.commit()
    migrate_dependants(webmemberid, companyid, planid, regionid)    
    
    logger.logger.info("===================Exit memberregion_equal_planregion=======================================")    
    return True


def memberregion_notequal_planregion(webmemberid, companyid, planid, regionid):
    
    # create a clode on the current plan
    currplan = db(db.hmoplan.id == planid).select()
    logger.logger.info("===================Enter memberregion_notequal_planregion=======================================")
    logger.logger.info("Insert Plan:Planid(%d), Plancode(%s) New Region(%d)", planid, currplan[0].hmoplancode, regionid)
    
    newplanid = db.hmoplan.insert(hmoplancode = currplan[0].hmoplancode,
                      name = currplan[0].name,
                      planfile = currplan[0].planfile,
                      welcomeletter = currplan[0].welcomeletter,
                      groupregion = regionid,
                      is_active = currplan[0].is_active,
                      created_by = 1,
                      created_on = datetime.datetime.now(),
                      modified_by = 1,
                      modified_on = datetime.datetime.now()
                      )

    logger.logger.info("Update Plan in Webmember:Webmember(%d), Planid(%d), Plancode(%s) New Region(%d)", webmemberid, newplanid, currplan[0].hmoplancode, regionid)
    
    db((db.webmember.id >= webmemberid) & (db.webmember.hmoplan == planid) & (db.webmember.groupregion == regionid)).\
        update(hmoplan = newplanid,modified_on = datetime.datetime.now()
                                              )
    db((db.patientmember.webmember >= webmemberid)&(db.patientmember.hmoplan == planid) & (db.patientmember.groupregion == regionid) & \
       (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).\
        update(hmoplan = newplanid,modified_on = datetime.datetime.now())
    
    db((db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.hmoplan==planid) & \
       ((db.companyhmoplanrate.groupregion == None)|(db.companyhmoplanrate.groupregion == ""))).update(\
           hmoplan=newplanid,groupregion=regionid,modified_on = datetime.datetime.now())
    db.commit()
    
    logger.logger.info("Insert CompanyPlanRate:Webmember(%d), Company(%d), Planid(%d), Plancode(%s) Region(%d), Relation(Self)", webmemberid, companyid, newplanid, currplan[0].hmoplancode, regionid)
    
    cpr = db((db.companyhmoplanrate.company == companyid) & \
             (db.companyhmoplanrate.hmoplan == newplanid) & (db.companyhmoplanrate.relation == 'Self') & \
             (db.companyhmoplanrate.is_active==True)).select()
     
    if(len(cpr) > 0):  # record exists, Update region
        if((cpr[0].groupregion == None)|(cpr[0].groupregion == '')): #D
            db((db.companyhmoplanrate.company == companyid) & (db.companyhmoplanrate.hmoplan == newplanid) & (db.companyhmoplanrate.relation == 'Self')).update(groupregion = regionid)
        elif ((cpr[0].groupregion != regionid)): # insert a new record
            db.companyhmoplanrate.insert(covered=1, 
                                             premium = int(common.getvalue(cpr[0].premium)),
                                             capitation = int(common.getvalue(cpr[0].capitation)),
                                             companypays = int(common.getvalue(cpr[0].companypays)),
                                             company = companyid,
                                             hmoplan = newplanid,
                                             groupregion = regionid,
                                             relation = 'Self',
                                             is_active = True,
                                             created_by = 1,
                                             created_on = datetime.datetime.now(),
                                             modified_by = 1,
                                             modified_on = datetime.datetime.now()
                                             )
    else: # record does not exists, add a record
        db.companyhmoplanrate.insert(covered=1, 
                                         premium = 0,
                                         capitation = 0,
                                         companypays = 0,
                                         company = companyid,
                                         hmoplan = newplanid,
                                         groupregion = regionid,
                                         relation = 'Self',
                                         is_active = True,
                                         created_by = 1,
                                         created_on = datetime.datetime.now(),
                                         modified_by = 1,
                                         modified_on = datetime.datetime.now()
                                         )

    db.commit()    
    migrate_dependants(webmemberid, companyid, newplanid, regionid)    
    logger.logger.info("===================Exit memberregion_notequal_planregion=======================================")
    
    return newplanid


def null_planregion(webmemberid, companyid, planid, regionid):
    
    logger.logger.info("===================Enter null_planregion=======================================")
    
    db(db.hmoplan.id == planid).update(groupregion = regionid)
    
    memberregion_equal_planregion(webmemberid, companyid, planid, regionid)
    logger.logger.info("===================Exit null_planregion=======================================")
    
    return True

@auth.requires_membership('webadmin')
@auth.requires_login()
def migratedata():

    username = auth.user.first_name + ' ' + auth.user.last_name
    
    #Updating Groupregion setting ALL in first record.
    logger.logger.info("=====Start: Updating Groupregion table record 1 with ALL======")       
    db(db.groupregion.id == 1).update(groupregion = 'ALL', region='ALL', is_active = True)
    logger.logger.info("====End: Updating Groupregion table record 1 with ALL======")       
    
    
    
    # for all members, 
    logger.logger.info("======Start:Assigning ALL region to Webmember and Patientmemebr with unassigned regions.=======")
    webmembers = db(db.webmember.id > 0).select()
    i = 0
    for webmember in webmembers:
        if((webmember.groupregion == None) | (webmember.groupregion == '')):
            i = i+1
            logger.logger.info("Update group region for webmember %s %s %s", webmember.webmember, webmember.fname, webmember.lname)
            db(db.webmember.id == webmember.id).update(groupregion = 1)
            db((db.patientmember.webmember == webmember.id) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).update(groupregion = 1)
    
    logger.logger.info("===== End:Assigning ALL region to Webmember and Patientmemebr with unassigned regions. Total(%d)=====", i)
    db.commit()
    
    #Set Company-Plan-Region in CompanyHmoPlanRate table based on Company-Plan set for a webmember
    logger.logger.info("===========Start:Migrate Company-Plan-Rate ====================")
    webmembers = db((db.webmember.is_active == True)).select()
    webmembercount = 0
    for webmember in webmembers:
        webmembercount += 1
        webmemberid = int(common.getid(webmember.id))
        companyid = int(common.getid(webmember.company))
        hmoplanid = int(common.getid(webmember.hmoplan))
        regionid = int(common.getid(webmember.groupregion))
        
        logger.logger.info("Migrating: Migrate Company-Plan-Rate Webmember(%d) Company(%d) Plan(%d) Region(%d)", \
                           webmemberid,companyid,hmoplanid,regionid)
        # get plan 
        plan = db(db.hmoplan.id == hmoplanid).select()
        if(len(plan) > 0): #A
            if((plan[0].groupregion == None)|(plan[0].groupregion == '')): #B  if plan region == NULL
                null_planregion(webmemberid, companyid, hmoplanid, regionid)
            elif((plan[0].groupregion != regionid)):
                    newplanid = memberregion_notequal_planregion(webmemberid, companyid, hmoplanid, regionid)
                    for i in xrange(0, len(webmembers)):
                        if((webmembers[i].id >= webmemberid) & (webmembers[i].hmoplan == hmoplanid) & (webmembers[i].groupregion == regionid)):
                           webmembers[i].hmoplan = newplanid
            elif((plan[0].groupregion == regionid)):
                    memberregion_equal_planregion(webmemberid, companyid, hmoplanid, regionid)
        else:
            logger.logger.info("Error: This Plan(%d) does not exists", hmoplanid)       
        
    #end of webmember
    logger.logger.info("===========End:Migrate Company-Plan-Rate ====================")                                
        

    #Update all the plan's regions to 1 (ALL) if not assigned any regions
    logger.logger.info("======Start:Assigning ALL region to Plans with unassigned regions.========")
    plans = db((db.hmoplan.groupregion == None) | (db.hmoplan.groupregion == '')).update(groupregion = 1)
    logger.logger.info("=====Complete:Number of ALL region assigned Plans =  %d=======", plans)
    
   
    
    #Updating companyhmoplanrate Groupregion = ALL where initially it was NULL
    logger.logger.info("======Start:Assigning ALL region to CPR with unassigned regions.========")
    count = db((db.companyhmoplanrate.groupregion == None)|(db.companyhmoplanrate.groupregion == "")).update(groupregion =1)
    logger.logger.info("======Completed: Assgigning Company-Plan-Rate-Region-NULL: Number of records (%d)=====", count)       
    
    #Number of Plans that either need PDF or Welcome Letter
    count = db((db.hmoplan.welcomeletter == None)|(db.hmoplan.welcomeletter == '')).update(welcomeletter='MyDentalPlanMemberWelcomeLetter.html')
    count = db((db.hmoplan.planfile == None)|(db.hmoplan.planfile == '')|(db.hmoplan.welcomeletter == None)|(db.hmoplan.welcomeletter == '')).count()
    logger.logger.info("Number of Plans with no Planfile or Welcomeletter(%d)", count)       
        
    returnurl = URL('default', 'main')
    return dict(username=username, returnurl=returnurl, planscount=count)


@auth.requires_login()
def agentcommissionreportparam():

    formheader = "Agent Commission Report"
    today = datetime.date.today()
    year  = datetime.timedelta(days=365)
    onedaydelta = datetime.timedelta(days=1)

    db.agentcommissionreportparam.startdate.default = datetime.date(today.year, 1, 1)
    db.agentcommissionreportparam.enddate.default = datetime.date(today.year, 12, 31)
    db.agentcommissionreportparam.agent.default = 1
    form = SQLFORM(db.agentcommissionreportparam,submit_button = 'Report>>',)

    if form.process().accepted:
        agentid = request.vars.agent
        startdate = request.vars.startdate
        enddate = request.vars.enddate
        redirect(URL('report','agentcommissionreport', args=[agentid,startdate,enddate]))
    return dict(form=form,formheader=formheader)

@auth.requires_login()
def enrollmentreportparam():
    if(auth.is_logged_in()):
        username = auth.user.first_name + ' ' + auth.user.last_name
    else:
        raise HTTP(400, "Error: User not logged - enrollmentreportparam")    
    return dict(username=username)

@auth.requires_login()
def memberenrollmentreportparam():
    return dict()


def providercapitationreportcsv():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Provider Capitation Report"
 
    providerid = int(common.getid(request.vars.providerid))
    provider = common.getstring(request.vars.provider)
    providername = common.getstring(request.vars.providername)
    startdt = request.vars.startdate
    enddt = request.vars.enddate
    is_active = bool(request.vars.is_active)
    
    left = None 
    links = None
    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)

    orderby =  db.vw_providercapitation.company
    groupby = db.vw_providercapitation.company | db.vw_providercapitation.premmonth
  
    field_id = db.vw_providercapitation.provider

    query = (\
             (db.vw_providercapitation.premstartdt >= startdt) & \
             (db.vw_providercapitation.premstartdt <= enddt) & \
             (db.vw_providercapitation.provider == providerid) \
       
            )
    
    fields=(db.vw_providercapitation.company,db.vw_providercapitation.hmoplancode,\
            db.vw_providercapitation.premmonth,db.vw_providercapitation.provider,db.vw_providercapitation.capitation\
            )


    
    headers={
        'vw_providercapitation.company':'Group(Company)',
        'vw_providercapitation.hmoplancode':'Plan',
        'vw_providercapitation.provider':'Provider',
        'vw_providercapitation.premmonth':'Cap. Month',
        'vw_providercapitation.capitation':'Capitation'
        }

    formB = SQLFORM.grid(query=query,
                         field_id = field_id,
                         headers=headers,
                         fields=fields,
                         links=links,
                         left=left,
                         orderby=orderby,
                         groupby=groupby,
                         exportclasses=exportlist,
                         links_in_grid=False,
                         searchable=False,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                        )    


    returnurl=URL('default','index')
    return dict(username=username, returnurl=returnurl,formB=formB, formheader=formheader)




@auth.requires_login()
def providercapitationreportparam():

    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Provider Capitation Report"
   
    providerid = int(common.getid(request.vars.providerid))
    
   
    form = SQLFORM.factory(
        Field('provider',  default=providerid, requires=IS_IN_DB(db(db.provider.is_active == True), db.provider.id, '%(providername)s %(provider)s')),
        Field('year', requires = IS_IN_SET(YEAR),length=20,default=request.now.year),
        Field('month', requires=IS_IN_SET(MONTH),length=20,default=months[request.now.month-1]),
        Field('is_active', 'boolean', default = True)
    )
   
    
    submit = form.element('input',_type='submit')
    submit['_style'] = 'display:none;'
    
       
    if form.accepts(request,session,keepvalues=True):
        providerid = int(common.getid(form.vars.provider))
        providers = db(db.provider.id == providerid).select()
        providername = providers[0].providername
        provider = providers[0].provider        
        
        year  = int(common.getid(form.vars.year))
        month = form.vars.month
        monthid = 1

        if(month == ""):
            startdate = datetime.date(year, 1,1)
            enddate = datetime.date(year, 12,31)
        else:
            for counter, value in enumerate(months,1):
                if(value == month):
                    monthid = counter
                    break;
            startdate = datetime.date(year, monthid,1)
            if((monthid == 1) | (monthid == 3)| (monthid == 5)| (monthid == 7)| (monthid == 8)| (monthid == 10)| (monthid == 12)):
                enddate = datetime.date(year, monthid,31)
            elif ((monthid == 4) | (monthid == 6)| (monthid == 9)| (monthid == 11)):
                enddate = datetime.date(year, monthid,30)
            else:
                if(calendar.isleap(startdate.year)):
                    enddate = datetime.date(year, monthid,29)
                else:
                    enddate = datetime.date(year, monthid,28)

            
        if(form.vars.is_active == True):
            is_active = 'T'
        else:
            is_active  = 'F'

        if(form.request_vars.action == 'csv'):
            redirect(URL('report','providercapitationreportcsv',\
                                     vars=dict(providerid=providerid, providername=providername, provider=provider,startdate=startdate,\
                                               enddate=enddate,is_active=is_active)))            
        else:
            
            props = db(db.urlproperties.id>0).select()
            
            if(len(props)>0):
                reportby = common.getstring((auth.user.first_name))  + " " + common.getstring((auth.user.last_name))
                reportlink = props[0].jasperreporturl + "ProviderCapitationDetail.pdf" \
                + "/?j_username=" + props[0].j_username + "&j_password=" + props[0].j_password \
                + "&providerid=" + str(providerid) + "&provider=" + provider + "&providername=" + providername \
                + "&startDt=" + startdate.strftime('%Y-%m-%d') + "&endDt=" + enddate.strftime('%Y-%m-%d')  + "&is_active=" + is_active  + "&reportby=" + reportby
    
                redirect(reportlink)            
    
        #redirect(URL('report','providercapitationreport', args=[providerid,startdate,enddate,is_active]))
    
    
    returnurl=URL('default','index')
    return dict(username=username,returnurl=returnurl,form=form,formheader=formheader)


#IB 05292016
@auth.requires_login()
def xprovidercapitationreportparam():

    username = auth.user.first_name + ' ' + auth.user.last_name

    formheader = "Provider Capitation Report"
    today = datetime.date.today()
    year  = datetime.timedelta(days=365)
    onedaydelta = datetime.timedelta(days=1)

    sql = "SELECT 1 AS providerid, '--Select--' AS providername "
    sql = sql + " UNION "
    sql = sql + "SELECT provider.id AS providerid, CONCAT(provider.providername,' ', provider.provider) AS providername from provider "
    sql = sql + " WHERE is_active='T'"


    dsprovider = db.executesql(sql)

    db.providercapitationreportparam.startdate.default = datetime.date(today.year, today.month, 1)
    db.providercapitationreportparam.enddate.default = datetime.date(today.year, today.month, calendar.monthrange(today.year,today.month)[1])
    db.providercapitationreportparam.provider.default = 1
    form = SQLFORM(db.providercapitationreportparam,submit_button = 'Report>>',)

    if form.process().accepted:
        providerid = form.vars.provider
        startdate = form.vars.startdate
        enddate = form.vars.enddate
        if(form.vars.is_active == True):
            is_active = 'T'
        else:
            is_active  = 'F'
        redirect(URL('report','providercapitationreport', args=[providerid,startdate,enddate,is_active]))
    returnurl=URL('default','index')
    return dict(username=username,returnurl=returnurl,form=form,formheader=formheader,dsprovider=dsprovider)

@auth.requires_login()
def agentcommissionreport():

    agentid = 0

    reportdate = datetime.date.today()

    today = datetime.date.today()
    year  = datetime.timedelta(days=365)

    startdate = datetime.date( datetime.date.today().year,1,1)
    enddate   = datetime.date( datetime.date.today().year,12,31)

    ds = None
    formheader = "Agent Commission Report"
    agentname = None
    agent = None

    if(len(request.args)==3):
        agentid = int(request.args[0])
        agents = db(db.agent.id == agentid).select()
        agentname = agents[0].name
        agent = agents[0].agent
        splits = request.args[1].split('-')
        startdate = datetime.date(int(splits[0]), int(splits[1]), int(splits[2]))
        splits = request.args[2].split('-')
        enddate = datetime.date(int(splits[0]), int(splits[1]), int(splits[2]))

        ds = account.agentcommissionYTD(db,agentid,startdate,enddate)
        return dict(ds=ds,formheader=formheader,reportdate=reportdate, agentid=agentid, agentname=agentname,agent=agent,startdate=request.args[1],enddate=request.args[2])


@auth.requires_login()
def xprovidercapitationreport():

    username = auth.user.first_name + ' ' + auth.user.last_name
    providerid = 0

    reportdate = datetime.date.today()

    #startdate = datetime.date( datetime.date.today().year,datetime.date.today().month,1)
    #enddate   = datetime.date( datetime.date.today().year,datetime.date.today().month,calendar.monthrange(datetime.date.today().year,datetime.date.today().month)[1])

    f = lambda name: name if ((name != "") & (name != None)) else ""
    reportby = f(auth.user.first_name)  + " " + f(auth.user.last_name)

    ds = None
    formheader = "Provider Capitation Report"
    providername = None
    provider = None

    if(len(request.args)==4):
        providerid = int(request.args[0])
        providers = db(db.provider.id == providerid).select()
        providername = providers[0].providername
        provider = providers[0].provider
        #splits = request.args[1].split('-')
        #startdate = datetime.date(int(splits[0]), int(splits[1]), int(splits[2]))
        #splits = request.args[2].split('-')
        #enddate = datetime.date(int(splits[0]), int(splits[1]), int(splits[2]))
        is_active = request.args[3]
        props = db(db.urlproperties.id>0).select()

        if(len(props)>0):
            reportlink = props[0].jasperreporturl + "ProviderCapitationDetail.pdf" \
            + "/?j_username=" + props[0].j_username + "&j_password=" + props[0].j_password \
            + "&providerid=" + str(providerid) + "&provider=" + provider + "&providername=" + providername \
            + "&startDt=" + request.args[1] + "&endDt=" + request.args[2]  + "&is_active=" + is_active  + "&reportby=" + reportby

            redirect(reportlink)

        ds = account.providercapitationYTD(db,providerid,startdate,enddate)
        returnurl=URL('default','index')
        return dict(username=username,returnurl=returnurl,ds=ds,formheader=formheader,reportdate=reportdate,providername=providername,providerid=providerid,provider=provider,startdate=request.args[1],enddate=request.args[2])

@auth.requires_login()
def agentcommissionreport_pdf():


    #<th>Group</th>
        #<th>Plan</th>
        #<th>Month</th>
        #<th>Members</th>
        #<th>Monthly Premium</th>
        #<th>Monthly Commission</th>

        response.title = "Agent Commission Report"
        reportdate = datetime.date.today()
        sreportdate = str(reportdate.year) + '-' + str(reportdate.month) + '-' + str(reportdate.day)

        agentid = request.args[0]
        agentname = request.args[1]
        agent = request.args[2]
        splits = request.args[3].split('-')
        startdate = datetime.date(int(splits[0]), int(splits[1]), int(splits[2]))
        sstartdate = splits[0] + '-' + splits[1] + '-' + splits[2]
        splits = request.args[4].split('-')
        enddate = datetime.date(int(splits[0]), int(splits[1]), int(splits[2]))
        senddate = splits[0] + '-' + splits[1] + '-' + splits[2]


        ds = account.agentcommissionYTD(db,agentid,startdate,enddate)

        grp = None
        pln = None


        head0 = THEAD(TR(TH("Report Date",_width="20%"),
                         TH("Agent",_width="50%"),
                         TH("Period",_width="30%"),
                         _bgcolor="#A0A0A0"))

        rows0 = []

        rows0.append(TR(TD(sreportdate, _align="left"),
                                  TD(agentname, _align="left"),
                                  TD(sstartdate + ' To ' + senddate, _align="center",_style="font-size:8px"),
                                  _bgcolor="#FFFFFF"))

        body0 = TBODY(*rows0)
        table0 = TABLE(*[head0,body0],
                      _border="1", _align="center", _width="100%")

        # define header and footers:
        head = THEAD(TR(TH("Group",_width="20%"),
                         TH("Plan",_width="20%"),
                         TH("Month",_width="10%"),
                         TH("Members",_width="10%"),
                         TH("Premium",_width="10%"),
                         TH("Commission",_width="30%"),
                         _bgcolor="#A0A0A0"))

        ## create several rows:
        grpcell = ''
        plncell = ''

        rows = []
        for i in xrange(0,len(ds)):
            col = i % 2 and "#F0F0F0" or "#FFFFFF"
            if(grp != ds[i][0]):
                grpcell = ds[i][0]
                grp = ds[i][0]
            else:
                grpcell = ds[i][0]

            if(pln != ds[i][1]):
                plncell = ds[i][1]
                pln = ds[i][1]
            else:
                plncell = ds[i][1]

            rows.append(TR(TD(grpcell, _align="left"),
                           TD(plncell, _align="left"),
                           TD(ds[i][2], _align="left",_style="color:red;font-size:19%"),
                           TD(ds[i][3], _align="right"),
                           TD(ds[i][4], _align="right"),
                           TD(ds[i][5], _align="right"),
                           _bgcolor=col))

        # make the table object
        body = TBODY(*rows)
        table = TABLE(*[head,body],
                      _border="1", _align="center", _width="100%")


        from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # create a custom class with the required functionalities
        class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                "hook to draw custom page header (logo and title)"
                #logo=os.path.join(request.env.web2py_path,"gluon","contrib","pyfpdf","tutorial","logo_pb.png")
                #self.image(logo,10,8,33)
                self.set_text_color(0,0,0)
                self.set_font('Courier','B',10)
                self.cell(40) # padding
                self.cell(100,10,response.title,1,0,'C')
                self.ln(5)

            def footer(self):
                "hook to draw custom page footer (printing page numbers)"
                self.set_y(-15)
                self.set_font('Arial','I',8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'C')

        pdf=MyFPDF()
        pdf.def_orientation='L'
        pdf.w_pt=pdf.fh_pt
        pdf.h_pt=pdf.fw_pt
        # create a page and serialize/render HTML objects
        pdf.add_page('L')
        pdf.set_text_color(0,0,0)
        pdf.set_font('Courier', '',  8)
        pdf.write_html(str(XML(table0, sanitize=False)))
        pdf.write_html(str(XML(table, sanitize=False)))
        #pdf.write_html(str(XML(CENTER(chart), sanitize=False)))
        # prepare PDF to download:
        response.headers['Content-Type']='application/pdf'
        return pdf.output(dest='S')

@auth.requires_login()
def providercapitationreport_pdf():

        response.title = "Provider Capitation Report"
        reportdate = datetime.date.today()
        sreportdate = str(reportdate.year) + '-' + str(reportdate.month) + '-' + str(reportdate.day)

        f = lambda name: name if ((name != "") & (name != None)) else ""
        reportby = f(auth.user.first_name)  + " " + f(auth.user.last_name)

        providerid = request.args[0]
        providername = request.args[1]
        provider = request.args[2]
        splits = request.args[3].split('-')
        startdate = datetime.date(int(splits[0]), int(splits[1]), int(splits[2]))
        sstartdate = splits[0] + '-' + splits[1] + '-' + splits[2]
        splits = request.args[4].split('-')
        enddate = datetime.date(int(splits[0]), int(splits[1]), int(splits[2]))
        senddate = splits[0] + '-' + splits[1] + '-' + splits[2]

        props = db(db.urlproperties.id>0).select()

        if(len(props)>0):
            reportlink = props[0].jasperreporturl + "ProviderCapitationDetail.html" \
            + "/?j_username=" + props[0].j_username + "&j_password=" + props[0].j_password \
            + "&providerid=" + str(providerid) + "&provider=" + provider + "&reportby=" + reportby \

            redirect(reportlink)


        ds = account.providercapitationYTD(db,providerid,startdate,enddate)

        grp = None
        pln = None


        head0 = THEAD(TR(TH("Report Date",_width="20%"),
                         TH("Provider",_width="50%"),
                         TH("Period",_width="30%"),
                         _bgcolor="#A0A0A0"))

        rows0 = []

        rows0.append(TR(TD(sreportdate, _align="left"),
                                  TD(providername, _align="left"),
                                  TD(sstartdate + ' To ' + senddate, _align="center",_style="font-size:8px"),
                                  _bgcolor="#FFFFFF"))

        body0 = TBODY(*rows0)
        table0 = TABLE(*[head0,body0],
                      _border="1", _align="center", _width="100%")

        # define header and footers:
        head = THEAD(TR(TH("Group",_width="30%"),
                         TH("Plan",_width="20%"),
                         TH("Month",_width="10%"),
                         TH("Members",_width="10%"),
                         TH("Monthly Capitation",_width="30%"),
                         _bgcolor="#A0A0A0"))

        ## create several rows:
        grpcell = ''
        plncell = ''

        rows = []
        for i in xrange(0,len(ds)):
            col = i % 2 and "#F0F0F0" or "#FFFFFF"
            if(grp != ds[i][0]):
                grpcell = ds[i][0]
                grp = ds[i][0]
            else:
                grpcell = ds[i][0]

            if(pln != ds[i][1]):
                plncell = ds[i][1]
                pln = ds[i][1]
            else:
                plncell = ds[i][1]

            rows.append(TR(TD(grpcell, _align="left"),
                           TD(plncell, _align="left"),
                           TD(ds[i][2], _align="left",_style="color:red;font-size:19%"),
                           TD(ds[i][3], _align="right"),
                           TD(ds[i][4], _align="right"),
                           _bgcolor=col))

        # make the table object
        body = TBODY(*rows)
        table = TABLE(*[head,body],
                      _border="1", _align="center", _width="100%")


        from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # create a custom class with the required functionalities
        class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                "hook to draw custom page header (logo and title)"
                #logo=os.path.join(request.env.web2py_path,"gluon","contrib","pyfpdf","tutorial","logo_pb.png")
                #self.image(logo,10,8,33)
                self.set_text_color(0,0,0)
                self.set_font('Courier','B',10)
                self.cell(40) # padding
                self.cell(100,10,response.title,1,0,'C')
                self.ln(5)

            def footer(self):
                "hook to draw custom page footer (printing page numbers)"
                self.set_y(-15)
                self.set_font('Arial','I',8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'C')

        pdf=MyFPDF()
        pdf.def_orientation='L'
        pdf.w_pt=pdf.fh_pt
        pdf.h_pt=pdf.fw_pt
        # create a page and serialize/render HTML objects
        pdf.add_page('L')
        pdf.set_text_color(0,0,0)
        pdf.set_font('Courier', '',  8)
        pdf.write_html(str(XML(table0, sanitize=False)))
        pdf.write_html(str(XML(table, sanitize=False)))
        #pdf.write_html(str(XML(CENTER(chart), sanitize=False)))
        # prepare PDF to download:
        response.headers['Content-Type']='application/pdf'
        return pdf.output(dest='S')


def validateNoneValue(e):
    retval = e
    if(e == None):
        retval = ''
    return retval

@auth.requires_login()
def enrollmentreport():
    formheader = "Enrollment Status"
    companyid = 0
    companyname = None
    company = None
    reportdate = datetime.date.today()
    f = lambda name: name if ((name != "") & (name != None)) else ""
    reportby = f(auth.user.first_name)  + " " + f(auth.user.last_name)
    employees = 0
    noattempts = 0
    attempts = 0
    completed  = 0
    enrolled = 0


    if(len(request.args)>0):
        companyid = int(request.args[0])
        session.companyid = companyid
    elif(len(request.vars)>0):
        companyid = session.companyid
    else:
        raise HTTP(400,"No Company")

    rows = db((db.company.id == companyid) & (db.company.is_active == True)).select()
    if(len(rows)>0):
        companyname = rows[0].name
        company = rows[0].company
        employees = db((db.webmember.company == companyid)&(db.webmember.is_active == True)).count()
        noattempts = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'No_Attempt')).count()
        attempts = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'Attempting')).count()
        completed = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'Completed')).count()
        enrolled = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'Enrolled')).count()
    else:
        raise HTTP(400,"No Company")




    #sql = "select webmember.*, count(webmemberdependants.id) as dependants from webmember  "
    #sql = sql + "left join webmemberdependants ON  webmemberdependants.webmember = webmember.id  "
    #sql = sql + " WHERE webmember.company = " + str(companyid)
    #sql = sql + " group by webmember.webmember "


    sql = "select webmember.*, IFNULL(webmemberdependants1.dependants,0) AS dependants from webmember "
    sql = sql + " left join "
    sql = sql + " (Select count(webmemberdependants.id) as dependants, webmemberdependants.webmember from webmemberdependants group by webmember order by webmember) AS webmemberdependants1 ON "
    sql = sql + " webmember.id = webmemberdependants1.webmember where webmember.company = " + str(companyid)
    ds  = db.executesql(sql)



    if(len(ds)>0):
        db((db.enrollmentstatus.companyid == companyid) & (db.enrollmentstatus.userid == auth.user.id)).delete()
        for i in xrange(0,len(ds)):



                db.enrollmentstatus.insert(companyname = companyname, companyid = companyid, userid=auth.user.id, \
                                           fname=validateNoneValue(ds[i][2]),\
                                           mname=validateNoneValue(ds[i][3]),\
                                           lname=validateNoneValue(ds[i][4]), \
                                           gender=validateNoneValue(ds[i][11]), \
                                           webdob=validateNoneValue(ds[i][16]), \
                                           address1=validateNoneValue(ds[i][5]), \
                                           address2=validateNoneValue(ds[i][6]), \
                                           address3=validateNoneValue(ds[i][7]), \
                                           city=validateNoneValue(ds[i][8]), \
                                           st=validateNoneValue(ds[i][9]), \
                                           pin = validateNoneValue(ds[i][10]),\
                                           telephone=validateNoneValue(ds[i][12]), \
                                           cell=validateNoneValue(ds[i][13]), \
                                           email=validateNoneValue(ds[i][14]), \
                                           webpan=validateNoneValue(ds[i][15]), \
                                           status=validateNoneValue(ds[i][17]), \
                                           pin1=validateNoneValue(ds[i][21]), \
                                           pin2=validateNoneValue(ds[i][22]), \
                                           pin3=validateNoneValue(ds[i][23]), \
                                           dependants=int(ds[i][36])\
                                          )




    fieldsB=(db.enrollmentstatus.fname,\
             db.enrollmentstatus.lname,\
             db.enrollmentstatus.status,\
             db.enrollmentstatus.dependants\
             )

    headersB={'enrollmentstatus.fname':'First Name',
             'enrollmentstatus.lname':'Last Name',
             'enrollmentstatus.status':'Status',
             'enrollmentstatus.dependants':'Dependants'
             }

    fieldsC=(db.enrollmentstatus.fname,\
             db.enrollmentstatus.mname,\
             db.enrollmentstatus.lname,\
             db.enrollmentstatus.webdob,\
             db.enrollmentstatus.gender,\
             db.enrollmentstatus.cell,\
             db.enrollmentstatus.telephone,\
             db.enrollmentstatus.email,\
             db.enrollmentstatus.address1,\
             db.enrollmentstatus.address2,\
             db.enrollmentstatus.address3,\
             db.enrollmentstatus.city,\
             db.enrollmentstatus.st,\
             db.enrollmentstatus.pin,\
             db.enrollmentstatus.pin1,\
             db.enrollmentstatus.pin2,\
             db.enrollmentstatus.pin3,\
             db.enrollmentstatus.status,\
             db.enrollmentstatus.dependants,\
             db.enrollmentstatus.companyname\
             )

    headersC={'enrollmentstatus.fname':'First Name',
             'enrollmentstatus.lname':'Last Name',
             'enrollmentstatus.webdob':'DOB',\
             'enrollmentstatus.gender':'Gender',\
             'enrollmentstatus.cell':'Mobile Number',\
             'enrollmentstatus.telephone':'Telelphone',\
             'enrollmentstatus.email':'Email ID',\
             'enrollmentstatus.address1':'Address 1',\
             'enrollmentstatus.address2':'Address 2',\
             'enrollmentstatus.address3':'Address 3',\
             'enrollmentstatus.city':'City',\
             'enrollmentstatus.st':'State',\
             'enrollmentstatus.pin':'Pin',\
             'enrollmentstatus.pin1':'Dentist Pin1',\
             'enrollmentstatus.pin2':'Dentist Pin2',\
             'enrollmentstatus.pin3':'Dentist Pin3',\
             'enrollmentstatus.status':'Status',\
             'enrollmentstatus.dependants':'Dependants',\
             'enrollmentstatus.companyname':'Company'
             }

    db.enrollmentstatus.mname.readable = False
    db.enrollmentstatus.webdob.readable=False
    db.enrollmentstatus.gender.readable=False
    db.enrollmentstatus.cell.readable=False
    db.enrollmentstatus.telephone.readable=False
    db.enrollmentstatus.email.readable=False
    db.enrollmentstatus.address1.readable=False
    db.enrollmentstatus.address2.readable=False
    db.enrollmentstatus.address3.readable=False
    db.enrollmentstatus.city.readable=False
    db.enrollmentstatus.st.readable=False
    db.enrollmentstatus.pin.readable=False
    db.enrollmentstatus.pin1.readable=False
    db.enrollmentstatus.pin2.readable=False
    db.enrollmentstatus.pin3.readable=False
    #db.enrollmentstatus.status.readable=False
    db.enrollmentstatus.companyname.readable=False


    exportlistB = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, csv=False, json=False, xml=False)
    exportlistC = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, xml=False)


    query = ((db.enrollmentstatus.companyid == companyid) & (db.enrollmentstatus.userid==auth.user.id))

    left = None ##   [db.webmemberdependants.on(db.webmemberdependants.webmember==db.webmember.id)]

    ## called from menu


    formB = SQLFORM.grid(query=query,
                        headers=headersB,
                        fields=fieldsC,
                        left=left,
                        searchable=True,
                        exportclasses=exportlistC,
                        csv=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        paginate=10,
                        user_signature=False)

    #formC = SQLFORM.grid(query=query,
                        #headers=headersC,
                        #fields=fieldsC,
                        #left=left,
                        #searchable=False,
                        #exportclasses=exportlistC,
                        #create=False,
                        #deletable=False,
                        #editable=False,
                        #details=False,
                        #paginate=None,
                        #user_signature=False)


    return dict(formheader=formheader,companyid=companyid, companyname = companyname, company=company, reportdate=reportdate, reportby=reportby,\
                employees=employees,noattempts=noattempts,attempts=attempts,completed=completed,enrolled=enrolled,formB=formB)


#@auth.requires_login()
#def membercard_pdf():

    #response.title = "Member Card"


    #formheader = "Member Card"
    #memberid = 0
    #membersql = ""
    #memberds = None
    #deprows = None
    #if(len(request.args)>0):
        #memberid = int(request.args[0])
        #memberds = db(db.patientmember.id == memberid).select(db.patientmember.id,db.patientmember.patientmember,db.patientmember.fname,db.patientmember.mname,db.patientmember.lname, db.hmoplan.hmoplancode, db.hmoplan.name, db.patientmember.enrollmentdate,\
                                                             #db.patientmember.pan, db.patientmember.address1, db.patientmember.address2, db.patientmember.address3,\
                                                             #db.patientmember.city, db.patientmember.st, db.patientmember.pin,db.patientmember.dob,db.patientmember.email,db.patientmember.cell,db.patientmember.gender,\
                                                             #db.patientmember.image,db.company.company, db.company.name,\
                                                             #left=[db.company.on(db.company.id == db.patientmember.company), \
                                                                   #db.hmoplan.on(db.hmoplan.id == db.company.hmoplan)
                                                                   #])



        #deprows = db(db.patientmemberdependants.patientmember == memberid).select(db.patientmemberdependants.fname, db.patientmemberdependants.lname, db.patientmemberdependants.depdob, db.patientmemberdependants.relation)


        #head0 = THEAD(TR(TH("Report Date",_width="20%"),
                         #TH("Report By",_width="50%"),
                         #TH("Company",_width="30%"),
                         #_bgcolor="#A0A0A0"))

        #rows0 = []

        #rows0.append(TR(TD(reportdate, _align="left"),
                              #TD(reportby, _align="left"),
                              #TD(companyname,_align="left"),
                              #_bgcolor="#FFFFFF"))

        #body0 = TBODY(*rows0)
        #table0 = TABLE(*[head0,body0],
                  #_border="1", _align="center", _width="100%")

        ## define header and footers:
        #head = THEAD(TR(TH("Employees",_width="30%"),
                         #TH("No Attempts",_width="20%"),
                         #TH("Attempts",_width="10%"),
                         #TH("Completed",_width="10%"),
                         #_bgcolor="#A0A0A0"))

        #rows = []
        #rows.append(TR(TD(employees, _align="left"),
                       #TD(noattempts, _align="left"),
                       #TD(attempts, _align="left",_style="color:red;font-size:19%"),
                       #TD(completed, _align="right"),
                       #_bgcolor="#F0F0F0"))


        ### create several rows:

        ## make the table object
        #body = TBODY(*rows)
        #table = TABLE(*[head,body],
                      #_border="1", _align="center", _width="100%")


        ## define header and footers:
        #dephead = THEAD(TR(TH("First Name",_width="40%"),
                         #TH("Last Name",_width="40%"),
                         #TH("Dependants",_width="20%"),
                         #_bgcolor="#A0A0A0"))
        #deprows = []
        #fnamecell = ''
        #lnamecell = ''
        #depscell = ''

        #fname = None
        #lname = None
        #deps = None

        #deprows = []
        #for i in xrange(0,len(ds)):
                #col = i % 2 and "#F0F0F0" or "#FFFFFF"
                #deprows.append(TR(
                               #TD(ds[i][2], _align="left"),
                               #TD(ds[i][3], _align="left"),
                               #TD(ds[i][4], _align="right"),
                               #_bgcolor=col))

        ## make the table object
        #depbody = TBODY(*deprows)
        #deptable = TABLE(*[dephead,depbody],
                      #_border="1", _align="center", _width="100%")


        #from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        ## create a custom class with the required functionalities
        #class MyFPDF(FPDF, HTMLMixin):
            #def header(self):
                #"hook to draw custom page header (logo and title)"
                ##logo=os.path.join(request.env.web2py_path,"gluon","contrib","pyfpdf","tutorial","logo_pb.png")
                ##self.image(logo,10,8,33)
                #self.set_text_color(0,0,0)
                #self.set_font('Courier','B',10)
                #self.cell(40) # padding
                #self.cell(100,10,response.title,1,0,'C')
                #self.ln(5)

            #def footer(self):
                #"hook to draw custom page footer (printing page numbers)"
                #self.set_y(-15)
                #self.set_font('Arial','I',8)
                #txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                #self.cell(0,10,txt,0,0,'C')

        #pdf=MyFPDF()
        ## create a page and serialize/render HTML objects
        #pdf.add_page()
        #pdf.set_text_color(0,0,0)
        #pdf.set_font('Courier', '',  8)
        #pdf.write_html(str(XML(table0, sanitize=False)))
        #pdf.write_html(str(XML(table, sanitize=False)))
        #pdf.write_html(str(XML(deptable, sanitize=False)))
        ##pdf.write_html(str(XML(CENTER(chart), sanitize=False)))
        ## prepare PDF to download:
        #response.headers['Content-Type']='application/pdf'
        #return pdf.output(dest='S')



@auth.requires_login()
def memberenrollmentreport():

    formheader = "Enrollment Status"
    companyid = None
    companyname = None
    company = None
    reportdate = datetime.date.today()
    f = lambda name: name if ((name != "") & (name != None)) else ""
    reportby = f(auth.user.first_name)  + " " + f(auth.user.last_name)

    employees = 0
    noattempts = 0
    attempts = 0
    completed  = 0
    enrolled = 0
    compamyid = 0

    if(len(request.args)>0):
        companyid = int(request.args[0])
        session.companyid = companyid
    elif(len(request.vars)>0):
        companyid = session.companyid
    else:
        raise HTTP(400,"No Company")


    rows = db((db.company.id == companyid) & (db.company.is_active == True)).select()
    if(len(rows)>0):
        companyname = rows[0].name
        company = rows[0].company
        employees = db((db.webmember.company == companyid)&(db.webmember.is_active == True)).count()
        noattempts = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'No_Attempt')).count()
        attempts = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'Attempting')).count()
        completed = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'Completed')).count()
        enrolled = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'Enrolled')).count()
    else:
        raise HTTP(400,"No Company")




    sql = "select webmember.webmember, webmember.fname, webmember.lname, provider.provider, provider.providername,"
    sql = sql + " company.company, hmoplan.hmoplancode, webmember.cell  from webmember  "
    sql = sql + " left join provider ON provider.id = webmember.provider "
    sql = sql + " left join company ON company.id = webmember.company "
    sql = sql + " left join hmoplan ON hmoplan.id = webmember.hmoplan "
    sql = sql + " WHERE webmember.status = 'Enrolled' AND webmember.company = " + str(companyid)
    sql = sql + " group by webmember.webmember "
    ds  = db.executesql(sql)

    #address1=validateNoneValue(ds[i][0]), \   # webmember
    #fname=validateNoneValue(ds[i][1]),\       # fname
    #lname=validateNoneValue(ds[i][2]), \      # lname
    #address2=validateNoneValue(ds[i][3]), \   # provider code
    #address3=validateNoneValue(ds[i][4]), \   # provider name
    #city=validateNoneValue(ds[i][5]), \       # company code
    #st=validateNoneValue(ds[i][6]), \         # hmo plan code
    #cell=validateNoneValue(ds[i][7]) \       # member cell


    if(len(ds)>0):
        db((db.enrollmentstatus.companyid == companyid) & (db.enrollmentstatus.userid == auth.user.id)).delete()
        for i in xrange(0,len(ds)):
                db.enrollmentstatus.insert(companyname = company, companyid = companyid, userid=auth.user.id, \
                                           address1=validateNoneValue(ds[i][0]),\
                                           fname=validateNoneValue(ds[i][1]),\
                                           lname=validateNoneValue(ds[i][2]), \
                                           address2=validateNoneValue(ds[i][3]), \
                                           address3=validateNoneValue(ds[i][4]), \
                                           city=validateNoneValue(ds[i][5]), \
                                           st=validateNoneValue(ds[i][6]), \
                                           cell=validateNoneValue(ds[i][7]) \
                                          )




    fieldsB=(

             db.enrollmentstatus.address1,\
             db.enrollmentstatus.fname,\
             db.enrollmentstatus.lname,\
             db.enrollmentstatus.cell,\
             db.enrollmentstatus.companyname,\
             db.enrollmentstatus.address2,\
             db.enrollmentstatus.address3,\
             db.enrollmentstatus.st\
             )

    headersB={
              'enrollmentstatus.address1':'Member ID',
              'enrollmentstatus.fname':'First Name',
              'enrollmentstatus.lname':'Last Name',
              'enrollmentstatus.cell':'Cell',
              'enrollmentstatus.companyname':'Company',
              'enrollmentstatus.address2':'Provider ID',
              'enrollmentstatus.address3':'Provider',
              'enrollmentstatus.st':'HMO'
             }

    fieldsC=(
                 db.enrollmentstatus.address1,\
                 db.enrollmentstatus.fname,\
                 db.enrollmentstatus.lname,\
                 db.enrollmentstatus.cell,\
                 db.enrollmentstatus.companyname,\
                 db.enrollmentstatus.address2,\
                 db.enrollmentstatus.address3,\
                 db.enrollmentstatus.st\
                 )

    headersC={
              'enrollmentstatus.address1':'Member ID',
              'enrollmentstatus.fname':'First Name',
              'enrollmentstatus.lname':'Last Name',
              'enrollmentstatus.cell':'Cell',
              'enrollmentstatus.companyname':'Company',
              'enrollmentstatus.address2':'Provider ID',
              'enrollmentstatus.address3':'Provider',
              'enrollmentstatus.st':'HMO'
             }


    #fieldsC=(db.enrollmentstatus.fname,\
             #db.enrollmentstatus.mname,\
             #db.enrollmentstatus.lname,\
             #db.enrollmentstatus.webdob,\
             #db.enrollmentstatus.gender,\
             #db.enrollmentstatus.cell,\
             #db.enrollmentstatus.telephone,\
             #db.enrollmentstatus.email,\
             #db.enrollmentstatus.address1,\
             #db.enrollmentstatus.address2,\
             #db.enrollmentstatus.address3,\
             #db.enrollmentstatus.city,\
             #db.enrollmentstatus.st,\
             #db.enrollmentstatus.pin,\
             #db.enrollmentstatus.pin1,\
             #db.enrollmentstatus.pin2,\
             #db.enrollmentstatus.pin3,\
             #db.enrollmentstatus.status,\
             #db.enrollmentstatus.dependants,\
             #db.enrollmentstatus.companyname\
             #)

    #headersC={'enrollmentstatus.fname':'First Name',
             #'enrollmentstatus.lname':'Last Name',
             #'enrollmentstatus.webdob':'DOB',\
             #'enrollmentstatus.gender':'Gender',\
             #'enrollmentstatus.cell':'Mobile Number',\
             #'enrollmentstatus.telephone':'Telelphone',\
             #'enrollmentstatus.email':'Email ID',\
             #'enrollmentstatus.address1':'Address 1',\
             #'enrollmentstatus.address2':'Address 2',\
             #'enrollmentstatus.address3':'Address 3',\
             #'enrollmentstatus.city':'City',\
             #'enrollmentstatus.st':'State',\
             #'enrollmentstatus.pin':'Pin',\
             #'enrollmentstatus.pin1':'Dentist Pin1',\
             #'enrollmentstatus.pin2':'Dentist Pin2',\
             #'enrollmentstatus.pin3':'Dentist Pin3',\
             #'enrollmentstatus.status':'Status',\
             #'enrollmentstatus.dependants':'Dependants',\
             #'enrollmentstatus.companyname':'Company'
             #}

    #db.enrollmentstatus.mname.readable = False
    #db.enrollmentstatus.webdob.readable=False
    #db.enrollmentstatus.gender.readable=False
    #db.enrollmentstatus.cell.readable=False
    #db.enrollmentstatus.telephone.readable=False
    #db.enrollmentstatus.email.readable=False
    #db.enrollmentstatus.address1.readable=False
    #db.enrollmentstatus.address2.readable=False
    #db.enrollmentstatus.address3.readable=False
    #db.enrollmentstatus.city.readable=False
    #db.enrollmentstatus.st.readable=False
    #db.enrollmentstatus.pin.readable=False
    #db.enrollmentstatus.pin1.readable=False
    #db.enrollmentstatus.pin2.readable=False
    #db.enrollmentstatus.pin3.readable=False
    #db.enrollmentstatus.status.readable=False
    #db.enrollmentstatus.companyname.readable=False


    exportlistB = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, csv=False, json=False, xml=False)
    exportlistC = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, xml=False)


    query = ((db.enrollmentstatus.companyid == companyid) & (db.enrollmentstatus.userid==auth.user.id))

    left = None ##   [db.webmemberdependants.on(db.webmemberdependants.webmember==db.webmember.id)]

    ## called from menu


    formB = SQLFORM.grid(query=query,
                        headers=headersB,
                        fields=fieldsC,
                        left=left,
                        searchable=False,
                        exportclasses=exportlistC,
                        csv=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=False)

    #formC = SQLFORM.grid(query=query,
                        #headers=headersC,
                        #fields=fieldsC,
                        #left=left,
                        #searchable=False,
                        #exportclasses=exportlistC,
                        #create=False,
                        #deletable=False,
                        #editable=False,
                        #details=False,
                        #paginate=None,
                        #user_signature=False)


    return dict(formheader=formheader,companyid=companyid, companyname = companyname, company=company, reportdate=reportdate, reportby=reportby,\
                employees=employees,noattempts=noattempts,attempts=attempts,completed=completed,enrolled=enrolled,formB=formB)


@auth.requires_login()
def enrollmentreport_pdf():

    response.title = "Enrollment Status Report"


    formheader = "Enrollment Status"
    companyid = None
    companyname = None
    company = None
    reportdate = datetime.date.today()
    f = lambda name: name if ((name != "") & (name != None)) else ""
    reportby = f(auth.user.first_name)  + " " + f(auth.user.last_name)
    employees = 0
    noattempts = 0
    attempts = 0
    completed  = 0
    enrolled = 0

    if(len(request.args)>0):
        companyid = int(request.args[0])
        rows = db((db.company.id == companyid) & (db.company.is_active == True)).select()
        if(len(rows)>0):
            companyname = rows[0].name
            company = rows[0].company
            employees = db((db.webmember.company == companyid)&(db.webmember.is_active == True)).count()
            noattempts = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'No_Attempt')).count()
            attempts = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'Attempting')).count()
            completed = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'Completed')).count()
            enrolled = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'Enrolled')).count()
        else:
            raise HTTP(400,"No Company")




        sql = "select webmember.id, webmember.webmember, webmember.fname AS fname, webmember.lname AS lname, count(webmemberdependants.id) as dependants, webmember.status as status from webmember  "
        sql = sql + "left join webmemberdependants ON  webmemberdependants.webmember = webmember.id  "
        sql = sql + " WHERE webmember.company = " + str(companyid)
        sql = sql + " group by webmember.webmember "
        ds  = db.executesql(sql)



        head0 = THEAD(TR(TH("Report Date",_width="20%"),
                         TH("Report By",_width="50%"),
                         TH("Company",_width="30%"),
                         _bgcolor="#A0A0A0"))

        rows0 = []

        rows0.append(TR(TD(reportdate, _align="left"),
                              TD(reportby, _align="left"),
                              TD(companyname,_align="left"),
                              _bgcolor="#FFFFFF"))

        body0 = TBODY(*rows0)
        table0 = TABLE(*[head0,body0],
                  _border="1", _align="center", _width="100%")

        # define header and footers:
        head = THEAD(TR(TH("Employees",_width="30%"),
                         TH("No Attempts",_width="20%"),
                         TH("Attempts",_width="10%"),
                         TH("Completed",_width="10%"),
                         _bgcolor="#A0A0A0"))

        rows = []
        rows.append(TR(TD(employees, _align="left"),
                       TD(noattempts, _align="left"),
                       TD(attempts, _align="left",_style="color:red;font-size:19%"),
                       TD(completed, _align="right"),
                       _bgcolor="#F0F0F0"))


        ## create several rows:

        # make the table object
        body = TBODY(*rows)
        table = TABLE(*[head,body],
                      _border="1", _align="center", _width="100%")


        # define header and footers:
        dephead = THEAD(TR(TH("First Name",_width="35%"),
                         TH("Last Name",_width="35%"),
                         TH("Status",_width="15%"),
                         TH("Dependants",_width="15%"),
                         _bgcolor="#A0A0A0"))
        deprows = []
        fnamecell = ''
        lnamecell = ''
        depscell = ''

        fname = None
        lname = None
        deps = None

        deprows = []
        for i in xrange(0,len(ds)):
                col = i % 2 and "#F0F0F0" or "#FFFFFF"
                deprows.append(TR(
                               TD(ds[i][2], _align="left"),
                               TD(ds[i][3], _align="left"),
                               TD(ds[i][5], _align="left"),
                               TD(ds[i][4], _align="right"),
                               _bgcolor=col))

        # make the table object
        depbody = TBODY(*deprows)
        deptable = TABLE(*[dephead,depbody],
                      _border="1", _align="center", _width="100%")


        from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # create a custom class with the required functionalities
        class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                "hook to draw custom page header (logo and title)"
                #logo=os.path.join(request.env.web2py_path,"gluon","contrib","pyfpdf","tutorial","logo_pb.png")
                #self.image(logo,10,8,33)
                self.set_text_color(0,0,0)
                self.set_font('Courier','B',10)
                self.cell(40) # padding
                self.cell(100,10,response.title,1,0,'C')
                self.ln(5)

            def footer(self):
                "hook to draw custom page footer (printing page numbers)"
                self.set_y(-15)
                self.set_font('Arial','I',8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'C')

        pdf=MyFPDF()
        pdf.def_orientation='L'
        pdf.w_pt=pdf.fh_pt
        pdf.h_pt=pdf.fw_pt
        # create a page and serialize/render HTML objects
        pdf.add_page('L')
        pdf.set_text_color(0,0,0)
        pdf.set_font('Courier', '',  8)
        pdf.write_html(str(XML(table0, sanitize=False)))
        pdf.write_html(str(XML(table, sanitize=False)))
        pdf.write_html(str(XML(deptable, sanitize=False)))
        #pdf.write_html(str(XML(CENTER(chart), sanitize=False)))
        # prepare PDF to download:
        response.headers['Content-Type']='application/pdf'
        return pdf.output(dest='S')

@auth.requires_login()
def memberenrollmentreport_pdf():

    response.title = "Member Enrollment Report"


    formheader = "Member Enrollment"
    companyid = None
    companyname = None
    company = None
    reportdate = datetime.date.today()
    f = lambda name: name if ((name != "") & (name != None)) else ""
    reportby = f(auth.user.first_name)  + " " + f(auth.user.last_name)
    employees = 0
    noattempts = 0
    attempts = 0
    completed  = 0
    enrolled = 0

    if(len(request.args)>0):
        companyid = int(request.args[0])
        rows = db((db.company.id == companyid) & (db.company.is_active == True)).select()
        if(len(rows)>0):
            companyname = rows[0].name
            company = rows[0].company
            employees = db((db.webmember.company == companyid)&(db.webmember.is_active == True)).count()
            noattempts = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'No_Attempt')).count()
            attempts = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'Attempting')).count()
            completed = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'Completed')).count()
            enrolled = db((db.webmember.company == companyid)&(db.webmember.is_active == True) & (db.webmember.status == 'Enrolled')).count()
        else:
            raise HTTP(400,"No Company")




        sql = "select webmember.webmember, webmember.fname, webmember.lname, provider.provider, provider.providername,"
        sql = sql + " company.company, hmoplan.hmoplancode, webmember.cell  from webmember  "
        sql = sql + " left join provider ON provider.id = webmember.provider "
        sql = sql + " left join company ON company.id = webmember.company "
        sql = sql + " left join hmoplan ON hmoplan.id = webmember.hmoplan "
        sql = sql + " WHERE webmember.status = 'Enrolled' AND webmember.company = " + str(companyid)
        sql = sql + " group by webmember.webmember "
        ds  = db.executesql(sql)


        head0 = THEAD(TR(TH("Report Date",_width="20%"),
                         TH("Report By",_width="50%"),
                         TH("Company",_width="30%"),
                         _bgcolor="#A0A0A0"))

        rows0 = []

        rows0.append(TR(TD(reportdate, _align="left"),
                              TD(reportby, _align="left"),
                              TD(companyname,_align="left"),
                              _bgcolor="#FFFFFF"))

        body0 = TBODY(*rows0)
        table0 = TABLE(*[head0,body0],
                  _border="1", _align="center", _width="100%")

        # define header and footers:
        head = THEAD(TR(TH("Employees",_width="30%",_style="color:red;font-size:8%"),
                         TH("No Attempts",_width="20%"),
                         TH("Attempts",_width="10%"),
                         TH("Completed",_width="10%"),
                         _bgcolor="#A0A0A0"))

        rows = []
        #rows.append(TR(TD(employees, _align="left"),
                       #TD(noattempts, _align="left"),
                       #TD(attempts, _align="left",_style="color:red;font-size:19%"),
                       #TD(completed, _align="right"),
                       #_bgcolor="#F0F0F0"))


        ## create several rows:
        #'enrollmentstatus.address1':'Member ID',
        #'enrollmentstatus.fname':'First Name',
        #'enrollmentstatus.lname':'Last Name',
        #'enrollmentstatus.cell':'Cell',
        #'enrollmentstatus.companyname':'Company',
        #'enrollmentstatus.address2':'Provider ID',
        #'enrollmentstatus.address3':'Provider',
        #'enrollmentstatus.st':'HMO'

        #address1=validateNoneValue(ds[i][0]), \   # webmember
        #fname=validateNoneValue(ds[i][1]),\       # fname
        #lname=validateNoneValue(ds[i][2]), \      # lname
        #address2=validateNoneValue(ds[i][3]), \   # provider code
        #address3=validateNoneValue(ds[i][4]), \   # provider name
        #city=validateNoneValue(ds[i][5]), \       # company code
        #st=validateNoneValue(ds[i][6]), \         # hmo plan code
        #cell=validateNoneValue(ds[i][7]) \       # member cell

        ## make the table object
        body = TBODY(*rows)
        table = TABLE(*[head,body],
                      _border="1", _align="center", _width="100%")


        # define header and footers:
        dephead = THEAD(TR(
                         TH("First Name",_width="15%"),
                         TH("Last Name",_width="15%"),
                         TH("Cell",_width="15%"),
                         TH("Provider",_width="20%"),
                         TH("Plan",_width="55%"),
                         _bgcolor="#A0A0A0"))
        deprows = []
        fnamecell = ''
        lnamecell = ''
        depscell = ''

        fname = None
        lname = None
        deps = None

        deprows = []
        for i in xrange(0,len(ds)):
                col = i % 2 and "#F0F0F0" or "#FFFFFF"
                deprows.append(TR(

                               TD(ds[i][1], _align="left"),
                               TD(ds[i][2], _align="left"),
                               TD(ds[i][7], _align="left"),
                               TD(ds[i][6], _align="left"),
                               TD(ds[i][4], _align="left"),
                               _bgcolor=col))

        # make the table object
        depbody = TBODY(*deprows)
        deptable = TABLE(*[dephead,depbody],
                      _border="1", _align="center", _width="100%")


        from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # create a custom class with the required functionalities
        class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                "hook to draw custom page header (logo and title)"
                #logo=os.path.join(request.env.web2py_path,"gluon","contrib","pyfpdf","tutorial","logo_pb.png")
                #self.image(logo,10,8,33)
                self.set_text_color(0,0,0)
                self.set_font('Courier','B',10)
                self.cell(40) # padding
                self.cell(100,10,response.title,1,0,'C')
                self.ln(5)

            def footer(self):
                "hook to draw custom page footer (printing page numbers)"
                self.set_y(-15)
                self.set_font('Arial','I',8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'C')

        pdf=MyFPDF()
        # create a page and serialize/render HTML objects
        pdf.def_orientation='L'
        pdf.w_pt=pdf.fh_pt
        pdf.h_pt=pdf.fw_pt
        pdf.add_page('L')
        pdf.set_text_color(0,0,0)
        pdf.set_font('Arial', '',  8)
        pdf.write_html(str(XML(table0, sanitize=False)))
        pdf.write_html(str(XML(table, sanitize=False)))
        pdf.write_html(str(XML(deptable, sanitize=False)))
        #pdf.write_html(str(XML(CENTER(chart), sanitize=False)))
        # prepare PDF to download:
        response.headers['Content-Type']='application/pdf'

        #appPath = request.folder
        #pdffile = os.path.join(appPath, 'templates','memberenrollment.pdf')
        #pdf.output(pdffile, dest='F')

        return pdf.output(dest='S')


@auth.requires_login()
def assignedmembers_pdf():
    
    
    reportby = common.getstring(auth.user.first_name) + ' ' + common.getstring(auth.user.last_name)
    response.title = "Assigned Members Report"
    reportdate    = datetime.date.today()
    
    providerid    = 0
    providercode  = None
    providername  = None
    provideremail = None
    
    providerid = int(common.getid(request.vars.providerid))
    rows = db(db.provider.id == providerid).select()
    if(len(rows)>0):
        providercode = rows[0].provider
        providername = rows[0].providername
        provideremail = rows[0].email


    props = db(db.urlproperties.id>0).select()

    if(len(props)>0):
        reportlink = props[0].jasperreporturl + "AssignedMembers.pdf" \
        + "/?j_username=" + props[0].j_username + "&j_password=" + props[0].j_password \
        + "&providerid=" + str(providerid) + "&provider=" + providercode + "&providername=" + providername + "&reportby=" + reportby \

        redirect(reportlink)
    

    return dict()

@auth.requires_login()
def emailproviderwelcomekit():

    providerid    = 0
    providercode  = None
    providername  = None
    provideremail = None

    if(len(request.args)>0):
        providerid = int(request.args[1])
    else:
        raise HTTP(403,"No Provider specified in generating report of assigned members")

    rows = db(db.provider.id == providerid).select()
    if(len(rows)>0):
        providercode = rows[0].provider
        providername = rows[0].providername
        provideremail = rows[0].email
        pdffile = "dummy"
        ret = mail.emailProviderWelcomeKit(db,request,providercode,provideremail,pdffile)
        redirect(URL('provider','emailconfirm',args=[ret,providerid,providername]))

    return dict()


def emailassignedmembers_pdf():

    mode = None
    providerid    = 0
    providercode  = None
    providername  = None
    provideremail = None
    reportdate    = datetime.date.today()
    #reportby      = auth.user.first_name + ' ' + auth.user.last_name
    f = lambda name: name if ((name != "") & (name != None)) else ""
    reportby = f(auth.user.first_name)  + " " + f(auth.user.last_name)

    response.title = "Assigned Members Report"

    if(len(request.args)>0):
        providerid = int(request.args[1])
        mode = request.args[0]
    else:
        raise HTTP(403,"No Provider specified in generating report of assigned members")

    rows = db(db.provider.id == providerid).select()
    if(len(rows)>0):
        providercode = rows[0].provider
        providername = rows[0].providername
        provideremail = rows[0].email
    else:
        raise HTTP(403,"No Provider generating report of assigned members")

    props = db(db.urlproperties.id>0).select()

    if(len(props)>0):
        reportlink = props[0].jasperreporturl + "AssignedMembers.pdf" \
        + "/?j_username=" + props[0].j_username + "&j_password=" + props[0].j_password \
        + "&providerid=" + str(providerid) + "&provider=" + providercode + "&providername=" + providername + "&reportby=" + reportby \

        redirect(reportlink)


    #select patientmember.fname, patientmember.lname, company.company from patientmember
    #left join company on company.id = patientmember.company
    #where patientmember.provider = 96

    #union

    #select patientmemberdependants.fname, patientmemberdependants.lname,company.company from patientmemberdependants
    #left join patientmember on patientmemberdependants.patientmember  = patientmember.id
    #left join company on company.id = patientmember.company
    #where patientmember.provider = 96


    #sql = " SELECT 'P' As pattype, patientmember.patientmember, patientmember.fname, patientmember.lname, patientmember.cell, patientmember.dob,patientmember.email,patientmember.enrollmentdate,company.company FROM patientmember "
    #sql = sql + " LEFT JOIN company on patientmember.company = company.id "
    #sql = sql + " WHERE patientmember.hmopatientmember = 'T' AND patientmember.is_active = 'T' AND patientmember.provider = " + str(providerid)
    #sql = sql + " UNION "
    #sql = sql + " SELECT 'D' AS pattype, patientmember.patientmember, patientmemberdependants.fname, patientmemberdependants.lname, patientmember.cell, patientmemberdependants.depdob as dob,patientmember.email,patientmember.enrollmentdate,company.company from patientmemberdependants"
    #sql = sql + " left join patientmember on patientmemberdependants.patientmember  = patientmember.id "
    #sql = sql + " left join company on company.id = patientmember.company  "
    #sql = sql + " WHERE patientmember.hmopatientmember = 'T' AND  patientmember.is_active = 'T' AND patientmember.provider = " + str(providerid)
    #sql = sql + " ORDER BY lname"

    sql = " SELECT * FROM vw_assignedmembers WHERE vw_assignedmembers.hmopatientmember = 'T' "
    sql = sql + " AND vw_assignedmembers.is_active = 'T' AND vw_assignedmembers.provider = " + str(providerid)
    sql = sql + " ORDER BY company,patientmember, pattype DESC"


    ds = db.executesql(sql)
    count = len(ds)

    head0 = THEAD(TR(TH("Report Date",_width="20%"),
                     TH("Provider",_width="60%"),
                     TH("Assigned Patients",_width="20%"),
                     _bgcolor="#A0A0A0"))

    rows0 = []

    rows0.append(TR(TD(reportdate, _align="left"),
                          TD(providername,_align="left"),
                          TD(str(count),_align="left"),
                          _bgcolor="#FFFFFF"))

    body0 = TBODY(*rows0)
    table0 = TABLE(*[head0,body0],
              _border="1", _align="center", _width="100%")



    # define header and footers:
    head = THEAD(TR(
                     TH(" ",_width="2%"),
                     TH("Member",_width="12%"),
                     TH("First Name",_width="15%"),
                     TH("Last Name",_width="15%"),
                     TH("Dob",_width="9%"),
                     TH("Cell",_width="10%"),
                     TH("Email",_width="20%"),
                     TH("Enroll Date",_width="9%"),
                     TH("Company",_width="8%"),
                     _bgcolor="#A0A0A0"))



    rows = []
    for i in xrange(0,len(ds)):
            col = i % 2 and "#F0F0F0" or "#FFFFFF"
            rows.append(TR(

                           TD(ds[i][0], _align="left"),
                           TD(ds[i][1], _align="left"),
                           TD(ds[i][2], _align="left"),
                           TD(ds[i][3], _align="left"),
                           TD(ds[i][5], _align="left"),
                           TD(ds[i][4], _align="left"),
                           TD(ds[i][6], _align="left"),
                           TD(ds[i][7], _align="left"),
                           TD(ds[i][11], _align="left"),
                           _bgcolor=col))

    # make the table object
    body = TBODY(*rows)
    table = TABLE(*[head,body],
                  _border="1", _align="center", _width="100%")


    from gluon.contrib.pyfpdf import FPDF, HTMLMixin

    # create a custom class with the required functionalities
    class MyFPDF(FPDF, HTMLMixin):
        def header(self):
            "hook to draw custom page header (logo and title)"
            #logo=os.path.join(request.env.web2py_path,"gluon","contrib","pyfpdf","tutorial","logo_pb.png")
            #self.image(logo,10,8,33)
            self.set_text_color(0,0,0)
            self.set_font('Courier','B',10)
            self.cell(40) # padding
            self.cell(100,10,response.title,1,0,'C')
            self.ln(5)

        def footer(self):
            "hook to draw custom page footer (printing page numbers)"
            self.set_y(-15)
            self.set_font('Arial','I',8)
            txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(0,10,txt,0,0,'C')

    objfpdf = FPDF('L', 'mm', 'A4')
    pdf=MyFPDF()
    pdf.def_orientation='L'
    pdf.w_pt=pdf.fh_pt
    pdf.h_pt=pdf.fw_pt
    #pdf.cur_orientation = 'L'
    #pdf.def_orientation = 'L'

    #pdf = FPDF('L','mm','A4')
    # create a page and serialize/render HTML objects
    pdf.set_text_color(0,0,0)
    pdf.set_font('Times', '',  8)
    pdf.add_page('L')
    #pdf.set_text_color(255,0,0)
    #pdf.set_font('Times', '',  8)
    #pdf.set_stretching(50.0)
    pdf.write_html(str(XML(table0, sanitize=False)))
    pdf.write_html(str(XML(table, sanitize=False)))
    #pdf.write_html(str(XML(CENTER(chart), sanitize=False)))
    # prepare PDF to download:
    response.headers['Content-Type']='application/pdf'

    appPath = request.folder
    filename = providercode + "_" + 'assignedmembers.pdf'
    pdffile = os.path.join(appPath, 'private',filename)
    pdf.output(pdffile, dest='F')

    if(mode == 'e'):
        ret = mail.emailAssignedMembers(db,request,providercode,provideremail,pdffile)
        redirect(URL('provider','assignedmembersconfirm',args=[ret,providerid,providername]))
    else:
        return pdf.output(dest='S')

@auth.requires_login()
def enrollmentstatusreportcsv():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Enrollement Stauts Report"
    
    companyid = int(common.getid(request.vars.companyid))
    status  = request.vars.status
    startdt = request.vars.startdt
    enddt   = request.vars.enddt
    is_active = bool(request.vars.is_active)
    
    left = [db.company.on(db.webmember.company==db.company.id),\
            db.provider.on(db.webmember.provider == db.provider.id),\
            db.hmoplan.on(db.webmember.hmoplan == db.hmoplan.id)\
           ]

    links = None

    field_id = db.company.id

    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)

    orderby =  db.webmember.webenrollcompletedate|db.company.company

    query = None
    if(status == 'ALL'):
        if(companyid == 0):
            query = (\
                     (db.webmember.webenrollcompletedate >= startdt) & \
                     (db.webmember.webenrollcompletedate <= enddt) & \
                     (db.webmember.is_active == is_active)\
                    )
        else:
            query = ((db.company.id == companyid) & \
                     (db.webmember.webenrollcompletedate >= startdt) & \
                     (db.webmember.webenrollcompletedate <= enddt) & \
                     (db.webmember.is_active == is_active)\
                    )
    else:
        if(companyid == 0):
            query = (\
                     (db.webmember.status == status) & \
                     (db.webmember.webenrollcompletedate >= startdt) & \
                     (db.webmember.webenrollcompletedate <= enddt) & \
                     (db.webmember.is_active == is_active)\
                    )
        else:
            query = ((db.company.id == companyid) & \
                     (db.webmember.status == status) & \
                     (db.webmember.webenrollcompletedate >= startdt) & \
                     (db.webmember.webenrollcompletedate <= enddt) & \
                     (db.webmember.is_active == is_active)\
                    )



    



    fields=(db.company.company,db.webmember.status,db.webmember.webmember,db.webmember.groupref,\
            db.webmember.fname,db.webmember.lname,db.provider.provider,db.webmember.webenrollcompletedate,\
            db.provider.providername,db.hmoplan.hmoplancode,db.webmember.cell,db.webmember.email,\
            db.webmember.address1,db.webmember.address2,db.webmember.address3,db.webmember.city,db.webmember.st,db.webmember.pin
            )


    
    headers={

        'company.company':'Group(Company)',
        'webmember.status':'Status',
        'webmember.webenrollcompletedate':'Enroll Date',
        'webmember.webmember':'Member',
        'webmember.groupref':'Employee ID',
        'webmember.fname': 'First Name',
        'webmember.lname': 'Last Name',
        'webmember.cell':'Cell',
        'webmember.email':'Email',
        'provider.providername':'Provider',
        'hmoplan.hmoplancode':'Plan',
        'webmember.pin':'Pin',
        'webmember.st':'State',
        'webmember.city':'City',
        'webmember.address1':'Address1',
        'webmember.address2':'Address2',
        'webmember.address3':'Address3'
                }

    formB = SQLFORM.grid(query=query,
                         field_id = field_id ,
                         headers=headers,
                         fields=fields,
                         links=links,
                         left=left,
                         orderby=orderby,
                         exportclasses=exportlist,
                         links_in_grid=False,
                         searchable=False,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                        )
    returnurl = URL('default','index')
    return dict(username=username, returnurl=returnurl,formB=formB, formheader=formheader,companyid=companyid,startdt=startdt,enddt=enddt,is_active=is_active,status=status)


#IB 05292016
@auth.requires_login()
def enrollmentstatusreportparams():

    username = auth.user.first_name + ' ' + auth.user.last_name

    company     = None
    companyname = None
    companyid = 0

    #f = lambda name: name if ((name != "") & (name != None)) else ""
    reportby = common.getstring((auth.user.first_name))  + " " + common.getstring((auth.user.last_name))
    
    db.enrollmentstatusreportparams.status.default = "ALL"
    db.enrollmentstatusreportparams.company.default = 1
    form = SQLFORM(db.enrollmentstatusreportparams,submit_button = 'PDF Report>>')


    sql = "SELECT 1 AS companyid, '--Select All--' AS companyname "
    sql = sql + " UNION "
    sql = sql + "SELECT company.id AS companyid, CONCAT(company.name,' ', company.company) AS companyname from company "
    sql = sql + " WHERE is_active='T'"


    dscompany = db.executesql(sql)
    
    
    
    #form = SQLFORM.factory(
           #Field('company', default='', requires=IS_IN_DB(db(db.company.is_active == True), db.company.id, '%(name)s (%(company)s)')),
           #Field('status', 'string',  label='Status',requires = IS_IN_SET(ALLSTATUS),default='ALL'),
           #Field('startdt', 'date', widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='From Date',requires=IS_DATE(format=('%d/%m/%Y')),length=20,default=request.now),
           #Field('enddt', 'date', widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),label='To Date',requires=IS_DATE(format=('%d/%m/%Y')),length=20,default=request.now),
           #Field('is_active', 'boolean', default = True)
       #)    

    if form.validate():
    #if form.accepts(request,session,keepvalues=True):
        ##get company code and name
        if((form.vars.companyname == '') | (form.vars.companyname == '--Select All--')):
            companyid = 0
        else:
            rows = db((db.company.id == int(form.vars.company)) & (db.company.is_active == True)).select()

            if(len(rows)>0):
                companyid = rows[0].id
                company = rows[0].company
                companyname = rows[0].name
            else:
                raise HTTP(400,"No Company")

        if(form.vars.is_active == True):
            flag = 'T'
        else:
            flag  = 'F'

        if(form.request_vars.action == 'csv'):

            redirect(URL('report','enrollmentstatusreportcsv',\
                         vars=dict(companyid=companyid, status=form.vars.status,startdt=form.vars.startdt,enddt=form.vars.enddt,is_active=form.vars.is_active)))
        #else:
            #props = db(db.urlproperties.id>0).select()

            #if(len(props)>0):

                #reportlink = props[0].jasperreporturl + "EnrollmentStatus.pdf" \
                #+ "/?j_username=" + props[0].j_username + "&j_password=" + props[0].j_password \
                #+ "&company=" + form.vars.company + "&companycode=" + company + "&companyname=" + companyname \
                #+ "&status=" + form.vars.status + "&startDate=" + str(form.vars.startdt) + "&endDate=" + str(form.vars.enddt) \
                #+ "&is_active=" + flag + "&reportby=" + reportby + "&attempting=0&completed=0&enrolled=0"

                #redirect(reportlink)
            #else:
               #raise HTTP(400,"No Report URL")

    returnurl=URL('default','index')
    return dict(username=username,returnurl=returnurl,form=form,formheader="Enrollment Status Report Parameters",dscompany=dscompany)

#IB 05292016
@auth.requires_login()
def xassignedmembersreportparam():
    
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    formheader = "Parameters for Assigned Members Report"

    providerid = int(common.getid(request.vars.providerid))
    if(providerid == 0):
        providerid = 1
    
    today = datetime.date.today()
    year  = datetime.timedelta(days=365)
    onedaydelta = datetime.timedelta(days=1)

    sql = "SELECT 1 AS providerid, '--Select--' AS providername "
    sql = sql + " UNION "
    sql = sql + "SELECT provider.id AS providerid, CONCAT(provider.providername,' ', provider.provider) AS providername from provider "
    sql = sql + " WHERE is_active='T'"


    dsprovider = db.executesql(sql)

    sql = "Select 'All', 'Active', 'Inactive'"
    dsstatus = db.executesql(sql)

    db.providercapitationreportparam.startdate.default = datetime.date(today.year, today.month, 1)
    db.providercapitationreportparam.enddate.default = datetime.date(today.year, today.month, calendar.monthrange(today.year,today.month)[1])
    db.providercapitationreportparam.provider.default = providerid
    
    form = SQLFORM(db.providercapitationreportparam,submit_button = 'Export CSV>>')


    if form.process().accepted:
        providerid = form.vars.provider
        startdate = form.vars.startdate
        enddate = form.vars.enddate
        memberstatus = form.vars.memberstatus
        if(form.vars.is_active == True):
            is_active = 'T'
        else:
            is_active  = 'F'

        # display members
        redirect(URL('report','assignedmembersreport', args=[providerid,startdate,enddate,is_active,memberstatus]))

    returnurl=URL('default','index')
    return dict(username=username,returnurl=returnurl,form=form,formheader=formheader,dsprovider=dsprovider,dsstatus=dsstatus)

#IB 05292016
@auth.requires_login()
def assignedmembersreportparam():
    
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    formheader = "Parameters for Assigned Members Report"

    providerid = int(common.getid(request.vars.providerid))
    if(providerid == 0):
        providerid = 1
    
    today = datetime.date.today()
    year  = datetime.timedelta(days=365)
    onedaydelta = datetime.timedelta(days=1)

    form = SQLFORM.factory(
           Field('provider',  default=providerid, requires=IS_IN_DB(db(db.provider.is_active == True), db.provider.id, '%(providername)s %(provider)s')),
           Field('startdate', requires=IS_DATE(format=('%d/%m/%Y')),length=20,default=datetime.date(today.year, today.month, 1)),
           Field('enddate',   requires=IS_DATE(format=('%d/%m/%Y')),length=20,default=datetime.date(today.year, today.month, calendar.monthrange(today.year,today.month)[1])),
           Field('memberstatus','string', default="Active")
       )
      
       
    #submit = form.element('input',_type='submit')
    #submit['_style'] = 'display:none;'
       

    #sql = "SELECT 1 AS providerid, '--Select--' AS providername "
    #sql = sql + " UNION "
    #sql = sql + "SELECT provider.id AS providerid, CONCAT(provider.providername,' ', provider.provider) AS providername from provider "
    #sql = sql + " WHERE is_active='T'"


    #dsprovider = db.executesql(sql)

    sql = "Select 'All', 'Active', 'Inactive'"
    dsstatus = db.executesql(sql)

    #db.providercapitationreportparam.startdate.default = datetime.date(today.year, today.month, 1)
    #db.providercapitationreportparam.enddate.default = datetime.date(today.year, today.month, calendar.monthrange(today.year,today.month)[1])
    #db.providercapitationreportparam.provider.default = providerid
    
    #form = SQLFORM(db.providercapitationreportparam,submit_button = 'Export CSV>>')


    if form.process().accepted:
        providerid = form.vars.provider
        startdate = form.vars.startdate
        enddate = form.vars.enddate
        memberstatus = form.vars.memberstatus
        if(form.vars.is_active == True):
            is_active = 'T'
        else:
            is_active  = 'F'

        # display members
        redirect(URL('report','assignedmembersreport', args=[providerid,startdate,enddate,is_active,memberstatus]))

    returnurl=URL('default','index')
    return dict(username=username,returnurl=returnurl,form=form,formheader=formheader,dsstatus=dsstatus,providerid=providerid)

def assignedmembersreport():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Assigned Members Report"



    if(len(request.args)>0):  # called with URL Params
        providerid = request.args[0]
        startdate = request.args[1]
        enddate = request.args[2]
        is_active = request.args[3]
        memberstatus = request.args[4]
        session.providerid = providerid
        session.startdate = startdate
        session.enddate = enddate
        session.is_active = is_active
        session.memberstatus = memberstatus
    elif (len(request.vars)>0):
        providerid = session.providerid
        startdate = session.startdate
        enddate = session.enddate
        is_active = session.is_active
        memberstatus = session.memberstatus
    else:
        providerid = 0
        startdate = datetime.date.today()
        enddate  = datetime.timedelta(days=365)
        memberstatus = 'all'
        is_active = True


    left = None

    links = None

    field_id = db.vw_assignedmembers.patientmember

    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)

    query = None
    
    
    query = ((db.vw_assignedmembers.hmopatientmember == True) & (db.vw_assignedmembers.provider == providerid))    
    if(memberstatus.lower() == 'active'):
        query = ((db.vw_assignedmembers.hmopatientmember == True) & (db.vw_assignedmembers.is_active == True)& (db.vw_assignedmembers.provider == providerid))
    elif(memberstatus.lower() == 'inactive'):
        query = ((db.vw_assignedmembers.hmopatientmember == True) & (db.vw_assignedmembers.is_active == False)& (db.vw_assignedmembers.provider == providerid))


    orderby = db.vw_assignedmembers.patientmember | ~db.vw_assignedmembers.pattype

    fields=(db.vw_assignedmembers.pattype,db.vw_assignedmembers.patientmember,db.vw_assignedmembers.groupref,\
                db.vw_assignedmembers.fname,db.vw_assignedmembers.lname,db.vw_assignedmembers.dob,db.vw_assignedmembers.cell,db.vw_assignedmembers.email,\
                db.vw_assignedmembers.enrollmentdate,db.vw_assignedmembers.premenddt,
                db.vw_assignedmembers.company,db.vw_assignedmembers.hmoplan,\
                db.vw_assignedmembers.is_active,db.vw_assignedmembers.hmopatientmember)
        
    db.vw_assignedmembers.provider.writeable = False
    db.vw_assignedmembers.is_active.writeable = False
    db.vw_assignedmembers.is_active.readable = False
    db.vw_assignedmembers.hmopatientmember.writeable = False
    db.vw_assignedmembers.hmopatientmember.readable = False
    db.vw_assignedmembers.provider.readable = False
    db.vw_assignedmembers.provider.writable = False

    headers={'vw_assignedmembers.pattype': 'Type',
             'vw_assignedmembers.patientmember':'Member ID',
           'vw_assignedmembers.groupref': 'Empl. ID',
           'vw_assignedmembers.fname': 'First Name',
           'vw_assignedmembers.lname': 'Last Name',
           'vw_assignedmembers.dob':'DOB',
           'vw_assignedmembers.cell':'Cell',
           'vw_assignedmembers.email':'Email',
           'vw_assignedmembers.enrollmentdate':'Enrollment Date',
           'vw_assignedmembers.premenddt':'Prem. End Date',
           'vw_assignedmembers.hmoplan':'Plan',
           'vw_assignedmembers.company':'Group(Company)',
              }


    formB = SQLFORM.grid(query=query,
                         field_id = field_id ,
                         headers=headers,
                         fields=fields,
                         links=links,
                         left=left,
                         orderby=orderby,
                         exportclasses=exportlist,
                         links_in_grid=False,
                         searchable=True,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                        )


    ## redirect on Items, with PO ID and return URL
    returnurl = URL('default','index')
    return dict(username=username,returnurl=returnurl,formB=formB, formheader=formheader,providerid=providerid,startdate=startdate,enddate=enddate,is_active=is_active,memberstatus=memberstatus)

#IB 05292016
@auth.requires_login()
def memberreportparams():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    

    company     = None
    companyname = None
    companyid = 0

    f = lambda name: name if ((name != "") & (name != None)) else ""
    reportby = f(auth.user.first_name)  + " " + f(auth.user.last_name)
    db.enrollmentstatusreportparams.status.default = "ALL"
    db.enrollmentstatusreportparams.company.default = 1
    db.enrollmentstatusreportparams.memberonly.default= False
    form = SQLFORM(db.enrollmentstatusreportparams)


    sql = "SELECT 1 AS companyid, '--Select All--' AS companyname "
    sql = sql + " UNION "
    sql = sql + "SELECT company.id AS companyid, CONCAT(company.name,' ', company.company) AS companyname from company "
    sql = sql + " WHERE is_active='T'"


    dscompany = db.executesql(sql)

    if form.validate():

        #get company code and name
        if((form.vars.companyname == '') | (form.vars.companyname == '--Select All--')):
            companyid = 0
        else:
            rows = db((db.company.id == int(form.vars.company)) & (db.company.is_active == True)).select()

            if(len(rows)>0):
                companyid = rows[0].id
                company = rows[0].company
                companyname = rows[0].name
            else:
                raise HTTP(400,"No Company")

        if(form.vars.is_active == True):
            flag = 'T'
        else:
            flag  = 'F'

        if(form.request_vars.action == 'csv'):

            redirect(URL('report','memberreportcsv',\
                         args=[companyid,form.vars.status,form.vars.startdt,form.vars.enddt,form.vars.is_active,form.vars.memberonly]))
    returnurl = URL('default','index')
    return dict(username=username,returnurl=returnurl,form=form,formheader="Member Report Parameters",dscompany=dscompany)

@auth.requires_login()
def memberreportcsv():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Member Report"
    if(len(request.args) > 0):
        companyid = int(request.args[0])
        status = request.args[1]
        startdt = request.args[2]
        enddt = request.args[3]
        if(request.args[4] == "True"):
            is_active = True
        else:
            is_active = False
            
        if(request.args[5] == "True"):
            memberonly = 'P'
        else:
            memberonly = ''
        
        session.companyid=companyid
        session.status=status
        session.startdt=startdt
        session.enddt=enddt
        session.is_active=is_active
        session.memberonly = memberonly

    elif (len(request.vars)>0):
        companyid = session.companyid
        status = session.status
        startdt = session.startdt
        enddt = session.enddt
        is_active = session.is_active
        memberonly  = session.memberonly
        

    left = None

    links = None

    field_id = db.vw_member.patientmember

    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)

    #orderby =  db.vw_member.patientmember
    orderby =  db.vw_member.premstartdt | db.vw_member.patientmember | ~db.vw_member.pattype

    if(memberonly == 'P'):
        query = ((db.vw_member.is_active == is_active) & (db.vw_member.chractive == True) &  (db.vw_member.pattype == 'P'))
    else:
        query = ((db.vw_member.is_active == is_active)  & (db.vw_member.chractive == True)  )
    if(status == 'ALL'):
        if(companyid == 0):
            query = query & (\
                     (db.vw_member.premstartdt >= startdt) & \
                     (db.vw_member.premstartdt <= enddt) \
                    )
        else:
            query = query & ((db.vw_member.companyid == companyid) & \
                     (db.vw_member.premstartdt >= startdt) & \
                     (db.vw_member.premstartdt <= enddt) 
                    )
    else:
        if(companyid == 0):
            query = query & (\
                     (db.vw_member.status == status) & \
                     (db.vw_member.premstartdt >= startdt) & \
                     (db.vw_member.premstartdt <= enddt) 
                    )
        else:
            query = query & ((db.vw_member.companyid == companyid) & \
                     (db.vw_member.status == status) & \
                     (db.vw_member.premstartdt >= startdt) & \
                     (db.vw_member.premstartdt <= enddt)
                    )



    fields=(
        db.vw_member.pattype,db.vw_member.patientmember,  db.vw_member.groupref, db.vw_member.fname, db.vw_member.mname, db.vw_member.lname,
        db.vw_member.dob,  db.vw_member.cell,  db.vw_member.telephone  ,db.vw_member.email,  db.vw_member.status,
        db.vw_member.address1,  db.vw_member.address2,  db.vw_member.address3,  db.vw_member.city,  db.vw_member.pin,
        db.vw_member.enrollmentdate,  db.vw_member.premstartdt, db.vw_member.premenddt,db.vw_member.relation,
        db.vw_member.dependants,  db.vw_member.amount,  db.vw_member.membercap,  db.vw_member.dependantcap,
        db.vw_member.provider,  db.vw_member.providername,  db.vw_member.provaddress1,  db.vw_member.provaddress2,
        db.vw_member.provaddress3,  db.vw_member.provcity,  db.vw_member.provpin,
        db.vw_member.provemail,  db.vw_member.provtelephone,   db.vw_member.company,
        db.vw_member.hmoplancode,  db.vw_member.planname,  db.vw_member.agent,  db.vw_member.agentname,
        db.vw_member.agentcommission, db.vw_member.paymentdate
    )


    db.vw_member.terminationdate.writeable = False
    db.vw_member.companyid.writeable = False
    db.vw_member.webmemberid.writeable = False
    db.vw_member.paymentdate.writeable = False
    db.vw_member.is_active.writeable = False


    headers={
        'vw_member.pattype':'P_D',
        'vw_member.patientmember':'Member',
        'vw_member.groupref':'Employee ID',
        'vw_member.fname':'First',
        'vw_member.mname':'Mid.',
        'vw_member.lname':'Last',
        'vw_member.dob':'DOB',
        'vw_member.cell':'Cell',
        'vw_member.telephone':'Tel.',
        'vw_member.email':'Email',
        'vw_member.status':'Status',
        'vw_member.address1':'Addr1',
        'vw_member.address2':'Addr2',
        'vw_member.address3':'Addr3',
        'vw_member.city':'City',
        'vw_member.pin':'Pin',
        'vw_member.enrollmentdate':'Enroll. Dt.',
        'vw_member.premstartdt':'Prem Start. Dt.',
        'vw_member.premenddt':'Prem.End Dt.',
        'vw_member.relation':'Relation',
        'vw_member.dependants':'Dependants',
        'vw_member.amount':'Amount',
        'vw_member.membercap':'MemberCap',
        'vw_member.dependantcap':'Dep.Cap',
        'vw_member.provider':'Provider',
        'vw_member.providername':'Name',
        'vw_member.provaddress1':'Addr1',
        'vw_member.provaddress2':'Addr2',
        'vw_member.provaddress3':'Addr3',
        'vw_member.provcity':'City',
        'vw_member.provpin':'Pin',
        'vw_member.provemail':'Email',
        'vw_member.provtelephone':'Tel.',
        'vw_member.company':'Company',
        'vw_member.hmoplancode':'Plan',
        'vw_member.planname':'Plan Name',
        'vw_member.agent':'Agent',
        'vw_member.agentname':'Agent Name',
        'vw_member.agentcommission':'Comm.',
        'vw_member.paymentdate':'Pay Date'
    }

    formB = SQLFORM.grid(query=query,
                         field_id = field_id ,
                         headers=headers,
                         fields=fields,
                         links=links,
                         left=left,
                         orderby=orderby,
                         exportclasses=exportlist,
                         links_in_grid=False,
                         searchable=False,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                        )
    returnurl=URL('default','index')
    return dict(formB=formB, username=username, returnurl=returnurl,formheader=formheader,companyid=companyid,startdt=startdt,enddt=enddt,is_active=is_active,status=status)

@auth.requires_login()
def paymenttxlogreportparams():
    if(auth.is_logged_in()):
        username = auth.user.first_name + ' ' + auth.user.last_name
    else:
        raise HTTP(400, "Error: User not logged - paymenttxlogreportparams")    
    return dict(username=username)

def getpremiumenddate(premiumstartdt):
    day = timedelta(days=1)
    premiumenddt = premiumstartdt - day
    return premiumenddt


def getnewrenewaldate(currentrenewaldate):

    if(calendar.isleap(currentrenewaldate.year + 1)):
            if(currentrenewaldate > datetime.date(currentrenewaldate.year,02,28)):
                year            = timedelta(days=366)
            else:
                year = timedelta(days=365)
    elif(calendar.isleap(currentrenewaldate.year)):
            if(currentrenewaldate <= datetime.date(currentrenewaldate.year,02,29)):
                year            = timedelta(days=366)
            else:
                year            = timedelta(days=365)
    else:
        year  = timedelta(days=365)

    newrenewaldate  = (currentrenewaldate + year)

    return newrenewaldate

def fixpremiumdates():
    
    

    
    members = db((db.patientmember.premstartdt < db.patientmember.enrollmentdate) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    members2 = len(members)
    for member in members:
        db((db.patientmember.id == member.id) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).update(premstartdt=member.enrollmentdate)    
        
    members = db((db.patientmember.id > 0) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    members1 = len(members)
    for member in members:
        newrenewaldt = getnewrenewaldate(member.premstartdt)
        newpremenddt = getpremiumenddate(newrenewaldt)
        db((db.patientmember.id == member.id) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).update(premenddt = newpremenddt)
    
    

    
    return dict(members1=members1, members2=members2)


def providerrevenuereport():

    
    
   
    yearbreakdown = request.vars.yearbreakdown
    status = request.vars.status
    

    username = ""
    formheader = "Provider List"
    
    if(status == "all"):
        query = ((db.provider.is_active == True)|(db.provider.is_active == False))
    elif(status == "active"):
        query = (db.provider.is_active == True)
    else:
        query = (db.provider.is_active == False)
    
    
        
    fields=(db.provider.provider,db.provider.providername, db.provider.practicename,\
            db.provider.address1, db.provider.address2, \
            db.provider.address3, \
            db.provider.city, db.provider.st, db.provider.pin, db.provider.assignedpatientmembers,db.provider.specialization,
            db.provider.pa_pan, db.provider.registration, db.provider.cell, db.provider.email, db.provider.pa_approvedon,
            db.provider.pa_accepted,db.provider.pa_approved,db.vw_providertotalrevenue.earnedrevenue)
      
  
    headers={'provider.provider':'Provider',
             'provider.providername':'Name',
             'provider.practicename' : 'Practice',
             'provider.address1' : 'address1',
             'provider.address2' : 'address2',
             'provider.address3' : 'address3',
             'provider.city':'City',
             'provider.st':'State',
             'provider.pin' : 'PIN',
             'provider.pa_pan' : 'PAN',
             'provider.registration' : 'RegNo',
             'provider.specialization' : 'Splz',
             'provider.assignedpatientmembers' : 'Members',
             'provider.cell' : 'Cell',
             'provider.emial' : 'Email',
             'provider.pa_accepted':'Acpt',
             'provider.pa_approved': 'Apr',
             'provider.pa_approvedon': 'Appr.On',
             'vw_providertotalrevenue.earnedrevenue': 'Earned Revenue'
            
               }
  
  
    maxtextlengths = {'provider.email':12,'provider.cell':2,'provider.registration':2}
      
    orderby = (db.provider.provider)
  
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    links = None  
    
    left =    [db.vw_providertotalrevenue.on(db.vw_providertotalrevenue.providerid==db.provider.id)]
    
    form = SQLFORM.grid(query=query,
                 headers=headers,
                 fields=fields,
                 links=links,
                 maxtextlengths = maxtextlengths,
                 orderby=orderby,
                 exportclasses=exportlist,
                 paginate=10,
                 left=left,
                 links_in_grid=True,
                 searchable=True,
                 create=False,
                 deletable=False,
                 editable=False,
                 details=False,
                 user_signature=True
                )            
  
      #searchable=lambda f, k: db.provider.providername.like("%" + k + "%") | db.provider.provider.like("%" + k + "%")
  
      #search_input = form.element('#w2p_keywords')
      #search_input.attributes.pop('_onfocus')   
  
    returnurl=URL('default','index')
    return dict(username=username,returnurl=returnurl,form=form,formheard=formheader)


@auth.requires_login()
def providerrevenuereportparams():
    
   
    
    
    form = SQLFORM.factory(Field('year','string',default=""),
                           Field('yearbreakdown','string'),
                           Field('status','status'))
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Export CSV;'
    
    if form.process().accepted:
        redirect(URL('report','providerrevenuereport', vars=dict(status=form.vars.status,yearbreakdown=form.vars.yearbreakdown)))
        
    returnurl = URL('default','index')
    return dict(returnurl=returnurl,form=form,username="")



def memberdatareport():

    
    
   
    status = request.vars.status
    

    username = ""
    formheader = "Member Data Report"
    
    if(status == "all"):
        query = ((db.vw_memberdata.is_active == True)|(db.vw_memberdata.is_active == False))
    elif(status == "active"):
        query = (db.vw_memberdata.is_active == True)
    else:
        query = (db.vw_memberdata.is_active == False)
    
    
        
    fields=(db.vw_memberdata.patientmember , 
            db.vw_memberdata.patienttype , 
            db.vw_memberdata.fname , 
            db.vw_memberdata.mname , 
            db.vw_memberdata.lname , 
            db.vw_memberdata.address1 , 
            db.vw_memberdata.address2 , 
            db.vw_memberdata.address3 , 
            db.vw_memberdata.city , 
            db.vw_memberdata.st , 
            db.vw_memberdata.pin , 
            db.vw_memberdata.cell , 
            db.vw_memberdata.email , 
            db.vw_memberdata.dob, 
            db.vw_memberdata.gender , 
            db.vw_memberdata.relation , 
            db.vw_memberdata.status , 
            db.vw_memberdata.premium, 
            db.vw_memberdata.renewed,
            db.vw_memberdata.upgraded,
            db.vw_memberdata.premstartdt,
            db.vw_memberdata.premenddt,
            db.vw_memberdata.hmoplanname , 
            db.vw_memberdata.hmoplancode , 
            db.vw_memberdata.companycode , 
            db.vw_memberdata.provider , 
            db.vw_memberdata.provaddress1 , 
            db.vw_memberdata.provaddress2 , 
            db.vw_memberdata.provaddress3 , 
            db.vw_memberdata.provcity , 
            db.vw_memberdata.provst , 
            db.vw_memberdata.provpin , 
            db.vw_memberdata.provcell , 
            db.vw_memberdata.provemail, 
            db.vw_memberdata.is_active
           
            )

    headers = {
        'vw_memberdata.patientmember ':'MDP ID' ,
        
        'vw_memberdata.patienttype ':'Patient Type', 
        'vw_memberdata.fname ':'First' ,
        'vw_memberdata.mname ':'Middle' ,
        'vw_memberdata.lname ':'Last' ,
        'vw_memberdata.address1 ':'Address1' ,
        'vw_memberdata.address2 ':'Address2' ,
        'vw_memberdata.address3 ':'Address3' ,
        'vw_memberdata.city ':'City' ,
        'vw_memberdata.st ':'St' ,
        'vw_memberdata.pin ':'Pin' ,
        'vw_memberdata.cell ':'Cell' ,
        'vw_memberdata.email ':'Email' ,
        'vw_memberdata.dob':'DOB' ,
        'vw_memberdata.gender ':'Gender' ,
        'vw_memberdata.relation ':'Relation' ,
        'vw_memberdata.status ':'Status' ,
        'vw_memberdata.premium':'Premium' ,
        'vw_memberdata.renewed':'Renewed',
        'vw_memberdata.upgraded':'Upgraded',
        
        'vw_memberdata.premstartdt':'Prem Start',
        'vw_memberdata.premenddt':'Prem End',
        'vw_memberdata.hmoplanname ':'Plan Name' ,
        'vw_memberdata.hmoplancode ':'Plan Code' ,
        'vw_memberdata.companycode ':'Company' ,
        'vw_memberdata.provider ':'Provider' ,
        'vw_memberdata.provaddress1 ':'ProvAddr1' ,
        'vw_memberdata.provaddress2 ':'ProvAddr2' ,
        'vw_memberdata.provaddress3 ':'ProvAddr3' ,
        'vw_memberdata.provcity ':'ProvCity' ,
        'vw_memberdata.provst ':'ProvSt' ,
        'vw_memberdata.provpin ':'ProvPin' ,
        'vw_memberdata.provcell ':'ProvCell' ,
        'vw_memberdata.provemail ':'ProvEmail' ,
        'vw_memberdata.is_active':'Active'
    }

  
  
    
      
   
  
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    links = None  
    left = None
    
    
    
    form = SQLFORM.grid(query=query,
                 headers=headers,
                 fields=fields,
                 exportclasses=exportlist,
                 paginate=10,
                 searchable=False,
                 create=False,
                 deletable=False,
                 editable=False,
                 details=False,
                 user_signature=True
                )            
  
     
  
   
    returnurl=URL('default','index')
    return dict(username=username,returnurl=returnurl,form=form,formheard=formheader)

def memberpaymentreport():

    
    
   
    status = request.vars.status
    

    username = ""
    formheader = "Member Payment Report"
    
    query = (db.vw_memberpaymentreport.id > 0)
    #if(status == "all"):
        #query = ((db.vw_memberpaymentreport.is_active == True)|(db.vw_memberpaymentreport.is_active == False))
    #elif(status == "active"):
        #query = (db.vw_memberpaymentreport.is_active == True)
    #else:
        #query = (db.vw_memberpaymentreport.is_active == False)
    
    
        
    fields=(db.vw_memberpaymentreport.patientmember , 
            db.vw_memberpaymentreport.patienttype , 
            db.vw_memberpaymentreport.fname , 
            db.vw_memberpaymentreport.mname , 
            db.vw_memberpaymentreport.lname , 
            db.vw_memberpaymentreport.city , 
            db.vw_memberpaymentreport.st , 
            db.vw_memberpaymentreport.pin , 
            db.vw_memberpaymentreport.cell , 
            db.vw_memberpaymentreport.email , 
            db.vw_memberpaymentreport.provider , 
            db.vw_memberpaymentreport.practicename, 
            db.vw_memberpaymentreport.provcity , 
            db.vw_memberpaymentreport.provst , 
            db.vw_memberpaymentreport.provpin , 
            db.vw_memberpaymentreport.provcell , 
            db.vw_memberpaymentreport.provemail, 
            
            db.vw_memberpaymentreport.treatment, 
            db.vw_memberpaymentreport.shortdescription, 
            
            db.vw_memberpaymentreport.paymentdate, 
            db.vw_memberpaymentreport.fppaymenttype, 
            db.vw_memberpaymentreport.fppaymentref, 
            
            
            db.vw_memberpaymentreport.fpinvoice, 
            db.vw_memberpaymentreport.invoiceamount, 
            db.vw_memberpaymentreport.paymentamount, 
            
            db.vw_memberpaymentreport.totaldue
            
            
            
            
           
            )

    headers = {
        'vw_memberpaymentreport.patientmember ':'MDP ID' ,
        
        'vw_memberpaymentreport.patienttype ':'Patient Type', 
        'vw_memberpaymentreport.fname ':'First' ,
        'vw_memberpaymentreport.mname ':'Middle' ,
        'vw_memberpaymentreport.lname ':'Last' ,
        'vw_memberpaymentreport.city ':'City' ,
        'vw_memberpaymentreport.st ':'St' ,
        'vw_memberpaymentreport.pin ':'Pin' ,
        'vw_memberpaymentreport.cell ':'Cell' ,
        'vw_memberpaymentreport.email ':'Email' ,
        'vw_memberpaymentreport.provider ':'Provider' ,
        'vw_memberpaymentreport.provcity ':'ProvCity' ,
        'vw_memberpaymentreport.provst ':'ProvSt' ,
        'vw_memberpaymentreport.provpin ':'ProvPin' ,
        'vw_memberpaymentreport.provcell ':'ProvCell' ,
        'vw_memberpaymentreport.provemail ':'ProvEmail' ,
        'vw_memberpaymentreport.treatment ':'Treatment' ,
        'vw_memberpaymentreport.shortdescription ':'Procedures' ,
        'vw_memberpaymentreport.paymentdate ':'Payment Date' ,        
        'vw_memberpaymentreport.fppaymenttype ':'Payment Mode' ,        
        'vw_memberpaymentreport.fppaymentref ':'Payment Ref' ,        
        'vw_memberpaymentreport.fpinvoice ':'Invoice' ,       
        'vw_memberpaymentreport.invoiceamount ':'Invoice Amt' ,       
        'vw_memberpaymentreport.paymentamount ':'Amt. Paid' ,       
        'vw_memberpaymentreport.totaldue ':'Amt. Due'     
        
        
    }

  
  
    
      
   
  
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
    links = None  
    left = None
    
    
    
    form = SQLFORM.grid(query=query,
                 headers=headers,
                 fields=fields,
                 exportclasses=exportlist,
                 paginate=10,
                 searchable=False,
                 create=False,
                 deletable=False,
                 editable=False,
                 details=False,
                 user_signature=True
                )            
  
     
  
   
    returnurl=URL('default','index')
    return dict(username=username,returnurl=returnurl,form=form,formheard=formheader)



@auth.requires_login()
def memberdatareportparams():
    
   
    
    
    form = SQLFORM.factory(
                           
                           Field('status','status'))
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Export CSV;'
    
    if form.process().accepted:
        redirect(URL('report','memberdatareport', vars=dict(status=form.vars.status)))
        
    returnurl = URL('default','index')
    return dict(returnurl=returnurl,form=form,username="")

@auth.requires_login()
def memberpaymentreportparams():
    
   
    
    
    form = SQLFORM.factory(
                           
                           Field('status','status'))
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Export CSV;'
    
    if form.process().accepted:
        redirect(URL('report','memberpaymentreport', vars=dict(status=form.vars.status)))
        
    returnurl = URL('default','index')
    return dict(returnurl=returnurl,form=form,username="")

@auth.requires_login()
def preregreportparams():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    form = SQLFORM.factory(Field('priority','string'))
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Export CSV;'
    if form.process().accepted:
        redirect(URL('report','preregreportcsv', vars=dict(priority=request.vars.priority)))
        
    returnurl = URL('default','index')
    return dict(username=username,returnurl=returnurl,form=form,formheader="Pre-Register Report Parameters")

@auth.requires_login()
def preregreportcsv():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Pre-Register Report"
    
    priority = request.vars.priority



    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)

    if(priority == 'all'):
        query = ((db.preregister.is_active == True))
    else:
        query = ((db.preregister.priority == priority) & (db.preregister.is_active == True))
    
    


    fields=(
        db.preregister.fname,db.preregister.lname,db.preregister.cell,db.preregister.oemail,db.preregister.pemail,db.preregister.description,db.preregister.priority
    )




    headers={
        'preregister.fname':'First',
        'preregister.lname':'Last',
        'preregister.cell':'Cell',
        'preregister.oemail':'Office Email',
        'preregister.pemail':'Personal Email',
        'preregister.priority':'priority',
        'preregister.description':'Description',
    }

    form = SQLFORM.grid(query=query,
                         headers=headers,
                         fields=fields,
                         exportclasses=exportlist,
                         links_in_grid=False,
                         searchable=False,
                         create=False,
                         deletable=False,
                         editable=False,
                         details=False,
                         user_signature=False
                        )
    returnurl=URL('default','index')
    
    return dict(username=username,formheader=formheader,returnurl=returnurl,form=form)


@auth.requires_login()
def paymentreportparams():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Payment Report"
    providerid = int(common.getid(request.vars.providerid))
    if(providerid == 0):
        providerid = 1
    form = SQLFORM.factory(
        Field('provider',  default=providerid, requires=IS_EMPTY_OR(IS_IN_DB(db(db.provider.is_active == True), db.provider.id, '%(provider)s : %(providername)s'))),
        Field('fromyear', requires = IS_IN_SET(YEAR),length=20,default=request.now.year),
        Field('frommonth', requires=IS_IN_SET(MONTH),length=20,default=months[request.now.month-1]),
        Field('toyear', requires = IS_IN_SET(YEAR),length=20,default=request.now.year),
        Field('tomonth', requires=IS_IN_SET(MONTH),length=20,default=months[request.now.month-1])
    )
   
    
    submit = form.element('input',_type='submit')
    submit['_style'] = 'display:none;'
    
    returnurl=URL('default','index')
    
    if form.accepts(request,session,keepvalues=True):
        providerid = int(common.getid(form.vars.provider))
           
        
        fromyear  = int(common.getid(form.vars.fromyear))
        frommonth = form.vars.month
        toyear  = int(common.getid(form.vars.toyear))
        tomonth = form.vars.tomonth
        
        monthid = 1

        if(frommonth == ""):
            fromstartdate = datetime.date(fromyear, 1,1)
            fromenddate = datetime.date(fromyear, 12,31)
        else:
            for counter, value in enumerate(months,1):
                if(value == frommonth):
                    monthid = counter
                    break;
            fromstartdate = datetime.date(fromyear, monthid,1)
            if((monthid == 1) | (monthid == 3)| (monthid == 5)| (monthid == 7)| (monthid == 8)| (monthid == 10)| (monthid == 12)):
                fromenddate = datetime.date(fromyear, monthid,31)
            elif ((monthid == 4) | (monthid == 6)| (monthid == 9)| (monthid == 11)):
                fromenddate = datetime.date(fromyear, monthid,30)
            else:
                if(calendar.isleap(fromstartdate.year)):
                    fromenddate = datetime.date(fromyear, monthid,29)
                else:
                    fromenddate = datetime.date(fromyear, monthid,28)

        monthid = 1
        if(tomonth == ""):
            tostartdate = datetime.date(toyear, 1,1)
            toenddate = datetime.date(toyear, 12,31)
        else:
            for counter, value in enumerate(months,1):
                if(value == tomonth):
                    monthid = counter
                    break;
            tostartdate = datetime.date(toyear, monthid,1)
            if((monthid == 1) | (monthid == 3)| (monthid == 5)| (monthid == 7)| (monthid == 8)| (monthid == 10)| (monthid == 12)):
                toenddate = datetime.date(fromyear, monthid,31)
            elif ((monthid == 4) | (monthid == 6)| (monthid == 9)| (monthid == 11)):
                toenddate = datetime.date(toyear, monthid,30)
            else:
                if(calendar.isleap(tostartdate.year)):
                    toenddate = datetime.date(toyear, monthid,29)
                else:
                    toenddate = datetime.date(toyear, monthid,28)
        
        

        
        redirect(URL('report','paymentreportcsv',\
                                     vars=dict(providerid=providerid,fromstartdate=fromstartdate,\
                                               fromenddate=fromenddate,tostartdate=tostartdate,\
                                               toenddate=toenddate)))            
    elif form.errors:
        response.flash = "Error - Payment! " + str(form.errors)
        redirect(returnurl)
        
    
    return dict(username=username,returnurl=returnurl,form=form,formheader=formheader)

@auth.requires_login()
def paymentreportcsv():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Payment Report"
    returnurl=URL('default','index')
    
    providerid    = int(common.getid(request.vars.providerid))
    fromstartdate = datetime.datetime.strptime(request.vars.fromstartdate,"%Y-%m-%d")
    fromenddate = datetime.datetime.strptime(request.vars.fromenddate,"%Y-%m-%d")
    tostartdate = datetime.datetime.strptime(request.vars.tostartdate,"%Y-%m-%d")
    toenddate = datetime.datetime.strptime(request.vars.toenddate,"%Y-%m-%d")
    
    
    query = ""
    
    if(providerid == 0):
        
        query = ((db.vw_payments.lastpaymentdate >= request.vars.fromstartdate) & (db.vw_payments.lastpaymentdate <= request.vars.toenddate) & \
                 (db.vw_payments.is_active == True))
        
    else:
        
        query = ((db.vw_payments.providerid== providerid) & (db.vw_payments.lastpaymentdate >= request.vars.fromstartdate) & (db.vw_payments.lastpaymentdate <= request.vars.toenddate) & \
                 (db.vw_payments.is_active == True))
        
    left =    [db.provider.on(db.provider.id==db.vw_payments.providerid)]
    
    fields = (db.vw_payments.id, db.provider.provider, db.provider.providername,db.vw_payments.patientname,db.vw_payments.treatment,db.vw_payments.shortdescription,\
              db.vw_payments.lastpaymentdate,db.vw_payments.totaltreatmentcost,db.vw_payments.totalpaid,db.vw_payments.totaldue)
    
    db.vw_payments.id.readable = False
    db.vw_payments.id.writable = False
    
    headers = {
        
        'provider.provider' : 'Provider',
        'provider.providername':'Prov. Name',
        'vw_payments.patientname':'Patient',
        'vw_payments.treatment':'Treatment',
        'vw_payments.lastpaymentdate':'Date',
        'vw_payments.totaltreatmentcost':'Total Cost',
        'vw_payments.totalpaid':'Total Paid',
        'vw_payments.totaldue':'Total Due'
        }
    
    orderby = db.provider.provider | ~db.vw_payments.lastpaymentdate 
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, xml=False)    
    field_id = db.vw_payments.id
    
    formPayments = SQLFORM.grid(query=query,
                                field_id=field_id,
                                headers=headers,
                                fields=fields,
                                paginate=10,
                                left=left,
                                orderby=orderby,
                                exportclasses=exportlist,
                                links_in_grid=False,
                                searchable=False,
                                create=False,
                                deletable=False,
                                editable=False,
                                details=False,
                                user_signature=True
                               )           
    
    return dict(formPayments=formPayments,username=username,formheader=formheader, returnurl=returnurl)
                
                
    
def providerreport():
    
    
    localtime = common.getISTCurrentLocatTime()
    
    
    form = SQLFORM.factory(
        Field('enrollyear','string',default=localtime.strtime("%Y")),
        Field('provstatus', widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _class='form_details'), default='ALL', label='Doctor',requires=IS_IN_SET(['ALL','Active','InActive']))
        )
    
    
    return dict(form=form,formheader="Provider Report")
        
@auth.requires_login()
def relgrprovreportcsv():
    logger.loggerpms2.info("Enter Religare Prov Report CSV")
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Religare Provider Report"
    returnurl=URL('default','index')
    
    providerid    = int(common.getid(request.vars.providerid))
   
    fromdate = datetime.datetime.strptime(request.vars.fromdate,"%Y-%m-%d")
    todate = datetime.datetime.strptime(request.vars.todate,"%Y-%m-%d")
    
    
    query = ""
    
    if(providerid == 0):
        
        query = ((db.vw_relgrtreatmentprocedure.treatmentdate >= fromdate) & (db.vw_relgrtreatmentprocedure.treatmentdate <= todate) & \
                 (db.vw_relgrtreatmentprocedure.relgrproc == True)&(db.vw_relgrtreatmentprocedure.is_active == True))
        
    else:
        query = ((db.vw_relgrtreatmentprocedure.providerid== providerid) & (db.vw_relgrtreatmentprocedure.treatmentdate >= fromdate) & (db.vw_relgrtreatmentprocedure.treatmentdate <= todate) & \
                 (db.vw_relgrtreatmentprocedure.relgrproc == True)&(db.vw_relgrtreatmentprocedure.is_active == True))
        
    logger.loggerpms2.info("Religare Prov Report CSV query "  + str(query))    

   
    fields = (
              db.vw_relgrtreatmentprocedure.fullname,
              db.vw_relgrtreatmentprocedure.cell,
              db.vw_relgrtreatmentprocedure.groupref,
              db.vw_relgrtreatmentprocedure.patientmember,
              db.vw_relgrtreatmentprocedure.company,
        
              db.vw_relgrtreatmentprocedure.providercode,
              db.vw_relgrtreatmentprocedure.providername,
              db.vw_relgrtreatmentprocedure.treatmentdate,
              db.vw_relgrtreatmentprocedure.treatment,
              db.vw_relgrtreatmentprocedure.service_id,
              db.vw_relgrtreatmentprocedure.relgrtransactionid,
              db.vw_relgrtreatmentprocedure.relgrprocdesc,
              db.vw_relgrtreatmentprocedure.procedurecode,
              db.vw_relgrtreatmentprocedure.procdesc,
              db.vw_relgrtreatmentprocedure.procedurefee,
              db.vw_relgrtreatmentprocedure.inspays,
              db.vw_relgrtreatmentprocedure.copay,
              db.vw_relgrtreatmentprocedure.status
              
    )
    
    
    headers = {
        'vw_relgrtreatmentprocedure.fullname':'Member Name',
        'vw_relgrtreatmentprocedure.cell':'Cell',
        'vw_relgrtreatmentprocedure.groupref':'Group Ref',
        'vw_relgrtreatmentprocedure.patientmember':'MDP Client ID',
        'vw_relgrtreatmentprocedure.company':'Company',
        
        'vw_relgrtreatmentprocedure.providercode':'Provider',
        'vw_relgrtreatmentprocedure.providername':'Name',
        'vw_relgrtreatmentprocedure.treatmentdate':'Date',
        'vw_relgrtreatmentprocedure.treatment':'Treatment',
        'vw_relgrtreatmentprocedure.service_id':'Service ID',
        'vw_relgrtreatmentprocedure.relgrtransactionid':'Trans ID',
        'vw_relgrtreatmentprocedure.procedurecode':'Proc Code',
        'vw_relgrtreatmentprocedure.procedesc':'Proc Desc',
        'vw_relgrtreatmentprocedure.procedurefee':'Transaction Cost',
        'vw_relgrtreatmentprocedure.inspays':'Transaction Amount',
        'vw_relgrtreatmentprocedure.copay':'Patient Pays',
        'vw_relgrtreatmentprocedure.status':'Treatment Status'
        
        }
    
    links = [\
           
           dict(header=CENTER("View/Print"), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),\
                                                                       _href=URL("payment","print_payment_receipt",\
                                                                                 vars=dict(paymentid=row.id, \
                                                                                           page=page,tplanid=tplanid,\
                                                                                           treatmentid=treatmentid,patient=patient,\
                                                                                           fullname=fullname,patientid=patientid, 
                                                                                           memberid=memberid,providerid=providerid,\
                                                                                           providername=providername,returnurl=returnurl,mode="update"))))),
    ]

    
    maxtextlengths = {'vw_relgrtreatmentprocedure.procdesc':30,'vw_relgrtreatmentprocedure.relgrtransactionid':30}
    orderby = db.vw_relgrtreatmentprocedure.providercode | db.vw_relgrtreatmentprocedure.treatmentdate 
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, xml=False)    
    field_id = db.vw_relgrtreatmentprocedure.providerid
    
    formPayments = SQLFORM.grid(query=query,
                                field_id=field_id,
                                headers=headers,
                                fields=fields,
                                paginate=10,
                                maxtextlengths = maxtextlengths,
                                orderby=orderby,
                                exportclasses=exportlist,
                                links_in_grid=False,
                                searchable=False,
                                create=False,
                                deletable=False,
                                editable=False,
                                details=False,
                                user_signature=True
                               )           
    
    return dict(formPayments=formPayments,username=username,formheader=formheader, returnurl=returnurl)

@auth.requires_login()
def relgrprovreportparams():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Religare Provider Report"
    providerid = int(common.getid(request.vars.providerid))
    if(providerid == 0):
        providerid = 1
        
    form = SQLFORM.factory(
        Field('provider',  default=providerid, requires=IS_EMPTY_OR(IS_IN_DB(db(db.vw_rlgprovider.is_active == True), db.vw_rlgprovider.id, '%(providercode)s : %(providername)s'))),
        Field('fromdate',
        'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),        
        Field('todate',
        'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),        
        Field('fromyear', requires = IS_IN_SET(YEAR),length=20,default=request.now.year),
        Field('frommonth', requires=IS_IN_SET(MONTH),length=20,default=months[request.now.month-1]),
        Field('toyear', requires = IS_IN_SET(YEAR),length=20,default=request.now.year),
        Field('tomonth', requires=IS_IN_SET(MONTH),length=20,default=months[request.now.month-1])
    )
   
    
    submit = form.element('input',_type='submit')
    submit['_style'] = 'display:none;'
    
    returnurl=URL('default','index')
    
    if form.accepts(request,session,keepvalues=True):
        providerid = 0 if(form.vars.provider == None) else int(common.getid(form.vars.provider))
           
        fromdate = form.vars.fromdate
        todate = form.vars.todate
        
        #fromyear  = int(common.getid(form.vars.fromyear))
        #frommonth = form.vars.month
        #toyear  = int(common.getid(form.vars.toyear))
        #tomonth = form.vars.tomonth
        
        #monthid = 1

        #if(frommonth == ""):
            #fromstartdate = datetime.date(fromyear, 1,1)
            #fromenddate = datetime.date(fromyear, 12,31)
        #else:
            #for counter, value in enumerate(months,1):
                #if(value == frommonth):
                    #monthid = counter
                    #break;
            #fromstartdate = datetime.date(fromyear, monthid,1)
            #if((monthid == 1) | (monthid == 3)| (monthid == 5)| (monthid == 7)| (monthid == 8)| (monthid == 10)| (monthid == 12)):
                #fromenddate = datetime.date(fromyear, monthid,31)
            #elif ((monthid == 4) | (monthid == 6)| (monthid == 9)| (monthid == 11)):
                #fromenddate = datetime.date(fromyear, monthid,30)
            #else:
                #if(calendar.isleap(fromstartdate.year)):
                    #fromenddate = datetime.date(fromyear, monthid,29)
                #else:
                    #fromenddate = datetime.date(fromyear, monthid,28)

        #monthid = 1
        #if(tomonth == ""):
            #tostartdate = datetime.date(toyear, 1,1)
            #toenddate = datetime.date(toyear, 12,31)
        #else:
            #for counter, value in enumerate(months,1):
                #if(value == tomonth):
                    #monthid = counter
                    #break;
            #tostartdate = datetime.date(toyear, monthid,1)
            #if((monthid == 1) | (monthid == 3)| (monthid == 5)| (monthid == 7)| (monthid == 8)| (monthid == 10)| (monthid == 12)):
                #toenddate = datetime.date(fromyear, monthid,31)
            #elif ((monthid == 4) | (monthid == 6)| (monthid == 9)| (monthid == 11)):
                #toenddate = datetime.date(toyear, monthid,30)
            #else:
                #if(calendar.isleap(tostartdate.year)):
                    #toenddate = datetime.date(toyear, monthid,29)
                #else:
                    #toenddate = datetime.date(toyear, monthid,28)
        
        

        
        redirect(URL('report','relgrprovreportcsv',\
                                     vars=dict(providerid=providerid,\
                                               fromdate=fromdate,\
                                               todate=todate)))            
    elif form.errors:
        response.flash = "Error - Religare Provider Report! " + str(form.errors)
        redirect(returnurl)
        
    
    return dict(username=username,returnurl=returnurl,form=form,formheader=formheader)


@auth.requires_login()
def relgrinvoicereportcsv():
    logger.loggerpms2.info("Enter Religare Invoice Report CSV")
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Religare Invoice Report"
    returnurl=URL('default','index')
    
    providerid    = int(common.getid(request.vars.providerid))
   
    fromdate = datetime.datetime.strptime(request.vars.fromdate,"%Y-%m-%d")
    todate = datetime.datetime.strptime(request.vars.todate,"%Y-%m-%d")
    status = request.vars.status
    company=request.vars.company
    
    
    query = ""
    
    
    if(providerid == 0):
        query = ((db.vw_relgrtreatmentprocedure.treatmentdate >= fromdate) & (db.vw_relgrtreatmentprocedure.treatmentdate <= todate) & \
                 (db.vw_relgrtreatmentprocedure.relgrproc == True)&(db.vw_relgrtreatmentprocedure.is_active == True))
        
    else:
        query = ((db.vw_relgrtreatmentprocedure.providerid== providerid) & (db.vw_relgrtreatmentprocedure.treatmentdate >= fromdate) & (db.vw_relgrtreatmentprocedure.treatmentdate <= todate) & \
                 (db.vw_relgrtreatmentprocedure.relgrproc == True)&(db.vw_relgrtreatmentprocedure.is_active == True))
        
    
    if(status == "ALL"):
        query = query & ((db.vw_relgrtreatmentprocedure.status == "Started")|(db.vw_relgrtreatmentprocedure.status == "Completed"))
    else:
        query = query & ((db.vw_relgrtreatmentprocedure.status == status))
        
    query = query & ((db.vw_relgrtreatmentprocedure.company == company))
    
    logger.loggerpms2.info("Religare Prov Report CSV query "  + str(query))    

   
    fields = (
              db.vw_relgrtreatmentprocedure.fullname,
              db.vw_relgrtreatmentprocedure.cell,
              db.vw_relgrtreatmentprocedure.groupref,
              db.vw_relgrtreatmentprocedure.patientmember,
              db.vw_relgrtreatmentprocedure.company,
              
              db.vw_relgrtreatmentprocedure.providerid,
              db.vw_relgrtreatmentprocedure.providercode,
              db.vw_relgrtreatmentprocedure.providername,
              db.vw_relgrtreatmentprocedure.practicename,
              db.vw_relgrtreatmentprocedure.regno,
              db.vw_relgrtreatmentprocedure.practiceaddress,
              
              db.vw_relgrtreatmentprocedure.treatmentdate,
              db.vw_relgrtreatmentprocedure.treatment,
              db.vw_relgrtreatmentprocedure.service_id,

              db.vw_relgrtreatmentprocedure.procedurecode,
              db.vw_relgrtreatmentprocedure.procdesc,
              db.vw_relgrtreatmentprocedure.procedurefee,
              db.vw_relgrtreatmentprocedure.copay,
              db.vw_relgrtreatmentprocedure.inspays,
              db.vw_relgrtreatmentprocedure.inspays_GST,
              db.vw_relgrtreatmentprocedure.tooth,
              db.vw_relgrtreatmentprocedure.quadrant,
              
              db.vw_relgrtreatmentprocedure.relgrtransactionid,
              db.vw_relgrtreatmentprocedure.relgrprocdesc,
              db.vw_relgrtreatmentprocedure.status
              
    )
    
    
    headers = {
        'vw_relgrtreatmentprocedure.fullname':'Member Name',
        'vw_relgrtreatmentprocedure.cell':'Cell',
        'vw_relgrtreatmentprocedure.groupref':'Group Ref',
        'vw_relgrtreatmentprocedure.patientmember':'MDP Client ID',
        'vw_relgrtreatmentprocedure.company':'Company',
        
        'vw_relgrtreatmentprocedure.providerid':'ProviderID',
        'vw_relgrtreatmentprocedure.providercode':'Provider',
        'vw_relgrtreatmentprocedure.providername':'Name',
        'vw_relgrtreatmentprocedure.practicename':'Practice Name',
        'vw_relgrtreatmentprocedure.regno':'Reg No',
        'vw_relgrtreatmentprocedure.practiceaddress':'Practice Address',
        
        'vw_relgrtreatmentprocedure.treatmentdate':'Date',
        'vw_relgrtreatmentprocedure.treatment':'Treatment',
        'vw_relgrtreatmentprocedure.service_id':'Service ID',
        
       
        
        'vw_relgrtreatmentprocedure.procedurecode':'Proc Code',
        'vw_relgrtreatmentprocedure.procedesc':'Proc Desc',
        
        'vw_relgrtreatmentprocedure.procedurefee':'Transaction Cost',
        'vw_relgrtreatmentprocedure.copay':'Patient Pays',
        'vw_relgrtreatmentprocedure.inspays':'Ins. Pays',
        'vw_relgrtreatmentprocedure.inspays_GST':'Ins. Pays (GST)',

        'vw_relgrtreatmentprocedure.relgrprocdesc':'Relgr Proc Desc',
        'vw_relgrtreatmentprocedure.relgrtransactionid':'Trans ID',
        
        'vw_relgrtreatmentprocedure.status':'Treatment Status',
        
        'vw_relgrtreatmentprocedure.tooth':'Tooth',
        'vw_relgrtreatmentprocedure.quadrant':'Quadrant'

        
        }
    
    links = [\
           
           dict(header=CENTER("View/Print"), body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=25, _height=25),\
                                                                       _href=URL("payment","print_payment_receipt",\
                                                                                 vars=dict(paymentid=row.id, \
                                                                                           page=page,tplanid=tplanid,\
                                                                                           treatmentid=treatmentid,patient=patient,\
                                                                                           fullname=fullname,patientid=patientid, 
                                                                                           memberid=memberid,providerid=providerid,\
                                                                                           providername=providername,returnurl=returnurl,mode="update"))))),
    ]

    
    maxtextlengths = {'vw_relgrtreatmentprocedure.procdesc':30,'vw_relgrtreatmentprocedure.relgrtransactionid':30}
    orderby = db.vw_relgrtreatmentprocedure.providercode | db.vw_relgrtreatmentprocedure.treatmentdate 
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, xml=False)    
    field_id = db.vw_relgrtreatmentprocedure.providerid
    
    formPayments = SQLFORM.grid(query=query,
                                field_id=field_id,
                                headers=headers,
                                fields=fields,
                                paginate=10,
                                maxtextlengths = maxtextlengths,
                                orderby=orderby,
                                exportclasses=exportlist,
                                links_in_grid=False,
                                searchable=False,
                                create=False,
                                deletable=False,
                                editable=False,
                                details=False,
                                user_signature=True
                               )           
    
    return dict(formPayments=formPayments,username=username,formheader=formheader, returnurl=returnurl)

@auth.requires_login()
def relgrinvoicereportparams():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Religare Invoice Report"
        
    form = SQLFORM.factory(
        Field('company', default="RLG",requires=IS_EMPTY_OR(IS_IN_DB(db(db.company.is_active == True), db.company.company, '%(company)s : %(name)s'))),
        Field('provider', requires=IS_EMPTY_OR(IS_IN_DB(db(db.vw_rlgprovider.is_active == True), db.vw_rlgprovider.id, '%(providercode)s : %(providername)s'))),
        Field('fromdate',
        'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='From Date',default=request.now,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),        
        Field('todate',
        'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='To Date',default=request.now,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),        
        Field('status', default="ALL", requires=IS_IN_SET(['ALL','Started','Completed']))    
    )
   
    
    submit = form.element('input',_type='submit')
    submit['_style'] = 'display:none;'
    
    returnurl=URL('default','index')
    
    if form.accepts(request,session,keepvalues=True):
        providerid = 0 if(form.vars.provider == None) else int(common.getid(form.vars.provider))
           
        fromdate = form.vars.fromdate
        todate = form.vars.todate
        
        status = form.vars.status 
        
        company = form.vars.company

        redirect(URL('report','relgrinvoicereportcsv',\
             vars=dict(company=company,providerid=providerid,\
                       fromdate=fromdate,\
                       todate=todate,\
                       status = status)))     
                
    elif form.errors:
        response.flash = "Error - Religare Invoice Report! " + str(form.errors)
        redirect(returnurl)
        
    
    return dict(username=username,returnurl=returnurl,form=form,formheader=formheader)


#@auth.requires_login()
def abhiclreport():
    
 
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "ABHICL MIS Report"
        
    form = SQLFORM.factory(
        Field('abhiclid', default=""),
        
        Field('company', default="ABHI",requires=IS_EMPTY_OR(IS_IN_DB(db(db.company.is_active == True), db.company.company, '%(company)s : %(name)s'))),
        Field('provider', requires=IS_EMPTY_OR(IS_IN_DB(db(db.vw_rlgprovider.is_active == True), db.vw_rlgprovider.id, '%(providercode)s : %(providername)s'))),
        Field('fromdate',
        'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='From Date',default=request.now,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),        
        Field('todate',
        'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='To Date',default=request.now,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),        
        Field('status', default="Completed", requires=IS_IN_SET(['ALL','Started','Completed']))    
    )
   
    
    submit = form.element('input',_type='submit')
    submit['_style'] = 'display:none;'
    
    returnurl=URL('default','index')
    
    if form.accepts(request,session,keepvalues=True):
        providerid = 0 if(form.vars.provider == None) else int(common.getid(form.vars.provider))
    
        abhiclid  = form.vars.abhiclid
        fromdate = (form.vars.fromdate).strftime("%d/%m/%Y")
        todate = (form.vars.todate).strftime("%d/%m/%Y")
        
        status = form.vars.status 
        
        company = form.vars.company
        
        abhiclobj = mdpabhicl.ABHICL(db, None, providerid)

        avars = {}
        avars["ABHICLID"] = abhiclid
        avars["company"] = company
 
        avars["from_date"] = fromdate
        avars["to_date"] = todate
        avars["status"] = status
           
        treatments = abhiclobj.get_treatments(avars)
        
    elif form.errors:
        response.flash = "Error - Religare Invoice Report! " + str(form.errors)
        redirect(returnurl)
        
    
    return dict(username=username,returnurl=returnurl,form=form,formheader=formheader)



