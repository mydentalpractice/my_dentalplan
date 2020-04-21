# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################
#response.logo = A(B('My Dental Plan - HMO Management System',SPAN(),'',_style="font-size:16px;font-weight: bold; color: rgb(255, 255, 255);"),B(XML('&trade;&nbsp;'),_style="font-size:16px;font-weight: bold; color: rgb(117, 117, 117);"),
                  #_class="brand",_href="http://www.mydentalplan.in/")
response.logo = ''
response.title = '' ##request.application.replace('_',' ').title().upper()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Imtiyaz Bengali <imtiazbengali@hotmail.com>'
response.meta.keywords = 'HMO, Provider, EOB, Benefits, Insurance, Primary, Secondary, CoPay, Deductibles, Network, HIPPA'
response.meta.generator = 'myDentalPlan'

## your http://google.com/analytics id
response.google_analytics_id = None


#response.menu = [
#> >                  ('Public',  True,  URL('index')),
#> >                  ('Member Only',  False,  URL('member')),
#> >                  ]
#> > if (auth.user_id != None) and ((auth.has_membership(role = 'vip')) :
#> >     response.menu += [('VIP Only',  False,  URL('vip')), ]


#########################################################################
## this is the main application menu add/remove items as required
#########################################################################


#if ((auth.user_id != None) & (auth.has_membership(role = 'webmember'))):
        #response.menu = [
            #(T('Home'), False, URL('default', 'index'), [])
         
        #]        
        #response.menu += [('Member Enrollement',  False,  URL('member','member_enrollment')), ]
        #response.menu += [(SPAN('About',_calss='highlight'),False,URL('default','index'))]
        

#if ((auth.user_id != None) & (auth.has_membership(role = 'webadministrator'))):
        #response.menu = [
            #(T('Home'), False, URL('default', 'index'), [])
         
        #]        
        #response.menu += [
                #(SPAN('Web Enrollment'), False, URL('member', 'import_member_csv'),[
                #(T('Group Enrollment'), False, URL('member', 'import_member_csv_0')), 
                #(T('Enrollment Status'), False, URL('member', 'list_webmember_0')) 
                #])]
        #response.menu += [(SPAN('Group(Company)'), False, URL('company', 'list_company'),[
                #(T('Group(Company)'), False, URL('company', 'list_company')) 
                #])]
        
        #response.menu += [
                #(SPAN('Member'), False, URL('member', 'list_member'),[
                #(T('Member List'), False, URL('member', 'list_member'))
                #])]
        #response.menu += [(SPAN('About',_calss='highlight'),False,URL('default','index'))]
        


if ((auth.user_id != None) & (auth.has_membership(role = 'webadmin'))):
    response.menu = [
        (T('Home'), False, URL('default', 'index'), [])
     
    ]       
         
    response.menu += [
            (SPAN('Web Enrollment'), False, URL('',''),[
            (T('Group Enrollment'), False, URL('member', 'import_member_csv_0')), 
            (T('Enrollment Status'), False, URL('member', 'list_webmember')),
            (T('New Member'), False, URL('member', 'new_webmember')) 
            ])]
        
    response.menu += [(SPAN('Group(Company)'), False, URL('company', 'list_company'),[
            (T('Group(Company)'), False, URL('company', 'list_company')) 
            ])]
    
    response.menu += [
            (SPAN('Member'), False, URL('member', 'list_member'),[
            (T('Member List'), False, URL('member', 'list_member'))
            ])]
    
    response.menu += [
            (SPAN('Provider'), False, URL('provider', 'list_provider'),[
            (T('Provider'), False, URL('provider', 'list_provider')),
            (T('Import Provider'), False, URL('provider', 'import_provider')),
            
            ])]
    
    response.menu += [
            (SPAN('Plan'), False,URL('plan', 'list_plan'),[
            (T('Plan'), False, URL('plan', 'list_plan'))
            ])]
    
    response.menu += [
            (SPAN('Agent'), False, URL('agent', 'list_agent'),[
            (T('Agent '), False, URL('agent', 'list_agent'))
            ])]
    
    
    response.menu += [
        (SPAN('Procedure'), False,URL('procedure', 'list_procedure'),[
            (T('Procedure'), False, URL('procedure', 'list_procedure')),
            (T('Import Procedure'), False, URL('procedure', 'import_procedure')),
        ])]
    
    response.menu += [
            (SPAN('Region'), False,URL('company', 'list_groupregion'),[
            (T('Region'), False, URL('company', 'list_groupregion'))])]
    
    response.menu += [
            (SPAN('Report'), False,URL('', ''),[
            (T('Provider Capitation'), False, URL('report', 'providercapitationreportparam')),
            #(T('Agent Commission'), False, URL('report', 'agentcommissionreportparam')),
            (T('Enrollment Status Report'), False, URL('report', 'enrollmentstatusreportparams')),
            (T('Enrollment Report'), False, URL('report', 'enrollmentreportparam')),
            (T('Assigned Members'), False, URL('report', 'assignedmembersreportparam')),
            (T('Payment Transaction Report'), False, URL('report', 'paymenttxlogreportparams')),
            (T('Member Report'), False, URL('report', 'memberreportparams'))
            #(T('Member Enrollment Report'), False, URL('report', 'memberenrollmentreportparam'))
            ])]
    
    
    response.menu += [
            (SPAN('About',_calss='highlight'), False,URL('', ''),[
            (T('My Dental Plan'), False, URL('default', 'index')),            
            (T('Properties'), False, URL('default', 'urlproperties'))
            ])]
    
    response.menu += [
            (SPAN('Test',_calss='highlight'), False,URL('', ''),[
            (T('Test1'), False, URL('default', 'create_test1')),            
            (T('Test2'), False, URL('default', 'create_test2')),
            (T('TestEmail'), False, URL('default', 'testemail1')),
            (T('Process Renewal'), False, URL('policyrenewal', 'process_renewals')),
            (T('List Renewal'), False, URL('policyrenewal', 'list_renewals'))
            ])]
    




DEVELOPMENT_MENU = False

#########################################################################
## provide shortcuts for development. remove in production
##########################################################################

#def _():
    ## shortcuts
    #app = request.application
    #ctr = request.controller
    ## useful links to internal and external resources

#if DEVELOPMENT_MENU: _()
