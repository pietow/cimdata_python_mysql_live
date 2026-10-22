import pytest

@pytest.fixture
def box():
    print()
    print("1: box vorbereiten")
    value = []
    yield value
    print()
    print("4: box aufräumen")
    value.clear()

@pytest.fixture
def filled_box(box):
    print("2. dieselbe box befüllen")
    box.append('Alte Runen')
    return box


def test_shared_value(filled_box, box):
    print("3. Test ausführen")
    assert filled_box is box
    assert box == ['Alte Runen']

# def test_fresh_value(box):
#    assert box == [] 