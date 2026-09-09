#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   load_inputs.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/17 13:55:12 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/09 13:23:04 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from json import load, JSONDecodeError
from model_validations import (PromptModel, FunctionDefinitionModel,
                               PromptError, FunctionDefError)
from pydantic import ValidationError
from typing import Any


RESET = "\033[0m"
RED = "\033[31m"


def validate_prompt_file(input_path: str) -> list[str]:
    valid_prompts: list[str] = []
    try:
        with open(input_path, 'r') as file_obj:
            prompts = load(file_obj)

        for item in prompts:
            try:
                PromptModel.model_validate(item)
                valid_prompts.append(item['prompt'])
            except ValidationError as e:
                for dict_error in e.errors():
                    print(f"{RED}Validation Error: {dict_error.get('msg')}"
                          f"{RESET}")
                print("Skipping the prompt...")
                continue

    except OSError as e:
        raise PromptError(f"Error on opening the file: {e}")
    except JSONDecodeError as e:
        raise PromptError(f"Invalid JSON: {e.msg}")

    return valid_prompts


def validate_function_def_file(input_path: str) -> list[Any]:
    valid_func_def: list[Any] = []
    try:
        with open(input_path, 'r') as file_obj:
            func_def = load(file_obj)

        for item in func_def:
            try:
                FunctionDefinitionModel.model_validate(item)
                valid_func_def.append(item)
            except ValidationError as e:
                for dict_error in e.errors():
                    print(f"{RED}Validation Error: {dict_error.get('msg')}"
                          f"{RESET}")
                print("Skipping the function definition ...")
                continue

    except OSError as e:
        raise FunctionDefError(f"Error on opening the file: {e}")
    except JSONDecodeError as e:
        raise FunctionDefError(f"Invalid JSON: {e.msg}")

    return valid_func_def
