#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   constraint_class.py                                  :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/20 10:12:39 by nrasolom            #+#    #+#            #
#   Updated: 2026/08/21 13:58:40 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from abc import ABC, abstractmethod
from typing import Any
from vocab import get_vocab, get_first_char_to_ids
from llm_sdk import Small_LLM_Model


class Constraint(ABC):
    @abstractmethod
    def simulate_from(self, state: Any, word: str) -> Any:
        pass

    @abstractmethod
    def is_accepted(self, state: Any) -> bool:
        pass

    @abstractmethod
    def get_candidate_ids(
        self, state: Any, first_char_to_ids: dict[str, int]
    ) -> list[str]:
        pass


class TrieNode:
    def __init__(self):
        self._children: dict[str, TrieNode] = {}
        self._EndOfWord = False


class Trie(Constraint):
    def __init__(self):
        self._root = TrieNode()

    def insert(self, option: str) -> None:
        curr = self._root

        for char in option:
            if char not in curr._children:
                curr._children[char] = TrieNode()
            curr = curr._children[char]
        curr._EndOfWord = True

    def simulate_from(self, state: TrieNode, word: str) -> TrieNode | None:
        curr = state

        for char in word:
            if char not in curr._children:
                return None
            curr = curr._children[char]
        return curr

    def is_accepted(self, state: TrieNode) -> bool:
        if state._EndOfWord:
            return True
        return False

    def get_candidate_ids(
            self,state: TrieNode, first_char_to_ids: dict[str, int]
    ) -> list[int]:
        ids: list[int] = []

        for key in state._children:
            ids += first_char_to_ids.get(key)
        return ids


class DFA(Constraint, ABC):
    def __init__(self, accepting_states: list[str]):
        self._start = "START"
        self._accepted = accepting_states

    @abstractmethod
    def transitions(state: str, char: str) -> None | str:
        pass

    def simulate_from(self, state: str, word: str) -> None | str:
        curr = state

        for char in word:
            next_state = self.transitions(curr, char)
            if next_state is None:
                return None
            curr = next_state
        return curr

    def is_accepted(self, state: str) -> bool:
        if state in self._accepted:
            return True
        return False

    @abstractmethod
    def get_candidate_ids(
        self, state: str, first_char_to_ids: dict[str, int]
    ) -> list[int]:
        pass


class StringDFA(DFA):
    def transitions(self, state: str, char: str) -> None | str:
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

    def get_candidate_ids(
            self, state: str, first_char_to_ids: dict[str, int]
    ) -> list[int]:
        if state == "START":
            return first_char_to_ids.get('"')
        if state == "ESCAPE":
            return first_char_to_ids.get("\\")
        if state == "IN_STRING":
            return []


class NumberDFA(DFA):
    def transitions(self, state: str, char: str) -> str | None:
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
                None
        if state == "DOT":
            return "IN_FRACTION" if char.isdigit() else None
        if state == "IN_FRACTION":
            return "IN_FRACTION" if char.isdigit() else None

    def get_candidate_ids(
            self, state: str, first_char_to_ids: dict[str, int]
    ) -> list[int]:
        pass


# if __name__ == "__main__":
#     groups_ids = get_first_char_to_ids(get_vocab(Small_LLM_Model()))
#     trie = Trie()
#     options = ["fn_add_numbers", "fn_greet", "fn_reverse_string"]
#     for opt in options:
#         trie.insert(opt)
#     test = trie.simulate_from(trie._root, "fn_add")
#     print(f"{test._EndOfWord}   {test._children}")
#     print(trie.get_candidate_ids(test, groups_ids))


#     str_dfa = StringDFA(["END"])
#     test = str_dfa.simulate_from(str_dfa._start, '"\l')
#     print(test)

#     num_dfa = NumberDFA(["IN_FRACTION"])
#     test = num_dfa.simulate_from(num_dfa._start, "42")
#     print(test)
#     print(num_dfa.is_accepted(test))
