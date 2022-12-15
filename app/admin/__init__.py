from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    make_response,
)
from sqlalchemy import select

from app.database import session
from app.models import (
    Collection,
    Person,
    NamedArea,
)

admin = Blueprint('admin', __name__)

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    #response.headers.add('Content-Range: bytes 200-20/200')
    #response.headers["Content-Range"] = "bytes %d-%d/%d" % (
    #            0, 20 - 1, 200)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@admin.route('/')
def index():
    return render_template('admin.html', name='foo')

@admin.route('/api/collections')
def get_collection_list():
    data = {
        'header': (
            ('pk', '#', {'align':'right'}),
            ('collector__full_name', '採集者', {'align': 'right'}),
            ('display_field_number', '採集號', {'align': 'right', 'type': 'x_field_number'}),
            ('collect_date', '採集日期', {'align': 'right'}),
        ),
        'rows': [],
        'model': 'collection',
    }
    #result = session.execute(select(Collection))
    #print (result.all())
    rows = Collection.query.all()
    for r in rows:
        data['rows'].append(r.to_dict())
    #for r in result.all():s
    #print (r[0].collect_date, r[0].collector_id, r[0].collector.full_name)
    #d = {
    #        'collect_date': r[0].collect_date,
    #        'collector': r[0].collector.full_name
    #    }
    #data.append(zd)


    #return jsonify(data)
    return _corsify_actual_response(jsonify(data['rows']))


@admin.route('/api/person')
def get_person_list():
    data = {
        'header': (
            ('pk', '#', {'align':'right'}),
            ('full_name', '全名', {'align': 'right'}),
            ('other_name', '英文名', {'align': 'right'}),
            ('is_collector', '採集者', {'align': 'right', 'type': 'radio'}),
            ('is_identifier', '鑒定者', {'align': 'right', 'type': 'radio'}),
        ),
        'rows': [],
        'model': 'person',
    }
    #result = session.execute(select(Collection))
    #print (result.all())
    rows = Person.query.all()
    for r in rows:
        data['rows'].append(r.todict())

    return jsonify(data)

@admin.route('/api/collection/<int:collection_id>/form')
def get_collection_form(collection_id):
    '''for frontend to render <form>'''
    col = session.get(Collection, collection_id)
    #print(col.todict())

    result = Person.query.filter(Person.is_collector==True).all()
    collector_list = [{'id': x.id, 'label': f'{x.full_name} ({x.other_name})'} for x in result]
    res_na_1 = NamedArea.query.filter(NamedArea.area_class_id==1).all()
    na_1 = [{'id': x.id, 'label': f'{x.display_name}'} for x in res_na_1]
    res_na_2 = NamedArea.query.filter(NamedArea.area_class_id==2).all()
    na_2 = [{'id': x.id, 'label': f'{x.display_name}'} for x in res_na_2]
    res_na_3 = NamedArea.query.filter(NamedArea.area_class_id==3).all()
    na_3 = [{'id': x.id, 'label': f'{x.display_name}'} for x in res_na_3]
    res_na_4 = NamedArea.query.filter(NamedArea.area_class_id==4).all()
    na_4 = [{'id': x.id, 'label': f'{x.display_name}'} for x in res_na_4]
    res_na_5 = NamedArea.query.filter(NamedArea.area_class_id==5).all()
    na_5 = [{'id': x.id, 'label': f'{x.display_name}'} for x in res_na_5]
    res_na_6 = NamedArea.query.filter(NamedArea.area_class_id==6).all()
    na_6 = [{'id': x.id, 'label': f'{x.display_name}'} for x in res_na_6]
    field_number = ''
    if fns := col.field_numbers:
        field_number = fns[0].todict().get('value', '')
    data = {
        'form': (
            (('collector_id', '採集者', 'x_collector', col.collector_id, {'options': collector_list}),
             ('field_number', '採集號', 'text', field_number)),
            (('collect_date', '採集日期', 'text', col.collect_date),),
            (('companion', '隨同人員', 'text', ''),),
            (('taxon', '物種', 'text', ''),),
            (('named_area_country', '國家', 'select', '', {'options': na_1}),),
            (('named_area_province', '省分', 'select', '', {'options': na_2}),),
            (('named_area_hsien', '縣市', 'select', '', {'options': na_3}),),
            (('named_area_town', '鄉鎮', 'select', '', {'options': na_4}),),
            (('named_area_park', '國家公園', 'select', '', {'options': na_5}),),
            (('named_area_locality', '地名', 'select', '', {'options': na_6}),),
            (('locality_text', '地點描述', 'text', '',),),
            (('latitude', '緯度', 'text', '',),
             ('longitude', '經度', 'text', '',),),
            (('altitude', '海拔', 'text', ''),
             ('altitude2', '海拔2', 'text', '',)),
            (('field_number', '採集號', 'text', field_number),),
            (('units', '標本', 'x_units', [x.todict() for x in col.units]),),
        ),
        'value': {
            'collector_id': col.collector_id,
        },
    }


    return jsonify(data)

@admin.route('/api/collection/<int:collection_id>/edit')
def post_collection(collection_id):
    #return redirect('')
    pass
