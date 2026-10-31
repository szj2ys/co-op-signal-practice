# Co-op Signal Practice

A small offline exercise for two people to rehearse a shared nonverbal code before a silent co-op puzzle. It adds random practice turns, hidden sender cards and receiver readback checks to a static code table.

This is an independent, unofficial companion to [Big Walk Guide’s communication protocols](https://thebigwalk.world/en/protocols). It is not affiliated with House House or Panic and does not connect to a game, inspect game data or solve puzzles.

## Run

Open the [hosted practice tool](https://szj2ys.github.io/co-op-signal-practice/) or download `index.html` and open it in a modern browser. The downloaded file needs no server, build, installation, account or network connection.

## GitHub Pages

The repository is [szj2ys/co-op-signal-practice](https://github.com/szj2ys/co-op-signal-practice). To publish this static file, use Settings → Pages, choose **Deploy from a branch**, then select **main** and **/ (root)**. Keep `index.html` and the empty `.nojekyll` file at the root. No custom workflow, package installation or secrets are needed.

After GitHub finishes deployment, open the hosted URL and try a practice turn. A successful commit alone does not confirm that Pages is available. See [GitHub’s Pages setup instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).

## Practice

1. Agree on an ordering, starting at 1. Configure 2–256 items, 2–4 gestures and 2–6 repeats. Apply the setup.
2. Agree on the counting direction, each signal and a separate stop/restart signal. Gesture names are rehearsal labels; choose actions that work in your game.
3. The receiver looks away. The sender draws a target, reveals the sender card, and sends its code without speaking.
4. Hide the card and pass the device back. The receiver enters an item number, repeats that number back, and checks the readback.
5. If it does not match, keep the target and review the code. Swap roles when ready. Reset restores the defaults and clears the current turn.

## Printable worksheets

These optional Markdown sheets help a pair record its agreement and observations. Print them or keep your own local notes; the practice page does not read or save them.

- [Shared signal agreement](worksheets/agreement-sheet.md): define ordering, viewpoint, channels and confirmation.
- [Practice observations](worksheets/observation-sheet.md): record an intended choice and readback, then change one uncertain condition.
- [Pause and handover](worksheets/handover-sheet.md): distinguish confirmed state from an unfinished exchange when roles change.

The sheets are discussion aids, not an accessibility assessment, game-save feature or performance measure.

## Encoding

When the items fit within gestures × repeats, item i uses gesture floor((i − 1) / repeats), zero-based, with ((i − 1) % repeats) + 1 repetitions.

Otherwise each item uses exactly ceil(log2(items)) binary signals. Encode i − 1 including leading zeroes: No = 0, Yes = 1. For 36 items this takes six signals. Codes beyond the configured item range are unused and should prompt a stop and resend.

The shared table is available in the page. Random targets are generated locally; consecutive draws avoid repeating the same target. There is no timer or score.

## Privacy and limits

All state stays in memory; refresh clears the session. The page uses no analytics, cookies, browser storage, external assets or network requests. Its reference link opens the guide only when clicked.

This is a one-device exercise, not remote multiplayer. Hiding a card prevents accidental viewing, not deliberate inspection. A match checks agreement on a number, not gesture visibility, physical performance or in-game compatibility. Download the HTML for offline use; a hosted copy is not installed or cached for offline reload.

The code and text were created with AI assistance. No game assets or copied guide text are included.

## Verification

To rerun the local interaction checks, use `python verify_practice.py` in a Python environment with Playwright and its Chromium browser installed. The app itself has no dependencies. The script opens the local HTML in a fresh offline browser, exercises setup, sender/receiver turns, validation, reset, mobile layout and the contextual guide link, then writes `verification.json` and screenshots under `verification/`. These local checks do not verify public hosting, indexing, physical gesture visibility or integration with a game.

## License

Original code and text are MIT licensed. The linked guide and game names belong to their respective owners.
