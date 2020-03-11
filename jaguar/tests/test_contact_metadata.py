from bddrest.authoring import status, response

from jaguar.tests.helpers import AutoDocumentationBDDTest


class TestContactMetadata(AutoDocumentationBDDTest):

    def test_metadata(self):
        with self.given('Test metadata verb', '/apiv1/contacts', 'METADATA'):
            assert status == 200

            fields = response.json['fields']

            assert fields['title']['maxLength'] is not None
            assert fields['title']['minLength'] is not None
            assert fields['title']['name'] is not None
            assert fields['title']['notNone'] is not None
            assert fields['title']['required'] is not None
            assert fields['title']['watermark'] is not None
            assert fields['title']['example'] is not None
            assert fields['title']['label'] is not None
            assert fields['title']['message'] is not None

            assert fields['phone']['maxLength'] is not None
            assert fields['phone']['minLength'] is not None
            assert fields['phone']['name'] is not None
            assert fields['phone']['notNone'] is not None
            assert fields['phone']['required'] is not None
            assert fields['phone']['watermark'] is not None
            assert fields['phone']['label'] is not None
            assert fields['phone']['example'] is not None
            assert fields['phone']['message'] is not None

            assert fields['email']['maxLength'] is not None
            assert fields['email']['minLength'] is not None
            assert fields['email']['name'] is not None
            assert fields['email']['notNone'] is not None
            assert fields['email']['required'] is not None
            assert fields['email']['watermark'] is not None
            assert fields['email']['label'] is not None
            assert fields['email']['example'] is not None
            assert fields['email']['message'] is not None

