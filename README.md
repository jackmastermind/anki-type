# Type Before Show Answer Add-on

This add-on places a text area in Anki's reviewer bottom bar and blocks the *Show Answer* action until you type something into the box. The text you enter is not checked against the card's answer; it simply acts as a commitment mechanism before you self-grade.

## Installation

### AnkiWeb (Recommended)

Coming soon! This add-on will be available on AnkiWeb at: https://ankiweb.net/shared/addons/

### From GitHub Releases

1. Download the latest `.ankiaddon` file from the [Releases page](https://github.com/jackmastermind/anki-type/releases)
2. Open Anki and go to `Tools → Add-ons`
3. Click `Install from file...` and select the downloaded `.ankiaddon` file
4. Restart Anki

### Manual Installation

1. Clone or download this repository
2. Copy the contents (not the folder itself) into your Anki add-ons directory:
   - Windows: `%APPDATA%\Anki2\addons21\anki-type\`
   - Mac: `~/Library/Application Support/Anki2/addons21/anki-type/`
   - Linux: `~/.local/share/Anki2/addons21/anki-type/`
3. Restart Anki or reload add-ons (`Tools → Add-ons → Reload`)

## Building from Source

To create a `.ankiaddon` package yourself:

```bash
python build.py
```

This will create `dist/anki-type-{version}.ankiaddon` which can be installed in Anki or uploaded to AnkiWeb.

## Usage

During review, you'll see a “Write something before revealing the answer” field beneath the *Show Answer* button. The field auto-focuses when the question appears, so you can start typing immediately. Hit **Enter** (without modifiers) after writing to trigger *Show Answer* instantly, or click the button/press the space bar. If you attempt to reveal the answer with an empty field, the add-on highlights the box and shows a tooltip reminder.
