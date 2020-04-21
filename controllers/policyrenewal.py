from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)

import datetime
import time
import calendar
import os
import random
import string
import urllib

from datetime import timedelta

from decimal import Decimal
from string import Template

from gluon.tools import Mail


#import sys
#sys.path.append('modules')
from applications.my_pms2.modules  import account
from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import mail
from applications.my_pms2.modules  import logger

#from gluon.contrib import account
#from gluon.contrib import mail
#from gluon.contrib import logger
#from gluon.contrib import common


common.getvalue = lambda amount: amount if((amount != None)&(amount != "")) else 0
getmode    = lambda mode:mode if(mode != None) else 'None'


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

def upgrade_policy_payment_cc():

    if(len(request.args)==0):
        raise HTTP(403,"Illegal values for Renewal Payment")

    mode = 'CreditCard'
    page = 1

    encodedmemberid = request.args[0]
    decodestr  = encodedmemberid.decode('base64','strict')
    splits = decodestr.split('_')
    logid = int(common.getid(splits[1]))
    normaltime = splits[0].decode('base64','strict')
    timestruct  = time.strptime(normaltime,'%a %b %d %H:%M:%S %Y')
    month = int(timestruct[1])
    day = int(timestruct[2])
    year = int(timestruct[0])

    if((year < 2015)):
        raise HTTP(403,"Illegal values in Renewal Payment!!!")
    if((month < 1) | (month>12)):
        raise HTTP(403,"Illegal values in Renewal Payment!!!")
    if((day < 1) | (day>31)):
        raise HTTP(403,"Illegal values in Renewal Payment!!!")

    rows = db(db.paymenttxlog.id == logid).select()
    if(len(rows)==0):
        raise HTTP(403,"Error in Policy Renewal Receipt - Pay Online")

    memberpolicyrenewalid = int(common.getid(rows[0].memberpolicyrenewal))
    webmemberid = int(common.getid(rows[0].webmember))
    patientmemberid = int(common.getid(rows[0].patientmember))
    premstartdt = common.getdt(rows[0].premstartdt)
    premenddt   = common.getdt(rows[0].premenddt)
    txdatetime = rows[0].txdatetime
    txno = rows[0].txno
    totpremium = rows[0].totpremium
    totcompanypays=rows[0].totcompanypays
    totyoupay = rows[0].txamount
    total  = rows[0].total
    servicetax = rows[0].servicetax
    swipecharge = rows[0].swipecharge
    paymentdetails = rows[0].responsemssg

    
    r = db((db.patientmember.id == patientmemberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    if(len(r)>0):
        lastpaid = round(float(common.getvalue(r[0].premium)),2)
        member = r[0].fname + ' ' + r[0].lname + ' (' + str(r[0].patientmember) + ')'
    else:
        lastpaid = 0
        member = ''


    return dict(member=member,paymenttxlog=logid, page=page,txdatetime=txdatetime,txno=txno,totpremium=totpremium,totcompanypays=totcompanypays,\
                totyoupay=totyoupay,total=total,servicetax=servicetax,swipecharge=swipecharge,paymentdetails=paymentdetails,lastpaid=lastpaid,mode=mode)


def renewal_payment_cc():

    if(len(request.args)==0):
        raise HTTP(403,"Illegal values for Renewal Payment")

    mode = 'CreditCard'
    page = 1

    encodedmemberid = request.args[0]
    decodestr  = encodedmemberid.decode('base64','strict')
    splits = decodestr.split('_')
    logid = int(common.getid(splits[1]))
    normaltime = splits[0].decode('base64','strict')
    timestruct  = time.strptime(normaltime,'%a %b %d %H:%M:%S %Y')
    month = int(timestruct[1])
    day = int(timestruct[2])
    year = int(timestruct[0])

    if((year < 2015)):
        raise HTTP(403,"Illegal values in Renewal Payment!!!")
    if((month < 1) | (month>12)):
        raise HTTP(403,"Illegal values in Renewal Payment!!!")
    if((day < 1) | (day>31)):
        raise HTTP(403,"Illegal values in Renewal Payment!!!")

    rows = db(db.paymenttxlog.id == logid).select()
    if(len(rows)==0):
        raise HTTP(403,"Error in Policy Renewal Receipt - Pay Online")

    memberpolicyrenewalid = int(common.getid(rows[0].memberpolicyrenewal))
    webmemberid = int(common.getid(rows[0].webmember))
    patientmemberid = int(common.getid(rows[0].patientmember))
    premstartdt = common.getdt(rows[0].premstartdt)
    premenddt   = common.getdt(rows[0].premenddt)
    txdatetime = rows[0].txdatetime
    txno = rows[0].txno
    totpremium = rows[0].totpremium
    totcompanypays=rows[0].totcompanypays
    totyoupay = rows[0].txamount
    total  = rows[0].total
    servicetax = rows[0].servicetax
    swipecharge = rows[0].swipecharge
    paymentdetails = rows[0].responsemssg

    r = db(db.webmember.id == webmemberid).select()
    if(len(r)>0):
        member = r[0].fname + ' ' + r[0].lname + ' (' + str(r[0].webmember) + ')'

    else:
        member = ''


   
    return dict(member=member,paymenttxlog=logid, page=page,txdatetime=txdatetime,txno=txno,totpremium=totpremium,totcompanypays=totcompanypays,\
                totyoupay=totyoupay,total=total,servicetax=servicetax,swipecharge=swipecharge,paymentdetails=paymentdetails,mode=mode)



def email_renewalpayment():

    server = None
    sender = None
    login = None
    tls = False

    page = getgridpage(request.vars)

    paymenttxlogid = int(common.getid(request.args[0]))
    if(len(request.args) == 0):
        raise HTTP(403,"Error in Email Renewal Paymenr - No Member Email address")
    r = db(db.paymenttxlog.id ==paymenttxlogid ).select()
    if(len(r) == 0):
        raise HTTP(403,"Error in Email Renewal Paymenr - No Member Email address")
    patientmemberid = int(common.getid(r[0].patientmember))

    r = db((db.patientmember.id == patientmemberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    if(len(r) == 0):
        raise HTTP(403,"Error in Email Renewal Paymenr - No Member Email address")
    memberemail = r[0].email
    membername = r[0].fname + ' ' + r[0].lname


    props = db(db.urlproperties.id>0).select()
    if(len(props)>0):
        server = props[0].mailserver + ":"  + props[0].mailserverport
        sender = props[0].mailsender
        login  = props[0].mailusername + ":" + props[0].mailpassword
        port = int(props[0].mailserverport)
        if((port != 25) & (port != 26)):
            tls = True
        else:
            tls = False

        if((props[0].mailusername == 'None')):
                    login = None
    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")

    normaltime = time.asctime(time.localtime(time.time())).encode('base64','strict')
    str1 = normaltime +'_'+ str(paymenttxlogid)
    encodedarg = str1.encode('base64','strict')
    renewalpaymentlink = props[0].mydp_ipaddress  +  "/my_dentalplan/policyrenewal/renewal_payment_cc/" + encodedarg

    mail = Mail()
    mail.settings.server = server
    mail.settings.sender = sender
    mail.settings.login =  login
    mail.settings.tls = tls

    to      =  memberemail
    subject = "Policy Renewal Payment Link"


    appPath = request.folder
    htmlfile = os.path.join(appPath, 'templates','Reminder_Renewal_Policy.html')

    f = open(htmlfile,'rb')
    html = Template(f.read())
    f.close()

    result  = html.safe_substitute(renewalpaymentlink=renewalpaymentlink)
    retVal = mail.send(to,subject,result,encoding='utf-8')

    return dict(ret=retVal, membername=membername, memberemail=memberemail,page=page)


def getpremiumenddate(premiumstartdt):
    day = timedelta(days=1)
    premiumenddt = premiumstartdt - day
    return premiumenddt

def getgridpage(requestvars):

    page = 1
    if(len(requestvars)==0):
        page = 1
    elif(requestvars == None):
        page = 1
    elif(requestvars.page == None):
        page = 1
    else:
        page = int(requestvars.page)

    return page

def getrenewalnoticeperiod():

    renewalnoticeperiod = 90
    r = db(db.urlproperties).select()
    if(len(r) == 1):
        if(r[0].renewalnoticeperiod == None):
            renewalnoticeperiod = 90
        else:
            renewalnoticeperiod = int(r[0].renewalnoticeperiod)

    return renewalnoticeperiod

def getrenewalnoticedate(currentdate, renewalnoticeperiod):

    return currentdate + timedelta(days=renewalnoticeperiod)


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
def emailwelcomekit(request,patientmemberid,providerid):

    ret = mail.emailWelcomeKit(db,request,patientmemberid,providerid)
    return ret


def getfamilypremiumamount(memberid):
    rows   = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    if(len(rows)==0):
            return dict(premium = 0, companyamt = 0, memberamt = 0)

    #09/02/2017 Replacing the following code from webmember to patientmember.since len(rows) > 0 check is already made at the start, this if..else condition has to be removed
    #webmemberid = int(common.getid(rows[0].webmember))
    #companyrows     = db((db.companyhmoplanrate.company == db.webmember.company) & (db.webmember.id == webmemberid)).select()  # this is not required
    #deprows  = db(db.webmemberdependants.webmember == webmemberid).select()

    #if(len(rows) > 0):   
        #if(len(deprows)>0):
            #ds = db.executesql('select "Self" AS relation,fname,lname,webdob, CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
                                #CASE WHEN companyhmoplanrate.companypays IS NOT NULL THEN companyhmoplanrate.companypays ELSE 0.0 END AS companypays, \
                                #CASE WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.premium - companyhmoplanrate.companypays \
                                #WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NULL) THEN companyhmoplanrate.premium \
                                #WHEN (companyhmoplanrate.premium IS NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.companypays \
                                #ELSE 0.00 END AS youpay FROM webmember \
                                #LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
                                #LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND webmember.groupregion = companyhmoplanrate.groupregion AND \
                                #companyhmoplanrate.relation = "Self"  AND companyhmoplanrate.is_Active = "T"  AND \
                                #companyhmoplanrate.hmoplan = webmember.hmoplan \
                                #WHERE \
                                #webmember.is_active = "T" AND webmember.id = ' + str(webmemberid) +
                                             #' UNION ' +
                                #'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob,\
                                #CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium, \
                                #CASE WHEN companyhmoplanrate.companypays IS NOT NULL THEN companyhmoplanrate.companypays ELSE 0.0 END AS companypays, \
                                #CASE WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.premium - companyhmoplanrate.companypays \
                                #WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NULL) THEN companyhmoplanrate.premium \
                                #WHEN (companyhmoplanrate.premium IS NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.companypays \
                                #ELSE 0.00 END  AS youpay FROM  webmember   \
                                #LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
                                #LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
                                #LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND webmember.groupregion = companyhmoplanrate.groupregion AND companyhmoplanrate.is_Active = "T"  AND  \
                                #webmemberdependants.relation = companyhmoplanrate.relation AND \
                                #companyhmoplanrate.hmoplan = webmember.hmoplan \
                                #where webmemberdependants.is_active = "T" AND webmember.id = ' + str(webmemberid))
        #else:
            #ds = db.executesql('select "Self" AS relation,fname,lname,webdob, \
                                #CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
                                #CASE WHEN companyhmoplanrate.companypays IS NOT NULL THEN companyhmoplanrate.companypays ELSE 0.0 END AS companypays,\
                                #CASE WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.premium - companyhmoplanrate.companypays \
                                #WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NULL) THEN companyhmoplanrate.premium \
                                #WHEN (companyhmoplanrate.premium IS NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.companypays \
                                #ELSE 0.00 END AS youpay FROM webmember \
                                #LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
                                #LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND webmember.groupregion = companyhmoplanrate.groupregion AND \
                                #companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND companyhmoplanrate.is_Active = "T"  \
                                #WHERE \
                                #webmember.is_active = "T" AND webmember.id = ' + str(webmemberid))
    #else:
        #if(len(deprows)>0):
            #ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay FROM webmember \
                                #LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
                                #LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND webmember.groupregion = companyhmoplanrate.groupregion AND \
                                #companyhmoplanrate.hmoplan = webmember.hmoplan AND\
                                #companyhmoplanrate.covered = "Self" AND companyhmoplanrate.is_Active = "T"  \
                                #WHERE webmember.is_active = "T" AND webmember.relation = ' + relation + 'webmember.id = ' + str(webmemberid) +
                                             #' UNION ' +
                                #'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob, 0 AS premium, \
                                 #0 AS companypays, 0 AS youpay FROM  webmember  \
                                 #LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
                                 #LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
                                 #LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND webmember.groupregion = companyhmoplanrate.groupregion AND \
                                 #webmemberdependants.relation = companyhmoplanrate.relation AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
                                 #companyhmoplanrate.is_Active = "T" \
                                 #WHERE webmemberdependants.is_active = "T" AND webmember.id = ' + str(webmemberid))

        #else:

            #ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay \
                               #FROM webmember \
                               #LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
                               #LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
                               #companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
                               #companyhmoplanrate.is_Active = "T" \
                               #WHERE webmember.is_active = "T" AND webmember.id = ' + str(webmemberid))
            

    deprows         = db(db.patientmemberdependants.patientmember == memberid).select()            
            
    if(len(deprows)>0):
        ds = db.executesql('select "Self" AS relation,fname,lname,dob, CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
                            CASE WHEN companyhmoplanrate.companypays IS NOT NULL THEN companyhmoplanrate.companypays ELSE 0.0 END AS companypays, \
                            CASE WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.premium - companyhmoplanrate.companypays \
                            WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NULL) THEN companyhmoplanrate.premium \
                            WHEN (companyhmoplanrate.premium IS NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.companypays \
                            ELSE 0.00 END AS youpay FROM patientmember \
                            LEFT JOIN company ON company.id = patientmember.company AND company.is_active = "T" \
                            LEFT JOIN companyhmoplanrate ON patientmember.company = companyhmoplanrate.company AND patientmember.groupregion = companyhmoplanrate.groupregion AND \
                            companyhmoplanrate.relation = "Self"  AND companyhmoplanrate.is_Active = "T"  AND \
                            companyhmoplanrate.hmoplan = patientmember.hmoplan \
                            WHERE \
                            patientmember.is_active = "T" AND patientmember.id = ' + str(memberid) +
                                         ' UNION ' +
                            'SELECT patientmemberdependants.relation ,patientmemberdependants.fname,patientmemberdependants.lname, patientmemberdependants.depdob,\
                            CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium, \
                            CASE WHEN companyhmoplanrate.companypays IS NOT NULL THEN companyhmoplanrate.companypays ELSE 0.0 END AS companypays, \
                            CASE WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.premium - companyhmoplanrate.companypays \
                            WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NULL) THEN companyhmoplanrate.premium \
                            WHEN (companyhmoplanrate.premium IS NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.companypays \
                            ELSE 0.00 END  AS youpay FROM  patientmember   \
                            LEFT JOIN company ON company.id = patientmember.company AND company.is_active = "T" \
                            LEFT JOIN patientmemberdependants ON patientmember.id = patientmemberdependants.patientmember \
                            LEFT JOIN companyhmoplanrate ON patientmember.company = companyhmoplanrate.company AND patientmember.groupregion = companyhmoplanrate.groupregion AND companyhmoplanrate.is_Active = "T"  AND  \
                            patientmemberdependants.relation = companyhmoplanrate.relation AND \
                            companyhmoplanrate.hmoplan = patientmember.hmoplan \
                            where patientmemberdependants.is_active = "T" AND patientmember.id = ' + str(memberid))
    else:
        ds = db.executesql('select "Self" AS relation,fname,lname,dob, \
                            CASE WHEN companyhmoplanrate.premium IS NOT NULL THEN companyhmoplanrate.premium ELSE 0.0 END AS premium,\
                            CASE WHEN companyhmoplanrate.companypays IS NOT NULL THEN companyhmoplanrate.companypays ELSE 0.0 END AS companypays,\
                            CASE WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.premium - companyhmoplanrate.companypays \
                            WHEN (companyhmoplanrate.premium IS NOT NULL) AND (companyhmoplanrate.companypays IS NULL) THEN companyhmoplanrate.premium \
                            WHEN (companyhmoplanrate.premium IS NULL) AND (companyhmoplanrate.companypays IS NOT NULL) THEN companyhmoplanrate.companypays \
                            ELSE 0.00 END AS youpay FROM patientmember \
                            LEFT JOIN company ON company.id = patientmember.company AND company.is_active = "T" \
                            LEFT JOIN companyhmoplanrate ON patientmember.company = companyhmoplanrate.company AND patientmember.groupregion = companyhmoplanrate.groupregion AND \
                            companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = patientmember.hmoplan AND companyhmoplanrate.is_Active = "T"  \
                            WHERE \
                            patientmember.is_active = "T" AND patientmember.id = ' + str(memberid))

    return ds

def getpremiumamount(memberid,relation):

    rows   = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    if(len(rows)==0):
            return dict(premium = 0, companyamt = 0, memberamt = 0)

    webmemberid = rows[0].webmember
    companyrows     = db((db.companyhmoplanrate.company == db.webmember.company) & (db.webmember.id == webmemberid)).select()
    deprows  = db(db.webmemberdependants.webmember == webmemberid).select()

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
                                webmember.is_active = "T" AND webmember.relation = ' + relation + 'webmember.id = ' + str(webmemberid) +
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
                                where webmemberdependants.is_active = "T" AND webmemberdependants.relation ' + relation + 'webmember.id = ' + str(webmemberid))
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
                                webmember.is_active = "T" AND webmember.relation = ' + relation + 'webmember.id = ' + str(webmemberid))
    else:
        if(len(deprows)>0):
            ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay FROM webmember \
                                LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
                                LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
                                companyhmoplanrate.hmoplan = webmember.hmoplan AND\
                                companyhmoplanrate.covered = "Self" AND companyhmoplanrate.is_Active = "T"  \
                                WHERE webmember.is_active = "T" AND webmember.relation = ' + relation + 'webmember.id = ' + str(webmemberid) +
                                             ' UNION ' +
                                'SELECT webmemberdependants.relation ,webmemberdependants.fname,webmemberdependants.lname, webmemberdependants.depdob, 0 AS premium, \
                                 0 AS companypays, 0 AS youpay FROM  webmember  \
                                 LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
                                 LEFT JOIN webmemberdependants ON webmember.id = webmemberdependants.webmember \
                                 LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND \
                                 webmemberdependants.relation = companyhmoplanrate.relation AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
                                 companyhmoplanrate.is_Active = "T" \
                                 WHERE webmemberdependants.is_active = "T" AND webmemberdependants.relation ' + relation + 'webmember.id = ' + str(webmemberid))

        else:

            ds = db.executesql('select "Self" AS relation,fname,lname,webdob,  0 AS premium, 0 AS companypays, 0 AS youpay \
                               FROM webmember \
                               LEFT JOIN company ON company.id = webmember.company AND company.is_active = "T" \
                               LEFT JOIN companyhmoplanrate ON webmember.company = companyhmoplanrate.company AND webmember.groupregion = companyhmoplanrate.groupregion AND \
                               companyhmoplanrate.relation = "Self" AND companyhmoplanrate.hmoplan = webmember.hmoplan AND \
                               companyhmoplanrate.is_Active = "T" \
                               WHERE webmember.is_active = "T" AND webmember.relation = ' + relation + 'webmember.id = ' + str(webmemberid))

    totpremium = 0
    totcompanypays = 0
    totyoupay = 0

    if(len(ds)>0):
        for i in xrange(0,len(ds)):
            totpremium = totpremium + round(Decimal(ds[i][4]),2)
            totcompanypays = totcompanypays + round(Decimal(ds[i][5]),2)
            totyoupay = totpremium - totcompanypays

    return dict(premium = totpremium, companyamt = totcompanypays, memberamt = totyoupay)



@auth.requires_membership('webadmin')
@auth.requires_login()
def process_payment(memberpolicyrenewalid,webmemberid,patientmemberid,mode):

    txdatetime = datetime.datetime.now()
    txno = str(webmemberid) + "_" + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S")
    totpremium = request.vars.totpremium 
    totcompanypays=request.vars.totcompanypays
    totyoupay = request.vars.totyoupay # A
    
    servicetax = request.vars.servicetax  #B
    swipecharge = request.vars.swipecharge #C
    lastpaid = request.vars.lastpaid #D
    total  = request.vars.total      #A+B+C-D
    paymentdetails = request.vars.paymentdetails
    responsecode = mode

    r = db((db.patientmember.id == patientmemberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    if(len(r)>0):
        if((request.vars.premstartdt == "")|(request.vars.premstartdt == None)):
            premstartdt =  r[0].premstartdt
        else:
            premstartdt = datetime.datetime.strptime(common.getdt(request.vars.premstartdt),'%d/%m/%Y')
        
        if((request.vars.premenddt == "")|(request.vars.premenddt == None)):
            premenddt = r[0].premenddt
        else:
            premenddt   = datetime.datetime.strptime(common.getdt(request.vars.premenddt),'%d/%m/%Y')        
        
        
        
    else:
        premstartdt = common.getdt(None)
        premenddt = getpremiumenddate(getnewrenewaldate(premstartdt))

    if(webmemberid != 0):
        logid = db.paymenttxlog.insert(txno=txno,txdatetime=txdatetime,webmember=webmemberid,\
                                       txamount=totyoupay,totpremium=totpremium,totcompanypays=totcompanypays,\
                                       total=total,servicetax=servicetax,swipecharge=swipecharge,responsecode=responsecode,\
                                       responsemssg=paymentdetails,premstartdt=premstartdt,premenddt=premenddt, \
                                       memberpolicyrenewal = memberpolicyrenewalid, patientmember = patientmemberid)
    else:
        logid = db.paymenttxlog.insert(txno=txno,txdatetime=txdatetime,\
                                       txamount=totyoupay,totpremium=totpremium,totcompanypays=totcompanypays,\
                                       total=total,servicetax=servicetax,swipecharge=swipecharge,responsecode=responsecode,\
                                       responsemssg=paymentdetails,premstartdt=premstartdt,premenddt=premenddt, \
                                       memberpolicyrenewal = memberpolicyrenewalid, patientmember = patientmemberid)
        

    db.commit()


    # update Member Policy Renewal with renewal information
    #db((db.memberpolicyrenewal.id == memberpolicyrenewalid) & (db.memberpolicyrenewal.is_active == True)).\
        #update(paymenttxlog = logid, renewed = True, premium=totpremium,companyamt=totcompanypays, memberamt=totyoupay,paymentmode=mode)

    ## Update patientmember, webmember with renewal information
    #db((db.patientmember.id == patientmemberid)&(db.patientmember.is_active == True)).\
        #update(premium = total, premstartdt = premstartdt, premenddt = premenddt, terminationdate=premstartdt, duedate = premenddt, status="Enrolled", paid = True )

    #db((db.webmember.id == webmemberid)&(db.webmember.is_active == True)).\
            #update(paid = True,status="Enrolled")

    return logid

def upgrade_policy_callback():


   

    responseheader = ''
    txamount = 0.00
    servicetax = 0.00
    swipecharge = 0.00
    total = 0.00
    fname = ''
    lname = ''
    paymenttxlogid = 0
    mode = 'CreditCard'
    welcomekit = False
    
    MerchantRefNo =  request.vars.MerchantRefNo
    #MerchantRefNo = '20_20160403_180636'  #TEST





    rows = db(db.paymenttxlog.txno == MerchantRefNo).select()
    if(len(rows)==0):
        raise HTTP(403,"Error in Payment Callback " + MerchantRefNo)



  
    paymenttxlogid = int(common.getid(rows[0].id))
    patientmemberid = int(common.getid(rows[0].patientmember))
    memberpolicyrenewalid = int(common.getid(rows[0].memberpolicyrenewal))

    r = db((db.patientmember.id == patientmemberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    providerid = int(common.getid(r[0].provider))

    txamount      = round(Decimal(common.getvalue(rows[0].txamount)),2)
    servicetax    = round(Decimal(common.getvalue(rows[0].servicetax)),2)
    swipecharge   = round(Decimal(common.getvalue(rows[0].swipecharge)),2)
    total         = round(Decimal(common.getvalue(rows[0].total)),2)
    totpremium    = round(Decimal(common.getvalue(rows[0].totpremium)),2)
    totcompanypays    = round(Decimal(common.getvalue(rows[0].totcompanypays)),2)
    premstartdt       = common.getdt(rows[0].premstartdt)
    premenddt         = common.getdt(rows[0].premenddt)


    if(request.vars.ResponseCode == None):
        responsecode = '999'
    else:
        responsecode = request.vars.ResponseCode



    responsemssg = request.vars.ResponseMessage
    paymentid = request.vars.PaymentID
    paymentdate = request.vars.DateCreated
    if(request.vars.Amount == None):
        paymentamount = 0.00
    else:
        paymentamount = round(Decimal(request.vars.Amount),2)
    paymenttxid = request.vars.TransactionID
    accountid = request.vars.TransactionIDAccountID


    BillingName = request.vars.BillingName
    BillingAddress = request.vars.BillingAddress


    ##TEST
    #total = 124.56
    #responsecode = "0"
    #responsemssg = "Success"
    #paymentid ="Payment_ID"
    #paymentdate = "20015-06-20"
    #paymentamount = 124.56
    #paymenttxid = "Payment_TXID"
    #BillingName = "Billing_Name"
    #BillingAddress= "Billing_Addr"
    ##END TEST
    
    ##& (total == paymentamount)
    if((responsecode == '0') & (total == paymentamount)):
        #TEST - comment the update when testing

        responseheader = "Thank you for your Payment! Please call MyDentalPlan Administrator for the Membership Card"
        #TEST - comment the update when testing
        db(db.paymenttxlog.txno == MerchantRefNo).update(responsecode=responsecode,
                                                         responsemssg=responsemssg,
                                                         paymentid=paymentid,
                                                         paymentdate=paymentdate,
                                                         paymentamount = paymentamount,
                                                         paymenttxid=paymenttxid,
                                                         accountid = accountid)




        
       

        # Update patientmember, webmember with renewal information
        premium = totpremium -totcompanypays + servicetax + swipecharge
        db((db.patientmember.id == patientmemberid)&(db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).\
            update(premium = premium, premstartdt = premstartdt, premenddt = premenddt, terminationdate=premstartdt, duedate = premenddt, status="Enrolled", paid = True, upgraded=True)

        db((db.patientmemberdependants.patientmember == patientmemberid)&(db.patientmemberdependants.is_active == True)).\
                update(paid = True)

        
        #db((db.webmember.id == webmemberid)&(db.webmember.is_active == True)).update(paid = True,status="Enrolled", upgraded=True)
        #db(db.webmemberdependants.webmember == webmemberid).update(paid=True)

        welcomekit = emailwelcomekit(request, patientmemberid, providerid)

    else:
        responseheader = "Payment Failure!"
        paymentamount = 'Error'

        if((responsemssg != '') & (responsemssg != None)):
            responsemssg = "Transaction Failure - " + responsemssg
        else:
            responsemssg = "Transaction Failure"

        if((responsecode != '') & (responsecode != None)):
            responsecode =  responsecode
        else:
            responsecode = "999"

        db(db.paymenttxlog.txno == MerchantRefNo).update(responsecode=responsecode,
                                                         responsemssg=responsemssg,
                                                         paymentid=paymentid,
                                                         paymentdate=paymentdate,
                                                         paymenttxid=paymenttxid,
                                                         accountid = accountid)

        # update Member Policy Renewal with renewal information
        db((db.memberpolicyrenewal.id == memberpolicyrenewalid) & (db.memberpolicyrenewal.is_active == True)).\
            update(renewed = False, premium=0,companyamt=0, memberamt=0,\
                   swipecharge=0,servicetax=0,total=0, \
                   newrenewaldate='', newduedate = '', paymentmode='None')

        # Update patientmember, webmember with renewal information
        db((db.patientmember.id == patientmemberid)&(db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).\
            update(status="Enrolled", paid = False )


        #db((db.webmember.id == webmemberid)&(db.webmember.is_active == True)).update(paid = False,status="Enrolled")
        #db(db.webmemberdependants.webmember == webmemberid).update(paid=False)


    return dict(PaymentID=paymentid, TransactionID=paymenttxid, MerchantRefNo=MerchantRefNo, BillingName=BillingName,BillingAddress=BillingAddress,\
                Amount=paymentamount,txamount=txamount,servicetax=servicetax,swipecharge=swipecharge,ResponseMessage=responsemssg,DateCreated=paymentdate,\
                ResponseCode=responsecode,ResponseHeader=responseheader,welcomekit=welcomekit)

def renewal_callback():


    webmemberid = 0

    responseheader = ''
    txamount = 0.00
    servicetax = 0.00
    swipecharge = 0.00
    total = 0.00
    fname = ''
    lname = ''
    paymenttxlogid = 0
    mode = 'CC'
    welcomekit = False

    MerchantRefNo =  request.vars.MerchantRefNo
    #MerchantRefNo = '20_20160403_180636'  #TEST





    rows = db(db.paymenttxlog.txno == MerchantRefNo).select()
    if(len(rows)==0):
        raise HTTP(403,"Error in Payment Callback " + MerchantRefNo)



    webmemberid = int(common.getid(rows[0].webmember))
    paymenttxlogid = int(common.getid(rows[0].id))
    patientmemberid = int(common.getid(rows[0].patientmember))
    memberpolicyrenewalid = int(common.getid(rows[0].memberpolicyrenewal))
    r = db((db.patientmember.id == patientmemberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    providerid = int(common.getid(r[0].provider))
    txamount      = round(Decimal(common.getvalue(rows[0].txamount)),2)
    servicetax    = round(Decimal(common.getvalue(rows[0].servicetax)),2)
    swipecharge   = round(Decimal(common.getvalue(rows[0].swipecharge)),2)
    total         = round(Decimal(common.getvalue(rows[0].total)),2)
    totpremium    = round(Decimal(common.getvalue(rows[0].totpremium)),2)
    totcompanypays    = round(Decimal(common.getvalue(rows[0].totcompanypays)),2)
    premstartdt       = common.getdt(rows[0].premstartdt)
    premenddt         = common.getdt(rows[0].premenddt)


    if(request.vars.ResponseCode == None):
        responsecode = '999'
    else:
        responsecode = request.vars.ResponseCode



    responsemssg = request.vars.ResponseMessage
    paymentid = request.vars.PaymentID
    paymentdate = request.vars.DateCreated
    if(request.vars.Amount == None):
        paymentamount = 0.00
    else:
        paymentamount = round(Decimal(request.vars.Amount),2)
    paymenttxid = request.vars.TransactionID
    accountid = request.vars.TransactionIDAccountID


    BillingName = request.vars.BillingName
    BillingAddress = request.vars.BillingAddress


    ##TEST
    #total = 124.56
    #responsecode = "0"
    #responsemssg = "Success"
    #paymentid ="Payment_ID"
    #paymentdate = "20015-06-20"
    #paymentamount = 124.56
    #paymenttxid = "Payment_TXID"
    #BillingName = "Billing_Name"
    #BillingAddress= "Billing_Addr"
    ##END TEST
    
    ##& (total == paymentamount)
    if((responsecode == '0') & (total == paymentamount)):
        #TEST - comment the update when testing

        responseheader = "Thank you for your Payment! Please call MyDentalPlan Administrator to send you Membership Card"
        #TEST - comment the update when testing
        db(db.paymenttxlog.txno == MerchantRefNo).update(responsecode=responsecode,
                                                         responsemssg=responsemssg,
                                                         paymentid=paymentid,
                                                         paymentdate=paymentdate,
                                                         paymentamount = paymentamount,
                                                         paymenttxid=paymenttxid,
                                                         accountid = accountid)




        # update Member Policy Renewal with renewal information
        db((db.memberpolicyrenewal.id == memberpolicyrenewalid) & (db.memberpolicyrenewal.is_active == True)).\
            update(renewed = True, premium=totpremium,companyamt=totcompanypays, memberamt=txamount,\
                   swipecharge=swipecharge,servicetax=servicetax,total=total, \
                   newrenewaldate=premstartdt, newduedate = premenddt, paymentmode=mode)

        # Update patientmember, webmember with renewal information
        db((db.patientmember.id == patientmemberid)&(db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).\
            update(premium = total, premstartdt = premstartdt, premenddt = premenddt, terminationdate=premstartdt, duedate = premenddt, status="Enrolled", paid = True, upgraded=False )
        
        db((db.patientmemberdependants.patientmember == patientmemberid)&(db.patientmemberdependants.is_active == True)).\
                update(paid = True)

        db((db.webmember.id == webmemberid)&(db.webmember.is_active == True)).update(paid = True,status="Enrolled")
        db(db.webmemberdependants.webmember == webmemberid).update(paid=True)

        welcomekit = emailwelcomekit(request, patientmemberid, providerid)

    else:
        responseheader = "Payment Failure!"
        paymentamount = 'Error'

        if((responsemssg != '') & (responsemssg != None)):
            responsemssg = "Transaction Failure - " + responsemssg
        else:
            responsemssg = "Transaction Failure"

        if((responsecode != '') & (responsecode != None)):
            responsecode =  responsecode
        else:
            responsecode = "999"

        db(db.paymenttxlog.txno == MerchantRefNo).update(responsecode=responsecode,
                                                         responsemssg=responsemssg,
                                                         paymentid=paymentid,
                                                         paymentdate=paymentdate,
                                                         paymenttxid=paymenttxid,
                                                         accountid = accountid)

        # update Member Policy Renewal with renewal information
        db((db.memberpolicyrenewal.id == memberpolicyrenewalid) & (db.memberpolicyrenewal.is_active == True)).\
            update(renewed = True, premium=0,companyamt=0, memberamt=0,\
                   swipecharge=0,servicetax=0,total=0, \
                   newrenewaldate='', newduedate = '', paymentmode='None')

        # Update patientmember, webmember with renewal information
        db((db.patientmember.id == patientmemberid)&(db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).\
            update(status="Enrolled", paid = False )


        db((db.webmember.id == webmemberid)&(db.webmember.is_active == True)).update(paid = False,status="Enrolled")
        db(db.webmemberdependants.webmember == webmemberid).update(paid=False)


    return dict(PaymentID=paymentid, TransactionID=paymenttxid, MerchantRefNo=MerchantRefNo, BillingName=BillingName,BillingAddress=BillingAddress,Amount=paymentamount,txamount=txamount,servicetax=servicetax,swipecharge=swipecharge,ResponseMessage=responsemssg,DateCreated=paymentdate,ResponseCode=responsecode,ResponseHeader=responseheader,welcomekit=welcomekit)


def payby_cc():


    if(len(request.args) == 0):
        raise HTTP(403,"Error in Policy Renewal Payment - Pay Online")

    if(request.args[0] == None):
        raise HTTP(403,"Error in Policy Renewal Payment - Pay Online: No Transaction")

    logid = request.args[0]

    txrows = db((db.paymenttxlog.id == logid)).select()
    if(len(txrows)==0):
        raise HTTP(403,"Error in Policy Renewal Payment - Pay Online No Transaction")

    if(txrows[0].total == None):
        txamount = 0
    else:
        txamount = txrows[0].total

    rows = db(db.webmember.id == txrows[0].webmember).select();

    if(len(rows) > 0):
        urls = db(db.urlproperties.id > 0).select()
        return_url=urls[0].renewalcallback


        if((rows[0].address1 == None)|(rows[0].address1=='')):
            address = " "
        else:
            address=rows[0].address1

        if((rows[0].city == None)|(rows[0].city=='')):
            city = " "
        else:
            city=rows[0].city

        if((rows[0].email == None)|(rows[0].email=='')):
            email = " "
        else:
            email=rows[0].email

        if((rows[0].cell == None)|(rows[0].cell=='')):
            phone = " "
        else:
            phone=rows[0].cell

        if((rows[0].pin == None)|(rows[0].pin=='')):
            postal_code = " "
        else:
            postal_code=rows[0].pin

        if((rows[0].st == None)|(rows[0].st=='')):
            state = " "
        else:
            state=rows[0].st

        secret_key='d67fa952ec2f66c394d3192f17e01550'
        account_id='16428'

        amount=str(txamount)
        channel='10'

        country='IND'
        currency='INR'
        description='Payment'
        mode='LIVE'
        name=rows[0].fname + ' ' + rows[0].lname

        reference_no = txrows[0].txno


        ship_address=address
        ship_city=city
        ship_country='IND'
        ship_name=name
        ship_phone=phone
        ship_postal_code=postal_code
        ship_state=state


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



def upgrade_policy_paybycc():


    if(len(request.args) == 0):
        raise HTTP(403,"Error in Policy Renewal Payment - Pay Online")

    if(request.args[0] == None):
        raise HTTP(403,"Error in Policy Renewal Payment - Pay Online: No Transaction")

    logid = request.args[0]

    txrows = db((db.paymenttxlog.id == logid)).select()
    if(len(txrows)==0):
        raise HTTP(403,"Error in Policy Renewal Payment - Pay Online: No Transaction")

    if(txrows[0].total == None):
        txamount = 0
    else:
        txamount = txrows[0].total

    rows = db(db.patientmember.id == txrows[0].patientmember).select();

    if(len(rows) > 0):
        urls = db(db.urlproperties.id > 0).select()
        return_url=urls[0].upgradepolicycallback


        if((rows[0].address1 == None)|(rows[0].address1=='')):
            address = " "
        else:
            address=rows[0].address1

        if((rows[0].city == None)|(rows[0].city=='')):
            city = " "
        else:
            city=rows[0].city

        if((rows[0].email == None)|(rows[0].email=='')):
            email = " "
        else:
            email=rows[0].email

        if((rows[0].cell == None)|(rows[0].cell=='')):
            phone = " "
        else:
            phone=rows[0].cell

        if((rows[0].pin == None)|(rows[0].pin=='')):
            postal_code = " "
        else:
            postal_code=rows[0].pin

        if((rows[0].st == None)|(rows[0].st=='')):
            state = " "
        else:
            state=rows[0].st

        secret_key='d67fa952ec2f66c394d3192f17e01550'
        account_id='16428'

        amount=str(txamount)
        channel='10'

        country='IND'
        currency='INR'
        description='Payment'
        mode='LIVE'
        name=rows[0].fname + ' ' + rows[0].lname

        reference_no = txrows[0].txno


        ship_address=address
        ship_city=city
        ship_country='IND'
        ship_name=name
        ship_phone=phone
        ship_postal_code=postal_code
        ship_state=state


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



@auth.requires_membership('webadmin')
@auth.requires_login()
def renewal_payment():

    if(len(request.args) == 0):
        raise HTTP(403,"Error in Policy Renewal Receipt - Pay By Cash")

    if(request.args[0] == None):
            raise HTTP(403,"Error in Policy Renewal Receipt - Pay By Cash")

    page    = getgridpage(request.vars)
    mode    = getmode(request.vars.mode)
    logid   = int(common.getid(request.args[0]))


    rows = db(db.paymenttxlog.id == logid).select()
    if(len(rows)==0):
        raise HTTP(403,"Error in Policy Renewal Receipt - Pay By Cash")

    memberpolicyrenewalid = int(common.getid(rows[0].memberpolicyrenewal))
    webmemberid = int(common.getid(rows[0].webmember))
    patientmemberid = int(common.getid(rows[0].patientmember))
    premstartdt = common.getdt(rows[0].premstartdt)
    premenddt   = common.getdt(rows[0].premenddt)
    txdatetime = rows[0].txdatetime
    txno = rows[0].txno
    totpremium = rows[0].totpremium
    totcompanypays=rows[0].totcompanypays
    totyoupay = rows[0].txamount
    total  = rows[0].total
    servicetax = rows[0].servicetax
    swipecharge = rows[0].swipecharge
    paymentdetails = rows[0].responsemssg

    r = db(db.webmember.id == webmemberid).select()
    if(len(r)>0):
        member = r[0].fname + ' ' + r[0].lname + ' (' + r[0].webmember + ')'
        providerid = common.getid(r[0].provider)
    else:
        member = ''
        providerid = 0

    if((mode == "Cash_Check_DD") | (mode == "Company")):
        # update Member Policy Renewal with renewal information
        db((db.memberpolicyrenewal.id == memberpolicyrenewalid) & (db.memberpolicyrenewal.is_active == True)).\
            update(paymenttxlog = logid, renewed = True, premium=totpremium,companyamt=totcompanypays, memberamt=totyoupay,\
                   swipecharge=swipecharge,servicetax=servicetax,total=total, \
                   newrenewaldate=premstartdt, newduedate = premenddt, paymentmode=mode)

        # Update patientmember, webmember with renewal information
        db((db.patientmember.id == patientmemberid)&(db.patientmember.is_active == True) &  (db.patientmember.hmopatientmember == True)).\
            update(premium = total, premstartdt = premstartdt, premenddt = premenddt, terminationdate=premstartdt, duedate = premenddt, status="Enrolled", paid = True, upgraded=False )

        db((db.webmember.id == webmemberid)&(db.webmember.is_active == True)).\
                update(paid = True,status="Enrolled")
        
        welcomekit = emailwelcomekit(request, patientmemberid, providerid)
        
    elif (mode == "None"):
        welcomekit = False
        # Update patientmember, webmember with renewal information
        db((db.patientmember.id == patientmemberid)&(db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).\
            update(premstartdt = premstartdt, premenddt = premenddt, terminationdate=premstartdt, duedate = premenddt, status="Enrolled", paid = True )

        db((db.webmember.id == webmemberid)&(db.webmember.is_active == True)).\
                update(paid = True,status="Enrolled")

    return dict(member=member,paymenttxlog=logid, page=page,txdatetime=txdatetime,txno=txno,totpremium=totpremium,totcompanypays=totcompanypays,\
                totyoupay=totyoupay,total=total,servicetax=servicetax,swipecharge=swipecharge,paymentdetails=paymentdetails,mode=mode,welcomekit=welcomekit)


@auth.requires_membership('webadmin')
@auth.requires_login()
def process_renewals():


    renewalnoticedate = getrenewalnoticedate(datetime.date.today(),getrenewalnoticeperiod())

    memberrows = db((db.patientmember.is_active == True)  &  (db.patientmember.hmopatientmember == True) & (db.patientmember.premenddt <= renewalnoticedate)).\
        select(db.patientmember.id, db.patientmember.premenddt)
    memberpolicyrenewalid = 0

    if(len(memberrows)>0):
        for r in memberrows:
            memberpolicyrenewalid = db.memberpolicyrenewal.update_or_insert(((db.memberpolicyrenewal.patientmember == r.id) & (db.memberpolicyrenewal.is_active==True)),
                                                patientmember = r.id,
                                                renewaldate = r.premenddt,
                                                renewaldays = (r.premenddt - datetime.date.today()).days,
                                                newrenewaldate = getnewrenewaldate(r.premenddt),
                                                is_active = True
                                                )


            rdep = db((db.patientmemberdependants.patientmember == r.id) & (db.patientmemberdependants.is_active == True)).select()
            if(len(rdep)>0):
                for d in rdep:
                    db.dependantpolicyrenewal.insert(
                                                patientmemberdependant = d.id,
                                                memberpolicyrenewal = memberpolicyrenewalid,
                                                is_active = True
                                                )
        redirect(URL('policyrenewal', 'list_renewals'))

    return dict()


@auth.requires_membership('webadmin')
@auth.requires_login()
def send_reminder():
    return dict()

@auth.requires_membership('webadmin')
@auth.requires_login()
def renew_policy():


    if(len(request.args) == 0):
        raise HTTP(403,"Error in Policy Renewal - No Policy")
    if((request.args[0] == None)|(request.args[0] == "")):
        raise HTTP(403,"Error in Policy Renewal - No Policy  (None)")

    
    username = auth.user.first_name + ' ' + auth.user.last_name



    memberpolicyrenewalid = int(request.args[0])
    renewals = db((db.memberpolicyrenewal.id == memberpolicyrenewalid)&(db.memberpolicyrenewal.is_active == True)).\
        select(db.memberpolicyrenewal.ALL,db.patientmember.ALL,\
               left=[db.patientmember.on((db.patientmember.id == db.memberpolicyrenewal.patientmember) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True))])

    if(len(renewals)==0):
        raise HTTP(403,"Error in Policy Renewal - No Policy")

    webmemberid = renewals[0]['patientmember.webmember']
    patientmemberid = renewals[0]['patientmember.id']
    providerid = renewals[0]['patientmember.provider']
    fname = renewals[0]['patientmember.fname']
    lname = renewals[0]['patientmember.lname']
    memberid = renewals[0]['patientmember.id']
    companyid = renewals[0]['patientmember.company']
    planid = renewals[0]['patientmember.hmoplan']
    patientmember = renewals[0]['patientmember.patientmember']
    groupref = renewals[0]['patientmember.groupref']

    prows = db((db.patientmember.id == renewals[0]['patientmember.id']) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    if(len(prows)==0):
        raise HTTP(403,"Error in Policy Renewal - No Patient to Renew")

    premstartdt = getnewrenewaldate(prows[0]["patientmember.premstartdt"])
    premenddt = getpremiumenddate(getnewrenewaldate(premstartdt))

    r = db(db.urlproperties).select()
    if(len(r)>0):
        servicetax = round(Decimal(r[0].servicetax),2)
        swipecharge = round(Decimal(r[0].swipecharge),2)

    ds = getfamilypremiumamount(memberid)
    formheader = "Policy Renewal for " + renewals[0]['patientmember.fname'] + " " + renewals[0]['patientmember.lname'] + "-" + renewals[0]['patientmember.patientmember']

    formA = SQLFORM.factory(
        Field('patientmember', 'string',  widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=patientmember,  label='Member ID'),
        Field('groupref', 'string', widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=groupref,  label='Group Ref.'),
        Field('company', default=companyid, requires=IS_IN_DB(db, 'company.id', '%(name)s')),
        Field('hmoplan', default=planid, requires=IS_IN_DB(db, 'hmoplan.id', '%(name)s')),
        Field('premstartdt', 'date', widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Policy Start Date',requires=IS_DATE(format=('%d/%m/%Y')),length=20,default=premstartdt),
        Field('premenddt', 'date', widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),label='Policy End Date',requires=IS_DATE(format=('%d/%m/%Y')),length=20,default=premenddt)
    )

    if formA.process().accepted:
        if(request.post_vars.paymentgrp == 'paybycc'):
            response.flash="Pay By CC"
            paymenttxlogid = process_payment(memberpolicyrenewalid,webmemberid,patientmemberid,"CreditCard")
            redirect(URL('email_renewalpayment',args=[paymenttxlogid],vars=dict(page=getgridpage(request.vars),mode="CreditCard")))
        elif(request.post_vars.paymentgrp == 'paybycash'):
            response.flash="Pay By Cash"
            paymenttxlogid = process_payment(memberpolicyrenewalid,webmemberid,patientmemberid,"Cash_Check_DD")
            redirect(URL('renewal_payment',args=[paymenttxlogid],vars=dict(page=getgridpage(request.vars),mode="Cash_Check_DD")))

        elif(request.post_vars.paymentgrp == 'paybycomp'):
            response.flash="Pay By Company"
            paymenttxlogid = process_payment(memberpolicyrenewalid,webmemberid,patientmemberid,"Company")
            redirect(URL('renewal_payment',args=[paymenttxlogid],vars=dict(page=getgridpage(request.vars),mode="Company")))
        else:
            response.flash="None"


    elif formA.errors:
        response.flash = 'form has errors'

    page = common.getgridpage(request.vars)
    returnurl=URL('policyrenewal','list_renewals',vars=dict(page=page))
    return dict(username=username, returnurl=returnurl,formA=formA, formheader=formheader, page= page, ds=ds,servicetax=servicetax,swipecharge=swipecharge,total=0)


@auth.requires_membership('webadmin')
@auth.requires_login()
def delete_renewal():
    return dict()



@auth.requires_membership('webadmin')
@auth.requires_login()
def list_renewals():

    username = auth.user.first_name + ' ' + auth.user.last_name

    formheader = "List of Renewals on " + (datetime.date.today()).strftime('%Y-%m-%d')

    fields = (db.patientmember.patientmember,db.patientmember.fname,db.patientmember.mname,db.patientmember.lname,db.company.company, \
              db.hmoplan.name,\
              db.memberpolicyrenewal.renewaldays,db.memberpolicyrenewal.renewaldate,\
              db.memberpolicyrenewal.premium,db.memberpolicyrenewal.renewed,db.memberpolicyrenewal.total)


    db.patientmember.id.readable = False
    db.patientmember.id.writeable = False

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
    db.patientmember.status.readable = False
    
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


    db.hmoplan.id.readable = False
    db.hmoplan.id.writeable = False
    db.hmoplan.hmoplancode.readable = False
    db.hmoplan.hmoplancode.writeable = False
    db.hmoplan.is_active.readable = False
    db.hmoplan.is_active.writeable = False



    db.memberpolicyrenewal.paymenttxlog.writeable = False
    db.memberpolicyrenewal.id.writeable = False
    db.memberpolicyrenewal.is_active.writeable = False
    
    db.memberpolicyrenewal.reminders.writeable = False
    
    db.memberpolicyrenewal.paymentmode.writeable = False
    
    
    db.memberpolicyrenewal.id.readable = False
    
    db.memberpolicyrenewal.id.readable = False
    db.memberpolicyrenewal.patientmember.readable = False
    db.memberpolicyrenewal.paymenttxlog.readable = False

    db.memberpolicyrenewal.renewaldays.readable = False
    db.memberpolicyrenewal.reminders.readable = False
    db.memberpolicyrenewal.reminderdate.readable = False
    db.memberpolicyrenewal.premium.readable = False
    db.memberpolicyrenewal.companyamt.readable = False
    db.memberpolicyrenewal.memberamt.readable = False
    db.memberpolicyrenewal.swipecharge.readable = False
    db.memberpolicyrenewal.servicetax.readable = False
    db.memberpolicyrenewal.total.readable = False
    db.memberpolicyrenewal.newrenewaldate.readable = False
    db.memberpolicyrenewal.newduedate.readable = False
    db.memberpolicyrenewal.paymentmode.readable = False
 
    db.memberpolicyrenewal.is_active.readable = False    


   

    headers={   'patientmember.patientmember':'Member ID',
                'patientmember.fname':'First Name',
                'patientmember.mname':'Middle Name',
                'patientmember.lname':'Last Name',
                'company.company': 'Company',
                'hmoplan.name': 'Plan',
                'memberpolicyrenewal.renewaldate':'Renew By',
                'memberpolicyrenewal.renewaldays':'Days To Renewal',
                'memberpolicyrenewal.premium':'Premium Amt.',
                'memberpolicyrenewal.renewed':'Renewed',
                'memberpolicyrenewal.total':'Paid Amt.'
               }


    query = ((db.memberpolicyrenewal.is_active == True) & (db.memberpolicyrenewal.renewed == False))

    left = [db.patientmember.on((db.patientmember.id==db.memberpolicyrenewal.patientmember) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)),
            db.company.on(db.company.id==db.patientmember.company),
            db.hmoplan.on(db.hmoplan.id==db.patientmember.hmoplan)]

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)



    links = None
    selectable  = None

    #links = [lambda row: A('Renew',_href=URL("policyrenewal","renew_policy",vars=dict(page=getgridpage(request.vars)), args=[row.memberpolicyrenewal.id])), lambda row: A('Remind',_href=URL("policyrenewal","send_reminder",vars=dict(page=getgridpage(request.vars)),args=[row.memberpolicyrenewal.id])), lambda row: A('Delete',_href=URL("policyrenewal","delete_renewal",vars=dict(page=getgridpage(request.vars)),args=[row.memberpolicyrenewal.id]))]
    links = [lambda row: A('Renew',_href=URL("policyrenewal","renew_policy",vars=dict(page=getgridpage(request.vars)), args=[row.memberpolicyrenewal.id]))]


    #selectable = lambda ids : redirect(URL('my_dentalplan','policyrenewal','renew_policies',args=(ids)))

    formA = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        left=left,
                        paginate=10,
                        selectable=selectable,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=False)

    returnurl=URL('default','index')
    return dict(username=username,returnurl=returnurl,formA = formA, formheader=formheader)

@auth.requires_membership('webadmin')
@auth.requires_login()
def group_renewal():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    
    letters = os.listdir(os.path.join(request.folder, 'templates/welcomeletter'))
    letteroptions=[welcomeletter for welcomeletter in letters] 
            
    returnurl = URL('default', 'main')
    
    company = 0

    companys = db(db.company.company == 'SABRE').select()
    company = companys[0].id
    
    #if(request.vars.company == None):
        #companys = db(db.company.company == 'SABRE').select()
        #company = companys[0].id
    #else:
        #company = int(common.getid(request.vars.company))

    
    fromdt = common.getstring(request.vars.fromdt)
    todt  =  common.getstring(request.vars.todt)
    newdt = common.getstring(request.vars.newdt)
    

    #if((fromdt != "") & (todt != "")):

        #formA = SQLFORM.factory(
                  #Field('company',  label='Company',default=company, requires=IS_IN_DB(db(db.company.is_active == True),db.company.id, '%(name)s (%(company)s)')),
                  #Field('fromdt', 'date', label='From Current Enroll Date', default=datetime.datetime.strptime(fromdt , '%Y-%m-%d').date(),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
                  #Field('todt', 'date', label='To Current Enroll Date',  default=datetime.datetime.strptime(todt , '%Y-%m-%d').date(), requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
                  #Field('newdt', 'date',   label='New Policy Start Date',  default=datetime.datetime.strptime(newdt , '%Y-%m-%d').date(),requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))))
                 
              #)    
    #else:
    formA = SQLFORM.factory(
              Field('company',  label='Company',default=company, requires=IS_IN_DB(db(db.company.is_active == True),db.company.id, '%(name)s (%(company)s)')),
              Field('fromdt', 'date', label='From Current Enroll Date', requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
              Field('todt', 'date', label='To Current Enroll Date',   requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
              Field('newdt', 'date',   label='New Policy Start Date',  requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))))
             
          )    

    
    
    submit = formA.element('input',_type='submit')
    submit['_value'] = 'Renew'   
    renewalcount = 0
    
    #if formA.process().accepted:
    if formA.accepts(request,session,keepvalues=True):        
        fromdt = datetime.datetime.strptime(request.vars.fromdt,'%d/%m/%Y')
        todt   = datetime.datetime.strptime(request.vars.todt,'%d/%m/%Y')
        newdt  = request.vars.newdt
        company = request.vars.company
        
        members = db((db.patientmember.premstartdt >= fromdt) & (db.patientmember.premstartdt <= todt) & (db.patientmember.company == company) & (db.patientmember.renewed==False) & \
                     (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
        
 
        
        if(newdt != ""):
            premstartdt = datetime.datetime.strptime(newdt , '%d/%m/%Y').date()
            terminationdt = getnewrenewaldate(premstartdt)
            premenddt = getpremiumenddate(terminationdt)
            renewalcount = db((db.patientmember.premstartdt >= fromdt) & (db.patientmember.premstartdt <= todt) & (db.patientmember.company == company) & (db.patientmember.renewed==False) & \
                              (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).\
                update(premstartdt=premstartdt,premenddt=premenddt,\
                terminationdate=terminationdt,duedate=premenddt,\
                paid=True,upgraded=False,renewed=True)            
            db.commit()
            
            for member in members:
                ret = mail.emailWelcomeKit(db,request,member.id, member.provider)
        else:
            for member in members:
                renewalcount += 1
                #logger.logger.info("Renewing Patient Member: %s %s %s  %s  %d", member.patientmember, member.fname, member.lname , member.groupref, member.company)
                premstartdt = getnewrenewaldate(member.premstartdt)
                terminationdt = getnewrenewaldate(premstartdt)
                premenddt = getpremiumenddate(terminationdt)
                db((db.patientmember.id == member.id) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).update(premstartdt=premstartdt,premenddt=premenddt,\
                                                            terminationdate=terminationdt,duedate=premenddt,\
                                                            paid=True,upgraded=False,renewed=True)
    
                ret = mail.emailWelcomeKit(db,request,member.id, member.provider)
                if(renewalcount % 2 == 0):
                    db.commit()
                    break

    return dict(formA=formA,username=username, returnurl=returnurl, page=0, renewalcount=renewalcount)


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




    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)

    #IB 05292016
    links = [lambda row: A('Policy Upgrade',_href=URL("policyrenewal","upgrade_policy",vars=dict(page=page,memberid=row.patientmember.id))),\
             lambda row: A('Member Card',_href=URL("member","member_card",vars=dict(page=page,returnurl='policyrenewal'),args=[row.patientmember.id])),\
             lambda row: A('Welcome Kit',_href=URL("default","emailwelcomekit_0",vars=dict(page=page,returnurl='policyrenewal'),args=[row.patientmember.id]))]

    query = ((db.patientmember.is_active==True) & (db.patientmember.hmopatientmember == True))

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
                        user_signature=True
                       )
    returnurl = URL('policyrenewal','list_member',vars=dict(page=1))
    return dict(username=username, returnurl=returnurl, form=form, formheader=formheader,page=page) #IB 05292016

@auth.requires_membership('webadmin')
@auth.requires_login()
def delete_dependant():
    
    memberid = int(common.getid(request.vars.memberid))
    depid = int(common.getid(request.vars.dependantid))
    page=common.getgridpage(request.vars)
    
    rows = db(db.patientmemberdependants.id == depid).select()
    if(len(rows) == 0):
        raise HTTP(400,"Nothing to delete ")
    
    name = rows[0].fname + ' ' + rows[0].lname
    
    form = FORM.confirm('Yes?',{'No':URL('policyrenewal','upgrade_policy',vars=dict(memberid=memberid,page=page))})

    if form.accepted:
        members = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select(db.patientmember.webmember)
        webmemberid = int(common.getid(members[0].webmember))
        webmembers = db(db.patientmemberdependants.id == depid).select(db.patientmemberdependants.fname,db.patientmemberdependants.lname)
        fname = webmembers[0].fname
        lname = webmembers[0].lname
        
        db(db.patientmemberdependants.id == depid).delete()
        
        db((db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.fname == fname) \
           & (db.webmemberdependants.lname == lname)).delete()
        
        redirect(URL('policyrenewal','upgrade_policy',vars=dict(memberid=memberid,page=page)))

    return dict(form=form,memberid=memberid,name=name)


def acceptupdate_dependant(form):

    dependantid = int(common.getid(form.vars.id))
    memberid = request.vars.memberid
    page = request.vars.page
    rows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    webmemberid = int(common.getid(rows[0].webmember))
    
    

    deps = db(db.patientmemberdependants.id == dependantid).select() 
    if(len(deps)>0):
        db(db.webmemberdependants.patdepid == dependantid).update(\
            fname = deps[0].fname,\
            mname = deps[0].mname,\
            lname = deps[0].lname,\
            depdob = deps[0].depdob,\
            gender = deps[0].gender,\
            relation = deps[0].relation,\
            webmember = webmemberid,\
            is_active = True,\
            memberorder = deps[0].memberorder,\
            paid = deps[0].paid,\
            created_by = deps[0].created_by,\
            created_on = deps[0].created_on,\
            modified_by = deps[0].modified_by,\
            modified_on = deps[0].modified_on)
            
    redirect(URL('policyrenewal','upgrade_policy',vars=dict(page=page,memberid=memberid)))
    return dict()

def acceptcreate_dependant(form):

    dependantid = int(common.getid(form.vars.id))
    memberid = request.vars.memberid
    page = request.vars.page
    
    rows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    webmemberid = int(common.getid(rows[0].webmember))
    

    deps = db(db.patientmemberdependants.id == dependantid).select()    
    if(len(deps)>0):
        db.webmemberdependants.insert(fname = deps[0].fname,\
                                      mname = deps[0].mname,\
                                      lname = deps[0].lname,\
                                      depdob = deps[0].depdob,\
                                      gender = deps[0].gender,\
                                      relation = deps[0].relation,\
                                      webmember = webmemberid,\
                                      patdepid = dependantid,\
                                      is_active = True,\
                                      memberorder = deps[0].memberorder,\
                                      paid = deps[0].paid,\
                                      created_by = deps[0].created_by,\
                                      created_on = deps[0].created_on,\
                                      modified_by = deps[0].modified_by,\
                                      modified_on = deps[0].modified_on)
        
    redirect(URL('policyrenewal','create_dependant',vars=dict(page=page,memberid=memberid)))
    return dict()

def acceptupdate_upgradepolicy(form):
    
    webmemberid = form.vars.webmember
    planid = form.vars.hmoplan
    companyid = form.vars.company
    regionid = form.vars.groupregion
    
    memberid = request.vars.memberid
    page = request.vars.page
    db(db.webmember.id == webmemberid).update(company=companyid, hmoplan=planid, groupregion = regionid)
    redirect(URL('policyrenewal','upgrade_policy',vars=dict(page=page,memberid=memberid)))
    return dict()
    
@auth.requires_membership('webadmin')
@auth.requires_login()
def upgrade_policy():
    i = 0
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    returnurl = URL('default', 'main')
    
    page = common.getgridpage(request.vars)
    memberid = int(common.getid(request.vars.memberid))
    
    
    rows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True)).select()
    
    companyid = int(common.getid(rows[0].company))
    providerid = int(common.getid(rows[0].provider))
    planid = int(common.getid(rows[0].hmoplan))
    regionid = int(common.getid(rows[0].groupregion))
    status = rows[0].status
    lastpaid = round(float(common.getvalue(rows[0].premium)),2)

    #x = db(db.company.id == companyid).select()
    #if(len(x)>0):
        #maxsubscribers = int(x[0].maxsubscribers)    
    #else:
        #maxsubscribers = 1

    x = db((db.companyhmoplanrate.company==companyid) & \
        (db.companyhmoplanrate.hmoplan==planid) &  \
        (db.companyhmoplanrate.groupregion==regionid) & \
        (db.companyhmoplanrate.is_active==True)).select()

    if(len(x)>0):
        maxsubscribers = int(len(x))
    else:
        maxsubscribers = 1
    

    subscribers = 1 + db((db.patientmemberdependants.patientmember == memberid) & \
                         (db.patientmemberdependants.is_active == True)).count()

    pin = ''
    pin1 = ''
    pin2 = ''
    pin3 = ''
    rows1 = db(db.webmember.webmember == rows[0].patientmember).select()
    if(len(rows1) > 0):
        pin = rows1[0].pin
        pin1 = rows1[0].pin1
        pin2 = rows1[0].pin2
        pin3 = rows1[0].pin3
        
    query = (db.hmoplan.groupregion == regionid)
    
    
    
    plans = db((db.companyhmoplanrate.groupregion==regionid) & (db.companyhmoplanrate.company==companyid)& (db.companyhmoplanrate.relation=='Self')).\
            select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
                   left=db.hmoplan.on(db.companyhmoplanrate.hmoplan == db.hmoplan.id),distinct=True)    
    
    #db.patientmember.hmoplan.requires=IS_IN_DB(db(db.hmoplan.groupregion == regionid),'hmoplan.id', ' %(name)s (%(hmoplancode)s)')
        
        
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('policyrenewal','upgrade_policy',vars=dict(page=page,memberid=memberid))
    crud.settings.update_onaccept = acceptupdate_upgradepolicy
    formA = crud.update(db.patientmember, memberid,cast=int,message="Member Information Updated!")
    

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
    links = [lambda row: A('Update',_href=URL("policyrenewal","update_dependant", vars=dict(dependantid=row.id,memberid=memberid,page=page))),
             lambda row: A('Delete',_href=URL("policyrenewal","delete_dependant", vars=dict(dependantid=row.id,memberid=memberid,page=page)))]

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

    status = "Attempting"
    showenrollment=checkenrollment(formA,status)
        
    return dict(username=username,returnurl=returnurl,formA=formA,formB=formB,subscribers=subscribers,\
                maxsubscribers=maxsubscribers, showenrollment=showenrollment,memberid=memberid,lastpaid=lastpaid,page=page,plans=plans,planid=planid)
            
    
@auth.requires_membership('webadmin')
@auth.requires_login()
def upgrade_premiumpayment():

    formheader = "Payment Details"
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    page = common.getgridpage(request.vars)
    memberid = int(common.getid(request.vars.memberid))
    lastpaid = round(float(common.getvalue(request.vars.lastpaid)),2)
    
    ds = getfamilypremiumamount(memberid)


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

    returnurl = URL('policyrenewal','upgrade_policy', vars=dict(memberid=memberid,page=page))
    return dict(username=username,returnurl=returnurl,ds=ds, formheader=formheader, memberid=memberid,txno=txno,servicetaxes=servicetaxes,swipecharges=swipecharges,total=total,\
                swipecharge=swipecharge, servicetax=servicetax, lastpaid=lastpaid,page=page)


@auth.requires_membership('webadmin')
@auth.requires_login()
def upgrade_policy_paybycash():

    username = auth.user.first_name + ' ' + auth.user.last_name
    page = getgridpage(request.vars)
    logid = int(common.getid(request.vars.paymenttxlogid))   
    mode    = getmode(request.vars.mode)
    lastpaid = round(float(common.getvalue(request.vars.lastpaid)), 2)
    returnurl = URL('policyrenewal','list_member', vars=dict(page=page))

    rows = db(db.paymenttxlog.id == logid).select()
    if(len(rows)==0):
        raise HTTP(403,"Error in Policy Renewal Receipt - Pay By Cash")

    memberpolicyrenewalid = int(common.getid(rows[0].memberpolicyrenewal))
    webmemberid = int(common.getid(rows[0].webmember))
    patientmemberid = int(common.getid(rows[0].patientmember))
    txdatetime = rows[0].txdatetime
    txno = rows[0].txno
    totpremium = rows[0].totpremium    
    totcompanypays=rows[0].totcompanypays  
    totyoupay = rows[0].txamount   
    total  = rows[0].total   
    servicetax = rows[0].servicetax
    swipecharge = rows[0].swipecharge
    paymentdetails = rows[0].responsemssg
    premstartdt = common.getdt(rows[0].premstartdt)
    premenddt   = common.getdt(rows[0].premenddt)
    

    r = db((db.patientmember.id == patientmemberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    if(len(r)>0):
        member = r[0].fname + ' ' + r[0].lname + ' (' + str(r[0].webmember) + ')'
    else:
        member = ''


    if((mode == "Cash_Check_DD") | (mode == "Company")):
        # Update patientmember, webmember with renewal information
        premium = totyoupay + servicetax + swipecharge
        db((db.patientmember.id == patientmemberid)&(db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).\
            update(premium = premium, premstartdt = premstartdt, premenddt = premenddt, terminationdate=premstartdt, duedate = premenddt, status="Enrolled", paid = True, upgraded = True )

        db((db.patientmemberdependants.patientmember == patientmemberid)&(db.patientmemberdependants.is_active == True)).\
            update(paid = True)

        db((db.webmember.id == webmemberid)&(db.webmember.is_active == True)).\
                update(paid = True,status="Enrolled", upgraded=True)
        db(db.webmemberdependants.webmember == webmemberid).update(paid=True)        
        
    elif (mode == "None"):
        # Update patientmember, webmember with renewal information
        db((db.patientmember.id == patientmemberid)&(db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).\
            update(premstartdt = premstartdt, premenddt = premenddt, terminationdate=premstartdt, duedate = premenddt, status="Enrolled", paid = True, upgraded=True )

        db((db.patientmemberdependants.patientmember == patientmemberid)&(db.patientmemberdependants.is_active == True)).\
                update(paid = True)
        
        db((db.webmember.id == webmemberid)&(db.webmember.is_active == True)).\
                update(paid = True,status="Enrolled",upgraded=True)
        db(db.webmemberdependants.webmember == webmemberid).update(paid=True)
        
    return dict(username=username,returnurl=returnurl,member=member,paymenttxlog=logid, page=page,txdatetime=txdatetime,txno=txno,totpremium=totpremium,totcompanypays=totcompanypays,\
                totyoupay=totyoupay,total=total,servicetax=servicetax,swipecharge=swipecharge,paymentdetails=paymentdetails,mode=mode,lastpaid=lastpaid)



def email_upgrade_policy_payment_function(page, memberid, webmemberid, paymenttxlogid, lastpaid):
    
    server = None
    sender = None
    login = None
    tls = False
    retval = False;
    
    r = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    if(len(r) == 0):
        retval = False;
    
    memberemail = r[0].email
    membername = r[0].fname + ' ' + r[0].lname


    props = db(db.urlproperties.id>0).select()
    if(len(props)>0):
        server = props[0].mailserver + ":"  + props[0].mailserverport
        sender = props[0].mailsender
        login  = props[0].mailusername + ":" + props[0].mailpassword
        port = int(props[0].mailserverport)
        if((port != 25) & (port != 26)):
            tls = True
        else:
            tls = False

        if((props[0].mailusername == 'None')):
                    login = None
    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")

    normaltime = time.asctime(time.localtime(time.time())).encode('base64','strict')
    str1 = normaltime +'_'+ str(paymenttxlogid)
    encodedarg = str1.encode('base64','strict')
    renewalpaymentlink = props[0].mydp_ipaddress + "/my_dentalplan/policyrenewal/upgrade_policy_payment_cc/" + encodedarg

    mail = Mail()
    mail.settings.server = server
    mail.settings.sender = sender
    mail.settings.login =  login
    mail.settings.tls = tls

    to      =  memberemail
    subject = "Policy Upgrade Payment Link"


    appPath = request.folder
    htmlfile = os.path.join(appPath, 'templates','Reminder_Upgrade_Policy.html')

    f = open(htmlfile,'rb')
    html = Template(f.read())
    f.close()

    result  = html.safe_substitute(renewalpaymentlink=renewalpaymentlink)
    retVal = mail.send(to,subject,result,encoding='utf-8')
    
    
    
    return retVal


@auth.requires_membership('webadmin')
@auth.requires_login()
def email_upgrade_policy_payment():

    server = None
    sender = None
    login = None
    tls = False

  
    
    page = getgridpage(request.vars)
    memberid = int(common.getid(request.vars.memberid))
    webmemberid = int(common.getid(request.vars.webmemberid))
    paymenttxlogid = int(common.getid(request.vars.paymenttxlogid))
    lastpaid = round(float(common.getvalue(request.vars.lastpaid)), 2)
    r = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    if(len(r) == 0):
        raise HTTP(403,"Error in Upgrade Policy By CC - Invalid Member")
    
    memberemail = r[0].email
    membername = r[0].fname + ' ' + r[0].lname


    props = db(db.urlproperties.id>0).select()
    if(len(props)>0):
        server = props[0].mailserver + ":"  + props[0].mailserverport
        sender = props[0].mailsender
        login  = props[0].mailusername + ":" + props[0].mailpassword
        port = int(props[0].mailserverport)
        if((port != 25) & (port != 26)):
            tls = True
        else:
            tls = False

        if((props[0].mailusername == 'None')):
                    login = None
    else:
        retVal = False
        raise HTTP(400,"Mail attributes not found")

    normaltime = time.asctime(time.localtime(time.time())).encode('base64','strict')
    str1 = normaltime +'_'+ str(paymenttxlogid)
    encodedarg = str1.encode('base64','strict')
    renewalpaymentlink = props[0].mydp_ipaddress + "/my_dentalplan/policyrenewal/upgrade_policy_payment_cc/" + encodedarg

    mail = Mail()
    mail.settings.server = server
    mail.settings.sender = sender
    mail.settings.login =  login
    mail.settings.tls = tls

    to      =  memberemail
    subject = "Policy Upgrade Payment Link"


    appPath = request.folder
    htmlfile = os.path.join(appPath, 'templates','Reminder_Upgrade_Policy.html')

    f = open(htmlfile,'rb')
    html = Template(f.read())
    f.close()

    result  = html.safe_substitute(renewalpaymentlink=renewalpaymentlink)
    retVal = mail.send(to,subject,result,encoding='utf-8')

    return dict(ret=retVal, membername=membername, memberemail=memberemail,page=page)


@auth.requires_membership('webadmin')
@auth.requires_login()
def upgrade_policy_processpayment():
    
    
    page = common.getgridpage(request.vars)
    memberid = int(common.getid(request.vars.memberid))
    lastpaid = round(float(common.getvalue(request.vars.lastpaid)),2)
    rows= db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
    webmemberid = int(common.getid(rows[0].webmember))
   
    if(request.vars.paymentgrp == 'paybycc'):
        paymenttxlogid = process_payment(memberid,webmemberid,memberid,"CreditCard")
        redirect(URL('email_upgrade_policy_payment',vars=dict(paymenttxlogid=paymenttxlogid,memberid=memberid,webmemberid=webmemberid,page=page,lastpaid=lastpaid,mode="CreditCard")))
    elif(request.vars.paymentgrp == 'paybycash'):
        response.flash="Pay By Cash"
        paymenttxlogid = process_payment(memberid,webmemberid,memberid,"Cash_Check_DD")
        redirect(URL('upgrade_policy_paybycash',vars=dict(paymenttxlogid=paymenttxlogid,page=page,lastpaid=lastpaid,mode="Cash_Check_DD")))

    elif(request.vars.paymentgrp == 'paybycomp'):
        response.flash="Pay By Company"
        paymenttxlogid = process_payment(memberid,webmemberid,memberid,"Company")
        redirect(URL('upgrade_policy_paybycash',vars=dict(paymenttxlogid=paymenttxlogid,page=page,mode="Company")))
    else:
        response.flash="None"
    
    return dict()
    

#IB 05292016
def create_dependant():

    username = auth.user.first_name + ' ' + auth.user.last_name
    page         = common.getgridpage(request.vars)
    memberid     = int(common.getid(request.vars.memberid))

    fname = None
    lname = None
    formheader   = "Add New Dependant"

    companyid = 0
    hmoplanid = 0
    relations = None

    memberrows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).\
        select(db.patientmember.ALL)


    fname = memberrows[0]['webmember.fname']
    lname = memberrows[0]['webmember.lname']
    hmoplanid = int(common.getid(memberrows[0].hmoplan))
    regionid = int(common.getid(memberrows[0].groupregion))
    companyid = int(common.getid(memberrows[0].company))


    relations = db((db.companyhmoplanrate.company == companyid) & \
                   (db.companyhmoplanrate.hmoplan == hmoplanid) & \
                   (db.companyhmoplanrate.groupregion == regionid) & \
                   (db.companyhmoplanrate.is_active == True) & \
                   (db.companyhmoplanrate.relation.lower() != 'self')).select(db.companyhmoplanrate.relation)
    
    rows = db(db.patientmemberdependants.patientmember == memberid).select()
    dependantnumber = len(rows) + 2


    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.create_onaccept = acceptcreate_dependant
    db.patientmemberdependants.patientmember.default = memberid
    db.patientmemberdependants.memberorder.default = dependantnumber
    db.patientmemberdependants.patientmember.writable = False
    db.patientmemberdependants.memberorder.writable = False
    if(len(relations) > 0):
        db.patientmemberdependants.relation.default = relations[0].relation
        
    #IB 05292016
    crud.settings.create_next = URL('policyrenewal','create_dependant',vars=dict(page=page,memberid=memberid))

    formA = crud.create(db.patientmemberdependants, message='New Member Dependant Added!')

    fields=(db.patientmemberdependants.fname,db.patientmemberdependants.lname,db.patientmemberdependants.gender,\
            db.patientmemberdependants.depdob,db.patientmemberdependants.relation)

    headers={'patientmemberdependants.fname':'First Name',
             'patientmemberdependants.lname': 'Last Name',
             'patientmemberdependants.depdob': 'DOB',
             'patientmemberdependants.gender': 'Gender',
             'patientmemberdependants.relation':'Relation'
             }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False, csv=False)

    left  = None
    links = None

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


    returnurl = URL('policyrenewal','upgrade_policy', vars=dict(page=page,memberid=memberid))
    return dict(username=username,returnurl=returnurl,formA=formA,  formB=formB, formheader=formheader,memberid=memberid,fname=fname,lname=lname,relations=relations,page=page)

#IB 05292016
def update_dependant():

    username = auth.user.first_name + ' ' + auth.user.last_name
    
    formheader="Update Member Dependant Data"
        
    page         = common.getgridpage(request.vars)
    memberid     = int(common.getid(request.vars.memberid))
    dependantid     = int(common.getid(request.vars.dependantid))



    memberrows = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).\
           select(db.patientmember.ALL)
   
   
    fname = memberrows[0].fname
    lname = memberrows[0].lname
    hmoplanid = int(common.getid(memberrows[0].hmoplan))
    regionid = int(common.getid(memberrows[0].groupregion))
    companyid = int(common.getid(memberrows[0].company))    
    webmemberid = int(common.getid(memberrows[0].webmember))

  

    relations = db((db.companyhmoplanrate.company == companyid) & \
                   (db.companyhmoplanrate.hmoplan == hmoplanid) & \
                   (db.companyhmoplanrate.groupregion == regionid) & \
                   (db.companyhmoplanrate.is_active == True) & \
                   (db.companyhmoplanrate.relation.lower() != 'self')).select(db.companyhmoplanrate.relation)

    rows = db(db.patientmemberdependants.id == dependantid).select()
    
    if(len(rows)>0):
        relation = rows[0].relation
        depfname = rows[0].fname
        deplname = rows[0].lname
        depdob = rows[0].depdob
        
        x = db((db.webmemberdependants.webmember == webmemberid) & (db.webmemberdependants.fname == depfname) \
                   & (db.webmemberdependants.lname == deplname)  \
                   & (db.webmemberdependants.depdob == depdob)  \
                   & (db.webmemberdependants.relation == relation)).select()
        
        if(len(x)>0):
            webdepid = int(common.getid(x[0].id))
        else:
            webdepid = 0
        
    else:
        raise HTTP(403,"There are no relations")

    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = URL('policyrenewal','upgrade_policy',vars=dict(page=page,memberid=memberid))
    crud.settings.update_onaccept = acceptupdate_dependant
    db.patientmemberdependants.patientmember.default = memberid
    db.patientmemberdependants.relation.default = relation
    db.patientmemberdependants.paid.writable = False
    formA = crud.update(db.patientmemberdependants, dependantid,cast=int, message='Member Dependant Information Updated!')
    
    returnurl = URL('policyrenewal','upgrade_policy',vars=dict(page=page,memberid=memberid))

    return dict(username=username,returnurl=returnurl,formA=formA, formheader=formheader, memberid=memberid,fname=fname,lname=lname,relations=relations,selectedrelation=relation,page=page)


def fromcompanys():

    fromcompanys = db(db.company.is_active == True).select(orderby=db.company.name)
    
    return dict(fromcompanys = fromcompanys)

def tocompanys():

    tocompanys = db(db.company.is_active == True).select(orderby=db.company.name)
    
    return dict(tocompanys = tocompanys)
    

def fromplans():
    
    regionid = common.getid(request.vars.groupregion)
    companyid = common.getid(request.vars.frcompany)
    
    plans = db((db.companyhmoplanrate.groupregion==regionid) & (db.companyhmoplanrate.company==companyid) & \
              (db.companyhmoplanrate.relation == 'Self') & (db.hmoplan.is_active==True)).\
       select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
              left=db.hmoplan.on(db.companyhmoplanrate.hmoplan == db.hmoplan.id),distinct=True)
            
        
    
    return dict(plans = plans)

def toplans():
    
    regionid = common.getid(request.vars.groupregion)
    companyid = common.getid(request.vars.tocompany)
    
    plans = db((db.companyhmoplanrate.groupregion==regionid) & (db.companyhmoplanrate.company==companyid) & \
              (db.companyhmoplanrate.relation == 'Self') & (db.hmoplan.is_active==True)).\
       select(db.hmoplan.id,db.hmoplan.hmoplancode,db.hmoplan.name,\
              left=db.hmoplan.on(db.companyhmoplanrate.hmoplan == db.hmoplan.id),distinct=True)
            
        
    
    return dict(toplans = plans)


def upgrade_one_policy(memberid, regionid, frcompany, frhmoplan, tocompany, tohmoplan, newpremstartdt, newpremenddt):

    totpremium = 0  
    totcompanypays = 0
    totyoupay = 0           #A
    servicetaxes = 0        #B
    swipecharges = 0        #C
    lastpaid = 0            #D
    total = 0               #A+B+C-D

    premstartdt = None
    premenddt = None
    
    servicetax = 0
    swipecharge = 0
    
    responsecode = "CreditCard"
    paymentdetails = "Group Ugrade Payment"
    
    #set transaction time and id
    txdatetime = datetime.datetime.now()
    txno = str(memberid) + "_" + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S")
    
    # get member last premium paid, premstartdt, premenddt
    ds = db(db.patientmember.id == memberid).select(db.patientmember.premium,db.patientmember.premstartdt,db.patientmember.premenddt)
    if(len(ds)>0):
        lastpaid = common.getvalue(ds[0]['premium'])
        premstartdt = common.getnulldt(ds[0]['premstartdt'])
        premenddt = common.getnulldt(ds[0]['premenddt'])

    # update members upgraded company and policy
    db(db.patientmember.id == memberid).update(company = tocompany, hmoplan = tohmoplan)
    db.commit()

    # Calculate new premium amounts
    ds = getfamilypremiumamount(memberid)
    
    if(len(ds)>0):
        for i in xrange(0,len(ds)):
            totpremium = totpremium + round(Decimal(ds[i][4]),2)
            totcompanypays = totcompanypays + round(Decimal(ds[i][5]),2)
            totyoupay = totpremium - totcompanypays

        #if(totyoupay <= 0):
            #db(db.webmember.id == webmemberid).update(status = 'Completed')

        r = db(db.urlproperties).select()
        if(len(r)>0):
            servicetax = round(Decimal(r[0].servicetax),2)
            swipecharge = round(Decimal(r[0].swipecharge),2)
        servicetaxes = round(totyoupay * servicetax / 100,2)
        swipecharges = round(totyoupay * swipecharge/ 100,2)
        
    total = totyoupay + servicetaxes + swipecharges - lastpaid

    #determine premstartdt and premenddt of the upgraded policy
    
    # new premstartdt at the start of group upgrade process
    if((newpremstartdt != None) & (newpremstartdt != "")):
        premstartdt = common.getnulldt(newpremstartdt)
        premenddt = common.getnulldt(newpremenddt)
    else:
        #calculate from member's premstartdt of the current poliocy
        r = db((db.patientmember.id == memberid) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True)).select()
        if(len(r)>0):
                premstartdt =  common.getnulldt(r[0].premenddt)
                premenddt  = getpremiumenddate(getnewrenewaldate(premstartdt))
        else:
            premstartdt = common.getdt(None)
            premenddt = getpremiumenddate(getnewrenewaldate(premstartdt))
            

    
    paymenttxlogid = db.paymenttxlog.insert(txno=txno,txdatetime=txdatetime,\
                                   txamount=totyoupay,totpremium=totpremium,totcompanypays=totcompanypays,\
                                   total=total,servicetax=servicetaxes,swipecharge=swipecharges,responsecode=responsecode,\
                                   responsemssg=paymentdetails,premstartdt=premstartdt,premenddt=premenddt, \
                                   memberpolicyrenewal = memberid, patientmember = memberid)
    
    
    db.commit()

    #Email Upgrade Email
    retval = email_upgrade_policy_payment_function(1, memberid, 0, paymenttxlogid, lastpaid)
    
    
    
    return retval

def upgrade_policy_link():

    uid = request.vars.id
    regionid = common.getid(request.vars.regionid)
    frcompany = common.getid(request.vars.frcompany)
    frhmoplan = common.getid(request.vars.frhmoplan)
    tocompany = common.getid(request.vars.tocompany)
    tohmoplan = common.getid(request.vars.tohmoplan)     
    
    newpremstartdt = common.getnulldt(request.vars.newpremstartdt)
    newpremenddt = common.getnulldt(request.vars.newpremenddt)

    lastPaidAmt  = 0
    
    success = 0
    error = 0
    

    retval = upgrade_one_policy(uid, regionid, frcompany, frhmoplan, 
                      tocompany, tohmoplan, 
                      newpremstartdt, 
                      newpremenddt)
    if(retval == True):
        success = success + 1
    else:
        error = error + 1
    
    returnurl = URL('policyrenewal','group_upgrade')
    
    return dict(success=success, error=error,returnurl=returnurl)

def upgrade_policies():

    uids = request.vars.id
    regionid = common.getid(request.vars.regionid)
    frcompany = common.getid(request.vars.frcompany)
    frhmoplan = common.getid(request.vars.frhmoplan)
    tocompany = common.getid(request.vars.tocompany)
    tohmoplan = common.getid(request.vars.tohmoplan)     
    
    newpremstartdt = common.getnulldt(request.vars.newpremstartdt)
    newpremenddt = common.getnulldt(request.vars.newpremenddt)

    lastPaidAmt  = 0
    
    success = 0
    error = 0
    
    for uid in uids:
        retval = upgrade_one_policy(uid, regionid, frcompany, frhmoplan, 
                          tocompany, tohmoplan, 
                          newpremstartdt, 
                          newpremenddt)
        if(retval == True):
            success = success + 1
        else:
            error = error + 1
    
    returnurl = URL('policyrenewal','group_upgrade')
    
    return dict(success=success, error=error,returnurl=returnurl)
    
def list_upgrades():

    username = auth.user.first_name + ' ' + auth.user.last_name
    returnurl = URL('policyrenewal', 'group_upgrade')

    page = 1
    regionid = common.getid(request.vars.regionid)
    frcompany = common.getid(request.vars.frcompany)
    frhmoplan = common.getid(request.vars.frhmoplan)
    tocompany = common.getid(request.vars.tocompany)
    tohmoplan = common.getid(request.vars.tohmoplan)
    newpremstartdt = common.getnulldt(request.vars.newpremstartdt)
    newpremenddt = common.getnulldt(request.vars.newpremenddt)
    
    #query = ((db.vw_memberpatientlist.is_active==True) & (db.vw_memberpatientlist.hmopatientmember == True))
    

    query = ((db.patientmember.is_active==True) & (db.patientmember.hmopatientmember == True)  &\
             (db.patientmember.groupregion == regionid)  & (db.patientmember.company == frcompany) & (db.patientmember.hmoplan == frhmoplan) )

    
    fields=(db.patientmember.id,db.patientmember.patientmember, \
            db.patientmember.fname, db.patientmember.lname, db.patientmember.cell, db.patientmember.email,\
            db.patientmember.company,db.patientmember.hmoplan,db.patientmember.upgraded)
    

    headers={
        'patientmember.id':'ID',
        'patientmember.patientmember':'Member ID',
        'patientmember.fname':'First',
        'patientmember.lname':'Last',
        'patientmember.cell':'Cell',
        'patientmember.email':'Email',
        'patientmember.upgraded':'Upgraded'
        
    }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)


    links = [lambda row: A('Policy Upgrade',_href=URL("policyrenewal","upgrade_policy_link",\
                                                      vars=dict(page=page,id=row.id,regionid=regionid,newpremstartdt=newpremstartdt,newpremenddt=newpremenddt,\
                                                                frcompany=frcompany,frhmoplan=frhmoplan,tocompany=tocompany,tohmoplan=tohmoplan)))]
    

    orderby = ~(db.patientmember.id)

    selectable = lambda ids : redirect(URL('policyrenewal','upgrade_policies',  vars=dict(id=ids, page=page,regionid=regionid,\
                                                              frcompany=frcompany,frhmoplan=frhmoplan,tocompany=tocompany,tohmoplan=tohmoplan,newpremstartdt=newpremstartdt,newpremenddt=newpremenddt)))
    
    

    
    form = SQLFORM.grid(query=query,
                        headers=headers,
                        orderby=orderby,
                        fields=fields,
                        links=links,
                        paginate=100,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        selectable = selectable,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )

    
    #submit = form.element('.web2py_table input[type=submit]')
    #submit['_value'] = T('Group Upgrade')
    #submit['_class'] = 'form_details_button'    
    #heading=form.elements('th')
    #if heading:
        #heading[0].append(INPUT(_type='checkbox', _onclick="checkboxes = document.getElementsByName('records');for each(var checkbox in checkboxes)checkbox.checked = this.checked;"))    
    
    
    return dict(form=form,username=username,returnurl=returnurl,page=page,regionid=regionid,frcompany=frcompany,frhmoplan=frhmoplan,tocompany=tocompany,tohmoplan=tohmoplan,newpremstartdt=newpremstartdt, newpremenddt=newpremenddt)

@auth.requires_membership('webadmin')
@auth.requires_login()
def group_upgrade():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    returnurl = URL('default', 'main')
    
    regions = db(db.groupregion.is_active == True).select()
    fromcompanys = db(db.company.is_active == True).select()
    
    formA = SQLFORM.factory(
        
        Field('groupregion',  label='Region', represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'), requires=IS_IN_DB(db(db.groupregion.is_active == True),db.groupregion.id, '%(region)s (%(groupregion)s)')),
        Field('newpremstartdt',
              'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
        Field('newpremenddt',
              'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
        
        Field('frcompany',  label='From Company', represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'), requires=IS_IN_DB(db(db.company.is_active == True),db.company.id, '%(name)s (%(company)s)')),
        Field('tocompany',  label='To Company', represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'), requires=IS_IN_DB(db(db.company.is_active == True),db.company.id, '%(name)s (%(company)s)')),
        Field('frhmoplan',  label='From Plan', represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'),requires=IS_IN_DB(db(db.hmoplan.is_active == True),db.hmoplan.id, '%(name)s (%(hmoplancode)s)')),
        Field('tohmoplan',  label='To Plan', represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'), requires=IS_IN_DB(db(db.hmoplan.is_active == True),db.hmoplan.id, '%(name)s (%(hmoplancode)s)')),
        
    )    

    submit = formA.element('input',_type='submit')
    submit['_value'] = 'Group Upgrade'   
    
    

    
    
    if formA.accepts(request,session,keepvalues=True):  
        regionid = common.getid(formA.vars.groupregion)
        frcompany = common.getid(formA.vars.frcompany)
        frhmoplan = common.getid(formA.vars.frhmoplan)
        tocompany = common.getid(formA.vars.tocompany)
        tohmoplan = common.getid(formA.vars.tohmoplan)       
        newpremstartdt = common.getnulldt(formA.vars.newpremstartdt)
        newpremenddt = common.getnulldt(formA.vars.newpremenddt)
        
        redirect(URL('policyrenewal', 'list_upgrades', vars=dict(regionid=regionid,frcompany=frcompany,frhmoplan=frhmoplan,tocompany=tocompany,tohmoplan=tohmoplan,newpremstartdt=newpremstartdt, newpremenddt = newpremenddt)))
        
        
    else:
        response.flash = "Error"
        
    return dict(formA=formA,username=username, returnurl=returnurl, page=0,regions=regions,fromcompanys=fromcompanys)


def reverse_one_policy(memberid, regionid, frcompany, frhmoplan, tocompany, tohmoplan, newpremstartdt, newpremenddt):

    retval = db(db.patientmember.id == memberid).update(company=frcompany,hmoplan=frhmoplan,upgraded=False)
    
    return retval

def reverse_policies():

    uids = request.vars.id
    regionid = common.getid(request.vars.regionid)
    frcompany = common.getid(request.vars.frcompany)
    frhmoplan = common.getid(request.vars.frhmoplan)
    tocompany = common.getid(request.vars.tocompany)
    tohmoplan = common.getid(request.vars.tohmoplan)     
    
    newpremstartdt = common.getnulldt(request.vars.newpremstartdt)
    newpremenddt = common.getnulldt(request.vars.newpremenddt)

    lastPaidAmt  = 0
    
    success = 0
    error = 0
    
    for uid in uids:
        retval = reverse_one_policy(uid, regionid, frcompany, frhmoplan, 
                          tocompany, tohmoplan, 
                          newpremstartdt, 
                          newpremenddt)
        if(retval > 0):
            success = success + 1
        else:
            error = error + 1
    
    returnurl = URL('policyrenewal','list_upgraded_members_param')
    
    return dict(success=success, error=error,returnurl=returnurl)

def reverse_policy_link():

    uid = request.vars.id
    regionid = common.getid(request.vars.regionid)
    frcompany = common.getid(request.vars.frcompany)
    frhmoplan = common.getid(request.vars.frhmoplan)
    tocompany = common.getid(request.vars.tocompany)
    tohmoplan = common.getid(request.vars.tohmoplan)     
    
    newpremstartdt = common.getnulldt(request.vars.newpremstartdt)
    newpremenddt = common.getnulldt(request.vars.newpremenddt)

    lastPaidAmt  = 0
    
    success = 0
    error = 0
    

    retval = reverse_one_policy(uid, regionid, frcompany, frhmoplan, 
                      tocompany, tohmoplan, 
                      newpremstartdt, 
                      newpremenddt)
    if(retval > 0):
        success = success + 1
    else:
        error = error + 1
    
    returnurl = URL('policyrenewal','list_upgraded_members_param')
    
    return dict(success=success, error=error,returnurl=returnurl)


def list_upgraded_members():

    username = auth.user.first_name + ' ' + auth.user.last_name
    returnurl = URL('policyrenewal', 'group_upgrade')

    page = 1
    regionid = common.getid(request.vars.regionid)
    frcompany = common.getid(request.vars.frcompany)
    frhmoplan = common.getid(request.vars.frhmoplan)
    tocompany = common.getid(request.vars.tocompany)
    tohmoplan = common.getid(request.vars.tohmoplan)
    newpremstartdt = common.getnulldt(request.vars.newpremstartdt)
    newpremenddt = common.getnulldt(request.vars.newpremenddt)
    
    #query = ((db.vw_memberpatientlist.is_active==True) & (db.vw_memberpatientlist.hmopatientmember == True))
    

    query = ((db.patientmember.is_active==True) & (db.patientmember.hmopatientmember == True)  &\
             (db.patientmember.groupregion == regionid)  & (db.patientmember.company == tocompany) & (db.patientmember.hmoplan == tohmoplan) )

    
    fields=(db.patientmember.id,db.patientmember.patientmember, \
            db.patientmember.fname, db.patientmember.lname, db.patientmember.cell, db.patientmember.email,\
            db.patientmember.company,db.patientmember.hmoplan,db.patientmember.upgraded)
    

    headers={
        'patientmember.id':'ID',
        'patientmember.patientmember':'Member ID',
        'patientmember.fname':'First',
        'patientmember.lname':'Last',
        'patientmember.cell':'Cell',
        'patientmember.email':'Email',
        'patientmember.upgraded':'Upgraded'
        
    }

    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)


    links = [lambda row: A('Reverse Policy Upgrade',_href=URL("policyrenewal","reverse_policy_link",\
                                                      vars=dict(page=page,id=row.id,regionid=regionid,newpremstartdt=newpremstartdt,newpremenddt=newpremenddt,\
                                                                frcompany=frcompany,frhmoplan=frhmoplan,tocompany=tocompany,tohmoplan=tohmoplan)))]
    

    orderby = ~(db.patientmember.id)

    selectable = lambda ids : redirect(URL('policyrenewal','reverse_policies',  vars=dict(id=ids, page=page,regionid=regionid,\
                                                              frcompany=frcompany,frhmoplan=frhmoplan,tocompany=tocompany,tohmoplan=tohmoplan,newpremstartdt=newpremstartdt,newpremenddt=newpremenddt)))
    
    

    
    form = SQLFORM.grid(query=query,
                        headers=headers,
                        orderby=orderby,
                        fields=fields,
                        links=links,
                        paginate=20,
                        exportclasses=exportlist,
                        links_in_grid=True,
                        selectable = selectable,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )

    
    
    
    return dict(form=form,username=username,returnurl=returnurl,page=page,regionid=regionid,frcompany=frcompany,frhmoplan=frhmoplan,tocompany=tocompany,tohmoplan=tohmoplan,newpremstartdt=newpremstartdt, newpremenddt=newpremenddt)


@auth.requires_membership('webadmin')
@auth.requires_login()
def list_upgraded_members_param():
        
    username = auth.user.first_name + ' ' + auth.user.last_name
    returnurl = URL('default', 'main')
    
    regions = db(db.groupregion.is_active == True).select()
    fromcompanys = db(db.company.is_active == True).select()
    
    formA = SQLFORM.factory(
        
        Field('groupregion',  label='Region', represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'), requires=IS_IN_DB(db(db.groupregion.is_active == True),db.groupregion.id, '%(region)s (%(groupregion)s)')),
        Field('newpremstartdt',
              'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
        Field('newpremenddt',
              'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))),
        
        Field('frcompany',  label='From Company', represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'), requires=IS_IN_DB(db(db.company.is_active == True),db.company.id, '%(name)s (%(company)s)')),
        Field('tocompany',  label='To Company', represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'), requires=IS_IN_DB(db(db.company.is_active == True),db.company.id, '%(name)s (%(company)s)')),
        Field('frhmoplan',  label='From Plan', represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'),requires=IS_IN_DB(db(db.hmoplan.is_active == True),db.hmoplan.id, '%(name)s (%(hmoplancode)s)')),
        Field('tohmoplan',  label='To Plan', represent=lambda v, r: '' if v is None else v, widget = lambda field, value:SQLFORM.widgets.options.widget(field, value, _style="width:100%;height:35px",_class='w3-input w3-border'), requires=IS_IN_DB(db(db.hmoplan.is_active == True),db.hmoplan.id, '%(name)s (%(hmoplancode)s)')),
        
    )    

    submit = formA.element('input',_type='submit')
    submit['_value'] = 'List Upgraded Members'   
    
    

    
    
    if formA.accepts(request,session,keepvalues=True):  
        regionid = common.getid(formA.vars.groupregion)
        frcompany = common.getid(formA.vars.frcompany)
        frhmoplan = common.getid(formA.vars.frhmoplan)
        tocompany = common.getid(formA.vars.tocompany)
        tohmoplan = common.getid(formA.vars.tohmoplan)       
        newpremstartdt = common.getnulldt(formA.vars.newpremstartdt)
        newpremenddt = common.getnulldt(formA.vars.newpremenddt)
        
        redirect(URL('policyrenewal', 'list_upgraded_members', vars=dict(regionid=regionid,frcompany=frcompany,frhmoplan=frhmoplan,tocompany=tocompany,tohmoplan=tohmoplan,newpremstartdt=newpremstartdt, newpremenddt = newpremenddt)))
        
        
    else:
        response.flash = "Error"
        
    return dict(formA=formA,username=username, returnurl=returnurl, page=0,regions=regions,fromcompanys=fromcompanys)
