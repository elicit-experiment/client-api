from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client
import ssl
from . import elicit_creds
from contextlib import contextmanager
import urllib
import urllib.request

@contextmanager
def user_agent_context(user_agent):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', user_agent)]
    urllib.request.install_opener(opener)
    yield
    urllib.request.install_opener(None)

# HACK to work around self-signed SSL certs used in development
def dont_check_ssl():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

class ElicitApi:
    #  PRODUCTION_URL = 'https://elicit.compute.dtu.dk'
    PRODUCTION_URL = 'http://localhost:3000'

    def __init__(self,
                 creds=elicit_creds.ElicitCreds(),
                 api_url=PRODUCTION_URL,
                 send_opt=dict(verify=True)):
        print("Initialize Elicit client library for %s options:" % api_url)
        print("Initialize Elicit client library for {} {} options:".format(creds.admin_user, creds.admin_password))
        print(send_opt)

        if ((not send_opt['verify']) and api_url.startswith("https")):
            print('WARNING: not checking SSL')
            dont_check_ssl()

        self.api_url = api_url
        with user_agent_context('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0'):
            self.swagger_url = self.api_url + '/apidocs/v1/swagger.json'
            print(self.swagger_url)
            self.app = App._create_(self.swagger_url)
        self.auth = Security(self.app)
        self.creds = creds

        # init swagger client
        self.client = Client(self.auth,
                             send_opt=send_opt)  # HACK to work around self-signed SSL certs used in development
        if (self.app.root.host != self.api_url):
            print('WARNING: API URL from swagger doesn\'t match this configuration: [%s] vs [%s]'%(self.api_url, self.app.root.host))

    def login(self):
        """
        Login to Elicit using credentials specified in init
        :return: client with auth header added.
        """
        auth_request = dict(client_id=self.creds.public_client_id,
                            client_secret=self.creds.public_client_secret,
                            grant_type='password',
                            email=self.creds.admin_user,
                            password=self.creds.admin_password)
        print(auth_request)
        resp = self.client.request(self.app.op['getAuthToken'](auth_request=auth_request))

        print(resp.status)
        assert resp.status == 200

        self.auth = resp.data
        self.auth_header = 'Bearer ' + self.auth.access_token
        self.client._Client__s.headers['Authorization'] = self.auth_header

        return self.client

    def __getitem__(self, op):
        return lambda **args: self.app.op[op](**(self.bind_auth(args)))

    def bind_auth(self, args):
        args.update(authorization=self.auth_header)
        return args
