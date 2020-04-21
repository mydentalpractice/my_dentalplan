from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)

import csv

import string
import random
import datetime
import time

from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import logger

#Generate Religare Vouchers
@auth.requires_membership('webadmin')
@auth.requires_login()
def generate_rlgvoucher():
    
    form = SQLFORM.factory(
                   Field('plancode','string',label='Plan Code', requires= IS_NOT_EMPTY()),
                   Field('policy','string',label='Policy', requires= IS_NOT_EMPTY())    
    )
    
    submit = form.element('input',_type='submit')
    submit['_value'] = 'Generate'    
    
    xplancode = form.element('input',_id='no_table_plancode')
    xplancode['_class'] =  'w3-input w3-border w3-small'       
    
    xpolicy = form.element('input',_id='no_table_policy')
    xpolicy['_class'] =  'w3-input w3-border w3-small'           

    errormssg = ""
    count = 0
    
    if form.accepts(request,session,keepvalues=True):
	try:    
	    auth = current.auth
	    plancode = form.vars.plancode
	    for i in range (0, 1000):
		count += 1
		random.seed(int(time.time()) + i)
		
		
		vouchercode = plancode
		for j in range(0,7):
		    vouchercode += str(random.randint(0,9))
		v = db(db.rlgvoucher.vouchercode == 'vouchercode').select(db.rlgvoucher.id)
		if(len(v) > 0):
		    continue
		db.rlgvoucher.insert(plancode=form.vars.plancode,
		                     policy=form.vars.policy,
		                     vouchercode=vouchercode,
		                     is_active = True,
		                     created_on = common.getISTFormatCurrentLocatTime(),
		                     created_by = 1 if(auth.user == None) else auth.user.id,
		                     modified_on = common.getISTFormatCurrentLocatTime(),
		                     modified_by =1 if(auth.user == None) else auth.user.id
		                     )
		db.commit()
		
	    errormssg = "Success!! " + str(count)
	except Exception as e:
	    errormssg = 'Religare Voucher Generation - ' + str(count) + "\n" + str(e)
	    logger.loggerpms2.info(errormssg)
	
    return dict(form=form, errormssg=errormssg)


def list_rlgvoucher():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Vouchers"
    
    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]

    returnurl=URL('default','index')
    page=common.getgridpage(request.vars)
    
    query = (db.rlgvoucher.is_active == True)
    
    fields=(db.rlgvoucher.id,db.rlgvoucher.plancode,db.rlgvoucher.policy,db.rlgvoucher.vouchercode,db.rlgvoucher.fname,db.rlgvoucher.lname)
    db.rlgvoucher.id.readable = False 
    
    headers = {\
           'rlgvoucher.plancode' : 'Plan',
           'rlgvoucher.policy' : 'Policy',
           'rlgvoucher.vouchercode' : 'Voucher',
           'rlgvoucher.fname' : 'First Name',
           'rlgvoucher.lname' : 'Last Name'
           }    

    exportlist = dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)    
    
    links = [lambda row: A('Update',_href=URL("religare","update_rlgvoucher",vars=dict(page=page,voucherid=row.id))),\
             lambda row: A('Delete',_href=URL("religare","delete_rlgvoucher",vars=dict(page=page,voucherid=row.id)))\
            ]


    
    form = SQLFORM.grid(query=query,
                               headers=headers,
                               fields=fields,
                               links=links,
                               paginate=10,
                               orderby=None,
                               exportclasses=exportlist,
                               links_in_grid=True,
                               searchable=True,
                               create=False,
                               deletable=False,
                               editable=False,
                               details=False,
                               user_signature=False
                              )        

    return dict(form=form,page=page,username=username, formheader=formheader,returnurl=returnurl,\
                providerid=providerid,providername=providername)


def new_rlgvoucher():

    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "New Voucher"

    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    returnurl = URL('religare', 'list_rlgvoucher')
    page = 0

    random.seed(int(time.time()))
    vouchercode = "399"
    for j in range(0,7):
	vouchercode += str(random.randint(0,9))    
    
    db.rlgvoucher.vouchercode.default = vouchercode
    db.rlgvoucher.plancode.default = "399"
    
    crud.settings.create_next = URL('religare','list_rlgvoucher')
    
    
    
    formA = crud.create(db.rlgvoucher,message="New Voucher added!")  
    
    
    xpc =  formA.element('input',_id='rlgvoucher_plancode')
    xpc['_class'] = 'form-control'

    xplc =  formA.element('input',_id='rlgvoucher_policy')
    xplc['_class'] = 'form-control'

    
    xvoucher =  formA.element('input',_id='rlgvoucher_vouchercode')
    xvoucher['_class'] = 'form-control'
    
    
    return dict(formA=formA, username=username,formheader=formheader, returnurl=returnurl,page=page,providerid=providerid,providername=providername)
    
    
  

def update_rlgvoucher():
    
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Update Voucher"    
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    voucherid = int(common.getid(request.vars.voucherid))
    
    returnurl = URL('religare', 'list_rlgvoucher')
    page=common.getgridpage(request.vars)
    
    
    
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = returnurl
    
    
    
    formA = crud.update(db.rlgvoucher, voucherid,cast=int, message="Voucher information updated!")  ## 

    xpc =  formA.element('input',_id='rlgvoucher_plancode')
    xpc['_class'] = 'form-control'

    xplc =  formA.element('input',_id='rlgvoucher_policy')
    xplc['_class'] = 'form-control'

    
    xvoucher =  formA.element('input',_id='rlgvoucher_vouchercode')
    xvoucher['_class'] = 'form-control'
    
    xfn =  formA.element('input',_id='rlgvoucher_fname')
    xfn['_class'] = 'form-control'

    xmn =  formA.element('input',_id='rlgvoucher_mname')
    xmn['_class'] = 'form-control'

    xln =  formA.element('input',_id='rlgvoucher_lname')
    xln['_class'] = 'form-control'
    
    return dict(formA=formA, username=username,formheader=formheader,returnurl=returnurl,page=page,providerid=providerid,providername=providername)


def import_rlgvoucher():
	
    strsql = "Truncate table importrlgvoucher"
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
	    count = 0
	    xcsvfile = request.vars.csvfile
	    code = ""
	    with open(xcsvfile, 'r') as csvfile:
		reader = csv.reader(csvfile)
		
		for row in reader:
		    strsql = "INSERT INTO importrlgvoucher"
		    strsql = strsql + "(id,plancode,policy,vouchercode,fname,lname"
		    strsql = strsql + ")VALUES("
		    strsql = strsql + row[0] + " "
		    strsql = strsql + ",'" + row[1] + "'"
		    strsql = strsql + ",'" + row[2] + "'"
		    strsql = strsql + ",'" + row[3] + "'"
		    strsql = strsql + ",'" + row[4] + "'"
		    strsql = strsql + ",'" + row[5] + "'"
		    strsql = strsql + ")"                
		    
		    db.executesql(strsql)
		    
		    
		    db.commit()
	
	
	    #loop through import rlgvoucher table
	    #for each import rlgvoucher, if it exists, then update fname, lname
	    
	    strsql = "SELECT * from importrlgvoucher where id > 0;"
	    ds = db.executesql(strsql)
	    
	    for i in xrange(0,len(ds)):
		#update voucher fname, mname, lname
		r = db((db.rlgvoucher.plancode == ds[i][1]) & (db.rlgvoucher.policy == ds[i][2]) & (db.rlgvoucher.vouchercode == ds[i][3])).select(db.rlgvoucher.id)
		if(len(r) == 1):
		    count = count+1
		    db((db.rlgvoucher.plancode == ds[i][1]) & (db.rlgvoucher.policy == ds[i][2]) & (db.rlgvoucher.vouchercode == ds[i][3])).update(\
		        fname = ds[i][4],
		        lname = ds[i][5],
		        modified_on = common.getISTFormatCurrentLocatTime(),
		        modified_by =1 if(auth.user == None) else auth.user.id
		        )
		
		    db.commit()
		
	except Exception as e:
	    logger.loggerpms2.info("Import Rlg Voucher Exception Error - " + str(e) + "\n" + str(e.message))
				       
	    error = "Import Rlg Voucher  Exception Error - " + str(e)    
		
    return dict(form=form, count=count,error=error)	    