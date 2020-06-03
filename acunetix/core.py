#!/usr/bin/env python3
import requests
import constants
import json

from .axeception import AXException

requests.packages.urllib3.disable_warnings()


class Acunetix(object):
    def __init__(self, host=None, api=None, timeout=20):
        self.apikey = api
        self.host = str(
            "{}{}".format("https://" if "https://" not in host else "", host)
        )
        self.timeout = timeout
        self.headers = {
            "X-Auth": self.apikey,
            "content-type": "application/json",
            "User-Agent": "Acunetix",
        }
        self.target_criticality_allowed = target_criticality_allowed

    def __json_return(self, data):
        try:
            return json.loads(data)
        except:
            pass

    def __send_request(self, method="get", endpoint="", data=None):
        request_call = getattr(requests, method)
        url = str("{}{}".format(self.host, endpoint if endpoint else "/"))
        try:
            request = request_call(
                url,
                headers=self.headers,
                timeout=self.timeout,
                data=json.dumps(data),
                verify=False,
            )
            return self.__json_return(request.text)
        except Exception as e:
            raise AXException(HTTP_ERROR, f"HTTP ERROR OCCURED: {e}")

    def info(self):
        return self.__send_request(method="get", endpoint="/api/v1/info")

    def targets(self):
        return self.__send_request(
            method="get", endpoint="/api/v1/targets?pagination=50"
        )

    def add_target(self, target="", criticality="normal"):
        if criticality not in self.target_criticality_allowed:
            raise AXException(NOT_ALLOWED_CRITICYLITY_PROFILE, "Criticallity not found")
        target_address = (
            target if "http://" or "https://" in target else "http://{}".format(target)
        )
        data = {
            "address": target_address,
            "description": "Sent from Acunetix-Python",
            "criticality": target_criticality_list[criticality],
        }
        return self.__send_request(method="post", endpoint="/api/v1/targets", data=data)

    def delete_target(self, target_id):
        return self.__send_request(
            method="delete", endpoint="/api/v1/targets/{}".format(target_id)
        )

    def scans(self):
        return self.__send_request(method="get", endpoint="/api/v1/scans")

    def delete_all_targets(self):
        targets = self.targets()
        if len(targets["targets"]):
            for target in targets["targets"]:
                self.delete_target(target["target_id"])
        else:
            break
