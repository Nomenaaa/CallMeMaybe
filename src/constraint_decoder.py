#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   constraint_decoder.py                                :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/21 09:56:49 by nrasolom            #+#    #+#            #
#   Updated: 2026/08/24 22:15:32 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from constraint_class import Constraint
from typing import Any
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
        if constraint.simulate_from(state, token_str) is not None:
            valid_tokens[token_id] = state

    return valid_tokens
