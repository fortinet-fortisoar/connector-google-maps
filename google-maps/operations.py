""" Copyright start
  Copyright (C) 2008 - 2022 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

import requests, json
import base64
from connectors.core.connector import get_logger, ConnectorError

logger = get_logger('google-maps')

errors = {
    400: 'Bad/Invalid Request',
    401: 'Unauthorized: Invalid credentials provided failed to authorize',
    403: 'Access Denied',
    404: 'Not Found',
    500: 'Internal Server Error',
}


class GoogleMaps(object):
    def __init__(self, config, *args, **kwargs):
        self.api_key = config.get('api_key')
        url = config.get('server_url').strip('/')
        if not url.startswith('https://') and not url.startswith('http://'):
            self.url = 'https://{0}/'.format(url)
        else:
            self.url = url + '/'
        self.sslVerify = config.get('verify_ssl')

    def make_rest_call(self, url, method, data=None, params=None):
        try:
            url = self.url + url
            params.update({'key': self.api_key})
            headers = {'Content-Type': 'application/json'}
            response = requests.request(method, url, headers=headers, verify=self.sslVerify, data=data, params=params)
            if response.ok or response.status_code == 204:
                logger.info('Successfully got response for url {}'.format(url))
                if 'json' in str(response.headers):
                    return response.json()
                else:
                    return response.content
            else:
                logger.error("{0}".format(errors.get(response.status_code, '')))
                raise ConnectorError("{0}".format(errors.get(response.status_code, response.text)))
        except requests.exceptions.SSLError:
            raise ConnectorError('SSL certificate validation failed')
        except requests.exceptions.ConnectTimeout:
            raise ConnectorError('The request timed out while trying to connect to the server')
        except requests.exceptions.ReadTimeout:
            raise ConnectorError(
                'The server did not send any data in the allotted amount of time')
        except requests.exceptions.ConnectionError:
            raise ConnectorError('Invalid endpoint or credentials')
        except Exception as err:
            raise ConnectorError(str(err))


def get_maps_geocode(config, params):
    try:
        gm = GoogleMaps(config)
        endpoint = "maps/api/geocode/json"
        query_parameter = {
            'address': params.get('address')
        }
        response = gm.make_rest_call(endpoint, 'GET', params=query_parameter)
        return response
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


def _check_health(config):
    try:
        response = get_maps_geocode(config, params={'address': "fortinet"})
        if response:
            return True
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


operations = {
    'get_maps_geocode': get_maps_geocode
}
