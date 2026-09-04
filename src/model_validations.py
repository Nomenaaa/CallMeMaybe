#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   model_validations.py                                 :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/17 14:12:30 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/04 12:12:51 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from pydantic import BaseModel, Field
from typing import Literal, Any


class ParamType(BaseModel):
    type: Literal["number", "string"]


class PromptModel(BaseModel):
    prompt: str = Field(..., min_length=5)


class FunctionDefinitionModel(BaseModel):
    name: str = Field(..., min_length=5)
    description: str = Field(..., min_length=15)
    parameters: dict[str, ParamType] | None
    returns: ParamType


class OutputValidator(BaseModel):
    prompt: str = Field(..., min_length=5)
    name: str = Field(..., min_length=5)
    parameters: dict[str, Any] | None


class PromptError(Exception):
    pass


class FunctionDefError(Exception):
    pass


class FunctionCallError(Exception):
    pass
