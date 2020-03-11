from nanohttp import settings
from restfulpy.logging_ import get_logger
from requests import request
from requests.exceptions import RequestException


logger = get_logger('webhook')


HTTP_NO_CONTENT = 204


class Webhook:

    def sent_message(self, room_id, member_reference_id):
        try:
            response = request(
                settings.webhooks.sent.verb,
                settings.webhooks.sent.url,
                params=dict(
                    roomId=room_id,
                    memberReferenceId=member_reference_id
                ),
                timeout=settings.webhooks.sent.timeout,
            )
            if response.status_code != HTTP_NO_CONTENT:
                self._bad_thirdparty_response(response.status_code)

        except Exception as ex:
            self._handle_exception(ex)

    def mentioned_member(self, room_id, mentioned_reference_id):
        try:
            response = request(
                settings.webhooks.mentioned.verb,
                settings.webhooks.mentioned.url,
                params=dict(
                    roomId=room_id,
                    memberReferenceId=mentioned_reference_id
                ),
                timeout=settings.webhooks.mentioned.timeout,
            )
            if response.status_code != HTTP_NO_CONTENT:
                self._bad_thirdparty_response(response.status_code)

        except Exception as ex:
            self._handle_exception(ex)

    def _handle_exception(self, ex):
        if isinstance(ex, RequestException):
            logger.exception(f'Request Error: {ex}')

    def _bad_thirdparty_response(self, code):
        logger.exception(
            f'Third party exception with {code} status'
        )

