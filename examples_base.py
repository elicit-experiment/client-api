import argparse
import socket

# grab the address using socket.getaddrinfo
answers = socket.getaddrinfo('elicit-experiment.com', 443)
ip4_answers = list(filter(lambda x: x[0] == socket.AF_INET, answers))

# print(answers)
# print(answers[0])
(family, type, proto, canonname, (prod_ip_address, port)) = ip4_answers[0]
#(family, type, proto, canonname, (prod_ip_address, port, x, y)) = answers[0]


ENVIRONMENTS = {
    'local': 'http://localhost:3000',
    'local_docker': 'http://elicit.docker.local',
    'prodx': 'http://142.93.48.58',
    'prod': "https://elicit-experiment.com"
    #    'prod': "https://%s"%(str(prod_ip_address))
}
parser = argparse.ArgumentParser(prog='elicit')
parser.add_argument('--env', choices=ENVIRONMENTS.keys(), default='prod',
                    help='Service environment to communicate with')
parser.add_argument('--apiurl', type=str, default=None)
parser.add_argument('--ignore_https', action='store_true', default=False)
parser.add_argument('--debug', action='store_true', default=False)

parser.add_argument('--role', type=str, default='admin')
parser.add_argument('--username', type=str, default=None)
parser.add_argument('--password', type=str, default=None)
parser.add_argument('--client_id', type=str, default='')
parser.add_argument('--client_secret', type=str, default=None)

def get_parser():
    return parser

def parse_command_line_args():
    args = parser.parse_args()

    if args.apiurl is None:
        args.apiurl = ENVIRONMENTS[args.env]

    if args.apiurl.startswith('http://'):
        args.ignore_https = True

    #{k: args[k] for k in set(args).intersection(['username', 'password', 'role', 'client_id', 'client_secret'])}

    args.send_opt = dict(verify=(not args.ignore_https))

    return args
