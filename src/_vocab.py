#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   _vocab.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 11:26:49 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/18 10:47:52 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
from collections import defaultdict
import json


def bytes_to_unicode() -> dict[int, str]:
    """Build byte-to-unicode placeholder mapping.

    Returns:
        Mapping from each byte value to its placeholder
            unicode character, e.g. ``{32: 'Ġ', 65: 'A', ...}``
    """
    bs = (
        list(range(ord("!"), ord("~") + 1)) +
        list(range(ord("¡"), ord("¬") + 1)) +
        list(range(ord("®"), ord("ÿ") + 1))
    )
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, [chr(c) for c in cs]))


def unicode_to_char(b_to_u: dict[int, str]) -> dict[str, str]:
    """Invert a byte_to_unicode mapping into a placeholder-to-har lookup.

    Args:
        b_to_u: Mapping from byte value to placeholder unicode
            character.

    Returns:
        Mapping from each placeholder unicode character to the real
            character it represents
    """
    unicode_to_char = {
            u_char: chr(b) for b, u_char in b_to_u.items()}

    return unicode_to_char


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


def get_first_char_to_ids(
        vocab_dict: dict[str, int],
        u_to_char: dict[str, str]) -> dict[str, list[int]]:
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
        first_char = vocab_str[0]
        group[u_to_char.get(first_char, first_char)].append(vocab_id)

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


class Vocab:
    """Byte-level BPE vocabulary wrapper with placeholder-to-text decoding.

    Attributes:
        str_to_id: Mapping from raw vocabulary strings to token ids.
        id_to_str: Mapping from token id to raw vocabulary string.
        b_to_u: Mapping from byte value to its placeholder
            unicode character.
        u_to_char: Mapping from placeholder unicode character back to
            the real character it represents.
        first_char_to_ids: Mapping from character to
                token IDs that begins with it.
    """
    def __init__(self, model: Small_LLM_Model):
        """Initialize the Vocab class.

        Args:
            model: The model instance to pull the vocabulary from.
        """
        self.str_to_id = get_vocab(model)
        self.id_to_str = {_id: char for char, _id in self.str_to_id.items()}
        self.b_to_u = bytes_to_unicode()
        self.u_to_char = unicode_to_char(self.b_to_u)
        self.first_char_to_ids = get_first_char_to_ids(
            self.str_to_id, self.u_to_char)

    def decode(self, token_id: int) -> str:
        """Decodes a single token id into its real character(s).

        Args:
            token_id: The token id to decode.

        Returns:
            The decoded string for this token.
        """
        raw_string = self.id_to_str[token_id]

        decoded: str = ""
        for char in raw_string:
            decoded += self.u_to_char.get(char, char)
        return decoded
