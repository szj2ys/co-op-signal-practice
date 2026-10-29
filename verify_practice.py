"""Independent browser interaction checks. No shared profile or network needed."""
from pathlib import Path
import json
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "verification"
OUT.mkdir(exist_ok=True)
checks = []
def record(name, detail):
    checks.append({"check": name, "status": "PASS", "detail": detail})
def expect(condition, description):
    assert condition, description

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 1000}, offline=True)
    page = context.new_page()
    errors, requests = [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("request", lambda request: requests.append(request.url))
    page.goto((ROOT / "index.html").as_uri())
    expect(page.locator("#guess").is_disabled(), "Guess must begin disabled")
    expect(page.locator("#check").is_disabled(), "Check must begin disabled")
    expect(page.locator("#toggle-card").is_disabled(), "Reveal must begin disabled")
    expect(page.locator("#sender-card").is_hidden(), "Card starts hidden")
    expect(page.locator("#code-rows tr").count() == 9, "Default table has nine rows")
    record("offline_initial_state", "Loaded from file:// with context offline; controls disabled and sender card hidden.")

    def apply(n, channels="3", repeats="4"):
        page.locator("#options").fill(str(n))
        page.locator("#channels").select_option(channels)
        page.locator("#repeats").select_option(repeats)
        page.get_by_role("button", name="Apply setup").click()
    def reveal():
        page.locator("#draw").click()
        expect(page.locator("#sender-card").is_hidden(), "Draw must not show target")
        page.locator("#toggle-card").click()
        return int(page.locator("#target").inner_text().split()[-1])
    def outcome():
        return page.locator("#feedback").get_attribute("data-outcome")
    def guess(n, readback=True):
        page.locator("#guess").fill(str(n))
        if readback:
            page.locator("#readback").check()
        page.locator("#check").click()

    # Use keyboard for target/reveal controls.
    page.locator("#draw").focus()
    page.keyboard.press("Enter")
    page.locator("#toggle-card").focus()
    page.keyboard.press("Space")
    target = int(page.locator("#target").inner_text().split()[-1])
    label = ["Left hand", "Right hand", "Both hands"][(target - 1) // 4]
    count = (target - 1) % 4 + 1
    expect(page.locator("#signal").inner_text() == f"{label} · {count} " + ("repeat" if count == 1 else "repeats"), "Independent nine-item gesture encoding")
    guess(target)
    expect(outcome() == "invalid" and "Hide" in page.locator("#feedback").inner_text(), "Visible card blocks answer confirmation")
    page.locator("#toggle-card").click()
    guess(target, readback=False)
    expect(outcome() == "invalid" and "Repeat" in page.locator("#feedback").inner_text(), "Readback checkbox required")
    wrong = target % 9 + 1
    guess(wrong)
    expect(outcome() == "retry", "Wrong guess permits retry")
    expect(str(target) not in page.locator("#feedback").inner_text(), "Wrong answer does not disclose target")
    page.locator("#toggle-card").click()
    expect(page.locator("#target").inner_text() == f"Item {target}", "Wrong guess keeps same target")
    page.locator("#toggle-card").click()
    guess(target)
    expect(outcome() == "correct", "Correct gesture readback matches")
    old = target
    target = reveal()
    expect(target != old, "New target should avoid preceding target")
    page.locator("#toggle-card").click()
    record("nine_item_gesture_turn", f"Keyboard draw/reveal; item {old} encoded correctly, visible-card/readback gates, wrong retry, correct answer and nonrepeating next target.")

    for invalid in ["", "1", "257", "2.5"]:
        page.locator("#options").fill(invalid)
        page.get_by_role("button", name="Apply setup").click()
        expect("has not changed" in page.locator("#setup-error").inner_text(), f"Invalid setup {invalid!r} rejected")
        expect(page.locator("#code-rows tr").count() == 9, "Invalid setup preserves active table")
        expect(page.locator("#toggle-card").is_enabled(), "Invalid setup preserves turn")
    record("invalid_setup", "Blank, 1, 257 and 2.5 rejected; existing nine-item setup and turn preserved.")

    apply(36)
    expect(page.locator("#guess").is_disabled(), "Applying setup clears turn")
    expect("fixed-width" in page.locator("#mode").inner_text(), "36 selects binary")
    target = reveal()
    signals = page.locator("#bits li").all_text_contents()
    expect(len(signals) == 6, "36 items needs six signals")
    expect(all(v in ("Yes", "No") for v in signals), "Only binary signals")
    decoded = int("".join("1" if v == "Yes" else "0" for v in signals), 2) + 1
    expect(decoded == target, "Item-1 binary mapping decodes to sender item")
    page.screenshot(path=str(OUT / "binary-card.png"), full_page=True)
    page.locator("#toggle-card").click()
    for invalid in ["", "0", "37", "1.5"]:
        guess(invalid)
        expect(outcome() == "invalid" and "whole item" in page.locator("#feedback").inner_text(), f"Invalid guess {invalid!r} rejected")
    guess(target)
    expect(outcome() == "correct", "Correct binary readback matches")
    # Changing the received value revokes an earlier readback confirmation.
    page.locator("#guess").fill(str(target % 36 + 1))
    expect(not page.locator("#readback").is_checked(), "Editing guess resets readback checkbox")
    record("36_item_binary_turn", f"Item {target} encoded as six Yes/No signals; independent decoding matched; invalid guesses rejected and corrected readback accepted.")

    apply(256)
    expect(page.locator("#code-rows tr").count() == 256, "256 boundary table")
    page.locator("#codebook summary").click()
    first = page.locator("#code-rows tr").first.locator("td").nth(1).inner_text().split(" → ")
    last = page.locator("#code-rows tr").last.locator("td").nth(1).inner_text().split(" → ")
    expect(first == ["No"] * 8, "Item1 uses eight No signals")
    expect(last == ["Yes"] * 8, "Item256 uses eight Yes signals")
    target = reveal()
    signals = page.locator("#bits li").all_text_contents()
    expect(len(signals) == 8, "256 uses eight signals")
    expect(int("".join("1" if x == "Yes" else "0" for x in signals), 2) + 1 == target, "256 boundary target decoding")
    page.locator("#toggle-card").click()
    guess(target)
    expect(outcome() == "correct", "256 answer accepted")
    record("256_item_boundary", "256 rows, item1 eight No signals, item256 eight Yes signals, random eight-bit target decoded and confirmed.")

    apply(24, "4", "6")
    expect("numbered gestures" in page.locator("#mode").inner_text(), "Capacity boundary stays gestures")
    expect(page.locator("#code-rows tr").last.locator("td").nth(1).inner_text() == "Fourth agreed gesture · 6 repeats", "Capacity last gesture valid")
    apply(25, "4", "6")
    expect("fixed-width" in page.locator("#mode").inner_text(), "One above capacity chooses binary")
    expect("exactly 5 signals" in page.locator("#encoding-note").inner_text(), "25 uses five bits")
    apply(2, "2", "2")
    target = reveal()
    expect(page.locator("#signal").inner_text() == "Left hand · " + str(target) + (" repeat" if target == 1 else " repeats"), "Minimum configuration")
    page.locator("#toggle-card").click()
    guess(target)
    expect(outcome() == "correct", "Minimum configuration answer accepted")
    record("capacity_boundaries", "2-item lower bound, 24-item gesture capacity (4 × 6), and 25-item transition to five-bit binary verified.")

    page.locator("#reset").click()
    expect(page.locator("#options").input_value() == "9", "Reset options")
    expect(page.locator("#channels").input_value() == "3", "Reset gestures")
    expect(page.locator("#repeats").input_value() == "4", "Reset repeats")
    expect(page.locator("#guess").is_disabled() and page.locator("#sender-card").is_hidden(), "Reset clears practice")
    record("reset", "Restored 9/3/4 defaults and cleared target, answer and confirmation.")
    page.screenshot(path=str(OUT / "desktop.png"), full_page=True)

    links = page.locator("a").evaluate_all("(els) => els.map(a => ({href:a.href, rel:a.getAttribute('rel'), text:a.textContent}))")
    expect(len(links) == 1, "One contextual citation only")
    expect(links[0]["href"] == "https://thebigwalk.world/en/protocols", "Exact approved instructional URL")
    expect(not (set((links[0]["rel"] or "").lower().split()) & {"nofollow", "sponsored", "ugc"}), "Citation does not opt out of following")
    record("actual_outgoing_link", links[0])

    page.set_viewport_size({"width": 375, "height": 812})
    expect(page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth"), "No mobile horizontal overflow")
    apply(256)
    reveal()
    page.locator("#codebook").evaluate("(el) => el.open = true")
    expect(page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth"), "Long binary/table mobile stays within viewport")
    page.screenshot(path=str(OUT / "mobile.png"), full_page=True)
    labels = page.locator("input, select").evaluate_all("(els) => els.map(el=>({id:el.id,labels:el.labels.length}))")
    expect(all(x["labels"] > 0 for x in labels), "Inputs have actual associated labels")
    page.locator("#draw").focus()
    page.keyboard.press("Tab")
    expect(page.locator("#toggle-card").evaluate("el=>el===document.activeElement"), "Keyboard tab reaches reveal button")
    focus = page.locator("#toggle-card").evaluate("(el)=>({outline:getComputedStyle(el).outlineStyle,width:getComputedStyle(el).outlineWidth})")
    expect(focus["outline"] != "none" and focus["width"] != "0px", "Keyboard focus indicator is visible")
    record("phone_and_accessibility_basics", {"width":375,"no_document_overflow":True,"input_labels":labels,"focus":focus})

    expect(not errors, f"Browser errors: {errors}")
    expect(all(url.startswith("file:") or url.startswith("data:") for url in requests), f"Unexpected network request: {requests}")
    expect(context.cookies() == [], "No cookies")
    expect(page.evaluate("localStorage.length + sessionStorage.length") == 0, "No browser storage")
    record("runtime_privacy", {"page_errors":errors,"requests":requests,"cookies":0,"storage_entries":0,"offline":True,"shared_profile_used":False})
    browser.close()

report = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "manual_browser_verdict": "PASS",
    "browser": "Playwright bundled Chromium, headless, fresh anonymous offline context",
    "check_count": len(checks),
    "checks": checks,
    "screenshots": ["verification/desktop.png", "verification/binary-card.png", "verification/mobile.png"],
    "not_covered": [
        "No automatic repository check is configured for index.html, README.md or LICENSE.",
        "No public hosting, account or publication was tested by these local checks.",
        "Physical gesture visibility, two-human usability and integration with any game are not verified.",
        "Only Chromium was exercised; assistive technology and other browsers were not tested.",
        "Followed citation markup does not establish search indexing, rankings or an externally published backlink."
    ]
}
(ROOT / "verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(f"PASS: {len(checks)} real browser checks; evidence: {ROOT / 'verification.json'}")

