from   datetime import date
from   operator import attrgetter
from   pathlib  import Path
import sqlalchemy as S
from   dbcsv    import dumpdb, loaddb

DATA_DIR = Path(__file__).with_name('data')

metadata = S.MetaData()

planets_tbl = S.Table('planets', metadata,
    S.Column('id', S.Integer, primary_key=True, nullable=False),
    S.Column('name', S.Unicode(64), nullable=False),
    S.Column('mass_kg', S.Float, nullable=False),
    S.Column('radius_m', S.Float, nullable=False),
    S.Column('semimajor_axis_m', S.Float, nullable=False),
    S.Column('discovery_date', S.Date, nullable=True),
)

moons_tbl = S.Table('moons', metadata,
    S.Column('id', S.Integer, primary_key=True, nullable=False),
    S.Column('planet_id', S.Integer, S.ForeignKey(planets_tbl.c.id),
             nullable=False),
    S.Column('name', S.Unicode(64), nullable=False),
    S.Column('mass_kg', S.Float, nullable=False),
    S.Column('radius_m', S.Float, nullable=False),
    S.Column('semimajor_axis_m', S.Float, nullable=False),
    S.Column('discovery_date', S.Date, nullable=True),
)

PLANETS = [
    {
        "id": 1,
        "name": "Mercury",
        "mass_kg": 3.30e23,
        "radius_m": 2439500.0,
        "semimajor_axis_m": 5.79e10,
        "discovery_date": None,
    },
    {
        "id": 2,
        "name": "Venus",
        "mass_kg": 4.87e24,
        "radius_m": 6052000.0,
        "semimajor_axis_m": 1.082e11,
        "discovery_date": None,
    },
    {
        "id": 3,
        "name": "Earth",
        "mass_kg": 5.97e24,
        "radius_m": 6378000.0,
        "semimajor_axis_m": 1.496e11,
        "discovery_date": None,
    },
    {
        "id": 4,
        "name": "Mars",
        "mass_kg": 6.42e23,
        "radius_m": 3396000.0,
        "semimajor_axis_m": 2.279e11,
        "discovery_date": None,
    },
    {
        "id": 5,
        "name": "Jupiter",
        "mass_kg": 1.898e27,
        "radius_m": 71492000.0,
        "semimajor_axis_m": 7.786e11,
        "discovery_date": None,
    },
    {
        "id": 6,
        "name": "Saturn",
        "mass_kg": 5.68e26,
        "radius_m": 60268000.0,
        "semimajor_axis_m": 1.4335e12,
        "discovery_date": None,
    },
    {
        "id": 7,
        "name": "Uranus",
        "mass_kg": 8.68e25,
        "radius_m": 25559000.0,
        "semimajor_axis_m": 2.8725e12,
        "discovery_date": date(1781, 3,13),
    },
    {
        "id": 8,
        "name": "Neptune",
        "mass_kg": 1.02e26,
        "radius_m": 24764000.0,
        "semimajor_axis_m": 4.4951e12,
        "discovery_date": date(1846, 9,23),
    },
    {
        "id": 9,
        "name": "Pluto",
        "mass_kg": 1.46e22,
        "radius_m": 1185000.0,
        "semimajor_axis_m": 5.9064e12,
        "discovery_date": date(1930, 2,18),
    },
]

MOONS = [
    {
        "id": 1,
        "planet_id": 3,
        "name": "Moon",
        "mass_kg": 7.3e22,
        "radius_m": 1737500.0,
        "semimajor_axis_m": 3.84e8,
        "discovery_date": None,
    },
    {
        "id": 2,
        "planet_id": 4,
        "name": "Phobos",
        "mass_kg": 1.06e16,
        "radius_m": 11266.7,
        "semimajor_axis_m": 9378000.0,
        "discovery_date": date(1877, 8,17),
    },
    {
        "id": 3,
        "planet_id": 4,
        "name": "Deimos",
        "mass_kg": 2.4e15,
        "radius_m": 6200.0,
        "semimajor_axis_m": 23459000.0,
        "discovery_date": date(1877, 8,11),
    },
    {
        "id": 4,
        "planet_id": 5,
        "name": "Ganymede",
        "mass_kg": 1.4819e23,
        "radius_m": 2631200.0,
        "semimajor_axis_m": 1.0704e9,
        "discovery_date": date(1610, 1, 7),
    },
    {
        "id": 5,
        "planet_id": 5,
        "name": "Callisto",
        "mass_kg": 1.0759e23,
        "radius_m": 2410300.0,
        "semimajor_axis_m": 1.8827e9,
        "discovery_date": date(1610, 1, 7),
    },
    {
        "id": 6,
        "planet_id": 5,
        "name": "Io",
        "mass_kg": 8.932e22,
        "radius_m": 1821500.0,
        "semimajor_axis_m": 4.218e8,
        "discovery_date": date(1610, 1, 8),
    },
    {
        "id": 7,
        "planet_id": 5,
        "name": "Europa",
        "mass_kg": 4.8e22,
        "radius_m": 1560800.0,
        "semimajor_axis_m": 6.711e8,
        "discovery_date": date(1610, 1, 8),
    },
    {
        "id": 8,
        "planet_id": 6,
        "name": "Titan",
        "mass_kg": 1.3455e23,
        "radius_m": 2575000.0,
        "semimajor_axis_m": 1.22183e9,
        "discovery_date": date(1655, 3,25),
    },
    {
        "id": 9,
        "planet_id": 6,
        "name": "Iapetus",
        "mass_kg": 1.81e21,
        "radius_m": 734500.0,
        "semimajor_axis_m": 3.5613e9,
        "discovery_date": date(1671,10,25),
    },
    {
        "id": 10,
        "planet_id": 6,
        "name": "Rhea",
        "mass_kg": 2.31e21,
        "radius_m": 763800.0,
        "semimajor_axis_m": 5.2704e8,
        "discovery_date": date(1672,12,23),
    },
    {
        "id": 11,
        "planet_id": 6,
        "name": "Tethys",
        "mass_kg": 6.18e20,
        "radius_m": 531100.0,
        "semimajor_axis_m": 2.9466e8,
        "discovery_date": date(1684, 3,21),
    },
    {
        "id": 12,
        "planet_id": 6,
        "name": "Dione",
        "mass_kg": 1.1e21,
        "radius_m": 561400.0,
        "semimajor_axis_m": 3.7740e8,
        "discovery_date": date(1684, 3,21),
    },
    {
        "id": 13,
        "planet_id": 6,
        "name": "Mimas",
        "mass_kg": 3.79e19,
        "radius_m": 198200.0,
        "semimajor_axis_m": 1.8552e8,
        "discovery_date": date(1789, 9,17),
    },
    {
        "id": 14,
        "planet_id": 6,
        "name": "Enceladus",
        "mass_kg": 1.08e20,
        "radius_m": 252100.0,
        "semimajor_axis_m": 2.3802e8,
        "discovery_date": date(1789, 8,28),
    },
    {
        "id": 15,
        "planet_id": 6,
        "name": "Hyperion",
        "mass_kg": 5.6e18,
        "radius_m": 135000.0,
        "semimajor_axis_m": 1.4811e9,
        "discovery_date": date(1848, 9,16),
    },
    {
        "id": 16,
        "planet_id": 7,
        "name": "Titania",
        "mass_kg": 3.42e21,
        "radius_m": 788900.0,
        "semimajor_axis_m": 4.363e8,
        "discovery_date": date(1787, 1,11),
    },
    {
        "id": 17,
        "planet_id": 7,
        "name": "Oberon",
        "mass_kg": 2.88e21,
        "radius_m": 761400.0,
        "semimajor_axis_m": 5.835e8,
        "discovery_date": date(1787, 1,11),
    },
    {
        "id": 18,
        "planet_id": 7,
        "name": "Miranda",
        "mass_kg": 6.6e19,
        "radius_m": 235800.0,
        "semimajor_axis_m": 1.299e8,
        "discovery_date": date(1948, 2,16),
    },
    {
        "id": 19,
        "planet_id": 7,
        "name": "Ariel",
        "mass_kg": 1.29e21,
        "radius_m": 578900.0,
        "semimajor_axis_m": 1.909e8,
        "discovery_date": date(1851,10,24),
    },
    {
        "id": 20,
        "planet_id": 7,
        "name": "Umbriel",
        "mass_kg": 1.22e21,
        "radius_m": 584700.0,
        "semimajor_axis_m": 2.66e8,
        "discovery_date": date(1851,10,24),
    },
    {
        "id": 21,
        "planet_id": 8,
        "name": "Triton",
        "mass_kg": 2.14e22,
        "radius_m": 1353400.0,
        "semimajor_axis_m": 3.5476e8,
        "discovery_date": date(1846,10,10),
    },
    {
        "id": 22,
        "planet_id": 8,
        "name": "Naiad",
        "mass_kg": 2e17,
        "radius_m": 30200.0,
        "semimajor_axis_m": 4.8227e7,
        "discovery_date": date(1989, 9, 1),
    },
    {
        "id": 23,
        "planet_id": 8,
        "name": "Thalassa",
        "mass_kg": 4e17,
        "radius_m": 40700.0,
        "semimajor_axis_m": 5.0075e7,
        "discovery_date": date(1989, 9, 1),
    },
    {
        "id": 24,
        "planet_id": 8,
        "name": "Despina",
        "mass_kg": 2e18,
        "radius_m": 78000.0,
        "semimajor_axis_m": 5.2526e7,
        "discovery_date": date(1989, 7, 1),
    },
    {
        "id": 25,
        "planet_id": 8,
        "name": "Galatea",
        "mass_kg": 4e18,
        "radius_m": 87400.0,
        "semimajor_axis_m": 6.1953e7,
        "discovery_date": date(1989, 7, 1),
    },
    {
        "id": 26,
        "planet_id": 8,
        "name": "Larissa",
        "mass_kg": 5e18,
        "radius_m": 97000.0,
        "semimajor_axis_m": 7.3548e7,
        "discovery_date": date(1981, 5,24),
    },
    {
        "id": 27,
        "planet_id": 8,
        "name": "Proteus",
        "mass_kg": 5e19,
        "radius_m": 210000.0,
        "semimajor_axis_m": 1.17647e8,
        "discovery_date": date(1989, 6,16),
    },
    {
        "id": 28,
        "planet_id": 8,
        "name": "Nereid",
        "mass_kg": 3e19,
        "radius_m": 170000.0,
        "semimajor_axis_m": 5.5134e9,
        "discovery_date": date(1949, 5, 1),
    },
    {
        "id": 29,
        "planet_id": 9,
        "name": "Charon",
        "mass_kg": 1.586e21,
        "radius_m": 606000.0,
        "semimajor_axis_m": 1.9596e7,
        "discovery_date": date(1978, 4,13),
    },
]

def assert_dirtrees_eq(tree1: Path, tree2: Path):
    assert sorted(map(attrgetter("name"), tree1.iterdir())) \
        == sorted(map(attrgetter("name"), tree2.iterdir()))
    for p1 in tree1.iterdir():
        p2 = tree2 / p1.name
        assert p1.is_dir() == p2.is_dir()
        if p1.is_dir():
            assert_dirtrees_eq(p1, p2)
        else:
            assert p1.read_text() == p2.read_text()

def test_loaddb():
    engine = S.create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    with engine.begin() as connection:
        loaddb(connection, metadata, DATA_DIR / 'planets')
        planet_query = connection.execute(
            S.select([planets_tbl]).order_by(S.asc(planets_tbl.c.id))
        )
        assert list(map(dict, planet_query)) == PLANETS
        moon_query = connection.execute(
            S.select([moons_tbl]).order_by(S.asc(moons_tbl.c.id))
        )
        assert list(map(dict, moon_query)) == MOONS
    metadata.drop_all(engine)

def test_dumpdb(tmp_path):
    engine = S.create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(planets_tbl.insert(), PLANETS)
        connection.execute(moons_tbl.insert(), MOONS)
        # Under Python 3.5, tmp_path is a pathlib2 object, calling `Path()` on
        # which doesn't work.
        dumpdb(connection, metadata, str(tmp_path))
        assert_dirtrees_eq(tmp_path, DATA_DIR / 'planets')
    metadata.drop_all(engine)
