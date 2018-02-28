import pytest


@pytest.fixture
def data():
    return {'name': 'Name', 'email': 'example@email.com',
            'message': 'Hello there'}
