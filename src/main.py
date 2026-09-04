#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   main.py                                              :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/29 06:17:07 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/04 15:17:17 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from load_inputs import validate_prompt_file, validate_function_def_file
from constraint_class import Trie, StringDFA, NumberDFA
from generate_functions import generate_function
from pydantic import ValidationError
from llm_sdk import Small_LLM_Model
from typing import Any
from model_validations import (OutputValidator, FunctionCallError,
                               FunctionDefError, PromptError)
import os
import json


def main() -> None:
    func_path = os.getcwd() + "/data/input/functions_definition.json"
    valid_func_def: list[Any] = validate_function_def_file(func_path)
    if (len(valid_func_def) == 0):
        raise FunctionDefError(
            "Validation Error: no function definition found!")

    prompt_path = os.getcwd() + "/data/input/function_calling_tests.json"
    prompts: list[str] = validate_prompt_file(prompt_path)
    if (len(prompts) == 0):
        raise PromptError("Validation Errror: no prompt found!")

    model = Small_LLM_Model()
    trie = Trie()
    for func_def in valid_func_def:
        trie.insert(func_def.get("name"))

    string_dfa = StringDFA(["END"])
    number_dfa = NumberDFA(["IN_FRACTION"])

    for prompt in prompts:
        func_call: dict[str, Any] = {"prompt": prompt}
        output_dict = generate_function(prompt, valid_func_def, model,
                                        number_dfa, string_dfa, trie)
        func_call.update(output_dict)
        try:
            OutputValidator.model_validate(func_call)
            print(json.dumps(func_call, indent=4))
        except ValidationError as e:
            for dict_error in e.errors():
                raise FunctionCallError(
                    f"Validation Error: {dict_error.get('msg')}")
