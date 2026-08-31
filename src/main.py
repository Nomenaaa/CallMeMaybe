#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   main.py                                              :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/29 06:17:07 by nrasolom            #+#    #+#            #
#   Updated: 2026/08/29 06:33:54 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from generate_functions import generate_function
from load_inputs import validate_prompt_file, validate_function_def_file
from typing import Any
# from model_validations import OutputValidator
import os


def main() -> None:
    function_defs: list[dict[str, Any]] = []
    input_path = os.getcwd() + "/data/input/functions_definition.json"
    prompts: list[str] = validate_prompt_file(input_path)
    valid_func_def: list[Any] = validate_function_def_file(input_path)

    for prompt in prompts:
        function_defs.append(generate_function(prompt, valid_func_def))
