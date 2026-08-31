#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   generate_functions.py                                :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/21 09:56:49 by nrasolom            #+#    #+#            #
#   Updated: 2026/08/31 14:40:19 by nrasolom           ###   ########.fr      #
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


def generate_function_name(prompt: str, options: dict[str, str]) -> str:
    trie = Trie()
    for option in list(options.keys()):
        trie.insert(option)
    trie.insert("None")

    function_catalog: str = "\n".join(
        [f"- {name}: {desc}" for name, desc in options.items()]
    )
    llm_prompt = (
        f"<|im_start|>system\n/no_think\n"
        "You are a strict router. Choose exactly ONE option from this list: "
        f"{list(options.keys())}. Use the descriptions bellow to help choose "
        f"the correct name: {function_catalog}."
        "If no option matches correctly, you MUST return 'None'."
        "\n<|im_end|>\n"
        f"<|im_start|>user\nQuery to match: {prompt}\n<|im_end|>\n"
        "<|im_start|>assistant\n"
    )

    return constraint_decoder(trie, llm_prompt)


def generate_string(
        function_name: str,
        prompt: str,
        param_outputs: dict[str, Any]) -> str:
    string_dfa = StringDFA(["END"])
    param_generated: list[Any] = list(param_outputs.values())
    llm_prompt = (
        "<|im_start|>system\n/no_think\n"
        f"You are a strict data extractor for the function '{function_name}'. "
        "Extract exactly ONE parameter value from the user query. "
        "Do NOT select any parameter that is already present in this list: "
        f"{param_generated}. Output ONLY the extracted text wrapped in double "
        "quotes, for example: \"value\".\n"
        "<|im_end|>\n"
        f"<|im_start|>user\nQuery to match: {prompt}\n<|im_end|>\n"
        "<|im_start|>assistant\n"
    )

    return constraint_decoder(string_dfa, llm_prompt)


def generate_number(
        function_name: str,
        prompt: str,
        param_outputs: dict[str, Any]
     ) -> str:
    number_dfa = NumberDFA(["IN_FRACTION"])
    param_generated: list[Any] = list(param_outputs.values())
    llm_prompt = (
        "<|im_start|>system\n/no_think\n"
        f"You are a strict data extractor for the function '{function_name}'. "
        "Extract exactly ONE numerical value from the query and format it "
        "strictly as a float number with a decimal point (e.g., 5 becomes 5.0,"
        " 3.14 remains 3.14). Do NOT select any parameter that is present "
        f"in this list: {param_generated}. Output ONLY the raw float number.\n"
        "<|im_end|>\n"
        f"<|im_start|>user\nQuery to match: {prompt}\n<|im_end|>\n"
        "<|im_start|>assistant\n"
    )

    return constraint_decoder(number_dfa, llm_prompt)


def generate_parameters(
        function_name: str, parameters: dict[str, Any], prompt: str
) -> dict[str, Any]:

    param_outputs: dict[str, Any] = {}

    for key, value in parameters.items():
        if value["type"] == "string":
            param_outputs[key] = generate_string(function_name,
                                                 prompt,
                                                 param_outputs)
        if value["type"] == "number":
            param_outputs[key] = generate_number(function_name,
                                                 prompt,
                                                 param_outputs)

    return param_outputs


def generate_function(
        prompt: str, valid_func_def: list[Any]
) -> dict[str, Any]:
    function_output: dict[str, Any] = {}
    options: dict[str, str] = []

    for func_def in valid_func_def:
        options[func_def.get("name")] = func_def["description"]

    function_name = generate_function_name(prompt, options)
    function_output["name"] = function_name

    parameters_model: dict[str, Any] = {}
    for func_def in valid_func_def:
        if func_def.get("name") == function_name:
            parameters_model = func_def.get("parameters")

    function_output["parameters"] = generate_parameters(function_name,
                                                        parameters_model,
                                                        prompt)

    return function_output
