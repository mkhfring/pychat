
from ..controllers.root import Root
from bddrest.authoring import response
from restfulpy.testing import ApplicableTestCase


class TestApplication(ApplicableTestCase):
    __controller_factory__ = Root

    def test_version(self):
        call = dict(
            title='Application version',
            description='Get application version',
            url='/apiv1/version',
            verb='GET',
        )

        with self.given(**call):
            assert response.status == '200 OK'

