from typing import Any, Callable, Iterable, Sequence, Type
from argparse import Action, ArgumentParser, HelpFormatter

from pydantic import BaseModel


class Argument(BaseModel):
    name_or_flags: str
    action: Type[Action] | str | None = None
    nargs: int | None = None
    const: Any = None
    default: Any = None
    type: Callable = None
    choices: Iterable[Any] | None = None
    required: bool | None = None
    help: str | None = None
    metavar: str | tuple[str, ...] | None = None
    dest: str | None = None
    version: str | None = None


class CommandManager(ArgumentParser):
    def __init__(
        self,
        prog: str | None = None,
        usage: str | None = None,
        description: str | None = None,
        epilog: str | None = None,
        parents: Sequence[ArgumentParser] = [],
        formatter_class = HelpFormatter,
        prefix_chars: str = '-',
        fromfile_prefix_chars: str | None = None,
        argument_default: Any = None,
        conflict_handler: str = 'error',
        add_help: bool = True,
        allow_abbrev: bool = True,
        exit_on_error: bool = True
    ) -> None:
        super().__init__(prog, usage, description, epilog, parents, formatter_class, prefix_chars, fromfile_prefix_chars, argument_default, conflict_handler, add_help, allow_abbrev, exit_on_error)
        self._commands = self.add_subparsers(
            title='commands',
            dest='command',
            parser_class=ArgumentParser,
            required=True
        )

    def add_command(self, name: str, arguments: Sequence[Argument], **kwargs) -> None:
        def mount(command: Callable):
            command_parser = self._commands.add_parser(name, **kwargs)

            for argument in arguments:
                argument_dict = argument.dict(exclude_none=True)
                name_or_flags = argument_dict.pop('name_or_flags')
                command_parser.add_argument(
                    name_or_flags,
                    **argument_dict
                )

            command_parser.set_defaults(func=command)
            return command
        return mount


command_manager = CommandManager()
