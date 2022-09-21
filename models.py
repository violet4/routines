#!/usr/bin/env python
import datetime
import os
from contextlib import contextmanager
import subprocess

from sqlalchemy import (
    BigInteger, Text, Integer, DateTime, DECIMAL, BOOLEAN,
    ForeignKey,
    Column
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.schema import MetaData
from sqlalchemy.orm import relationship

from sqlalchemy import create_engine


def pkey(id_str, dtype=Integer):
    return Column(
        id_str,
        dtype,
        autoincrement=True,
        primary_key=True,
    )


def datetime_col(colname, nullable=False, default="date_trunc('second', now())::timestamp"):
    return Column(
        colname,
        DateTime,
        nullable=nullable,
        default=default,
    )


def load_connection_strings():
    # hostname:port:database:username:password
    connection_strings = []
    pgpass_path = os.path.join(os.environ['HOMEPATH'], r'AppData\Roaming\postgresql\pgpass.conf')
    with open(pgpass_path, 'r') as fr:
        for line in fr:
            if line.strip().startswith('#'):
                continue
            parts = line.strip().split(':')
            if len(parts) != 5:
                continue
            hostname, port, database, username, password = parts
            connection_strings.append(f'postgresql://{username}:{password}@{hostname}:{port}/{database}')
    return connection_strings


def load_connection_string():
    return load_connection_strings()[0]


def do_create_engine():
    return create_engine(load_connection_string())


# %APPDATA%\postgresql\pgpass.conf
# connection_string = 'postgresql://username[:password]@host[:port]/dbname'
schema_name = 'routines'

engine = do_create_engine()

SABase = declarative_base(
    metadata=MetaData(
        bind=engine,
        schema=schema_name,
    ),
)


class Base:
    created_at = datetime_col('created_at')
    modified_at = datetime_col('modified_at')

    def __init__(self, time=None):
        if time is None:
            time = datetime.datetime.now().replace(microsecond=0)
        self.created_at = self.modified_at = time

    @staticmethod
    def get_col_name(col):
        return str(col).split('.')[-1]

    @classmethod
    def get_row(cls, col, value, sess):
        query = sess.query(cls).filter(col==value)

        # if it exists, then return it
        row = query.one_or_none()
        if row is not None:
            return row

        # otherwise, create one
        row = cls()
        setattr(
            row,
            cls.get_col_name(col),
            value
        )

        # make sure the row is entered into the db and
        # has its id field populated so its id can be
        # referenced
        try:
            sess.add(row)
            sess.commit()
        except Exception as e:
            print("if this raises a confusing error, it could be that the sqlalchemy model doesn't match the database schema")
            raise

        return row

    Session = None
    @classmethod
    def set_sess(cls, Session):
        cls.Session = Session

    @classmethod
    @contextmanager
    def get_session(cls, sess=None):
        """

        Note that operations that create rows in
        multiple tables at once need to share
        the same session.
        """
        if sess is None:
            managed = True
            if cls.Session is None:
                raise Exception(
                    "session not set. must be set using Base.set_sess(sqlalchemy.orm.sessionmaker(bind=engine))"
                )
            sess = cls.Session()
        else:
            managed = False
        try:
            yield sess
        except KeyboardInterrupt:
            raise
        except Exception:
            # TODO not sure whether unmanaged session should be rolled back
            sess.rollback()
        else:
            if managed:
                sess.commit()
        finally:
            if managed:
                sess.close()

    def __repr__(self):
        """Generic repr method for 
        """
        attrs = list()
        for k in self.__init__.__code__.co_varnames[1:]:
            if not hasattr(self, k):
                continue
            attrs.append('{}={}'.format(
                k, repr(getattr(self, k))
            ))
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(attrs),
        )

    def __str__(self):
        return repr(self)


class Activity(Base, SABase):
    __tablename__ = 'activity'
    activity_id = pkey('activity_id')
    name = Column('name', TEXT)


class Food(Base, SABase):
    __tablename__ = 'food'
    fid = pkey('fid')
    food = Column('food', Text, unique=True)

    @classmethod
    def get_row(cls, food_str, sess):
        food = super(Food, cls).get_row(
            col=cls.food,
            value=food_str,
            sess=sess,
        )
        return food

    def __repr__(self):
        return '{}(food={})'.format(
            self.__class__.__name__,
            repr(self.food),
        )


class Eat(Base, SABase):
    __tablename__ = 'eat'

    # primary key - "eat id"
    eid = pkey('eid', dtype=BigInteger)

    # local columns
    amount = Column('amount', Text)
    deleted = Column('deleted', BOOLEAN, default=False, nullable=False)
    location = Column('location', Text, default=None)

    ### Foreign columns

    fid = Column('fid', Integer, ForeignKey('food.fid'))
    food = relationship('Food')

    @classmethod
    def create_entry(cls, food_str, amount_str=None, time=None, location_str=None, sess=None):
        with cls.get_session(sess=sess) as sess:
            eat = cls()
            eat.amount = amount_str
            eat.created_at = eat.modified_at = time or datetime.datetime.now()
            eat.location = location_str

            food = Food.get_row(food_str, sess)
            eat.fid = food.fid

            sess.add(eat)
            sess.commit()
        return eat

    def __repr__(self):
        return '{}(food_str={}, amount_str={}, time={}, location_str={})'.format(
            self.__class__.__name__,
            *[repr(obj) for obj in [
                self.food.food,
                self.amount,
                self.created_at,
                self.location,
            ]]
        )
    def __str__(self):
        return repr(self)



if __name__ == '__main__':
    import sqlalchemy
    Base.set_sess(sqlalchemy.orm.sessionmaker(bind=engine))
    with Base.get_session() as sess:
        eat = Eat.create_entry(food_str='hot chocolate', amount_str='1 cup', location_str='home', sess=sess)
        print(eat)
