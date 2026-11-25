#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   _trie_constraint.py                                  :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 14:11:46 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/15 15:28:20 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from ._constraint_class import Constraint
from typing import Any


class TrieNode:
    """Single node in a trie used for word-prefix validation.

    Attributes:
        children: Mapping from a character to its child node.
        EndOfWord: Whether the current node marks the end of a valid word.
    """

    def __init__(self) -> None:
        """Initiliaze the trie node instance."""
        self._children: dict[str, TrieNode] = {}
        self._EndOfWord = False


class Trie(Constraint):
    """Constraint that accepts strings matching a set of valid prefixes.

    Attributes:
        root: Root node of the trie.
    """

    def __init__(self) -> None:
        """Initiliaze the Trie constraint instance."""
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
