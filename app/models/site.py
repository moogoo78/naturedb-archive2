from sqlalchemy import (
    Table,
    Column,
    Integer,
    Numeric,
    String,
    Text,
    DateTime,
    Date,
    Boolean,
    ForeignKey,
    desc,
)
from sqlalchemy.orm import (
    relationship,
    backref,
    validates,
)
from sqlalchemy.dialects.postgresql import JSONB
from flask_login import UserMixin

from app.database import (
    Base,
    session,
    TimestampMixin,
)

# organization_collection = Table(
#     'organization_collection',
#     Base.metadata,
#     Column('organization_id', ForeignKey('organization.id')),
#     Column('collection_id', ForeignKey('collection.id')),
# )

class User(Base, UserMixin, TimestampMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(500))
    passwd = Column(String(500))
    status = Column(String(1), default='P')
    organization_id = Column(Integer, ForeignKey('organization.id', ondelete='SET NULL'), nullable=True)
    #default_collection_id = Column(Integer, ForeignKey('collection.id', on
    organization = relationship('Organization')
    favorites = relationship('Favorite', primaryjoin='User.id == Favorite.user_id')


class Favorite(Base):
    __tablename__ = 'favorite'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    record = Column(String(500))


class Organization(Base, TimestampMixin):
    __tablename__ = 'organization'

    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    short_name = Column(String(500))
    code = Column(String(500))
    related_link_categories = relationship('RelatedLinkCategory')
    #collections = relationship('Collection', secondary=organization_collection)
    collections = relationship('Collection')
    #default_collection_id = Column(Integer, ForeignKey('collection.id', ondelete='SET NULL'), nullable=True)
    #default_collection = relationship('Collection', primaryjoin='Organization.default_collection_id == Collection.id')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation,
        }

class ArticleCategory(Base):
    __tablename__ = 'article_category'

    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    label = Column(String(500))
    organization_id = Column(Integer, ForeignKey('organization.id', ondelete='SET NULL'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id, 
            'name': self.name,
            'label': self.label,
        }

class Article(Base, TimestampMixin):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    subject = Column(String(500))
    content = Column(Text)
    organization_id = Column(Integer, ForeignKey('organization.id', ondelete='SET NULL'), nullable=True)
    category_id = Column(Integer, ForeignKey('article_category.id', ondelete='SET NULL'), nullable=True)
    category = relationship('ArticleCategory')
    publish_date = Column(Date)
    # published_by = Column(String(500))
    data = Column(JSONB) # language, url, published_by
    is_markdown = Column(Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id or '',
            'subject': self.subject or '',
            'content': self.content or '',
            'category_id': self.category_id or '',
            'publish_date': self.publish_date.strftime('%Y-%m-%d') if self.publish_date else'',
            'created': self.created or '',
            'category': self.category.to_dict() if self.category else None,
        }

    def get_form_layout(self):
        return {
            'categories': [x.to_dict() for x in ArticleCategory.query.all()]
        }

class RelatedLinkCategory(Base):
    __tablename__ = 'related_link_category'

    id = Column(Integer, primary_key=True)
    label = Column(String(500))
    name = Column(String(500))
    sort = Column(Integer, nullable=True)
    organization_id = Column(ForeignKey('organization.id', ondelete='SET NULL'))
    related_links = relationship('RelatedLink')

class RelatedLink(Base, TimestampMixin):
    __tablename__ = 'related_link'

    id = Column(Integer, primary_key=True)
    category_id = Column(ForeignKey('related_link_category.id', ondelete='SET NULL'))
    title = Column(String(500))
    url = Column(String(1000))
    note = Column(String(1000))
    status = Column(String(4), default='P')
    organization_id = Column(Integer, ForeignKey('organization.id', ondelete='SET NULL'), nullable=True)

    category = relationship('RelatedLinkCategory', back_populates='related_links')
