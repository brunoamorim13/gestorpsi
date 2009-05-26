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

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import slugify
from gestorpsi.organization.models import PersonType, UnitType, AdministrationEnvironment, Source, ProvidedType, Management, Dependence, Activitie, Organization, ProfessionalResponsible
from gestorpsi.phone.models import PhoneType
from gestorpsi.address.models import Country, State, AddressType
from gestorpsi.internet.models import EmailType, IMNetwork
from gestorpsi.address.views import address_save
from gestorpsi.phone.views import phone_save
from gestorpsi.internet.views import email_save, site_save, im_save
from gestorpsi.util.decorators import permission_required_with_403
from gestorpsi.careprofessional.models import Profession

@permission_required_with_403('organization.organization_write')
def professional_responsible_save(request, object, ids, names, subscriptions, organization_subscriptions, professions):
    ProfessionalResponsible.objects.all().delete()
    for x in range(len(names)):
        obj = []
        obj = (ProfessionalResponsible(name=names[x], subscription=subscriptions[x], organization=object, organization_subscription=organization_subscriptions[x], profession=Profession.objects.get(pk = professions[x])) )
        if ( len(names[x]) != 0 or len(subscriptions[x]) !=0 ):
            obj.save()

@permission_required_with_403('organization.organization_read')
def form(request):
    user = request.user
    object = get_object_or_404( Organization, pk=user.get_profile().org_active.id )
    return render_to_response('organization/organization_form.html', {
        'object': object, #Organization.objects.get(pk= user.get_profile().org_active.id),
        'PhoneTypes': PhoneType.objects.all(), 
        'AddressTypes': AddressType.objects.all(), 
        'EmailTypes': EmailType.objects.all(), 
        'IMNetworks': IMNetwork.objects.all(),
        'countries': Country.objects.all(),
        'States': State.objects.all(),
        'phones': object.phones.all(),
        'addresses': object.address.all(),
        'emails': object.emails.all(),
        'websites': object.sites.all(),
        'ims': object.instantMessengers.all(),
        'PersonType': PersonType.objects.all(),
        'UnitType': UnitType.objects.all(),
        'AdministrationEnvironment': AdministrationEnvironment.objects.all(),
        'Source': Source.objects.all(),
        'ProvidedType': ProvidedType.objects.all(),
        'Management': Management.objects.all(),
        'Dependence': Dependence.objects.all(),
        'Activitie': Activitie.objects.all(),
        'professional_responsible': ProfessionalResponsible.objects.filter(organization = user.get_profile().org_active),
        'Professions': Profession.objects.all(),
        },
        context_instance=RequestContext(request))

@permission_required_with_403('organization.organization_write')
def save(request):
    user = request.user
    try:
		object = Organization.objects.get(pk= user.get_profile().org_active.id)
    except:
        object = Organization()
        object.short_name = slugify(request.POST['name'])
    
    if (object.short_name != request.POST['short_name']):
        if (Organization.objects.filter(short_name__iexact = request.POST['short_name']).count()):
	        return HttpResponse("false")
        else:
            object.short_name = request.POST['short_name']
         
    #identity
    object.name = request.POST['name']
    object.trade_name = request.POST['trade_name']
    object.register_number = request.POST['register_number']
    object.cnes = request.POST['cnes']
    object.state_inscription = request.POST['state_inscription']
    object.city_inscription = request.POST['city_inscription']
    object.photo = request.POST['photo']
    object.visible = get_visible( request, request.POST.get('visible') )
    #profile
    object.person_type = PersonType.objects.get(pk=request.POST['person_type'])
    object.unit_type = UnitType.objects.get(pk=request.POST['unit_type'])
    object.environment = AdministrationEnvironment.objects.get(pk=request.POST['environment'])
    object.management = Management.objects.get(pk=request.POST['management'])
    object.source = Source.objects.get(pk=request.POST['source'])
    object.dependence = Dependence.objects.get(pk=request.POST['dependence'])
    object.activity = Activitie.objects.get(pk=request.POST['activity'])
    """ provided types """
    object.provided_type.clear()
    for p in request.POST.getlist('provided_type'):
        object.provided_type.add(ProvidedType.objects.get(pk=p))
    # comment
    object.comment = request.POST['comment']
    object.save()
   
    professional_responsible_save(request, object, request.POST.getlist('professionalId'), request.POST.getlist('professional_name'), request.POST.getlist('professional_subscription'), request.POST.getlist('professional_organization_subscription'), request.POST.getlist('service_profession'))
            #object.subscriptions_professional_institutional = request.POST['subscriptions_professional_institutional']
            #object.professional_responsible = request.POST['professional_responsible']

    phone_save(object, request.POST.getlist('phoneId'), request.POST.getlist('area'), request.POST.getlist('phoneNumber'), request.POST.getlist('ext'), request.POST.getlist('phoneType'))
    email_save(object, request.POST.getlist('email_id'), request.POST.getlist('email_email'), request.POST.getlist('email_type'))
    site_save(object, request.POST.getlist('site_id'), request.POST.getlist('site_description'), request.POST.getlist('site_site'))
    im_save(object, request.POST.getlist('im_id'), request.POST.getlist('im_identity'), request.POST.getlist('im_network'))
    address_save(object, request.POST.getlist('addressId'), request.POST.getlist('addressPrefix'),
    request.POST.getlist('addressLine1'), request.POST.getlist('addressLine2'),
    request.POST.getlist('addressNumber'), request.POST.getlist('neighborhood'),
    request.POST.getlist('zipCode'), request.POST.getlist('addressType'),
    request.POST.getlist('city'), request.POST.getlist('foreignCountry'),
    request.POST.getlist('foreignState'), request.POST.getlist('foreignCity'))
    return HttpResponse(object.id)
    
# The question is, is available the short name?
# 0 = NO
# 1 = YES
@permission_required_with_403('organization.organization_read')
def shortname_is_available(request, short):
    if Organization.objects.filter(short_name__iexact = short).count():
	    return HttpResponse("0")
    else:
	    return HttpResponse("1")

@permission_required_with_403('organization.organization_read')
def get_visible( request, value ):
    if ( value == 'on' ):
        return True
    else:
        return False 
