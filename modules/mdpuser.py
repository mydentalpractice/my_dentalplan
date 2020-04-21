# -*- coding: utf-8 -*-
from gluon import current
CRYPT = current.globalenv["CRYPT"]

import datetime
import time

import os;
import uuid
from uuid import uuid4

import json
from applications.my_pms2.modules import common
from applications.my_pms2.modules import status
from applications.my_pms2.modules import cycle
from applications.my_pms2.modules import gender
from applications.my_pms2.modules import mail

from applications.my_pms2.modules import logger



class User:
  def __init__(self,db,auth,username,password):
    self.db = db
    self.auth = auth
    self.username  = username.strip()
    self.password = password.strip()
    return 
  
  
  def getmailserverdetails(self):
     
    db = self.db
    
    
    try:
      
      urlprops = db((db.urlproperties.id > 0) & (db.urlproperties.is_active == True)).\
        select(db.urlproperties.mailsender,db.urlproperties.mailserver, db.urlproperties.mailserverport,\
               db.urlproperties.mailusername, db.urlproperties.mailpassword)
      if(len(urlprops) == 1):
        return json.dumps({"result":"success","error_message":"", "mailserver":urlprops[0].mailserver,"mailserverport":urlprops[0].mailserverport,\
                           "mailurl":urlprops[0].mailsender, "mailusername":urlprops[0].mailusername, "mailpassword":urlprops[0].mailpassword})
      else:
        return json.dumps({"result":"fail","error_message":"Error: Invalide Sender Email Details"})
      
    except Exception as e:
        error_message = "Request Mail Sender Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return  

  def member_registration_validation(self,email, cell, username):
     
    db = self.db

    
    try:
      error_message = ""
  
      r = db((db.auth_user.email == email)).count()
      if((r >= 1) | (email == "")):
        error_message = error_message + "This email " + email + " is already registered or empty. Please enter valid email\n"

      r = db(db.auth_user.username == username).count()
      if((r >= 1) | (username == "")):
        error_message = error_message + "This username " + username + " is already registered or empty. Please enter valid username!\n"

      r = db(db.auth_user.cell == cell).count()
      if((r >= 1) | (cell == "")):
        error_message = error_message + "This mobile number " + cell + " is already registered. Please enter valid cell!\n"
      
      obj = {}
      if(error_message == ""):
        obj = {
          "result":"sucess",
          "error_message":error_message
        }
      else:
        obj = {
          "result":"fail",
          "error_message":error_message
        }
        
      return obj
        

        
    except Exception as e:
        error_message = "Add Mediclaim Procedures Exception Error - " + str(e)
        logger.loggerpms2.info(error_message)
        excpobj = {}
        excpobj["result"] = "fail"
        excpobj["error_message"] = error_message
        return json.dumps(excpobj)    
    
    return

  
    
  
  #Authenticate the user returning JSON data
  #If successful, return authenticate user data, provider data(if user is provider), web admin data (if user is admin), patient data (if user is patient - member or walkin)
  def login(self):
    auth = self.auth
    db = self.db
    
    logger.loggerpms2.info(">>LOGIN API\n")
    logger.loggerpms2.info("===Req_data=\n" + self.username + " " + self.password + "\n")
    
    user = auth.login_bare(self.username, self.password)
    user_data = {}
    
    if(user==False):
      user_data ={
        "result" : "fail",
        "error_message":"Login Failure. Please re-enter correct your username and password"
      }

    else:
        auth.user.impersonated = False
        auth.user.impersonatorid = 0        
        
        provdict = common.getprovider(auth, db)
        
        if(int(provdict["providerid"]) == 0):
            
            #webadmin
            user_data ={
              "result" : 'success',
              "error_message":"",
              "usertype":"webadmin",
              "providerid":int(provdict["providerid"]),
              "providername":provdict["providername"],
            }
          
        else:
            
            #provider
            providerid = int(provdict["providerid"])
            
            rlgprov = db(db.rlgprovider.providerid == providerid).select()
            urlprops = db(db.urlproperties.id > 0).select(db.urlproperties.relgrpolicynumber)
            user_data ={
              "result" : "success",
              "error_message":"",
              "usertype":"provider",
              "providerid":providerid,
              "provider":provdict["provider"],
              "providername":provdict["providername"],
              "practicename":provdict["practicename"],
              "practiceaddress":provdict["practiceaddress"],
              "cell":provdict["cell"],
              "email":provdict["email"],
              "registration":provdict["registration"],
              "rlgprovider": False if(len(rlgprov) == 0) else True,
              "rlgrpolicynumber": "" if(len(urlprops) == 0) else common.getstring(urlprops[0].relgrpolicynumber),
              "regionid": 0 if(len(rlgprov) == 0) else int(rlgprov[0].regionid),
              "planid": 0 if(len(rlgprov) == 0) else int(rlgprov[0].planid)
            
            }
    logger.loggerpms2.info(">>LOGIN API\n")
    logger.loggerpms2.info("===Rsp_data=\n" + json.dumps(user_data) + "\n")
            
    return json.dumps(user_data)
  
  def logout(self):
    auth = self.auth
    auth.logout()
    
    data = {"logout":"Logout Success"}
    
    return json.dumps(data)  
  

  def request_username(self,email):
    
    
    db = self.db
    
    ds = db(db.auth_user.email == email).select(db.auth_user.username,db.auth_user.cell)

    user_data = None
    
    if(len(ds) == 0):
      user_data = {"result":False, "message":"Invalid Email"}
    elif (len(ds) > 1):
      user_data = {"result":False, "message":"More than one user has this email"}
    else:
      user_data = {"result":True, "username":ds[0].username, "cell":ds[0].cell}
      
    
    return json.dumps(user_data)
  
  
 

  def request_resetpassword(self,email):

    db = self.db
    ds = db((db.auth_user.email == email) & (db.auth_user.username == self.username)).select(db.auth_user.id,db.auth_user.cell)
    user_data = None
       
    if(len(ds) == 0):
      user_data = {"result":False, "message":"Invalid Email-Username"}
    elif (len(ds) > 1):
      user_data = {"result":False, "message":"More than one user has this email"}
    else:
      reset_password_key=str(int(time.time()))+'-'+str(uuid.uuid4())
      userid = common.getid(ds[0].id)
      db(db.auth_user.id == userid).update(reset_password_key = reset_password_key)   
      user_data = {"result":True, "resetpasswordkey":reset_password_key,"cell":ds[0].cell}
    
    return json.dumps(user_data)

  
  
  def reset_password(self,email,resetpasswordkey,newpassword):
  
    db = self.db
    auth = self.auth
    
    ds = db((db.auth_user.username == self.username) & (db.auth_user.email == email) & (db.auth_user.reset_password_key == resetpasswordkey)).select(db.auth_user.id)
    
    if(len(ds) == 0):
      user_data = {"result":False, "message":"Invalid Email-Username-Passwordkey"}
    elif (len(ds) > 1):
      user_data = {"result":False, "message":"More than one user has this email"}
    else:
      userid = common.getid(ds[0].id)
      my_crypt = CRYPT(key=auth.settings.hmac_key)
      crypt_pass = my_crypt(newpassword)[0]        

      db(db.auth_user.id == userid).update(password=crypt_pass,reset_password_key='')
      
      user_data = {"result":True, "resetpasswordkey":resetpasswordkey}
    
    return json.dumps(user_data)

  #This method receives validated otp with cell number from mobile app
  #Search the patientmembers for registered cell number.  Ideally, there will be only 
  #one registered cell number, if more are found, then return with error
  #else return with member and dependant list or walk-in patient list
  def otpvalidation(self, cell, email, otp, otpdatetime):
    
    db = self.db   #there is no provider id at this stage
    
    cellno = common.modify_cell(cell)   #in standard with 91
    
    #search for the cell number in patientmember
    pats = db((db.vw_memberpatientlist.cell == cell)|(db.vw_memberpatientlist.cell == cellno)).select()   #compare with 91 or without 91
    
    patlist = []
    patobj  = {}
    message = "Success"
    
    for pat in pats:
      patobj = {
        "member":common.getboolean(pat.hmopatientmember),  #False for walk in patient
        "patientmember" : pat.patientmember,
        "fname":pat.fname,
        "lname":pat.lname,
        "memberid":int(common.getid(pat.primarypatientid)),
        "patientid":int(common.getid(pat.patientid)),
        "primary":True if(pat.patienttype == "P") else False,   #True if "P" False if "D"
        "relation":pat.relation,
        "cell":pat.cell,
        "email":pat.email,
        "providerid":pat.providerid
        
        
      }
      patlist.append(patobj)   
      
      
      db.otplog.insert(\
        
        memberid = int(common.getid(pat.primarypatientid)),
        patientid = int(common.getid(pat.patientid)),
        cell = cell,
        email = email,
        otp = otp,
        otpdatetime = otpdatetime,
        is_active = True,
        created_by = 1,
        created_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1,
        modified_on = common.getISTFormatCurrentLocatTime()
      
      
      )
    message = "Success" if(len(pats)>0) else "Failure"
    return json.dumps({"patientcount":len(pats),"patientlist":patlist,"message":message})
  
  
  def getallconstants(self):
    
    #get appointment status
    apptsts = status.APPTSTATUS
    
    #get appointment duration
    apptdur = cycle.DURATION
    
    #patient status
    patsts = status.STATUS
    
    #genders
    gr = gender.GENDER
    
     
    #pattitles
    pattitle = gender.PATTITLE
    
    #doctitle
    doctitle = gender.DOCTITLE
     
    #regions
    
    
    
    obj = {"gender":gr, "patsts":patsts, "apptsts":apptsts, "apptdur":apptdur, "pattitle":pattitle, "doctitle":doctitle}

    return json.dumps(obj)
  
  
  def member_registration(self, request, sitekey, email, cell, registration_id, username, password):
    #logger.loggerpms2.info("Enter member registration")
    db = self.db
    regobj = {}
    auth = self.auth
    try:
      
      #check for valid registration data
      regobj = self.member_registration_validation(email, cell, username)
      if(regobj["result"] == "fail"):
        return json.dumps(regobj)
      
      db((db.auth_user.sitekey==sitekey) & (db.auth_user.email == email)).update(registration_key = '')
      
      # create new user
      users = db((db.auth_user.email==email) & (db.auth_user.sitekey == sitekey)).select()
      if users:
        my_crypt = CRYPT(key=auth.settings.hmac_key)
        crypt_pass = my_crypt(password)[0]  
        db(db.auth_user.id == users[0].id).update(username=username,password=crypt_pass)
        db.commit()
      else:
        my_crypt = CRYPT(key=auth.settings.hmac_key)
        crypt_pass = my_crypt(password)[0]        
        id_user= db.auth_user.insert(
                                   email = email,
                                   cell = cell,
                                   sitekey = sitekey,
                                   registration_id = registration_id,
                                   username = username,
                                   password = crypt_pass 
                                   )
        db.commit()      
      
      # create new member
      rows = db(db.company.groupkey == sitekey).select()
      companyid = rows[0].id
      companycode = rows[0].company
      webid = db.webmember.insert(email=email,webkey=sitekey,status='No_Attempt',cell=cell,\
                                  webenrolldate = common.getISTFormatCurrentLocatTime(),\
                                  company=companyid,\
                                  provider=1,hmoplan=1,imported=True,
                                  created_on = common.getISTFormatCurrentLocatTime(),
                                  created_by = 1 if(auth.user == None) else auth.user.id,
                                  modified_on = common.getISTFormatCurrentLocatTime(),
                                  modified_by = 1 if(auth.user == None) else auth.user.id    
                                  
                                  )
      
      if(webid > 0):
        db(db.webmember.id == webid).update(webmember = companycode + str(webid))

        regobj["result"] = "success"
        regobj["error_message"] = ""
        regobj["webmemberid"] = str(webid)
        regobj["webmember"] = companycode + str(webid)
        regobj["email"] = email
        regobj["cell"] = cell
        regobj["sitekey"] = sitekey
      else:
        regobj["result"] = "fail"
        regobj["error_message"] = "Member Registration Error"
        
      return json.dumps(regobj)
      
    except Exception as e:
      excpobj = {}
      excpobj["result"] = "fail"
      excpobj["error_message"] = "Member Registration Exception Error - " + str(e)
      logger.loggerpms2.info("Member Registration Exception Error - " + str(e))
      return json.dumps(excpobj)       
   
   
   
   
  
  
    
   
  def provider_registration(self, request, providername, sitekey, email, cell, registration_id, username, password,role):
      logger.loggerpms2.info("Enter provider registration")
      db = self.db
      regobj = {}
      auth = self.auth
      try:
        db((db.auth_user.sitekey==sitekey) & (db.auth_user.email == email)).update(registration_key = '')
        
        # create new user
        users = db((db.auth_user.email==email) & (db.auth_user.sitekey == sitekey)).select()
        if users:
          #logger.loggerpms2.info("before CRYPT_1")
          my_crypt = CRYPT(key=auth.settings.hmac_key)
          #logger.loggerpms2.info("after CRYPT_1")
          crypt_pass = my_crypt(str(password))[0]  
          #logger.loggerpms2.info("after CRYPT_PASS_1")
          db(db.auth_user.id == users[0].id).update(first_name=providername,username=username,password=crypt_pass)
          db.commit()
          #logger.loggerpms2.info("after UPDATE_1")      
          
          # Setting Group Membership
          group_id = auth.id_group(role=role)
          auth.add_membership(group_id, users[0].id)  
         
         
          regobj["result"] = "success"
          regobj["error_message"] = ""
          regobj["new"] = False
          regobj["userid"] = str(users[0].id)
          regobj["email"] = email
          regobj["cell"] = cell
          regobj["sitekey"] = sitekey
             
          
        else:
          #logger.loggerpms2.info("befor CRYPT_2")
          
          my_crypt = CRYPT(key=auth.settings.hmac_key)
          #logger.loggerpms2.info("after CRYPT_2")
          
          crypt_pass = my_crypt(str(password))[0]
          
          #logger.loggerpms2.info("after CRYPT_PASS_2_" + " " + str(crypt_pass).encode("ASCII"))
          id_user= db.auth_user.insert(
                                     email = str(email),
                                     cell = str(cell),
                                     sitekey = str(sitekey),
                                     registration_id = str(registration_id),
                                     username = str(username),
                                    
                                     password = str(crypt_pass) 
                                     )
          db.commit()      
          #logger.loggerpms2.info("after INSERT_2")      
          # Setting Group Membership
          group_id = auth.id_group(role=role)
          auth.add_membership(group_id, id_user)       
  
       
         
          regobj["result"] = "success"
          regobj["error_message"] = ""
          regobj["new"] = True
          regobj["userid"] = str(id_user)
          regobj["email"] = email
          regobj["cell"] = cell
          regobj["sitekey"] = sitekey
      
      
      except Exception as e:
        excpobj = {}
        
        excpobj["result"] = "fail"
        excpobj["new"] = False
        excpobj["userid"] = ""
        excpobj["error_message"] = "Provider Registration Exception Error - " + str(e)
        logger.loggerpms2.info("Provider Registration Exception Error - " + str(e))
        return json.dumps(excpobj)       
  
      return json.dumps(regobj)
      
    
    
  
  
  
  
  
  