import time
from app.db.utils import uuid7


def test_uuid7_generation():
    id1 = uuid7()
    time.sleep(0.005)
    id2 = uuid7()

    assert id1 != id2
    assert id1.version == 7
    assert id2.version == 7
    # UUIDv7 are time-ordered
    assert str(id1) < str(id2)
