# Cold Email Coach

[skills.sh profile](https://www.skills.sh/madeval) - this skill is not indexed yet.

\[ **English** | [Русский](README.ru.md) \]

**Write the email a person would actually answer.**

Most cold emails fail for an unglamorous reason: they are about the sender. A paragraph of company history, a feature list, a demo request, and a "just following up" three days later. The recipient has no reason to care and no easy way to reply.

This is a skill for AI agents that fixes that. Give it who you are writing to, what you sell, and the problem it solves. It writes two or three short emails, scores them against an 11-point checklist, and cuts anything that still sounds like a campaign.

The rules come from two people who have thought harder about cold email than most: Josh Braun and Will Allred. Their principles are applied in original words. No quotes, no name-dropping, no affiliation.

## What it does

| Mode | Input | Output |
|---|---|---|
| **WRITE** | A recipient and an offer | 2-3 short emails with subject lines and word counts |
| **REVIEW** | An existing email | 11-item checklist, score out of 11, up to 3 fixes |
| **REWRITE** | An existing email | Short critique, score, then a fixed version |

It also handles follow-ups, subject lines, and the awkward case where you have no personalization fact. In that case it writes a placeholder instead of inventing a compliment.

## The 11 checks

Every email is scored on the same things:

1. 50-125 words.
2. The first line is about the recipient.
3. No pitch, no feature list.
4. A concrete problem or observation, not "we're the best".
5. Exactly one CTA, easy to answer.
6. "You" outnumbers "I/we".
7. Plain words, no jargon.
8. A short, neutral subject line.
9. No template openings or clichés.
10. No fake urgency or promised results.
11. It can be read aloud without cringing.

A score is a diagnostic, not a guarantee. The skill says so, and means it.

## Install

```bash
git clone https://github.com/MADEVAL/cold-email-coach.git
cd cold-email-coach
python install.py --target all
```

That copies the skill into:

- **Claude Code:** `~/.claude/skills/cold-email-coach`
- **OpenCode:** `~/.config/opencode/skills/cold-email-coach`
- **Portable:** `~/.agents/skills/cold-email-coach`

Useful flags:

```bash
python install.py --list     # where it is installed
python install.py --check    # compare installed copies with the repo
python install.py --target project   # install into ./.opencode/skills
```

No dependencies. Python 3.9+ is only needed for the optional linter and the installer.

## Use

Ask in plain language:

- "Write a cold email to a Head of Support at a 200-person SaaS. We sell ticket routing. Their support page promises a 12-hour first response."
- "Review this cold email. Don't rewrite it."
- "Rewrite this. It's 240 words and asks for a demo."
- "Three follow-ups. No reply to the first email."
- "Five subject lines about onboarding drop-off."
- "Write it in German. The recipient is in Berlin."

The skill chooses the mode automatically: an email pasted without instructions gets **REWRITE**, no email gets **WRITE**, and "rate this" gets **REVIEW**.

## What the output looks like

```text
Subject: week one

Dana - your post about 40% of new accounts never finishing setup stayed with me.
That number usually lives in a spreadsheet, and someone ends up chasing each
account by hand.

We make a small checklist tool for CS teams. It shows where each account gets
stuck, so nobody has to guess.

Is that still a problem for you, or is setup under control?

Yevhen, Founder at Relay

Words: 67
```

A review looks like this:

```text
1. Length - FAIL (213 words)
2. First line - FAIL ("I hope this email finds you well" is about the sender)
...
Score: 0/11

Top fixes
1. Replace the first two paragraphs with one observation about the recipient.
2. Cut from 213 to about 70 words.
3. Remove the demo, the calendar link, and the reply request. Keep one question.
```

## Optional linter

For a quick mechanical check:

```bash
python scripts/email_lint.py draft.txt
cat draft.txt | python scripts/email_lint.py
```

It reports word count, reading grade, you/I ratio, question and ask count, subject length, clichés, urgency words, caps, exclamations, links, and placeholders. It exits non-zero when a hard check fails.

It cannot judge relevance, personalization, or voice. That is still the model's job, and yours.

## Repository layout

| Path | Purpose |
|---|---|
| `SKILL.md` | The skill itself: modes, rules, checklist, workflow |
| `references/braun.md` | Problem-first outreach, permission to say no |
| `references/allred.md` | Brevity, readability, subject lines, follow-ups |
| `references/checklist.md` | Every check with pass/fail examples |
| `references/patterns.md` | Openers, subjects, CTAs, follow-up sequences |
| `references/anti-patterns.md` | Clichés and structural mistakes, with fixes |
| `examples/` | Worked examples for WRITE, REVIEW, REWRITE, follow-ups |
| `tests/cases.md` | 15 test cases and pass criteria |
| `scripts/email_lint.py` | Heuristic linter |
| `install.py` | Installer for Claude Code, OpenCode, and portable agents |

## Design decisions

- **Short beats clever.** 50-125 words. If it needs scrolling on a phone, it is not finished.
- **One ask.** A second CTA is not a backup plan. It is a reason to do nothing.
- **No invented facts.** No fake personalization, no imaginary customers, no made-up metrics. A placeholder is honest and gets filled in.
- **No fake urgency.** Real deadlines are fine. Manufactured ones cost trust.
- **Language follows the recipient.** The email is written in their language, not translated word for word from English.
- **Plain text.** No HTML, images, tracking pixels, or banner signatures.

## Limits

- It is not a CRM, a sequencer, or a deliverability tool.
- It cannot verify that your case study is real. You have to do that.
- The checklist is a diagnostic. A 10/11 email can still be irrelevant.
- No tool can promise replies. Anyone who does is selling something else.

## Contributing

Issues and pull requests are welcome. If a rule is wrong, bring an example. If a cliché is missing, add it with a replacement. Run the cases in `tests/cases.md` before opening a PR.

## License

MIT. Built by [Yevhen Leonidov](https://github.com/MADEVAL).

If this saves you an hour of rewriting, a star is nice. If it writes something embarrassing, open an issue.
