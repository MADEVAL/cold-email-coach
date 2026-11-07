#!/usr/bin/env python3
"""Heuristic linter for cold emails.

This is a smoke test, not a verdict. It catches the mechanical problems that
are easy to measure: length, reading grade, pronoun balance, number of asks,
subject length, clichés, urgency words, caps, exclamation marks, and links.

It cannot judge relevance, personalization, or whether the email sounds human.

Usage:
    python scripts/email_lint.py draft.txt
    cat draft.txt | python scripts/email_lint.py
    python scripts/email_lint.py draft.txt --json

Exit codes:
    0  no hard check failed
    1  at least one hard check failed
    2  bad input
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TARGET_MIN_WORDS = 50
TARGET_MAX_WORDS = 125
HARD_MAX_WORDS = 160

CLICHES = [
    "hope this email finds you well",
    "hope you are doing well",
    "hope you're doing well",
    "hope all is well",
    "i hope i'm not bothering you",
    "i know you're busy",
    "i know you are busy",
    "i wanted to reach out",
    "i'm reaching out",
    "i am reaching out",
    "my name is",
    "we are a leading",
    "we're a leading",
    "companies like yours",
    "just following up",
    "following up on my last email",
    "circling back",
    "circle back",
    "bumping this",
    "touch base",
    "quick question",
    "quick call",
    "pick your brain",
    "at your earliest convenience",
    "please don't hesitate",
    "please do not hesitate",
    "i'd love to",
    "i would love to",
    "would you be open to",
    "as per my last email",
    "per my last email",
    "let's take this offline",
    "move the needle",
    "low-hanging fruit",
    "game changer",
    "game-changer",
    "revolutionary",
    "cutting-edge",
    "best-in-class",
    "world-class",
    "seamless",
    "robust",
    "synergy",
    "leverage",
    "utilize",
    "facilitate",
    "optimize",
    "streamline",
    "end-to-end",
    "pain points",
    "value-add",
    "no-brainer",
    "last chance",
    "act now",
    "limited time",
    "limited spots",
    "now or never",
    "guaranteed results",
    "10x your pipeline",
    "this will change everything",
]

URGENCY = [
    "last chance",
    "act now",
    "limited time",
    "limited spots",
    "hurry",
    "urgent",
    "asap",
    "don't miss",
    "do not miss",
    "expires",
    "today only",
    "final call",
    "now or never",
    "immediately",
]

PITCH_WORDS = [
    "platform",
    "solution",
    "leverage",
    "utilize",
    "streamline",
    "optimize",
    "robust",
    "seamless",
    "end-to-end",
    "synergy",
    "ecosystem",
    "empower",
    "cutting-edge",
    "best-in-class",
    "world-class",
    "game-changer",
    "revolutionary",
    "ai-powered",
    "real-time visibility",
    "pain points",
    "roi",
]

CTA_SIGNALS = [
    "book a",
    "book time",
    "schedule a",
    "schedule time",
    "15-minute",
    "30-minute",
    "demo",
    "call",
    "calendar",
    "reply",
    "let me know",
    "reach out",
    "get in touch",
    "sign up",
    "learn more",
    "website",
    "worth a look",
    "open to",
]

FIRST_PERSON = {
    "i", "me", "my", "mine", "we", "us", "our", "ours", "myself", "ourselves",
    "я", "меня", "мне", "мой", "моя", "моё", "мои", "мы", "нас", "нам", "наш",
    "наша", "наше", "наши",
}

SECOND_PERSON = {
    "you", "your", "yours", "yourself", "yourselves",
    "вы", "вас", "вам", "ваш", "ваша", "ваше", "ваши", "тебя", "тебе", "твой",
}

WORD_RE = re.compile(
    r"[A-Za-zА-Яа-яЁё0-9]+(?:['’-][A-Za-zА-Яа-яЁё0-9]+)*"
)
LATIN_WORD_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
SUBJECT_RE = re.compile(r"^\s*(?:subject|тема)\s*:\s*(.+)$", re.IGNORECASE)
LINK_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
CAPS_RE = re.compile(r"\b[A-ZА-ЯЁ]{2,}\b")
PLACEHOLDER_RE = re.compile(r"\[[^\]\n]+\]")


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def sentences(text: str) -> list[str]:
    parts = [p.strip() for p in SENTENCE_RE.split(text) if p.strip()]
    return parts or ([text.strip()] if text.strip() else [])


def syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    groups = re.findall(r"[aeiouy]{1,2}", w)
    return max(1, len(groups))


def reading_grade(body: str) -> float | None:
    latin = LATIN_WORD_RE.findall(body)
    if len(latin) < 10:
        return None
    sents = sentences(body)
    syl = sum(syllables(w) or 1 for w in latin)
    if not sents:
        return None
    grade = 0.39 * (len(latin) / len(sents)) + 11.8 * (syl / len(latin)) - 15.59
    return round(max(0.0, grade), 1)


def find_phrases(text: str, phrases: list[str]) -> list[str]:
    low = " " + re.sub(r"\s+", " ", text.lower()) + " "
    hits = []
    for phrase in phrases:
        if re.search(r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", low):
            hits.append(phrase)
    return hits


def first_content_line(body: str) -> str:
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    if not lines:
        return ""
    first = lines[0]
    if re.match(r"^(hi|hey|hello|dear|здравствуйте|привет|добрый день)\b", first, re.IGNORECASE):
        for line in lines[1:]:
            if re.match(r"^(hi|hey|hello|dear|здравствуйте|привет|добрый день)\b", line, re.IGNORECASE):
                continue
            return line
        return first
    return first


def sender_focused(first: str) -> bool:
    low = first.lower().strip()
    patterns = [
        r"^i\s", r"^i'", r"^i’", r"^we\s", r"^we'", r"^we’", r"^my\s", r"^our\s",
        r"^hope\b", r"^my name\b", r"^this is\b", r"^i am\b",
        r"^я\s", r"^мы\s", r"^меня\s", r"^наш",
    ]
    return any(re.search(p, low) for p in patterns)


def lint(raw: str, source: str) -> dict:
    text = raw.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    subject = ""
    body = text
    first_line = body.split("\n", 1)[0]
    m = SUBJECT_RE.match(first_line)
    if m:
        subject = m.group(1).strip()
        body = body.split("\n", 1)[1] if "\n" in body else ""
    body = body.strip()

    body_words = words(body)
    word_count = len(body_words)
    sent_list = sentences(body)
    avg_sentence = round(word_count / len(sent_list), 1) if sent_list else 0.0
    grade = reading_grade(body)

    low = body.lower()
    first_person = sum(1 for w in body_words if w.lower() in FIRST_PERSON)
    second_person = sum(1 for w in body_words if w.lower() in SECOND_PERSON)
    ratio = round(second_person / first_person, 2) if first_person else float(second_person)

    questions = body.count("?")
    ask_sentences = [s for s in sent_list if s.rstrip().endswith("?") or find_phrases(s, CTA_SIGNALS)]
    asks = len(ask_sentences)
    subject_words = words(subject)
    subject_count = len(subject_words)
    cliches = find_phrases(body, CLICHES)
    urgency = find_phrases(body, URGENCY)
    pitch = find_phrases(body, PITCH_WORDS)
    exclamations = body.count("!") + subject.count("!")
    caps = CAPS_RE.findall(subject + " " + body)
    links = LINK_RE.findall(body)
    placeholders = PLACEHOLDER_RE.findall(body)
    first = first_content_line(body)

    checks: dict[str, dict] = {}

    def add(name, status, value, detail):
        checks[name] = {"status": status, "value": value, "detail": detail}

    # Length
    if word_count < TARGET_MIN_WORDS:
        status = "WARN" if word_count >= 40 else "FAIL"
    elif word_count <= TARGET_MAX_WORDS:
        status = "PASS"
    elif word_count <= HARD_MAX_WORDS:
        status = "FAIL"
    else:
        status = "FAIL"
    add("length", status, word_count, f"target {TARGET_MIN_WORDS}-{TARGET_MAX_WORDS}, hard ceiling {HARD_MAX_WORDS}")

    # Reading grade
    if grade is None:
        add("reading_grade", "INFO", None, "not enough English text to estimate")
    elif grade <= 6:
        add("reading_grade", "PASS", grade, "target 3-5, ceiling 6")
    elif grade <= 8:
        add("reading_grade", "WARN", grade, "target 3-5, ceiling 6")
    else:
        add("reading_grade", "FAIL", grade, "target 3-5, ceiling 6")

    # Sentence length
    if avg_sentence <= 15:
        add("sentence_length", "PASS", avg_sentence, "target <= 15 words")
    elif avg_sentence <= 20:
        add("sentence_length", "WARN", avg_sentence, "target <= 15 words")
    else:
        add("sentence_length", "FAIL", avg_sentence, "target <= 15 words")

    # Pronoun balance
    if ratio >= 1:
        add("you_vs_i", "PASS", f"{second_person}:{first_person}", f"ratio {ratio}")
    elif ratio >= 0.5:
        add("you_vs_i", "WARN", f"{second_person}:{first_person}", f"ratio {ratio}, target >= 1")
    else:
        add("you_vs_i", "FAIL", f"{second_person}:{first_person}", f"ratio {ratio}, target >= 1")

    # Questions / asks
    if questions == 1:
        add("questions", "PASS", questions, "target exactly 1")
    elif questions == 0:
        add("questions", "WARN", questions, "no question found; every cold email needs one clear ask")
    else:
        add("questions", "FAIL", questions, "more than one question; keep one ask")

    # Explicit CTA sentences
    if asks == 1:
        add("asks", "PASS", asks, "one clear ask")
    elif asks == 0:
        add("asks", "WARN", asks, "no ask found; give the recipient one easy next step")
    else:
        add("asks", "FAIL", asks, "multiple asks; keep one")

    # Subject
    if not subject:
        add("subject", "FAIL", None, "no Subject: line found")
    else:
        if subject_count > 9:
            subj_status = "FAIL"
        elif subject_count > 6:
            subj_status = "WARN"
        else:
            subj_status = "PASS"
        if CAPS_RE.search(subject) or "!" in subject:
            subj_status = "FAIL"
        add("subject", subj_status, subject_count, "target 1-6 words, no caps, no exclamation marks")

    # Clichés
    if not cliches:
        add("cliches", "PASS", 0, "none found")
    elif len(cliches) <= 2:
        add("cliches", "WARN", len(cliches), ", ".join(cliches))
    else:
        add("cliches", "FAIL", len(cliches), ", ".join(cliches))

    # Urgency
    if not urgency:
        add("urgency", "PASS", 0, "none found")
    elif len(urgency) == 1:
        add("urgency", "WARN", 1, ", ".join(urgency))
    else:
        add("urgency", "FAIL", len(urgency), ", ".join(urgency))

    # Pitch words
    if not pitch:
        add("pitch_words", "PASS", 0, "none found")
    elif len(pitch) <= 2:
        add("pitch_words", "WARN", len(pitch), ", ".join(pitch))
    else:
        add("pitch_words", "FAIL", len(pitch), ", ".join(pitch))

    # Exclamations
    if exclamations == 0:
        add("exclamations", "PASS", 0, "none found")
    elif exclamations == 1:
        add("exclamations", "WARN", 1, "one is enough to sound like a campaign")
    else:
        add("exclamations", "FAIL", exclamations, "remove them all")

    # ALL CAPS
    if not caps:
        add("all_caps", "PASS", 0, "none found")
    else:
        add("all_caps", "WARN", len(caps), ", ".join(caps[:8]))

    # Links
    if not links:
        add("links", "PASS", 0, "none found")
    elif len(links) == 1:
        add("links", "WARN", 1, "one link at most; make sure it earns its place")
    else:
        add("links", "FAIL", len(links), "remove all but one, or none")

    # First line
    if not first:
        add("first_line", "FAIL", "", "no body text")
    elif sender_focused(first):
        add("first_line", "WARN", first, "starts with the sender, not the recipient")
    else:
        add("first_line", "PASS", first, "starts with the recipient or a neutral observation")

    # Placeholders are informational; they are intentional during drafting.
    add("placeholders", "INFO", len(placeholders), ", ".join(placeholders) if placeholders else "none")

    statuses = [c["status"] for c in checks.values()]
    failed = statuses.count("FAIL")
    warned = statuses.count("WARN")
    passed = statuses.count("PASS")

    return {
        "source": source,
        "subject": subject,
        "word_count": word_count,
        "sentences": len(sent_list),
        "avg_sentence_words": avg_sentence,
        "reading_grade": grade,
        "first_person": first_person,
        "second_person": second_person,
        "you_vs_i": ratio,
        "questions": questions,
        "asks": asks,
        "cliche_count": len(cliches),
        "cliches": cliches,
        "urgency": urgency,
        "pitch_words": pitch,
        "exclamations": exclamations,
        "caps": caps,
        "links": len(links),
        "placeholders": placeholders,
        "first_line": first,
        "checks": checks,
        "summary": {"passed": passed, "warnings": warned, "failed": failed},
        "ok": failed == 0,
    }


SYMBOL = {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL", "INFO": "INFO"}


def render(result: dict) -> str:
    lines = []
    lines.append("Cold email lint")
    lines.append("=" * 15)
    lines.append(f"Source: {result['source']}")
    if result["subject"]:
        lines.append(f"Subject: {result['subject']}")
    lines.append("")
    order = [
        ("length", "Words"),
        ("reading_grade", "Reading grade"),
        ("sentence_length", "Avg sentence"),
        ("you_vs_i", "You vs I"),
        ("questions", "Questions"),
        ("asks", "Asks"),
        ("subject", "Subject words"),
        ("cliches", "Clichés"),
        ("urgency", "Urgency"),
        ("pitch_words", "Pitch words"),
        ("exclamations", "Exclamations"),
        ("all_caps", "ALL CAPS"),
        ("links", "Links"),
        ("first_line", "First line"),
    ]
    for key, label in order:
        check = result["checks"][key]
        value = check["value"]
        if value is None:
            value = "-"
        detail = check["detail"]
        line = f"{label:<16} {str(value):<28} [{SYMBOL[check['status']]}]"
        if detail:
            line += f" {detail}"
        lines.append(line)
    if result["placeholders"]:
        lines.append(f"{'Placeholders':<16} {len(result['placeholders']):<28} [INFO] {', '.join(result['placeholders'])}")
    lines.append("")
    lines.append(f"Sentences: {result['sentences']} | Avg words per sentence: {result['avg_sentence_words']}")
    lines.append(f"First line: {result['first_line']!r}")
    lines.append("")
    s = result["summary"]
    lines.append(f"Passed: {s['passed']} | Warnings: {s['warnings']} | Failed: {s['failed']}")
    if s["failed"]:
        lines.append("Result: needs work. Fix the FAIL items before sending.")
    elif s["warnings"]:
        lines.append("Result: usable, with warnings. Read each one; some are intentional.")
    else:
        lines.append("Result: clean on the measurable checks. Relevance is still a human call.")
    lines.append("")
    lines.append("Reminder: this script cannot judge personalization, relevance, or voice.")
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Heuristic linter for cold emails.")
    parser.add_argument("file", nargs="?", help="Email file. If omitted, read stdin.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a report.")
    args = parser.parse_args()

    try:
        if args.file:
            path = Path(args.file)
            raw = path.read_text(encoding="utf-8")
            source = str(path)
        else:
            raw = sys.stdin.read()
            source = "<stdin>"
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not raw.strip():
        print("error: empty input", file=sys.stderr)
        return 2

    result = lint(raw, source)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
