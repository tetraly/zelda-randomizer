from typing import List

class CharacterMap():
  MAP = {
      '0': 0x00,
      '1': 0x01,
      '2': 0x02,
      '3': 0x03,
      '4': 0x04,
      '5': 0x05,
      '6': 0x06,
      '7': 0x07,
      '8': 0x08,
      '9': 0x09,
      'a': 0x0A,
      'b': 0x0B,
      'c': 0x0C,
      'd': 0x0D,
      'e': 0x0E,
      'f': 0x0F,
      'g': 0x10,
      'h': 0x11,
      'i': 0x12,
      'j': 0x13,
      'k': 0x14,
      'l': 0x15,
      'm': 0x16,
      'n': 0x17,
      'o': 0x18,
      'p': 0x19,
      'q': 0x1A,
      'r': 0x1B,
      's': 0x1C,
      't': 0x1D,
      'u': 0x1E,
      'v': 0x1F,
      'w': 0x20,
      'x': 0x21,
      'y': 0x22,
      'z': 0x23,
      '_': 0x24, # Meant to represent a space.
      '~': 0x25, # Meant to represent leading space.
      ',': 0x28,
      '!': 0x29,
      "'": 0x2A,
      '&': 0x2B,
      '.': 0x2C,
      '"': 0x2D,
      '?': 0x2E,
      '-': 0x2F
  }

  def single_line_to_bytes(self, phrase: str) -> List[int]:
    phrase_lower = phrase.lower()
    phrase_bytes = len(phrase) * [None]
    for i in range(0, len(phrase)):
      phrase_bytes[i] = self.MAP[phrase_lower[i]] or self.MAP['_']

    return phrase_bytes
