"""Browser smoke test for the self-contained interactive map."""
from __future__ import annotations

from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest


ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def static_server():
    handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(*args, directory=str(ROOT), **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()


def test_map_controls_preserve_shareable_state_and_disable_invalid_nai_difference():
    sync_api = pytest.importorskip("playwright.sync_api")
    with static_server() as base_url, sync_api.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:  # Browser binaries are optional in this repo.
            pytest.skip(f"Playwright Chromium unavailable: {exc}")
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(f"{base_url}/outputs/maps/ocean_park_interactive.html", wait_until="networkidle", timeout=30_000)
        page.wait_for_selector("#grid-mode")
        page.select_option("#grid-mode", "nai")
        assert page.locator('#scenario-sel option[value="difference"]').evaluate("option => option.disabled")
        page.select_option("#grid-mode", "smci")
        page.select_option("#scenario-sel", "difference")
        page.wait_for_timeout(200)
        assert "scenario=difference" in page.url and "metric=smci" in page.url
        page.get_by_role("button", name="Population exposure").click()
        page.wait_for_timeout(200)
        assert "metric=exposure" in page.url
        browser.close()
        assert not errors


def test_map_hides_secondary_controls_until_a_user_requests_them():
    sync_api = pytest.importorskip("playwright.sync_api")
    with static_server() as base_url, sync_api.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:  # Browser binaries are optional in this repo.
            pytest.skip(f"Playwright Chromium unavailable: {exc}")
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(f"{base_url}/outputs/maps/ocean_park_interactive.html", wait_until="networkidle", timeout=30_000)
        assert page.locator("#primary-controls").is_visible()
        assert not page.locator("#advanced-layers").evaluate("panel => panel.open")
        assert not page.locator("#chk-grid").is_visible()
        page.locator("#advanced-layers summary").click()
        assert page.locator("#chk-grid").is_visible()
        browser.close()
