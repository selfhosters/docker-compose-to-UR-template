import argparse
from Converter import Generator, ReadYAML, run


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


parser = argparse.ArgumentParser(description='WIP CLI for compose>template',)

li_ = []
services = ReadYAML().services

service = ""

msg = """Please choose from this list:"""
for i in services:
    it = i + 1
    msg += "\n" + str(it) + ": " + str(services[i])
    li_.append(it)

parser.add_argument('-s', '--service', choices=li_, type=int,
                    help='list servers, storage, or both (default: %(default)s)')

parser.add_argument('-a', '--automated', action='store_true', help="Generates files from best-guess")
parser.add_argument('-m', '--manual', action='store_true', help="To escape entrypoint imn docker")

parser.add_argument('-t', '--templateurl', help="Sets Template URL")
parser.add_argument('-n', '--name', help="Sets Name")
parser.add_argument('-g', '--repository', help="Sets Repository")
parser.add_argument('-r', '--registry', help="Sets Registry")
parser.add_argument('-u', '--project', help="Sets Project")
parser.add_argument('-i', '--icon', help="Sets Icon URL")
parser.add_argument('-b', '--bindtime', help="Sets Bindtime", type=str2bool)
parser.add_argument('-p', '--privileged', help="Sets Privileged")
parser.add_argument('-o', '--overview', help="Sets Overview")
parser.add_argument('-d', '--description', help="Sets Description")

args = parser.parse_args()

meta_kwargs = {}

if args.description:
    meta_kwargs["description"] = args.description

if args.name:
    meta_kwargs["name"] = args.name

if args.repository:
    meta_kwargs["repository"] = args.repository

if args.registry:
    meta_kwargs["registry"] = args.registry

if args.project:
    meta_kwargs["project"] = args.project

if args.icon:
    meta_kwargs["icon"] = args.icon

if args.bindtime:
    meta_kwargs["bindtime"] = args.bindtime

if args.privileged:
    meta_kwargs["privileged"] = args.privileged

if args.overview:
    meta_kwargs["overview"] = args.overview

if args.automated:
    run()

elif args.manual:
    print(msg)

elif not args.service:
    print(msg)

if args.service:
    service = services[args.service - 1]
    elm = Generator(service)
    elm.metadata(**meta_kwargs)
    elm.variable()
    elm.network()
    elm.data()
    elm.write()
