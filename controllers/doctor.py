from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)




#import sys
#sys.path.append('modules')
from applications.my_pms2.modules import common
from applications.my_pms2.modules import status
from applications.my_pms2.modules import states
from applications.my_pms2.modules import gender
from applications.my_pms2.modules import cycle

from cycle import WEEKDAYS
from cycle import AMS
from cycle import PMS




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def delete_role():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Roles"    
    
    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]
    
    roleid = int(common.getid(request.vars.roleid))

    returnurl = URL('doctor', 'list_roles')
    
    form = FORM.confirm('Yes',{'No': returnurl})
    
    if form.accepted:
        db(db.role_default.id == roleid).update(is_active = False)  
	session.flash = "Role deleted!"
        redirect(returnurl)
        
    return dict(form=form,username=username, formheader=formheader,returnurl=returnurl,providerid=providerid,providername=providername,page=0)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_roles():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Roles"
    
    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]

     
    query = ((db.role_default.is_active == True ))
    fields=(db.role_default.role,db.role_default.id)
    db.role_default.id.readable = False    

    
    headers = {\
        'role_default.role' : 'Role'
        
    }
    
    links = [\
        dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),_href=URL("doctor","update_role",vars=dict(roleid=row.id))))),
        dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),_href=URL("doctor","delete_role",vars=dict(roleid=row.id)))))
        ]
    
    orderby = (db.role_default.role)
        
    exportlist =dict( csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,csv=False,xml=False)    

    returnurl=URL('default','index')
    
   
    
    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            paginate=10,
                            orderby=orderby,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            searchable=False,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            user_signature=False
                           )    

    return dict(form=form,page=0,username=username, formheader=formheader,returnurl=returnurl,providerid=providerid,providername=providername)




@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def new_role():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "New Role"    
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    returnurl = URL('doctor', 'list_roles')
    page = 0
    
    db.role_default.is_active.default = True
    
    
    crud.settings.create_next = URL('doctor','list_roles')
    
    formA = crud.create(db.role_default,message="New Role added!")  
    
    xrole =  formA.element('input',_id='role_default_role')
    xrole['_class'] = 'form-control'
    
    return dict(formA=formA, username=username, formheader=formheader, returnurl=returnurl,page=page,providerid=providerid,providername=providername)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def delete_speciality():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Delete Speciality"    
    
    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]
    
    specialityid = int(common.getid(request.vars.specialityid))

    returnurl = URL('doctor', 'list_specialities')
    
    form = FORM.confirm('Yes',{'No': returnurl})
    
    if form.accepted:
        db(db.speciality_default.id == specialityid).update(is_active = False)
	session.flash = "Speciality deleted!"
        redirect(returnurl)
        
    return dict(form=form,username=username, formheader=formheader, returnurl=returnurl,providerid=providerid,providername=providername,page=0)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def list_specialities():

    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Specialities"
    
    providerdict = common.getprovider(auth, db)
    providerid = providerdict["providerid"]
    providername = providerdict["providername"]

     
    query = ((db.speciality_default.is_active == True))
    fields = (db.speciality_default.speciality,db.speciality_default.id)
    db.speciality_default.id.readable = False 

    
    headers = {\
        'speciality_default.speciality' : 'Speciality'
        
    }
    
    links = [\
        dict(header=CENTER('Edit'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/edit.png",_width=30, _height=30),_href=URL("doctor","update_speciality",vars=dict(specialityid=row.id))))),
        dict(header=CENTER('Delete'),body=lambda row: CENTER(A(IMG(_src="/my_pms2/static/img/delete.png",_width=30, _height=30),_href=URL("doctor","delete_speciality",vars=dict(specialityid=row.id)))))
        ]
    
    orderby = (db.speciality_default.speciality)
        
    exportlist = dict( csv=False,csv_with_hidden_cols=False,  html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)    

    returnurl = URL('admin', 'providerhome')
    
   
    
    form = SQLFORM.grid(query=query,
                            headers=headers,
                            fields=fields,
                            links=links,
                            maxtextlengths={'speciality_default.speciality':128},
                            paginate=10,
                            orderby=orderby,
                            exportclasses=exportlist,
                            links_in_grid=True,
                            searchable=False,
                            create=False,
                            deletable=False,
                            editable=False,
                            details=False,
                            user_signature=True
                           )    

    return dict(form=form,page=0,username=username, formheader=formheader,returnurl=returnurl,providerid=providerid,providername=providername)

@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def new_speciality():
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Specialities"
    
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    returnurl = URL('doctor', 'list_specialities')
    page = 0
    
    db.speciality_default.is_active.default = True
    
    crud.settings.create_next = URL('doctor','list_specialities')
    
    formA = crud.create(db.speciality_default,message="New Speciality added!")  
    
    xspeciality =  formA.element('input',_id='speciality_default_speciality')
    xspeciality['_class'] = 'form-control'
    
    return dict(formA=formA, username=username, formheader=formheader,returnurl=returnurl,page=page,providerid=providerid,providername=providername)





@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def update_role():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Update Role"    
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    roleid = int(common.getid(request.vars.roleid))
    
    returnurl = URL('doctor', 'list_roles')
    page = 0
    
    
    
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = returnurl
    
    
    
    formA = crud.update(db.role_default, roleid,cast=int, message="Role information updated!")  ## company Details entry form
    
    xrole =  formA.element('input',_id='role_default_role')
    xrole['_class'] = 'form-control'
    
    
    return dict(formA=formA, username=username,formheader=formheader,returnurl=returnurl,page=page,providerid=providerid,providername=providername)


@auth.requires(auth.has_membership('provider') or auth.has_membership('webadmin')) 
@auth.requires_login()
def update_speciality():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    formheader = "Update Speciality"   
    
    provdict = common.getprovider(auth,db)
    providerid = common.getid(provdict["providerid"])
    providername = common.getstring(provdict["providername"])
    
    specialityid = int(common.getid(request.vars.specialityid))
    
    returnurl = URL('doctor', 'list_specialities')
    page = 0
    
    db.speciality_default.is_active.default = True
   
    
    crud.settings.keepvalues = True
    crud.settings.showid = True
    crud.settings.update_next = returnurl
    
    
    
    formA = crud.update(db.speciality_default, specialityid,cast=int, message="Speciality information updated!")  ## company Details entry form
    
    xspeciality =  formA.element('input',_id='speciality_default_speciality')
    xspeciality['_class'] = 'form-control'
    
    
    return dict(formA=formA, username=username,formheader=formheader,returnurl=returnurl,page=page,providerid=providerid,providername=providername)


