from   dbcsv import marshal_object, unmarshal_object
import pytest
import sqlalchemy as S

schema = S.MetaData()

table = S.Table('table', schema,
    S.Column('id', S.Integer, primary_key=True, nullable=False),
    S.Column('name', S.Unicode(2048)),
    S.Column('str', S.String(32)),
    S.Column('about', S.UnicodeText),
)

@pytest.mark.parametrize('dbtyped,strtyped', [
    (
        {"id": None, "name": None, "str": None, "about": None},
        {"id": r'\N', "name": r'\N', "str": r'\N', "about": r'\N'},
    ),

    (
        {
            "id": 1,
            "name": "user",
            "str": "thing",
            "about": "This is test text.",
        },
        {
            "id": "1",
            "name": "user",
            "str": "thing",
            "about": "This is test text.",
        },
    ),
])
def test_marshal_object(dbtyped, strtyped):
    assert marshal_object(table, dbtyped) == strtyped
    assert unmarshal_object(table, strtyped) == dbtyped
