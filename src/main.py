#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   main.py                                              :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 16:02:17 by nrasolom            #+#    #+#            #
#   Updated: 2026/08/18 16:22:05 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from typing import Any
import json


def generate_function_call(prompt: str, functions: list[Any]
) -> dict[str, Any]:
    output_str = "{"
    output_str += prompt

    output_str += ", 'name': '"
    function_name = generate_enum(prompt, functions)
    output_str += function_name

    output_str += "', 'parameters': "
    chosen_function = [item for item in functions
                       if item.get('name') == function_name]
    param_schema = chosen_function[0].get('parameters')
    output_str += generate_object(prompt, param_schema)

    output_str += "}"

    return json.loads(output_str)
