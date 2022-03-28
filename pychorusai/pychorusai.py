import requests
from dateutil import parser, utils, tz
import time
import logging
logger = logging.getLogger(__name__)

TEN_MINUTES = 60 * 10


class chorusai:

    def __init__(self, token: str):
        self.token = token
        self.auth_header = {"Authorization": f"Bearer {token}"}

    def getEngagements(self, min_date=None, max_date=None, with_trackers=False):
        url = 'https://chorus.ai/v3/engagements'
        payload = {}
        payload['min_date'] = self.__datetimeToStr(min_date)
        payload['max_date'] = self.__datetimeToStr(max_date)
        if with_trackers:
            payload['with_trackers'] = True
        yield from self.getData(url, payload=payload, data_key='engagements')

    def getUsers(self):
        url = 'https://chorus.ai/v3/users'
        return next(self.getData(url))

    def getEmails(self, min_date=None, max_date=None):
        url = 'https://chorus.ai/api/v1/emails'
        payload = {}
        payload['filter[email.sent]'] = self.__comboDateRangeStr(
            min_date, max_date)
        payload['page[size]'] = 100
        yield from self.getData(url, payload=payload, data_key='data', req_page_key='page[after]')

    def getScorecards(self, min_date=None, max_date=None):
        url = 'https://chorus.ai/api/v1/scorecards'
        payload = {}
        payload['filter[submitted]'] = self.__comboDateRangeStr(
            min_date, max_date)
        payload['page[size]'] = 100
        yield from self.getData(url, payload=payload, data_key='data', req_page_key='page[number]')

    def getExternalMoments(self, min_date=None, max_date=None):
        url = 'https://chorus.ai/api/v1/moments'
        payload = {}
        payload['filter[shared_on]'] = self.__comboDateRangeStr(
            min_date, max_date)
        return next(self.getData(url, payload=payload, data_key='data'))

    def getPlaylists(self):
        url = 'https://chorus.ai/api/v1/playlists'
        payload = {}
        payload['page[size]'] = 100
        yield from self.getData(url, payload=payload, data_key='data', req_page_key='page[number]')

    def __getFromAPI(self, url: str, headers: str, params: dict = {}):
        retry = 0
        retry_limit = 5
        while retry < retry_limit:
            res = requests.get(url, headers=headers, params=params)
            if res.status_code == 429:
                logger.warning(
                    "Request reached Rate Limit of 10/min: resume in 10 minutes.")
                time.sleep(TEN_MINUTES)
                retry += 1
            else:
                return res.json()
        raise RuntimeError("Exceeded retry limit.")

    def __getData_v1(self, url=None, payload={}, req_page_key=None):
        if url is None:
            logger.error('URL missing')
            return None

        auth_header = self.auth_header
        data_key = 'data'

        first_page = self.__getFromAPI(url, auth_header, payload)
        if isinstance(first_page, dict) and 'errors' in first_page.keys():
            logger.error(first_page['errors'])
            return
        yield first_page.get(data_key)

        if not req_page_key:
            return

        if req_page_key == 'page[number]':
            payload[req_page_key] = 1
            num_returned = len(first_page[data_key])
            page_size = payload.get('page[size]')
            while num_returned == page_size:
                payload[req_page_key] += 1
                next_page = self.__getFromAPI(url, auth_header, payload)
                if isinstance(first_page, dict) and 'errors' in first_page.keys():
                    logger.error(next_page['errors'])
                    return
                yield next_page[data_key]
                num_returned = len(next_page)

        else:
            page_val = first_page.get('meta', {}).get(
                'page', {}).get('cursor')

            while page_val != None:
                payload[req_page_key] = page_val
                next_page = self.__getFromAPI(url, auth_header, payload)
                yield next_page[data_key]
                page_val = next_page.get('meta', {}).get(
                    'page', {}).get('cursor')

    def __getData_v3(self, url: str, payload: dict = {}, data_key: str = None):
        if url is None:
            logger.error('URL missing')
            return None

        auth_header = self.auth_header

        first_page = self.__getFromAPI(url, auth_header, payload)
        if data_key:
            yield first_page[data_key]
        else:
            yield first_page

        if not isinstance(first_page, dict):
            return
        page_val = first_page.get('continuation_key')

        while page_val != None:
            payload['continuation_key'] = page_val
            next_page = self.__getFromAPI(url, auth_header, payload)
            if data_key:
                if data_key not in next_page:
                    logger.error(next_page)
                    return
                yield next_page[data_key]
            else:
                yield next_page

            page_val = next_page.get('continuation_key')

    def getData(self, url: str, payload: dict = {}, data_key: str = None, req_page_key: str = None):
        if 'v3' in url:
            yield from self.__getData_v3(url, payload=payload, data_key=data_key)
        elif 'v1' in url:
            yield from self.__getData_v1(url, payload=payload, req_page_key=req_page_key)

    def __datetimeToStr(self, dt):
        if dt is None:
            return None
        if isinstance(dt, str):
            dt = parser.parse(dt)
        return utils.default_tzinfo(dt, tz.tzlocal()).isoformat()

    def __comboDateRangeStr(self, min_date=None, max_date=None):
        if min_date or max_date:
            min_date = self.__datetimeToStr(min_date)
            max_date = self.__datetimeToStr(max_date)
            return str(min_date or '*') + ':' + str(max_date or '*')
        else:
            return None
