#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   generate_functions.py                                :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/21 09:56:49 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/07 10:49:20 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from constraint_class import Constraint, StringDFA, NumberDFA, Trie
from typing import Any
from llm_sdk import Small_LLM_Model
from vocab import get_vocab, get_first_char_to_ids
from json import JSONDecodeError, loads
from model_validations import FunctionCallError


def get_valid_tokens(
        constraint: Constraint, state: Any,
        first_char_to_ids: dict[str, list[int]],
        model: Small_LLM_Model) -> dict[int, Any]:

    valid_tokens: dict[int, Any] = {}
    candidate_ids: list[int] = constraint.get_candidate_ids(
        state, first_char_to_ids)

    for token_id in candidate_ids:
        token_str = model.decode(token_id)
        next_state = constraint.simulate_from(state, token_str)
        if next_state is not None:
            valid_tokens[token_id] = next_state

    return valid_tokens


def constraint_decoder(
        constraint: Constraint,
        prompt_ids: list[int],
        model: Small_LLM_Model) -> list[int]:

    state: Any = constraint.get_start_state()
    vocab_dict: dict[str, int] = get_vocab(model)
    first_char_to_ids: dict[str, list[int]] = get_first_char_to_ids(vocab_dict)

    MAX_GENERATED_TOKENS = 200
    generated_ids: list[int] = []
    while not constraint.is_accepted(state):
        if (len(generated_ids) > MAX_GENERATED_TOKENS):
            raise RuntimeError("Generation exceeds safety limit. "
                               "Model start hallucinating...")
        if state in constraint._cache:
            valid_tokens = constraint._cache[state]
        else:
            valid_tokens = get_valid_tokens(
                constraint, state, first_char_to_ids, model)
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
        model: Small_LLM_Model,
        trie: Trie) -> list[list[int]]:

    name_ids: list[list[int]] = []
    gen_ids: list[int] = model.encode('{"name": "').tolist()[0]
    prompt_ids.extend(gen_ids)

    func_name_ids = constraint_decoder(trie, prompt_ids, model)
    name_ids.append(func_name_ids)
    gen_ids.extend(func_name_ids)
    name_ids.append(gen_ids)

    return name_ids


def generate_parameters(
        parameters: dict[str, Any] | None,
        prompt_ids: list[int],
        model: Small_LLM_Model,
        number_dfa: NumberDFA,
        string_dfa: StringDFA) -> list[int]:

    if parameters is None:
        gen_ids: list[int] = model.encode('", "parameters": null}').tolist()[0]
        return gen_ids

    gen_ids = model.encode('", "parameters": {').tolist()[0]
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
        prompt: str,
        valid_func_def: list[Any],
        model: Small_LLM_Model,
        number_dfa: NumberDFA,
        string_dfa: StringDFA,
        trie: Trie) -> dict[str, Any]:

    options: dict[str, str] = {}
    for func_def in valid_func_def:
        options[func_def.get("name")] = func_def.get("description")

    function_catalog: str = "\n".join(
            [f"- {name}: {desc}"
             for name, desc in options.items()]
    )

    # llm_prompt = (
    #     "Select the appropriate function from the available functions "
    #     "and extract its arguments from the user's request.\n"
    #     f"Available functions: {function_catalog}\n"
    #     f"User request: {prompt}"
    #     "Output:"
    # )

    llm_prompt = (
        "Select the appropriate function from the available functions "
        "and extract its arguments from the user's request.\n"
        f"Available functions: {function_catalog}\n"
        "Example:\n"
        'Request: Substitute the word "cat" with "dog" in "cat cat"\n'
        'Output: {"name":"fn_substitute_string_with_regex","parameters":'
        '{"source_string":"cat cat","regex":"cat","replacement":"dog"}}\n'
        "The regex must represent the pattern described by the user. "
        f"User request: {prompt}\n"
        "Output:"
    )

    prompt_ids: list[int] = model.encode(llm_prompt).tolist()[0]

    name_ids = generate_function_name(prompt_ids, model, trie)
    function_name: str = model.decode(name_ids[0])
    prompt_ids.extend(name_ids[1])

    for func_def in valid_func_def:
        if func_def.get("name") == function_name:
            parameters = func_def.get("parameters")

    try:
        param_ids = generate_parameters(parameters, prompt_ids, model,
                                        number_dfa, string_dfa)
    except RuntimeError as e:
        print(f"Generation stopped safely: {e}")
        param_ids = model.encode('", "parameters": null}').tolist()[0]

    output_str = model.decode(name_ids[1] + param_ids)
    try:
        output_dict: dict[str, Any] = loads(output_str)
        return output_dict
    except JSONDecodeError as e:
        raise FunctionCallError(f"Validation Error : {e.msg}")
