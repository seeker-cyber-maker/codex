"""Contract tests for the offline Dream House worker relay."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from house.relay import Relay, RelayError


def envelope(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema": "codex-house-relay-envelope/1",
        "envelope_id": "relay-001",
        "thread_id": "thread-001",
        "sender_id": "worker.alpha",
        "recipient_id": "worker.beta",
        "contract_version": "worker-contract/1",
        "payload": {"kind": "proposal", "artifact_sha256": "a" * 64},
        "ttl_hops": 2,
        "turn_budget": 1,
    }
    value.update(overrides)
    return value


class RelayContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.relay = Relay(Path(self.temporary.name) / "relay.sqlite")

    def tearDown(self) -> None:
        self.relay.close()
        self.temporary.cleanup()

    def test_store_forward_acknowledgement_and_receipts_are_authority_neutral(
        self,
    ) -> None:
        accepted = self.relay.submit(envelope())
        self.assertEqual(accepted["state"], "QUEUED")
        self.assertEqual(accepted["authority_disposition"], "NO_AUTHORITY_GRANTED")

        delivered = self.relay.receive("worker.beta", limit=1)
        self.assertEqual([item["envelope_id"] for item in delivered], ["relay-001"])
        self.assertEqual(delivered[0]["state"], "DELIVERED")
        self.assertEqual(delivered[0]["hop_count"], 1)

        acknowledged = self.relay.acknowledge("worker.beta", "relay-001", "received")
        self.assertEqual(acknowledged["state"], "ACKNOWLEDGED")
        self.assertEqual(acknowledged["authority_disposition"], "NO_AUTHORITY_GRANTED")
        self.assertEqual(self.relay.get("relay-001")["state"], "ACKNOWLEDGED")
        self.assertTrue(self.relay.verify_journal())

    def test_replies_are_threaded_and_cannot_exceed_parent_budget(self) -> None:
        self.relay.submit(envelope())
        self.relay.receive("worker.beta", limit=1)
        reply = envelope(
            envelope_id="relay-002",
            sender_id="worker.beta",
            recipient_id="worker.alpha",
            parent_envelope_id="relay-001",
            turn_budget=0,
        )
        accepted = self.relay.submit(reply)
        self.assertEqual(accepted["thread_id"], "thread-001")
        self.assertEqual(accepted["parent_envelope_id"], "relay-001")

        self.relay.receive("worker.alpha", limit=1)
        with self.assertRaisesRegex(RelayError, "turn budget"):
            self.relay.submit(
                envelope(
                    envelope_id="relay-003",
                    sender_id="worker.alpha",
                    recipient_id="worker.beta",
                    parent_envelope_id="relay-002",
                    turn_budget=0,
                )
            )

    def test_invalid_contract_or_expired_ttl_fails_before_journal_mutation(
        self,
    ) -> None:
        before = self.relay.events()
        with self.assertRaisesRegex(RelayError, "ttl_hops"):
            self.relay.submit(envelope(ttl_hops=0))
        with self.assertRaisesRegex(RelayError, "contract_version"):
            self.relay.submit(envelope(contract_version=""))
        self.assertEqual(self.relay.events(), before)

    def test_recipient_cannot_acknowledge_another_workers_envelope(self) -> None:
        self.relay.submit(envelope())
        self.relay.receive("worker.beta", limit=1)
        with self.assertRaisesRegex(RelayError, "recipient"):
            self.relay.acknowledge("worker.gamma", "relay-001", "nope")

    def test_envelope_idempotency_binds_every_routing_field(self) -> None:
        self.relay.submit(envelope())
        with self.assertRaisesRegex(RelayError, "different content"):
            self.relay.submit(envelope(recipient_id="worker.gamma"))


if __name__ == "__main__":
    unittest.main()
