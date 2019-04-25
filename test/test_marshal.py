from   datetime          import date, datetime, time, timedelta, timezone
from   decimal           import Decimal
from   enum              import Enum
import pytest
import sqlalchemy as S
from   dbcsv.marshalling import marshal_object, unmarshal_object

class RGBEnum(Enum):
    RED   = 1
    GREEN = 2
    BLUE  = 3

schema = S.MetaData()

table = S.Table('table', schema,
    S.Column('id', S.Integer, primary_key=True, nullable=False),
    S.Column('name', S.Unicode(2048)),
    S.Column('str', S.String(32)),
    S.Column('about', S.UnicodeText),
    S.Column('data', S.LargeBinary),
    S.Column('truth', S.Boolean),
    S.Column('realval', S.Float),
    S.Column('decval', S.Float(asdecimal=True)),
    S.Column('localtimestamp', S.DateTime()),
    S.Column('abstimestamp', S.DateTime(timezone=True)),
    S.Column('date', S.Date()),
    S.Column('time', S.Time()),
    S.Column('timetz', S.Time(timezone=True)),
    S.Column('timedelta', S.Interval()),
    S.Column('strenum', S.Enum('red', 'blue', 'green')),
    S.Column('enumenum', S.Enum(RGBEnum)),
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
            "realval": None,
            "decval": None,
            "localtimestamp": None,
            "abstimestamp": None,
            "date": None,
            "time": None,
            "timetz": None,
            "timedelta": None,
        },
        {
            "id": r'\N',
            "name": r'\N',
            "str": r'\N',
            "about": r'\N',
            "data": r'\N',
            "truth": r'\N',
            "realval": r'\N',
            "decval": r'\N',
            "localtimestamp": r'\N',
            "abstimestamp": r'\N',
            "date": r'\N',
            "time": r'\N',
            "timetz": r'\N',
            "timedelta": r'\N',
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
            "realval": 3.14,
            "decval": Decimal('3.14'),
        },
        {
            "id": "1",
            "name": "user",
            "str": "thing",
            "about": "This is test text.",
            "data": "3q2+7w==",
            "truth": "t",
            "realval": "3.14",
            "decval": "3.14",
        },
    ),

    ({"str": r'\N'}, {"str": r'\\N'}),
    ({"str": r'\\N'}, {"str": r'\\\\N'}),
    ({"truth": False}, {"truth": "f"}),

    (
        {"localtimestamp": datetime(2019, 4, 13, 19, 28, 36)},
        {"localtimestamp": "2019-04-13T19:28:36"},
    ),

    (
        {"localtimestamp": datetime(2019, 4, 13, 19, 28, 36, 314159)},
        {"localtimestamp": "2019-04-13T19:28:36.314159"},
    ),

    (
        {"abstimestamp": datetime(2019, 4, 13, 19, 28, 36,
                                  tzinfo=timezone(timedelta(hours=-4)))},
        {"abstimestamp": "2019-04-13T19:28:36-04:00"},
    ),

    (
        {"abstimestamp": datetime(2019, 4, 13, 19, 28, 36, 314159,
                                  tzinfo=timezone(timedelta(hours=-4)))},
        {"abstimestamp": "2019-04-13T19:28:36.314159-04:00"},
    ),

    ({"date": date(2019, 4, 13)}, {"date": "2019-04-13"}),
    ({"time": time(19, 28, 36)}, {"time": "19:28:36"}),
    ({"time": time(19, 28, 36, 314159)}, {"time": "19:28:36.314159"}),

    (
        {"timetz": time(19, 28, 36, tzinfo=timezone(timedelta(hours=-4)))},
        {"timetz": "19:28:36-04:00"},
    ),

    (
        {"timetz": time(19, 28, 36, 314159,
                        tzinfo=timezone(timedelta(hours=-4)))},
        {"timetz": "19:28:36.314159-04:00"},
    ),

    (
        {"timedelta": timedelta(hours=-4)},
        {"timedelta": "-14400.0"},
    ),

    (
        {"timedelta": timedelta(hours=5, microseconds=314159)},
        {"timedelta": "18000.314159"},
    ),

    ({"strenum": "red"}, {"strenum": "red"}),
    ({"strenum": "blue"}, {"strenum": "blue"}),
    ({"strenum": "green"}, {"strenum": "green"}),

    ({"enumenum": RGBEnum.RED}, {"enumenum": "RED"}),
    ({"enumenum": RGBEnum.BLUE}, {"enumenum": "BLUE"}),
    ({"enumenum": RGBEnum.GREEN}, {"enumenum": "GREEN"}),
])
def test_marshal_object(dbtyped, strtyped):
    assert marshal_object(table, dbtyped) == strtyped
    assert unmarshal_object(table, strtyped) == dbtyped
