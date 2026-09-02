#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   main.py                                              :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/29 06:17:07 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/02 15:35:00 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from generate_functions import generate_function
from load_inputs import validate_prompt_file, validate_function_def_file
from typing import Any
# from model_validations import OutputValidator
import os, time


def main() -> None:
    # function_defs: list[dict[str, Any]] = []
    func_path = os.getcwd() + "/data/input/functions_definition.json"
    prompt_path = os.getcwd() + "/data/input/function_calling_tests.json"
    prompts: list[str] = validate_prompt_file(prompt_path)
    valid_func_def: list[Any] = validate_function_def_file(func_path)

    for prompt in prompts:
        print(generate_function(prompt, valid_func_def))
        print()


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    end = time.perf_counter()
    print(f"Elapsed time: {end - start}")
