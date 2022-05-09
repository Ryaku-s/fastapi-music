import argparse

from scripts.runserver import runserver

command_parser = argparse.ArgumentParser(description='Manages commands')
subparsers = command_parser.add_subparsers(
    title='commands',
    description='Management commands',
    dest='command',
    required=True
)

runserver_parser = subparsers.add_parser(
    'runserver',
    description='Runs a server'
)
runserver_parser.add_argument(
    '--reload',
    action='store_true',
    help='Enable auto-reload'
)
runserver_parser.add_argument(
    '--host',
    default='127.0.0.1',
    type=str,
    help='Host'
)
runserver_parser.add_argument(
    '--port',
    default=8000,
    type=int,
    help='Port'
)
runserver_parser.set_defaults(func=runserver)
