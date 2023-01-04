# NatureDB


## Development

Create .env (copy dotenv.sample & edit)

```
$ cp dotenv.sample .env

postgres: create database naturedb;

flask:
$ flask migrate
```
collection & organization migrate failed,
commented collection_organization and migarte later

insert default collection, organization, by hand

import hast21
- person
- proj
- geo
insert assertion_type
- assertion_type_option

change 
- other-csv
- img
- name-comment
## workflow

create db (naturedb) use adminer web ui

##


Dataset
 - 

## migrate

```bash
  $/root/.local/bin/alembic revision --autogenerate -m 'some-comment'
  $/root/.local/bin/alembic upgrade head
```



'''
class Annotation(Base):

    # CAT_CHOICES = (
    #     ('flower', '花'),
    #     ('fruit', '果'),
    #     ('flower-color', '花色'),
    #     ('fruit-color', '果色'),
    #     ('life-form', '生長型'),
    #     ('veget','植群型'),
    #     ('habitat','微生育地'),
    #     ('light-intensity','環境光度'),
    #     ('humidity','環境濕度'),
    #     ('topography', '地形位置'),
    #     ('abundance','豐富度'),
    #     ('naturalness','自然度'),
    # )
    __tablename__ = 'annotation'
    id = Column(Integer, primary_key=True)
    text = Column(String(500))
    # todo: english
    # abcd: Annotator
    # abcd: Date
    category = Column(String(500))


# Geographical Index
class AreaClass(Base):

#HAST: country (249), province (142), hsienCity (97), hsienTown (371), additionalDesc(specimen.locality_text): ref: hast_id: 144954

    __tablename__ = 'area_class'
    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    label = Column(String(500))
    #org = models.ForeignKey(on_delete=models.SET_NULL, null=True, blank=True)


#class AreaClassSystem(models.Model):
#    ancestor = models.ForeignKey(AreaClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='descendant_nodes')
#    descendant = models.ForeignKey(AreaClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='ancestor_nodes')
#    depth = models.PositiveSmallIntegerField(default=0)

class NamedArea(Base):
    __tablename__ = 'named_area'
    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    name_other = Column(String(500))
    code = Column(String(500))
    #code_standard = models.CharField(max_length=1000, null=True)
    area_class_id = Column(Integer, ForeignKey('area_class.id', ondelete='SET NULL'), nullable=True)
    area_class = relationship('AreaClass', backref=backref('named_area', passive_delete=True))
    #source_data = models.JSONField(default=dict, blank=True)
    #parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)


class Identification(Base):

    # VER_LEVEL_CHOICES = (
    #     ('0', '初次鑑定'),
    #     ('1', '二次鑑定'),
    #     ('2', '三次鑑定'),
    #     ('3', '四次鑑定'),
    )

    __tablename__ = 'identinulfication'
    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey('unit.id', ondelete='SET NULL'), nullable=True)
    unit = relationship('Unit')
    identifier = Column(Integer, ForeignKey('person.id', ondelete='SET NULL'), nullable=True)
    taxon_id = Column(Integer, ForeignKey('taxon.id', ondelete='set NULL'), nullable=True)
    taxon = relationship('Taxon', backref=backref('taxon', passive_deletes=True))
    date = Column(DateTime)
    date_text = Column(String(50)) #格式不完整的鑑訂日期, helper: ex: 1999-1
    created = Column(DateTime, default=get_time)
    changed = Column(DateTime, default=get_time, onupdate=get_time) # abcd: DateModified
    verification_level = Column(String(50))
    # abcd: IdentificationSource
    reference = Column(Text)
    note = Column(Text)

class SpecimenMark(Base):
    __tablename__ = 'specimen_mark'
    id = Column(Integer, primary_key=True)
    mark_type = Column(String(50)) # qrcode, rfid
    mark_text = Column(String(500))
    mark_author = Column(Integer, ForeignKey('person.id'))

class OtherCollector(Base):
    __tablename__ = 'gather_person_other'
    gathering_id = Column(ForeignKey('gathering.id', ondelete='CASCADE'), primary_key=True)
    gathering = relationship('gathering')
    person_id = Column(ForeignKey('person.id'), primary_key=True, ondelete='SET NULL')
    role = Column(String(50))


class Gathering(Base):
    __tablename__ = 'gathering'
    id = Column(Integer, primary_key=True)
    #project
    #method

    collect_date = Column(DateTime) # abcd: Date
    collect_date_text = Column(String(500))
    # abcd: GatheringAgent
    collector_id = Column(Integer, ForeignKey('person.id'))
    other_collectors = relationship('OtherCollector') # companion
    collector_text = Column(String(500)) # unformatted value

    # Locality
    locality_text = Column(String(500))
    locality_text2 = Column(String(500))

    #country
    name_areas = relationship('NamedArea')

    altitude = Column(Integer)
    altitude2 = Column(Integer)
    #depth

    # Coordinate
    latitude_decimal = Column(Numeric(precision=9, scale=6))
    longtitude_decimal = Column(Numeric(precision=9, scale=6))
    verbatim_latitude = Column(String(50))
    verbatim_longitude = Column(String(50))

    note = Column(Text)


class Unit(Base):
      '''specimen or observation record'''
    __tablename__ = 'unit'
    id = Column(Integer, primary_key=True)
    #guid =
    dataset_id = Column(Integer, ForeignKey('dataset.id', ondelete='SET NULL'), nullable=True)
    created = Column(DateTime, default=get_time)
    changed = Column(DateTime, default=get_time, onupdate=get_time) # abcd: DateModified
    #last_editor = Column(String(500))
    #owner
    identifications = relationship('Identification', backref=backref('units', passive_deletes=True))
    kind_of_unit = Column(String(500)) # herbarium sheet, leaf, muscle, leg, blood, ...
    # multimedia_objects
    # assemblages
    # associations
    # sequences
    # measurements_or_facts
    # sex
    # age
    field_number = Column(String(500))
    gathering_id = Column(Integer, ForeignKey('gathering.id', ondelete='SET NULL'), nullable=True)
    # abcd: SpecimenUnit
    #accessions = relationship('') multiple
    accession_number = Column(String(500))
    #preparations = TODO
    # abcd: Acquisition
    acquisition_type = Column(String(500)) # bequest, purchase, donation
    acquisition_date = Column(DateTime)
    acquired_from = Column(Integer, ForeignKey('person.id'))
    acquisition_source_text = Column(Text)
    marks = relationship('Mark')

    # abcd: Disposition (in collection/missing...)
    # specimen_measurement_or_fact
    # observation
    source_data = Column(JSONB)
    information_withheld = Column(Text)
    annotations = relationship('Annotation')

class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    given_name = Column(String(500)) # first name
    inherited_name = Column(String(500)) # last name
    is_collector = Column(Boolean, default=False)
    is_identifier = Column(Boolean, default=False)
    source_data = Column(JSONB)
    organization_id = Column(Integer, ForeignKey('organization.id', ondelete='SET NULL'), nullable=True)
'''
