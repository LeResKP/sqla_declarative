import unittest
import sqlalchemy as sa
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension
from declarative import extended_declarative_base, _marker
import transaction


class TestExtendedBase(unittest.TestCase):

    def setUp(self):
        self.session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
        Base = extended_declarative_base(
            self.session,
            metadata=sa.MetaData('sqlite:///:memory:'))

        class Test1(Base):
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.String(50))

        class Test2(Base):
            idtest = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.String(50))

        Base.metadata.create_all()

        self.Test1 = Test1
        self.Test2 = Test2
        with transaction.manager:
            self.value1 = Test1(name='Bob')
            self.session.add(self.value1)
            self.value2 = Test2(name='Bob')
            self.session.add(self.value2)

    def test_query(self):
        self.session.add(self.value1)
        self.session.add(self.value2)
        self.assertEqual(self.Test1.query.count(), 1)
        self.assertEqual(self.Test1.query.one(), self.value1)
        self.assertEqual(self.Test2.query.count(), 1)
        self.assertEqual(self.Test2.query.one(), self.value2)

    def test_tablename(self):
        self.assertEqual(self.Test1.__tablename__, 'test1')
        self.assertEqual(self.Test2.__tablename__, 'test2')

    def test_pk_name(self):
        self.assertEqual(self.Test1._pk_name_cached, _marker)
        self.assertEqual(self.Test1._pk_name(), 'id')
        self.assertEqual(self.Test1._pk_name_cached, 'id')
        self.assertEqual(self.Test1()._pk_name(), 'id')

        self.assertEqual(self.Test2._pk_name_cached, _marker)
        self.assertEqual(self.Test2._pk_name(), 'idtest')
        self.assertEqual(self.Test2._pk_name_cached, 'idtest')
        self.assertEqual(self.Test2()._pk_name(), 'idtest')

    def test_pk_id(self):
        v = self.Test1.query.one()
        self.assertEqual(v.pk_id, 1)
        v = self.Test2.query.one()
        self.assertEqual(v.pk_id, 1)


class TestExtendedBaseManyPk(unittest.TestCase):

    def setUp(self):
        self.session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
        Base = extended_declarative_base(
            self.session,
            metadata=sa.MetaData('sqlite:///:memory:'))

        class Test1(Base):
            id1 = sa.Column(sa.Integer, primary_key=True)
            id2 = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.String(50))

        Base.metadata.create_all()

        self.Test1 = Test1
        with transaction.manager:
            self.value = Test1(id1=1, id2=1, name='Bob')
            self.session.add(self.value)

    def test_query(self):
        self.assertEqual(self.Test1.query.count(), 1)

    def test_tablename(self):
        self.assertEqual(self.Test1.__tablename__, 'test1')

    def test_pk_name(self):
        self.assertEqual(self.Test1._pk_name_cached, _marker)
        try:
            self.assertEqual(self.Test1._pk_name(), 'id')
            assert(0)
        except Exception, e:
            self.assertEqual(
                str(e),
                'Too many primary keys to use this function')

    def test_pk_id(self):
        v = self.Test1.query.one()
        try:
            self.assertEqual(v.pk_id, 1)
            assert(0)
        except Exception, e:
            self.assertEqual(
                str(e),
                'Too many primary keys to use this function')

