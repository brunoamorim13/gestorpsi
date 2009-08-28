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

from django.core.paginator import Paginator
from django.conf import settings
from gestorpsi.address.models import City
from gestorpsi.address.views import address_save
from gestorpsi.document.views import document_save
from gestorpsi.person.models import MaritalStatus
from gestorpsi.phone.views import phone_save
from gestorpsi.internet.views import email_save, site_save, im_save
from datetime import datetime

def person_save(request, person):
    person.name= request.POST['name']
    person.nickname = request.POST['nickname']
    person.comments = request.POST.get('comments')

    if(request.POST['photo']):
        person.photo = request.POST['photo']
    else:
        person.photo = ''

    if(request.POST.get('dataNasc')):
        person.birthDate = datetime.strptime(request.POST.get('dataNasc'),'%d/%m/%Y')

    if(request.POST.get('birthDate_supposed')):
        person.birthDateSupposed = True
    else:
        person.birthDateSupposed = False

    person.gender = request.POST['gender']
    
    # maritalStatus
    try:
        if not (request.POST['maritalStatus']):
            person.maritalStatus = None
        else:
            person.maritalStatus = MaritalStatus.objects.get(pk = request.POST['maritalStatus'])
    except:
        person.maritalStatus = None

    # birthPlace (Naturality)
    person.birthForeignCity= ''
    person.birthForeignState= ''
    person.birthForeignCountry= None
    
    try:
        person.birthPlace = City.objects.get(pk = request.POST['birthPlace'])
    except:
        person.birthPlace = None
        if( request.POST['birthForeignCity']):
            person.birthForeignCity= request.POST['birthForeignCity']
        if( request.POST['birthForeignState'] ):
            person.birthForeignState= request.POST['birthForeignState']
        try:
            person.birthForeignCountry= request.POST['birthForeignCountry']
        except:
            person.birthForeignCountry= None


    person.save()    
    user = request.user
    person.organization.add(user.get_profile().org_active)

    # save phone numbers (using Phone APP)
    phone_save(person, request.POST.getlist('phoneId'), request.POST.getlist('area'), request.POST.getlist('phoneNumber'), request.POST.getlist('ext'), request.POST.getlist('phoneType'))

    # save addresses (using Address APP)
    address_save(person, request.POST.getlist('addressId'), request.POST.getlist('addressPrefix'),
                 request.POST.getlist('addressLine1'), request.POST.getlist('addressLine2'),
                 request.POST.getlist('addressNumber'), request.POST.getlist('neighborhood'),
                 request.POST.getlist('zipCode'), request.POST.getlist('addressType'),
                 request.POST.getlist('city'), request.POST.getlist('foreignCountry'),
                 request.POST.getlist('foreignState'), request.POST.getlist('foreignCity'))
    
    # save documents (using Document APP) 
    document_save(person, request.POST.getlist('documentId'), request.POST.getlist('document_typeDocument'), request.POST.getlist('document_document'), request.POST.getlist('document_issuer'), request.POST.getlist('document_state'))
    
    # save internet data
    email_save(person, request.POST.getlist('email_id'), request.POST.getlist('email_email'), request.POST.getlist('email_type'))
    site_save(person, request.POST.getlist('site_id'), request.POST.getlist('site_description'), request.POST.getlist('site_site'))
    im_save(person, request.POST.getlist('im_id'), request.POST.getlist('im_identity'), request.POST.getlist('im_network'))

    return person

def person_type_url(person):
    """ Return an URL linking to a Client, Care Professional or an Employee form """
    try:
        x = person.client
        return "/client/%s/" % x.id
    except:
        pass
        
    try:
        x = person.careprofessional
        return "/careprofessional/%s/" % x.id
    except:
        pass
        
    try:
        x = person.employee
        return "/employee/%s/" % x.id
    except:
        pass

def person_json_list(request, object, perm, page):
    object_length = len(object)
    paginator = Paginator(object, settings.PAGE_RESULTS)
    object = paginator.page(page)

    array = {} #json
    i = 0

    array['util'] = {
        'has_perm_read': request.user.has_perm(perm),
        'paginator_has_previous': object.has_previous().real,
        'paginator_has_next': object.has_next().real,
        'paginator_previous_page_number': object.previous_page_number().real,
        'paginator_next_page_number': object.next_page_number().real,
        'paginator_actual_page': object.number,
        'paginator_num_pages': paginator.num_pages,
        'object_length': object_length,
    }

    
    array['paginator'] = {}
    for p in paginator.page_range:
        array['paginator'][p] = p
    
    for c in object.object_list:
        try:
            username = c.user.username
        except:
            username = ''
        array[i] = {
            'id': c.id,
            'person_id': c.person.id,
            'name': c.person.name,
            'phone': u'%s' % c.person.get_first_phone(),
            'email': u'%s' % c.person.get_first_email(),
            'username': username,
        }
        i = i + 1

    return array
