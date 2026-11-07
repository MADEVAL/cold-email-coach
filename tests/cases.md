# Test cases

Run these before shipping a change to the skill. Each case states the input, the expected mode, and the pass criteria. A case fails if any criterion is missed.

## 1. Long pitched email

**Input:** a 250-word cold email that opens with "I hope this email finds you well", lists six features, praises the company, and asks for a demo plus a reply.

**Expected mode:** REWRITE.

**Pass criteria:**

- The checklist marks length, no-pitch, and one-CTA as FAIL.
- The rewritten body is 125 words or fewer.
- The rewritten email has exactly one question.
- No invented facts or metrics appear.

## 2. No personalization

**Input:** "Write a cold email to a Head of Support at a mid-size SaaS company about our ticket-routing tool. We cut response time."

**Expected mode:** WRITE.

**Pass criteria:**

- The first line contains an explicit placeholder such as `[PERSONALIZE: ...]`.
- No fake compliment, post, or mutual connection is invented.
- The output contains 2–3 variants, each with subject, body, and word count.

## 3. Two CTAs

**Input:** a short email ending with "Would you be open to a 15-minute call? Otherwise, reply with your thoughts or grab time on my calendar."

**Expected mode:** REVIEW (or REWRITE if the user asks to fix it).

**Pass criteria:**

- Item 5 is marked FAIL with the reason that there are multiple asks.
- The fix list says to keep exactly one question.
- If rewritten, the new email contains one question and no calendar link.

## 4. Non-English email

**Input:** a cold email in Russian, plus a request in Russian to check it.

**Expected mode:** REVIEW.

**Pass criteria:**

- The review is written in Russian.
- The same 11 checks are applied, with the same scoring.
- The tone stays conversational; no literal translation of English idioms.

## 5. Follow-up request

**Input:** "Write two follow-ups to this cold email. The prospect did not reply."

**Expected mode:** WRITE (follow-up variant).

**Pass criteria:**

- Each follow-up adds a new angle or a useful piece of information.
- No "just following up", "circling back", "bumping this", or guilt.
- The sequence has a clean exit and then stops.
- Each email is shorter than or equal to the original.

## 6. Missing required information

**Input:** "Write a cold email for my product."

**Expected mode:** WRITE, but no draft yet.

**Pass criteria:**

- The response asks no more than three short questions in one message.
- The questions cover recipient, offer, and problem.
- No email is generated from guesses.

## 7. Subject lines only

**Input:** "Give me five subject lines for an email about onboarding drop-off to a Head of CS."

**Expected mode:** WRITE (partial).

**Pass criteria:**

- Exactly five subject lines.
- Each is 1–6 words, neutral, lowercase or sentence case.
- No caps, exclamation marks, emoji, or fake "Re:"/"Fwd:".
- No extra commentary beyond a short heading.

## 8. Invented proof trap

**Input:** "Say we worked with three companies like theirs and improved onboarding by 40%." (No such data exists.)

**Expected mode:** WRITE.

**Pass criteria:**

- The skill refuses to invent the claim.
- It offers a placeholder or a version without the metric.
- It explains the refusal in one line, not a lecture.

## 9. Not a cold email

**Input:** a newsletter draft or an email to an existing customer.

**Expected mode:** REVIEW.

**Pass criteria:**

- The skill says in one line that this is not a cold email and stops.
- It does not apply the checklist to the wrong genre.

## 10. Review without rewriting

**Input:** an email pasted with "Rate this. Don't rewrite it."

**Expected mode:** REVIEW.

**Pass criteria:**

- Output is the 11-item checklist, a score, and up to three fixes.
- No rewritten email is included.
- The fixes are specific: what to cut or change, not "make it shorter".

## 11. Score format

**Input:** any email.

**Pass criteria:**

- All 11 items are listed, numbered 1–11.
- Each item has PASS or FAIL and a one-line reason.
- A score of the form `X/11` is present.
- No more than three fixes are listed.

## 12. Cliché detection

**Input:** an email containing "Hope this email finds you well", "I wanted to reach out", "quick call", and "at your earliest convenience".

**Pass criteria:**

- Item 9 is FAIL.
- At least two of the phrases are named in the reason.
- The fixes replace the phrases with concrete alternatives, not just "remove clichés".

## 13. Placeholder preservation

**Input:** "Use [PERSONALIZE: their recent launch] in the first line. Don't change it."

**Pass criteria:**

- The placeholder survives in the output exactly as written.
- The skill does not replace it with a guess.

## 14. Language of the request

**Input:** a request in English asking for an email to a German-speaking recipient, with no language specified.

**Pass criteria:**

- The skill asks or states the assumption in one line.
- It does not silently produce English if the recipient's language is clearly German.
- If it proceeds, the assumption is explicit.

## 15. Linter smoke test

**Input:** `tests/fixtures/bad-email.txt`, passed to `scripts/email_lint.py`.

**Pass criteria:**

- The script reports more than 125 words.
- It flags the subject line length and caps.
- It lists several clichés.
- It exits with a non-zero status when a hard check fails.

## Regression rule

If a change makes one case pass and another fail, the change is not ready. Fix the tension, do not relax the test.
