from gluon import current
import json
import datetime
from datetime import timedelta

import requests
import urllib
import base64
import hashlib



from applications.my_pms2.modules import common
from applications.my_pms2.modules import mdppatient
from applications.my_pms2.modules import account

from applications.my_pms2.modules import logger

class Religare:
  def __init__(self,db,providerid):
    self.db = db
    self.providerid = providerid
    
    props = db(db.urlproperties.id > 0).select(db.urlproperties.relgrprodurl, db.urlproperties.relgrapikey)
    
    self.url = "" if(len(props)==0) else props[0].relgrprodurl
    self.apikey = "" if(len(props)==0) else props[0].relgrapikey
    self.ackid = ""
    return 
  
  def errormessage(self,errorcode,response_message=""):
    db = self.db
    
    errormssgs = db((db.rlgerrormessage.code == errorcode) & (db.rlgerrormessage.is_active == True)).select()
    
    #if error_code not in the Error table, then add it, commit, and reload
    if(len(errormssgs)==0):
      db.rlgerrormessage.insert(code=errorcode,internalmessage=response_message,externalmessage=response_message + " Please contact MDP Customer Support")
      db.commit()
      errormssgs = db((db.rlgerrormessage.code == errorcode) & (db.rlgerrormessage.is_active == True)).select()
    errormssg = errorcode + ":" + response_message  if(len(errormssgs) == 0) else errorcode + ":\n" + common.getstring(errormssgs[0].externalmessage)
    
    return errormssg
  
  
  #this will create a new religare patient if not in db else return the current religare pateint.
  #
  def getreligarepatient(self,customer_id, customer_name,cell,dob,gender):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    patobj = []
    fname = ""
    lname = ""
    try:
      customer_name = "RLG_" + str(customer_id)  if(common.getstring(customer_name) == "") else customer_name
      d=dob.split('-')  #dob is in YYYY-m-d format
      dob = datetime.datetime.strptime(d[2] + "/" + d[1] + "/" + d[0], "%d/%m/%Y")
      
      patientmember = "RLGDEL0001"   #default religare member in DEL region
       
       
       
      ##from provider id, get provider city and region
      provs = db((db.rlgprovider.providerid == providerid) & (db.rlgprovider.is_active == True)).select()
      
      if(len(provs)==1):
	p = db(db.provider.id == providerid).select()
        h = db((db.hmoplan.id == int(common.getid(provs[0].planid))) & (db.hmoplan.is_active == True)).select()
        r = db((db.groupregion.id == int(common.getid(provs[0].regionid))) & (db.groupregion.is_active == True)).select()
        c = db(db.company.company == 'RLG').select()
        companyid = int(common.getid(c[0].id)) if(len(c) > 0) else 0
        companycode = common.getstring(c[0].company) if(len(c) > 0) else "RLG"
        hmoplancode = common.getstring(h[0].hmoplancode) if(len(h) > 0) else "RLGMUM102"
        
        sql = "UPDATE membercount SET membercount = membercount + 1 WHERE company = " + str(companyid) + ";"
        db.executesql(sql)
        db.commit()    
     
        xrows = db(db.membercount.company == companyid).select()
        membercount = int(xrows[0].membercount)
     
      
     
        patientmember = hmoplancode + str(membercount)    
      
      
        todaydt = common.getISTFormatCurrentLocatTime()
        todaydtnextyear = common.addyears(todaydt,1)
      
        name = customer_name.split(" ",1)
      
        if(len(name) >= 1 ):
          fname = name[0]
          
        if(len(name) >= 2 ):
          lname = name[1]  
        
	pats = db((db.patientmember.groupref==customer_id)|(db.patientmember.groupref == "ci_" + cell)).select(db.patientmember.address1,\
	                                                                                                       db.patientmember.address2,\
	                                                                                                       db.patientmember.address3,\
	                                                                                                       db.patientmember.city,\
	                                                                                                       db.patientmember.st,\
	                                                                                                       db.patientmember.pin,\
	                                                                                                       db.patientmember.groupregion,\
	                                                                                                       db.patientmember.cell,\
	                                                                                                       db.patientmember.email\
	                                                                                                       )
	
	
        patid = db.patientmember.update_or_insert(((db.patientmember.groupref==customer_id)|(db.patientmember.groupref == "ci_" + cell)),
          patientmember = patientmember,
          groupref = customer_id,
          fname = fname,
          lname = lname,
          address1 = pats[0].address1 if len(pats)>0 else (p[0].address1 if(len(p)>0) else "addr1"),
	  address2 = pats[0].address2 if len(pats)>0 else (p[0].address2 if(len(p)>0) else "addr2"),
	  address3 = pats[0].address3 if len(pats)>0 else (p[0].address3 if(len(p)>0) else "addr3"),
          city = pats[0].city if len(pats)>0 else (p[0].city  if(len(p)>0) else "city"),
          st = pats[0].st if len(pats)>0 else (p[0].st if(len(p)>0) else "st"),
          pin = pats[0].pin if len(pats)>0 else (p[0].pin if(len(p)>0) else "999999"),
          cell = pats[0].cell if len(pats)>0 else (p[0].cell if(len(p)>0) else "999999"),
	  email = pats[0].email if len(pats)>0 else (p[0].email if(len(p)>0) else "x@gmail.com"),
          dob = dob,
          gender = 'Female' if(gender == 'F') else "Male",
          status = 'Enrolled',
          groupregion = int(common.getid(pats[0].groupregion)) if len(pats)>0 else (int(common.getid(r[0].id)) if(len(r)>0) else 1),
          provider = providerid,
          company = int(common.getid(c[0].id)) if(len(c) > 0) else 1,
          hmoplan = int(common.getid(h[0].id)) if(len(h) >0) else 1,
          enrollmentdate = todaydt,
          premstartdt = todaydt,
          premenddt = todaydtnextyear,
          startdate = todaydt,
          hmopatientmember = True,
          paid = True,
          newmember = False,
          freetreatment  = True,
          created_on = common.getISTFormatCurrentLocatTime(),
          created_by = 1 if(auth.user == None) else auth.user.id,
          modified_on = common.getISTFormatCurrentLocatTime(),
          modified_by = 1 if(auth.user == None) else auth.user.id    
        
        )
        db.commit()
        
        if(patid == None):
          r = db(db.patientmember.groupref == customer_id).select(db.patientmember.id)
          if(len(r)==1):
            patid = int(common.getid(r[0].id))
            opat = mdppatient.Patient(db, providerid)
            patobj = opat.getpatient(patid, patid, "")          
          else:    
            patobj=json.dumps({"result":"fail","error_message":self.errormessage("MDP102")})
        else:
          opat = mdppatient.Patient(db, providerid)
          patobj = opat.getpatient(patid, patid, "")          
      else:
        patobj=json.dumps({"result":"fail","error_code":"MDP101","error_message":self.errormessage("MDP101") })
          
    except Exception as e:
      patobj1 = {}
      patobj1["result"] = "fail"
      patobj1["error_code"] = "MDP001"
      patobj1["error_message"] = "Get Religare Patient API:\n" + self.errormessage("MDP100")  + "\n(" + str(e) + ")"
      return json.dumps(patobj1) 
    
    return patobj
 
 
  def updatereligarepatient(self,memberid,email,addr1,addr2,addr3,city,st,pin):
    
     
    db = self.db
    providerid = self.providerid
    auth = current.auth
    
    try:
      memberid = int(memberid)
      
      db(db.patientmember.id == memberid).update(\
        email = email,
        address1 = addr1,
        address2 = addr2,
        address3 = addr3,
        city =city,
        st = st,
        pin = pin,
        modified_on = common.getISTFormatCurrentLocatTime(),
        modified_by = 1 if(auth.user == None) else auth.user.id     
        
      )
      
      retobj = {"result":"success","error_message":""}
    except Exception as e:
      retobj = {"result":"fail","error_code":"MDP100","error_message":"Update Religare Patient API:\n" + self.errormessage("MDP100")  + "\n(" + str(e) + ")"}
    
    return json.dumps(retobj) 

  
  #This method 
  #stringify json obj
  #encrypt stringified json obj
  #base64 encode
  #return {"req_data":<encoded encrypted json data}
  def encoderequestdata(self,jsondata):
    jsonstr = json.dumps(jsondata)
    jsonstrencrypt = self.encrypts(jsonstr)
    #jsonstrencoded = base64.b64encode(jsonstrencrypt)
    #jsonstrdecrypt = self.decrypts(jsonstrencrypt)
    reqobj = {"req_data":jsonstrencrypt}
    
    return reqobj  
  
  def decoderesponsedata(self,jsondatastr):
    #jsonstrdecoded = base64.b64decode(jsondatastr)
     
    jsonstrdecrypt = self.decrypts(jsondatastr)
    jsondata = json.loads(jsonstrdecrypt)
    return jsondata
    
  def encrypts128(self,raw):
        
        phpurl = "http://myphp128.com/encrypt.php"
        
        rlgrobj = {"raw":raw}
        
        resp = requests.post(phpurl,json=rlgrobj)
        
        jsonresp = {}
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
              respobj = resp.json()    
              jsonresp = {
                "encrypt": respobj["encrypt"]
               
              }
        else:
          jsonresp={"encrypt": "Response Error - " + str(resp.status_code)}
          
        return jsonresp["encrypt"]    
 
  def decrypts128(self,encrypt):    
    phpurl = "http://myphp128.com/decrypt.php"
    
    rlgrobj = {"encrypt":encrypt}
    
    resp = requests.post(phpurl,json=rlgrobj)
    
    jsonresp = {}
    if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
          respobj = resp.json()    
          jsonresp = {
            "raw": respobj["raw"]
          }
    else:
      jsonresp = {"raw":"Request Error - " + str(resp.status_code)}
      
    return jsonresp["raw"]
    

  def decrypts(self,encrypt):
    
    
    phpurl = "http://myphp.com/decrypt.php"
    
    rlgrobj = {"encrypt":encrypt}
    
    resp = requests.post(phpurl,json=rlgrobj)
    
    jsonresp = {}
    if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
          respobj = resp.json()    
          jsonresp = {
            "raw": respobj["raw"]
          }
    else:
      jsonresp = {"raw":"Request Error - " + str(resp.status_code)}
      
    return jsonresp["raw"]

  def decrypt(self,encrypt):
    
    phpurl = "http://myphp.com/decrypt.php"
    
    rlgrobj = {"encrypt":encrypt}
    
    resp = requests.post(phpurl,json=rlgrobj)
    
    jsonresp = {}
    if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
          respobj = resp.json()    
          jsonresp = {
            "raw": respobj["raw"]
          }
    return json.dumps(jsonresp)  

  def encrypt_login(self,action,providerid,username,password):
    
    request_data = {"action":action, "providerid":providerid,"username":username, "password":password}
    request_data_string = json.dumps(request_data)
    encrypt_string = self.encrypts(request_data_string)
    
    
    return encrypt_string
  
  def encrypts(self,raw):
      
      phpurl = "http://myphp.com/encrypt.php"
      
      rlgrobj = {"raw":raw}
      
      resp = requests.post(phpurl,json=rlgrobj)
      
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respobj = resp.json()    
            jsonresp = {
              "encrypt": respobj["encrypt"]
             
            }
      else:
        jsonresp={"encrypt": "Response Error - " + str(reps.status_code)}
        
      return jsonresp["encrypt"]

  def encrypt(self,raw):
    
    phpurl = "http://myphp.com/encrypt.php"
    
    rlgrobj = {"raw":raw}
    
    resp = requests.post(phpurl,json=rlgrobj)
    
    jsonresp = {}
    if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
          respobj = resp.json()    
          jsonresp = {
            "encrypt": respobj["encrypt"]
           
          }
    return json.dumps(jsonresp)
  
  #this api will call Religare API 1 - 
  #Rlgr URL : http://... API1
  #Request: policy, cell or custid, action
  #Response: Ack Id.
  #def xsendOTP(self,policy,cell,custid,action):
    
    #db = self.db
    #providerid = self.providerid
  
    #cell = common.modify_cell(cell)
    
    #prop = db(db.urlproperties.id>0).select(db.urlproperties.relgrprodurl,db.urlproperties.religare)
    #religare = common.getboolean(prop[0]["religare"])
    
    #jsonresp = {}
    #if(religare == True):
    
      #url = prop[0]["relgrprodurl"] if(len(prop) == 1) else URL("religare","religare")
    
      #religareobj = {"action":action,"policy":policy,"mobile":cell,"customerid":custid}
    
      #resp = requests.post(url,religareobj )
      
      #if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
        #respobj = resp.json()
        ##populate jsonresp as:
        #jsonresp = {
               #"result" : "success",
               #"ackid"  : "123",  #respobj["ackid"]
               #"action" : action,
               #"policy" : policy,
               #"cell"   : cell,
               #"customerid":custid,
               #"reason" : resp.status_code
               
             #}      
        
      #else:
        #jsonresp = {
               #"result" : "fail",
               #"ackid"  : "",
               #"action":action,
               #"policy" : policy,
               #"cell": cell,
               #"customerid":custid,
               #"reason":"SendOTP request failed ==>" + resp.status_code
             #}      
    
    
    #else:
      ##dummy response
      #jsonresp = {
        #"result" : "success",
        #"ackid"  : "000", 
        #"action" : action,
        #"policy" : policy,
        #"cell"   : cell,
        #"customerid":custid,
        #"reason" : resp.status_code        
      #}
    
    #return json.dumps(jsonresp)
  
  
  #def xvalidateOTP(self, ackid, otp):
      #db = self.db
      #providerid = self.providerid
    
      
      #prop = db(db.urlproperties.id>0).select(db.urlproperties.relgrprodurl,db.urlproperties.religare)
      #religare = common.getboolean(prop[0]["religare"])
      
      #jsonresp = {}
      #if(religare == True):

        #url = prop[0]["relgrprodurl"] if(len(prop) == 1) else URL("religare","religare")

        #religareobj = {"action":"validateOTP","ackid":ackid,"otp":otp}
        
        #resp = requests.post(url,religareobj )
        
        #if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
          #respobj = resp.json()

          ## based on provider, provider city
          
          #jsonresp = {}

        #else:
          #jsonresp = {
                 #"authentication" : "fail",
                 #"ackid" : ackid,
                 #"otp":otp,
                 #"reason":"Authentication failed. " + resp.status_code
               #}      
      
      
      #else:
        ##dummy response
        #jsonresp = {
          #"authentication" : "success",
          #"ackid": ackid,
          #"otp"  : otp,
          #"membername":"RELIGARECUST", 
          #"dob":"01/01/1960",
          #"gender":"M",
          #"description" : "Religare"          
        #}
      
      #return jsonresp    

  
  
  
  #def X_sendOTP(self,policy_number,customer_id,mobile_number):
    
    #jsonresp = {
        #"policy_number": "10271334",
        #"response_status": True,
        #"response_message": "",
        #"mobile_number": "9137908350",
        #"ackid": "38cd00d007",
        #"customer_id": "50753136",
        #"error_code": ""
    #}        
    
      

    
    #return json.dumps(jsonresp)
    
  
  #API-1
  def sendOTP(self,policy_number,customer_id,mobile_number):
    
    db = self.db
    providerid = self.providerid
    url = self.url + "getCustomerInfoForOpd.php"
    apikey = self.apikey
    jsonresp = {}
    
    
    try:
      jsonreqdata = {
        "apikey":apikey,
        "policy_number":policy_number,
        "customer_id":customer_id,
        "mobile_number":mobile_number
      
      }
      
      logger.loggerpms2.info(">>API-1 Send OTP Request\n")
      logger.loggerpms2.info("===Req_data=\n" + json.dumps(jsonreqdata) + "\n")
      
      
      jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
      #call API-1
      resp = requests.post(url,data=jsonencodeddata)
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
            jsonresp = self.decoderesponsedata(respstr)
	    
            if(jsonresp["response_status"]==True):
              self.ackid = jsonresp["ackid"]
              jsonresp["result"] = "success"
              jsonresp["error_message"] = ""
              jsonresp["customer_id"] = "ci_" + mobile_number if(customer_id == "") else customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number
            else:
              self.ackid = ''
              jsonresp["result"] = "fail"
              jsonresp["error_message"] = self.errormessage(jsonresp["error_code"],jsonresp.get('response_message',"")) 
              jsonresp["customer_id"] = "ci_" + mobile_number if(customer_id == "") else customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number            
            
      else:
        jsonresp={
          "result" : "fail",
          "error_message":"Send OTP API-1:\n" + self.errormessage("MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":"ci_" + mobile_number if(customer_id == "") else customer_id,
          "policy_number":policy_number,
          "mobile_number": mobile_number
        }

    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Send OTP API-1:\n" + self.errormessage("MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":"ci_" + mobile_number if(customer_id == "") else customer_id,
        "policy_number":policy_number,
        "mobile_number": mobile_number
      }

    logger.loggerpms2.info(">>API-1 Send OTP Response\n")
    logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp) + "\n")    
    return json.dumps(jsonresp)
  
  #def X_validateOTP(self,ackid,otp,policy_number,customer_id,mobile_number):
    
    
    #jsonresp = {
        #"description": "",
        #"policy_number": "10271334",
        #"dob": "1982-09-12",
        #"response_status": True,
        #"mobile_number": "9137908350",
        #"response_message": "",
        #"gender": "M",
        #"membername": "IMTIYAZ BENGALI",
        #"customer_id": "50753136",
        #"error_code": ""
    #}    
    

    
    #return json.dumps(jsonresp)
  
  
  
  #API-2
  def validateOTP(self,ackid,otp,policy_number,customer_id,mobile_number):
    
    db = self.db
    providerid = self.providerid
    url = self.url + "validateOtpForOpd.php"
    apikey = self.apikey
    
    try:
      
      jsonreqdata = {
        "apikey":apikey,
        "ackid":ackid,
        "otp":otp
       
      
      }

      logger.loggerpms2.info(">>API-2 Validate OTP Request\n")
      logger.loggerpms2.info("===Req_data=\n" + json.dumps(jsonreqdata) + "\n")      

      jsonencodeddata = self.encoderequestdata(jsonreqdata)
   
       
      
      #call API-2
      #resp = requests.post(url,json=jsonencodeddata)
      resp = requests.post(url,data=jsonencodeddata)
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
            jsonresp = self.decoderesponsedata(respstr)
            
            if(jsonresp["response_status"] == True):
              jsonresp["ackid"] = ackid
              jsonresp["dob"] = jsonresp["dob"] if((common.getstring(jsonresp["dob"]) != "") & (common.getstring(jsonresp["dob"]) != "--")) else "1990-01-01"
              jsonresp["gender"] = jsonresp["gender"] if(common.getstring(jsonresp["gender"]) != "") else "M"
              jsonresp["customer_id"] = customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number
              jsonresp["result"] = "success"
              jsonresp["error_message"] = ""
            else:
              jsonresp["result"] = "fail"
	      jsonresp["ackid"] = ackid
              jsonresp["error_message"] = self.errormessage(jsonresp["error_code"],jsonresp.get('response_message',"")) 
              jsonresp["customer_id"] = customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number
      else:
        jsonresp={
          "result" : "fail",
          "error_message":"Validate OTP API-2:\n" + self.errormessage("MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":customer_id,
          "policy_number":policy_number,
          "mobile_number": mobile_number
        }
    
    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Validate OTP API-2:\n" + self.errormessage("MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":customer_id,
        "policy_number":policy_number,
        "mobile_number": mobile_number
      }
  
    logger.loggerpms2.info(">>API-2 Validate OTP Response\n")
    logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp) + "\n")      
    return json.dumps(jsonresp)
  
  #API-3
  def uploadDocument(self,ackid,file_data,filename,policy_number,customer_id,mobile_number):
    
    db = self.db
    providerid = self.providerid
    apikey = self.apikey
    url = self.url + "uploadDocumentForOpd.php"

    ackservices =[]
    jsonresp = {}
    
    try:
      
      #jsonresp["response_status"] =  True
      #jsonresp["response_message"] =  ""
      #jsonresp["error_code"] =  ""
      #jsonresp["customer_id"] = customer_id
      #jsonresp["policy_number"] = policy_number
      #jsonresp["mobile_number"] = mobile_number 
      #jsonresp["result"] = "success"       
      #jsonresp["error_message"] = ""       
      
      #jsonresp["opd_service_details"] = [
        #{
          #"service_id" : "125",
          #"service_name" : "service id 125",
          #"service_category" : "dental"       
        #},
        #{
          #"service_id" : "201",
          #"service_name" : "service id 201",
          #"service_category" : "dental"       
        #},
        #{
          #"service_id" : "221",
          #"service_name" : "service id 221",
          #"service_category" : "dental"       
        #},
        #{
          #"service_id" : "222",
          #"service_name" : "service id 222",
          #"service_category" : "dental"       
        #},
        #{
          #"service_id" : "223",
          #"service_name" : "service id 223",
          #"service_category" : "dental"       
        #},
        #{
          #"service_id" : "224",
          #"service_name" : "service id 224",
          #"service_category" : "dental"       
        #}
      #]
      
      ##populate religare acknowledged services
      #ackservices = jsonresp["opd_service_details"]
      
      
      
      #for ackservice in ackservices:
        
        #db.rlgservices.update_or_insert(((db.rlgservices.ackid==ackid) & (db.rlgservices.service_id == ackservice["service_id"])),
                                         #ackid=ackid, 
                                         #service_id = ackservice["service_id"]
                                         #)
      
     
     #this has to be uncommmented once Religare is ready with new API3 on PROD 25/4/2019
      
      jsonreqdata = {
           "apikey":apikey,
           "ackid":ackid,
           "file_data":file_data,
           "filename":filename
          
         
         }  
      xjsonreqdata = {
           "apikey":apikey,
           "ackid":ackid,
           "filename":filename
         }  
      
      logger.loggerpms2.info(">>API-3 Upload Document Reuest\n")
      logger.loggerpms2.info("===Req_data=\n" + json.dumps(xjsonreqdata) + "\n")      
      
      #this has to be removed once Religare is ready with new API3 on PROD 25/4/2019
      
      #jsonreqdata = {
                 #"apikey":apikey,
                 #"ackid":ackid,
                 #"document":file_data
                
               
               #}       
      
      jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
      #resp = requests.post(url,json=jsonencodeddata)
      resp = requests.post(url,data=jsonencodeddata)
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
            jsonresp = self.decoderesponsedata(respstr)
            
            if(jsonresp["response_status"] == True):
              jsonresp["customer_id"] = customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number 
              jsonresp["result"] = "success"       
              jsonresp["error_message"] = ""       
	      #jsonresp["opd_service_details"] = []
              #populate religare acknowledged services
              if(len(jsonresp["opd_service_details"])==0):
                jsonresp["result"] = "fail"
		jsonresp["error_code"] = "MDP103"
                jsonresp["error_message"] = "Upload Document API-3:\n" + self.errormessage("MDP103") 
                jsonresp["customer_id"] = customer_id
                jsonresp["policy_number"] = policy_number
                jsonresp["mobile_number"] = mobile_number  
		
		
		#logger.loggerpms2.info(">>>Upload Document API-3:\n" + self.errormessage("MDP103") )
		#logger.loggerpms2.info("===Req_data=\n" + json.dumps(jsonresp))                
                #hard coding the services in case of error
                #jsonresp["opd_service_details"] = [
                       #{
                         #"service_id" : "161",
                         #"service_name" : "Dental X-Ray",
                         #"service_category" : "Radiology"       
                       #},
                       #{
                         #"service_id" : "162",
                         #"service_name" : "Periodental",
                         #"service_category" : "Surgical Procedures"       
                       #},
                       #{
                         #"service_id" : "163",
                         #"service_name" : "Endodontic",
                         #"service_category" : "Surgical Procedures"       
                       #},
                       #{
                         #"service_id" : "88",
                         #"service_name" : "Dental Consultation",
                         #"service_category" : "Dental Consultation"       
                       #},
                       #{
                         #"service_id" : "164",
                         #"service_name" : "Extractions",
                         #"service_category" : "Surgical Procedures"       
                       #},
                       #{
                         #"service_id" : "165",
                         #"service_name" : "Conservative",
                         #"service_category" : "Surgical Procedures"       
                       #}
                     #]
              else:
                ackservices = jsonresp["opd_service_details"]
                for ackservice in ackservices:
                  db.rlgservices.update_or_insert(((db.rlgservices.ackid==ackid) & (db.rlgservices.service_id == ackservice["service_id"])),
                                                   ackid=ackid, 
                                                   service_id = ackservice["service_id"]
                                                   )
	
            else:
	

              jsonresp["result"] = "fail"
              jsonresp["error_message"] = self.errormessage(jsonresp["error_code"],jsonresp.get('response_message',"")) 
              jsonresp["customer_id"] = customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number
              
      else:
        jsonresp={
	
          "result" : "fail",
          "error_message":"Upload Document API-3:\n" + self.errormessage("MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":customer_id,
          "policy_number":policy_number,
          "mobile_number": mobile_number
        }
    
    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Send OTP API-1:\n" + self.errormessage("MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":customer_id,
        "policy_number":policy_number,
        "mobile_number": mobile_number
      }
      
    logger.loggerpms2.info(">>API-3 Upload Document Response\n")
    logger.loggerpms2.info("===Resp_data=\n" + json.dumps(jsonresp) + "\n")      
      
    
    return json.dumps(jsonresp) 
  
  
  #def xaddProcedure(self,ackid,sub_service_id,treatment_code,treatment_name,swipe_value):
     
    #db = self.db
    #providerid = self.providerid
    #apikey = self.apikey
    #url = self.url + "getTransactionIdForOpd.php"
    
    #sub_service_id = ""
    #treatment_code = ""
    #treatment_name = ""
    #procedurecode = ""
    
    #jsonreqdata = {
         #"apikey":apikey,
         #"ackid":ackid,
         #"sub_service_id":sub_service_id,
         #"treatment_code":treatment_code,
         #"treatment_name":treatment_name,
         #"swipe_value":swipe_value
        
       
       #}    
    
    #jsonencodeddata = self.encoderequestdata(jsonreqdata)
    
    ##resp = requests.post(url,json=jsonencodeddata)
    #resp = requests.post(url,data=jsonencodeddata)
    #jsonresp = {}
    #if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
          #respstr =   resp.text
          #jsonresp = self.decoderesponsedata(respstr)
    #else:
      #jsonresp={
        #"response_status":False,
        #"response_message":"API Response Error",
        #"error_code":str(resp.status_code),
        #"ackid":""
      #}   
    
      
    #return json.dumps(jsonresp)   
    
  #this procedure 
 
  #API-4
  def geTransactionID(self,ackid,service_id,procedurecode, procedurename,procedurefee,\
                      procedurepiceplancode,policy_number,customer_id,mobile_number):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    apikey = self.apikey
  
    url = self.url + "getTransactionIdForOpd.php"  
    
    try:
      jsonreqdata = {
           "apikey":apikey,
           "ackid":ackid,
           "sub_service_id":service_id,
           "treatment_code":procedurecode,
           "treatment_name":procedurecode,
           "swipe_value":str(procedurefee)
         }    
      
      jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
      #resp = requests.post(url,json=jsonencodeddata)
      resp = requests.post(url,data=jsonencodeddata)      
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
            jsonresp = self.decoderesponsedata(respstr)
            if(jsonresp["response_status"] == True):   
              jsonresp["procedurecode"] = procedurecode
              jsonresp["procedurename"] = procedurename
              jsonresp["procedurefee"] = procedurefee
              jsonresp["procedurepiceplancode"] = procedurepiceplancode
              jsonresp["result"] = "success"
              jsonresp["error_message"] = ""              
              jsonresp["customer_id"] = customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number  
            else:
              jsonresp["result"] = "fail"
              jsonresp["error_message"] = self.errormessage(jsonresp["error_code"],jsonresp.get('response_message',"")) 
              jsonresp["customer_id"] = customer_id
              jsonresp["policy_number"] = policy_number
              jsonresp["mobile_number"] = mobile_number
              
      else:
        jsonresp={
          "result" : "fail",
          "error_message":"Get Transaction ID API-4:\n" + self.errormessage("MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":customer_id,
          "policy_number":policy_number,
          "mobile_number": mobile_number
        }
    
        
    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Get Transaction ID API-4:\n" + self.errormessage("MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":customer_id,
        "policy_number":policy_number,
        "mobile_number": mobile_number
      }
    
    return json.dumps(jsonresp)
    
  #this procedure adds a new procedure to the treatment
  #API-5
  def addRlgProcedureToTreatment(self,ackid,otp,treatmentid,procedurepriceplancode, procedurecode, procedurename,procedurefee,\
                              tooth, quadrant,remarks,policy_number,customer_id,mobile_number):
    db = self.db
    providerid = self.providerid
    auth = current.auth
    apikey = self.apikey
  
    url = self.url + "doTransactionForOpd.php"  
    
    try:
      procs = db((db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode) & \
                 (db.vw_procedurepriceplan_relgr.procedurecode == procedurecode)).select()
      
      procedureid = 0
      ucrfee = 0
      procedurefee = 0
      copay = 0
      companypays = 0
      relgrproc = False
      memberid = 0
      
      service_id = ""
      service_name = ""
      service_category = ""
      
      if(len(procs)>0):
              ucrfee = float(common.getvalue(procs[0].ucrfee))
              procedurefee = float(common.getvalue(procs[0].relgrprocfee))
              if(procedurefee == 0):
                  procedurefee = ucrfee
              copay = float(common.getvalue(procs[0].relgrcopay))
              inspays = float(common.getvalue(procs[0].relgrinspays))
              companypays = float(common.getvalue(procs[0].companypays))
              procedureid = int(common.getid(procs[0].id))    
              relgrproc = bool(common.getboolean(procs[0].relgrproc))
              service_id = int(common.getid(procs[0].service_id))
              service_name = procs[0].service_name
              service_category = procs[0].service_category
              
                
      sub_service_id = ""
      treatment_code = ""
      treatment_name = ""
      procedurecode = ""
      
      jsonreqdata = {
           "apikey":apikey,
           "ackid":ackid,
           "otp":otp
         }    
      
      jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
      #resp = requests.post(url,json=jsonencodeddata)
      resp = requests.post(url,data=jsonencodeddata)      
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
            jsonresp = self.decoderesponsedata(respstr)
            
            if(jsonresp["response_status"] == True):
              if(common.getstring(jsonresp["transaction_status"])=='SUCCESS' ):
                inspays = float(common.getvalue(jsonresp["transaction_amount"]))
                copay = float(common.getvalue(jsonresp["copay"]))
                transaction_id = common.getstring(jsonresp["transaction_id"])
                t = db(db.vw_treatmentlist.id == treatmentid).\
                  select(db.vw_treatmentlist.tplanid,db.vw_treatmentlist.startdate, db.vw_treatmentlist.memberid)
              
                procid = db.treatment_procedure.insert(treatmentid = treatmentid, dentalprocedure = procedureid,status="Started",\
                                                       treatmentdate=t[0].startdate if(len(t)>0) else common.getISTFormatCurrentLocatTime(),\
                                                     ucr = ucrfee, procedurefee=procedurefee, copay=copay,inspays=inspays,companypays=companypays,\
                                                     tooth=tooth,quadrant=quadrant,remarks=remarks,authorized=False,service_id = service_id,\
                                                     relgrproc=relgrproc,relgrtransactionid = transaction_id,relgrtransactionamt=inspays) 
          
                
                tplanid = int(common.getid(t[0].tplanid)) if(len(t) > 0) else 0
                memberid = int(common.getid(t[0].memberid)) if(len(t) > 0) else 0
                #update treatment with new treatment cost
                account.updatetreatmentcostandcopay(db,auth.user,treatmentid)
                #update tplan with new treatment cost
                account.calculatecost(db,tplanid)
                account.calculatecopay(db, tplanid,memberid)
                account.calculateinspays(db,tplanid)
                account.calculatedue(db,tplanid)  
                jsonresp["treatmentprocid"] = procid
                jsonresp["ackid"]=ackid
                jsonresp["result"] =  "success"
                jsonresp["error_message"] = ""
              else:
                jsonresp["ackid"]=ackid
                jsonresp["result"] = "fail"
		jsonresp["error_code"] = "MDP027"
                jsonresp["error_message"] = self.errormessage("MDP027")
            else:
              jsonresp["result"] = "fail"
              jsonresp["error_message"] = self.errormessage(jsonresp["error_code"],jsonresp.get('response_message',"")) 
            
            jsonresp["customer_id"] = customer_id
            jsonresp["policy_number"] = policy_number
            jsonresp["mobile_number"] = mobile_number      
            
      else:
        jsonresp={
          "result" : "fail",
          "error_message":"Do OPD Transaction API-5:\n" + self.errormessage("MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
          "ackid":"",
          "customer_id":customer_id,
          "policy_number":policy_number,
          "mobile_number": mobile_number
        }
    
      

    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Do OPD Transaction API-5:\n" + self.errormessage("MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
        "ackid":"",
        "customer_id":customer_id,
        "policy_number":policy_number,
        "mobile_number": mobile_number
      }

    return json.dumps(jsonresp)
  
  def getreligareprocedures(self,ackid,procedurepriceplancode,searchphrase="",page=0,maxcount=0):
    
    db = self.db
    providerid = self.providerid
    
    
    page = page -1
    urlprops = db(db.urlproperties.id >0 ).select(db.urlproperties.pagination)
    items_per_page = 10 if(len(urlprops) <= 0) else int(common.getvalue(urlprops[0].pagination))
    limitby = ((page)*items_per_page,(page+1)*items_per_page)      
    proclist = []
    procobj = {}
    result = "success"
    error_message = ""
    query = ""
    try:
      if((searchphrase == "") | (searchphrase == None)):
        query = (db.rlgservices.ackid ==ackid) & (db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode)&\
                (db.vw_procedurepriceplan_relgr.is_active == True) & (db.vw_procedurepriceplan_relgr.relgrproc ==True)        
      else:
        query = (db.rlgservices.ackid ==ackid) & (db.vw_procedurepriceplan_relgr.procedurepriceplancode == procedurepriceplancode)&\
                (db.vw_procedurepriceplan_relgr.shortdescription.like('%' + searchphrase + '%'))&\
                (db.vw_procedurepriceplan_relgr.is_active == True) & (db.vw_procedurepriceplan_relgr.relgrproc ==True)        
        
      
      if(page >=0 ): 
        procs = db(query).select(\
                       db.vw_procedurepriceplan_relgr.ALL, db.rlgservices.ALL, \
                       left=[db.vw_procedurepriceplan_relgr.on(db.vw_procedurepriceplan_relgr.service_id == db.rlgservices.service_id)],limitby=limitby\
                      )
        if(maxcount == 0):
          
          procs1 = db(query).select(\
                 db.vw_procedurepriceplan_relgr.ALL, db.rlgservices.ALL, \
                 left=[db.vw_procedurepriceplan_relgr.on(db.vw_procedurepriceplan_relgr.service_id == db.rlgservices.service_id)]\
                )    
          maxcount = len(procs1)
      else:
        procs = db(query).select(\
                       db.vw_procedurepriceplan_relgr.ALL, db.rlgservices.ALL, \
                       left=[db.vw_procedurepriceplan_relgr.on(db.vw_procedurepriceplan_relgr.service_id == db.rlgservices.service_id)]\
                      )
        if(maxcount == 0):
          maxcount = len(procs)

      for proc in procs:
        procobj = {
            "plan":procedurepriceplancode,
            "procedurecode":proc.vw_procedurepriceplan_relgr.procedurecode,
            "altshortdescription":common.getstring(proc.vw_procedurepriceplan_relgr.altshortdescription),
            "procedurefee":float(common.getvalue(proc.vw_procedurepriceplan_relgr.relgrprocfee)),
            "inspays":float(common.getvalue(proc.vw_procedurepriceplan_relgr.relgrinspays)),
            "copay":float(common.getvalue(proc.vw_procedurepriceplan_relgr.relgrcopay)),
            "service_id":common.getstring(proc.vw_procedurepriceplan_relgr.service_id),
            "service_name":common.getstring(proc.vw_procedurepriceplan_relgr.service_name),
            "service_category":common.getstring(proc.vw_procedurepriceplan_relgr.service_category)
        }        
        proclist.append(procobj) 
        result = 'success'
        error_message = ""
        
    except Exception as e:
      result = "fail"
      error_message = "Get Religare Procedure API:\n" + self.errormessage("MDP100")  + "\n(" + str(e) + ")",
      
    xcount = ((page+1) * items_per_page) - (items_per_page - len(procs)) 
            
    bnext = True
    bprev = True
      
    #first page
    if((page+1) == 1):
        bnext = True
        bprev = False
      
    #last page
    if(len(procs) < items_per_page):
        bnext = False
        bprev = True  
          
    return json.dumps({"result":result,"error_message":error_message,"count":len(procs),"page":page+1,"proclist":proclist,"runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev})

  #def xgetreligareprocedures(self,ackid,procedurepriceplancode,page=0,maxcount=0):
    
    #db = self.db
    #providerid = self.providerid
    
    
    #page = page -1
    #items_per_page = 4
    #limitby = ((page)*items_per_page,(page+1)*items_per_page)      
    #proclist = []
    #procobj = {}
    #result = "success"
    #error_message = ""
    #try:
      #if(page >=0 ):    
        #procs = db((db.rlgservices.ackid ==ackid) & (db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode)&\
                      #(db.vw_procedurepriceplan.is_active == True) & (db.vw_procedurepriceplan.relgrproc ==True)).select(\
                       #db.vw_procedurepriceplan.ALL, db.rlgservices.ALL, \
                       #left=[db.vw_procedurepriceplan.on(db.vw_procedurepriceplan.service_id == db.rlgservices.service_id)],limitby=limitby\
                      #)
        #if(maxcount == 0):
          
          #procs1 = db((db.rlgservices.ackid ==ackid) & (db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode)&\
                #(db.vw_procedurepriceplan.is_active == True) & (db.vw_procedurepriceplan.relgrproc ==True)).select(\
                 #db.vw_procedurepriceplan.ALL, db.rlgservices.ALL, \
                 #left=[db.vw_procedurepriceplan.on(db.vw_procedurepriceplan.service_id == db.rlgservices.service_id)]\
                #)    
          #maxcount = len(procs1)
      #else:
        #procs = db((db.rlgservices.ackid ==ackid) & (db.vw_procedurepriceplan.procedurepriceplancode == procedurepriceplancode)&\
                      #(db.vw_procedurepriceplan.is_active == True) & (db.vw_procedurepriceplan.relgrproc ==True)).select(\
                       #db.vw_procedurepriceplan.ALL, db.rlgservices.ALL, \
                       #left=[db.vw_procedurepriceplan.on(db.vw_procedurepriceplan.service_id == db.rlgservices.service_id)]\
                      #)
        #if(maxcount == 0):
          #maxcount = len(procs)
        
        
     
      
      #for proc in procs:
        #procobj = {
            #"plan":procedurepriceplancode,
            #"procedurecode":proc.vw_procedurepriceplan.procedurecode,
            #"altshortdescription":common.getstring(proc.vw_procedurepriceplan.altshortdescription),
            #"procedurefee":float(common.getvalue(proc.vw_procedurepriceplan.procedurefee)),
            #"inspays":float(common.getvalue(proc.vw_procedurepriceplan.inspays)),
            #"copay":float(common.getvalue(proc.vw_procedurepriceplan.copay)),
            #"service_id":common.getstring(proc.vw_procedurepriceplan.service_id),
            #"service_name":common.getstring(proc.vw_procedurepriceplan.service_name),
            #"service_category":common.getstring(proc.vw_procedurepriceplan.service_category)
        #}        
        #proclist.append(procobj) 
        #result = 'success'
        #error_message = ""
        
    #except Exception as e:
      #result = "fail"
      #error_message = "Exception Error getreligareprocedures API " + e.message,
      
    #xcount = ((page+1) * items_per_page) - (items_per_page - len(procs)) 
            
    #bnext = True
    #bprev = True
      
    ##first page
    #if((page+1) == 1):
        #bnext = True
        #bprev = False
      
    ##last page
    #if(len(procs) < items_per_page):
        #bnext = False
        #bprev = True  
          
    #return json.dumps({"result":result,"error_message":error_message,"count":len(procs),"page":page+1,"proclist":proclist,"runningcount":xcount, "maxcount":maxcount, "next":bnext, "prev":bprev})
  
  
  
  #API-6 
  def settleTransaction(self, treatmentid,treatmentprocid):
      
    db = self.db
    providerid = self.providerid
    url = self.url + "settledOpdTransaction.php"
    apikey = self.apikey
    
    
    try:
      xid = db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.id == treatmentprocid)).select()
      relgrproc = False
      transaction_id = ""
      if(len(xid)==1):
        transaction_id = common.getstring(xid[0].relgrtransactionid)
        relgrproc = common.getboolean(xid[0].relgrproc)
      
      trlist = []
      trlist.append(transaction_id)
      
      jsonreqdata = {
           "apikey":apikey,
           "transaction_id":trlist
         }    
        
      jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
      resp = requests.post(url,data=jsonencodeddata)
      jsonresp = {}
      if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
            respstr =   resp.text
            jsonresp = self.decoderesponsedata(respstr)
            if(jsonresp["response_status"] == True):
              j1 = jsonresp["transaction_status"][0]
              j2 = j1[transaction_id]
              
              if(j2 == "SUCCESS"):
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
                db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.id == treatmentprocid)).update(\
                           status = 'Completed')              
              else:
                jsonresp["result"] = "fail"
		jsonresp["error_code"] = "MDP028"
                jsonresp["error_message"] = self.errormessage("MDP028")
		
              
            else:
              jsonresp["result"] = "fail"
              jsonresp["error_message"] = self.errormessage(jsonresp["error_code"],jsonresp.get('response_message',""))
              
      else:
        jsonresp={
          "result" : "fail",
          "error_message":"Transaction Settlement API-6:\n" + self.errormessage("MDP099")  + "\n(" + str(resp.status_code) + ")",
          "response_status":"",
          "response_message":"",
          "error_code":"MDP099",
        }
      
    
    except Exception as e:
      jsonresp = {
        "result":"fail",
        "error_message":"Transaction Settlement API-6:\n" + self.errormessage("MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
      }
          

    
          
    return json.dumps(jsonresp)
    
  
  #API-7
  def voidTransaction(self,treatmentid,treatmentprocid):
    
    db = self.db
    providerid = self.providerid
    auth = current.auth
    apikey = self.apikey
  
    url = self.url + "voidOpdTransaction.php" 
    
    try:
      xid = db((db.treatment_procedure.treatmentid == treatmentid) & (db.treatment_procedure.id == treatmentprocid)).select()
      relgrproc = False
      transaction_id = ""
      if(len(xid)==1):
        transaction_id = common.getstring(xid[0].relgrtransactionid)
        relgrproc = common.getboolean(xid[0].relgrproc)
        
      if(relgrproc == True)  :
        jsonreqdata = {
               "apikey":apikey,
               "transaction_id":transaction_id
        }
        
        jsonencodeddata = self.encoderequestdata(jsonreqdata)
      
        #resp = requests.post(url,json=jsonencodeddata)
        resp = requests.post(url,data=jsonencodeddata)      
        jsonresp = {}
        if((resp.status_code == 200)|(resp.status_code == 201)|(resp.status_code == 202)|(resp.status_code == 203)):
              respstr =   resp.text
              jsonresp = self.decoderesponsedata(respstr) 
              if(jsonresp["response_status"] == True):
                jsonresp["result"] = "success"
                jsonresp["error_message"] = ""
                db((db.treatment_procedure.relgrtransactionid == transaction_id) & \
                   (db.treatment_procedure.relgrproc == True)).update(\
                     is_active = False,
                     status = 'Cancelled',
                             
                )
                account.updatetreatmentcostandcopay(db,None,treatmentid)
              else:
                jsonresp["result"] = "fail"
                jsonresp["error_message"] = self.errormessage(jsonresp["error_code"],jsonresp.get('response_message',"")) 
                
        else:
          
          jsonresp={
            "result" : "fail",
            "error_message":"Void Transaction API-7:\n" + self.errormessage("MDP099")  + "\n(" + str(resp.status_code) + ")",
            "response_status":"",
            "response_message":"",
            "error_code":"MDP099",
          }
      else:
        jsonresp={
          "result" : "fail",
          "error_message":self.errormessage("MDP029") ,
          "response_status":"",
          "response_message":"",
          "error_code":"MDP029",
        }
    
      
    except Exception as e:
      
      jsonresp = {
        "result":"fail",
        "error_message":"Void Transaction API-7:\n" + self.errormessage("MDP100")  + "\n(" + str(e) + ")",
        "response_status":"",
        "response_message":"",
        "error_code":"MDP100",
      }
          
    return json.dumps(jsonresp)
  
  
    