from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
query = Table('query', post_meta,
    Column('id', Integer),
    Column('value', String(length=140), primary_key=True, nullable=False),
    Column('errors', String(length=140)),
    Column('votes', Integer),
    Column('timestamp', DateTime),
    Column('views', Integer),
    Column('success', Boolean),
    Column('user_id', Integer),
)

tag = Table('tag', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=50)),
)

tags = Table('tags', post_meta,
    Column('tag_id', Integer),
    Column('query_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['query'].create()
    post_meta.tables['tag'].create()
    post_meta.tables['tags'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['query'].drop()
    post_meta.tables['tag'].drop()
    post_meta.tables['tags'].drop()
