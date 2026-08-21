#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   vocab.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 11:26:49 by nrasolom            #+#    #+#            #
#   Updated: 2026/08/21 11:46:27 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from llm_sdk import Small_LLM_Model
from collections import defaultdict
import json
import numpy as np
import time

def get_vocab(model: Small_LLM_Model) -> dict[str, int]:
    with open(model.get_path_to_vocab_file(), 'r') as file:
        vocab_dict: dict[str, int] = json.load(file)

    return vocab_dict


def get_id_to_str(vocab_dict: dict[str, int]
) -> np.ndarray[tuple[int], np.dtype[np.object_]]:
    size = len(vocab_dict)
    id_lookup = np.empty(size, dtype=object)

    for vocab_str, vocab_id in vocab_dict.items():
        id_lookup[vocab_id] = vocab_str

    return id_lookup


def get_first_char_to_ids(vocab_dict: dict[str, int]) -> dict[str, list[int]]:
    group: defaultdict[str, list[int]] = defaultdict(list)

    for vocab_str, vocab_id in vocab_dict.items():
        if not vocab_str:
            continue
        group[vocab_str[0]].append(vocab_id)

    return dict(group)


# if __name__ == "__main__":
#     start = time.perf_counter()
#     group_ids = first_char_to_ids(get_vocab(Small_LLM_Model()))
#     print(group_ids.get("a"))
#     end = time.perf_counter()
#     print(f"Elapsed time: {round(end - start, 3)} seconds")
