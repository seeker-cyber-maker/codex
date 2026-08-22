from __future__ import annotations

import unittest

from house.worker_exec.human_authority import (
    HumanAuthorityError,
    prepare_authority_request,
    refuse_authority_request,
)


class HumanAuthorityTests(unittest.TestCase):
    def test_every_well_formed_request_refuses(self) -> None:
        request = prepare_authority_request(
            request_id="request-1",
            operation_id="operation-1",
            record_sha256="a" * 64,
            profile_sha256="b" * 64,
            scope_sha256="c" * 64,
            wall_seconds=60,
            issued_at=100,
            expires_at=160,
            challenge_sha256="d" * 64,
        )
        refusal = refuse_authority_request(request)
        self.assertEqual(refusal["state"], "UNQUALIFIED_REFUSE")
        self.assertEqual(refusal["dispatch"], "NOT_ATTEMPTED")

    def test_tampered_request_never_reaches_refusal_backend(self) -> None:
        request = prepare_authority_request(
            request_id="request-1",
            operation_id="operation-1",
            record_sha256="a" * 64,
            profile_sha256="b" * 64,
            scope_sha256="c" * 64,
            wall_seconds=60,
            issued_at=100,
            expires_at=160,
            challenge_sha256="d" * 64,
        )
        with self.assertRaisesRegex(HumanAuthorityError, "hash mismatch"):
            refuse_authority_request({**request, "wall_seconds": 61})
