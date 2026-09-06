#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   main.py                                              :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/29 06:17:07 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/06 20:10:31 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from load_inputs import validate_prompt_file, validate_function_def_file
from constraint_class import Trie, StringDFA, NumberDFA
from generate_functions import generate_function
from pydantic import ValidationError
from llm_sdk import Small_LLM_Model
from typing import Any
from argparse import ArgumentParser
from model_validations import (OutputValidator, FunctionCallError,
                               FunctionDefError, PromptError)
import json
import os


def parser() -> ArgumentParser:
    arg_parser = ArgumentParser(
        prog="src",
        description="Program that generates function calls using a LLM"
    )

    arg_parser.add_argument(
        "--functions_definition",
        default=os.getcwd() + "/data/input/functions_definition.json",
        help="path to get the functions definition JSON file"
    )

    arg_parser.add_argument(
        "--input",
        default=os.getcwd() + "/data/input/function_calling_test.json",
        help="path to get the prompts JSON file to generate the function calls"
    )

    arg_parser.add_argument(
        "--output",
        default=os.getcwd() + "/data/output/function_calls.json",
        help="path to write the function calls generated"
    )

    return arg_parser


def main() -> None:
    args = parser().parse_args()

    func_path: str = args.functions_definition
    print(func_path)
    valid_func_def: list[Any] = validate_function_def_file(func_path)
    if (len(valid_func_def) == 0):
        raise FunctionDefError(
            "Validation Error: no function definition found!")

    prompt_path: str = args.input
    print(prompt_path)
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
