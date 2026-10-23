import pytest

@pytest.fixture(scope="session")
def start_end():
    print()
    print('Start')
    yield
    print('End')

@pytest.fixture(scope="function")
def prepared_student(start_end):
    student = {'id': 1, 'name': 'harry'}
    return student
    print('Fixture ended')


def test_student(prepared_student):
    assert prepared_student['name'] == 'harry'


def test_student2(prepared_student):
    assert prepared_student['id'] == 1