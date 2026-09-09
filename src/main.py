#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   main.py                                              :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/29 06:17:07 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/09 12:14:25 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from load_inputs import validate_prompt_file, validate_function_def_file
from constraint_class import Trie, StringDFA, NumberDFA
from generate_functions import generate_function
from pydantic import ValidationError
from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
from typing import Any
from argparse import ArgumentParser
from model_validations import (OutputValidator, FunctionCallError,
                               FunctionDefError, PromptError)
from json import dump, dumps
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
        default=os.getcwd() + "/data/input/function_calling_tests.json",
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
    valid_func_def: list[Any] = validate_function_def_file(func_path)
    if (len(valid_func_def) == 0):
        raise FunctionDefError(
            "Validation Error: no function definition found!")

    prompt_path: str = args.input
    prompts: list[str] = validate_prompt_file(prompt_path)
    if (len(prompts) == 0):
        raise PromptError("Validation Errror: no prompt found!")

    constraints: dict[str, Any] = {}

    model = Small_LLM_Model()
    name_trie = Trie()
    for func_def in valid_func_def:
        name_trie.insert(func_def.get("name"))
    constraints["name_trie"] = name_trie

    constraints["string_dfa"] = StringDFA(["END"])
    constraints["integer_dfa"] = NumberDFA(["DOT"])
    constraints["number_dfa"] = NumberDFA(["IN_FRACTION"])

    bool_trie = Trie()
    for boolean in ["true", "false"]:
        bool_trie.insert(boolean)
    constraints["bool_trie"] = bool_trie

    func_calls: list[dict[str, Any]] = []
    for prompt in prompts:
        func_call: dict[str, Any] = {"prompt": prompt}
        print("Generating function call...")
        output_dict = generate_function(prompt, valid_func_def,
                                        model, constraints)
        func_call.update(output_dict)
        try:
            OutputValidator.model_validate(func_call)
            func_calls.append(func_call)
            print(dumps(func_call, indent=4))
        except ValidationError as e:
            for dict_error in e.errors():
                raise FunctionCallError(
                    f"Validation Error: {dict_error.get('msg')}")

    try:
        file_obj = open(args.output, 'w')
        dump(func_calls, file_obj, indent=2)
        print(f"Successfully saved functions calls to {args.output}")
        file_obj.close()
    except OSError as e:
        raise FunctionCallError(e)
