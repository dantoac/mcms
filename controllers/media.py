# -*- coding: utf-8 -*-

@auth.requires_login()
def index():
    '''
    Devuelve un grid para adjuntar archivos
    '''

    form = SQLFORM.grid(db.mcms_media, user_signature=False)

    return {'form':form}
