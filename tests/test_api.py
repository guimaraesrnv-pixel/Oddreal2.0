from services.api import OddsAPI


def test_api_creation():

    api = OddsAPI()

    assert api is not None
