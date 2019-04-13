import pytest
import sqlalchemy as S
from   dbcsv import marshal_object, unmarshal_object

schema = S.MetaData()

table = S.Table('table', schema,
    S.Column('id', S.Integer, primary_key=True, nullable=False),
    S.Column('name', S.Unicode(2048)),
    S.Column('str', S.String(32)),
    S.Column('about', S.UnicodeText),
    S.Column('data', S.LargeBinary),
    S.Column('truth', S.Boolean),
)

@pytest.mark.parametrize('dbtyped,strtyped', [
    (
        {
            "id": None,
            "name": None,
            "str": None,
            "about": None,
            "data": None,
            "truth": None,
        },
        {
            "id": r'\N',
            "name": r'\N',
            "str": r'\N',
            "about": r'\N',
            "data": r'\N',
            "truth": r'\N',
        },
    ),

    (
        {
            "id": 1,
            "name": "user",
            "str": "thing",
            "about": "This is test text.",
            "data": b'\xDE\xAD\xBE\xEF',
            "truth": True,
        },
        {
            "id": "1",
            "name": "user",
            "str": "thing",
            "about": "This is test text.",
            "data": "3q2+7w==",
            "truth": "t",
        },
    ),

    ({"str": r'\N'}, {"str": r'\\N'}),
    ({"str": r'\\N'}, {"str": r'\\\\N'}),
    ({"truth": False}, {"truth": "f"}),
])
def test_marshal_object(dbtyped, strtyped):
    assert marshal_object(table, dbtyped) == strtyped
    assert unmarshal_object(table, strtyped) == dbtyped
