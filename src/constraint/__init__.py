#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 15:05:11 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/15 15:16:24 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""A package for optimizing graph search constraints.

Available Modules:
    _constraint_class: Base class for implementation.
    _dfa_constraint: Finite automata engines.
    _trie_constraint: Text prefix lookup structures.
"""

from ._constraint_class import Constraint
from ._dfa_constraint import NumberDFA, StringDFA
from ._trie_constraint import Trie

__all__ = ["Constraint", "NumberDFA", "StringDFA", "Trie"]
