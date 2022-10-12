from __future__ import annotations
import requests
from datetime import datetime
from typing import Optional, List
from vatusa_api_client.models import (ControllerData, ControllerDetails, ControllerActionLog,
                                      FacilityData, FacilityRequestsData, Config, NewsPostData)


class Client:
    api_token: str
    config: ConfigSubClient
    controller: ControllerSubClient
    facility: FacilitySubClient
    news: NewsSubClient
    request: RequestSubClient
    solo: SoloSubClient

    def __init__(self, api_token: str, base_url: str = None):
        self.base_url = base_url if base_url is not None else 'http://127.0.0.1:8000'  # TODO: Set default base URL
        if self.base_url.endswith('/'):
            raise Exception("Base URL should not end with /")
        self.api_token = api_token
        self.config = ConfigSubClient(self)
        self.controller = ControllerSubClient(self)
        self.facility = FacilitySubClient(self)
        self.news = NewsSubClient(self)
        self.request = RequestSubClient(self)
        self.solo = SoloSubClient(self)

    def _raw_request(self, method: str, uri: str, **kwargs):
        if method not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise Exception("API Method not supported %s" % method)
        if not uri.startswith('/'):
            raise Exception("URI must start with /")
        url = '%s%s' % (self.base_url, uri)
        response = requests.request(method, url, headers={'Authorization': 'Bearer %s' % self.api_token}, **kwargs)
        if response.status_code != 200:
            raise Exception("Response Status Code not 200")
        return response.json()

    def call(self, method: str, uri: str, object_type=None, is_list=False, **kwargs):
        output = self._raw_request(method, uri, **kwargs)
        if object_type is not None:
            if is_list:
                return [object_type.parse_obj(r) for r in output]
            else:
                return object_type.parse_obj(output)
        return None

    def get(self, uri, object_type, is_list=False, **kwargs):
        return self.call('GET', uri, object_type=object_type, is_list=is_list, **kwargs)

    def post(self, uri, **kwargs):
        return self.call('POST', uri, **kwargs)

    def put(self, uri, **kwargs):
        return self.call('PUT', uri, **kwargs)

    def delete(self, uri, **kwargs):
        return self.call('DELETE', uri, **kwargs)


class SubClient:
    def __init__(self, client: Client):
        self.client = client


class ConfigSubClient(SubClient):
    def get(self) -> Config:
        return self.client.get('/config/', Config)


class ControllerSubClient(SubClient):
    def get(self, cid: int) -> ControllerData:
        return self.client.get('/controller/%s' % cid, ControllerData)

    def get_details(self, cid: int) -> ControllerDetails:
        return self.client.get('/controller/%s/details' % cid, ControllerDetails)

    def search(self, *,
               first_name: Optional[str] = None,
               last_name: Optional[str] = None,
               facility: Optional[str] = None,
               rating: Optional[int] = None,
               email: Optional[str] = None) -> List[ControllerData]:
        return self.client.get('/controller/search', ControllerData, is_list=True, params={
            'first_name': first_name,
            'last_name': last_name,
            'facility': facility,
            'rating': rating,
            'email': email
        })

    def get_action_log(self, cid: int) -> List[ControllerActionLog]:
        return self.client.get('/controller/%s/log' % cid, ControllerActionLog, is_list=True)

    def add_facility_role(self, cid: int, admin_cid: int, facility: str, role: str) -> bool:
        return self.client.post('/controller/%s/role/facility' % cid, data={
            'admin_cid': admin_cid,
            'facility': facility,
            'role': role
        })

    def remove_facility_role(self, cid: int, admin_cid: int, facility: str, role: str) -> bool:
        return self.client.delete('/controller/%s/role/facility' % cid, data={
            'admin_cid': admin_cid,
            'facility': facility,
            'role': role
        })

    def add_global_role(self, cid: int, admin_cid: int, role: str) -> bool:
        return self.client.post('/controller/%s/role/global' % cid, data={
            'admin_cid': admin_cid,
            'role': role
        })

    def remove_global_role(self, cid: int, admin_cid: int, role: str) -> bool:
        return self.client.delete('/controller/%s/role/global' % cid, data={
            'admin_cid': admin_cid,
            'role': role
        })

    def update_rating(self, cid: int, admin_cid: int, rating: int) -> bool:
        return self.client.put('/controller/%s/rating' % cid, data={
            'admin_cid': admin_cid,
            'rating': rating
        })

    def set_flag(self, cid: int, admin_cid: int, flag: str, value: bool) -> bool:
        return self.client.put('/controller/%s/flag' % cid, data={
            'admin_cid': admin_cid,
            'flag': flag,
            'value': value
        })

    def roster_remove(self, cid: int, admin_cid: int, facility: str, reason: str) -> bool:
        return self.client.delete('/controller/%s/facility' % cid, data={
            'admin_cid': admin_cid,
            'facility': facility,
            'reason': reason
        })


class FacilitySubClient(SubClient):
    def all(self) -> List[FacilityData]:
        return self.client.get('/facility/', FacilityData, is_list=True)

    def get(self, facility: str) -> FacilityData:
        return self.client.get('/facility/%s' % facility, FacilityData)

    def get_roster(self, facility: str, include_home=True, include_visitor=True) -> List[ControllerData]:
        if include_home and include_visitor:
            roster_type = 'ALL'
        elif include_home:
            roster_type = 'HOME'
        elif include_visitor:
            roster_type = 'VISITOR'
        else:
            raise Exception("Invalid RosterType")
        return self.client.get('/facility/%s/roster/%s' % (facility, roster_type), ControllerData, is_list=True)

    def add_visitor(self, facility: str, cid: int, reason: Optional[str]) -> bool:
        return self.client.post('/facility/%s/roster' % facility, data={
            'cid': cid,
            'reason': reason
        })

    def remove_controller(self, facility: str, cid: int, reason: Optional[str]) -> bool:
        return self.client.delete('/facility/%s/roster' % facility, data={
            'cid': cid,
            'reason': reason
        })

    def get_requests(self, facility: str) -> FacilityRequestsData:
        return self.client.get('/facility/%s/request' % facility, FacilityRequestsData)

    def get_staff(self, facility: str):
        return self.client.get('/facility/%s/staff' % facility, None)  # TODO - Add object type


class RequestSubClient(SubClient):
    def create_transfer(self, cid: int, admin_cid: int, facility: str, reason: str) -> bool:
        pass

    def update_transfer(self, transfer_id: int, admin_cid: int, accept: bool, reason: Optional[str]) -> bool:
        pass

    def create_visit_request(self, cid: int, admin_cid: int, facility: str, reason: str) -> bool:
        pass

    def update_visit_request(self, cid: int, admin_cid: int, accept: bool, reason: Optional[str]) -> bool:
        pass


class NewsSubClient(SubClient):
    def get_news(self) -> List[NewsPostData]:
        return self.client.get('/news/', NewsPostData, is_list=True)

    def create_news(self, facility: str, author_cid: int, title: str, body: str, banner_image_url: str, publish: bool):
        return self.client.post('/news/', data={
            'facility': facility,
            'author_cid': author_cid,
            'title': title,
            'body': body,
            'banner_image_url': banner_image_url,
            'publish': publish
        })

    def update_news_post(self,
                         post_id: int,
                         facility: str,
                         author_cid: int,
                         title: str,
                         body: str,
                         banner_image_url: str,
                         publish: bool):
        return self.client.put('/news/%d' % post_id, data={
            'facility': facility,
            'author_cid': author_cid,
            'title': title,
            'body': body,
            'banner_image_url': banner_image_url,
            'publish': publish
        })

    def delete_news_post(self, post_id: int):
        return self.client.delete('/news/%d' % post_id)


class SoloSubClient(SubClient):
    def all(self):
        pass

    def all_facility(self, facility: str):
        pass

    def create(self, cid: int, facility: str, position: str, expiration: datetime.date, admin_cid: int) -> bool:
        pass

    def delete(self, solo_id: int) -> bool:
        pass
