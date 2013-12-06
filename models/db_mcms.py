# coding: utf8

#auth.wiki(resolve=False)

auth.settings.create_user_groups = None


extras={'code_cpp':lambda text: CODE(text,language='cpp').xml(),
        'code_java':lambda text: CODE(text,language='java').xml(),
        'code_python':lambda text: CODE(text,language='python').xml(),
        'code_html':lambda text: CODE(text,language='html').xml()}



def recortatexto(texto=None,limite=24):
    if not isinstance(texto, str): return texto
    return texto[:limite]+'(...)' if len(texto)>limite else texto

from uuid import uuid4

dt = db.define_table

dt('mcms_page',
   Field('mcms_uuid', default=str(uuid4()),
         readable=False, writable=False),
   Field('mcms_title', label='Título',
         requires=IS_NOT_IN_DB(db,'mcms_page.mcms_title')),
   Field('mcms_slug', 
         compute=lambda r: IS_SLUG.urlify(r.mcms_title)),
   Field('mcms_excerpt', 'string', length=140,
         label='Extracto'),
   Field('mcms_render', 'integer', readable=False,
         label='Interpretación',
         requires=IS_IN_SET([(1,'markmin'),(2,'html')]), default=1),
   Field('mcms_body', 'text', label='Cuerpo'),
   Field('mcms_html', compute=lambda r: MARKMIN(r.mcms_body, extra=extras) if r.mcms_render == 1 else XML(r.mcms_body, sanitize=True),
         readable=False),
   auth.signature,
   format=lambda r: '%s (%s)' % (r.mcms_title, 'markmin' if r.mcms_render == 1 else 'html')
)

db.mcms_page._enable_record_versioning()

dt('mcms_tag',
   Field('mcms_page', 'reference mcms_page'),
   Field('page_tag', 'list:string')
)

dt('mcms_media',
   Field('mcms_page_id', 'reference mcms_page'),
   Field('mcms_name'),
   Field('mcms_file', 'upload'),
   auth.signature,
)
