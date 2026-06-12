---
description: Log a job application — classify against P1–P5 profiles, write Obsidian candidature note + 7-day relance task (via obsidian-crm)
---

Run the `log-application` skill from the `jobsearch` plugin: given the pasted job offer (and the source — LinkedIn / WTTJ / direct / referral / other), classify it against the P1–P5 profile taxonomy from `cv-generator`, then compose the global `obsidian-crm` skill to create one `opportunite-js` candidature note (with `source`, `target_profile`, `lien_offre`, body = pasted offer) and one `tache` relance with `etiquettes: ["jobsearch"]` and `echeance: today + 7d`. Tomorrow morning, `/briefing` will surface the relance.
