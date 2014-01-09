# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('NIM',SPAN('.IO')), _class="brand")
response.title = 'NIMIO Technologies Chile %s' % request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'NIMIO TECHNOLOGIES <contacto@nim.io>'
response.meta.description = 'Repositorio de información'
response.meta.keywords = ','.join(str(request.args(0) or request.title or request.application).split('-'))
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    ('Portada', False, URL('default', 'index'), []),
]


if auth.is_logged_in():
    response.menu.insert(0,(STRONG('Crear Página'), True, URL('default','new', []))),
    response.menu.insert(1,('Media', False, URL('media','index'), []))
