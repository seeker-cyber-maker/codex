from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

from house.term_notation import (
    NOTATION_ID,
    TermNotationError,
    missing_preference,
    parse_record,
)
from house.term_notation.parser import (
    MAX_BLOCK_LINES,
    MAX_CONTEXT_IDENTIFIER_CHARACTERS,
    MAX_RECORD_BYTES,
    MAX_VALUE_CHARACTERS,
)


class TermNotationParserTests(unittest.TestCase):
    def test_parses_casual_repair_query(self) -> None:
        self.assertEqual(
            parse_record("TERM? native language").to_dict(),
            {
                "schema": "dream-house/term-notation-record/1",
                "notation_id": NOTATION_ID,
                "kind": "repair_query",
                "operator": "TERM?",
                "candidate": "native language",
                "meaning": None,
                "excluded_meaning": None,
                "scope": None,
                "context_generation": None,
                "reason": None,
                "target": None,
                "preference": None,
                "alternative": None,
            },
        )

    def test_parses_detailed_repair_query(self) -> None:
        record = parse_record(
            "TERM? native language\n"
            "MEAN observed coordination register\n"
            "NOT claim of innate origin\n"
            "SCOPE Dream House communications RFC"
        )
        self.assertEqual(record.meaning, "observed coordination register")
        self.assertEqual(record.excluded_meaning, "claim of innate origin")
        self.assertEqual(record.scope, "Dream House communications RFC")

    def test_parses_working_definition(self) -> None:
        record = parse_record(
            "TERM= native language | MEAN discovery alias | "
            "SCOPE Dream House RFC | CTX 7"
        )
        self.assertEqual(record.kind, "working_definition")
        self.assertEqual(record.context_generation, "7")

    def test_parses_unresolved_record(self) -> None:
        record = parse_record("TERM~ native language | SCOPE RFC | WHY origin unclear")
        self.assertEqual(record.kind, "unresolved")
        self.assertEqual(record.reason, "origin unclear")

    def test_parses_preference_query_and_all_declared_values(self) -> None:
        query = parse_record("PREF? target=TERM_NOTATION/1")
        self.assertEqual(query.kind, "preference_query")
        for value in ("preferred", "not_preferred", "no_preference", "undetermined"):
            with self.subTest(value=value):
                record = parse_record(f"PREF= target=TERM_NOTATION/1 | {value}")
                self.assertEqual(record.preference, value)

    def test_alt_is_only_valid_with_not_preferred(self) -> None:
        record = parse_record(
            "PREF= target=TERM_NOTATION/1 | not_preferred | ALT use plain prose"
        )
        self.assertEqual(record.alternative, "use plain prose")
        with self.assertRaisesRegex(TermNotationError, "only with not_preferred"):
            parse_record("PREF= target=TERM_NOTATION/1 | preferred | ALT use prose")

    def test_missing_preference_is_wrapper_only(self) -> None:
        self.assertEqual(missing_preference().preference, "not_stated")
        with self.assertRaisesRegex(TermNotationError, "wrapper-only"):
            parse_record("PREF= target=TERM_NOTATION/1 | not_stated")

    def test_rejects_unknown_operator_field_and_control_extension(self) -> None:
        invalid = (
            "TERMM? candidate",
            "TERM? candidate\nCOLOR blue",
            "TERM= candidate | MEAN value | SCOPE scope | CTX 1 | EXEC open",
        )
        for text in invalid:
            with self.subTest(text=text), self.assertRaises(TermNotationError):
                parse_record(text)

    def test_rejects_duplicate_fields(self) -> None:
        invalid = (
            "TERM? candidate\nMEAN one\nMEAN two",
            "TERM= candidate | MEAN one | MEAN two | SCOPE scope | CTX 1",
        )
        for text in invalid:
            with self.subTest(text=text), self.assertRaisesRegex(
                TermNotationError, "duplicate field"
            ):
                parse_record(text)

    def test_rejects_noncanonical_field_order(self) -> None:
        invalid = (
            "TERM? candidate\nSCOPE scope\nMEAN value",
            "TERM= candidate | SCOPE scope | MEAN value | CTX 1",
            "TERM~ candidate | WHY unclear | SCOPE scope",
        )
        for text in invalid:
            with self.subTest(text=text), self.assertRaisesRegex(
                TermNotationError, "canonically ordered"
            ):
                parse_record(text)

    def test_rejects_missing_required_fields(self) -> None:
        for text in (
            "TERM= candidate | MEAN value | SCOPE scope",
            "TERM~ candidate | SCOPE scope",
        ):
            with self.subTest(text=text), self.assertRaisesRegex(
                TermNotationError, "missing required"
            ):
                parse_record(text)

    def test_rejects_ambiguous_delimiters_and_multiple_records(self) -> None:
        invalid = (
            "TERM= candidate|other | MEAN value | SCOPE scope | CTX 1",
            "TERM= candidate | MEAN value|other | SCOPE scope | CTX 1",
            "TERM? one\nTERM? two",
        )
        for text in invalid:
            with self.subTest(text=text), self.assertRaises(TermNotationError):
                parse_record(text)

    def test_rejects_oversized_or_control_character_input(self) -> None:
        with self.assertRaisesRegex(TermNotationError, "byte limit"):
            parse_record("TERM? " + "x" * MAX_RECORD_BYTES)
        with self.assertRaisesRegex(TermNotationError, "character limit"):
            parse_record("TERM? " + "x" * (MAX_VALUE_CHARACTERS + 1))
        with self.assertRaisesRegex(TermNotationError, "control character"):
            parse_record("TERM? bad\x00value")
        with self.assertRaisesRegex(TermNotationError, "context identifier"):
            parse_record(
                "TERM= candidate | MEAN value | SCOPE scope | CTX "
                + "x" * (MAX_CONTEXT_IDENTIFIER_CHARACTERS + 1)
            )

    def test_dictionary_matches_parser_constants_and_contract(self) -> None:
        path = Path(__file__).parents[1] / "dictionary.json"
        dictionary = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(dictionary["notation_id"], NOTATION_ID)
        self.assertEqual(dictionary["limits"]["max_record_bytes"], MAX_RECORD_BYTES)
        self.assertEqual(
            dictionary["limits"]["max_value_characters"], MAX_VALUE_CHARACTERS
        )
        self.assertEqual(
            dictionary["limits"]["max_context_identifier_characters"],
            MAX_CONTEXT_IDENTIFIER_CHARACTERS,
        )
        self.assertEqual(dictionary["limits"]["max_block_lines"], MAX_BLOCK_LINES)
        self.assertEqual(
            set(dictionary["operators"]["PREF="]["reviewer_values"]),
            {"preferred", "not_preferred", "no_preference", "undetermined"},
        )

    def test_parser_has_only_pure_standard_library_dependencies(self) -> None:
        path = Path(__file__).parents[1] / "parser.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported_roots: set[str] = set()
        called_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
        self.assertEqual(
            imported_roots,
            {"__future__", "collections", "dataclasses", "re", "types"},
        )
        self.assertTrue(
            {"open", "exec", "eval", "compile", "__import__"}.isdisjoint(called_names)
        )


if __name__ == "__main__":
    unittest.main()
