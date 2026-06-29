#!/usr/bin/env python3
"""Note schema definitions and validation — Job-Search vault slice (5 types).

Carved out of the global `obsidian-crm` note_schemas. This copy owns ONLY the
job-search note types:

    opportunite-js · entreprise-js · contact-js · entretien · tache (jobsearch)

The `entretien` schema ships the categorie/interlocuteurs fix from day one, so
creating a Préparation/Compte-rendu interview note raises zero "unknown field"
warnings.

Self-contained module — no dependency on migration scripts or any *-bg type.

Public API:
    validate_create(note_type, fields) -> ValidationResult
    validate_update(note_type, field_name, value) -> ValidationResult
    get_schema(note_type) -> NoteSchema | None

Run directly for self-tests:
    python note_schemas.py
"""

import re
import sys
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class FieldDef:
    """Schema definition for a single frontmatter field."""
    name: str
    ftype: str  # string|date|number|bool|url|wikilink|list|wikilink_list|enum
    required: bool = False
    enum_values: list = field(default_factory=list)


@dataclass
class NoteSchema:
    """Schema for a note type."""
    note_type: str
    folder: str
    fields: dict  # name -> FieldDef
    body_sections: list = field(default_factory=list)  # list of heading strings


@dataclass
class ValidationResult:
    """Result of a validation check."""
    errors: list = field(default_factory=list)   # blocking
    warnings: list = field(default_factory=list)  # non-blocking

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


# Fields silently allowed on all note types (legacy/system fields).
# NOTE: target_profile is intentionally NOT here — log-application writes it onto
# opportunite-js notes and relies on the resulting non-blocking "unknown field"
# warning as its documented escape-hatch contract. Keep parity with obsidian-crm.
LEGACY_FIELDS = {"notion_id"}


# ---------------------------------------------------------------------------
# Enum value sets (job-search only)
# ---------------------------------------------------------------------------

JS_STATUTS = [
    "📝 À postuler",
    "📋 CV préparé — à envoyer",
    "✉️ Candidature envoyée",
    "📞 Entretien prévu",
    "🔄 Relance à faire",
    "🔍 À analyser",
    "❌ Refus",
    "✅ Offre reçue",
    "⏸️ En pause",
]

ENTRETIEN_CATEGORIES = [
    "Préparation",
    "Compte-rendu",
]

# tache closed states are "Terminé" / "Archivé" (NOT "Terminée" / "Annulée").
TACHE_ETATS = [
    "Pas commencée",
    "Today",
    "En cours",
    "Terminé",
    "Archivé",
]

TACHE_PRIORITES = [
    "Basse",
    "Moyenne",
    "Haute",
    "Urgent",
]


# ---------------------------------------------------------------------------
# Helper: build fields dict from list of FieldDefs
# ---------------------------------------------------------------------------

def _fields(*defs: FieldDef) -> dict:
    return {d.name: d for d in defs}


# ---------------------------------------------------------------------------
# Schema definitions — 5 job-search note types
# ---------------------------------------------------------------------------

SCHEMAS: dict[str, NoteSchema] = {}


def _register(schema: NoteSchema):
    SCHEMAS[schema.note_type] = schema


_register(NoteSchema(
    note_type="opportunite-js",
    folder="CRM-JobSearch/Opportunites",
    fields=_fields(
        FieldDef("statut", "enum", enum_values=JS_STATUTS),
        FieldDef("entreprise", "wikilink"),
        FieldDef("contact_principal", "wikilink"),
        FieldDef("date_candidature", "date"),
        FieldDef("date_relance", "date"),
        FieldDef("prochain_rdv", "date"),
        FieldDef("source", "string"),
        FieldDef("score_match", "number"),
        FieldDef("priorite", "string"),
        FieldDef("type_contrat", "string"),
        FieldDef("teletravail", "string"),
        FieldDef("salaire_propose", "string"),
        FieldDef("localisation", "string"),
        FieldDef("lien_offre", "url"),
    ),
))

_register(NoteSchema(
    note_type="entreprise-js",
    folder="CRM-JobSearch/Entreprises",
    fields=_fields(
        FieldDef("secteur", "string"),
        FieldDef("taille", "string"),
        FieldDef("interet", "string"),
        FieldDef("localisation_hq", "string"),
        FieldDef("site_web", "url"),
        FieldDef("linkedin", "url"),
        FieldDef("glassdoor", "url"),
    ),
))

_register(NoteSchema(
    note_type="contact-js",
    folder="CRM-JobSearch/Contacts",
    fields=_fields(
        FieldDef("entreprise", "wikilink"),
        FieldDef("role", "string"),
        FieldDef("email", "string"),
        FieldDef("telephone", "string"),
        FieldDef("linkedin", "url"),
    ),
))

_register(NoteSchema(
    note_type="entretien",
    folder="CRM-JobSearch/Entretiens",
    fields=_fields(
        FieldDef("categorie", "enum", enum_values=ENTRETIEN_CATEGORIES),
        FieldDef("date", "date"),
        FieldDef("date_suivi", "date"),
        FieldDef("opportunite", "wikilink"),
        FieldDef("interlocuteurs", "list"),
        FieldDef("interviewer", "wikilink"),
        FieldDef("type_entretien", "string"),
        FieldDef("feeling", "string"),
        FieldDef("suivi_envoye", "bool"),
    ),
    body_sections=["## Notes clés", "## Questions posées", "## Next steps"],
))

_register(NoteSchema(
    note_type="tache",
    folder="Taches",
    fields=_fields(
        FieldDef("id_tache", "string"),
        FieldDef("etat", "enum", enum_values=TACHE_ETATS),
        FieldDef("priorite", "enum", enum_values=TACHE_PRIORITES),
        FieldDef("echeance", "date"),
        FieldDef("etiquettes", "list"),
        FieldDef("projet", "wikilink"),
        FieldDef("cycle", "wikilink"),
        FieldDef("opportunite", "wikilink"),
        FieldDef("contacts", "wikilink_list"),
        FieldDef("sous_taches", "wikilink_list"),
        FieldDef("tache_parent", "wikilink"),
        FieldDef("personne_assignee", "string"),
    ),
    body_sections=["## Résumé"],
))


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
WIKILINK_RE = re.compile(r"^\[\[.+\]\]$")


def _validate_value(field_def: FieldDef, value, result: ValidationResult):
    """Validate a single field value against its FieldDef."""
    ftype = field_def.ftype
    name = field_def.name

    if value is None:
        return

    if ftype == "enum":
        if str(value) not in field_def.enum_values:
            allowed = ", ".join(f'"{v}"' for v in field_def.enum_values)
            result.errors.append(
                f'field "{name}": invalid value "{value}". '
                f"Allowed: [{allowed}]"
            )

    elif ftype == "date":
        if not DATE_RE.match(str(value)):
            result.errors.append(
                f'field "{name}": invalid date "{value}". Expected YYYY-MM-DD format.'
            )

    elif ftype == "wikilink":
        if not WIKILINK_RE.match(str(value)):
            result.errors.append(
                f'field "{name}": invalid wikilink "{value}". Expected [[Note Title]] format.'
            )

    elif ftype == "wikilink_list":
        items = value if isinstance(value, list) else [value]
        for item in items:
            if not WIKILINK_RE.match(str(item)):
                result.errors.append(
                    f'field "{name}": invalid wikilink "{item}". '
                    f"Expected [[Note Title]] format."
                )

    elif ftype == "number":
        try:
            float(value)
        except (ValueError, TypeError):
            result.errors.append(
                f'field "{name}": invalid number "{value}".'
            )

    elif ftype == "bool":
        if value not in (True, False, "true", "false"):
            result.errors.append(
                f'field "{name}": invalid boolean "{value}". Expected true/false.'
            )

    elif ftype == "url":
        if not str(value).startswith("http"):
            result.warnings.append(
                f'field "{name}": value "{value}" does not look like a URL.'
            )

    # "string" and "list" — no validation needed


def validate_create(note_type: str, fields: dict) -> ValidationResult:
    """Validate fields for creating a note of the given type.

    Returns ValidationResult with .errors (blocking) and .warnings (non-blocking).
    """
    result = ValidationResult()

    schema = SCHEMAS.get(note_type)
    if schema is None:
        result.errors.append(f'unknown note type: "{note_type}"')
        return result

    for name, value in fields.items():
        if name in LEGACY_FIELDS:
            continue
        field_def = schema.fields.get(name)
        if field_def is None:
            result.warnings.append(
                f'unknown field "{name}" for type "{note_type}"'
            )
            continue
        _validate_value(field_def, value, result)

    for name, field_def in schema.fields.items():
        if field_def.required and name not in fields:
            result.warnings.append(
                f'missing required field "{name}" for type "{note_type}"'
            )

    return result


def validate_update(note_type: str, field_name: str, value) -> ValidationResult:
    """Validate a single field update for a note of the given type.

    Returns ValidationResult with .errors (blocking) and .warnings (non-blocking).
    """
    result = ValidationResult()

    schema = SCHEMAS.get(note_type)
    if schema is None:
        result.errors.append(f'unknown note type: "{note_type}"')
        return result

    if field_name in LEGACY_FIELDS:
        return result

    field_def = schema.fields.get(field_name)
    if field_def is None:
        result.warnings.append(
            f'unknown field "{field_name}" for type "{note_type}"'
        )
        return result

    _validate_value(field_def, value, result)
    return result


def get_schema(note_type: str) -> Optional[NoteSchema]:
    """Get the schema for a note type, or None if unknown."""
    return SCHEMAS.get(note_type)


# ---------------------------------------------------------------------------
# Self-tests (run with: python note_schemas.py)
# ---------------------------------------------------------------------------

def _self_test():
    """Run basic validation self-tests."""
    passed = 0
    failed = 0

    def check(label, condition):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  PASS: {label}")
        else:
            failed += 1
            print(f"  FAIL: {label}")

    print("Running self-tests...\n")

    # 1. Valid JS candidature
    r = validate_create("opportunite-js", {
        "statut": "✉️ Candidature envoyée",
        "entreprise": "[[Anthropic]]",
        "date_candidature": "2026-06-12",
    })
    check("valid JS candidature", r.ok and not r.warnings)

    # 2. Invalid JS statut
    r = validate_create("opportunite-js", {"statut": "INVALID"})
    check("invalid JS statut → error", not r.ok and "invalid value" in r.errors[0])

    # 3. Invalid wikilink
    r = validate_create("contact-js", {"entreprise": "NotALink"})
    check("invalid wikilink → error", not r.ok and "wikilink" in r.errors[0])

    # 4. Valid wikilink
    r = validate_create("contact-js", {"entreprise": "[[Anthropic]]"})
    check("valid wikilink", r.ok)

    # 5. Invalid date
    r = validate_create("entretien", {"date": "17/02/2026"})
    check("invalid date → error", not r.ok and "date" in r.errors[0])

    # 6. Valid date
    r = validate_create("entretien", {"date": "2026-02-17"})
    check("valid date", r.ok)

    # 7. Unknown field → warning only
    r = validate_create("contact-js", {"unknown_field": "value"})
    check("unknown field → warning (not error)", r.ok and len(r.warnings) == 1)

    # 8. Unknown note type → error
    r = validate_create("nonexistent-type", {"foo": "bar"})
    check("unknown note type → error", not r.ok)

    # 9. validate_update with valid enum
    r = validate_update("tache", "etat", "En cours")
    check("valid update enum", r.ok)

    # 10. validate_update with invalid enum
    r = validate_update("tache", "etat", "WRONG")
    check("invalid update enum → error", not r.ok)

    # 11. Legacy field accepted (notion_id)
    r = validate_create("contact-js", {"notion_id": "abc-123"})
    check("legacy field notion_id accepted", r.ok and not r.warnings)

    # 12. Bool validation
    r = validate_create("entretien", {"suivi_envoye": True})
    check("valid bool true", r.ok)
    r = validate_create("entretien", {"suivi_envoye": "maybe"})
    check("invalid bool → error", not r.ok)

    # 13. Number validation
    r = validate_create("opportunite-js", {"score_match": "not_a_number"})
    check("invalid number → error", not r.ok)

    # 14. URL warning
    r = validate_create("entreprise-js", {"site_web": "not-a-url"})
    check("bad URL → warning (not error)", r.ok and len(r.warnings) == 1)

    # 15. tache wikilink_list validation
    r = validate_create("tache", {"contacts": ["[[Alice]]", "[[Bob]]"]})
    check("valid wikilink_list", r.ok)
    r = validate_create("tache", {"contacts": ["[[Alice]]", "Bob"]})
    check("invalid wikilink_list item → error", not r.ok)

    # 16. wikilink_list single value (auto-OK)
    r = validate_create("tache", {"contacts": "[[Alice]]"})
    check("wikilink_list single value accepted", r.ok)

    # 17. get_schema
    check("get_schema returns NoteSchema", get_schema("tache") is not None)
    check("get_schema unknown returns None", get_schema("nope") is None)

    # 18. Exactly 5 jobsearch types registered, no *-bg leaked
    check(f"5 schemas registered (got {len(SCHEMAS)})", len(SCHEMAS) == 5)
    check("no *-bg types leaked", not any(t.endswith("-bg") for t in SCHEMAS))
    check("projet/sprint not present", "projet" not in SCHEMAS and "sprint" not in SCHEMAS)

    # 19. Body sections
    s = get_schema("entretien")
    check("entretien has 3 body sections", len(s.body_sections) == 3)

    # 20. JS statut with emoji
    r = validate_create("opportunite-js", {"statut": "📞 Entretien prévu"})
    check("JS statut with emoji accepted", r.ok)

    # 20b. New statut "CV préparé — à envoyer" (sub-agent fan-out)
    r = validate_create("opportunite-js", {"statut": "📋 CV préparé — à envoyer"})
    check("JS statut CV préparé accepted", r.ok)

    # 21. The categorie/interlocuteurs fix: zero warnings on a full entretien
    r = validate_create("entretien", {
        "categorie": "Préparation",
        "date": "2026-06-13",
        "opportunite": "[[Applied AI Architect — Anthropic]]",
        "interlocuteurs": ["TBD"],
        "type_entretien": "RH",
    })
    check("entretien categorie+interlocuteurs → zero warnings (AC2)",
          r.ok and not r.warnings)

    # 22. Invalid entretien categorie → error
    r = validate_create("entretien", {"categorie": "Debrief"})
    check("invalid entretien categorie → error", not r.ok)

    # 23. tache closed state Terminé valid (not "Terminée")
    r = validate_update("tache", "etat", "Terminé")
    check("tache etat Terminé valid", r.ok)
    r = validate_update("tache", "etat", "Terminée")
    check("tache etat Terminée (wrong) → error", not r.ok)

    # 24. target_profile still warns (parity with obsidian-crm escape hatch)
    r = validate_create("opportunite-js", {"target_profile": "P1"})
    check("target_profile → non-blocking warning (escape hatch)",
          r.ok and len(r.warnings) == 1)

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
    print("All tests passed!")


if __name__ == "__main__":
    _self_test()
