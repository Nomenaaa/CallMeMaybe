#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   _dfa_constraint.py                                   :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 14:12:01 by nrasolom            #+#    #+#            #
#   Updated: 2026/10/15 07:55:38 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from abc import ABC, abstractmethod
from typing import Any
from .._vocab import collect_ids_from_chars
from ._constraint_class import Constraint


class DFA(Constraint, ABC):
    """Abstract deterministic finite automaton constraint.

    Args:
        accepting_states: States that represent valid terminal states.

    Attributes:
        accepted: Accepting states for the automaton.
    """

    def __init__(self, accepting_states: list[str]):
        """Initiliaze the DFA constraint instance."""
        super().__init__()
        self._accepted = accepting_states

    @abstractmethod
    def transitions(self, state: str, char: str) -> None | str:
        """Return the next DFA state after consuming a character.

        Args:
            state: The current DFA state.
            char: The character to process.

        Returns:
            The next DFA state if the transition is valid, else None.
        """
        pass

    def simulate_from(self, state: str, word: str) -> None | str:
        """Advance the DFA state by consuming a word.

        Args:
            state: The current DFA state.
            word: The token string to consume.

        Returns:
            The state reached after consuming the word, or None if invalid.
        """
        curr = state

        for char in word:
            next_state = self.transitions(curr, char)
            if next_state is None:
                return None
            curr = next_state
        return curr

    def is_accepted(self, state: str) -> bool:
        """Check whether the given state is accepting.

        Args:
            state: The DFA state to evaluate.

        Returns:
            True if the state is accepting, else False.
        """
        if state in self._accepted:
            return True
        return False

    @abstractmethod
    def get_candidate_ids(
        self, state: str, first_char_to_ids: dict[str, list[int]]
    ) -> list[int]:
        """Collect token IDs that may continue from the current state.

        Args:
            state: The current DFA state.
            first_char_to_ids: Mapping from character to
                token IDs that begins with it.

        Returns:
            Candidate token IDs that are pre-filtred as possible valid.
        """
        pass

    @abstractmethod
    def get_start_state(self) -> Any:
        """Return the initial DFA state.

        Returns:
            Any: The start state of the automaton.
        """
        pass


class StringDFA(DFA):
    """Finite automaton for validating JSON-style string literals."""

    def transitions(self, state: str, char: str) -> None | str:
        """Return the next state while parsing a string literal.

        Args:
            state: The current DFA state.
            char: The next character to process.

        Returns:
            The next state if the character is valid, else None.
        """
        if state == "START":
            return "IN_STRING" if char == '"' else None
        if state == "IN_STRING":
            if char == "\\":
                return "ESCAPE"
            elif char == '"':
                return "END"
            else:
                return "IN_STRING"
        if state == "ESCAPE":
            return "IN_STRING" if char in "\\'\"nrtbfva" else None
        return None

    def get_candidate_ids(
            self, state: str, first_char_to_ids: dict[str, list[int]]
    ) -> list[int]:
        """Collect possible valid next-token IDs for a string DFA state.

        Args:
            state: The current DFA state.
            first_char_to_ids: Mapping from character to
                token IDs that begins with it.

        Returns:
            Token IDs that may legally continue from the current state.
        """
        if state == "START":
            return first_char_to_ids.get('"', [])
        if state == "ESCAPE":
            ids: list[int] = collect_ids_from_chars(
                "\\'\"bnfrtu/", first_char_to_ids)
            return ids
        if state == "IN_STRING":
            ids = []
            for ch, ch_ids in first_char_to_ids.items():
                if (not ch == '\\' and not ch == '"'):
                    ids.extend(ch_ids)
            ids.extend([1, 14])
            return ids
        return []

    def get_start_state(self) -> str:
        """Return the initial DFA state for string parsing.

        Returns:
            The initial state for a string literal.
        """
        return "IN_STRING"


class NumberDFA(DFA):
    """Finite automaton for validating numeric literals."""

    def transitions(self, state: str, char: str) -> str | None:
        """Return the next state while parsing a numeric literal.

        Args:
            state: The current DFA state.
            char: The next character to process.

        Returns:
            The next state if the character is valid, else None.
        """
        if state == "START":
            if char == "-" or char == "+":
                return "SIGN"
            elif char.isdigit():
                return "IN_NUMBER"
            else:
                return None
        if state == "SIGN":
            return "IN_NUMBER" if char.isdigit() else None
        if state == "IN_NUMBER":
            if char == ".":
                return "DOT"
            elif char.isdigit():
                return "IN_NUMBER"
            else:
                return None
        if state == "DOT":
            return "IN_FRACTION" if char.isdigit() else None
        if state == "IN_FRACTION":
            if char.isdigit():
                return "IN_FRACTION"
            elif char == ",":
                return "END"
            else:
                return None
        return None

    def get_candidate_ids(
            self, state: str, first_char_to_ids: dict[str, list[int]]
    ) -> list[int]:
        """Collect possible valid next-token IDs for a numeric DFA state.

        Args:
            state: The current DFA state.
            first_char_to_ids: Mapping from character to
                token IDs that begins with it.

        Returns:
            Token IDs that may legally continue from the current state.
        """
        number: list[int] = collect_ids_from_chars(
            "0123456789", first_char_to_ids)
        if state == "START":
            number.extend(collect_ids_from_chars("+-", first_char_to_ids))
            return number
        if state == "IN_NUMBER":
            number.extend(first_char_to_ids.get('.', []))
            return number
        if state in ["SIGN", "DOT"]:
            return number
        if state == "IN_FRACTION":
            number.extend(first_char_to_ids.get(",", []))
            return number
        return []

    def get_start_state(self) -> str:
        """Return the initial DFA state for number parsing.

        Returns:
            The initial state for numeric parsing.
        """
        return "START"
