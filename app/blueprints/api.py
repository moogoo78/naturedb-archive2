import json
import time
import re
import logging

from flask import (
    Blueprint,
    request,
    abort,
    jsonify,
)
from flask.views import MethodView
from sqlalchemy import (
    select,
    func,
    text,
    desc,
    cast,
    between,
    Integer,
    LargeBinary,
    extract,
    or_,
    inspect,
    join,
)
from app.database import session

from app.models.collection import (
    Entity,
    Person,
    NamedArea,
    AreaClass,
    Unit,
    Identification,
    Person,
    AssertionTypeOption,
    Collection,
    #LogEntry,
    #get_structed_list,
)
from app.models.taxon import (
    Taxon,
    TaxonRelation,
)
from app.models.site import (
    Favorite,
)

api = Blueprint('api', __name__)

def make_query_response(query):
    start_time = time.time()

    rows = [x.to_dict() for x in query.all()]
    end_time = time.time()
    elapsed = end_time - start_time

    result = {
        'data': rows,
        'total': len(rows),
        'query': str(query),
        'elapsed': elapsed,
    }
    # print(result, flush=True)
    return result

def record_filter(stmt, payload):
    filtr = payload['filter']
    if value := filtr.get('collection'):
        if c := Collection.query.filter(Collection.name==value).scalar():
            stmt = stmt.where(Entity.collection_id==c.id)
    if catalog_number := filtr.get('catalog_number'):
        cn_list = [catalog_number]

        if catalog_number2 := filtr.get('catalog_number2'):
            # TODO validate
            cn_int1 = int(catalog_number)
            cn_int2 = int(calatog_number2)
            cn_list = [str(x) for x in range(cn_int1, cn_int2+1)]
            if len(cn_list) > 1000:
                cn_list = [] # TODO flash

        stmt = stmt.where(Unit.catalog_number.in_(cn_list))
    if value := filtr.get('collector'):
        stmt = stmt.where(Entity.collector_id==value[0])
    if value := filtr.get('field_number'):
        if value2 := filtr.get('field_number2'):
            # TODO validate
            int1 = int(value)
            int2 = int(value2)
            fn_list = [str(x) for x in range(int1, int2+1)]
            if len(fn_list) > 1000:
                fn_list = [] # TODO flash

            many_or = or_()
            for x in fn_list:
                many_or = or_(many_or, Entity.field_number.ilike(f'{x}%'))
            stmt = stmt.where(many_or)
        else:
            stmt = stmt.where(Entity.field_number.ilike('%{}%'.format(value)))
    if value := filtr.get('field_number_range'):
        if '-' in value:
            start, end = value.split('-')
            fn_list = [str(x) for x in range(int(start), int(end)+1)]
            if len(fn_list) > 1000:
                fn_list = [] # TODO flash

            many_or = or_()
            for x in fn_list:
                many_or = or_(many_or, Entity.field_number == x)
            stmt = stmt.where(many_or)
        else:
            stmt = stmt.where(Entity.field_number.ilike('%{}%'.format(value)))
    if value := filtr.get('collect_date'):
        if value2 := filtr.get('collect_date2'):
            stmt = stmt.where(Entity.collect_date>=value, Entity.collect_date<=value2)
        else:
            stmt = stmt.where(Entity.collect_date==value)
    if value := filtr.get('collect_month'):
        stmt = stmt.where(extract('month', Entity.collect_date) == value)
    # if scientific_name := filtr.get('scientific_name'): # TODO variable name
    #     if t := session.get(Taxon, scientific_name[0]):
    #         taxa_ids = [x.id for x in t.get_children()]
    #         stmt = stmt.where(Collection.proxy_taxon_id.in_(taxa_ids))
    # if taxa := filtr.get('species'):
    #     if t := session.get(Taxon, taxa[0]):
    #         taxa_ids = [x.id for x in t.get_children()]
    #         stmt = stmt.where(Collection.proxy_taxon_id.in_(taxa_ids))
    #         query_key_map['taxon'] = t.to_dict()
    # elif taxa := filtr.get('genus'):
    #     if t := session.get(Taxon, taxa[0]):
    #         taxa_ids = [x.id for x in t.get_children()]
    #         stmt = stmt.where(Collection.proxy_taxon_id.in_(taxa_ids))
    #         query_key_map['taxon'] = t.to_dict()
    # elif taxa := filtr.get('family'):
    #     if t := session.get(Taxon, taxa[0]):
    #         taxa_ids = [x.id for x in t.get_children()]
    #         stmt = stmt.where(Collection.proxy_taxon_id.in_(taxa_ids))
    #         query_key_map['taxon'] = t.to_dict()
    elif taxa_ids := filtr.get('taxon'):
        if t := session.get(Taxon, taxa_ids[0]):
            taxa_ids = [x.id for x in t.get_children()]
            stmt = stmt.where(Entity.proxy_taxon_id.in_(taxa_ids))
    elif taxa_names := filtr.get('taxon_name'):
        taxa_name = taxa_names[0]
        stmt = stmt.where(Entity.proxy_taxon_text.ilike(f'%{taxa_name}%'))

    if value := filtr.get('locality_text'):
        stmt = stmt.where(Entity.locality_text.ilike(f'%{value}%'))
    if value := filtr.get(''):
        stmt = stmt.where(Entity.named_areas.any(id=value[0]))
    if value := filtr.get('named_area'):
        stmt = stmt.where(Entity.named_areas.any(id=value[0]))
    if value := filtr.get('country'):
        stmt = stmt.where(Entity.named_areas.any(id=value[0]))
    if value := filtr.get('stateProvince'):
        stmt = stmt.where(Entity.named_areas.any(id=value[0]))
        print(stmt, flush=True)
    if value := filtr.get('county'):
        stmt = stmt.where(Entity.named_areas.any(id=value[0]))
    if value := filtr.get('locality'):
        stmt = stmt.where(Entity.named_areas.any(id=value[0]))
    if value := filtr.get('national_park'):
        stmt = stmt.where(Entity.named_areas.any(id=value[0]))
    if value := filtr.get('locality_text'):
        stmt = stmt.where(Entity.locality_text.ilike(f'%{value}%'))
    if value := filtr.get('altitude'):
        value2 = filtr.get('altitude2')
        if cond := filtr.get('altitude_condiction'):
            if cond == 'eq':
                stmt = stmt.where(Entity.altitude==value)
            elif cond == 'gte':
                stmt = stmt.where(Entity.altitude>=value)
            elif cond == 'lte':
                stmt = stmt.where(Entity.altitude<=value)
            elif cond == 'between' and value2:
                stmt = stmt.where(Entity.altitude>=value, Entity.altitude2<=value2)
        else:
            stmt = stmt.where(Entity.altitude==value)

    if value := filtr.get('type_status'):
        stmt = stmt.where(Unit.type_status==value)
    if q := filtr.get('q'):
        term, value = q.split(':')
        if term == 'taxon_name':
            stmt = stmt.where(Entity.proxy_taxon_scientific_name.ilike(f'%{value}%') | Entity.proxy_taxon_common_name.ilike(f'%{value}%'))
        elif term in ['taxon_family_name', 'taxon_genus_name', 'taxon_species_name']:
            rank = term.split('_')[1]
            stmt_taxa = select(Taxon).where(Taxon.rank==rank).where(Taxon.full_scientific_name.ilike(f'%{value}%') | Taxon.common_name.ilike(f'%{value}%'))
            result = session.execute(stmt_taxa)
            ids = []
            for t in result.all():
                ids += [t[0].id] + [x.id for x in t[0].get_children()]

            if len(ids):
                stmt = stmt.where(Entity.proxy_taxon_id.in_(ids))
            else:
                stmt = stmt.where(False)
        elif term == 'collector_name':
            stmt_p = select(Person.id).where(Person.full_name.ilike(f'%{value}%') | Person.full_name_en.ilike(f'%{value}%'))
            result = session.execute(stmt_p)
            ids = []
            for p in result.all():
                ids.append(p[0])
            if len(ids):
                stmt = stmt.where(Entity.collector_id.in_(ids))
            else:
                stmt = stmt.where(False)
        elif term == 'field_number':
            stmt = stmt.where(Entity.field_number.ilike(f'%{value}%'))
        elif term == 'collect_date':
            stmt = stmt.where(Entity.collect_date==value)
        elif term == 'collect_date_month':
            stmt = stmt.where(extract('month', Entity.collect_date) == value)
        elif term == 'collect_date_month':
            stmt = stmt.where(extract('month', Entity.collect_date) == value)
        elif 'named_areas_' in term:
            na_list = term.split('_')
            na_name = '_'.join(na_list[2:])
            if ac := AreaClass.query.filter(AreaClass.name==na_name).first():
                stmt_na = select(NamedArea.id).where(NamedArea.name.ilike(f'%{value}%') | NamedArea.name_en.ilike(f'%{value}%')).where(NamedArea.area_class==ac)
                result = session.execute(stmt_na)
                many_or = or_()
                ids = [x[0] for x in result.all()]
                if len(ids):
                    for id_ in ids:
                        many_or = or_(many_or, Entity.named_areas.any(id=id_))
                        stmt = stmt.where(many_or)
                else:
                    stmt = stmt.where(False)

        elif term == 'altitude':
            if '-' in value:
                alt_range = value.split('-')
                stmt = stmt.where(Entity.altitude >= alt_range[0], Entity.altitude2 <= alt_range[1] )
            else:
                stmt = stmt.where(Entity.altitude == value)
        elif term == 'catalog_number':
            stmt = stmt.where(Unit.catalog_number.ilike(f'%{value}%'))


    return stmt

def allow_cors_preflight():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def allow_cors(data):
    resp = jsonify(data)
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp


@api.route('/collections/<int:collection_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def collection_item(collection_id):
    obj = session.get(Collection, collection_id)
    if not obj:
        return abort(404)

    if request.method == 'GET':
        data = obj.to_dict()
        return allow_cors({
            'data': data,
            'form': obj.get_form_layout()
        })

    elif request.method == 'OPTIONS':
        return allow_cors_preflight()

    elif request.method == 'PUT':
        changes = obj.update_from_json(request.json)
        log = LogEntry(
            model='Collection',
            item_id=collection_id,
            action='update',
            changes=changes)
        session.add(log)
        session.commit()

        return allow_cors(obj.to_dict())
    elif request.method == 'DELETE':
        session.delete(obj)
        session.commit()
        log = LogEntry(
            model='Collection',
            item_id=item.id,
            action='delete')
        session.add(log)
        session.commit()
        return allow_cors({})



@api.route('/searchbar', methods=['GET'])
def get_searchbar():
    '''for searchbar
    '''
    q = request.args.get('q')
    data = []
    if q.isdigit():
        # Field Number (with Collector)
        rows = Entity.query.filter(Entity.field_number.ilike(f'{q}%')).limit(10).all()
        for r in rows:
            item = {
                'field_number': r.field_number or '',
                'collector': r.collector.to_dict(with_meta=True) if r.collector else {},
            }
            item['meta'] = {
                'term': 'field_number_with_collector',
                'label': '採集號',
                'display': '{} {}'.format(r.collector.display_name if r.collector else '', r.field_number),
                'seperate': {
                    'field_number': {
                        'term': 'field_number',
                        'label': '採集號',
                        'display': r.field_number,
                    },
                },
            }
            data.append(item)

        # calalogNumber
        rows = Unit.query.filter(Unit.accession_number.ilike(f'{q}%')).limit(10).all()
        for r in rows:
            #unit = r.to_dict()
            unit = {
                'value': r.catalog_number or '',
            }
            unit['meta'] = {
                'term': 'catalog_number',
                'label': '館號',
                'display': r.catalog_number
            }
            data.append(unit)
    elif '-' in q:
        # TODO
        m = re.search(r'([0-9]+)-([0-9]+)', q)
        if m:
            data.append({
                'field_number_range': q,
                'term': 'field_number_range',
            })
    else:
        # Collector
        rows = Person.query.filter(Person.full_name.ilike(f'%{q}%') | Person.atomized_name['en']['given_name'].astext.ilike(f'%{q}%') | Person.atomized_name['en']['inherited_name'].astext.ilike(f'%{q}%')).limit(10).all()
        for r in rows:
            collector = r.to_dict(with_meta=True)
            data.append(collector)

        # Taxon
        rows = Taxon.query.filter(Taxon.full_scientific_name.ilike(f'{q}%') | Taxon.common_name.ilike(f'%{q}%')).limit(10).all()
        for r in rows:
            taxon = r.to_dict(with_meta=True)
            data.append(taxon)

        # Location
        rows = NamedArea.query.filter(NamedArea.name.ilike(f'{q}%') | NamedArea.name_en.ilike(f'%{q}%')).limit(10).all()
        for r in rows:
            loc = r.to_dict(with_meta=True)
            data.append(loc)

    resp = jsonify({
        'data': data,
    })
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.headers.add('Access-Control-Allow-Methods', '*')
    return resp


@api.route('/explore', methods=['GET'])
def get_explore():
    view = request.args.get('view', '')
    # group by collection
    #stmt = select(Collection, func.array_agg(Unit.id), func.array_agg(Unit.accession_number)).select_from(Unit).join(Collection, full=True).group_by(Collection.id) #where(Unit.id>40, Unit.id<50)
    # TODO: full outer join cause slow
    #stmt = select(Collection, func.array_agg(Unit.id), func.array_agg(Unit.accession_number)).select_from(Collection).join(Unit).group_by(Collection.id)

    # cast(func.nullif(Collection.field_number, 0), Integer)
    #unit_collection_join = join(Unit, Collection, Unit.collection_id==Collection.id)
    #collection_person_join = join(Collection, Person, Collection.collector_id==Person.id)
    #orig stmt = select(Unit.id, Unit.accession_number, Collection, Person.full_name).join(Collection, Collection.id==Unit.collection_id).join(Person, Collection.collector_id==Person.id)
    stmt = select(Unit, Entity) \
    .join(Unit, Unit.entity_id==Entity.id, isouter=True) \
    .join(Person, Entity.collector_id==Person.id)

    #res = session.execute(stmt)
    #.select_from(cp_join)
    #print(f'!!default stmt: \n{stmt}\n-----------------', flush=True)
    total = request.args.get('total', None)

    payload = {
        'filter': json.loads(request.args.get('filter')) if request.args.get('filter') else {},
        'sort': json.loads(request.args.get('sort')) if request.args.get('sort') else {},
        'range': json.loads(request.args.get('range')) if request.args.get('range') else [0, 20],
    }
    # query_key_map = {}
    # print(payload, flush=True)
    stmt = record_filter(stmt, payload)
    # logging.debug(stmt)

    base_stmt = stmt
    # print(payload['filter'], flush=True)
    # sort
    if view == 'checklist':
        stmt = stmt.order_by(Entity.proxy_taxon_scientific_name)
    elif view != 'map':
        if sort := payload['sort']:
            if 'collect_date' in sort:
                stmt = stmt.order_by(Entity.collect_date)
            elif 'collect_num' in sort:
                stmt = stmt.order_by(Person.full_name, cast(Collection.field_number, LargeBinary)) # TODO ulitilize Person.sorting_name
            elif 'taxon' in sort:
                stmt = stmt.order_by(Collection.proxy_taxon_scientific_name)
            elif 'created' in sort:
                stmt = stmt.order_by(Collection.created)
        else:
            # default order
            stmt = stmt.order_by(Person.full_name, cast(Entity.field_number, LargeBinary)) # TODO ulitilize Person.sorting_name
        #print(stmt, flush=True)

    # limit & offset
    if view != 'checklist':
        start = int(payload['range'][0])
        end = int(payload['range'][1])
        limit = min((end-start), 1000) # TODO: max query range
        stmt = stmt.limit(limit)
        if start > 0:
            stmt = stmt.offset(start)

    # group by
    #if view == 'checklist':
    #    stmt = stmt.group_by(Collection.proxy_taxon_id)

    # =======
    # results
    # =======
    begin_time = time.time()
    result = session.execute(stmt)
    elapsed = time.time() - begin_time

    # -----------
    # count total
    # -----------
    elapsed_count = None
    if total is None:
        begin_time = time.time()
        subquery = base_stmt.subquery()
        count_stmt = select(func.count()).select_from(subquery)
        total = session.execute(count_stmt).scalar()
        elapsed_count = time.time() - begin_time

    # --------------
    # result mapping
    # --------------
    data = []
    begin_time = time.time()
    elapsed_mapping = None

    rank_list = [{}, {}, {}] # family, genus, species
    rank_map = {'family': 0, 'genus': 1, 'species': 2}
    is_truncated = False
    TRUNCATE_LIMIT = 2000
    if view == 'checklist' and total > TRUNCATE_LIMIT: #  TODO
        is_truncated = True

    rows = result.all()
    if is_truncated is True:
        rows = rows[0:TRUNCATE_LIMIT] # TODO

    for r in rows:
        unit = r[0]
        if me := r[1]:
            t = None
            if taxon_id := me.proxy_taxon_id:
                t = session.get(Taxon, taxon_id)

            if view == 'map':
                if me.longitude_decimal and me.latitude_decimal:
                    data.append({
                        'catalog_number': unit.catalog_number or '',
                        'collector': me.collector.to_dict() if me.collector else '',
                        'field_number': me.field_number,
                        'collect_date': me.collect_date.strftime('%Y-%m-%d') if me.collect_date else '',
                        'taxon': f'{me.proxy_taxon_scientific_name} ({me.proxy_taxon_common_name})',
                        'longitude_decimal': me.longitude_decimal,
                        'latitude_decimal': me.latitude_decimal,
                    })
            elif view == 'checklist':
                if me.proxy_taxon_id:
                    # taxon = session.get(Taxon, me.proxy_taxon_id)
                    # parents = taxon.get_parents()
                    tr_list = TaxonRelation.query.filter(TaxonRelation.child_id==me.proxy_taxon_id).order_by(TaxonRelation.depth).all()
                    tlist = [r.parent for r in tr_list]
                    for index, t in enumerate(tlist):
                        map_idx = rank_map[t.rank]
                        parent_id = 0
                        if index < len(tlist) - 1:
                            parent_id = tlist[index+1].id
                        if t.id not in rank_list[map_idx]:
                            rank_list[map_idx][t.id] = {
                                'obj': t.to_dict(),
                                'parent_id': parent_id,
                                'count': 1,
                                'children': [],
                            }
                        else:
                            rank_list[map_idx][t.id]['count'] += 1
            else:
                image_url = ''
                try:
                    catalog_number_int = int(unit.catalog_number)
                    instance_id = f'{catalog_number_int:06}'
                    first_3 = instance_id[0:3]
                    image_url = f'https://brmas-pub.s3-ap-northeast-1.amazonaws.com/hast/{first_3}/S_{instance_id}_s.jpg'
                except:
                    pass

                data.append({
                    'unit_id': unit.id if unit else '',
                    'collection_id': me.id,
                    'record_key': f'u{unit.id}' if unit else f'c{me.id}',
                    # 'accession_number': unit.accession_number if unit else '',
                    'catalog_number': unit.catalog_number if unit else '',
                    'image_url': image_url,
                    'field_number': me.field_number,
                    'collector': me.collector.to_dict() if me.collector else '',
                    'collect_date': me.collect_date.strftime('%Y-%m-%d') if me.collect_date else '',
                    'taxon_text': f'{me.proxy_taxon_scientific_name} ({me.proxy_taxon_common_name})',
                    'taxon': t.to_dict() if t else {},
                    'named_areas': [x.to_dict() for x in me.named_areas],
                    'locality_text': me.locality_text,
                    'altitude': me.altitude,
                    'altitude2': me.altitude2,
                    'longitude_decimal': me.longitude_decimal,
                    'latitude_decimal': me.latitude_decimal,
                    'type_status': unit.type_status if unit and unit.type_status else '',
                })

    elapsed_mapping = time.time() - begin_time

    # update data while view = checklist
    if view == 'checklist':
        flat_list = []
        tree = {'id':0, 'children':[]}
        taxon_list = {
            0: tree,
        }
        # sort
        for rank_dict in rank_list:
            for _, node in rank_dict.items():
                flat_list.append(node)

        # make tree
        for x in flat_list:
            taxon_list[x['obj']['id']] = x
            taxon_list[x['parent_id']]['children'].append(taxon_list[x['obj']['id']])

        data = tree['children']

    resp = jsonify({
        'data': data,
        # 'key_map': query_key_map,
        'is_truncated': is_truncated,
        'total': total,
        'elapsed': elapsed,
        'elapsed_count': elapsed_count,
        'elapsed_mapping': elapsed_mapping,
        'debug': {
            'query': str(stmt),
            'payload': payload,
        }
    })
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.headers.add('Access-Control-Allow-Methods', '*')
    return resp


@api.route('/collections', methods=['GET', 'POST', 'OPTIONS'])
def collection():
    if request.method == 'GET':
        # group by collection
        #stmt = select(Collection, func.array_agg(Unit.id), func.array_agg(Unit.accession_number)).select_from(Unit).join(Collection, full=True).group_by(Collection.id) #where(Unit.id>40, Unit.id<50)
        # TODO: full outer join cause slow
        #stmt = select(Collection, func.array_agg(Unit.id), func.array_agg(Unit.accession_number)).select_from(Collection).join(Unit).group_by(Collection.id)

        # stmt = select(Collection)
        stmt = select(Unit.id, Unit.accession_number, Collection, Person.full_name) \
            .join(Unit, Unit.collection_id==Collection.id, isouter=True) \
            .join(Person, Collection.collector_id==Person.id)

        total = request.args.get('total', None)
        payload = {
            'filter': json.loads(request.args.get('filter')) if request.args.get('filter') else {},
            'sort': json.loads(request.args.get('sort')) if request.args.get('sort') else {},
            'range': json.loads(request.args.get('range')) if request.args.get('range') else [0, 20],
        }

        base_stmt = record_filter(stmt, payload)

        # =======
        # results
        # =======
        begin_time = time.time()
        result = session.execute(stmt)
        elapsed = time.time() - begin_time

        # -----------
        # count total
        # -----------
        elapsed_count = None
        if total is None:
            begin_time = time.time()
            subquery = base_stmt.subquery()
            count_stmt = select(func.count()).select_from(subquery)
            total = session.execute(count_stmt).scalar()
            elapsed_count = time.time() - begin_time

        # --------------
        # result mapping
        # --------------
        data = []
        begin_time = time.time()
        elapsed_mapping = None

        rows = result.all()
        for r in rows:
            if c := r[2]:
                units = []
                for u in c.units:
                    unit = {
                        'id': u.id,
                        'accession_number': u.accession_number,
                    }
                    image_url = ''
                    # TODO
                    try:
                        accession_number_int = int(u.accession_number)
                        instance_id = f'{accession_number_int:06}'
                        first_3 = instance_id[0:3]
                        image_url = f'https://brmas-pub.s3-ap-northeast-1.amazonaws.com/hast/{first_3}/S_{instance_id}_s.jpg'
                    except:
                        pass

                    if image_url:
                        unit['image_url'] = image_url

                    units.append(unit)

                data.append({
                    'id': c.id,
                    'field_number': c.field_number,
                    'collector': c.collector.to_dict() if c.collector else '',
                    'collect_date': c.collect_date.strftime('%Y-%m-%d') if c.collect_date else '',
                    'taxon': c.proxy_taxon_text,
                    'units': units,
                    'named_areas': [x.to_dict() for x in c.named_areas],
                })
            else:
                print(r, flush=True)
        elapsed_mapping = time.time() - begin_time

        resp = jsonify({
            'data': data,
            'total': total,
            'elapsed': elapsed,
            'elapsed_count': elapsed_count,
            'elapsed_mapping': elapsed_mapping,
            'debug': {
                'query': str(stmt),
                'payload': payload,
            }
        })
        resp.headers.add('Access-Control-Allow-Origin', '*')
        resp.headers.add('Access-Control-Allow-Methods', '*')
        return resp

    elif request.method == 'OPTIONS':
        return allow_cors_preflight()

    elif request.method == 'POST':
        collection = Collection()
        changes = collection.update_from_json(request.json)
        session.add(collection)
        session.commit()
        log = LogEntry(
            model='Collection',
            item_id=collection.id,
            action='insert',
            changes=changes)
        session.add(log)
        session.commit()

        return allow_cors(collection.to_dict())

@api.route('/people/<int:id>', methods=['GET'])
def get_person_detail(id):
    obj = session.get(Person, id)
    return jsonify(obj.to_dict(with_meta=True))

@api.route('/people', methods=['GET'])
def get_person_list():
    query = Person.query.select_from(Collection).join(Collection.people)
    if filter_str := request.args.get('filter', ''):
        filter_dict = json.loads(filter_str)
        collector_id = None
        if keyword := filter_dict.get('q', ''):
            like_key = f'{keyword}%' if len(keyword) == 1 else f'%{keyword}%'
            # query = query.filter(Person.full_name.ilike(like_key) | Person.atomized_name['en']['given_name'].astext.ilike(like_key) | Person.atomized_name['en']['inherited_name'].astext.ilike(like_key))
            query = query.filter(Person.full_name.ilike(like_key) | Person.full_name_en.ilike(like_key))
        if is_collector := filter_dict.get('is_collector', ''):
            query = query.filter(Person.is_collector==True)
        if is_identifier := filter_dict.get('is_identifier', ''):
            query = query.filter(Person.is_identifier==True)

        #if x := filter_dict.get('collector_id', ''):
        #    collector_id = x
        if x := filter_dict.get('id', ''):
            query = query.filter(Person.id.in_(x))
        if collection_id := filter_dict.get('collection_id', ''):
            query = query.filter(Collection.id==collection_id)

    return jsonify(make_query_response(query))

@api.route('/taxa/<int:id>', methods=['GET'])
def get_taxa(id):
    obj = session.get(Taxon, id)
    return jsonify(obj.to_dict(with_meta=True))

@api.route('/named_areas/<int:id>', methods=['GET'])
def get_named_area_detail(id):
    obj = session.get(NamedArea, id)
    return jsonify(obj.to_dict(with_meta=True))

@api.route('/named_areas', methods=['GET'])
def get_named_area_list():
    query = NamedArea.query

    if filter_str := request.args.get('filter', ''):
        filter_dict = json.loads(filter_str)
        if keyword := filter_dict.get('q', ''):
            like_key = f'{keyword}%' if len(keyword) == 1 else f'%{keyword}%'
            query = query.filter(NamedArea.name.ilike(like_key) | NamedArea.name_en.ilike(like_key))
        if ids := filter_dict.get('id', ''):
            query = query.filter(NamedArea.id.in_(ids))
        if area_class_id := filter_dict.get('area_class_id', ''):
            query = query.filter(NamedArea.area_class_id==area_class_id)
        if parent_id := filter_dict.get('parent_id'):
            query = query.filter(NamedArea.parent_id==parent_id)

    return jsonify(make_query_response(query))

@api.route('/assertion_type_options', methods=['GET'])
def get_assertion_type_option_list():
    query = AssertionTypeOption.query

    if filter_str := request.args.get('filter', ''):
        filter_dict = json.loads(filter_str)
        if keyword := filter_dict.get('q', ''):
            like_key = f'{keyword}%' if len(keyword) == 1 else f'%{keyword}%'
            query = query.filter(AssertionTypeOption.value.ilike(like_key))
        #if ids := filter_dict.get('id', ''):
        #    query = query.filter(AssertionTypeOption.id.in_(ids))
        if type_id := filter_dict.get('type_id', ''):
            query = query.filter(AssertionTypeOption.assertion_type_id==type_id)

    return jsonify(make_query_response(query))

@api.route('/taxa', methods=['GET'])
def get_taxon_list():
    query = Taxon.query
    if filter_str := request.args.get('filter', ''):
        filter_dict = json.loads(filter_str)
        if keyword := filter_dict.get('q', ''):
            like_key = f'{keyword}%' if len(keyword) == 1 else f'%{keyword}%'
            query = query.filter(Taxon.full_scientific_name.ilike(like_key) | Taxon.common_name.ilike(like_key))
        if ids := filter_dict.get('id', ''):
            query = query.filter(Taxon.id.in_(ids))
        if rank := filter_dict.get('rank'):
            query = query.filter(Taxon.rank==rank)
        if pid := filter_dict.get('parent_id'):
            if parent := session.get(Taxon, pid):
                depth = Taxon.RANK_HIERARCHY.index(parent.rank)
                taxa_ids = [x.id for x in parent.get_children(depth)]
                query = query.filter(Taxon.id.in_(taxa_ids))

    return jsonify(make_query_response(query))


@api.route('/favorites', methods=['GET', 'POST'])
def favorite():
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        data = request.json
        action = ''
        if fav := Favorite.query.filter(Favorite.user_id == data['uid'], Favorite.record == data['record']).scalar():
            action = 'remove'
            session.delete(fav)
            session.commit()
        else:
            fav = Favorite(user_id=data['uid'], record=data['record'])
            session.add(fav)
            action = 'add'

        session.commit()

        return jsonify({'action': action, 'record': data['record']})

    return abort(404)
