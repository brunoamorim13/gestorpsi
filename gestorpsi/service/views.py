# -*- coding: utf-8 -*-

"""
Copyright (C) 2008 GestorPsi

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404
from gestorpsi.service.models import Service, ServiceForm, ResearchProject
from gestorpsi.organization.models import Agreement, AgeGroup, ProcedureProvider, Procedure
from gestorpsi.careprofessional.models import CareProfessional
from gestorpsi.organization.models import Organization
from django.core.exceptions import ObjectDoesNotExist

def index(request):
    """
    Returns a list that contains all the currently existing services.
    @param request: this is a request sent by the browser.
    @type request: an instance of the class C{HttpRequest} created by the framework Django.
    """
    user = request.user
    
    return render_to_response( "service/service_index.html", { 'object':Service.objects.filter(organization = user.org_active ), 'Agreements': Agreement.objects.all(), 'ResearchProjects': ResearchProject.objects.all(), 'CareProfessionals': CareProfessional.objects.all(), 'AgeGroups': AgeGroup.objects.all(), 'ProcedureProviders': ProcedureProvider.objects.all(), 'Procedures': Procedure.objects.all() })

def form(request, object_id= ''):
    """
    This function view uses I{forms} to show the information related to the
    C{Service} with id equals to I{object_id}
    @param request: this is a request sent by the browser.
    @type request: an instance of the class C{HttpRequest} created by the framework Django.
    @param object_id: id of the C{Service}.
    @type object_id: an instance of the built-in class I{int}.
    """
    try:
        object= get_object_or_404( Service, pk= object_id )
    except (Http404, ObjectDoesNotExist):
        object= Service()
    service_form= ServiceForm( instance= object )
    return render_to_response('service/service_form.html', {'object': object, 'service_form': service_form } )

def save_agreements( list_of_agreements, object ):
    """
    Saves the list of agreements passed as parameter and associate them with the
    instance of service passed as parameter (I{object}).
    @param list_of_agreements: list that contains the agreements which will be associated with the service.
    @type object_id: an instance of the built-in class I{list}.
    @param object: represents the id code of the service.
    @type object_id: an instance of the built-in class I{list}.
    """
    object.agreements.clear()
    object.save()
    for agreement_id in list_of_agreements:
        agreement= Agreement.objects.get( pk= agreement_id )
        object.agreements.add( agreement )
        
def save_responsibles( list_of_responsibles, object ):
    """
    Saves the list of responsibles and associates it with the object passed as parameter.
    @param list_of_responsibles: list that contains the responsibles which will be associated with the service (I{object}).
    @type object_id: an instance of the built-in class I{list}.
    @param object: represents the id code of the service.
    @type object_id: an instance of the built-in class I{list}.
    """
    object.responsibles.clear()
    object.save()
    for responsible_id in list_of_responsibles:
        responsible= CareProfessional.objects.get(pk= responsible_id )
        object.responsibles.add( responsible )

def save(request, object_id= ''):
    """
    This function view searches for the C{Service} with id equals to I{object_id}, if there is such a
    C{Service} instance, it is loaded and updated with the values of the request object, otherwise a 
    new C{Service} instance is created, filled with request's values and saved.
    """
    try:
        object= get_object_or_404( Service, pk= object_id )
    except (Http404, ObjectDoesNotExist):
        object= Service()
        user = request.user
        object.organization = user.org_active 
        
    
    object.name= request.POST['service_name']
    object.description= request.POST['service_description']
    object.keywords= request.POST['service_keywords']
    if request.POST['service_research_project']:
        object.research_project= ResearchProject.objects.get(pk= request.POST['service_research_project'])
    object.save()
    
#    if ( request.POST['organization'] != '' ):
#        organization= Organization.objects.get(pk= request.POST['organization'] )
#        object.organization= organization
    
    save_agreements( request.POST.getlist('service_agreements'), object )
    save_responsibles( request.POST.getlist('service_responsibles'), object )
     
    object.save()
    service_form= ServiceForm( instance= object )
    return HttpResponse(object.id)

def delete(request, object_id= ''):
    """
    This function view searches for a C{Service} object which has the id equals to I{object_id}, if there is
    such C{Service} instance it is deleted.
    """
    object= get_object_or_404( Service, pk= object_id )
    object.delete()
    list_of_services= Service.objects.all()
    return render_to_response( "service/service_index.html", locals() )
