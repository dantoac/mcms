# -*- coding: utf-8 -*-

@auth.requires_login()
def index():
    '''
    Recibe como request.args(0) el slug de algún artículo.
    Alternativamente, recibe el slug precedido por un '?'.
    Si el artícuo no existe, permite crearlo.
    '''
    r = request.vars.keys()
    portada = LOAD(f='view.load', args=request.args(0) or r, ajax=True)
    return locals()


def search():
    return dict(form=FORM(
        INPUT(_id='keyword',_name='keyword', _class='search-query',
              _placeholder='Buscar Artículo', _type='text',
              _onkeyup="ajax('%s', ['keyword'], 'search-result');" \
               % URL(f='callback.load')),
        _class='navbar-search pull-left'),
                search_result=DIV(_id='search-result', 
                                  _class='pull-left'))


def callback():
    if not request.vars.keyword: return ''
    keyword = request.vars.keyword
    query = db.mcms_page.mcms_slug.contains(keyword)
    pages = db(query).select(orderby=db.mcms_page.mcms_title,
                             cacheable=True)
    links = [A(p.mcms_title, _href=URL('index.html',args=p.mcms_slug)) for p in pages] or [A(STRONG('Crear Artículo: '),keyword, callback=URL(f='new', vars={'title':keyword}), target='page')]
    return UL(*links)



@auth.requires_login()
def edit():

    page_id = request.args(0)

    page = db.mcms_page(page_id) or redirect(URL(f='index'))
        
    form = SQLFORM(db.mcms_page, 
                   page_id, 
                   showid=False,
                   deletable=True,
    )
    
    if form.process().accepted:

        slug = IS_SLUG.urlify(form.vars.mcms_title)
        
        redirect(URL(f='view',args=slug))
    
    return locals()

@auth.requires_login()
def new():

    db.mcms_page.mcms_title.default = request.vars.title

    form = SQLFORM(db.mcms_page)

    if form.process().accepted:

        slug = IS_SLUG.urlify(form.vars.mcms_title)

        redirect(URL(f='index',args=slug))
        
    return {'form':form}


@auth.requires_login()
def view():
    page_title = request.args(0) or 'portada'

    page_slug = IS_SLUG.urlify(page_title)

    dataset = db((db.mcms_page.mcms_slug == page_slug)
             ).select(db.mcms_page.ALL)

    if not dataset: 
        redirect(URL(f='new.html',vars={'title':str(page_title)}),
                 client_side=True)


    tags = db((db.mcms_page.mcms_slug == page_slug)
              & (db.mcms_page.id == db.mcms_tag.mcms_page)
              ).select(db.mcms_tag.page_tag)

    title = dataset.first()['mcms_page.mcms_title']
    excerpt = dataset.first()['mcms_page.mcms_excerpt']

    response.title = title
    
    return locals()

@auth.requires_login()
def admin(): return {'menu':UL([A(t, _href=URL(args=t)) for t in db.tables]),'admin':SQLFORM.smartgrid(db[request.args(0) or 'auth_user'], user_signature=False)}


def markmindocs():
    return IFRAME(_src="http://www.web2py.com/examples/static/markmin.html",
                  _class="row-fluid well well-large", _height="450px")


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
