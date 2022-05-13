import uvicorn

from scripts.base import Argument, command_manager


@command_manager.add_command('runserver', arguments=[
    Argument(
        name_or_flags='--reload',
        action='store_true',
        help='Enable auto-reload'
    ),
    Argument(
        name_or_flags='--host',
        default='127.0.0.1',
        type=str,
        help='Host'
    ),
    Argument(
        name_or_flags='--port',
        default=8000,
        type=int,
        help='Port'
    )
])
def runserver(args):
    uvicorn.run('main:app', host=args.host, port=args.port, reload=args.reload)
