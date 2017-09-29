# -*- coding: utf-8 -*-

import json, logging, pprint
import requests
from . import logger_setup
from .auth import Authenticator


log = logging.getLogger(__name__)
logger_setup.check_logger()


class Requester( object ):
    """ Enables easy calls to the BorrowDirect request webservice.
        BorrowDirect 'RequestItem Web Service' docs: <http://borrowdirect.pbworks.com/w/page/90133541/RequestItem%20Web%20Service> (login required)
        Called by BorrowDirect.run_request_item() """

    def __init__( self ):
        self.valid_search_keys = [ 'ISBN', 'ISSN', 'LCCN', 'OCLC', 'PHRASE' ]

    def request_item( self, patron_barcode, search_key, search_value, pickup_location, api_url_root, api_key, partnership_id, university_code ):
        """ Searches for exact key-value.
            Called by BorrowDirect.run_request_item() """
        assert search_key in self.valid_search_keys
        authorization_id = self.get_authorization_id( patron_barcode, api_url_root, api_key, partnership_id, university_code )
        params = self.build_params( partnership_id, authorization_id, pickup_location, search_key, search_value )
        url = '%s/dws/item/add?aid=%s' % ( api_url_root, authorization_id )
        headers = { 'Content-type': 'application/json' }
        r = requests.post( url, data=json.dumps(params), headers=headers )
        log.debug( 'request r.url, `%s`' % r.url )
        log.debug( 'request r.content, `%s`' % r.content.decode('utf-8') )
        result_dct = r.json()
        return result_dct

    def get_authorization_id( self, patron_barcode, api_url_root, api_key, partnership_id, university_code ):
        """ Obtains authorization_id.
            Called by request_item()
            Note that only the authenticator webservice is called;
              the authorization webservice simply extends the same id's session time and so is not needed here. """
        authr = Authenticator()
        authorization_id = authr.authenticate(
            patron_barcode, api_url_root, api_key, partnership_id, university_code )
        return authorization_id

    def build_params( self, partnership_id, authorization_id, pickup_location, search_key, search_value ):
        """ Builds request json.
            Called by request_item() """
        params = {
            'PartnershipId': partnership_id,
            'PickupLocation': pickup_location,
            'Notes': '',
            'ExactSearch': [ {
                'Type': search_key,
                'Value': search_value
                } ]
            }
        log.debug( 'params, `%s`' % pprint.pformat(params) )
        return params

    # end class Requester
