# -*- coding: utf-8 -*-


@auth.requires_login()
def preview():

    title = request.vars.mcms_title
    excerpt = request.vars.mcms_excerpt
    page = request.vars.mcms_body
    render = request.vars.mcms_render


    header = DIV(H1(title.title(), _class='center'),
                 TAG.p(excerpt), _class='hero-unit')

    if render == '1':
        rendered_page = MARKMIN(page)
    elif render == '2':
        rendered_page = XML(page, sanitize=True)

    response.flash = 'Previsualizando edición. Cambios sin guardar.'

    return DIV(header,rendered_page)



def index():
    '''
    Recibe como request.args(0) el slug de algún artículo.
    Alternativamente, recibe el slug precedido por un '?'.
    Si el artícuo no existe, permite crearlo.
    '''
    r = request.vars.keys()

    dataset = None
    page = None
    if request.args(0) or r:
        page = LOAD(f='view.load', args=request.args(0) or r, ajax=True)
    else:
            
        if auth.is_logged_in():
            query = (db.mcms_page.id>0)
        else:
            query = (db.mcms_page.mcms_public == True)

        dataset = db(query).select(orderby=~db.mcms_page.created_on)

    return locals()


def search():
    return dict(form=FORM(
        INPUT(_id='keyword',_name='keyword', _class='search-query',
              _placeholder='Buscar Artículo', _type='text',
              _onkeyup="ajax('%s', ['keyword'], 'search-result');" \
               % URL(f='callback.load'),
              _tabindex=0),
        _class='navbar-search pull-left'),
                search_result=DIV(_id='search-result', 
                                  _class='pull-left'))


def callback():
    if not request.vars.keyword: return ''
    keyword = request.vars.keyword
    query = db.mcms_page.mcms_slug.startswith(keyword)
    pages = db(query).select(orderby=db.mcms_page.mcms_title,
                             cacheable=True)

    links = [A(p.mcms_title, _href=URL('index.html',args=p.mcms_slug)) 
             for p in pages] or [A(STRONG('Crear Artículo: '),
                                   keyword, _href=URL(f='new.html', 
                                                      vars={'title':keyword}))]
    return UL(*links, _tabindex=1)


@auth.requires_login()
def edit():

    page_id = request.args(0)

    page = db.mcms_page(page_id) or redirect(URL(f='index'))
        
    form = SQLFORM(db.mcms_page, 
                   page_id, 
                   showid=False,
                   deletable=True,
    )


    form[0][-1][1].append(XML('''<a href="#preview" class='btn btn-primary' 
    onclick='ajax("%s", ["mcms_title","mcms_excerpt","mcms_body","mcms_render"],"preview");'>
    Previsualizar</a>''' % URL(f='preview',vars=request.vars)))
    
    if form.process().accepted:

        slug = IS_SLUG.urlify(form.vars.mcms_title)
        
        redirect(URL(f='index',args=slug))
    
    return locals()

@auth.requires_login()
def new():

    db.mcms_page.mcms_title.default = request.vars.title

    form = SQLFORM(db.mcms_page)

    
    form[0][-1][1].append(XML('''<a href="#preview" class='btn btn-primary' 
    onclick='ajax("%s", ["mcms_title","mcms_excerpt","mcms_body","mcms_render"],"preview");'>
    Previsualizar</a>''' % URL(f='preview',vars=request.vars)))


    if form.process().accepted:

        slug = IS_SLUG.urlify(form.vars.mcms_title)

        redirect(URL(f='index',args=slug))
        
    return {'form':form}



def view():
    '''
    Permite VER las páginas ofreciendo una vista (vista.html) especial
    para el usuario anónimo y otra (vista.load) para el usuario
    autenticado.
    '''

    page = request.args(0)

    if page.isdigit():
        query = (db.mcms_page.id == int(page))
    else:
        page_slug = IS_SLUG.urlify(page)
        query = (db.mcms_page.mcms_slug == page_slug)

    dataset = db(query
             ).select(db.mcms_page.ALL, cacheable=True)

    if not dataset: 
        redirect(URL(f='new.html',vars={'title':str(page)}),
                 client_side=True)

    if not auth.is_logged_in() and not dataset.first()['mcms_page.mcms_public']: 
        raise HTTP(404)

    tags = db((query)& (db.mcms_page.id == db.mcms_tag.mcms_page)
          ).select(db.mcms_tag.page_tag)

    title = dataset.first()['mcms_page.mcms_title']
    excerpt = dataset.first()['mcms_page.mcms_excerpt']
    slug = dataset.first()['mcms_page.mcms_slug']
    id = dataset.first()['mcms_page.id']
    response.title = title
    
    return locals()


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
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
