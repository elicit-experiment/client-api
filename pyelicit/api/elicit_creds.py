import pprint

class ElicitCreds:
    """
    Class defining credentials to communicate with the Elicit service
    """
    PUBLIC_CLIENT_ID = 'admin_public'
    PUBLIC_CLIENT_SECRET = 'czZCaGRSa3F0MzpnWDFmQmF0M2JW'
    # ADMIN_USER = 'pi@elicit.com'
    # ADMIN_PASSWORD = 'password'

    PUBLIC_CLIENT_SECRET = 'xzZCaGRSa3F0MzpnWDFmQmF0M2JW'
    # ADMIN_USER = 'admin@elicit.com'

    ADMIN_USER = 'admin@elicit.com'
    ADMIN_PASSWORD = 'Daeph1eiGh7'

    def __init__(self,
                 _user=ADMIN_USER,
                 _password=ADMIN_PASSWORD,
                 _public_client_id=PUBLIC_CLIENT_ID,
                 _public_client_secret=PUBLIC_CLIENT_SECRET):
        """
        Initialize
        :param _admin_user: The (typically admin) user name
        :param _admin_password: The password
        :param _public_client_id: The OAuth Client ID
        :param _public_client_secret: The OAuth client secret
        :return: returns nothing
        """
        self.user = _user
        self.password = _password
        self.public_client_id = _public_client_id
        self.public_client_secret = _public_client_secret

    @classmethod
    def from_env(cls, config):
        pprint.pprint(config)
        pprint.pprint(cls)
        return cls(config['user'], config['password'], config['client_id'], config['client_secret'])


