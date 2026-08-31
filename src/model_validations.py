#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   model_validations.py                                 :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/17 14:12:30 by nrasolom            #+#    #+#            #
#   Updated: 2026/08/31 14:26:22 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from pydantic import BaseModel
from typing import Literal, Any


class ParamType(BaseModel):
    type: Literal["number", "string"]


class PromptModel(BaseModel):
    prompt: str


class FunctionDefinitionModel(BaseModel):
    name: str
    description: str
    parameters: dict[str, ParamType]
    returns: ParamType


class OutputValidator(BaseModel):
    prompt: str
    name: str
    parameters: dict[str, Any]
