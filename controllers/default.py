# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def check(form):
    try:
        # Convert input strings to keys
        key1 = CoolProp.CoolProp.get_parameter_index(input_longname_to_key[form.vars.name1])
        key2 = CoolProp.CoolProp.get_parameter_index(input_longname_to_key[form.vars.name2])
        # Try to get the pair
        CoolProp.CoolProp.generate_update_pair(key1, float(form.vars.value1), key2, float(form.vars.value2))
    except RuntimeError:
        form.errors.name1 = "These inputs do not form a valid pair"
        form.errors.name2 = "These inputs do not form a valid pair"

possible_inputs = [('Density (mass)[kg/m^3]', 'Dmass'),
                   ('Pressure [Pa]', 'P'),
                   ('Temperature [K]', 'T'),
                   ('Enthalpy [J/kg]', 'Hmass'),
                   ('Entropy [J/kg/K]', 'Smass'),
                   ('Internal Energy [J/kg]', 'Umass'),
                   ('Vapor Quality [kg/kg]', 'Q')
                   ]
input_long_strings, input_key_strings = zip(*possible_inputs)
input_longname_to_key = {l: k for l, k in possible_inputs}
input_key_to_longname = {k: l for l, k in possible_inputs}

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt, mpld3
import CoolProp
fluids = sorted(CoolProp.__fluids__)

def index():
    """
    """
    form=FORM(TABLE(TR("Fluid",SELECT(*fluids,_name="fluid",value="Ammonia", requires=IS_IN_SET(fluids))),
                    TR("Input #1",SELECT(*input_long_strings,_name="name1",value="Pressure [Pa]", requires=IS_IN_SET(input_long_strings))),
                    TR("Value #1",INPUT(_type="text",_name="value1",_value = "101325", requires=IS_FLOAT_IN_RANGE())),
                    TR("Input #2",SELECT(*input_long_strings,_name="name2",value="Temperature [K]", requires=IS_IN_SET(input_long_strings))),
                    TR("Value #2",INPUT(_type="text",_name="value2",_value = "298", requires=IS_FLOAT_IN_RANGE())),
                    TR("",INPUT(_type="submit",_value="SUBMIT"))
                    ))
    if form.process(onvalidation=check).accepted:
        response.flash = "success"
        return redirect(URL(r=request, f='next',vars=request.vars))

    return dict(form = form)

def next():
    """
    """
    fluid = request.vars.fluid

    # Create the state
    HEOS = CoolProp.AbstractState("HEOS", fluid)
    # Convert input strings to keys
    key1 = CoolProp.CoolProp.get_parameter_index(input_longname_to_key[request.vars.name1])
    key2 = CoolProp.CoolProp.get_parameter_index(input_longname_to_key[request.vars.name2])
    # Update it using the input pair that was selected
    # Upstream the input pair will be checked to make sure it is valid, so when it gets here there should not be a problem
    HEOS.update(*CoolProp.CoolProp.generate_update_pair(key1, float(request.vars.value1), key2, float(request.vars.value2)))

    form=TABLE(TR("Temperature [K]",HEOS.T()),
               TR("Pressure [Pa]",HEOS.p()),
               TR("Mass Density [kg/m3]",HEOS.rhomass()),
               TR("Molar Density [mol/m3]",HEOS.rhomolar()),
               TR("Molar specific heat [J/mol/K]",HEOS.cpmolar())
               )

    T = np.linspace(CoolProp.CoolProp.PropsSI(fluid,"Ttriple")+0.1, CoolProp.CoolProp.PropsSI(fluid,"Tcrit")-0.1)
    p = CoolProp.CoolProp.PropsSI("P","T",T,"Q",[0]*len(T),fluid)
    fig, ax = plt.subplots()
    ax.plot(T, p, 'k-', lw = 2)
    ax.set_xlabel('Temperature [K]')
    ax.set_ylabel('Pressure [Pa]')
    ax.set_yscale('log')
    fig_html = XML(mpld3.fig_to_html(fig, no_extras=True, template_type = 'simple'))
    plt.close('all')
    return dict(form = form, fig = fig_html, fluid = fluid)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
