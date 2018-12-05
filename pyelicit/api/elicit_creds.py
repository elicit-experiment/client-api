class ElicitCreds:
    """
    Class defining credentials to communicate with the Elicit service
    """
    PUBLIC_CLIENT_ID = 'admin_public'
    PUBLIC_CLIENT_SECRET = 'czZCaGRSa3F0MzpnWDFmQmF0M2JW'
    ADMIN_USER = 'admin@elicit.dk'
    ADMIN_PASSWORD = 'password'

    def __init__(self,
                 _admin_user=ADMIN_USER,
                 _admin_password=ADMIN_PASSWORD,
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
        self.admin_user = _admin_user
        self.admin_password = _admin_password
        self.public_client_id = _public_client_id
        self.public_client_secret = _public_client_secret
