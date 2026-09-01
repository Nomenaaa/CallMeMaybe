#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   generate_functions.py                                :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/21 09:56:49 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/01 15:56:59 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from constraint_class import Constraint, StringDFA, NumberDFA, Trie
from typing import Any
from llm_sdk import Small_LLM_Model
from vocab import get_vocab, get_first_char_to_ids, get_id_to_str
import numpy as np
from load_inputs import validate_function_def_file
import os, time

def get_valid_tokens(
        constraint: Constraint, state: Any,
        first_char_to_ids: dict[str, list[int]],
        id_to_str: np.ndarray[tuple[int], np.dtype[np.object_]]
        ) -> dict[int, Any]:

    valid_tokens: dict[int, Any] = {}
    candidate_ids: list[int] = constraint.get_candidate_ids(
        state, first_char_to_ids)

    for token_id in candidate_ids:
        token_str = id_to_str[token_id]
        next_state = constraint.simulate_from(state, token_str)
        if next_state is not None:
            valid_tokens[token_id] = next_state

    return valid_tokens


def constraint_decoder(
        constraint: Constraint,
        prompt_ids: list[int],
        model: Small_LLM_Model
    ) -> list[int]:

    state: Any = constraint.get_start_state()
    vocab_dict: dict[str, int] = get_vocab(model)
    first_char_to_ids: dict[str, list[int]] = get_first_char_to_ids(vocab_dict)
    id_to_str = get_id_to_str(vocab_dict, model)

    generated_ids: list[int] = []
    while not constraint.is_accepted(state):
        if state in constraint._cache:
            valid_tokens = constraint._cache[state]
        else:
            valid_tokens = get_valid_tokens(
                constraint, state, first_char_to_ids, id_to_str)
            constraint._cache[state] = valid_tokens

        logits = model.get_logits_from_input_ids(prompt_ids)
        for token_id in range(len(logits)):
            if token_id not in valid_tokens:
                logits[token_id] = float("-inf")

        next_token = logits.index(max(logits))
        prompt_ids.append(next_token)
        generated_ids.append(next_token)
        state = valid_tokens[next_token]

    return generated_ids


def generate_function_name(
        prompt_ids: list[int],
        options: dict[str, str],
        model: Small_LLM_Model
    ) -> list[int]:
    trie = Trie()
    for option in list(options.keys()):
        trie.insert(option)
    trie.insert("None")

    return constraint_decoder(trie, prompt_ids, model)


# def generate_string(
#         prompt_ids: list[int],
#         model: Small_LLM_Model
#     ) -> list[int]:
#     string_dfa = StringDFA(["END"])

#     return constraint_decoder(string_dfa, prompt_ids, model)


# def generate_number(
#         prompt_ids: list[int],
#         model: Small_LLM_Model) -> str:
#     number_dfa = NumberDFA(["IN_FRACTION"])

#     return constraint_decoder(number_dfa, prompt_ids, model)


# def generate_parameters(
#         parameters: dict[str, Any], prompt_ids: str
#     ) -> str:

#     return ""


def generate_function(
        prompt: str, valid_func_def: list[Any]
    ) -> str:

    options: dict[str, str] = {}
    for func_def in valid_func_def:
        options[func_def.get("name")] = func_def.get("description")

    function_catalog: str = "\n".join(
            [f"- {name}: {desc}"
             for name, desc in options.items()]
    )
    ex_output = '{"name": "fn_add_numbers","parameters": {"a": 2.0, "b": 3.5}}'
    llm_prompt = (
        "Select the appropriate function from the available functions "
        "and extract its arguments from the user's query."
        f"Avalaible functions: {function_catalog}"
        "Example: "
        "User query: What is the sum of 2 and 3?"
        f"Output: {ex_output}"
        f"User query: {prompt}"
        "Output: "
    )

    model: Small_LLM_Model = Small_LLM_Model()
    prompt_ids: list[int] = model.encode(llm_prompt).tolist()[0]

    gen_output: str = '{"name": '
    gen_ids: list[int] = model.encode(gen_output).tolist()[0]
    prompt_ids.append(gen_ids)

    gen_ids += generate_function_name(prompt_ids, options, model)
    gen_output: str = model.decode(gen_ids)

    return gen_output


if __name__ == "__main__":
    start = time.perf_counter()
    valid_func_def = validate_function_def_file(os.getcwd() + "/data/input/functions_definition.json")
    prompt = "Replace all numbers in \"Hello 34 I'm 233 years old\" with NUMBERS"
    print(generate_function(prompt, valid_func_def))
    end = time.perf_counter()
    print(f"Execution time: {end - start}")
