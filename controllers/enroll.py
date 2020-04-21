# this file is released under public domain and you can use without limitations
from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)

from gluon.tools import Mail

#import sys
#sys.path.append('modules')
from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import mail
#from gluon.contrib import common
#from gluon.contrib import mail


def new_user(email, username, passw,key):    
    users = db(db.auth_user.email==email).select()
    if users:
        return int(common.getid(users[0].id))
    else:
        my_crypt = CRYPT(key=auth.settings.hmac_key)
        crypt_pass = my_crypt(passw)[0]        
        id_user= db.auth_user.insert(
                                   email = email,
                                   sitekey = key,
                                   username = username,
                                   password = crypt_pass 
                                   )
        return id_user


    
def member_showerror():

    if(len(request.args)>0):
        errorheader = request.args[0]
        errormssg   = request.args[1]
        returnURL   = URL(request.args[3],request.args[4],request.args[5])
    else:
        errorheader = "Unknown"
        errormssg   = "Unknown"
        returnURL   = URL('enroll','member_home')
    
    return dict(errorheader=errorheader,errormssg=errormssg,returnURL=returnURL,buttontext='Return')


@auth.requires_membership('member')
@auth.requires_login()
def member_home():
    
    if(auth.is_logged_in()):
        username = common.getstring(auth.user.username)
    else:
        raise HTTP(400, "Error: User not logged - member_home") 
    
    rows = db((db.webmember.webkey == auth.user.sitekey) & (db.webmember.email == auth.user.email)).select()
    if(len(rows)>0):
        webmemberid = int(common.getid(rows[0].id))
    else:
        redirect(URL('enroll','member_showerror'))    

    returnurl = URL('enroll','member_home')
    return dict(username=username, returnurl=returnurl,webmemberid=webmemberid)


def member_verify(form):
    sitekey = form.vars.sitekey
    email   = form.vars.email

    #check whether company exists
    rows = db((db.company.groupkey == sitekey) & (db.company.is_active == True)).select()
    if(len(rows) == 0):
        redirect(URL('enroll','member_register_error', args=['companynotregistered'])) #IB 05292016
    else:
        #check whether company-hmoplan rate defiend
        rows1 = db((db.companyhmoplanrate.company == int(rows[0].id)) & (db.companyhmoplanrate.is_active == True)).select()
        if(len(rows1) == 0):
            redirect(URL('enroll','member_register_error', args=['planrateerror'])) #IB 05292016

def member_register_error():
    if(len(request.args)>0):
        return dict(error = request.args[0])
    else:
        return dict(error = "registrationerror")

def member_register_success():
    ret = True
    
    if(request.vars["ret"] == "True"):
        ret = True
    else:
        ret = False

    email = request.vars["email"]

    return dict(ret=ret, email=email)


def member_register():
    
    sitekey = ''
    
    if(len(request.vars)>0):
        sitekey = request.vars["promocode"]
        
    form = SQLFORM.factory(
            Field('email', 'string', label='Email',requires=[IS_EMAIL(),IS_NOT_IN_DB(db, 'auth_user.email')]),
            Field('sitekey', 'string', default=sitekey, label='Promotion Code',requires=IS_NOT_EMPTY()),
            Field('username', 'string',  label='User Name',requires=IS_NOT_EMPTY()),
            Field('password', 'password',  label='Password',requires=[IS_NOT_EMPTY(),CRYPT(key=auth.settings.hmac_key)]),
            Field('confirm', 'password',  label='Confirm', requires=IS_EXPR('value==%s' % repr(request.vars.get('password', None)),
             error_message='passwords do not match')),             
        )    
    
    submit = form.element('input',_type='submit')
    submit['_style'] = 'display:none;'
    
    if form.process(onvalidation=member_verify).accepted:
        sitekey = form.vars.sitekey
        email   = form.vars.email
        
        user_id = new_user(form.vars.email,form.vars.username,form.vars.password.password,form.vars.sitekey)
        if(user_id <= 0):
            redirect(URL('enroll','member_register_error'))

        
        # Setting Group Membership
        group_id = int(common.getid(auth.id_group(role="member")))

        if(group_id == 0):
            group_id = auth.add_group('member', 'Member')
        elif(group_id > 0):
            auth.add_membership(group_id, user_id)
        elif(group_id < 0):
            raise HTTP(400,"Error: Creating Member Group:register()")
        
        db((db.auth_user.sitekey==sitekey) & (db.auth_user.email == email)).update(registration_key = '')
      
      
        # create new member
        rows = db(db.company.groupkey == sitekey).select()
        companyid = int(common.getid(rows[0].id))
        hmoplanid = int(common.getid(rows[0].hmoplan))
        companycode = common.getstring(rows[0].company)
        webid = db.webmember.insert(email=email,webkey=sitekey,status='No_Attempt',webenrolldate = datetime.date.today(),company=companyid,provider=1,hmoplan=hmoplanid,imported=True)
        db(db.webmember.id == webid).update(webmember = companycode + str(webid))
        
        ret = mail.emailEnrollLoginDetails(db,request,sitekey,email)
       
        redirect(URL('enroll','member_register_success', vars=dict(ret=ret,email=email)))
        
    elif form.errors:
        response.flash = 'form has errors'     
    
    username = None
    returnurl = URL('enroll','member_register')
    return dict(username=username, form=form, returnurl=returnurl)


def member_login():
    
    form = SQLFORM.factory(
                Field('username', 'string',  label='User Name',requires=IS_NOT_EMPTY()),
                Field('password', 'password',  label='Password',requires=[IS_NOT_EMPTY(),CRYPT(key=auth.settings.hmac_key)])
        )
    if form.process().accepted:
        user = auth.login_bare(form.vars.username, form.vars.password.password)
        if(user==False):
            redirect(URL('enroll','member_showerror'))
        else:
            rows = db((db.webmember.webkey == auth.user.sitekey) & (db.webmember.email == auth.user.email)).select()
            if(len(rows)>0):
                webmemberid = int(common.getid(rows[0].id))
                db((db.webmember.id == webmemberid) & (db.webmember.status == 'No_Attempt') & (db.webmember.is_active==True)).update(status = 'Attempting')
                redirect(URL('enroll', 'member_update_profile', vars=dict(webmemberid = webmemberid)))  
            else:
                redirect(URL('enroll','member_showerror'))
            

            
    return dict(formlogin=form)

def member_resetpassword():
    props = db(db.urlproperties.id>0).select()

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

    mail = auth.settings.mailer
    mail.settings.server = server
    mail.settings.sender = sender
    mail.settings.login =  login
    mail.settings.tls = tls

    auth.settings.reset_password_next = URL( 'enroll','member_login')
    auth.settings.request_reset_password_next = URL('enroll','member_login')
    form = auth.request_reset_password()
    return dict(form=form)

@auth.requires_login()
def member_logout():
    """ Logout handler """
    auth.settings.logout_next = URL('enroll','member_login')
    auth.logout()
    return dict()



@auth.requires_membership('member')
@auth.requires_login()
def member_update_profile():
    
    if(len(request.vars)<=0):
        raise HTTP(403,"Error: No Member Profile to Update : update_member_profile()_1")

    if(auth.is_logged_in()):
        username = common.getstring(auth.user.username)
    else:
        raise HTTP(400, "Error: User not logged - update_webmember_profile()_2")    

    returnurl = URL('enroll','member_home')    
    
    webmemberid = int(common.getid(request.vars['webmemberid']))
    if(webmemberid == 0):
        raise HTTP(403,"Error: No Member Profile to Update : update_member_profile()_3")
    webmembers= db((db.webmember.id == webmemberid) & (db.webmember.is_active == True)).select(db.webmember.ALL, db.company.name, db.hmoplan.name,\
                left=[db.company.on(db.company.id==db.webmember.company),db.hmoplan.on(db.hmoplan.id==db.webmember.hmoplan)])
    if(len(webmembers) != 1):
        raise HTTP(403,"Error: No Member Profile to Update : update_member_profile()_4")
    
    
    formA = SQLFORM.factory(
        Field('webmember', 'string',label='Member ID', default=common.getstring(webmembers[0].webmember.webmember),writable=False, readable=True),
        Field('webkey', 'string',label='Promo Code', default=common.getstring(webmembers[0].webmember.webkey), writable=False,readable=True),
        Field('company', 'string', default=common.getstring(webmembers[0].company.name), writable=False,readable=True),
        Field('hmoplan', 'string', default=common.getstring(webmembers[0].hmoplan.name), writable=False,readable=True),
        Field('groupref', 'string',label='Employee ID', default=common.getstring(webmembers[0].webmember.groupref)),
        Field('fname', 'string',label='First Name', default=common.getstring(webmembers[0].webmember.fname), writable=False,readable=True, requires=IS_NOT_EMPTY()),
        Field('mname', 'string',label='Middle Name', default=common.getstring(webmembers[0].webmember.mname), writable=False,readable=True),
        Field('lname', 'string',label='Last Name', default=common.getstring(webmembers[0].webmember.lname), writable=False,readable=True, requires=IS_NOT_EMPTY()),
        Field('groupregion', default=common.getid(webmembers[0].webmember.groupregion), requires=IS_IN_DB(db, 'groupregion.id', '%(groupregion)s')),
        Field('gender', 'string',label='Gender', default='Male', requires = IS_IN_SET(GENDER)),
        Field('webdob', 'date',label='DOB', default=request.now,  requires=IS_DATE(format=('%d/%m/%Y')),length=20),
        )
    
    
    if formA.process().accepted:
        webmemberid = db(db.webmember.id == webmemberid).update(**db.webmember._filter_fields(formA.vars))
        redirect(URL('enroll','member_update_contact', vars=dict(webmemberid=webmemberid)))
    
    elif formA.errors:
        response.flash = 'form has errors'    
        
    return dict(username=username,returnurl=returnurl,formA=formA)