#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   vocab.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 11:26:49 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/10 18:13:08 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
from collections import defaultdict
import json


def get_vocab(model: Small_LLM_Model) -> dict[str, int]:
    """Load the tokenizer vocabulary associated with the model.

    Args:
        model: The language model instance to load the vocabulary file.

    Returns:
        Mapping from vocabulary strings to token IDs.
    """
    with open(model.get_path_to_vocab_file(), 'r') as file:
        vocab_dict: dict[str, int] = json.load(file)

    return vocab_dict


def get_first_char_to_ids(vocab_dict: dict[str, int]) -> dict[str, list[int]]:
    """Group token IDs by the first character of each vocabulary string.

    Args:
        vocab_dict: Mapping from vocabulary strings to token IDs.

    Returns:
        Mapping from each leading character to the token IDs
            whose strings start with it.
    """
    group: defaultdict[str, list[int]] = defaultdict(list)

    for vocab_str, vocab_id in vocab_dict.items():
        if not vocab_str:
            continue
        group[vocab_str[0]].append(vocab_id)

    return dict(group)


def collect_ids_from_chars(
        chars: str, first_char_to_ids: dict[str, list[int]]) -> list[int]:
    """Collect all token IDs for the provided characters in order.

    Args:
        chars: Sequence of leading characters to look up.
        first_char_to_ids: Mapping from a character to
            the token IDs that begins with it.

    Returns:
        List of token IDs for the requested characters.
    """
    ids = []

    for ch in chars:
        ids.extend(first_char_to_ids.get(ch, []))
    return ids
