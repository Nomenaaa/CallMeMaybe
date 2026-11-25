#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   _main.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/29 06:17:07 by nrasolom            #+#    #+#            #
#   Updated: 2026/10/15 07:57:27 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from ._load_inputs import validate_prompt_file, validate_function_def_file
from .constraint import Trie, StringDFA, NumberDFA
from ._generate_functions import generate_function
from pydantic import ValidationError
from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
from typing import Any
from argparse import ArgumentParser
from ._vocab import Vocab
from ._model_validations import (OutputValidator, FunctionCallError,
                                 FunctionDefError, PromptError)
from json import dump, dumps
from pathlib import Path
import typing


def parser() -> ArgumentParser:
    """Create and configure the CLI argument parser for the program.

    Returns:
        Configured parser for the CLI arguments.
    """
    arg_parser = ArgumentParser(
        prog="src",
        description="Program that generates function calls using a LLM"
    )

    arg_parser.add_argument(
        "--functions_definition",
        default=Path("data/input/functions_definition.json"),
        help="path to get the functions definition JSON file"
    )

    arg_parser.add_argument(
        "--input",
        default=Path("data/input/function_calling_tests.json"),
        help="path to get the prompts JSON file to generate the function calls"
    )

    arg_parser.add_argument(
        "--output",
        default="data/output/function_calling_results.json",
        help="path to write the function calls generated"
    )

    return arg_parser


def main(model_name: str) -> typing.Generator[tuple[str, str], None, None]:
    """Run the model over valid prompts and yield validated function calls.

    Yields:
        A prompt and its generated JSON function-call payload.

    Raises:
        FunctionDefError: If no valid function definitions are found.
        PromptError: If no valid prompts are found.
        FunctionCallError: If output validation fails.
    """
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

    model = Small_LLM_Model(model_name)
    vocab = Vocab(model)
    name_trie = Trie()
    for func_def in valid_func_def:
        name_trie.insert(func_def.get("name"))
    constraints["name_trie"] = name_trie

    constraints["string_dfa"] = StringDFA(["END"])
    constraints["integer_dfa"] = NumberDFA(["DOT"])
    constraints["number_dfa"] = NumberDFA(["END"])

    bool_trie = Trie()
    for boolean in ["true", "false"]:
        bool_trie.insert(boolean)
    constraints["bool_trie"] = bool_trie

    func_calls: list[dict[str, Any]] = []
    for prompt in prompts:
        func_call: dict[str, Any] = {"prompt": prompt}
        output_dict = generate_function(prompt, valid_func_def,
                                        model, constraints, vocab)
        func_call.update(output_dict)
        try:
            OutputValidator.model_validate(func_call)
            func_calls.append(func_call)
            yield ((prompt), (dumps(func_call, indent=4)))
        except ValidationError as e:
            for dict_error in e.errors():
                raise FunctionCallError(
                    f"Validation Error: {dict_error.get('msg')}")

        try:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            file_obj = open(args.output, 'w')
            dump(func_calls, file_obj, indent=2)
            file_obj.close()
        except OSError as e:
            raise FunctionCallError(e)
