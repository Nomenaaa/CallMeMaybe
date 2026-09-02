#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   generate_functions.py                                :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/21 09:56:49 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/02 15:55:06 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from constraint_class import Constraint, StringDFA, NumberDFA, Trie
from typing import Any
from llm_sdk import Small_LLM_Model
from vocab import get_vocab, get_first_char_to_ids, get_id_to_str
import numpy as np


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
    ) -> list[list[int], list[int]]:
    trie = Trie()
    for option in list(options.keys()):
        trie.insert(option)

    name_ids: list[list[int], list[int]] = []
    gen_ids: list[int] = model.encode('{"name": "').tolist()[0]
    prompt_ids.extend(gen_ids)

    func_name_ids = constraint_decoder(trie, prompt_ids, model)
    name_ids.append(func_name_ids)
    gen_ids.extend(func_name_ids)
    name_ids.append(gen_ids)

    return name_ids


def generate_parameters(
        parameters: dict[str, Any],
        prompt_ids: str,
        model: Small_LLM_Model
    ) -> list[int]:

    number_dfa = NumberDFA(["IN_FRACTION"])
    string_dfa = StringDFA(["END"])

    gen_ids : list[int] = model.encode('", "parameters": {').tolist()[0]
    prompt_ids.extend(gen_ids)
    for i, (key, value) in enumerate(parameters.items()):
        key_ids = model.encode(f'"{key}":').tolist()[0]
        gen_ids.extend(key_ids)
        prompt_ids.extend(key_ids)

        if value["type"] == "string":
            quote_ids = model.encode('"').tolist()[0]
            gen_ids.extend(quote_ids)
            prompt_ids.extend(quote_ids)
            value_ids = constraint_decoder(string_dfa, prompt_ids, model)
            gen_ids.extend(value_ids)
            prompt_ids.extend(value_ids)

        if value["type"] == "number":
            value_ids = constraint_decoder(number_dfa, prompt_ids, model)
            gen_ids.extend(value_ids)
            prompt_ids.extend(value_ids)

        if i < len(parameters) - 1:
            sep_ids = model.encode(', ').tolist()[0]
            gen_ids.extend(sep_ids)
            prompt_ids.extend(sep_ids)

    gen_ids.extend(model.encode('}}').tolist()[0])
    return gen_ids


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
    # ex_output = '{"name": "fn_add_numbers", "parameters": {"a": 2.0, "b": 3.0}}'
    # llm_prompt = (
    #     "You are a function-calling assistant. Given the user request below, "
    #     "determine which function should be called and what argument values to use. "
    #     "Use ONLY information explicitly stated in the request — do not infer or guess "
    #     "missing values.\n\n"
    #     f"Available functions:\n{function_catalog}\n\n"
    #     f"User request: {prompt}\n"
    # )
    # llm_prompt = (
    #     "/no_think\n"
    #     "You are a precise function selection assistant.\n"
    #     "Choose exactly one tool from the list below to fulfill"
    #     "the user request.\n"
    #     "Respond or complete ONLY with a VALID raw JSON string.\n"
    #     "NO identations of any type.\n\n"
    #     f"Available functions: {function_catalog}"
    #     f"User Prompt: {prompt}"
    #     "Response:"
    # )
    llm_prompt = (
        "Select the appropriate function from the available functions "
        "and extract its arguments from the user's request.\n"
        f"Available functions: {function_catalog}\n"
        f"User request: {prompt}"
        "Output:"
    )

    model: Small_LLM_Model = Small_LLM_Model()
    prompt_ids: list[int] = model.encode(llm_prompt).tolist()[0]

    name_ids : list[int] = generate_function_name(prompt_ids, options, model)
    function_name: str = model.decode(name_ids[0])
    prompt_ids.extend(name_ids[1])

    parameters:  dict[str, Any] = {}
    for func_def in valid_func_def:
        if func_def.get("name") == function_name:
            parameters = func_def.get("parameters")

    param_ids: list[int] = generate_parameters(parameters, prompt_ids, model)
    output_ids = name_ids[1] + param_ids

    return model.decode(output_ids)


# if __name__ == "__main__":
#     start = time.perf_counter()
#     valid_func_def = validate_function_def_file(os.getcwd() + "/data/input/functions_definition.json")
#     prompt = "Substitute the word 'cat' with 'dog' in 'The cat sat on the mat with another cat'"
#     print(generate_function(prompt, valid_func_def))
#     end = time.perf_counter()
#     print(f"Execution time: {end - start}")
