#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   generate_functions.py                                :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/21 09:56:49 by nrasolom            #+#    #+#            #
#   Updated: 2026/08/29 06:36:01 by nrasolom           ###   ########.fr      #
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


def constraint_decoder(constraint: Constraint, prompt: str) -> str:
    state = constraint.get_start_state()
    model = Small_LLM_Model()
    vocab_dict = get_vocab(model)
    first_char_to_ids = get_first_char_to_ids(vocab_dict)
    id_to_str = get_id_to_str(vocab_dict, model)
    input_ids: list = model.encode(prompt).tolist()[0]

    generated_ids = []
    while not constraint.is_accepted(state):
        if state in constraint._cache:
            valid_tokens = constraint._cache[state]
        else:
            valid_tokens = get_valid_tokens(
                constraint, state, first_char_to_ids, id_to_str)
            constraint._cache[state] = valid_tokens

        logits = model.get_logits_from_input_ids(input_ids)
        for token_id in range(len(logits)):
            if token_id not in valid_tokens:
                logits[token_id] = float("-inf")

        next_token = logits.index(max(logits))
        input_ids.append(next_token)
        generated_ids.append(next_token)
        state = valid_tokens[next_token]

    return model.decode(generated_ids)


def generate_function_name(prompt: str, options: list[str]) -> str:
    trie = Trie()
    for option in options:
        trie.insert(option)

    return constraint_decoder(trie, prompt)


def generate_string(prompt: str) -> str:
    string_dfa = StringDFA(["END"])

    return constraint_decoder(string_dfa, prompt)


def generate_number(prompt: str) -> str:
    number_dfa = NumberDFA(["END"])

    return constraint_decoder(number_dfa, prompt)


def generate_parameters(
        function_name: str, parameters: dict[str, Any]
) -> dict[str, Any]:
    prompt = ""
    paramaters_gen: dict[str, Any] = {}

    for key, value in parameters.items():
        if value == "string":
            paramaters_gen[key] = generate_string(prompt)
        if value == "number" or value == "integer":
            paramaters_gen[key] = generate_number(prompt)

    return paramaters_gen


def generate_function(
        prompt: str, valid_func_def: list[Any]
) -> dict[str, Any]:
    function: dict[str, Any] = {}
    options: list[str] = []

    for func_def in valid_func_def:
        options.append(func_def.get("name", ""))

    prompt_gen = ""
    function_name = generate_function_name(prompt_gen, options)
    function["name"] = function_name

    parameters_model: dict[str, Any] = {}
    for func_def in valid_func_def:
        if func_def.get("name") == function_name:
            parameters_model = func_def.get("parameters")

    function["parameters"] = generate_parameters(function_name,
                                                 parameters_model)

    return function
