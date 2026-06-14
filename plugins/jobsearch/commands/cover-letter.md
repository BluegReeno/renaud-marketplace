---
description: Generate a tailored cover letter for Renaud Laborbe based on a job offer. Detects profile × company type from the offer, applies cell-specific narrative rules, and produces a 3-paragraph letter anchored in real, verifiable experience. No boilerplate.
---

Run the `cover-letter` skill from the `jobsearch` plugin: given the pasted job offer (or description of target role + company type), detect the right profile × company-type cell (same 15-cell matrix as the CV generator), load the matching profile narrative rules from `profiles/p<n>_*.md`, and generate a 3-paragraph cover letter (~300 words EN / ~330 words FR) using only real verifiable facts (EnBW France, Valorem, IC Ingénieurs, Open Ocean team/funding, Artelia P&L). No standard HR boilerplate — open with a hook, close with confidence. Output directly in the conversation, followed by a one-line meta: _Profile: ... × ... · Language: ..._
