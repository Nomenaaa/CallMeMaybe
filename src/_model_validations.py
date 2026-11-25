#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   _model_validations.py                                :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/17 14:12:30 by nrasolom            #+#    #+#            #
#   Updated: 2026/10/15 08:23:04 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Any


class ParamType(BaseModel):
    """Schema describing a supported parameter type.

    Attributes:
        type: The parameter type accepted by the model.
    """

    model_config = ConfigDict(extra='forbid')
    type: Literal["number", "string", "integer", "float", "boolean"]


class PromptModel(BaseModel):
    """Validation model for a user prompt entry.

    Attributes:
        prompt: The prompt text to validate.
    """

    model_config = ConfigDict(extra='forbid')
    prompt: str = Field(...)


class FunctionDefinitionModel(BaseModel):
    """Validation model for a function definition record.

    Attributes:
        name: Name of the function.
        description: Human-readable description of the function.
        parameters: Structured parameters accepted by the function.
        returns: Return type declared by the function.
    """

    model_config = ConfigDict(extra='forbid')
    name: str = Field(...)
    description: str = Field(...)
    parameters: dict[str, ParamType] | None
    returns: ParamType


class OutputValidator(BaseModel):
    """Validation model for a generated function-call result.

    Attributes:
        prompt: Prompt associated with the generated payload.
        name: Name of the selected function.
        parameters: Generated arguments passed to the function.
    """

    prompt: str = Field(...)
    name: str | None
    parameters: dict[str, Any] | None


class PromptError(Exception):
    """Raised when a prompt input cannot be loaded or validated."""

    pass


class FunctionDefError(Exception):
    """Raised when a function-definition file fails validation."""

    pass


class FunctionCallError(Exception):
    """Raised when a generated function call fails validation or decoding."""

    pass
