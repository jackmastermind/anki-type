# Type Before Show Answer Add-on

This add-on places a text area in Anki's reviewer bottom bar and blocks the *Show Answer* action until you type something into the box. The text you enter is not checked against the card's answer; it simply acts as a commitment mechanism before you self-grade.

## Installation

### AnkiWeb

TODO

### Manual
1. Copy the `anki-type` folder (containing `__init__.py` and `manifest.json`) into your Anki add-ons directory (typically ~/.local/share/Anki2/addons21 on Debian).
2. Restart Anki or reload the add-ons (`Tools → Add-ons → Reload`).

## Usage

During review, you'll see a “Write something before revealing the answer” field beneath the *Show Answer* button. The field auto-focuses when the question appears, so you can start typing immediately. Hit **Enter** (without modifiers) after writing to trigger *Show Answer* instantly, or click the button/press the space bar. If you attempt to reveal the answer with an empty field, the add-on highlights the box and shows a tooltip reminder.
