from gluon import current
db = current.globalenv['db']

from gluon.tools import Crud
crud = Crud(db)

from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import gender

def list_dentalcasesheet():
    
    username = auth.user.first_name + ' ' + auth.user.last_name
  
    page = common.getgridpage(request.vars)
    
    # grid
    query = ((db.dentalcasesheet.is_active==True))
    
    
   
    fields=(db.dentalcasesheet.id, \
               db.dentalcasesheet.child_name, db.dentalcasesheet.parent_name,db.dentalcasesheet.school_name,db.dentalcasesheet.admission_number,db.dentalcasesheet.cell, db.dentalcasesheet.email)
    
    headers={
          'dentalcasesheet.school_name':'School',
          'dentalcasesheet.admission_number':'Admission',          
          'dentalcasesheet.child_name':'Child Name',
          'dentalcasesheet.parent_name':'Parent Name',
          'dentalcasesheet.cell':'Cell',
          'dentalcasesheet.oemail':'Email',
         
      }    

    
    exportlist = dict( csv_with_hidden_cols=False, html=False,tsv_with_hidden_cols=False, tsv=False, json=False,xml=False)
	
    links = [\
             lambda row: A('Dental Case Sheet',_href=URL("dentalcasesheet","view_dentalcasesheet",vars=dict(dcsid=row.id,page=page)))]

    orderby = (db.dentalcasesheet.school_name)

    formA = SQLFORM.grid(query=query,
                        headers=headers,
                        fields=fields,
                        links=links,
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

    
    
  
   
    returnurl = URL('default','index')
    formheader = "Dental Case Sheet List"
    return dict(formA=formA,username=username,formheader=formheader,returnurl=returnurl,page=page)


def view_dentalcasesheet():
    
    page = int(request.vars.page)
    
    username = auth.user.first_name + ' ' + auth.user.last_name
    
    formheader = "Dental Case Sheet Details"    
    
    dcsid = int(common.getid(request.vars.dcsid)) if(request.vars.dcsid != "") else 0
    
    dcs = db((db.dentalcasesheet.id == dcsid) & (db.dentalcasesheet.is_active == True)).select()
    
   
    
    formA = SQLFORM.factory(\
           Field('child_name', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'), \
                 default=dcs[0].child_name),
           Field('parent_name', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'), default=dcs[0].parent_name),
           Field('school_name', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'), default=dcs[0].school_name),
           Field('admission_number', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'), default=dcs[0].admission_number),
           Field('child_class', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'), default=dcs[0].child_class),
           Field('cell', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'), default=dcs[0].cell,length=13),
           Field('email', 'string',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'), default=dcs[0].email),
           Field('xgender','string',  widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control'),\
                 default=dcs[0].gender,label='Gender'),
           Field('dob','date', label='DOB',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'),\
                 default=dcs[0].dob,requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
           Field('cavity_milk_teeth', 'boolean',default=common.getboolean(dcs[0].cavity_milk_teeth)),
           Field('cavity_perm_teeth', 'boolean',default=common.getboolean(dcs[0].cavity_perm_teeth)),
           Field('crooked_teeth', 'boolean',default=common.getboolean(dcs[0].crooked_teeth)),
           Field('gum_problems', 'boolean',default=common.getboolean(dcs[0].gum_problems)),
           Field('fluoride_check', 'boolean',default=common.getboolean(dcs[0].fluoride_check)),
           Field('emergency_consult', 'boolean',default=common.getboolean(dcs[0].emergency_consult)),
           Field('priority_checkup', 'boolean',default=common.getboolean(dcs[0].priority_checkup)),
           Field('routine_checkup', 'boolean',default=common.getboolean(dcs[0].routine_checkup)),
           Field('casereport','text', default=dcs[0].casereport),
           Field('created_on','date', label='DOB',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'),\
                 default=dcs[0].created_on,requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
           Field('modified_on','date', label='DOB',widget = lambda field, value:SQLFORM.widgets.string.widget(field, value,_class='form-control  date'),\
                 default=dcs[0].modified_on,requires=IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y')))),
           
           
           
           
    )
    
    xcsr = formA.element('textarea[name=casereport]')
    xcsr['_style'] = 'height:100px;line-height:1.0'
    xcsr['_class'] = 'form-control'
    xcsr['_rows'] = 5
    xcsr['_readonly'] = 'true'

    child_name = formA.element('input',_id='no_table_child_name')
    child_name['_readonly'] = 'true'
    
    parent_name = formA.element('input',_id='no_table_parent_name')
    parent_name['_readonly'] = 'true'
    
    admission_number = formA.element('input',_id='no_table_admission_number')
    admission_number['_readonly'] = 'true'
    
    
    child_class = formA.element('input',_id='no_table_child_class')
    child_class['_readonly'] = 'true'
    
    school_name = formA.element('input',_id='no_table_school_name')
    school_name['_readonly'] = 'true'
    
    xgender = formA.element('input',_id='no_table_xgender')
    xgender['_readonly'] = 'true'
  

    
    email = formA.element('input',_id='no_table_email')
    email['_readonly'] = 'true'
    
    dob = formA.element('input',_id='no_table_dob')
    dob['_readonly'] = 'true'

    created_on = formA.element('input',_id='no_table_created_on')
    created_on['_readonly'] = 'true'

    modified_on = formA.element('input',_id='no_table_modified_on')
    modified_on['_readonly'] = 'true'


    xcell = formA.element('input',_id='no_table_cell')
    xcell['_readonly'] = 'true'
    xcell['_onkeypress'] = "phoneno()"
    xcell['_maxlength'] = "10"

    cmt = formA.element('input',_id='no_table_cavity_milk_teeth')	  
    cmt['_disabled'] = 'true'

    cpt = formA.element('input',_id='no_table_cavity_perm_teeth')	  
    cpt['_readonly'] = 'true'

    ckt = formA.element('input',_id='no_table_crooked_teeth')	  
    ckt['_readonly'] = 'true'
    
    gum = formA.element('input',_id='no_table_gum_problems')	  
    gum['_readonly'] = 'true'

    flchk = formA.element('input',_id='no_table_fluoride_check')	  
    flchk['_readonly'] = 'true'
    
    emg = formA.element('input',_id='no_table_emergency_consult')	  
    emg['_disabled'] = 'true'
    
    prc = formA.element('input',_id='no_table_priority_checkup')	  
    prc['_disabled'] = 'true'

    rch = formA.element('input',_id='no_table_routine_checkup')	  
    rch['_disabled'] = 'true'

    returnurl=URL('dentalcasesheet','list_dentalcasesheet',vars=dict(page=page))

    return dict(formA=formA, username=username,returnurl=returnurl,formheader=formheader,page=page)
