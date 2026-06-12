---
description: Generate a 5-section interview prep note for a candidature, profile-positioned per the candidature's target_profile (via obsidian-crm)
---

Run the `interview-prep` skill from the `jobsearch` plugin: given the candidature name (or company + role), invoke `obsidian-crm` to read the candidature's frontmatter (including `target_profile`) and body, then read the matching `profiles/p<n>_*.md` narrative, and create one `entretien` note (`categorie: "Préparation"`) under `CRM-JobSearch/Entretiens/` with the always-identical 5-section body: Société · Résumé de la JD · Pitch (positionné P<n>) · Cas du parcours pertinents · Questions probables de l'interlocuteur. Same structure every time; the pitch is profile-positioned so the interview matches the CV.
