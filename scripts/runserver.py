import uvicorn

from scripts.base import Argument, CommandManager

runserver_manager = CommandManager()


@runserver_manager.add_command(
    'runserver',
    description='Runs a server',
    arguments=[
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
    ]
)
def runserver(
    *,
    host: str | None = None,
    port: int | None = None,
    reload: bool | None = None
) -> None:
    uvicorn.run('main:app', host=host, port=port, reload=reload)
