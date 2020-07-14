from flask import current_app

def add_to_index(index, model):

""" Metodo que sirve para añadir indices a Elasticsearch.

    Args:
        index: indice que será agregado.
        model: modelo que referencia una tabla de la DB.
    """

    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def remove_from_index(index, model):

""" Metodo que sirve para eliminar indices a Elasticsearch.

    Args:
        index: indice que será eliminado.
        model: modelo que referencia una tabla de la DB.
    """

    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

def query_index(index, query, page, per_page):

""" Metodo que sirve para hacer una query, de forma paginada y con una busqueda por multicampos.

    Args:
        index: indice de la busqueda.
        query: consulta que se hará a Elasticsearch.
        page: pagina actual de la busqueda.
        per_page: cantidad de objetos que serán extraidos de la query.


    Returns:
        Una lista de Identificadores que se encuentra en la query.
        JSON - con los resulatados de las busquedas.
    """

    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        body={'query': 
                    {'multi_match': 
                            {'query': query, 'fields': ['*']}},
                            'from': (page - 1) * per_page, 'size': per_page})

    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']