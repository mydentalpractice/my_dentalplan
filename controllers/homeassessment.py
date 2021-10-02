# -*- coding: utf-8 -*-
from gluon import current
db = current.globalenv['db']
from gluon.tools import Crud
crud = Crud(db)

import urllib2
import webbrowser


import string
import random
import json
import datetime

from applications.my_pms2.modules  import common
from applications.my_pms2.modules  import mail
from applications.my_pms2.modules  import mdpuser
from applications.my_pms2.modules  import mdpprospect
from applications.my_pms2.modules  import mdpprovider
from applications.my_pms2.modules  import mdpbank
from applications.my_pms2.modules  import logger

#this redirects to Home Assessment URL
def ha_dashboard():
    
    r = db(db.urlproperties.id > 0).select()
    haurl = r[0].hdfc_transaction_url if(len(r) == 1) else ""
    if(haurl != ""):
        webbrowser.open(haurl)
        
    return dict()
