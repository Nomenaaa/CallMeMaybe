#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   _generate_functions.py                               :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/21 09:56:49 by nrasolom            #+#    #+#            #
#   Updated: 2026/10/19 09:24:25 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from .constraint import Constraint, NumberDFA, StringDFA
from typing import Any
from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
from ._vocab import Vocab
from json import JSONDecodeError, loads
from ._model_validations import FunctionCallError


def get_valid_tokens(
        constraint: Constraint,
        state: Any,
        vocab: Vocab) -> dict[int, Any]:
    """Return the valid next-token IDs and their resulting states.

    Args:
        constraint: The constraint automaton used to validate tokens.
        state: The current constraint state.
        vocab: model's vocabulary, providing token id/string
            lookups and decoding.

    Returns:
        Mapping from valid token IDs to the next state produced by
            consuming each token string.
    """
    valid_tokens: dict[int, Any] = {}
    candidate_ids: list[int] = constraint.get_candidate_ids(
        state, vocab.first_char_to_ids)

    for token_id in candidate_ids:
        token_str = vocab.decode(token_id)
        next_state = constraint.simulate_from(state, token_str)
        if next_state is not None:
            valid_tokens[token_id] = next_state

    return valid_tokens


def constraint_decoder(
        constraint: Constraint,
        prompt_ids: list[int],
        model: Small_LLM_Model,
        vocab: Vocab) -> list[int]:
    """Generate a valid token sequence while respecting the constraint.

    Args:
        constraint: The constraint automaton to enforce.
        prompt_ids: Token IDs already provided as context.
        model: The language model used to score token choices.
        vocab: model's vocabulary, providing token id/string
                lookups and decoding.

    Returns:
        Generated token IDs that satisfy the constraint.

    Raises:
        RuntimeError: if generated tokens exceed the MAX_GENERATED_TOKENS.
    """
    state: Any = constraint.get_start_state()

    if isinstance(constraint, NumberDFA):
        MAX_GENERATED_TOKENS = 50
    else:
        MAX_GENERATED_TOKENS = 100

    generated_ids: list[int] = []
    while not constraint.is_accepted(state):
        if (len(generated_ids) > MAX_GENERATED_TOKENS):
            print("Generation stopped safely: "
                  "Generation exceeds safety limit. "
                  "Model start hallucinating...")
            if isinstance(constraint, StringDFA):
                generated_ids.append(model.encode('"').tolist()[0])
            return generated_ids

        if state in constraint._cache:
            valid_tokens = constraint._cache[state]
        else:
            valid_tokens = get_valid_tokens(
                constraint, state, vocab)
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
        trie: Constraint,
        vocab: Vocab) -> list[list[int]]:
    """Generate the selected function name using the trie constraint.

    Args:
        prompt_ids: Token IDs already provided as context.
        model: The language model used for generation.
        trie: Trie constraint describing valid function names.
        vocab: model's vocabulary, providing token id/string
                lookups and decoding.

    Returns:
        A pair of token ID lists: the function name and the full
            generated list containing it.
    """
    name_ids: list[list[int]] = []
    gen_ids: list[int] = model.encode('{"name": "').tolist()[0]
    prompt_ids.extend(gen_ids)

    func_name_ids = constraint_decoder(trie, prompt_ids, model, vocab)
    name_ids.append(func_name_ids)
    gen_ids.extend(func_name_ids)
    name_ids.append(gen_ids)

    return name_ids


def generate_parameters(
        parameters: dict[str, Any] | None,
        prompt_ids: list[int],
        model: Small_LLM_Model,
        constraints: dict[str, Constraint],
        vocab: Vocab) -> list[int]:
    """Generate the JSON parameter block for the selected function definition.

    Args:
        parameters: Parameter schema for the selected function,
            or None if no parameters.
        prompt_ids: Token IDs already provided as context.
        model: The language model used for token generation.
        constraints: Mapping of constraint names to
            automata used to guide valid token generation.
        vocab: model's vocabulary, providing token id/string
            lookups and decoding.

    Returns:
        Generated token IDs for the JSON parameter block.
    """
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
            value_ids = constraint_decoder(constraints["string_dfa"],
                                           prompt_ids, model, vocab)
            gen_ids.extend(value_ids)
            prompt_ids.extend(value_ids)

        if value["type"] == "integer":
            value_ids = constraint_decoder(constraints["integer_dfa"],
                                           prompt_ids, model, vocab)
            gen_ids.extend(value_ids[:-1])
            prompt_ids.extend(value_ids[:-1])

        if value["type"] == "number" or value["type"] == "float":
            value_ids = constraint_decoder(constraints["number_dfa"],
                                           prompt_ids, model, vocab)
            gen_ids.extend(value_ids[:-1])
            prompt_ids.extend(value_ids[:-1])

        if value["type"] == "boolean":
            value_ids = constraint_decoder(constraints["bool_trie"],
                                           prompt_ids, model, vocab)
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
        constraints: dict[str, Constraint],
        vocab: Vocab) -> dict[str, Any]:
    """Generate a valid function-call dictionary from a user prompt.

    Args:
        prompt: User request to process.
        valid_func_def: Valid function definitions to choose from.
        model: The language model used for generation.
        constraints: Mapping of constraint names to
            automata used to guide valid token generation.
        vocab: model's vocabulary, providing token id/string
            lookups and decoding.

    Returns:
        Parsed function-call payload representing the output.

    Raises:
        FunctionCallError: If the generated output cannot be decoded into valid
            JSON.
    """
    options: dict[str, str] = {}
    for func_def in valid_func_def:
        options[func_def.get("name")] = func_def.get("description")

    function_catalog: str = "\n".join(
        [f"- {name}: {desc}"
         for name, desc in options.items()])

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

    name_ids = generate_function_name(prompt_ids, model,
                                      constraints["name_trie"], vocab)
    function_name = ""
    for token_id in name_ids[0]:
        function_name += vocab.decode(token_id)
    prompt_ids.extend(name_ids[1])

    for func_def in valid_func_def:
        if func_def.get("name") == function_name:
            parameters = func_def.get("parameters")

    param_ids = generate_parameters(parameters, prompt_ids, model,
                                    constraints, vocab)

    output_str = ""
    for token_id in (name_ids[1] + param_ids):
        output_str += vocab.decode(token_id)
    try:
        output_dict: dict[str, Any] = loads(output_str)
        return output_dict
    except JSONDecodeError as e:
        raise FunctionCallError(f"Validation Error : {e.msg}")
