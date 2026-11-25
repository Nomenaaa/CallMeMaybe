#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/03 10:47:00 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/21 13:52:51 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Execution entry point of the program.

Usage:
src [-h] [--functions_definition FUNCTIONS_DEFINITION] [--input INPUT]
    [--output OUTPUT]

Flags:
  -h, --help            show this help message and exit
  --functions_definition FUNCTIONS_DEFINITION
                        path to get the functions definition JSON file
  --input INPUT         path to get the prompts JSON file to generate
  --output OUTPUT       path to write the function calls generated
"""

from ._model_validations import (PromptError, FunctionDefError,
                                 FunctionCallError)
from ._main import main, parser
import sys

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"

try:
    print()
    print("📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞")
    print("📞                                              📞")
    print(f"📞    {BLUE}   CALL ME MAYBE (?)  {RESET}                    📞")
    print("📞                                              📞")
    print("📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞📞")
    print()
    args = parser().parse_args()
    print(f"{YELLOW}Getting the prompts from {args.input} ...{RESET}")
    print(f"{YELLOW}Getting the function definitions from "
          f"{args.functions_definition} ...{RESET}")

    while True:
        choice = input(
            "Choose a model:\n"
            "(1) Qwen/Qwen3-0.6B (default)\n"
            "(2) Qwen/Qwen2.5-1.5B-Instruct\n"
            "Select 1 or 2 or 'p' to pass: ")
        if choice == "1" or choice == "p":
            print(f"{YELLOW}Loading Qwen3-0.6B... {RESET}")
            gen = main("Qwen/Qwen3-0.6B")
            break
        if choice == "2":
            print(f"{YELLOW}Loading Qwen2.5-1.5B-Instruct... {RESET}")
            gen = main("Qwen/Qwen2.5-1.5B-Instruct")
            break
        continue

    while True:
        try:
            prompt, func_call = next(gen)
        except StopIteration:
            print(f"{YELLOW}Successfully saved function calls "
                  f"to {args.output} {RESET}")
            break
        else:
            print(f"Input: {YELLOW}{prompt}{RESET}")
            print("Generating the function call...")
            print("Output:")
            print(f"{GREEN}{func_call}{RESET}")

except PromptError as e:
    print(f"{RED}[ERROR]: {e} {RESET}")
except FunctionDefError as e:
    print(f"{RED}[ERROR]: {e} {RESET}")
except FunctionCallError as e:
    print(f"{RED}[ERROR]: {e} {RESET}")
except KeyboardInterrupt:
    sys.exit(1)
