# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    #db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
    db =  DAL('mysql://mydentalplan:mydentalplan@mydentalplan.mysql.pythonanywhere-services.com:3306/mydentalplan$my_dentalplan_prod',pool_size=1,check_reserved=['all'],migrate_enabled=False)
    #--db =  DAL('mysql://mydentalplan:mydentalplan@mydentalplan.mysql.pythonanywhere-services.com:3306/mydentalplan$my_dentalplan_db',pool_size=1,check_reserved=['all'],migrate_enabled=False)
    #--db =  DAL('mysql://StagingServer:mydentalplan@StagingServer.mysql.pythonanywhere-services.com:3306/StagingServer$my_dentalplan_stg',pool_size=1,check_reserved=['all'],migrate_enabled=False)
    #db =  DAL('mysql://mydentalplan:mydentalplan@mysql.server:3306/mydentalplan$my_dentalplan_db',pool_size=1,check_reserved=['all'],migrate_enabled=False)
    #db = DAL('mysql://root:root@localhost:3306/mydentalplan$my_dentalplan_db',pool_size=1,check_reserved=['all'],migrate_enabled=False)
    #db = DAL('mysql://root:root@localhost:3306/my_dentalplan_db2',pool_size=1,check_reserved=['all'],migrate_enabled=False)
    #db = DAL('mysql://root:root@localhost:3306/my_dentalplan_db_prod',pool_size=1,check_reserved=['all'],migrate_enabled=False)
    #--db = DAL('mysql://root:root@localhost:3306/mydentalplan$my_dentalplan_prod',pool_size=1,check_reserved=['all'],migrate_enabled=False)
    #db = DAL('mysql://dhimantshah:root@mysql.server/dhimantshah$my_dentalplan_db',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.contrib.account import *
from gluon.contrib.states import *
from gluon.contrib.relations import *
from gluon.contrib.gender import *
from gluon.contrib.treatmentstatus import *
from gluon.contrib.dental import *
from gluon.contrib.cycle import *
from gluon.contrib.status import *


from gluon.contrib.status import ALLSTATUS

#from applications.my_dentalplan.modules.account import *
#from applications.my_dentalplan.modules.states import *
#from applications.my_dentalplan.modules.relations import *
#from applications.my_dentalplan.modules.gender import *
#from applications.my_dentalplan.modules.treatmentstatus import *
#from applications.my_dentalplan.modules.dental import *
#from applications.my_dentalplan.modules.cycle import *
#from applications.my_dentalplan.modules.status import *
#from applications.my_dentalplan.modules.treatmentstatus import *



from gluon.contrib.populate import populate
from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
auth = Auth(db)
service = Service()
plugins = PluginManager()

#additonal fields

## create all tables needed by auth if not custom tables
#auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.janrain_account import use_janrain
use_janrain(auth, filename='private/janrain.key')


#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','xstring'))
##
## Fields can be 'xstring','text','xpassword','xinteger','xdouble','xboolean'
##       'xdate','xtime','xdatetime','xblob','xupload', 'xreference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing

db.define_table('auth_user',
    Field('id','id',
          represent=lambda id:SPAN(id,' ',A('view',_href=URL('auth_user_read',args=id)))),
    Field('first_name', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
          label=T('Provider Name')),
    Field('last_name', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
          label=T('Last Name'),writable=False,readable=False),
    Field('email', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
          label=T('Email')),
    Field('sitekey', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
             label=T('Site Key')),
    Field('username', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
             label=T('Username')),
    Field('password', 'password',
          readable=False,
          label=T('Password')),

    Field('created_on','datetime',default=request.now,
          label=T('Created On'),writable=False,readable=False),
    Field('modified_on','datetime',default=request.now,
          label=T('Modified On'),writable=False,readable=False,
          update=request.now),
    Field('registration_key',default='',
          writable=False,readable=False),
    Field('reset_password_key',default='',
          writable=False,readable=False),
    Field('registration_id',default='',
          writable=False,readable=False),
    format='%(username)s')

db.auth_user.first_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
#db.auth_user.last_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
db.auth_user.password.requires = CRYPT(key=auth.settings.hmac_key)
#db.auth_user.sitekey.requires = IS_NOT_IN_DB(db,db.auth_user.sitekey)
db.auth_user.username.requires = IS_NOT_IN_DB(db, db.auth_user.username)
db.auth_user.registration_id.requires = IS_NOT_IN_DB(db, db.auth_user.registration_id)
db.auth_user.email.requires = (IS_EMAIL(error_message=auth.messages.invalid_email),
                               IS_NOT_IN_DB(db, db.auth_user.email))
auth.define_tables(username=True)            # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
#auth.settings.actions_disabled.append('register')
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['reset_password'])+'/%(key)s to reset your password'

auth.settings.remember_me_form = False

db.define_table('monthly',
                Field('premmonth','integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                auth.signature,
                format='%(premmonth)s'
                )

db.define_table('enrollstatus',
                Field('enrollstatus', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                auth.signature,
                format='%(enrollstatus).s'
                )
db.enrollstatus._singular = "EnrollStatus"
db.enrollstatus._plural = "EnrollStatus"


db.define_table('groupregion',
                Field('groupregion','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('region','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                auth.signature,
                format='%(region)s (%(groupregion)s)'
                )
db.groupregion._singular = "GroupRegion"
db.groupregion._plural   = "GroupRegion"

db.define_table('hmoplan',
                Field('hmoplancode','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='HMOPlan  Code',requires=IS_NOT_EMPTY(error_message='cannot be empty!'),length=20),
                Field('name','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Name',length=32),
                Field('planfile','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Plan File'),
                Field('welcomeletter','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Welcome Letter'),
                Field('groupregion','reference groupregion'),                
                auth.signature,
                format = '%(name)s (%(hmoplancode)s)'
               )

db.hmoplan._singular = "HMOPlan"
db.hmoplan._plural   = "HMOPlan"

## Agent  Table
db.define_table('agent',
                Field('agent', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Agent Code',requires=IS_NOT_EMPTY(error_message='cannot be empty!'), unique=True,length=20),
                Field('name', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Agent Name',length=128),
                Field('address1', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1',length=50),
                Field('address2', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=50),
                Field('address3', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=50),
                Field('city', 'string', default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
                Field('st', 'string', default=None,label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',length=20),
                Field('telephone', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
                Field('cell', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
                Field('fax', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Fax',length=20),
                Field('email', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
                Field('taxid', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='TaxID',length=20),
                Field('enrolleddate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),label='Enrolled Date',default=request.now, requires=IS_DATE(format=('%Y-%m-%d'))),
                Field('holdcommissionchecks', 'boolean', default=False,label='Hold Commission Checks'),
                Field('commissionYTD','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Commission YTD'),
                Field('commissionMTD','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Commission MTD'),
                Field('TotalCompanies','integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=0, label='Companies Assigned'),
                auth.signature,
                format='%(agent)s'
               )
db.agent._singular = "Agent"
db.agent._plural = "Agent"


db.define_table('company',
                Field('company','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Company Code',required=True,unique=True,length=24),
                Field('name', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Company',default='',length=128),
                Field('contact', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='HR Contact',default='',length=128),
                Field('address1', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1', required=True,length=50),
                Field('address2', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=50),
                Field('address3', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=50),
                Field('city', 'string', default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
                Field('st', 'string', default='',label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',required=True,length=20),
                Field('telephone', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
                Field('cell', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
                Field('fax', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Fax',length=20),
                Field('email', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
                Field('enrolleddate','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Enrolled Date',default=request.now, requires=IS_DATE(format=('%Y-%m-%d'))),
                Field('terminationdate','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),label='Termination Date',default=request.now, requires=IS_DATE(format=('%Y-%m-%d'))),
                Field('renewaldate','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),label='Renewal Date',default=request.now, requires=IS_DATE(format=('%Y-%m-%d'))),
                Field('capcycle', 'string',default='Annual',label='Capitation Cycle',length=24,requires = IS_IN_SET(CYCLE)),
                Field('premcycle', 'string', default='Annual',label='Premium Cycle',length=24,requires = IS_IN_SET(CYCLE)),
                Field('adminfee', 'double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Admin Fee'),
                Field('minsubscribers', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=1,label='Minimum Subscribers'),
                Field('maxsubscribers', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=20,label='Maximum Subscribers'),
                Field('minsubsage', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=1,label='Subscriber Age(Min.)'),
                Field('maxsubsage', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=99,label='Subscriber Age(Max'),
                Field('mindependantage', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=1,label='Dependant Age(Min.)'),
                Field('maxdependantage', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=99,label='Dependant Age(Max'),
                Field('maxdependantage', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=99,label='Dependant Age(Max'),
                Field('notes', 'text', default='', label='Notes'),
                Field('commission', 'double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Commission'),
                Field('hmoplan', 'reference hmoplan'),
                Field('agent', 'reference agent'),
                Field('groupkey', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='', label='Group Key', length=20),
                auth.signature,
                format='%(name)s (%(company)s)')

db.company._singular = "Company"
db.company._plural   = "Company"

db.define_table('membercount',
                Field('membercount', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=10000),
                Field('dummy1', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('company',  'reference company'),
                auth.signature
            )


db.define_table('dentalprocedure',
                Field('dentalprocedure','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Procedure',requires=IS_NOT_EMPTY(error_message='cannot be empty!'),unique=False,length=20),
                Field('shortdescription','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Short Name',length=32),
                Field('description','text', default='',label='Description',length=128),
                Field('procedurefee','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Standard Fees'),
                auth.signature,
                format = '%(dentalprocedure)s'
                )

db.dentalprocedure._singular = "Procedure"
db.dentalprocedure._plural   = "Procedure"



db.define_table('copay',
                Field('copay','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Co-Pay'),
                Field('dentalprocedure', 'reference dentalprocedure'),
                Field('shortdescription','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Short Name',length=32),
                Field('procedureucrfee','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Standard Fees'),
                Field('procedurefee','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Procedure Fees'),
                Field('region', 'reference groupregion'),
                Field('hmoplan', 'reference hmoplan'),
                auth.signature
               )

db.copay._singular = "Copay"
db.copay._plural   = "Copay"




db.define_table('agentcommission',
                Field('commission','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Commission'),
                Field('effectiveddate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Effective Date',default=request.now, requires=IS_DATE(format=('%Y-%m-%d'))),
                Field('hmoplan', 'reference hmoplan', label='HMOPlan'),
                Field('agent', 'reference agent', label='Agent'),
                Field('company', 'reference company', label='Company'),
                auth.signature
               )
db.agentcommission._singular = "Agent_Commission"
db.agentcommission._plural = "Agent_Commission"

db.define_table('companyagent',
                Field('company', 'reference company', label='Company'),
                Field('hmoplan', 'reference hmoplan', label='HMOPlan'),
                Field('agent', 'reference agent', label='Agent'),
                auth.signature
               )
db.companyagent._singular = "Company_Agent"
db.companyagent._plural   = "Company_Agent"

db.define_table('companyhmoplan',
                Field('company', 'reference company', label='Company'),
                Field('hmoplan', 'reference hmoplan', label='HMOPlan'),
                Field('agent', 'reference agent', label='Agent'),
                auth.signature
               )
db.companyhmoplan._singular = "Company_HMOPlan"
db.companyhmoplan._plural   = "Company_HMOPlan"

db.define_table('companyhmoplanrate',
                Field('covered','integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=1, label='Covered'),
                Field('premium','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Premium'),
                Field('capitation','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Capitation'),
                Field('companypays','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Company Pays'),
                Field('relation', 'string',default='Self',label='Relationship',length=50,requires = IS_IN_SET(PLANRELATIONS)),
                Field('company', 'reference company', label='Company'),
                Field('hmoplan', 'reference hmoplan', label='HMOPlan'),
                Field('groupregion', 'reference groupregion', label='Region'),
                auth.signature
               )
db.companyhmoplanrate._singular = "Company_HMOPlan_Rate"
db.companyhmoplanrate._plural   = "Company_HMOPlan_Rate"

## Provider Table
db.define_table('provider',
                Field('provider', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Provider Code',default='',length=20),
                Field('providername', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Provider Name ',length=50),
                Field('practicename', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Pratice Name',length=50),
                Field('address1', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1',default='',length=50),
                Field('address2', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=50),
                Field('address3', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=50),
                Field('city', 'string', default='None',label='City',length=50,requires=IS_IN_SET(CITIES)),
                Field('st', 'string', default='None',label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',default='',length=20),
                Field('telephone', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
                Field('cell', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
                Field('fax', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Fax',length=20),
                Field('email', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
                Field('taxid', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='PAN',readable=False, writable=False,length=20),
                Field('enrolleddate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),label='Enrolled Date',default=request.now,length=20),
                Field('assignedpatientmembers', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'),default=0,label='Assigned Members'),
                Field('captguarantee', 'double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Capitation Guarantee'),
                Field('schedulecapitation', 'double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Schedule Guarantee'),
                Field('capitationytd', 'double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Capitation YTD'),
                Field('captiationmtd', 'double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00,label='Capitation MTD'),
                Field('languagesspoken', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Languages Spoken',length=32),
                Field('specialization', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Specialization',length=64),
                Field('sitekey','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Web Enrollment Key', default='1234', length=20),
                Field('groupregion','reference groupregion'),
                auth.signature,
                format='%(providername)s (%(provider)s')
               
db.provider._singular = "Provider"
db.provider._plural = "Provider"



## Member Table
db.define_table('patientmember',
                Field('patientmember', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), required=True, label="Member/Patient ID",length=50),
                Field('groupref', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Employee ID',length=50),
                Field('pan', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Pan Card',length=20),
                Field('dob',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,length=20),
                Field('fname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='First',length=50),
                Field('mname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Middle',length=50),
                Field('lname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Last',length=50),
                Field('gender','string',default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
                Field('address1', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1', required=True,length=50),
                Field('address2', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=50),
                Field('address3', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=50),
                Field('city', 'string', default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
                Field('st', 'string', default='',label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',required=True,length=20),
                Field('telephone', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
                Field('cell', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
                Field('email', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
                Field('enrollmentdate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Enrollment Date',default=request.now,length=20),
                Field('terminationdate', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now,length=20),
                Field('duedate', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now,length=20),
                Field('premstartdt', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now, length=20),
                Field('premenddt', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now, length=20),
                Field('premium', 'double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00),
                Field('status', 'string', label='Status',default='No_Attempt',requires = IS_IN_SET(STATUS)),
                Field('webkey', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Web Key', default='', length=20),
                Field('hmopatientmember','boolean', default=True),
                Field('image','upload'),
                Field('paid', 'boolean',default=False,label='Paid'),
                Field('upgraded', 'boolean',default=False,label='Upgraded'),
                Field('renewed', 'boolean',default=False,label='Renewed'),
                Field('webmember','reference webmember',label='Member'),
                Field('company','reference company',label='Company(Company)'),
                Field('provider','reference provider', label='Provider'),
                Field('memberorder', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'),default=1),
                Field('groupregion','reference groupregion'),
                Field('hmoplan', 'reference hmoplan'),
                Field('startdate','date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Start Date',default=request.now,  \
                      requires=IS_EMPTY_OR(IS_DATE(format=('%Y-%m-%d'))),length=20),
                
                auth.signature,
                format='%(patientmember)s '
               )
db.patientmember._singular = "PatientMember"
db.patientmember._plural   = "PatientMember"

## Member Table
db.define_table('patientmemberdependants',
                Field('fname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='First',length=50),
                Field('mname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Middle',length=50),
                Field('lname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Last',length=50),
                Field('depdob', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='DOB', default=request.now, requires=IS_DATE(format=('%Y-%m-%d')),length=20),
                Field('gender','string', default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
                Field('relation', 'string',default='Spouse',label='Relationship',length=50,requires = IS_IN_SET(RELATIONS)),
                Field('paid', 'boolean',default=False,label='Paid'),
                Field('patientmember','reference patientmember'),
                Field('webdepid','integer'),
                Field('memberorder', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'),default=2),
                auth.signature
               )
db.patientmemberdependants._singular = "Dependant"
db.patientmemberdependants._plural   = "Dependant"


db.define_table('companypatientmember',
                Field('company', 'reference company', label='Company'),
                Field('patientmember', 'reference patientmember', label='Member'),
                auth.signature
               )
db.companypatientmember._singular = "Company_Member"
db.companypatientmember._plural   = "Company_Member"


db.define_table('webmember',
               Field('webmember', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Member ID',length=50),
               Field('groupref', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Employee ID',length=50),
               Field('fname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='First',length=50),
               Field('mname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Middle',length=50),
               Field('lname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Last',length=50),
               Field('address1', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Address 1', length=50),
               Field('address2', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=50),
               Field('address3', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=50),
               Field('city', 'string', default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
               Field('st', 'string', default='None',label='State',length=50,requires = IS_IN_SET(STATES)),
               Field('pin', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',length=20),
               Field('gender','string', default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
               Field('telephone', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
               Field('cell', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
               Field('email', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
               Field('webpan', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Pan Card',length=50),
               Field('webdob',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Birth Date',default=request.now,  requires=IS_DATE(format=('%Y-%m-%d')),length=20),
               Field('status', 'string', label='Status',default='No_Attempt',requires = IS_IN_SET(STATUS)),
               Field('enrollstatus', 'string', label='Status',default='No_Attempt'),
               Field('image','upload'),
               Field('webkey','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Web Key'),
               Field('pin1','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Option 1'),
               Field('pin2','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Option 2'),
               Field('pin3','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Option 3'),
               Field('webenrolldate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Web Enroll Date',default=request.now,length=20),
               Field('webenrollcompletedate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Web Enrollment Complete Date',default=request.now,length=20),
               Field('imported', 'boolean', default=False, label='Imported'),
               Field('paid', 'boolean',default=False,label='Paid'),
               Field('upgraded', 'boolean',default=False,label='Upgraded'),
               Field('renewed', 'boolean',default=False,label='Renewed'),
               Field('company','reference company'),
               Field('provider','reference provider'),
               Field('groupregion','reference groupregion'),
               Field('hmoplan','reference hmoplan'),
               Field('memberorder', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'),default=1),
               Field('startdate',
                     'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='Start Date',default=request.now,  \
                     requires=IS_EMPTY_OR(IS_DATE(format=('%Y-%m-%d'))),length=20),
               auth.signature,
                 format='%(webmember)s'
               )
db.webmember._singular = "Web_Member"
db.webmember._plural   = "Web_Member"

## Member Table
db.define_table('webmemberdependants',
                Field('fname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='First',length=50),
                Field('mname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Middle',length=50),
                Field('lname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Last',length=50),
                Field('depdob', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), label='DOB', default=request.now, requires=IS_DATE(format=('%Y-%m-%d')),length=20),
                Field('gender','string', default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
                Field('relation', 'string',default='Spouse',label='Relationship',length=50,requires = IS_IN_SET(RELATIONS)),
                Field('paid', 'boolean',default=False,label='Paid'),
                Field('webmember','reference webmember'),
                Field('patdepid','integer'),
                Field('memberorder', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'),default=2),
                auth.signature
               )
db.webmemberdependants._singular = "Web_Dependant"
db.webmemberdependants._plural   = "Web_Dependant"

db.define_table('agentcommissionreportparam',
                Field('agent', 'reference agent', label='Agent'),
                Field('startdate', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,length=20, label='Commission Start Date'),
                Field('enddate', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,length=20 ,  label = 'Commission End Date'),
                auth.signature
                )
db.agentcommissionreportparam._singular = "Agent_Commission_Report_Params"
db.agentcommissionreportparam._plural   = "Agent_Commission_Report_Params"


db.define_table('providercapitationreportparam',
                Field('provider', 'reference provider', label='Provider'),
                Field('startdate', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,length=20, label='Commission Start Date'),
                Field('enddate', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,length=20 ,  label = 'Commission End Date'),
                Field('memberstatus', 'string', default='all',length=20 ,  label = 'Commission End Date'),
                Field('is_active', 'boolean',default=True),
                auth.signature
                )
db.providercapitationreportparam._singular = "Provider_Capitation_Report_Params"
db.providercapitationreportparam._plural   = "Provider_Capitation_Report_Params"

db.define_table('treatmentplan',
                Field('treatmentplan','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Treatment_Plan', requires=IS_NOT_EMPTY(error_message='cannot be empty!'), unique=False,length=20),
                Field('description','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Description',length=128),
                Field('startdate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now, requires=IS_DATE(format=('%Y-%m-%d')),label="Start Date",length=20),
                Field('enddate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,requires=IS_DATE(format=('%Y-%m-%d')),label="End Date",length=20),
                Field('status', 'string',default='Open',label='Status',length=20,requires = IS_IN_SET(TREATMENTSTATUS)),
                Field('totaltreatmentcost','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Cost'),
                Field('totalcopay','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Copay'),
                Field('totalinspays','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Insurance Pays'),
                Field('patient', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('patienttype','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='P'),
                Field('patientname','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('provider','reference provider',label='Provider'),
                Field('primarypatient','reference patientmember',label='Member/Patient'),
                auth.signature
                )
db.treatmentplan._singular = "Treatment_Plan"
db.treatmentplan._plural   = "Treatment_Plan"

## Provider Notes Table
db.define_table('treatmentplannotes',
                Field('notes', 'text',label='Notes'),
                Field('treatmentplan', 'reference treatmentplan'),
                auth.signature
               )

db.treatmentplannotes._singular = "Treatment_Notes"
db.treatmentplannotes._plural = "Treatment_Notes"



db.define_table('treatmentplan_procedure',
                 Field('treatmentplan', 'reference treatmentplan'),
                 Field('procedurecode', 'reference dentalprocedure')
                )

db.define_table('treatmentplan_patient',
                 Field('treatmentplan', 'reference treatmentplan'),
                 Field('patientmember', 'reference patientmember')
                )




db.define_table('tplan',
                Field('tplan','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Treatment_Plan', requires=IS_NOT_EMPTY(error_message='cannot be empty!'), unique=False,length=20),
                Field('description','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Description',length=128),
                Field('startdate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now, requires=IS_DATE(format=('%Y-%d-%m')),label="Start Date",length=20),
                Field('enddate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default='',requires=IS_DATE(format=('%Y-%d-%m')),label="End Date",length=20),
                Field('status', 'string', default='Open',label='Status',length=20,requires = IS_IN_SET(TREATMENTSTATUS)),
                Field('totaltreatmentcost','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Cost'),
                Field('totalcopay','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Copay'),
                Field('totalinspays','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Total Insurance Pays'),
                Field('patient', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('patienttype','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='P'),
                Field('patientname','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('provider','reference provider',label='Provider'),
                Field('primarypatient','reference patientmember',label='Member/Patient'),
                auth.signature,
                format = '%(tplan)s'
                )
db.tplan._singular = "TPlan"
db.tplan._plural   = "TPlan"

db.define_table('treatment',
                Field('treatment','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), label='Treatment', requires=IS_NOT_EMPTY(error_message='cannot be empty!'), unique=False,length=20),
                Field('description','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='', label='Description',length=128),
                Field('quadrant','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Quadrant(s)'),
                Field('tooth','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Tooth/Teeth'),
                Field('startdate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now, requires=IS_DATE(format=('%Y-%d-%m')),label="Start Date",length=20),
                Field('enddate',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,requires=IS_DATE(format=('%Y-%d-%m')),label="End Date",length=20),
                Field('status', 'string', default='Open',label='Status',length=20,requires = IS_IN_SET(TREATMENTSTATUS)),
                Field('treatmentcost','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Treatment Cost'),
                Field('copay','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Copay'),
                Field('inspay','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00,label='Ins. Pays'),
                Field('treatmentplan','reference treatmentplan',label='Member/Patient'),
                Field('dentalprocedure','reference dentalprocedure',label='Member/Patient'),
                auth.signature,
                format = '%(treatment)s'
                )
db.treatment._singular = "Treatment"
db.treatment._plural   = "Treatment"

## Provider Notes Table
db.define_table('treatmentnotes',
                Field('notes', 'text',label='Notes'),
                Field('treatment', 'reference treatment'),
                auth.signature
               )

db.treatmentnotes._singular = "TreatmentNotes"
db.treatmentnotes._plural = "TreatmentNotes"

db.define_table('dentalimage',
                Field('title', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Title'),
                Field('image','upload',length=255),
                Field('tooth', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Tooth',length=20),
                Field('quadrant', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Quadrant',length=20),
                Field('imagedate', 
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now,length=20),
                Field('description', 'text', default='',label='Description',length=128),
                Field('treatmentplan', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('treatment', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('patientmember', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('patient', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('provider', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('patientname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('patienttype', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('provider', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                auth.signature,
                format = '%(title)s')
db.dentalimage._singular = "DentalImage"
db.dentalimage._plural = "DentalImage"


db.define_table('t_appointment',
    Field('id','id',
          represent=lambda id:SPAN(id,' ',A('view',_href=URL('appointment_read',args=id)))),
    Field('f_title', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), notnull=True,
          label=T('Title')),
    Field('f_start_time', 'datetime',
          label=T('Start Time')),
    Field('f_end_time', 'datetime',
          label=T('End Time')),
    Field('f_location','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),
          label=T('Location')),
    Field('provider', 'reference provider',label=T('Dentist'), default=''),
    Field('patient', 'reference patientmember', label=T('Patient'), default = ''),

    auth.signature,
    format='%(f_title)s'
    )

db.define_table('t_appointment_archive',db.t_appointment,Field('current_record','reference t_appointment'))

db.define_table('paymenttxlog',
                Field('txno','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Transaction Reference'),
                Field('txdatetime','datetime',default=request.now,length=20, label='Transaction Date_Time' ),
                Field('txamount','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Transaction Amount'),
                Field('totpremium','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Premium Amount'),
                Field('totcompanypays','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Company Pays Amount'),
                Field('servicetax','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Service Tax Amount'),
                Field('swipecharge','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Swipe Charge Amount'),
                Field('total','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00, label='Total Amount'),
                Field('responsecode','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('responsemssg', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('paymentid', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('paymentdate', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('paymentamount','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'), default=0.00),
                Field('paymenttxid','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('accountid','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('premstartdt','datetime',length=20, label='Premium Start Date' ),
                Field('premenddt','datetime',length=20, label='Premium End Date' ),
                Field('webmember','reference webmember'),
                Field('patientmember','reference patientmember'),
                Field('memberpolicyrenewal','reference memberpolicyrenewal'),
                auth.signature
                )

db.paymenttxlog._singular = "PaymentTxLog"
db.paymenttxlog._plural = "PaymentTxLog"

db.define_table('urlproperties',
                Field('callbackurl', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('mydp_ipaddress', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('mydp_port', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='8001'),
                Field('mydp_application', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='my_dentalplan'),
                Field('pms_ipaddress', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('pms_port', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='8001'),
                Field('pms_application', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='jaiminipms'),
                Field('mailserver','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('mailserverport','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='25'),
                Field('mailsender','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('mailcc','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('mailusername','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('mailpassword','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('servicetax','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00),
                Field('swipecharge','double',widget = lambda field, value:SQLFORM.widgets.double.widget(field, value, _class='form_details'),default=0.00),
                Field('jasperreporturl','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('jdomain','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('jport','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('j_username','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('j_password','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details')),
                Field('renewalnoticeperiod','integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'),default=0, label='Renewal Notice Period'),
                Field('renewalcallback','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('emailreceipt','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('upgradepolicycallback','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('smsusername','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                Field('smsemail','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default=''),
                auth.signature
                )
db.urlproperties._singular = "URL_Properties"
db.urlproperties._plural = "URL_Properties"


db.define_table('enrollmentstatus',
                Field('companyid', 'reference company'),
                Field('userid', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details')),
                Field('fname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('mname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('lname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                Field('gender','string',default='Male',label='Gender',length=10),
                Field('webdob',
'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=''),
                Field('address1', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='', length=50),
                Field('address2', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 2',length=50),
                Field('address3', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Address 3',length=50),
                Field('city', 'string', default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
                Field('st', 'string', default='None',label='State',length=50,requires = IS_IN_SET(STATES)),
                Field('pin', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Pin',length=20),
                Field('telephone', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Telephone',length=20),
                Field('cell', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Cell',length=20),
                Field('email', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Email',length=50),
                Field('webpan', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default='',label='Pan Card',length=50),
                Field('status', 'string', label='Status',default='No_Attempt'),
                Field('pin1','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Option 1'),
                Field('pin2','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Option 2'),
                Field('pin3','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),default='',label='Option 3'),
                Field('provider','reference provider'),
                Field('groupregion','reference groupregion'),
                Field('dependants', 'integer',widget = lambda field, value:SQLFORM.widgets.integer.widget(field, value, _class='form_details'), default=0),
                Field('companyname', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'), default=''),
                auth.signature

                )
db.enrollmentstatus._singular = "enrollmentstatus"
db.enrollmentstatus._plural = "enrollmentstatus"

db.define_table('vw_assignedmembers',
                Field('pattype', 'string'),
                Field('patientmember', 'string'),
                Field('groupref', 'string'),
                Field('fname', 'string'),
                Field('lname', 'string'),
                Field('cell', 'string'),
                Field('dob', 'date'),
                Field('email', 'string'),
                Field('enrollmentdate', 'date'),
                Field('premenddt', 'date'),
                Field('hmopatientmember', 'boolean'),
                Field('is_active', 'boolean'),
                Field('provider', 'reference provider'),
                Field('company', 'string'),
                Field('providername', 'string'),
                Field('hmoplan', 'string'),
                migrate = False
                )

db.define_table('vw_enrollmentstatus',
                Field('webmember', 'string'),
                Field('groupref', 'string'),
                Field('fname', 'string'),
                Field('lname', 'string'),
                Field('status', 'string'),
                Field('provider', 'string'),
                Field('providername', 'string'),
                Field('companyid', 'reference company'),
                Field('company', 'string'),
                Field('hmoplancode', 'string'),
                Field('cell', 'string'),
                Field('webenrollcompletedate', 'date'),
                Field('is_active', 'boolean'),
                Field('dependants', 'integer'),
                migrate = False
                )

db.define_table('vw_enrollmentstatus1',
                Field('id', 'integer'),
                Field('webmember', 'string'),
                Field('groupref', 'string'),
                Field('fname', 'string'),
                Field('lname', 'string'),
                Field('status', 'string'),
                Field('provider', 'string'),
                Field('providername', 'string'),
                Field('companyid', 'reference company'),
                Field('company', 'string'),
                Field('hmoplancode', 'string'),
                Field('cell', 'string'),
                Field('webenrollcompletedate', 'date'),
                Field('is_active', 'boolean'),
                Field('dependants', 'integer'),
                migrate = False
                )

db.define_table('vw_member',
                Field('pattype', 'string'),
                Field('patientmember',  'string'),
                Field('groupref',  'string'),
                Field('fname',  'string'),
                Field('mname',  'string'),
                Field('lname',  'string'),
                Field('dob',  'date'),
                Field('cell',  'string'),
                Field('telephone',  'string'),
                Field('email',  'string'),
                Field('status',  'string'),
                Field('address1',  'string'),
                Field('address2','string'),
                Field('address3','string'),
                Field('city','string'),
                Field('pin','string'),
                Field('enrollmentdate','date'),
                Field('terminationdate','date'),
                Field('premstartdt','date'),
                Field('premenddt','date'),
                Field('is_active','boolean'),
                Field('relation','string'),
                Field('dependants','integer'),
                Field('amount','double'),
                Field('membercap','double'),
                Field('dependantcap','double'),
                Field('provider','string'),
                Field('providername','string'),
                Field('provaddress1','string'),
                Field('provaddress2','string'),
                Field('provaddress3','string'),
                Field('provcity','string'),
                Field('provpin','string'),
                Field('provemail','string'),
                Field('provtelephone','string'),
                Field('companyid','reference company'),
                Field('company','string'),
                Field('hmoplancode','string'),
                Field('planname','string'),
                Field('agent','string'),
                Field('agentname','string'),
                Field('agentcommission','string'),
                Field('webmemberid','reference webmember'),
                Field('paymentdate','string'),
                migrate = False
                )

db.define_table('vw_memberpayment',
                Field('webmemberid','reference webmember'),
                Field('paymentdate','string'),
                migrate = False
                )
db.define_table('vw_patientmemberdependants',
                Field('dependants','integer'),
                Field('patientmember','reference patientmember'),
                migrate = False
                )

db.define_table('vw_birthday',
                Field('dependants','integer'),
                Field('patientmember','reference patientmember'),
                migrate = False
                )

db.define_table('enrollmentstatusreportparams',
                Field('company', 'reference company', label='Company'),
                Field('companyname','string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value, _class='form_details'),label='Company Name'),
                Field('status', 'reference company', label='Status',requires = IS_IN_SET(ALLSTATUS)),
                Field('startdt', 'date',widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'), default=request.now,length=20, label='Start Date'),
                Field('enddt', 'date', widget = lambda field, value:SQLFORM.widgets.date.widget(field, value, _style='height:30px'),default=request.now,length=20, label='End Date'),
                Field('is_active', 'boolean',default=True),
                Field('memberonly', 'boolean',default=True),
                auth.signature
                )
db.enrollmentstatusreportparams._singular = "enrollmentstatusreportparams"
db.enrollmentstatusreportparams._plural   = "enrollmentstatusreportparams"

db.define_table('memberpolicyrenewal',
                Field('patientmember', 'reference patientmember', label='Member'),
                Field('paymenttxlog','reference paymenttxlog'),
                Field('renewaldate', 'date',length=20, label='Renewal Date'),
                Field('renewaldays', 'integer', default=0, label='Renewal Days'),
                Field('reminders', 'integer', default=0, label='Reminders'),
                Field('reminderdate', 'date',length=20, label='Reminder Date'),
                Field('premium', 'double', default=0.00, label="Premium Amount"),
                Field('companyamt', 'double', default=0.00, label="Company Amount"),
                Field('memberamt', 'double', default=0.00, label="Member Amount"),
                Field('swipecharge', 'double', default=0.00, label="Swipe Charge"),
                Field('servicetax', 'double', default=0.00, label="Service Tax"),
                Field('total', 'double', default=0.00, label="Total"),
                Field('newrenewaldate', 'date',length=20, label='New Renewal Date'),
                Field('newduedate', 'date',length=20, label='New Due Date'),
                Field('paymentmode','string', default='None',label='Payment Mode',length=20,requires = IS_IN_SET(PAYMENTMODE)),
                Field('renewed', 'boolean',default=False),
                Field('is_active', 'boolean',default=True),
                auth.signature
                )
db.memberpolicyrenewal._singular = "memberpolicyrenewal"
db.memberpolicyrenewal._plural   = "memberpolicyrenewal"



db.define_table('dependantpolicyrenewal',
                Field('patientmemberdependant', 'reference patientmemberdependant', label='Dependant Member'),
                Field('memberpolicyrenewal', 'reference memberpolicyrenewal'),
                Field('paymenttxlog','reference paymenttxlog'),
                Field('premium', 'double', default=0.00, label="Premium Amount"),
                Field('companyamt', 'double', default=0.00, label="Company Amount"),
                Field('memberamt', 'double', default=0.00, label="Member Amount"),
                Field('is_active', 'boolean',default=True),
                auth.signature
                )
db.dependantpolicyrenewal._singular = "dependantpolicyrenewal"
db.dependantpolicyrenewal._plural   = "dependantpolicyrenewal"




db.define_table('memberpayment',
                Field('patientmember','integer'),
                Field('premium', 'double', default=0.00, label="Premium Amount"),
                Field('companyamt', 'double', default=0.00, label="Company Amount"),
                Field('memberamt', 'double', default=0.00, label="Member Amount"),
                Field('is_active', 'boolean',default=True),
                auth.signature
                )
db.memberpayment._singular = "memberpayment"
db.memberpayment._plural   = "memberpayment"

db.define_table('dependantpayment',
                Field('patientmember','integer'),
                Field('premium', 'double', default=0.00, label="Premium Amount"),
                Field('companyamt', 'double', default=0.00, label="Company Amount"),
                Field('memberamt', 'double', default=0.00, label="Member Amount"),
                Field('is_active', 'boolean',default=True),
                auth.signature
                )
db.dependantpayment._singular = "dependantpayment"
db.dependantpayment._plural   = "dependantpayment"

db.define_table('appointmentreminders',
                Field('appointmentid','reference t_appointment'),
                Field('lastreminder', 'date'),
                auth.signature
                )
db.appointmentreminders._singular = "appointmentreminders"
db.appointmentreminders._plural   = "appointmentreminders"

db.define_table('birthdayreminders',
                Field('patient','reference patientmember'),
                Field('lastreminder', 'date'),
                auth.signature
                )
db.appointmentreminders._singular = "birthdayreminders"
db.appointmentreminders._plural   = "birthdayreminders"


db.define_table('vw_providercapitation',
                Field('company','string'),
                Field('hmoplancode','string'),
                Field('premstartdt', 'date'),
                Field('premenddt', 'date'),
                Field('premmonth', 'string'),
                Field('capitation', 'double'),
                Field('provider','reference provider')
                )
db.vw_providercapitation._singular = "vw_providercapitation"
db.vw_providercapitation._plural   = "vw_providercapitation"


db.define_table('importdata',
                Field('memberid', 'string'),
                Field('employeeid', 'string', default='', label='Member ID',length=50),
                Field('firstname', 'string', default='', label='Reference ID',length=50),
               Field('lastname', 'string', default='', label='First',length=50),
               Field('startdate','date', label='Start Date',default=request.now,length=20),
               Field('webdob','date', label='Birth Date',default=request.now,  requires=IS_DATE(format=('%Y-%m-%d')),length=20),
               Field('email', 'string', default='',label='Email',length=50),
               Field('gender','string', default='Male',label='Gender',length=10,requires = IS_IN_SET(GENDER)),
               Field('webkey','string',default='',label='Web Key'),
               Field('address1', 'string',label='Address 1', length=50),
               Field('address2', 'string', default='',label='Address 2',length=50),
               Field('address3', 'string', default='',label='Address 2',length=50),
               Field('city', 'string', default='None',label='City',length=50,requires = IS_IN_SET(CITIES)),
               Field('st', 'string', default='None',label='State',length=50,requires = IS_IN_SET(STATES)),
               Field('pin', 'string',label='Pin',length=20),
               Field('status', 'string', label='Status',default='No_Attempt',requires = IS_IN_SET(STATUS)),
               Field('enrolldate','date', label='Web Enroll Date',default=request.now,length=20),
               Field('imported', 'boolean', default=False, label='Imported'),
               Field('company','reference company'),
               Field('provider','reference provider'),
               Field('groupregion','reference groupregion'),
               Field('hmoplan','reference hmoplan'),
               Field('is_active', 'boolean',default=True),
               auth.signature
               )
db.importdata._singular = "importdata"
db.importdata._plural   = "importdata"
  
db.define_table('vw_treatmentplancost',
                Field('primarypatient','reference patientmember'), 
                Field('totaltreatmentcost','double'),  
                Field('totalcopay','double'),  
                Field('totalinspays','double'),  
                Field('totalmemberpays','double'),  
                migrate = False
                )
db.vw_treatmentplancost._singular = "vw_treatmentplancost"
db.vw_treatmentplancost._plural   = "vw_treatmentplancost"

db.define_table('vw_primarypatientlist',
                Field('id','reference patientmember'), 
                Field('patienttype','string'),  
                Field('fname','string'),  
                Field('lname','string'),  
                
                migrate = False
                )
db.vw_primarypatientlist._singular = "vw_primarypatientlist"
db.vw_primarypatientlist._plural   = "vw_primarypatientlist"

db.define_table('vw_imagememberlist',
                Field('patientid','integer'), 
                Field('primarypatientid','integer'), 
                Field('providerid','reference provider'), 
                Field('patientmember','string'),  
                Field('patienttype','string'),  
                Field('fname','string'),  
                Field('lname','string'),  
                Field('cell','string'),  
                Field('email','string'),  
                Field('is_active','boolean'),  
                migrate = False
                )
db.vw_imagememberlist._singular = "vw_imagememberlist"
db.vw_imagememberlist._plural   = "vw_imagememberlist"

db.define_table('vw_patientmemberbirthday',
                Field('patientmember','string'),  
                Field('groupref','string'),  
                Field('fname','string'),  
                Field('lname','string'),  
                Field('cell','string'),  
                Field('email','string'),  
                Field('dob','date'),
                Field('birthday','date'),
                Field('gender','string'),
                Field('hmopatientmember','boolean'),  
                Field('is_active','boolean'),  
                Field('lastreminder','date'),
                Field('providername','string'),  
                Field('provider','integer'),  
                Field('company','integer'),  
                migrate = False
                )
db.vw_patientmemberbirthday._singular = "vw_patientmemberbirthday"
db.vw_patientmemberbirthday._plural   = "vw_patientmemberbirthday"


db.define_table('vw_appointmentreminders',
                Field('title','string'),  
                Field('starttime','date'),  
                Field('endtime','date'),  
                Field('startdate','date'),  
                Field('enddate','date'),  
                Field('place','string'),  
                Field('providername','string'),  
                Field('patientmember','string'),  
                Field('groupref','string'),  
                Field('fname','string'),  
                Field('lname','string'),  
                Field('cell','string'),  
                Field('email','string'),  
                Field('hmopatientmember','boolean'),  
                Field('activeappt','boolean'),  
                Field('provider','integer'),
                Field('patient','integer'),
                Field('lastreminder','date'),
                migrate = False
                )
db.vw_appointmentreminders._singular = "vw_appointmentreminders"
db.vw_appointmentreminders._plural   = "vw_appointmentreminders"

def geocode2(form):
    from gluon.tools import geocode
    lo,la= geocode(form.vars.f_location+' USA')
    form.vars.f_latitude=la
    form.vars.f_longitude=lo






#db.provider.update_or_insert(provider=' ', providername=' ', is_active=False)
#db.groupregion.update_or_insert(groupregion=' ', region=' ', is_active=False)
#db.agent.update_or_insert(agent=' ', name=' ', is_active=False)
#db.hmoplan.update_or_insert(hmoplancode=' ', name=' ', is_active=False)


#db.monthly.update_or_insert(premmonth=1)
#db.monthly.update_or_insert(premmonth=2)
#db.monthly.update_or_insert(premmonth=3)
#db.monthly.update_or_insert(premmonth=4)
#db.monthly.update_or_insert(premmonth=5)
#db.monthly.update_or_insert(premmonth=6)
#db.monthly.update_or_insert(premmonth=7)
#db.monthly.update_or_insert(premmonth=8)
#db.monthly.update_or_insert(premmonth=9)
#db.monthly.update_or_insert(premmonth=10)
#db.monthly.update_or_insert(premmonth=11)
#db.monthly.update_or_insert(premmonth=12)

db.webmember.fname.requires = IS_NOT_EMPTY()
db.webmember.lname.requires = IS_NOT_EMPTY()
db.webmember.address1.requires = IS_NOT_EMPTY()
db.webmember.address2.requires = IS_NOT_EMPTY()
#db.webmember.city.requires = IS_NOT_EMPTY()
db.webmember.pin.requires = IS_NOT_EMPTY()
db.webmember.cell.requires = IS_NOT_EMPTY()
db.webmember.email.requires = IS_NOT_EMPTY()
db.webmember.email.requires = IS_EMAIL(error_message = 'Invalid Email')



db.webmemberdependants.fname.requires = IS_NOT_EMPTY()
db.webmemberdependants.lname.requires = IS_NOT_EMPTY()

db.provider.providername.requires = IS_NOT_EMPTY()
db.provider.address1.requires = IS_NOT_EMPTY()
db.provider.address2.requires = IS_NOT_EMPTY()

db.provider.pin.requires = IS_NOT_EMPTY()
db.provider.cell.requires = IS_NOT_EMPTY()
db.provider.email.requires = IS_NOT_EMPTY()

db.patientmember.fname.requires = IS_NOT_EMPTY()
db.patientmember.lname.requires = IS_NOT_EMPTY()
db.patientmember.address1.requires = IS_NOT_EMPTY()
db.patientmember.address2.requires = IS_NOT_EMPTY()
db.patientmember.pin.requires = IS_NOT_EMPTY()
db.patientmember.cell.requires = IS_NOT_EMPTY()
db.patientmember.email.requires = IS_NOT_EMPTY()
db.patientmember.email.requires = IS_EMAIL(error_message = 'Invalid Email')
