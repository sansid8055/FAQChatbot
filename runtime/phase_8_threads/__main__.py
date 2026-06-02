"""CLI: threads + messages + phase 7 RAG (rag-architecture.md §8)."""

from __future__ import annotations

import argparse
import json
import logging
import sys

from ingest.repo_dotenv import load_repo_dotenv

from runtime.phase_8_threads.chat_service import context_messages_for_thread, post_user_message
from runtime.phase_8_threads.store import create_thread, list_messages, list_threads, thread_exists
from runtime.phase_8_threads.types import ThreadNotFoundError


def main() -> int:
    load_repo_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(
        description="Phase 8 — thread store + safe RAG (rag-architecture.md §8)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_new = sub.add_parser("new-thread", help="Create a thread; print its UUID")
    p_new.add_argument(
        "--session",
        default=None,
        metavar="KEY",
        help="Optional non-PII session key for filtering (§8.1)",
    )

    p_list = sub.add_parser("list-threads", help="List threads (newest first)")
    p_list.add_argument(
        "--session",
        default=None,
        metavar="KEY",
        help="Filter by session key",
    )

    p_hist = sub.add_parser("history", help="List all messages in a thread")
    p_hist.add_argument("thread_id")
    p_hist.add_argument(
        "--json",
        action="store_true",
        help="Structured JSON output",
    )

    p_ctx = sub.add_parser(
        "context",
        help="Show last-N-turn message window (§8.2; env THREAD_MAX_TURNS)",
    )
    p_ctx.add_argument("thread_id")

    p_say = sub.add_parser("say", help="Post user message; run pipeline; print assistant reply")
    p_say.add_argument("thread_id")
    p_say.add_argument("text", help="User message")
    p_say.add_argument(
        "--no-expand",
        action="store_true",
        help="Disable §8.2 retrieval query expansion",
    )
    p_say.add_argument(
        "--allow-pii-queries",
        action="store_true",
        help="Disable §7.3 PII heuristic on the (possibly expanded) query",
    )
    p_say.add_argument(
        "--json",
        action="store_true",
        help="Print user + assistant rows as JSON",
    )

    args = parser.parse_args()

    if args.cmd == "new-thread":
        tid = create_thread(session_key=args.session)
        print(tid)
        return 0

    if args.cmd == "list-threads":
        for t in list_threads(session_key=args.session):
            sk = t.session_key or ""
            print(f"{t.id}\t{t.created_at}\t{sk}")
        return 0

    if args.cmd == "history":
        if not thread_exists(args.thread_id):
            print(f"Unknown thread: {args.thread_id}", file=sys.stderr)
            return 2
        msgs = list_messages(args.thread_id)
        if args.json:
            print(
                json.dumps(
                    [
                        {
                            "id": m.id,
                            "role": m.role,
                            "content": m.content,
                            "created_at": m.created_at,
                            "retrieval_debug_id": m.retrieval_debug_id,
                        }
                        for m in msgs
                    ],
                    indent=2,
                )
            )
        else:
            for m in msgs:
                print(f"[{m.role}] {m.content}")
        return 0

    if args.cmd == "context":
        try:
            msgs = context_messages_for_thread(args.thread_id)
        except ThreadNotFoundError:
            print(f"Unknown thread: {args.thread_id}", file=sys.stderr)
            return 2
        for m in msgs:
            print(f"[{m.role}] {m.content}")
        return 0

    if args.cmd == "say":
        try:
            user_m, asst_m = post_user_message(
                args.thread_id,
                args.text,
                expand_for_retrieval=not args.no_expand,
                block_on_pii_in_query=not args.allow_pii_queries,
            )
        except ThreadNotFoundError:
            print(f"Unknown thread: {args.thread_id}", file=sys.stderr)
            return 2
        except Exception:
            logging.exception("post_user_message failed")
            return 1
        if args.json:
            print(
                json.dumps(
                    {
                        "user": {
                            "id": user_m.id,
                            "content": user_m.content,
                            "created_at": user_m.created_at,
                        },
                        "assistant": {
                            "id": asst_m.id,
                            "content": asst_m.content,
                            "created_at": asst_m.created_at,
                            "retrieval_debug_id": asst_m.retrieval_debug_id,
                        },
                    },
                    indent=2,
                )
            )
        else:
            print(asst_m.content)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
