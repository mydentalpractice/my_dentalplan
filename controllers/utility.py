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
from applications.my_pms2.modules  import mdpclinic
from applications.my_pms2.modules  import mdpbenefits

from applications.my_pms2.modules import logger


def importappointments():
    
    logger.loggerpms2.info("Import Appointments")
    
   
   
      
    
    count = 0
    apptcount = 0
    form = SQLFORM.factory(
                Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
                )    
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    
    
    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'    
    

    error = ""
    count = 0
    
    if form.accepts(request,session,keepvalues=True):
	try:
	    logger.loggerpms2.info("Form Accepted")
	    
	    
	    #----------- START : IMPORT EXCEL SHEET INTO IMPORTAPPOINT TABLE THIS IS DONE HENCE CODE IS COMMENTED---#
	    #strsql = "Truncate table importappointment"
	    #db.executesql(strsql)
	    #db.commit() 	    

	    #xcsvfile = request.vars.csvfile
	    #code = ""
	    #with open(xcsvfile, 'r') as csvfile:
		#reader = csv.reader(csvfile)
		#count = -1
		#apptcount = 0
		    
                
		#for row in reader:
		    #count = count+1
		    #if(count == 0):
			#continue
		    
		 
		   
		    #strsql = "INSERT INTO importappointment"
		    #strsql = strsql + "(customer_ref,cell,enrolldate,status,providercode,companycode,plan,"
		    #strsql = strsql + "appointment_id,appointment_date,appointment_time"
		    #strsql = strsql + ")VALUES("
		    #strsql = strsql + "'" + row[0] + "'"
		    #strsql = strsql + ",'" + row[1] + "'"
		    #strsql = strsql + ",'" + row[2] + "'"
		    #strsql = strsql + ",'" + row[3] + "'"
		    #strsql = strsql + ",'" + row[4] + "'"
		    #strsql = strsql + ",'" + row[5] + "'"
		    #strsql = strsql + ",'" + row[6] + "'"
		    #strsql = strsql + ",'" + row[7] + "'"
		    #strsql = strsql + ",'" + row[8] + "'"
		    #strsql = strsql + ",'" + row[9] + "'"
		 
		    #strsql = strsql + ")"                
		    
		    ##logger.loggerpms2.info("Import Appointment SQL \n" + strsql)

		    #db.executesql(strsql)
		    #db.commit()
	    #----------- END : IMPORT EXCEL SHEET INTO IMPORTAPPOINT TABLE THIS IS DONE HENCE CODE IS COMMENTED---#
	  
	    #----------- START: Read ImportAppointment table and for each record, create an appointment in t_appointment tabl ----#
	    #loop through import Appoint table for each import appointment,
	    #if patient exists & no appointment is created, then create the appointment else skip
	    
	    #for all appointments in importappointment table which have not been converted to t_appointment 
	    #is_active == FALSE means the appointment has not been converted
	    strsql = "SELECT * from importappointment where is_active = 'F' "
	    ds = db.executesql(strsql)
	    
	    memberid = 0
	    patientid = 0
	    patientmember = ""
	    
	    for i in xrange(0,len(ds)):
		#logger.loggerpms2.info("Appointment member fullname = " + ds[i][1])
		
		#if the importappointment[customer_ref] != <patientmember[FN] [LN]> then skip
		r = db((db.vw_memberpatientlist.fullname.like(ds[i][1]))).select()
		logger.loggerpms2.info("Appointment member fullname = " + ds[i][1] + " " + str(len(r)))
		if(len(r) == 0):
		    continue;
		
		#getting member details from the patientmember table
		memberid = int(common.getid(r[0].primarypatientid))
		patientid = int(common.getid(r[0].patientid))
		patientmember = common.getstring(r[0].patientmember)
		
		#get the appointment start and en date & time specified in importpatient table for that member. Duration is assumed 30 minutes
		appointment_date = ds[i][9]   
		appointment_time = ds[i][10]
		appointment_startstr = appointment_date + " " + appointment_time
		appointment_start = common.getdatefromstring(appointment_startstr, "%Y-%m-%d %H:%M")
	        duration = timedelta(minutes = 30)
		appointment_end = appointment_start + duration
		
		#get the importappointment[status] 
		status = ds[i][4]
		if(status.lower().find("cancelled") >= 0):
		    status = "Cancelled"
		else:
		    status = "Confirmed" 

	        #get importappointment[provider]
		providercode = ds[i][5]
		rows = db((db.provider.provider == providercode) & (db.provider.is_active == True)).select()
		providerid = 0 if(len(rows)<=0) else rows[0].id
		
		#get clinic for the corresponding provider.  If there are more clinics, we will take the first one
		clinics  = db((db.clinic_ref.ref_code == 'PRV') & (db.clinic_ref.ref_id == providerid)).select()
		clinicid = 0 if(len(clinics) <= 0) else int(common.getid(clinics[0].id))
		
		#check whether the appointment to be imported from importappointment table for this member for this date & time exists
		#in t_appointment table, then update importappointment table, apptid & is_active fieldds. This indicates the importappointment 
		#record is already in the system and it maps to the apptid
		t = db((db.t_appointment.patientmember == memberid) & (db.t_appointment.patient == patientid) &\
		       (db.t_appointment.f_start_time == appointment_start)).select()
		logger.loggerpms2.info("Appointment for " + ds[i][1] + " " + str(memberid) + " at " + 
		                       appointment_startstr + " " + str(len(t)))
		if(len(t) > 0):
	            logger.loggerpms2.info("Previous Appointment " + str(t[0].id) + " for member " + t[0].f_patientname)
		    strsql = "UPDATE importappointment set is_active = 'T', apptid = " + str(t[0].id) + " WHERE id = " + str(ds[i][0])
		    db.executesql(strsql)
		    continue;
		
		#if it is not there, then insert a new appointment
                #logger.loggerpms2.info("Insert Appoint for " + ds[i][1])
		apptid = db.t_appointment.insert(f_patientname = ds[i][1], 
		                        f_start_time  = appointment_start,
		                        f_end_time = appointment_end,
		                        f_duration = 30,
		                        f_status = status,
		                        provider = providerid,
		                        doctor = providerid,
		                        patientmember = memberid,
		                        patient = memberid,
		                        cell = ds[i][2],
		                        clinicid = clinicid,
		                        sendsms = False,
		                        sendrem = False,
		                        smsaction = 'update'
		                       
		                      
		                        )
		
		db.commit()
		apptcount = apptcount+1
		logger.loggerpms2.info("Inserted Appointment " + str(apptid) + " " + str(apptcount))		

                #logging some information in importmember["DESCRIPTION"] field if it was XXX or keep as-is the current value of that field.
		apptstr = "[Imported Appointment]:"
		if((ds[i][8]=="") | (ds[i][8] == "XXX")):
		    apptstr = apptstr+ str(apptid)
		else:
		    apptstr = apptstr + ds[i][8]
		    
		db(db.t_appointment.id == apptid).update(f_uniqueid = apptid,description=apptstr)
		strsql = "UPDATE importappointment set is_active = 'T', apptid = " + str(apptid) + " WHERE id = " + str(ds[i][0])
		db.executesql(strsql)
		db.commit()
		
	except Exception as e:
	    logger.loggerpms2.info("Import Appointment Exception Error - " + str(e) + "\n" + str(e.message))
	    error = "Import Appointment Exception Error - " + str(e)
        
    return dict(form=form, count=count,apptcount = apptcount, error=error)



#This method converts HMO Plan ID from region based to plan based
#for CGI, there are three plans - CGI_PREM, CDI_SC, CGI_NDPC, CGI_PREM
#All region based plans like 
def convertCGIPlans():
    
    cos = db((db.company.company == 'CGI') &  (db.company.is_active == True)).select()
    cgi_id = cos[0].id if(len(cos) > 0) else 0
    
    pats = db((db.patientmember.company == cgi_id) &  (db.patientmember.is_active == True)).select()
    
    for pat in pats:
	plan_id = int(common.getid(pat.hmoplan))
	plans = db((db.hmoplan.id == plan_id) & (db.hmoplan.is_active == True)).select()
	plancode = plans[0].hmoplancode if(len(plans) > 0) else ""
	if(plancode.startswith("NDPC") == True):
	    i = 0
	    hmoplan = db((db.hmoplan.hmoplancode == "CISCO_NDPC") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
	
	if(plancode.startswith("CSX") == True):
	    i = 0
	    hmoplan = db((db.hmoplan.hmoplancode == "CISCO_CSX") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
	    
	
	if(plancode.startswith("BLRPrem") == True):
	    i = 0
	    hmoplan = db((db.hmoplan.hmoplancode == "MEDI_PREM") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
		
		
    db((db.provider_region_plan.companycode == 'CISCO') & (db.provider_region_plan.is_active == True) &\
       (db.provider_region_plan.plancode.like('CDX%'))).update(plancode = 'CISCO_CDX',policy='CISCO_CDX')
    
    db((db.provider_region_plan.companycode == 'CISCO') & (db.provider_region_plan.is_active == True) &\
               (db.provider_region_plan.plancode.like('NDPC%'))).update(plancode = 'CISCO_NDPC',policy='CISCO_NDPC')

    db((db.provider_region_plan.companycode == 'CISCO') & (db.provider_region_plan.is_active == True) &\
       (db.provider_region_plan.plancode.like('BLRPrem%'))).update(plancode = 'CISCO_PREM',policy='CISCO_PREM')
 
    return dict()

#This method converts HMO Plan ID from region based to plan based
#for CISCO, there are three plans - CISCO_PREM, CISCO_CSX, CISCO_NDPC
#All region based plans like 
def convertCISCOPlans():
    
    cos = db((db.company.company == 'CISCO') &  (db.company.is_active == True)).select()
    cisco_id = cos[0].id if(len(cos) > 0) else 0
    
    pats = db((db.patientmember.company == cisco_id) &  (db.patientmember.is_active == True)).select()
    
    for pat in pats:
	plan_id = int(common.getid(pat.hmoplan))
	plans = db((db.hmoplan.id == plan_id) & (db.hmoplan.is_active == True)).select()
	plancode = plans[0].hmoplancode if(len(plans) > 0) else ""
	if(plancode.startswith("NDPC") == True):
	    i = 0
	    hmoplan = db((db.hmoplan.hmoplancode == "CISCO_NDPC") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
	
	if(plancode.startswith("CSX") == True):
	    i = 0
	    hmoplan = db((db.hmoplan.hmoplancode == "CISCO_CSX") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
	    
	
	if(plancode.startswith("BLRPrem") == True):
	    i = 0
	    hmoplan = db((db.hmoplan.hmoplancode == "MEDI_PREM") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
		
		
    db((db.provider_region_plan.companycode == 'CISCO') & (db.provider_region_plan.is_active == True) &\
       (db.provider_region_plan.plancode.like('CDX%'))).update(plancode = 'CISCO_CDX',policy='CISCO_CDX')
    
    db((db.provider_region_plan.companycode == 'CISCO') & (db.provider_region_plan.is_active == True) &\
               (db.provider_region_plan.plancode.like('NDPC%'))).update(plancode = 'CISCO_NDPC',policy='CISCO_NDPC')

    db((db.provider_region_plan.companycode == 'CISCO') & (db.provider_region_plan.is_active == True) &\
       (db.provider_region_plan.plancode.like('BLRPrem%'))).update(plancode = 'CISCO_PREM',policy='CISCO_PREM')
 
    return dict()

#This method converts HMO Plan ID from region based to plan based
#for MEDI, there are three plans - MEDI_NDPC, MEDI_SC, MED_SP
#All region based plans like NDPC102,103,101,104 = MEDI_NDPC and likewise
def convertMEDIPlans():
    
    cos = db((db.company.company == 'MEDI') &  (db.company.is_active == True)).select()
    medi_id = cos[0].id if(len(cos) > 0) else 0
    
    pats = db((db.patientmember.company == medi_id) &  (db.patientmember.is_active == True)).select()
    
    for pat in pats:
	plan_id = int(common.getid(pat.hmoplan))
	plans = db((db.hmoplan.id == plan_id) & (db.hmoplan.is_active == True)).select()
	plancode = plans[0].hmoplancode if(len(plans) > 0) else ""
	if(plancode.startswith("NDPC") == True):
	    i = 0
	    hmoplan = db((db.hmoplan.hmoplancode == "MEDI_NDPC") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
	
	if(plancode.startswith("SC") == True):
	    i = 0
	    hmoplan = db((db.hmoplan.hmoplancode == "MEDI_SC") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
	    
	
	if(plancode.startswith("SP") == True):
	    i = 0
	    hmoplan = db((db.hmoplan.hmoplancode == "MEDI_SP") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
		
		
    db((db.provider_region_plan.companycode == 'MEDI') & (db.provider_region_plan.is_active == True) &\
       (db.provider_region_plan.plancode.like('SP%'))).update(plancode = 'MEDI_SP',policy='MEDI_SP')
    
    db((db.provider_region_plan.companycode == 'MEDI') & (db.provider_region_plan.is_active == True) &\
               (db.provider_region_plan.plancode.like('NDPC%'))).update(plancode = 'MEDI_NDPC',policy='MEDI_NDPC')

    db((db.provider_region_plan.companycode == 'MEDI') & (db.provider_region_plan.is_active == True) &\
       (db.provider_region_plan.plancode.like('SC%'))).update(plancode = 'MEDI_SC',policy='MEDI_SC')
 
    return dict()



#This method converts HMO Plan ID from region based to plan based
#for MEDI, there are three plans - MEDI_NDPC, MEDI_SC, MED_SP
#All region based plans like NDPC102,103,101,104 = MEDI_NDPC and likewise
def convertABHIPlans():
    
    cos = db((db.company.company == 'ABHI') &  (db.company.is_active == True)).select()
    medi_id = cos[0].id if(len(cos) > 0) else 0
    
    pats = db((db.patientmember.company == medi_id) &  (db.patientmember.is_active == True)).select()
    
    for pat in pats:
	plan_id = int(common.getid(pat.hmoplan))
	plans = db((db.hmoplan.id == plan_id) & (db.hmoplan.is_active == True)).select()
	plancode = plans[0].hmoplancode if(len(plans) > 0) else ""
	if((plancode.startswith("ABHI") == True) & (plancode.endswith("103") == True)):
	    i = 0
	    hmoplan = db((db.hmoplan.hmoplancode == "ABHI_ABHI") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
	
	if(plancode.startswith("i") == True):
	    hmoplan = db((db.hmoplan.hmoplancode == "ABHI_I") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
	    
	
	if(plancode.startswith("Z") == True):
	    hmoplan = db((db.hmoplan.hmoplancode == "ABHI_Z") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
		
	if((plancode.startswith("ABHI") == True)& (plancode.endswith("103") == False)):
	    i = 0
	    hmoplan = db((db.hmoplan.hmoplancode == "ABHI_CSX") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
		
    db((db.provider_region_plan.companycode == 'ABHI') & (db.provider_region_plan.is_active == True) &\
       (db.provider_region_plan.plancode.like('ABHI%'))).update(plancode = 'ABHI_ABHI',policy='ABHI_ABHI')
    
    db((db.provider_region_plan.companycode == 'ABHI') & (db.provider_region_plan.is_active == True) &\
               (db.provider_region_plan.plancode.like('i%'))).update(plancode = 'ABHI_I',policy='ABHI_I')

    db((db.provider_region_plan.companycode == 'ABHI') & (db.provider_region_plan.is_active == True) &\
       (db.provider_region_plan.plancode.like('Z%'))).update(plancode = 'ABHI_Z',policy='ABHI_Z')

    db((db.provider_region_plan.companycode == 'ABHI') & (db.provider_region_plan.is_active == True) &\
       ((db.provider_region_plan.plancode.like('ABHIBLR')) | (db.provider_region_plan.plancode.like('ABHIHYD')) |\
                                                            (db.provider_region_plan.plancode.like('ABHIDEL')))
       ).update(plancode = 'ABHI_CSX',policy='ABHI_CSX')
   
   
    cos = db((db.company.company == 'ABHIC') &  (db.company.is_active == True)).select()
    abhic_id = cos[0].id if(len(cos) > 0) else 0
    
    pats = db((db.patientmember.company == abhic_id) &  (db.patientmember.is_active == True)).select()
    
    for pat in pats:
	plan_id = int(common.getid(pat.hmoplan))
	plans = db((db.hmoplan.id == plan_id) & (db.hmoplan.is_active == True)).select()
	plancode = plans[0].hmoplancode if(len(plans) > 0) else ""
	
	if(plancode.startswith("ABHIC") == True):
	   
	    hmoplan = db((db.hmoplan.hmoplancode == "ABHIC_NDPC") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
	
	
	if(plancode.startswith("Z") == True):
	    hmoplan = db((db.hmoplan.hmoplancode == "ABHIC_Z") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
		
	
		
    db((db.provider_region_plan.companycode == 'ABHIC') & (db.provider_region_plan.is_active == True) &\
       (db.provider_region_plan.plancode.like('NDPC%'))).update(plancode = 'ABHIC_NDPC',policy='ABHIC_NDPC')
    
 

    db((db.provider_region_plan.companycode == 'ABHIC') & (db.provider_region_plan.is_active == True) &\
       (db.provider_region_plan.plancode.like('Z%'))).update(plancode = 'ABHIC_Z',policy='ABHIC_Z')


    cos = db((db.company.company == 'ABWPL') &  (db.company.is_active == True)).select()
    abwpl_id = cos[0].id if(len(cos) > 0) else 0
    
    pats = db((db.patientmember.company == abwpl_id) &  (db.patientmember.is_active == True)).select()
    
    for pat in pats:
	plan_id = int(common.getid(pat.hmoplan))
	plans = db((db.hmoplan.id == plan_id) & (db.hmoplan.is_active == True)).select()
	plancode = plans[0].hmoplancode if(len(plans) > 0) else ""
	
	if(plancode.startswith("i") == True):
	   
	    hmoplan = db((db.hmoplan.hmoplancode == "ABWPL_I") & (db.hmoplan.is_active == True)).select()
	    hmoplanid = int(common.getid(hmoplan[0].id)) if(len(hmoplan) > 0) else 0
	    db(db.patientmember.id == pat.id).update(hmoplan = hmoplanid)
	
	
	
	
		
    db((db.provider_region_plan.companycode == 'ABWPL') & (db.provider_region_plan.is_active == True) &\
       (db.provider_region_plan.plancode.like('ABWPL%'))).update(plancode = 'ABHIC_I',policy='ABHIC_I')
    

   
    
    return dict()


#this function assigns provider clinics to agents
#for each provider, create a clinic if no clinic has been 
#created. Then assign the clinic to agent within the same
#region
def assign_clinics():
    username = ""
    formheader = "Assigned Clinics Report"
    provs = db((db.provider.is_active == True)).select()
    provider_count = len(provs)
    new_clinics = 0
    old_clinics = 0
    assigned_provs = ""
    unassigned_provs = ""
    
    for prov in provs:
	
	#does the clinic exists for this provider?
	#if not, then create one for this provider
	
	ref_code = 'PRV'
	ref_id = prov.id
	r = db((db.clinic_ref.ref_code == ref_code) & (db.clinic_ref.ref_id == ref_id)).select()
	if(len(r) > 0):
	    #clinic exists for this provider
	    old_clinics = old_clinics + len(r)

	    #if it is a primary clinic & treatment clinicid == NULL and t_appointment clinicid = NUll, then
	    #assign primary clinic as the default_clinic
	
	    clns = db((db.clinic_ref.ref_code == 'PRV') & (db.clinic_ref.ref_id == ref_id) & (db.clinic.primary_clinic == True) &(db.clinic.is_active == True)).\
		select(db.clinic_ref.clinic_id, left=db.clinic.on(db.clinic.id==db.clinic_ref.clinic_id))
	    
	    clinicid = 0 if(len(clns) == 0) else clns[0].clinic_id

	    db((db.treatment.provider ==prov.id) & ( (db.treatment.clinicid == None) | (db.treatment.clinicid == "") | (db.treatment.clinicid == 0))).update(clinicid=clinicid)
	    
	    db((db.t_appointment.provider == prov.id) & ( (db.t_appointment.clinicid == None) | (db.t_appointment.clinicid == "") | (db.t_appointment.clinicid == 0))).update(clinicid = clinicid)

	    continue
	
	#clinic does not exist
	reqobj = {
	"action":"new_clinic", 
	"ref_code":ref_code,     
	"ref_id":ref_id,        
	"name":prov.practicename,      
	"address1":prov.address1,
	"address2":prov.address2,
	"address3":prov.address3,
	"city":prov.city,
	"st":prov.st,
	"pin":prov.pin,
	"cell":prov.cell,
	"email":prov.email,

	"status":"Old",
	"primary":"True",
	
	"gps_location":prov.pa_locationurl,
	
	"bank_id":prov.bankid,
	
	"state_dental_registration":prov.registration,
	"mdp_registration":"Yes",
	"notes":common.getstringfromdate(datetime.datetime.today(),"%d/%m/%Y") + "\n" + " New Clinic Assigend"
	
	}

	clinicobj = mdpclinic.Clinic(db)
	rsp = json.loads(clinicobj.new_clinic(reqobj))
	
	if(rsp["result"] == 'fail'):
	    unassigned_provs = unassigned_provs + "," + prov.provider + " "
	else:
	    assigned_provs = assigned_provs + "," + prov.provider + " "
	    new_clinics = new_clinics  + 1
	    
	    clinicid = int(common.getid(common.getkeyvalue(rsp,"clinicid","0")))

	    db(db.treatment.provider ==prov.id).update(clinicid=clinicid)
	    
	    db((db.t_appointment.provider == prov.id) & ( (db.t_appointment.clinicid == None) | (db.t_appointment.clinicid == "") | (db.t_appointment.clinicid == 0))).update(clinicid = clinicid)
		                                            
    	    
    returnurl = URL('default','main')
    return dict(formheader=formheader,username=username,\
                provider_count=provider_count, new_clinics = new_clinics,old_clinics=old_clinics,assigned_provs=assigned_provs,\
                unassigned_provs=unassigned_provs,returnurl=returnurl)


def assign_appointment_clinics():
    logger.loggerpms2.info("Enter assign_appointment_clinics")
    username = ""
    formheader = "Assigned Clinics Report"
    provs = db((db.provider.is_active == True)).select()
    provider_count = len(provs)
    logger.loggerpms2.info("Sssign_appointment_clinics " + str(provider_count))
    new_clinics = 0
    old_clinics = 0
    assigned_provs = ""
    unassigned_provs = ""
    
    
    try:
	for prov in provs:
	    logger.loggerpms2.info("Enter Provider loog " + str(prov.id))
	    #does the clinic exists for this provider?
	    #if not, then create one for this provider
	    
	    ref_code = 'PRV'
	    ref_id = prov.id
	    r = db((db.clinic_ref.ref_code == ref_code) & (db.clinic_ref.ref_id == ref_id)).select()
	    if(len(r) > 0):
		logger.loggerpms2.info("Enter Provider R > 0 ")
		
		#clinic exists for this provider
		old_clinics = old_clinics + len(r)
    
		#if it is a primary clinic & treatment clinicid == NULL and t_appointment clinicid = NUll, then
		#assign primary clinic as the default_clinic
	    
		clns = db((db.clinic_ref.ref_code == 'PRV') & (db.clinic_ref.ref_id == ref_id) & (db.clinic.primary_clinic == True) &(db.clinic.is_active == True)).\
		    select(db.clinic_ref.clinic_id, left=db.clinic.on(db.clinic.id==db.clinic_ref.clinic_id))
		
		clinicid = 0 if(len(clns) == 0) else clns[0].clinic_id
		logger.loggerpms2.info("Enter Provider R > 0  Clinicid  " + str(clinicid))
    
		db((db.treatment.provider ==prov.id) & ( (db.treatment.clinicid == None) | (db.treatment.clinicid == "") | (db.treatment.clinicid == 0))).update(clinicid=clinicid)
		
		db((db.t_appointment.provider == prov.id) & ( (db.t_appointment.clinicid == None) | (db.t_appointment.clinicid == "") | (db.t_appointment.clinicid == 0))).update(clinicid = clinicid)
    
		
	db.commit()
    except Exception as e:
	logger.loggerpms2.info("Assign_Appointment_Clinics Exception " + str(e))
	
   
    
    returnurl = URL('default','main')
    logger.loggerpms2.info("Exit assign_appointment_clinics")
    return dict(formheader=formheader,username=username,\
                provider_count=provider_count, new_clinics = new_clinics,old_clinics=old_clinics,assigned_provs=assigned_provs,\
                unassigned_provs=unassigned_provs,returnurl=returnurl)


def download():
    return response.download(request, db)



    
    


    
    

    



    
    


def new_user(providername, email,cell, username, passw,key,registration_id,role): 
    logger.loggerpms2.info("Enter New User - Calling provider_registration API")
    
    #props = db(db.urlproperties.id > 0).select(db.urlproperties.mydp_ipaddress)
    #url = props[0].mydp_ipaddress + "/my_pms2/mdpapi/mdpapi" if(len(props) > 0) else "http://127.0.0.1:8001/my_pms2/mdpapi/mdpapi"
    
    #jsonreqdata = {
	#"action":"provider_registration",
	#"providerid":0,
	#"providername":"Dr.Manjunath A",
	#"username":"P10825",
	#"password":"P10825",
	#"cell":"9035314080",
	#"email":"manjunathshidling2@gmail.com",
	#"sitekey":"wJ3vN7",
	#"registration_id":"4080",
	#"role":"provider"
    #}
          
    #logger.loggerpms2.info(">>New User\n")
    #logger.loggerpms2.info("===URL" + url + "\n")    
    #logger.loggerpms2.info("===Req_data=\n" + json.dumps(jsonreqdata) + "\n")    
    
    #resp = requests.post(url,data=jsonreqdata)
    #obj={}
    #jsonresp = {}
    #if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
        #respstr =   resp.text 
        #obj={
            #"new" : True,
            #"userid":"userid",
            #"result":"success",
            #"error_message":""
        #}
    #else:
        #obj={
            #"new" : False,
            #"userid":"userud",
            #"result":"fail",
            #"error_message":""
        #}
        
    #logger.loggerpms2.info("Response Code " + str(resp.status_code) + "\n")
    #logger.loggerpms2.info("Response  " + resp.text + "\n")
    ouser = mdpuser.User(current.globalenv['db'],current.auth,"","")
    
    rsp = ouser.provider_registration(current.globalenv["request"],\
                                      providername, \
                                      key, \
                                      email,\
                                      cell, \
                                      registration_id,\
                                      username,\
                                      passw,\
                                      role
                            )    
    
    logger.loggerpms2.info("Provider Registrations API Resp\n" + rsp)
    obj = json.loads(rsp)        
    
    return dict(new = obj["new"], userid = common.getstring(obj["userid"]),\
                result=obj["result"], error_message=obj["error_message"])



def xnew_user(providername, email,cell, username, passw,key,registration_id,role): 
    logger.loggerpms2.info("Enter New User")
    users = db((db.auth_user.email==email) & (db.auth_user.sitekey == key)).select()
    if users:
        logger.loggerpms2.info("Enter New User a")
        my_crypt = CRYPT(key=auth.settings.hmac_key)
        logger.loggerpms2.info("Enter New User b")
        crypt_pass = my_crypt(str(passw))[0]  
        logger.loggerpms2.info("Enter New User c")
        db(db.auth_user.id == users[0].id).update(first_name=providername,
                                                  username=username,password=crypt_pass)
        
        db.commit()
        logger.loggerpms2.info("Enter New User d")
        
        # Setting Group Membership
        group_id = auth.id_group(role=role)
        auth.add_membership(group_id, users[0].id)  
        
        logger.loggerpms2.info("Return New User e ")
        return dict(result="success",new=False, userid = users[0].id)
    else:
        logger.loggerpms2.info("Enter New User f")
        my_crypt = CRYPT(key=auth.settings.hmac_key)
        logger.loggerpms2.info("Enter New User g")
        crypt_pass = my_crypt(str(passw))[0]  
        #base64.b64encode(imageFile.read())
        #encode_pass = base64.b64encode(crypt_pass)
        
        
        #strsql = "INSERT INTO auth_user (first_name,email,cell,sitekey,registration_id,username,password)values("
        #strsql = strsql + "'" + providername + "' "
        #strsql = strsql + ",'" + email + "' "
        #strsql = strsql + ",'" + cell + "' "
        #strsql = strsql + ",'" + key + "' "
        #strsql = strsql + ",'" + registration_id + "' "
        #strsql = strsql + ",'" + username + "' "
        #strsql = strsql + ",'" + crypt_pass + "') "
        #logger.loggerpms2.info("Enter New User h " + strsql )
        #db.executesql(strsql)
        #INSERT INTO `mydp_stg`.`auth_user`
        #(`id`,
        #`first_name`,
        #`last_name`,
        #`email`,
        #`cell`,
        #`sitekey`,
        #`username`,
        #`password`,
        #`created_on`,
        #`modified_on`,
        #`registration_key`,
        #`reset_password_key`,
        #`registration_id`,
        #`impersonated`,
        #`impersonatorid`,
        #`impersonatorfname`,
        #`impersonatorlname`)
        #VALUES
        #(<{id: }>,
        #<{first_name: }>,
        #<{last_name: }>,
        #<{email: }>,
        #<{cell: }>,
        #<{sitekey: }>,
        #<{username: }>,
        #<{password: }>,
        #<{created_on: }>,
        #<{modified_on: }>,
        #<{registration_key: }>,
        #<{reset_password_key: }>,
        #<{registration_id: }>,
        #<{impersonated: F}>,
        #<{impersonatorid: 1}>,
        #<{impersonatorfname: }>,
        #<{impersonatorlname: }>);        
        
        
        id_user= db.auth_user.insert(
                                   first_name=providername,
                                   email = email,
                                   cell=cell,
                                   sitekey = key,
                                   registration_id = registration_id,
                                   username = username,
                                   password = crypt_pass 
                                   )
        db.commit()
        logger.loggerpms2.info("Enter New User i")
        # Setting Group Membership
        group_id = auth.id_group(role=role)
        auth.add_membership(group_id, id_user)          
        logger.loggerpms2.info("Return New User 2 ")
               
        return dict(result="success",new = True, userid = id_user)
    
def getKey():
    key = ''
    
    for i in range(0,2):
        key += random.choice(string.lowercase)
        key += random.choice(string.uppercase)
        key += random.choice(string.digits)    
    
    return key

def getProviderCode():
    
    sql = "UPDATE providercount SET providercount = providercount + 1;"
    db.executesql(sql)
    db.commit()
    
    xrows = db(db.providercount.id >0).select()
    providercount = int(xrows[0].providercount)    

    providercode = "P" + str(providercount).zfill(5)
    return providercode



    
    
def importrlgprovider():
    logger.loggerpms2.info("Enter Import Religare Provider")
    strsql = "Truncate table importrlgprovider"
    db.executesql(strsql)
    db.commit()    

    strsql = "Truncate table rlgprovider"
    db.executesql(strsql)
    db.commit()    

    
    count = 0
    form = SQLFORM.factory(
                Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
                )    
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    
    
    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'       
    error = ""
    
    if form.accepts(request,session,keepvalues=True):
        try:
            xcsvfile = request.vars.csvfile
            code = ""
            with open(xcsvfile, 'r') as csvfile:
                reader = csv.reader(csvfile)
                count = 0
                memberID = ""
                
                for row in reader:
		    count=count+1
		    if(count == 1):
			continue		    
		    
                    
                    strsql = "INSERT INTO importrlgprovider"
                    strsql = strsql + "(id,providercode,region,plan)VALUES("                
                    strsql = strsql + row[0] + " "
                    strsql = strsql + ",'" + row[1] + "'"
                    strsql = strsql + ",'" + row[2] + "'"
                    strsql = strsql + ",'" + row[3] + "'"
                    strsql = strsql + ")"                
                    
                    db.executesql(strsql)
                    db.commit()

		logger.loggerpms2.info("Import Religare Provider - After reading " + str(count))
                    
            
                ##update regionid
                strsql = "UPDATE importrlgprovider imp, groupregion rgn SET imp.regionid = rgn.id WHERE rgn.groupregion = imp.region"
                db.executesql(strsql)
                db.commit()            

		logger.loggerpms2.info("Import Religare Provider - After reading A " + str(count))
    
                ##update planid
                strsql = "UPDATE importrlgprovider imp, hmoplan hmp SET imp.planid = hmp.id WHERE hmp.hmoplancode = imp.plan"
                db.executesql(strsql)
                db.commit()            

		logger.loggerpms2.info("Import Religare Provider - After reading B " + str(count))
                
                ##update providerid
                strsql = "UPDATE importrlgprovider imp, provider prov SET imp.providerid = prov.id WHERE prov.provider = imp.providercode"
                db.executesql(strsql)
                db.commit()            
		
		logger.loggerpms2.info("Import Religare Provider - After reading C " + str(count))
        
            #importrlgprovider -> rlgprovider
            strsql = "SELECT * from importrlgprovider where id > 0  and providerid <> 0;"
            ds = db.executesql(strsql)
                   
            for i in xrange(0,len(ds)):
                db.rlgprovider.insert(providerid=ds[i][4],\
                                      providercode=ds[i][1],\
                                      regionid = ds[i][5],\
                                      planid = ds[i][6])
        except Exception as e:
            error = "Import Religare Provider Exception Error - " + str(e)
	    logger.loggerpms2.info(error)
            
    return dict(form=form, count=count, error=error)




def importprovider():
    
    strsql = "Truncate table importprovider"
    db.executesql(strsql)
    db.commit()    
    
    count = 0
    form = SQLFORM.factory(
                Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
                )    
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    
    
    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'    
    error = ""
    if form.accepts(request,session,keepvalues=True):
        try:
            xcsvfile = request.vars.csvfile
            code = ""
            with open(xcsvfile, 'r') as csvfile:
                reader = csv.reader(csvfile)
                count = 0
                memberID = ""
                
                for row in reader:
		    count = count+1
		    
		    if(count == 1):
			continue		    
		    
                    strsql = "INSERT INTO importprovider"
                    strsql = strsql + "(id,providerid,provider,title,providername,practicename,address1,address2,address3,city,st,pin,"
                    strsql = strsql + "p_address1,p_address2,p_address3,p_city,p_st,p_pin,telephone,cell,fax,email,taxid,enrolleddate,assignedpatientmembers,"
                    strsql = strsql + "captguarantee,schedulecapitation,capitationytd,captiationmtd,languagesspoken,specialization,sitekey,groupregion,registration,registered,"
                    strsql = strsql + "pa_providername,pa_practicename,pa_practiceaddress,pa_dob,pa_parent,pa_address,pa_pan,pa_regno,pa_date,pa_accepted,pa_approved,"
                    strsql = strsql + "pa_approvedby,pa_approvedon,pa_day,pa_month,pa_location,pa_practicepin,region,"
		    strsql = strsql + "bankname,bankbranch,bankaccountno,bankaccounttype,bankmicrno,bankifsccode,"
		    strsql = strsql + "longitude,latitude,locationurl"
		    strsql = strsql + ")VALUES("
                    strsql = strsql + row[0] + " "
                    strsql = strsql + "," + row[1] + " "
                    strsql = strsql + ",'" + row[2] + "'"
                    strsql = strsql + ",'" + row[3] + "'"
                    strsql = strsql + ",'" + row[4] + "'"
                    strsql = strsql + ",'" + row[5] + "'"
                    strsql = strsql + ",'" + row[6] + "'"
                    strsql = strsql + ",'" + row[7] + "'"
                    strsql = strsql + ",'" + row[8] + "'"
                    strsql = strsql + ",'" + row[9] + "'"
                    strsql = strsql + ",'" + row[10] + "'"
                    strsql = strsql + ",'" + row[11] + "'"
                    strsql = strsql + ",'" + row[12] + "'"
                    strsql = strsql + ",'" + row[13] + "'"
                    strsql = strsql + ",'" + row[14] + "'"
                    strsql = strsql + ",'" + row[15] + "'"
                    strsql = strsql + ",'" + row[16] + "'"
                    strsql = strsql + ",'" + row[17] + "'"
                    strsql = strsql + ",'" + row[18] + "'"
                    strsql = strsql + ",'" + row[19] + "'"
                    strsql = strsql + ",'" + row[20] + "'"
                    strsql = strsql + ",'" + row[21] + "'"
                    strsql = strsql + ",'" + row[22] + "'"
                    strsql = strsql + ",'" + row[23] + "'"
                    strsql = strsql + "," + row[24] + " "
                    strsql = strsql + "," + row[25] + " "
                    strsql = strsql + "," + row[26] + " "
                    strsql = strsql + "," + row[27] + " "
                    strsql = strsql + "," + row[28] + " "
                    strsql = strsql + ",'" + row[29] + "'"
                    strsql = strsql + ",'" + row[30] + "'"
                    strsql = strsql + ",'" + row[31] + "'"
                    strsql = strsql + "," + row[32] + " "
                    strsql = strsql + ",'" + row[33] + "'"
                    strsql = strsql + ",'" + row[34] + "'"
                    strsql = strsql + ",'" + row[35] + "'"
                    strsql = strsql + ",'" + row[36] + "'"
                    strsql = strsql + ",'" + row[37] + "'"
                    strsql = strsql + ",'" + row[38] + "'"
                    strsql = strsql + ",'" + row[39] + "'"
                    strsql = strsql + ",'" + row[40] + "'"
                    strsql = strsql + ",'" + row[41] + "'"
                    strsql = strsql + ",'" + row[42] + "'"
                    strsql = strsql + ",'" + row[43] + "'"
                    strsql = strsql + ",'" + row[44] + "'"
                    strsql = strsql + ",'" + row[45] + "'"
                    strsql = strsql + "," + row[46] + " "
                    strsql = strsql + ",'" + row[47] + "'"
                    strsql = strsql + ",'" + row[48] + "'"
                    strsql = strsql + ",'" + row[49] + "'"
                    strsql = strsql + ",'" + row[50] + "'"
                    strsql = strsql + ",'" + row[51] + "'"
                    strsql = strsql + ",'" + row[52] + "'"
		    strsql = strsql + ",'" + row[53] + "'"
		    strsql = strsql + ",'" + row[54] + "'"
		    strsql = strsql + ",'" + row[55] + "'"
		    strsql = strsql + ",'" + row[56] + "'"
		    strsql = strsql + ",'" + row[57] + "'"
		    strsql = strsql + ",'" + row[58] + "'"
		    strsql = strsql + ",'" + row[59] + "'"
		    strsql = strsql + ",'" + row[60] + "'"
		    strsql = strsql + ",'" + row[61] + "'"
                    strsql = strsql + ")"                
                    
                    db.executesql(strsql)
                    logger.loggerpms2.info("Insert into Provider \n" + strsql)
                    
                    db.commit()
        
                ##update pa_dobto NULL
                sql = "UPDATE importprovider SET pa_dob = null where id > 0  and pa_dob = '';"
                logger.loggerpms2.info("Update pa_dob to NULL \n" + sql)
                db.executesql(sql)
                db.commit()             
            
                ##update groupregion
                strsql = "UPDATE importprovider imp, groupregion rgn SET imp.groupregion = rgn.id WHERE rgn.groupregion = imp.region"
                logger.loggerpms2.info("Update groupregion \n" + strsql)
                db.executesql(strsql)
                db.commit()            
    
    
            #loop through import provider table
            #for each import provider, if it exists, then create a username/password
            #update the record, send email
            #if does not exist, insert the record, and send email
            strsql = "SELECT * from importprovider where id > 0;"
            ds = db.executesql(strsql)
            
            for i in xrange(0,len(ds)):
                
                #create user
                logger.loggerpms2.info("Create User")
                
                provider = common.getstring(ds[i][2]).strip()
                provider = getProviderCode() if(provider == "") else provider
                
                providername = common.getstring(ds[i][4]).strip()
                email = common.getstring(ds[i][21]).strip()
                username = provider
                password = provider
    
                key = common.getstring(ds[i][31]).strip()
                key = getKey() if(key=="") else key
                
                registration_id= common.getstring(ds[i][33]).strip()
                cell = common.getstring(ds[i][19]).strip()
              
                providerid0 = None
                r = db((db.provider.provider == provider)&(db.provider.is_active == True)).select(db.provider.id)
                if(len(r) == 1):
                    providerid0 = int(common.getid(r[0].id))
                
                        
                #create or update provider
                logger.loggerpms2.info("Before Update/Insert Provider")
                
                providerid = None
                providerid = db.provider.update_or_insert(db.provider.provider == provider,\
                                    provider = provider,\
                                    title = ds[i][3],\
                                    providername = ds[i][4],\
                                    practicename = ds[i][5],\
                                    address1 = ds[i][6],\
                                    address2 = ds[i][7],\
                                    address3 = ds[i][8],\
                                    city = ds[i][9],\
                                    st = ds[i][10],\
                                    pin = ds[i][11],\
                                    p_address1 = ds[i][12],\
                                    p_address2 = ds[i][13],\
                                    p_address3 = ds[i][14],\
                                    p_city = ds[i][15],\
                                    p_st = ds[i][16],\
                                    p_pin = ds[i][17],\
                                    telephone = ds[i][18],\
                                    cell = cell,\
                                    fax = ds[i][20],\
                                    email = ds[i][21],\
                                    taxid = ds[i][22],\
                                    enrolleddate =  ds[i][23],\
                                    assignedpatientmembers = int(common.getid(ds[i][24])),\
                                    captguarantee = float(common.getvalue(ds[i][25])),\
                                    schedulecapitation = float(common.getvalue(ds[i][26])),\
                                    capitationytd = float(common.getvalue(ds[i][27])),\
                                    captiationmtd = float(common.getvalue(ds[i][28])),\
                                    languagesspoken = ds[i][29],\
                                    specialization = ds[i][30],\
                                    sitekey =key,\
                                    groupregion = int(common.getid(ds[i][32])),\
                                    registration = ds[i][33],\
                                    registered = ds[i][34],\
                                    pa_providername = ds[i][35],\
                                    pa_practicename = ds[i][36],\
                                    pa_practiceaddress = ds[i][37],\
                                    pa_dob =  ds[i][38],\
                                    pa_parent = ds[i][39],\
                                    pa_address = ds[i][40],\
                                    pa_pan = ds[i][41],\
                                    pa_regno = ds[i][42],\
                                    pa_date =  ds[i][43],\
                                    pa_accepted = ds[i][44],\
                                    pa_approved = ds[i][45],\
                                    pa_approvedby = int(common.getid(ds[0][46])),\
                                    pa_approvedon = ds[i][47],\
                                    pa_day = ds[i][48],\
                                    pa_month = ds[i][49],\
                                    pa_location = ds[i][50],\
                                    pa_practicepin = ds[i][51],\
		                    
		                    pa_latitude = ds[i][59],\
		                    pa_longitude = ds[i][60],\
		                    pa_locationurl = ds[i][61],\
		                    
                                    is_active = True,\
                                    created_on = datetime.datetime.today(),\
                                    created_by = 1,\
                                    modified_on = datetime.datetime.today(),\
                                    modified_by = 1\
                                    )
		db.commit()
		providerid = providerid0 if (providerid == None) else providerid
		
		#enter bank details
		p = db((db.provider.provider == provider) & (db.provider.is_active == True)).select(db.provider.id)
		providerid = int(common.getid(p[0].id)) if(len(p) == 1) else 1
		db.providerbank.update_or_insert(((db.providerbank.bankmicrno == ds[i][57]) & (db.providerbank.bankifsccode == ds[i][58])),\
		                                 bankname = ds[i][53],\
		                                 bankbranch = ds[i][54],\
		                                 bankaccountno = ds[i][55],\
		                                 bankaccounttype = ds[i][56],\
		                                 bankmicrno = ds[i][57],\
		                                 bankifsccode = ds[i][58],\
		                                 providerid = providerid)
		
		#update provider bank reference                                 
		b = db((db.providerbank.bankmicrno == ds[i][57]) & (db.providerbank.bankifsccode == ds[i][58])).select(db.providerbank.id)
		bnkid = int(common.getid(b[0].id)) if(len(b) == 1) else 1
		db(db.provider.id == providerid).update(bankid = bnkid)
		
		
                #if this provider is new, then create doctor, role etc. for this provider
                logger.loggerpms2.info("Before New User")
                userdict = new_user(providername,email, cell,username, password, key, registration_id,'provider')
                new = common.getboolean(userdict["new"])
                if(userdict["result"]=="success"):
                    if(new == True):
                        #copy default Roles, Speciality and Medicines for this provider
                        sql = "insert into role(role,providerid, is_active, created_by, created_on, modified_by, modified_on)"
                        sql = sql + " select role," +  str(providerid) + ", 'T'," +  str(providerid) + ", NOW()," +  str(providerid) + ", NOW() from role_default"
                        logger.loggerpms2.info("Roles\n" + sql)                    
                        db.executesql(sql)    
                        db.commit()
                         
                        sql = "insert into speciality(speciality,providerid, is_active, created_by, created_on, modified_by, modified_on)"
                        sql = sql + " select speciality," +  str(providerid) + ", 'T'," +  str(providerid) + ", NOW()," +  str(providerid) + ", NOW() from speciality_default"
                        logger.loggerpms2.info("RSpeciality\n" + sql)                    
                        db.executesql(sql)    
                        db.commit()
                        
                        sql = "insert into medicine(providerid,medicine,medicinetype, strength,strengthuom, instructions,   is_active, created_by, created_on, modified_by, modified_on)"
                        sql = sql + " select " + str(providerid) + ", medicine , meditype , strength , strngthuom ,instructions, 'T'," +  str(providerid) + ", NOW()," + str(providerid) + ", NOW() from medicine_default"
                        logger.loggerpms2.info("Medicine\n" + sql)                    
                        
                        db.executesql(sql)    
                        db.commit()
                        
                    
                    
                        #Add role = 'Doctor_Owner' and 'General Dentist' in Speciality
                        roles = db((db.role.providerid == providerid) & (db.role.role == "Chief Consultant")).select()
                        if(len(roles)==0):
                            roleid = db.role.insert(role='Chief Dentist', providerid = providerid, is_active = True, \
                                                    created_by = providerid, modified_by = providerid, created_on = request.now,modified_on = request.now)
                        else:
                            roleid = int(common.getid(roles[0].id))
                            
                        spcs = db((db.speciality.providerid == providerid) & (db.speciality.speciality == "General Dentist")).select()
                        if(len(spcs)==0):
                            specialityid = db.speciality.insert(speciality='General Dentist', providerid = providerid, is_active = True, \
                                                    created_by = providerid, modified_by = providerid, created_on = request.now,modified_on = request.now)
                        else:
                            specialityid = int(common.getid(spcs[0].id))
                            
                       
                        logger.loggerpms2.info("InsertDoctor")                    
                      
                        db.doctor.insert(name = providername, providerid = providerid, speciality=specialityid, role = roleid, email=email,cell=cell,registration=registration_id,stafftype='Doctor',\
                                         color="#ff0000",practice_owner=True,is_active = True, created_on = request.now, created_by = providerid, modified_on=request.now, modified_by = providerid)      
             
                    
                    
                    logger.loggerpms2.info("Mail")
                    retval = mail.emailProviderLoginDetails(db,request,key,email,username,password)
                else:
                    
                    error = "Import Provider Error - \n" + userdict["error_message"]
                    logger.loggerpms2.info(error)
                
        except Exception as e:
            logger.loggerpms2.info("Import Provider Exception Error - " + str(e) + "\n" + str(e.message))
                                   
            error = "Import Provider Exception Error - " + str(e)
        
                                
    return dict(form=form, count=count,error=error)


def importdoctor():
    
    logger.loggerpms2.info("Import Doctor")
    
    strsql = "Truncate table importdoctor"
    db.executesql(strsql)
    db.commit()    
    
    count = 0
    form = SQLFORM.factory(
                Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
                )    
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    
    
    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'    
    
    if form.accepts(request,session,keepvalues=True):
	try:
	    xcsvfile = request.vars.csvfile
	    code = ""
	    with open(xcsvfile, 'r') as csvfile:
		reader = csv.reader(csvfile)
		count = 0
		memberID = ""
		
		#title varchar(45) 
		#name varchar(128) 
		#provider varchar(128) 
		#speciality varchar(128) 
		#role varchar(128) 
		#practice_owner char(1) 
		#email varchar(128) 
		#cell varchar(45) 
		#registration varchar(45) 
		#color varchar(45) 
		#stafftype varchar(45) 
		#docsms char(1) 
		#docemail char(1) 
		#groupsms char(1) 
		#groupemail char(1)	    
    
		for row in reader:
		    count = count + 1
		    if(count == 1):
			continue		    
		   
		    strsql = "INSERT INTO importdoctor"
		    strsql = strsql + "(id,title,name,provider,speciality,role,"
		    strsql = strsql + "practice_owner,email,cell,registration,color,stafftype,"
		    strsql = strsql + "docsms,docemail,groupsms,groupemail"
		    strsql = strsql + ")VALUES("
		    strsql = strsql + row[0] + " "
		    strsql = strsql + ",'" + row[1] + "'"
		    strsql = strsql + ",'" + row[2] + "'"
		    strsql = strsql + ",'" + row[3] + "'"
		    strsql = strsql + ",'" + row[4] + "'"
		    strsql = strsql + ",'" + row[5] + "'"
		    strsql = strsql + ",'" + row[6] + "'"
		    strsql = strsql + ",'" + row[7] + "'"
		    strsql = strsql + ",'" + row[8] + "'"
		    strsql = strsql + ",'" + row[9] + "'"
		    strsql = strsql + ",'" + row[10] + "'"
		    strsql = strsql + ",'" + row[11] + "'"
		    strsql = strsql + ",'" + row[12] + "'"
		    strsql = strsql + ",'" + row[13] + "'"
		    strsql = strsql + ",'" + row[14] + "'"
		    strsql = strsql + ",'" + row[15] + "'"
		    strsql = strsql + ")"                
		    
		    logger.loggerpms2.info("Import Doctor SQL \n" + strsql)

		    db.executesql(strsql)
		    db.commit()
		
	    #UPDATE specialityid, roleid, providerid
	    strsql = "UPDATE importdoctor imp, role_default roldef SET imp.roleid = roldef.id WHERE roldef.role = imp.role"
	    logger.loggerpms2.info("Update RoleID \n" + strsql)
	    db.executesql(strsql)
	    db.commit()            

	    strsql = "UPDATE importdoctor imp, speciality_default spldef SET imp.specialityid = spldef.id WHERE spldef.speciality = imp.speciality"
	    logger.loggerpms2.info("Update SpecialityID \n" + strsql)
	    db.executesql(strsql)
	    db.commit()            

	    strsql = "UPDATE importdoctor imp, provider prov SET imp.providerid = prov.id WHERE prov.provider = imp.provider"
	    logger.loggerpms2.info("Update SpecialityID \n" + strsql)
	    db.executesql(strsql)
	    db.commit()            
	    
	    
	    #loop through import doctor table and populate doctor table
	    strsql = "SELECT * from importdoctor where id > 0;"
	    ds = db.executesql(strsql)
	    
	    
	    #0id int(11) AI PK  
	    #1title varchar(45) 
	    #2name varchar(128) 
	    #3provider varchar(128) 
	    #4speciality varchar(128) 
	    #5role varchar(128) 
	    #6xpractice_owner char(1) 
	    #7email varchar(128) 
	    #8cell varchar(45) 
	    #9registration varchar(45) 
	    #10color varchar(45) 
	    #11stafftype varchar(45) 
	    #12docsms char(1) 
	    #13docemail char(1) 
	    #14groupsms char(1) 
	    #15groupemail char(1) 
	    #16providerid int(11) 
	    #17specialityid int(11) 
	    #18roleid int(11)  
	    
	    
	    
	   
	    
	    #xproviderid int(11) 
	    #xspeciality int(11) 
	    #xrole int(11) 
	    #xpractice_owner char(1) 
	    #xemail varchar(128) 
	    #xcell varchar(45) 
	    #xregistration varchar(45) 
	    #xcolor varchar(45) 
	    #xstafftype varchar(45) 
	    #xnotes text 
	    #xdocsms char(1) 
	    #xdocemail char(1) 
	    #xgroupsms char(1) 
	    #xgroupemail char(1) 
	    #xis_active char(1) 
	    #xcreated_by int(11) 
	    #xcreated_on datetime 
	    #xmodified_by int(11) 
	    #xmodified_on datetime	    


	    for i in xrange(0,len(ds)):
		
		db.doctor.insert(
		    providerid = int(common.getid(ds[i][16])), 
		    speciality=  int(common.getid(ds[i][17])),
		    role=  int(common.getid(ds[i][18])),
		    practice_owner = common.getboolean(ds[i][6]),
		    email = common.getstring(ds[i][7]),
		    cell = common.getstring(ds[i][8]),
		    registration=common.getstring(ds[i][9]),
		    color=common.getstring(ds[i][10]),
		    stafftype=common.getstring(ds[i][11]),
		    docsms = common.getboolean(ds[i][12]),
		    docemail = common.getboolean(ds[i][13]),
		    groupsms = common.getboolean(ds[i][14]),
		    groupemail = common.getboolean(ds[i][15]),
		    is_active = True, 
		    created_on = request.now,
		    created_by = providerid, 
		    modified_on=request.now, 
		    modified_by = providerid)      
	 
	except Exception as e:
	    logger.loggerpms2.info("Import Doctor Exception Error - " + str(e) + "\n" + str(e.message))
	    error = "Import Doctor Exception Error - " + str(e)

    return dict(form=form, count=count, error=error)


def importSPAT():
    
    logger.loggerpms2.info("Import SPAT")
    
    strsql = "Truncate table importSPAT"
    db.executesql(strsql)
    db.commit()    
    
    count = 0
    form = SQLFORM.factory(
                Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
                )    
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    
    
    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'    
    

    error = ""
    count = 0
    
    if form.accepts(request,session,keepvalues=True):
	try:
	    xcsvfile = request.vars.csvfile
	    code = ""
	    with open(xcsvfile, 'r') as csvfile:
		reader = csv.reader(csvfile)
		count = 0
		memberID = ""
		
		    
    
		for row in reader:
		    count = count + 1
		    if(count == 1):
			continue		    
		   
		    strsql = "INSERT INTO importspat"
		    strsql = strsql + "(id,agent,name,address1,address2,address3,city,st,pin,"
		    strsql = strsql + "cell,email"
		    strsql = strsql + ")VALUES("
		    strsql = strsql + row[0] + " "
		    strsql = strsql + ",'" + row[1] + "'"
		    strsql = strsql + ",'" + row[2] + "'"
		    strsql = strsql + ",'" + row[3] + "'"
		    strsql = strsql + ",'" + row[4] + "'"
		    strsql = strsql + ",'" + row[5] + "'"
		    strsql = strsql + ",'" + row[6] + "'"
		    strsql = strsql + ",'" + row[7] + "'"
		    strsql = strsql + ",'" + row[8] + "'"
		    strsql = strsql + ",'" + row[9] + "'"
		    strsql = strsql + ",'" + row[10] + "'"
		    strsql = strsql + ")"                
		    
		    logger.loggerpms2.info("Import SPAT SQL \n" + strsql)

		    db.executesql(strsql)
		    db.commit()
	  
	    
	    #loop through import spat table
	    #for each import spat, if it exists, then create a username/password
	    #update the record, send email
	    #if does not exist, insert the record, and send email	    
	    #loop through import spat table and populate agent table
	    strsql = "SELECT * from importspat where id > 0;"
	    ds = db.executesql(strsql)
	    
	    
	    for i in xrange(0,len(ds)):
		
		#check if agent already present, if yes, then skip & continue
		r = db((db.agent.agent == ds[i][1]) & (db.agent.is_active == True)).select()
		if(len(r) > 0):
		    continue;
		
		
		agentid = db.agent.insert(
		    agent = common.getstring(ds[i][1]),
		    name = common.getstring(ds[i][2]),
		    address1 = common.getstring(ds[i][3]),
		    address2 = common.getstring(ds[i][4]),
		    address3 = common.getstring(ds[i][5]),
		    city = common.getstring(ds[i][6]),
		    st = common.getstring(ds[i][7]),
		    pin = common.getstring(ds[i][8]),
		    cell = common.getstring(ds[i][10]),
		    email = common.getstring(ds[i][12]),
		    
		    is_active = True, 
		    created_on = request.now,
		    created_by = 1 if(auth.user == None) else auth.user.id,
		    modified_on=request.now, 
		    modified_by = 1 if(auth.user == None) else auth.user.id
		)      
		
		#if inserted, now create username/password
		if(agentid > 0):
		    
		    username = "SPA" + str(agentid).zfill(4)
		    password = "SPA" + str(agentid).zfill(4)
		    
		    ouser = mdpuser.User(current.globalenv['db'],current.auth,"","")
		    #def spat_registration(self, request, spat, spatname,  email, cell, username, password):
		    rspobj = json.loads(ouser.spat_registration(request, common.getstring(ds[i][1]), common.getstring(ds[i][2]), common.getstring(ds[i][12]),\
		                              common.getstring(ds[i][10]),username,password))
		    if(rspobj["result"] == "fail"):
			logger.loggerpms2.info("Import SPAT Error - " + rspobj["error_message"])
			error = "Import SPAT Error - " + rspobj["error_message"]
		    else:
			error = "success"
	 
	except Exception as e:
	    logger.loggerpms2.info("Import SPAT Exception Error - " + str(e) + "\n" + str(e.message))
	    error = "Import SPAT Exception Error - " + str(e)

    return dict(form=form, count=count, error=error)

def importSPATprovider():
    auth = current.auth
     
    count = 0
    logger.logger.info("Enter Import SPAT Provider") 
    strsql = "Truncate table importspatprov"
    db.executesql(strsql)
    db.commit()    
    
    count = 0
    form = SQLFORM.factory(
                Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
                )    
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    
    
    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'

    error = ""    
    if form.accepts(request,session,keepvalues=True):
	try:
	    if request.vars.csvfile != None:
		xcsvfile = request.vars.csvfile
		code = ""
		with open(xcsvfile, 'r') as csvfile:
		    reader = csv.reader(csvfile)
		    count = 0
		    for row in reader:
			count = count+1
			
			if(count == 1):
			    continue		    
			
			code = row[1]
			strsql = "INSERT INTO importspatprov(id,providercode,spatcode)VALUES("
			strsql = strsql + row[0] + ",'" + row[1] + "','" + row[2] + "')" 
			db.executesql(strsql)    
		        db.commit()
		
		strsql = "SELECT * from importspatprov where id > 0;"
		ds = db.executesql(strsql)
		
		for i in xrange(0,len(ds)):
		    
		    providercode = ds[i][1]
		    spatcode = ds[i][2]
		    
		    ref_code = "AGN"
		    agns = db((db.agent.agent == spatcode) & (db.agent.is_active == True)).select()
		    ref_id = 0 if len(agns) == 0 else agns[0].id
		    provs = db((db.provider.provider == providercode) & (db.provider.is_active == True)).select()
		    provider_id = 0 if len(provs) == 0 else provs[0].id
		    
		    db.prospect_ref.insert(
		        ref_code = ref_code,
		        ref_id = ref_id,
		        provider_id = provider_id
		    )
		    
		    
	except Exception as e:
	    error = "Import SPAT Provider Exception Error - " + str(e)
	    
       
    return dict(form=form, count=count, error = error)

def importproviderregionplan():
    auth = current.auth
     
    count = 0
    logger.logger.info("Enter Import Provider Region Plan") 
    strsql = "Truncate table import_provider_region_plan"
    db.executesql(strsql)
    db.commit()    
    
    count = 0
    form = SQLFORM.factory(
                Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
                )    
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    
    
    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'

    error = ""    
    if form.accepts(request,session,keepvalues=True):
	try:
	    if request.vars.csvfile != None:
		xcsvfile = request.vars.csvfile
		code = ""
		with open(xcsvfile, 'r') as csvfile:
		    reader = csv.reader(csvfile)
		    count = 0
		    for row in reader:
			count = count+1
			
			if(count == 1):
			    continue		    
			
			code = row[1]
			strsql = "INSERT INTO import_provider_region_plan(id,providercode,companycode,regioncode,policy,plancode,procedurepriceplancode)VALUES("
			strsql = strsql + row[0] + ",'" + row[1] + "','" + row[2] + "','" + row[3] +"','" + row[4] + "','" + row[5] + "','" + row[6] + "')" 
			db.executesql(strsql)    
		        db.commit()
		
		strsql = "SELECT * from import_provider_region_plan where id > 0;"
		ds = db.executesql(strsql)
		
		for i in xrange(0,len(ds)):
		    
		    providercode = ds[i][1]
		    companycode = ds[i][2]
		    regioncode = ds[i][3]
		    policy = ds[i][4]
		    plancode = ds[i][5]
		    procedurepriceplancode = ds[i][6]
		    
		    xid = db.provider_region_plan.update_or_insert((db.provider_region_plan.providercode == providercode) &\
			                                           (db.provider_region_plan.companycode == companycode) &\
			                                           (db.provider_region_plan.regioncode == regioncode) &\
			                                           (db.provider_region_plan.policy == policy),
			                                           providercode = providercode,companycode=companycode,
		                                                   regioncode=regioncode,policy=policy,plancode=plancode,
		                                                   procedurepriceplancode = procedurepriceplancode,
			                                           is_active = True,
			                                           created_on = common.getISTFormatCurrentLocatTime(),
			                                           created_by = 1 if(auth.user == None) else auth.user.id,
			                                           modified_on = common.getISTFormatCurrentLocatTime(),
			                                           modified_by = 1 if(auth.user == None) else auth.user.id
			                                           )
	except Exception as e:
	    error = "Import Provider Region Plan Exception Error - " + str(e)
	    
       
    return dict(form=form, count=count, error = error)


def importmember():
    logger.logger.info("Enter Import Member") 
    strsql = "Truncate table importmember"
    db.executesql(strsql)
    db.commit()    
    
    count = 0
    form = SQLFORM.factory(
                Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
                )    
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    
    
    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'

    error = ""
    
    if form.accepts(request,session,keepvalues=True):
        try:
            xcsvfile = request.vars.csvfile
            code = ""
            with open(xcsvfile, 'r') as csvfile:
                reader = csv.reader(csvfile)
                count = 0
                memberID = ""
                
                for row in reader:
		    count = count+1		    
		    if(count == 1):
			continue		    
		    
                    
                    logger.logger.info("Import Member = Count = " + str(count)) 
                    strsql = "INSERT INTO importmember"
                    strsql = strsql + "(ID,pattype,patientmember,groupref,fname,mname,lname,regionid,dob,gender,cell,telephone,email,status,address1,"
                    strsql = strsql + "address2,address3,city,pin,enrollmentdate,premstartdt,premenddt,relation,dependants,amount,membercap,dependantcap,"
                    strsql = strsql + "provider,providername,provaddr1,provaddr2,provaddr3,provcity,provpin,provemail,provtel,"
                    strsql = strsql + "company,hmoplancode,planname,agent,agentname,agentcommission,paymentdate,st)VALUES("                
                    strsql = strsql + row[0] + " "
                    strsql = strsql + ",'" + row[1] + "'"
                    strsql = strsql + ",'" + row[2] + "'"
                    strsql = strsql + ",'" + row[3] + "'"
                    strsql = strsql + ",'" + row[4] + "'"
                    strsql = strsql + ",'" + row[5] + "'"
                    strsql = strsql + ",'" + row[6] + "'"
                    strsql = strsql + "," + row[7] + " "
                    strsql = strsql + ",'" + row[8] + "'"
                    strsql = strsql + ",'" + row[9] + "'"
                    strsql = strsql + ",'" + row[10] + "'"
                    strsql = strsql + ",'" + row[11] + "'"
                    strsql = strsql + ",'" + row[12] + "'"
                    strsql = strsql + ",'" + row[13] + "'"
                    strsql = strsql + ",'" + row[14] + "'"
                    strsql = strsql + ",'" + row[15] + "'"
                    strsql = strsql + ",'" + row[16] + "'"
                    strsql = strsql + ",'" + row[17] + "'"
                    strsql = strsql + ",'" + row[18] + "'"
                    strsql = strsql + ",'" + row[19] + "'"
                    strsql = strsql + ",'" + row[20] + "'"
                    strsql = strsql + ",'" + row[21] + "'"
                    strsql = strsql + ",'" + row[22] + "'"
                    strsql = strsql + "," + row[23] + " "
                    strsql = strsql + "," + row[24] + " "
                    strsql = strsql + "," + row[25] + " "
                    strsql = strsql + "," + row[26] + " "
                    strsql = strsql + ",'" + row[27] + "'"
                    strsql = strsql + ",'" + row[28] + "'"
                    strsql = strsql + ",'" + row[29] + "'"
                    strsql = strsql + ",'" + row[30] + "'"
                    strsql = strsql + ",'" + row[31] + "'"
                    strsql = strsql + ",'" + row[32] + "'"
                    strsql = strsql + ",'" + row[33] + "'"
                    strsql = strsql + ",'" + row[34] + "'"
                    strsql = strsql + ",'" + row[35] + "'"
                    strsql = strsql + ",'" + row[36] + "'"
                    strsql = strsql + ",'" + row[37] + "'"
                    strsql = strsql + ",'" + row[38] + "'"
                    strsql = strsql + ",'" + row[39] + "'"
                    strsql = strsql + ",'" + row[40] + "'"
                    strsql = strsql + "," + row[41] + " "
                    strsql = strsql + ",'" + row[42] + "'"
                    strsql = strsql + ",'" + row[43] + "'"
                    strsql = strsql + ")"                
                    
                    db.executesql(strsql)
                    db.commit()
                    
                    
                    #get group region code  BLR, CHE etc.
		    logger.logger.info("Import Member-1") 
                    r = db(db.groupregion.id == int(row[7])).select()
                    groupregion = r[0].groupregion                

		    logger.logger.info("Import Member-2") 
                    
                    strsql = "SELECT id FROM provider WHERE provider = '" + row[27] + "'"
                    ds = db.executesql(strsql)
                    providerid = int(ds[0][0])

		    logger.logger.info("Import Member-3") 
                    
                    #get company id and company code 
                    strsql = "SELECT id FROM company WHERE company = '" + row[36] + "'"
                    ds = db.executesql(strsql)
                    companyid = int(ds[0][0])
                    companycode =row[36]

		    logger.logger.info("Import Member-4") 
                    
                    strsql = "SELECT id FROM hmoplan WHERE hmoplancode = '" + row[37] + "'"
                    ds = db.executesql(strsql)
                    planid = int(ds[0][0])
                    
		    logger.logger.info("Import Member-5") 
                    
                    #get last member count for this company
                    sql = "UPDATE membercount SET membercount = membercount + 1 WHERE company = " + str(companyid) + ";"
                    db.executesql(sql)
                    db.commit()                
                    xrows = db(db.membercount.company == companyid).select()
                    membercount = int(xrows[0].membercount) 
                    
                    #generate patientmember = BLRMDP100002
                    patientmember = groupregion + companycode[:3] + str(companyid).zfill(3) + str(membercount)
		    logger.logger.info("Import Member-6") 
                    
                    strsql = "UPDATE importmember SET patientmember = '" + patientmember + "', providerid = " + str(providerid) + ", companyid = " + str(companyid) + ", planid=" + str(planid)
                    strsql = strsql + " WHERE id = " + str(row[0])
                    db.executesql(strsql)
                    db.commit()
                    
                    strsql = "INSERT INTO webmember"
                    strsql = strsql + "(webmember,webdob,fname,mname,lname,gender,address1,address2,address3,city,st,pin,telephone,cell,"
                    strsql = strsql + "email,webenrolldate,webenrollcompletedate,status,"
                    strsql = strsql + "company,provider,memberorder,is_active,created_on,created_by,modified_on,modified_by,"
                    strsql = strsql + "groupregion,hmoplan,paid,startdate,upgraded,renewed,groupref)"
                    strsql = strsql + "select patientmember,dob,fname,mname,lname,gender,address1,address2,address3,city,st,pin,telephone,cell,email,"
                    strsql = strsql + "enrollmentdate,enrollmentdate,'Enrolled',companyid,providerid,1,'T',NOW(),1,NOW(),1,regionid,"
                    strsql = strsql + "planid,'T',premstartdt,'F','F',groupref  from importmember where id = "+ str(row[0])                    
                    db.executesql(strsql)
                    db.commit()                
                    
                    
                    strsql = "INSERT INTO patientmember"
                    strsql = strsql + "(patientmember,dob,fname,mname,lname,gender,address1,address2,address3,city,st,pin,telephone,cell,"
                    strsql = strsql + "email,enrollmentdate,premstartdt,premenddt,premium,status,"
                    strsql = strsql + "hmopatientmember,company,provider,memberorder,is_active,created_on,created_by,modified_on,modified_by,"
                    strsql = strsql + "groupregion,hmoplan,paid,startdate,upgraded,renewed,freetreatment,newmember,groupref)"
                    strsql = strsql + "select patientmember,dob,fname,mname,lname,gender,address1,address2,address3,city,st,pin,telephone,cell,email,"
                    strsql = strsql + "enrollmentdate,premstartdt,premenddt,amount,'Enrolled','T',companyid,providerid,1,'T',NOW(),1,NOW(),1,regionid,"
                    strsql = strsql + "planid,'T',premstartdt,'F','F','F','F',groupref  from importmember where id = "+ str(row[0])        
                    db.executesql(strsql)
                    db.commit()
		    
		    logger.logger.info("Import Member-7") 
                    ##send welcomekit
                    props = db(db.urlproperties.id > 0).select(db.urlproperties.welcomekit)
                    welcomekit = common.getboolean(props[0].welcomekit) if(len(props) > 0) else False
                    if(welcomekit):
                        r = db(db.patientmember.patientmember == patientmember).select()
                        if(len(r)>0):
                            patientid = int(common.getid(r[0].id))
                            retval = mail.emailWelcomeKit(db,request,patientid,providerid)
                        
                        
        except Exception as e:
            error = "Import Member Update Exception Error - " + str(e)
                  
            
    return dict(form=form, count=count, error = error)

def importprocedurepriceplan():
    
    strsql = "Truncate table importprocedurepriceplan"
    db.executesql(strsql)
    db.commit()    

    count = 0
    form = SQLFORM.factory(
                Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
                )    
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    
    
    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'
    error = ""
    
    if form.accepts(request,session,keepvalues=True):
        try:
            xcsvfile = request.vars.csvfile
            code = ""
            with open(xcsvfile, 'r') as csvfile:
                reader = csv.reader(csvfile)
                count = 0
                for row in reader:
		    count = count+1
		    if(count == 1):
			continue		    
                    code = row[1]
                    strsql = "INSERT INTO importprocedurepriceplan(id, priceplancode,procedurecode,proceduredescription,UCR,copay,is_free,relgrproc,relgrprocdesc,service_id,service_name,service_category,authorizationrequired)VALUES("
                    strsql = strsql + row[0] + ",'" + row[1] + "','" + row[2] + "','" + row[3] + "'," + row[4] + "," + row[5] + ",'" + row[6] + "','" + row[7] + "','" + \
                        row[8] +"','" + row[9] + "','" + row[10] + "','" + row[11] + "','" + row[12] + "')" 
                    db.executesql(strsql)    
            db.commit()
            
           
            strsql = "update procedurepriceplan set procedurepriceplancode = CONCAT('x', procedurepriceplancode), procedurecode = CONCAT('x',procedurecode), is_active  = 'F'  where procedurepriceplancode = '" + code + "'"
            db.executesql(strsql)    
            db.commit()
            
            strsql = "insert into procedurepriceplan (providerid, procedurepriceplancode, procedurecode, ucrfee, procedurefee,copay, companypays,inspays,remarks,is_free,authorizationrequired,"
            strsql = strsql + "relgrproc,relgrprocdesc,service_id,service_name,service_category,is_active, created_by,created_on, modified_by, modified_on)"
            strsql = strsql + "select 0, priceplancode,procedurecode,ucr,0,copay,0,0,remarks,is_free,authorizationrequired,relgrproc,relgrprocdesc,service_id,service_name,service_category,'T',1,NOW(),1,NOW() FROM importprocedurepriceplan"    
            db.executesql(strsql)    
            db.commit()
        except Exception as e:
            error = "Import Prcoedure Price Plan Exception Error - " + str(e)        
        
        
    return dict(form=form, count=count,error=error)


def importplans():
    
    strsql = "Truncate table importplan"
    db.executesql(strsql)
    db.commit()    

    count = 0
    form = SQLFORM.factory(
                Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
                )    
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    
    
    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'


    
    error = ""
    
    if form.accepts(request,session,keepvalues=True):
        try:
            xcsvfile = request.vars.csvfile
            code = ""
            with open(xcsvfile, 'r') as csvfile:
                reader = csv.reader(csvfile)
                count = 0
                for row in reader:
		    count = count+1
		    
		    if(count == 1):
			continue
		    
                    code = row[1]
                    strsql = "INSERT INTO importplan(id, hmoplancode,name,procedurepriceplancode,is_active,created_on,created_by,modified_on,modified_by,\
		    planfile,groupregion,welcomeletter,voucher_code,discount_amount,walletamount,authorizationrequired,company_code)VALUES("
                    strsql = strsql + row[0] + ",TRIM('" + row[1] + "'),TRIM('" + row[2] + "'),TRIM('" + row[3] + "'),'" + row[4] + "','" +\
		        row[5] + "',1,'" + row[7] + "',1,'" + row[9] + "'," + row[10] + ",'" + row[11] + "','" + row[12] + "'," +\
		        row[13] + "," + row[14] + ",'" + row[15] + "','"  + row[16] + "')"
		    #logger.loggerpms2.info("SQL\n" + strsql)
                    db.executesql(strsql)    
            db.commit()
            
           
            
            
            strsql = "insert into hmoplan (hmoplancode,name,procedurepriceplancode,is_active,created_on,created_by,modified_on,modified_by,planfile,\
	    groupregion,welcomeletter,voucher_code,discount_amount,walletamount,authorizationrequired,company_code)"
            strsql = strsql + " select hmoplancode,name,procedurepriceplancode,is_active,created_on,created_by,modified_on,modified_by,planfile,groupregion,\
	    welcomeletter,voucher_code,discount_amount,walletamount, authorizationrequired,company_code from importplan" 
            db.executesql(strsql)
            db.commit()
        
        except Exception as e:
            error = "Import Plan Rates Exception Error - " + str(e)        
    
        
    return dict(form=form, count=count,error=error)


def importcompanyprovidereligibility():
    
    logger.loggerpms2.info("Import importcompanyprovidereligibility")
    
    strsql = "Truncate table import_company_provider_eligible"
    db.executesql(strsql)
    db.commit()    
    error  = ""
    count = 0
    form = SQLFORM.factory(
                Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
                )    
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    
    
    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'    
    

    error = ""
    count = 0
    
    if form.accepts(request,session,keepvalues=True):
	try:
	    xcsvfile = request.vars.csvfile
	    code = ""
	    with open(xcsvfile, 'r') as csvfile:
		reader = csv.reader(csvfile)
		count = 0
		memberID = ""
		
		    
    
		for row in reader:
		    count = count + 1
		    if(count == 1):
			continue		    
		   
		    strsql = "INSERT INTO import_company_provider_eligible"
		    strsql = strsql + "(id,company_code,provider_code"
		    strsql = strsql + ")VALUES("
		    strsql = strsql + row[0] + " "
		    strsql = strsql + ",'" + row[1] + "'"
		    strsql = strsql + ",'" + row[2] + "'"
		    strsql = strsql + ")"                
		    
		    logger.loggerpms2.info("import_company_provider_eligible SQL \n" + strsql)

		    db.executesql(strsql)
		    db.commit()
	  
	    
	    #loop through import spat table
	    #for each import spat, if it exists, then create a username/password
	    #update the record, send email
	    #if does not exist, insert the record, and send email	    
	    #loop through import spat table and populate agent table
	    strsql = "SELECT * from import_company_provider_eligible where id > 0;"
	    ds = db.executesql(strsql)
	    
	    
	    for i in xrange(0,len(ds)):
		
		company_code = ds[i][1]
		provider_code = ds[i][2]
		
		c = db((db.company.company == company_code) & (db.company.is_active == True)).select()
		companyid = 0 if(len(c) <= 0) else c[0].id

		c = db((db.provider.provider == provider_code) & (db.provider.is_active == True)).select()
		providerid = 0 if(len(c) <= 0) else c[0].id
		
		
		
		cpeid = db.company_provider_eligibility.insert(
		    companyid = companyid,
		    providerid = providerid,
		    is_active = True, 
		)      
	    
	except Exception as e:
	    logger.loggerpms2.info("Import company_provider_eligibility Exception Error - " + str(e) + "\n" + str(e.message))
	    error = "Import company_provider_eligibility Exception Error - " + str(e)

    return dict(form=form, count=count, error=error)

def importplanrates():
    
    strsql = "Truncate table importplanrates"
    db.executesql(strsql)
    db.commit()    

    count = 0
    form = SQLFORM.factory(
                Field('csvfile','string',label='CSV File', requires= IS_NOT_EMPTY())
                )    
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Import'    
    
    xcsvfile = form.element('input',_id='no_table_csvfile')
    xcsvfile['_class'] =  'w3-input w3-border w3-small'


    
    error = ""
    
    if form.accepts(request,session,keepvalues=True):
        try:
            xcsvfile = request.vars.csvfile
            code = ""
            with open(xcsvfile, 'r') as csvfile:
                reader = csv.reader(csvfile)
                count = 0
                for row in reader:
		    count = count+1
		    
		    if(count == 1):
			continue		    
		    
                    code = row[1]
                    strsql = "INSERT INTO importplanrates(id, company,region,plan,relation,covered,premium,companypays,capitation,companyid,planid,regionid)VALUES("
                    strsql = strsql + row[0] + ",'" + row[1] + "','" + row[2] + "','" + row[3] + "','" + row[4] + "'," + row[5] + "," + row[6] + "," + row[7] + "," + row[8] + ",0,0,0)" 
                    db.executesql(strsql)    
            db.commit()
            
            strsql = "UPDATE importplanrates imp, company cmp SET imp.companyid = cmp.id WHERE cmp.company = imp.company"       
            db.executesql(strsql)
            db.commit()
            
            strsql = "UPDATE importplanrates imp, hmoplan hmp SET imp.planid = hmp.id WHERE hmp.hmoplancode = imp.plan"
            db.executesql(strsql)
            db.commit()
            
            strsql = "UPDATE importplanrates imp, groupregion rgn SET imp.regionid = rgn.id WHERE rgn.groupregion = imp.Region"
            db.executesql(strsql)
            db.commit()
            
            strsql = "update companyhmoplanrate cmph, importplanrates imp set cmph.is_active = 'F'  WHERe cmph.company = imp.companyid"
            db.executesql(strsql)
            db.commit()
            
            
            strsql = "insert into companyhmoplanrate (covered, premium, capitation, companypays, company, hmoplan, is_active, created_on, created_by, modified_on, modified_by, relation,groupregion)"
            strsql = strsql + " select covered, premium, capitation, companypays, companyid, planid, 'T', Now(), 1, now(), 1, relation,regionid from importplanrates" 
	    
            db.executesql(strsql)
            db.commit()
        
        except Exception as e:
	    
            error = "Import Plan Rates Exception Error - " + str(e) 
	    logger.loggerpms2.info(error)
	    logger.loggerpms2.info("SQL Query\n" + strsql)	    
    
        
    return dict(form=form, count=count,error=error)

def encrypt():
    
    form = SQLFORM.factory(
            Field('key','string',label='Key'),
            Field('encoded', 'string',label='Encoded'),
            )
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Encrypt'     
    
    xkey = form.element('input',_id='no_table_key')
    xkey['_class'] =  'w3-input w3-border w3-small'
    xencoded = form.element('input',_id='no_table_encoded')
    xencoded['_class'] =  'w3-input w3-border  w3-small'  
    
    result = ''
    if form.accepts(request,session,keepvalues=True):

        key = form.vars.key        
        for i in range(0, len(key)):
            result = result + chr(ord(key[i]) - 2) 
        
        
    return dict(form=form,encoded=result)

def sms_multiple():
    ids = request.vars.id
    source = request.vars.source
    
    redirect(URL('utility', 'send_sms', vars=dict(page=1, mode='multiple',source=source,ids=ids)))
    return dict()



@auth.requires_membership('webadmin')
@auth.requires_login()
def send_sms():

    username   = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "SMS Text"
    
    page=common.getgridpage(request.vars)
    
    formA = SQLFORM.factory(Field('description','text', label='Message'))
    
    formA.element('textarea[name=description]')['_style'] = 'height:100px;line-height:1.0;'
    formA.element('textarea[name=description]')['_rows'] = 5
    formA.element('textarea[name=description]')['_cols'] = 70
   
  
    retVal = None
    if formA.accepts(request,session,keepvalues=True):
        ids = request.vars.ids
        source = request.vars.source
        
        cellnos = ""
        
        mode = request.vars.mode
        if(mode == 'single'):
            uid = int(common.getid(request.vars.ids))
            if(source == 'webmember'):
                pat = db((db.webmember.id == uid) & (db.webmember.is_active == True)).select(db.webmember.cell)
            else:
                pat = db((db.patientmember.id == uid) & (db.patientmember.is_active == True) &  (db.patientmember.hmopatientmember == True)).select(db.patientmember.cell)
            
            cellno = common.getstring(pat[0].cell)    
            if(cellno != ""):
                if(cellno.startswith("91") == True):
                    cellnos = cellnos + cellno
                else:
                    cellnos = cellnos + "91" + cellno
                
        else:
            for uid in ids:
                if(source == 'webmember'):
                    pat = db((db.webmember.id == uid) & (db.webmember.is_active == True)).select(db.webmember.cell)
                else:
                    pat = db((db.patientmember.id == uid) & (db.patientmember.is_active == True)  & (db.patientmember.hmopatientmember == True)).select(db.patientmember.cell)
                
                cellno = common.getstring(pat[0].cell)    
                if(cellno != ""):
                    if(cellno.startswith("91") == True):
                        cellnos = cellnos + cellno + ","
                    else:
                        cellnos = cellnos + "91" + cellno + ","            

            cellnos = cellnos.rstrip(',')
            
        retVal = mail.sendSMS2Email(db,cellnos,formA.vars.description)

        
        
    
    returnurl = URL('default','index')
    return dict(username=username, returnurl=returnurl, formA=formA,formheader=formheader,page=page, retVal = retVal)



def list_appointments_to_reset():
    
    username   = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Appointment List"
    
    page=common.getgridpage(request.vars)
    
        
    fields=(db.t_appointment.f_patientname,db.patientmember.patientmember,\
            db.provider.provider,db.t_appointment.cell,db.t_appointment.f_start_time)
    
    headers={
        'patientmember.patientmember':'Member ID',
        't_appointment.f_patientname':'Patient Name',
        'provider.provider':'Provider',
        't_appointment.cell':'Cell',
        't_appointment.f_start_time':'Appointment Date'
            }



    selectable = None
    selectable = lambda ids : redirect(URL('utility', 'reset_allsendsms', vars=dict(id=ids)))    
 
    links = [lambda row: A('SendSMS',_href=URL("utility","reset_sendsms",vars=dict(page=page, mode='single', ids=row.patientmember.id)))\
             ]
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
    query = ((db.t_appointment.f_start_time >= True) & (db.t_appointment.f_start_time <= True) & (db.t_appointment.sendsms == True))

    left =    [db.patientmember.on(db.patientmember.id==db.t_appointment.patientmember),\
               db.provider.on(db.provider.id==db.t_appointment.provider)
               ]

    orderby = (db.t_appointment.f_start_time)

    form = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
                        left=left,
                        orderby=orderby,
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
    
    
    submit = form.element('.web2py_table input[type=submit]')
    submit['_value'] = T('Send SMS')
    submit['_class'] = 'form_details_button'
        
    
    returnurl = URL('default','index')
    return dict(username=username, returnurl=returnurl, form=form, formheader=formheader,page=page)

def resetappointments():

    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Appointment List"
    
    form = SQLFORM.factory(
        Field('fromdate',
        'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!')),        
        Field('todate',
        'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,length=20,requires = IS_DATE(format=T('%d/%m/%Y'),error_message='must be d/m/Y!'))      
    )
      
    submit = form.element('input',_type='submit')
    submit['_style'] = 'display:none;'
      
    returnurl=URL('default','index')
      
    if form.accepts(request,session,keepvalues=True):
	fromdate = form.vars.fromdate
	todate = form.vars.todate
	redirect(URL('utility','list_appointments_to_reset',\
                                     vars=dict(\
                                               fromdate=fromdate,\
                                               todate=todate)))            
    elif form.errors:
	response.flash = "Error - Reset Appointments! " + str(form.errors)
	redirect(returnurl)
	  
      
    return dict(username=username,returnurl=returnurl,form=form,formheader=formheader)

@auth.requires_membership('webadmin')
@auth.requires_login()
def list_member():

    username   = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Member List"
    
    page=common.getgridpage(request.vars)
    
        
    fields=(db.patientmember.fname,db.patientmember.lname,db.patientmember.patientmember,\
            db.patientmember.cell,db.patientmember.email,db.company.company)
    
    headers={
        'patientmember.patientmember':'Member ID',
        'patientmember.fname':'First Name',
        'patientmember.lname':'Last Name',
        'patientmember.email':'Email',
        'patientmember.cell':'Cell',
        'company.company':'Company'
            }



    selectable = None
    selectable = lambda ids : redirect(URL('utility', 'sms_multiple', vars=dict(id=ids)))    
 
    links = [lambda row: A('SMS',_href=URL("utility","send_sms",vars=dict(page=page, mode='single', ids=row.patientmember.id)))\
             ]
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
    query = ((db.patientmember.is_active==True) & (db.patientmember.is_active == True) & (db.patientmember.hmopatientmember == True))

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
                        selectable = selectable,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )
    
    
    submit = form.element('.web2py_table input[type=submit]')
    submit['_value'] = T('Send SMS')
    submit['_class'] = 'form_details_button'
        
    
    returnurl = URL('default','index')
    return dict(username=username, returnurl=returnurl, form=form, formheader=formheader,page=page)


@auth.requires_membership('webadmin')
@auth.requires_login()
def list_webmember():

    username   = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Member List"
    
    page=common.getgridpage(request.vars)
    
        
    fields=(db.webmember.fname,db.webmember.lname,db.webmember.webmember,db.webmember.status,\
            db.webmember.cell,db.webmember.email,db.company.company)
    
    headers={
        'webmember.webmember':'Member ID',
        'webmember.fname':'First Name',
        'webmember.lname':'Last Name',
        'webmember.email':'Email',
        'webmember.cell':'Cell',
        'webmember.status':'Status',
        'company.company':'Company'
            }



    selectable = None
    selectable = lambda ids : redirect(URL('utility', 'sms_multiple', vars=dict(id=ids,source='webmember')))    
 
    links = [lambda row: A('SMS',_href=URL("utility","send_sms",vars=dict(page=page, mode='single', source='webmember', ids=row.webmember.id)))\
             ]
    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False, csv=False, xml=False)
    
    query = ((db.webmember.is_active==True) & (db.webmember.status != 'Enrolled'))

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
                        selectable = selectable,
                        searchable=True,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        user_signature=True
                       )
    
    
    submit = form.element('.web2py_table input[type=submit]')
    submit['_value'] = T('Send SMS')
    submit['_class'] = 'form_details_button'    
        
    
    returnurl = URL('default','index')
    return dict(username=username, returnurl=returnurl, form=form, formheader=formheader,page=page)

@auth.requires_membership('webadmin')
@auth.requires_login()
def map_member_benefits():
    logger.loggerpms2.info("Enter Map Member Benefits")
    
    #get plancode RPIP599 ID
    c = db(db.company.company == "RPIP599").select(db.company.id,db.company.company)
    companyid = int(common.getid(c[0].id)) if len(c) > 0 else 0
    
    pats = db((db.patientmember.id > 0) & (db.patientmember.company == companyid)).select()
    
    bnft = mdpbenefits.Benefit(db)
    count = 0
    for pat in pats:
	count = count+1
	reqobj = {}
	reqobj["memberid"] = pat.id
	reqobj["plan"] = c[0].company if len(c) > 0 else ""
	bnft.map_member_benefit(reqobj)

    return dict(count=count)

@auth.requires_membership('webadmin')
@auth.requires_login()
def change_of_provider():
    form = SQLFORM.factory(
               Field('source','string',label='Source'),
               Field('target', 'string',label='Target'),
               )
       
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Transfer'     
    
    x = form.element('input',_id='no_table_source')
    x['_class'] =  'w3-input w3-border w3-small'
    y = form.element('input',_id='no_table_target')
    y['_class'] =  'w3-input w3-border  w3-small'  
    
    result = ''
    if form.accepts(request,session,keepvalues=True):

	source = form.vars.source
	target = form.vars.target
	
	p = db((db.provider.provider == source) & (db.provider.is_active == True)).select()
	srcid = p[0].id if(len(p) > 0) else 0
	
	t = db((db.provider.provider == target) & (db.provider.is_active == True)).select()
	trgtid = t[0].id if(len(t) > 0) else 0
	
	db(db.activitytracker.providerid == srcid).update(providerid = trgtid,
	                                                providername = t[0].providername if(len(t) > 0) else "")
	
	
	db(db.bank_details.providerid == srcid).update(providerid = trgtid)
	db(db.casereport.providerid == srcid).update(providerid = trgtid)
	
	db((db.clinic_ref.ref_code == "PRV") & (db.clinic_ref.ref_id == srcid)).update(ref_id = trgtid)
	
	db(db.consentform.providerid == srcid).update(providerid = trgtid)
	db(db.customer.providerid == srcid).update(providerid = trgtid)
	db(db.dentalcasesheet.providerid == srcid).update(providerid = trgtid)
	db(db.dentalchart.providerid == srcid).update(providerid = trgtid)
	
	db((db.dentalimage_ref.ref_code == "PRV") & (db.dentalimage_ref.ref_id == srcid)).update(ref_id = trgtid)
	
	db(db.dentalprocedure_chart.providerid == srcid).update(providerid = trgtid)
	
	db(db.doctor.providerid == srcid).update(providerid = trgtid)
	db((db.doctor_ref.ref_code == "PRV") & (db.doctor_ref.ref_id == srcid)).update(ref_id = trgtid)
	
	db(db.webmember.provider == srcid).update(provider = trgtid)

	db(db.medicaltest.providerid == srcid).update(providerid = trgtid)

	db(db.medicine.providerid == srcid).update(providerid = trgtid)
	
	db(db.mediclaim.providerid == srcid).update(providerid = trgtid)

	db(db.patientmember.provider == srcid).update(provider = trgtid)
	
	db(db.payment.provider == srcid).update(provider = trgtid)
	
	db(db.preregister.provider == srcid).update(provider = trgtid)
	
	db(db.prescription.providerid == srcid).update(providerid = trgtid)
	
	db(db.procedurepriceplan.providerid == srcid).update(providerid = trgtid)

	db(db.providerbank.providerid == srcid).update(providerid = trgtid)

	db(db.prospect_ref.provider_id == srcid).update(provider_id = trgtid)

	
	
	db(db.providercapitationreportparam.provider == srcid).update(provider = trgtid)

	db(db.rldprovider.providerid == srcid).update(providerid = trgtid,providercode=target)

	db(db.role.providerid == srcid).update(providerid = trgtid)
	
	db(db.speciality.providerid == srcid).update(providerid = trgtid)

	db(db.t_appointment.provider == srcid).update(provider = trgtid)
	db(db.t_appointment_archive.provider == srcid).update(provider = trgtid)

	db(db.treatment.provider == srcid).update(provider = trgtid)
	db(db.treatmentplan.provider == srcid).update(provider = trgtid)

	db(db.ind_meeting.provider_id == srcid).update(provider_id = trgtid)
	db(db.ind_meeting_document.provider_id == srcid).update(provider_id = trgtid)

    return dict(form=form)
    