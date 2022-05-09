import inspect
from typing import Callable, Type

from pydantic import BaseModel
from fastapi import Form, File, UploadFile


def model_form_factory(model: Type[BaseModel]) -> Callable[..., BaseModel]:
    new_params = []
    for model_field in model.__fields__.values():
        if model_field.outer_type_ == UploadFile:
            default = File(
                ... if model_field.required else model_field.default
            )
        else:
            default = Form(
                ... if model_field.required else model_field.default
            )
        param = inspect.Parameter(
            model_field.name,
            inspect.Parameter.POSITIONAL_ONLY,
            default=default,
            annotation=model_field.outer_type_
        )
        new_params.append(param)

    def model_form(**kwargs):
        return model(**kwargs)

    sig = inspect.signature(model_form)
    sig = sig.replace(parameters=new_params)
    model_form.__signature__ = sig
    return model_form
