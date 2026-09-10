#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   constraint_class.py                                  :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/20 10:12:39 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/10 17:52:13 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from abc import ABC, abstractmethod
from typing import Any
from vocab import collect_ids_from_chars


class Constraint(ABC):
    """Abstract base class for automaton-based token-generation constraints.

    Attributes:
        cache: Cache of valid token IDs keyed by state.
    """

    def __init__(self) -> None:
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


class TrieNode:
    """Single node in a trie used for word-prefix validation.

    Attributes:
        children: Mapping from a character to its child node.
        EndOfWord: Whether the current node marks the end of a valid word.
    """

    def __init__(self) -> None:
        self._children: dict[str, TrieNode] = {}
        self._EndOfWord = False


class Trie(Constraint):
    """Constraint that accepts strings matching a set of valid prefixes.

    Attributes:
        root: Root node of the trie.
    """

    def __init__(self) -> None:
        super().__init__()
        self._root = TrieNode()

    def insert(self, option: str) -> None:
        """Insert a word into the trie.

        Args:
            option: The string to insert.
        """
        curr = self._root

        for char in option:
            if char not in curr._children:
                curr._children[char] = TrieNode()
            curr = curr._children[char]
        curr._EndOfWord = True

    def simulate_from(self, state: TrieNode, word: str) -> TrieNode | None:
        """Advance the trie state by consuming a word.

        Args:
            state: The current trie node.
            word: The word to consume.

        Returns:
            The node reached after consuming the word, or None if invalid.
        """
        curr = state

        for char in word:
            if char not in curr._children:
                return None
            curr = curr._children[char]
        return curr

    def is_accepted(self, state: TrieNode) -> bool:
        """Check whether the trie node marks the end of a valid word.

        Args:
            state: The trie node to evaluate.

        Returns:
            bool: True if the word is complete, otherwise False.
        """
        if state._EndOfWord:
            return True
        return False

    def get_candidate_ids(
            self, state: TrieNode, first_char_to_ids: dict[str, list[int]]
    ) -> list[int]:
        """Collect valid next-token IDs from the current trie node.

        Args:
            state: The current trie node.
            first_char_to_ids: Mapping from a character to
                the token IDs that begin with it.

        Returns:
            Token IDs whose first character matches a valid child.
        """
        ids: list[int] = []

        for key in state._children:
            ids.extend(first_char_to_ids.get(key, []))
        return ids

    def get_start_state(self) -> Any:
        """Return the root node of the trie.

        Returns:
            The start state of the trie.
        """
        return self._root


class DFA(Constraint, ABC):
    """Abstract deterministic finite automaton constraint.

    Args:
        accepting_states: States that represent valid terminal states.

    Attributes:
        accepted: Accepting states for the automaton.
    """

    def __init__(self, accepting_states: list[str]):
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
            return collect_ids_from_chars("\\'\"bnfrtu/", first_char_to_ids)
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
            return "IN_FRACTION" if char.isdigit() else None
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
        number = collect_ids_from_chars("0123456789", first_char_to_ids)
        if state == "START":
            number.extend(collect_ids_from_chars("+-", first_char_to_ids))
            return number
        if state == "IN_NUMBER":
            number.extend(first_char_to_ids.get('.', []))
            return number
        if state in ["SIGN", "DOT", "IN_FRACTION"]:
            return number
        return []

    def get_start_state(self) -> str:
        """Return the initial DFA state for number parsing.

        Returns:
            The initial state for numeric parsing.
        """
        return "START"
