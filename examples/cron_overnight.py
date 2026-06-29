#!/usr/bin/env python3
"""cron_overnight.py — End-to-end example: overnight agent run → publish.

This script simulates a cron-driven agent pipeline:

1. An AI agent writes research output to a markdown file
2. agent_publish.convert() turns it into styled HTML
3. agent_publish.publish() pushes it to GitHub Pages

Usage:
    python examples/cron_overnight.py

Requires:
    pip install agentpub
    Set AGENT_PUBLISH_API_KEY (optional, for humanize/tldr/tags features)
    GitHub repo with Pages enabled at the configured base_url

Configuration:
    Reads agent-publish.toml from the current directory or ~/.config/agent-publish/
    Override with --config flag.
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

from agent_publish import Config, convert, load_config, publish


def simulate_agent_run() -> str:
    """Simulate an overnight AI agent producing research output.

    In a real pipeline this would be the output of an LLM call, a data
    analysis script, or a multi-agent collaboration session.

    Returns:
        Markdown string ready for conversion.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return dedent(f"""\
    ---
    title: Overnight Agent Summary — {today}
    type: daily
    author: Agent Pipeline
    tags: [auto-generated, research]
    ---

    # Overnight Agent Summary — {today}

    ## Highlights

    - **PR review queue**: 3 new PRs opened overnight (2 backend, 1 frontend)
    - **CI status**: All green — 142 tests passed across the monorepo
    - **Dependency update**: `httpx` 0.28.0 released, no breaking changes in our range
    - **Error spike**: `/api/v2/search` p99 latency jumped from 320ms → 890ms at 03:00 UTC

    ## Search Latency Investigation

    The overnight latency spike on `/api/v2/search` correlates with a new deployment
    at 02:45 UTC (commit `a1b2c3d`). Key findings:

    1. **Root cause**: The new caching layer is evicting entries 3× faster than
       expected because the default TTL was set to 60s instead of 300s.
    2. **Impact**: ~12,000 requests were affected over a 45-minute window.
    3. **Fix**: The on-call engineer rolled back at 03:45 UTC. Latency returned
       to baseline (280ms p99) by 03:50 UTC.
    4. **Action item**: Add TTL configuration guardrails to the deployment
       validation script (issue #847).

    ## Dependency Health

    | Package   | Current | Latest | Action   |
    |-----------|---------|--------|----------|
    | httpx     | 0.27.2  | 0.28.0 | Upgrade  |
    | fastapi   | 0.115.0 | 0.115.1| Patch    |
    | pydantic  | 2.10.0  | 2.10.1 | Patch    |
    | ruff      | 0.8.0   | 0.9.0  | Upgrade  |

    ## GitHub Activity

    - **3 PRs opened**: #846 (fix search TTL), #847 (add validation guardrails), #848 (docs update)
    - **2 PRs merged**: #844 (auth refactor), #845 (rate limiting)
    - **No new issues** filed overnight

    ## Tomorrow's Focus

    1. Review and merge #846 (TTL fix)
    2. Draft #847 validation guardrails RFC
    3. Schedule httpx and ruff upgrades for next deployment window
    """)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Overnight agent → publish pipeline example",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to agent-publish.toml or .yaml",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Convert to HTML but skip git push",
    )
    parser.add_argument(
        "--theme",
        default="default",
        choices=["default", "minimal", "brutalist", "editorial"],
        help="CSS theme",
    )
    parser.add_argument(
        "--skill",
        default=None,
        choices=[None, "article", "briefing", "changelog", "deck"],
        help="Skill template to use",
    )
    args = parser.parse_args()

    # 1. Load configuration
    config = load_config(args.config) if args.config else load_config()
    if not args.dry_run and not config.base_url:
        print("Error: Set base_url in config or pass --dry-run for testing")
        sys.exit(1)

    # 2. Simulate agent producing markdown output
    print("[1/4] Simulating overnight agent run...")
    markdown = simulate_agent_run()
    print(f"      Generated {len(markdown)} characters of markdown")

    # 3. Convert markdown to HTML using the public API
    print("[2/4] Converting to HTML...")
    result = convert(
        markdown,
        theme=args.theme,
        skill=args.skill,
        entry_type="daily",
        site_title="Agent Overnight Reports",
        author="AI Pipeline",
        show_toc=True,
        mermaid=True,
    )
    print(f"      Title: {result.title}")
    print(f"      Reading time: {result.reading_time} min")
    print(f"      Output: {result.output_path}")

    # 4. Publish to GitHub Pages
    if args.dry_run:
        print("[3/4] Dry run — skipping publish")
        print(f"      Would publish to: {config.base_url}/{config.output_dir}")
        print("[4/4] Done (dry run)")
    else:
        print("[3/4] Publishing to GitHub Pages...")
        pub_result = publish(
            html_path=result.output_path,
            title=result.title,
            fingerprint=result.fingerprint,
            config=config,
            asset_paths=result.assets_copied,
        )
        if pub_result.success:
            print(f"      {pub_result.message}")
            if pub_result.url:
                print(f"      View at: {pub_result.url}")
        else:
            print(f"      Failed: {pub_result.message}")
            sys.exit(1)
        print("[4/4] Done!")


if __name__ == "__main__":
    main()
