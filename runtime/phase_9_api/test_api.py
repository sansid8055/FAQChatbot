"""HTTP tests for phase 9 API (run: python -m unittest runtime.phase_9_api.test_api -v)."""

from __future__ import annotations

import os
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi.testclient import TestClient

# Default in-process thread store (no SQLite). Set THREAD_BACKEND=sqlite before importing app
# if you need disk-backed threads for a test module.
os.environ.setdefault("THREAD_BACKEND", "memory")


def tearDownModule() -> None:
    if os.environ.get("THREAD_BACKEND", "memory").lower() == "memory":
        from runtime.phase_8_threads.store_memory import reset_memory_store_for_tests

        reset_memory_store_for_tests()


class Phase9ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from runtime.phase_8_threads.store_memory import reset_memory_store_for_tests

        reset_memory_store_for_tests()
        from runtime.phase_9_api.app import app

        cls.client = TestClient(app)

    def tearDown(self) -> None:
        if os.environ.get("THREAD_BACKEND", "memory").lower() == "memory":
            from runtime.phase_8_threads.store_memory import reset_memory_store_for_tests

            reset_memory_store_for_tests()

    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"status": "ok"})

    def test_root_json_points_to_next_ui(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data.get("service"), "mf-faq-runtime-api")
        self.assertIn("docs", data)
        self.assertIn("web", (data.get("ui") or "").lower())

    def test_threads_list_and_create(self):
        r = self.client.get("/threads")
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), list)

        r2 = self.client.post("/threads", json={})
        self.assertEqual(r2.status_code, 200)
        data = r2.json()
        self.assertIn("id", data)
        self.assertIn("created_at", data)
        tid = data["id"]

        r3 = self.client.get(f"/threads/{tid}/messages")
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3.json()["thread_id"], tid)
        self.assertEqual(r3.json()["messages"], [])

    def test_messages_unknown_thread_404(self):
        r = self.client.get("/threads/00000000-0000-4000-8000-000000000000/messages")
        self.assertEqual(r.status_code, 404)

    def test_post_message_advisory_no_llm(self):
        """Router refusal path — no Groq/Chroma required."""
        tid = self.client.post("/threads", json={}).json()["id"]
        r = self.client.post(
            f"/threads/{tid}/messages",
            json={"content": "Should I put all my savings in this fund?"},
        )
        self.assertEqual(r.status_code, 200, r.text)
        body = r.json()
        self.assertIn("assistant_message", body)
        self.assertTrue(body["assistant_message"])
        self.assertEqual(body["user"]["role"], "user")
        self.assertEqual(body["assistant"]["role"], "assistant")

    def test_concurrent_advisory_posts_different_threads_no_cross_talk(self):
        """Two threads in parallel: each stores only its own user line (advisory path)."""
        t1 = self.client.post("/threads", json={}).json()["id"]
        t2 = self.client.post("/threads", json={}).json()["id"]
        q1 = "Should I invest everything in fund A?"
        q2 = "Which fund is better for retirement?"

        def post_pair(tid: str, content: str):
            r = self.client.post(
                f"/threads/{tid}/messages",
                json={"content": content},
            )
            return tid, r

        with ThreadPoolExecutor(max_workers=4) as ex:
            futs = [
                ex.submit(post_pair, t1, q1),
                ex.submit(post_pair, t2, q2),
            ]
            for f in as_completed(futs):
                tid, r = f.result()
                self.assertEqual(r.status_code, 200, r.text)

        m1 = self.client.get(f"/threads/{t1}/messages").json()["messages"]
        m2 = self.client.get(f"/threads/{t2}/messages").json()["messages"]
        self.assertEqual(len(m1), 2)
        self.assertEqual(len(m2), 2)
        self.assertEqual(m1[0]["content"], q1)
        self.assertEqual(m2[0]["content"], q2)
        self.assertNotEqual(m1[0]["content"], m2[0]["content"])

    def test_concurrent_posts_same_thread_serialized(self):
        """Same thread: parallel calls serialize; each turn is user+assistant with no gaps."""
        tid = self.client.post("/threads", json={}).json()["id"]

        def post_advisory(n: int):
            r = self.client.post(
                f"/threads/{tid}/messages",
                json={"content": f"Should I buy fund number {n}?"},
            )
            return n, r

        with ThreadPoolExecutor(max_workers=4) as ex:
            futs = [ex.submit(post_advisory, i) for i in (1, 2, 3)]
            for f in as_completed(futs):
                n, r = f.result()
                self.assertEqual(r.status_code, 200, r.text)

        msgs = self.client.get(f"/threads/{tid}/messages").json()["messages"]
        self.assertEqual(len(msgs), 6)
        for i in range(0, 6, 2):
            self.assertEqual(msgs[i]["role"], "user")
            self.assertEqual(msgs[i + 1]["role"], "assistant")
        users = {m["content"] for m in msgs if m["role"] == "user"}
        self.assertEqual(users, {f"Should I buy fund number {i}?" for i in (1, 2, 3)})

    def test_admin_reindex_without_secret_503(self):
        old = os.environ.pop("ADMIN_REINDEX_SECRET", None)
        try:
            r = self.client.post("/admin/reindex", headers={"Authorization": "Bearer x"})
            self.assertEqual(r.status_code, 503)
        finally:
            if old is not None:
                os.environ["ADMIN_REINDEX_SECRET"] = old


if __name__ == "__main__":
    unittest.main()
