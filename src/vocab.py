#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   vocab.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 11:26:49 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/09 12:14:32 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
from collections import defaultdict
import json


def get_vocab(model: Small_LLM_Model) -> dict[str, int]:
    with open(model.get_path_to_vocab_file(), 'r') as file:
        vocab_dict: dict[str, int] = json.load(file)

    return vocab_dict


def get_first_char_to_ids(vocab_dict: dict[str, int]) -> dict[str, list[int]]:
    group: defaultdict[str, list[int]] = defaultdict(list)

    for vocab_str, vocab_id in vocab_dict.items():
        if not vocab_str:
            continue
        group[vocab_str[0]].append(vocab_id)

    return dict(group)


def collect_ids_from_chars(
        chars: str, first_char_to_ids: dict[str, list[int]]) -> list[int]:
    ids = []

    for ch in chars:
        ids.extend(first_char_to_ids.get(ch, []))
    return ids
