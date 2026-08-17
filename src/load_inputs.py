#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   load_inputs.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/17 13:55:12 by nrasolom            #+#    #+#            #
#   Updated: 2026/08/17 15:50:44 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from json import load, JSONDecodeError
from model_validations import PromptModel, FunctionDefinitionModel
from pydantic import ValidationError
from typing import Any
import os


def validate_prompt_file(input_path: str) -> list[str]:
    try:
        with open(input_path, 'r') as file_obj:
            prompts = load(file_obj)
    
        valid_prompts: list[str] = []
        for item in prompts:
            try:
                PromptModel.model_validate(item)
                valid_prompts.append(item['prompt'])
            except ValidationError as e:
                for dict_error in e.errors():
                    print(f"Validation Error: {dict_error.get('msg')}")
                print("Skipping...")
                continue

        return valid_prompts

    except OSError as e:
        print(f"Error on opening the file: {e}")
    except JSONDecodeError as e:
        print(f"Invalid JSON: {e.msg}")


def validate_function_def_file(input_path: str) -> list[Any]:
    try:
        with open(input_path, 'r') as file_obj:
            func_def = load(file_obj)

        valid_func_def: list[Any] = []
        for item in func_def:
            try:
                FunctionDefinitionModel.model_validate(item)
                valid_func_def.append(item)
            except ValidationError as e:
                for dict_error in e.errors():
                    print(f"Validation Error: {dict_error.get('msg')}")
                print("Skipping...")
                continue

        return valid_func_def

    except OSError as e:
        print(f"Error on opening the file: {e}")
    except JSONDecodeError as e:
        print(f"Invalid JSON: {e.msg}")


# if __name__ == "__main__":
#     input_path = os.getcwd() + "/data/input/functions_definition.json"
#     print(validate_function_def_file(input_path))
