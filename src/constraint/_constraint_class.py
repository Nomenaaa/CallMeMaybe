#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   _constraint_class.py                                 :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/20 10:12:39 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/15 15:26:49 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from abc import ABC, abstractmethod
from typing import Any


class Constraint(ABC):
    """Abstract base class for automaton-based token-generation constraints.

    Attributes:
        cache: Cache of valid token IDs keyed by state.
    """

    def __init__(self) -> None:
        """Initiliaze the constraint instance."""
        self._cache: dict[Any, dict[int, Any]] = {}

    @abstractmethod
    def simulate_from(self, state: Any, word: str) -> Any:
        """Advance the constraint state by consuming a token string.

        Args:
            state: The current state, either a string or a trie node.
            word: The token string to simulate.

        Returns:
            Any: The next state after consuming the token string.
        """
        pass

    @abstractmethod
    def is_accepted(self, state: Any) -> bool:
        """Check whether the provided state represents a valid completion.

        Args:
            state: The current state to evaluate.

        Returns:
            True if the state is accepting, otherwise False.
        """
        pass

    @abstractmethod
    def get_candidate_ids(
        self, state: Any, first_char_to_ids: dict[str, list[int]]
    ) -> list[int]:
        """Collect the token IDs that may legally continue from a state.

        Args:
            state: The current state, either a string or a trie node.
            first_char_to_ids: Mapping from a character to
                the token IDs that begin with it.

        Returns:
            Candidate token IDs pre-filtred as possible valid from this state.
        """
        pass

    @abstractmethod
    def get_start_state(self) -> Any:
        """Return the initial state for the constraint.

        Returns:
            The initial state of the automaton or trie.
        """
        pass
