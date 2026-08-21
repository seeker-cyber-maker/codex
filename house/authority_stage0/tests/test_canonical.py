from __future__ import annotations

import unittest

from house.authority_stage0.canonical import (
    CanonicalError,
    canonical_text,
    strict_loads,
)


class CanonicalTests(unittest.TestCase):
    def assert_code(self, code: str, action) -> None:
        with self.assertRaises(CanonicalError) as caught:
            action()
        self.assertEqual(caught.exception.code, code)

    def test_rejects_duplicate_key(self) -> None:
        self.assert_code("CANON_DUPLICATE_KEY", lambda: strict_loads('{"a":1,"a":2}'))

    def test_rejects_invalid_utf8(self) -> None:
        self.assert_code("CANON_UTF8", lambda: strict_loads(b'"\xff"'))

    def test_rejects_float_and_constants(self) -> None:
        self.assert_code("CANON_FLOAT", lambda: strict_loads("1.0"))
        self.assert_code("CANON_CONSTANT", lambda: strict_loads("NaN"))
        self.assert_code("CANON_CONSTANT", lambda: strict_loads("Infinity"))

    def test_rejects_out_of_range_integer(self) -> None:
        self.assert_code("CANON_INTEGER_RANGE", lambda: strict_loads(str(2**63)))
        self.assert_code("CANON_INTEGER_RANGE", lambda: canonical_text(-(2**63) - 1))

    def test_rejects_lone_surrogate_and_unsupported_type(self) -> None:
        self.assert_code("CANON_SURROGATE", lambda: strict_loads('"\\ud800"'))
        self.assert_code("CANON_TYPE", lambda: canonical_text({"a": {1, 2}}))

    def test_utf16_key_order(self) -> None:
        # U+10000 sorts before U+E000 by UTF-16 code units, unlike code points.
        value = {"\ue000": 2, "\U00010000": 1}
        self.assertEqual(canonical_text(value), '{"\U00010000":1,"\ue000":2}')

    def test_input_order_is_irrelevant(self) -> None:
        left = {"z": 1, "a": {"y": 2, "b": 3}}
        right = {"a": {"b": 3, "y": 2}, "z": 1}
        self.assertEqual(canonical_text(left), canonical_text(right))

    def test_escaped_content_and_int64_boundaries(self) -> None:
        value = {"s": 'quote=" newline=\n unicode=é', "lo": -(2**63), "hi": 2**63 - 1}
        parsed = strict_loads(canonical_text(value))
        self.assertEqual(parsed, value)


if __name__ == "__main__":
    unittest.main()
