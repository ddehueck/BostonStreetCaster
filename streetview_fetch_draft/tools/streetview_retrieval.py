""" StreetviewQueryToolset.py

    Author: Po-Yu Hsieh (pyhsieh@bu.edu)
    Last Update: 2019/04/26
"""
from os.path import join
import json
import hashlib
import hmac
import base64
from time import time
from copy import deepcopy
import urllib.request
from urllib.request import urlretrieve
from urllib.parse import urlparse

class StreetviewQueryToolset():
    """ Toolset for doing Google street view API queries.
    """

    # API URL
    __URL_PANO = "https://maps.googleapis.com/maps/api/streetview?"
    __URL_META = "https://maps.googleapis.com/maps/api/streetview/metadata?"
    __API_OK_RESPOND = "OK"

    @staticmethod 
    def sign_url(input_url, secret):
        """ Sign a request URL with a URL signing secret.

            Args:
            input_url  - The URL to sign
            secret     - URL signing secret

            Returns:
            (str) The signed request URL.
        """
        if not input_url or not secret:
            raise Exception("Both URL and secret should be non-empty string.")

        url = urlparse(input_url)
        url_to_sign = "{}?{}".format(url.path, url.query)

        decoded_key = base64.urlsafe_b64decode(secret)
        url_to_sign_encoded = url_to_sign.encode("utf-8")
        signature = hmac.new(decoded_key, url_to_sign_encoded, hashlib.sha1)

        encoded_signature = base64.urlsafe_b64encode(signature.digest()).decode("utf-8")
        signed_url_format_args = [url.scheme, url.netloc, url.path, url.query, encoded_signature]

        return "{}://{}{}?{}&signature={}".format(*signed_url_format_args)

    @staticmethod
    def get_credentials(path):
        """ A shorthand function to access google API keys from secret file.

            Args:
                path - (str) Path to credential content (in JSON)

            Returns:
                key - Google API key
                secret - Google API secret
        """
        with open(path, "r") as fd_r:
            content = json.loads(fd_r.read())
        return content["key"], content["secret"]

    @staticmethod
    def combine_parameters(param_dict):
        """ Simple URL parameter string generation, does not handle with encoding issues.

            Args:
                param_dict - (dict) Key-value pairs for parameter name and value

            Returns:
                (str) Combined parameter string.
        """
        return "&".join(["{0:s}={1:s}".format(str(k), str(v)) for k, v in  param_dict.items()])

    def __init__(self, apikey=None, secret=None, credential_path=None, verbose=True):
        """
            Args:
                apikey - (str) Streetview service's API key.
                secret - (str) Secret key for Google API. This is required
                        when working on large-amount queries
                credential_path - (str) File for storing credential info.
                        If it's used, Credentials obtained from this parameter will
                        replace values from apikey and secret.
                verbose - (bool) Verbosity. It will print out query URL if set to
                        True.
        """
        if credential_path:
            self._apikey, self._secret = self.get_credentials(credential_path)
        else:
            self._apikey, self._secret = apikey, secret
        self.verbose = verbose

    def get_meta(self, settings):
        """ Retrieve metadata for Google street view and check if there's
            available data for this query.

            Args:
                settings - (dict) Key-value pairs for API's parameters

            Returns:
                (str|None) Panorama ID for the image, or None if not
                available.
        """
 
        settings_combined = deepcopy(settings)
        settings_combined["key"] = self._apikey
        url_base = "{0:s}{1:s}".format(self.__URL_META, self.combine_parameters(settings_combined))
        url_retrieval = self.sign_url(url_base, self._secret) if self._secret else url_base
        req_obj = urllib.request.Request(url_retrieval)
        req_result = urllib.request.urlopen(req_obj).read()
        req_json = json.loads(req_result.decode('utf-8'))
        if req_json["status"] == self.__API_OK_RESPOND:
            return req_json["pano_id"]
        if self.verbose:
            print("Failed to obtain panorama information.\n Error message: {0:s}".format(req_json["status"]))
        return None

    def get_streetview(self, output_dir, settings, prefix="", meta_guard=True):
        """ Retrive Google street view from given settings.
            Output files will be named of timestamp generated on request.

            Args:
                output_dir - (str) Output directory
                settings   - (dict) Key-value pairs for API's parameters
                prefix     - (str) Prefix for output files
                meta_guard - (bool) Do meta request (by calling get_meta()) in
                        advance, and stop the query if Google street view's
                        meta API responds with any non-success status.

            Returns:
                (str|None) File name of the retrieved image. If meta_guard
                        is set to True, it will return None when failed to
                        obtain corresponding result from API response.
        """

        if meta_guard:
            pano_id = self.get_meta(settings)
            if not pano_id:
                return None

        settings_combined = deepcopy(settings)
        # Replace location with pano ID
        if meta_guard:
            del settings_combined["location"]
            settings_combined["pano_id"] = pano_id
        settings_combined["key"] = self._apikey
        url_base = "{0:s}{1:s}".format(self.__URL_PANO, self.combine_parameters(settings_combined))
        url_retrieval = self.sign_url(url_base, self._secret) if self._secret else url_base
        output_name = "{}{}.jpg".format(prefix, str(int(time() * 1000)))
        if self.verbose:
            print("URL request:" + url_retrieval)
        _ = urlretrieve(url_retrieval, join(output_dir, output_name))
        if self.verbose:
            print("Done with saving file to: {0:s}".format(output_name))

        return output_name

