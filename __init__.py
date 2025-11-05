"""Require typing before revealing the answer in the reviewer."""

from __future__ import annotations

import logging
from typing import Callable

import aqt
from aqt import gui_hooks
from aqt.reviewer import Reviewer
from aqt.utils import tooltip

logger = logging.getLogger(__name__)

INPUT_ID = "anki-type-commitment-input"
WRAPPER_ID = "anki-type-wrapper"
CONTAINER_ID = "anki-type-commitment-container"
TOOLTIP_MESSAGE = "Type something before showing the answer."

# Timing constants (milliseconds)
FOCUS_DELAY_MS = 50  # Delay before focusing the input field

INSERT_INPUT_JS = """
(function() {{
    const middle = document.getElementById("middle");
    if (!middle) {{
        return;
    }}
    let wrapper = document.getElementById("{wrapper_id}");
    if (!wrapper) {{
        wrapper = document.createElement("div");
        wrapper.id = "{wrapper_id}";
        wrapper.style.display = "flex";
        wrapper.style.flexDirection = "column";
        wrapper.style.alignItems = "stretch";
        while (middle.firstChild) {{
            wrapper.appendChild(middle.firstChild);
        }}
        middle.appendChild(wrapper);
    }}

    let container = document.getElementById("{container_id}");
    if (!container) {{
        container = document.createElement("div");
        container.id = "{container_id}";
        container.style.marginTop = "8px";
        container.style.textAlign = "left";

        const label = document.createElement("label");
        label.textContent = "Write something before revealing the answer:";
        label.style.display = "block";
        label.style.fontSize = "0.9em";
        label.style.marginBottom = "4px";
        label.htmlFor = "{input_id}";

        const textarea = document.createElement("textarea");
        textarea.id = "{input_id}";
        textarea.rows = 3;
        textarea.style.width = "100%";
        textarea.style.boxSizing = "border-box";
        textarea.style.resize = "vertical";
        textarea.style.padding = "6px";
        textarea.dataset.ankiTypeCommitment = "1";

        container.appendChild(label);
        container.appendChild(textarea);
        wrapper.insertBefore(container, wrapper.firstChild);
    }} else {{
        const textarea = document.getElementById("{input_id}");
        if (textarea) {{
            textarea.value = "";
            textarea.style.boxShadow = "";
            if (!textarea.dataset.ankiTypeCommitment) {{
                textarea.dataset.ankiTypeCommitment = "1";
            }}
        }}
        if (wrapper && wrapper.firstChild !== container) {{
            wrapper.insertBefore(container, wrapper.firstChild);
        }}
    }}

    setTimeout(function() {{
        const textarea = document.getElementById("{input_id}");
        if (textarea) {{
            textarea.focus({{ preventScroll: true }});
            textarea.select();
        }}
    }}, {focus_delay_ms});

    const textarea = document.getElementById("{input_id}");
    if (textarea && !textarea.dataset.ankiTypeCommitmentHandler) {{
        textarea.addEventListener("keydown", function(evt) {{
            if (
                evt.key === "Enter" &&
                !evt.shiftKey &&
                !evt.altKey &&
                !evt.ctrlKey &&
                !evt.metaKey
            ) {{
                evt.preventDefault();
                pycmd("ans");
            }}
        }});
        textarea.dataset.ankiTypeCommitmentHandler = "1";
    }}
}})();
""".format(
    wrapper_id=WRAPPER_ID,
    container_id=CONTAINER_ID,
    input_id=INPUT_ID,
    focus_delay_ms=FOCUS_DELAY_MS,
)

GET_VALUE_JS = """
(function() {{
    const el = document.getElementById("{input_id}");
    return el ? el.value : "";
}})();
""".format(input_id=INPUT_ID)

WARN_INPUT_JS = """
(function() {{
    const el = document.getElementById("{input_id}");
    if (el) {{
        el.focus({{ preventScroll: true }});
        el.style.boxShadow = "0 0 0 2px rgba(220, 53, 69, 0.55)";
    }}
}})();
""".format(input_id=INPUT_ID)


def _bottom_web_available(reviewer: Reviewer) -> bool:
    bottom = getattr(reviewer, "bottom", None)
    return bool(bottom and getattr(bottom, "web", None))


def _call_with_commitment_text(
    reviewer: Reviewer, callback: Callable[[str], None]
) -> None:
    if not _bottom_web_available(reviewer):
        callback("")
        return

    def _wrapped(result: str | None) -> None:
        callback((result or "").strip())

    reviewer.bottom.web.evalWithCallback(GET_VALUE_JS, _wrapped)


def _warn_and_refocus(reviewer: Reviewer) -> None:
    tooltip(TOOLTIP_MESSAGE, parent=reviewer.mw, period=2000)
    if _bottom_web_available(reviewer):
        reviewer.bottom.web.eval(WARN_INPUT_JS)


def _on_show_question(card) -> None:  # type: ignore[override]
    reviewer = getattr(aqt.mw, "reviewer", None)
    if not reviewer or reviewer.card is None:
        return

    reviewer._anki_type_commitment_ready = False  # type: ignore[attr-defined]
    if _bottom_web_available(reviewer):
        reviewer.bottom.web.eval(INSERT_INPUT_JS)
        def _focus_bottom() -> None:
            if _bottom_web_available(reviewer):
                reviewer.bottom.web.setFocus()
        reviewer.mw.progress.single_shot(FOCUS_DELAY_MS, _focus_bottom)


def _patch_reviewer_methods() -> None:
    if hasattr(Reviewer, "_anki_type_original_get_typed_answer"):
        return

    Reviewer._anki_type_original_get_typed_answer = Reviewer._getTypedAnswer  # type: ignore[attr-defined]
    Reviewer._anki_type_original_show_answer = Reviewer._showAnswer  # type: ignore[attr-defined]

    def _gated_get_typed_answer(self: Reviewer) -> None:
        original: Callable[[Reviewer], None] = getattr(
            Reviewer, "_anki_type_original_get_typed_answer"
        )
        if getattr(self, "state", None) != "question":
            original(self)
            return

        def _after(text: str) -> None:
            try:
                if text:
                    self._anki_type_commitment_ready = True  # type: ignore[attr-defined]
                    original(self)
                else:
                    _warn_and_refocus(self)
            except Exception:
                logger.exception("Error in _gated_get_typed_answer callback, falling back to original")
                self._anki_type_commitment_ready = False  # type: ignore[attr-defined]
                original(self)

        try:
            _call_with_commitment_text(self, _after)
        except Exception:
            logger.exception("Error calling _call_with_commitment_text in _gated_get_typed_answer")
            original(self)

    def _gated_show_answer(self: Reviewer) -> None:
        original: Callable[[Reviewer], None] = getattr(
            Reviewer, "_anki_type_original_show_answer"
        )
        if getattr(self, "state", None) != "question":
            original(self)
            return

        if getattr(self, "_anki_type_commitment_ready", False):
            original(self)
            return

        def _after(text: str) -> None:
            try:
                if text:
                    self._anki_type_commitment_ready = True  # type: ignore[attr-defined]
                    original(self)
                else:
                    _warn_and_refocus(self)
            except Exception:
                logger.exception("Error in _gated_show_answer callback, falling back to original")
                self._anki_type_commitment_ready = False  # type: ignore[attr-defined]
                original(self)

        try:
            _call_with_commitment_text(self, _after)
        except Exception:
            logger.exception("Error calling _call_with_commitment_text in _gated_show_answer")
            original(self)

    Reviewer._getTypedAnswer = _gated_get_typed_answer  # type: ignore[assignment]
    Reviewer._showAnswer = _gated_show_answer  # type: ignore[assignment]


def _setup() -> None:
    _patch_reviewer_methods()
    gui_hooks.reviewer_did_show_question.append(_on_show_question)


_setup()
