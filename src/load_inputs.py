#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   load_inputs.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/17 13:55:12 by nrasolom            #+#    #+#            #
#   Updated: 2026/08/17 15:20:10 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from json import load, JSONDecodeError
from model_validations import PromptModel
from pydantic import ValidationError


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


# if __name__ == "__main__":
#     input_path = os.getcwd() + "/data/input/function_calling_tests.json"
#     print(validate_prompt_file(input_path))
