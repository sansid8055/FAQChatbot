"""Run §9 API with uvicorn: ``python -m runtime.phase_9_api``."""

from __future__ import annotations

from ingest.repo_dotenv import load_repo_dotenv


def main() -> None:
    load_repo_dotenv()
    import uvicorn

    from runtime.phase_9_api.config import api_host, api_port

    uvicorn.run(
        "runtime.phase_9_api.app:app",
        host=api_host(),
        port=api_port(),
        reload=False,
    )


if __name__ == "__main__":
    main()
