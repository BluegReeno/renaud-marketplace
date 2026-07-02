#!/usr/bin/env python3
"""
CV Generator — generates 1-page PDF CVs from a 5-profile × 5-company-type matrix.

Usage:
    python generate_cv.py --profile p1 --company-type t5 --lang en
    python generate_cv.py --profile p3 --company-type t1 --lang fr
    python generate_cv.py --profile p4 --company-type t5 --lang fr \
        --company "Yotta" --job-title "Forward Deployed Engineer" \
        --container-titles '["Architecture & agents IA", "Cycle client & deploiement", "Secteurs"]' \
        --bullet-overrides '{"blue_green.p4.fr.0": "Nouveau bullet personnalise"}'
    python generate_cv.py --positioning cto   # retro-compat
"""

import json
import os
import re
import shutil
import argparse
from pathlib import Path


LABELS = {
    'en': {
        'about': 'About',
        'contact': 'Contact',
        'competencies': 'Key Competencies',
        'experience': 'Work Experience',
        'earlier': 'Earlier Career',
        'education': 'Education',
    },
    'fr': {
        'about': 'À propos',
        'contact': 'Contact',
        'competencies': 'Compétences clés',
        'experience': 'Expérience professionnelle',
        'earlier': 'Carrière antérieure',
        'education': 'Formation',
    },
}

RETRO_COMPAT_MAP = {
    'ai_consulting': ('p1', 't4'),
    'cto':           ('p3', 't1'),
    'business_dev':  ('p5', 't3'),
}

# Cells where Artelia (corporate proof) must lead over Blue Green (solopreneur perception)
# — hardcoded rule, never derived from the matrix.
CORPORATE_FIRST_CELLS = {('p1', 't4'), ('p2', 't4'), ('p5', 't5')}

# Progressive compact CSS levels — injected before </head>, tried in sequence until 1-page fits
COMPACT_CSS_LEVELS = [
    # Level 1 — gentle: tighten padding/margins
    """<style>
.header { padding: 15px 25px; }
.content { padding: 15px 20px; }
.about-contact-row { margin-bottom: 12px; }
.about-item { margin-bottom: 4px; }
.competencies-section { margin-bottom: 12px; }
.competency-block { padding: 10px; }
.experience-section { margin-bottom: 10px; }
.job { margin-bottom: 8px; }
</style>
</head>""",
    # Level 2 — moderate: reduce font-size + tighten further
    """<style>
body { font-size: 8.8pt; }
.header { padding: 10px 20px; }
.content { padding: 12px 18px; }
.about-contact-row { margin-bottom: 8px; }
.about-item { margin-bottom: 3px; font-size: 8.8pt; }
.competencies-section { margin-bottom: 8px; }
.competency-block { padding: 8px; }
.experience-section { margin-bottom: 8px; }
.job { margin-bottom: 6px; }
.section-title { margin-bottom: 4px; padding-bottom: 2px; }
li { margin-bottom: 2px; }
</style>
</head>""",
    # Level 3 — ultra-compact: smallest readable size + minimal spacing
    """<style>
body { font-size: 8.5pt; }
.header { padding: 8px 18px; }
.name { font-size: 20pt; }
.content { padding: 10px 15px; }
.about-contact-row { margin-bottom: 6px; }
.about-item { margin-bottom: 2px; font-size: 8.5pt; }
.competencies-section { margin-bottom: 6px; }
.competency-block { padding: 6px; }
.experience-section { margin-bottom: 6px; }
.job { margin-bottom: 4px; }
.section-title { margin-bottom: 3px; padding-bottom: 1px; font-size: 9pt; }
.job-header { margin-bottom: 2px; }
li { margin-bottom: 1px; }
</style>
</head>""",
]


def get_skill_dir():
    """Return the plugin root (parent of scripts/)."""
    return Path(__file__).parent.parent


def slugify(text):
    """Convert text to a filename-safe ASCII slug (lowercase, underscores)."""
    text = text.lower()
    # Replace accented chars with ascii equivalents
    replacements = [
        ('é', 'e'), ('è', 'e'), ('ê', 'e'), ('ë', 'e'),
        ('à', 'a'), ('â', 'a'), ('ä', 'a'),
        ('î', 'i'), ('ï', 'i'),
        ('ô', 'o'), ('ö', 'o'),
        ('ù', 'u'), ('û', 'u'), ('ü', 'u'),
        ('ç', 'c'), ('ñ', 'n'),
    ]
    for src, dst in replacements:
        text = text.replace(src, dst)
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s-]+', '_', text).strip('_')


def load_cv_data(data_dir=None):
    if data_dir:
        cv_master_path = Path(data_dir) / 'cv-master.json'
    else:
        cv_master_path = get_skill_dir() / 'data' / 'cv-master.json'
    with open(cv_master_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_cell(cv_data, profile, company_type):
    try:
        return cv_data['matrix'][profile][company_type]
    except KeyError:
        valid = [(p, ct) for p, cts in cv_data['matrix'].items() for ct in cts]
        raise ValueError(
            f"Cell ({profile}, {company_type}) not in matrix. Valid cells: {valid}"
        )


def resolve_cell_content(cv_data, profile, company_type, lang):
    cell = get_cell(cv_data, profile, company_type)
    return {
        'title': cell['title'][lang],
        'about': cell['about'][lang],
        'containers': cell['containers'][lang],
    }


def get_job_order(profile, company_type):
    if (profile, company_type) in CORPORATE_FIRST_CELLS:
        return ['artelia', 'blue_green', 'open_ocean']
    return ['blue_green', 'artelia', 'open_ocean']


def count_pdf_pages(pdf_path):
    """Return page count, or None if pikepdf is unavailable."""
    try:
        import pikepdf
        with pikepdf.open(pdf_path) as pdf:
            return len(pdf.pages)
    except ImportError:
        return None


def generate_cv_html(output_html_path, cv_data, profile, company_type, lang,
                     output_dir=None, container_titles=None, bullet_overrides=None,
                     about_override=None, title_override=None,
                     compact_level=0):
    """Generate customised HTML from template for the given profile×company_type cell."""

    template_path = get_skill_dir() / 'templates' / 'cv_template.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    if compact_level > 0 and compact_level <= len(COMPACT_CSS_LEVELS):
        html = html.replace('</head>', COMPACT_CSS_LEVELS[compact_level - 1])

    cell = resolve_cell_content(cv_data, profile, company_type, lang)

    # === LABELS ===
    labels = LABELS[lang]
    html = html.replace('{{LABEL_ABOUT}}', labels['about'])
    html = html.replace('{{LABEL_CONTACT}}', labels['contact'])
    html = html.replace('{{LABEL_COMPETENCIES}}', labels['competencies'])
    html = html.replace('{{LABEL_EXPERIENCE}}', labels['experience'])
    html = html.replace('{{LABEL_EARLIER}}', labels['earlier'])
    html = html.replace('{{LABEL_EDUCATION}}', labels['education'])

    # === TITLE ===
    html = html.replace('{{TITLE}}', title_override if title_override else cell['title'])

    # === ABOUT ===
    about = about_override if about_override else cell['about']
    html = html.replace('{{ABOUT_1}}', about[0])
    html = html.replace('{{ABOUT_2}}', about[1])
    html = html.replace('{{ABOUT_3}}', about[2])

    # === COMPETENCY CONTAINER TITLES ===
    containers = cell['containers']
    titles = [c['title'] for c in containers]
    if container_titles:
        for i, t in enumerate(container_titles[:3]):
            titles[i] = t
    html = html.replace('{{COMP_AI_TITLE}}', titles[0])
    html = html.replace('{{COMP_BUSINESS_TITLE}}', titles[1])
    html = html.replace('{{COMP_SECTOR_TITLE}}', titles[2])

    # === COMPETENCY ITEMS ===
    html = html.replace('{{COMP_AI}}',
                        '\n'.join(f'<li>{c}</li>' for c in containers[0]['items']))
    html = html.replace('{{COMP_BUSINESS}}',
                        '\n'.join(f'<li>{c}</li>' for c in containers[1]['items']))
    html = html.replace('{{COMP_SECTOR}}',
                        '\n'.join(f'<li>{c}</li>' for c in containers[2]['items']))

    # === EXPERIENCES ===
    experiences = cv_data['experiences']
    job_order = get_job_order(profile, company_type)

    for slot, job_key in enumerate(job_order, start=1):
        job = experiences[job_key]
        title_key = f"{profile}_{company_type}"
        title = job['titles'].get(title_key, job['titles'][profile])[lang]
        period = job['period']
        if lang == 'fr':
            period = period.replace('Present', "Aujourd'hui")
        company_str = f"{job['company']} — {job['location']}"
        profile_bullets = job['bullets'][profile]
        bullets = list(profile_bullets.get(company_type, profile_bullets['default'])[lang])

        # Apply bullet overrides — key: "{company}.{profile}.{lang}.{index}"
        if bullet_overrides:
            for key, new_text in bullet_overrides.items():
                parts = key.split('.')
                if len(parts) == 4:
                    b_company, b_profile, b_lang, b_index = parts
                    if b_company == job_key and b_profile == profile and b_lang == lang:
                        idx = int(b_index)
                        if 0 <= idx < len(bullets):
                            bullets[idx] = new_text

        html = html.replace(f'{{{{JOB{slot}_TITLE}}}}', title)
        html = html.replace(f'{{{{JOB{slot}_PERIOD}}}}', period)
        html = html.replace(f'{{{{JOB{slot}_COMPANY}}}}', company_str)
        html = html.replace(f'{{{{JOB{slot}_BULLETS}}}}',
                            '\n'.join(f'<li>{b}</li>' for b in bullets))

    # Earlier career
    earlier = experiences['earlier']
    earlier_html = '\n'.join(
        '<div class="earlier-item">'
        f'<span class="earlier-content">&#8226; {item.get("title_" + lang, item["title"])} &#8212; {item["company"]}'
        f' ({item.get("description_" + lang, item.get("description", ""))})</span>'
        f'<span class="earlier-period">{item["period"]}</span></div>'
        for item in earlier['items']
    )
    html = html.replace('{{EARLIER_CAREER}}', earlier_html)

    # === EDUCATION ===
    education_html = '\n'.join(
        '<div class="education-item">'
        '<span class="education-content">'
        f'<span class="degree">{edu["degree"]}:</span> '
        f'<span class="school">{edu["school"]}, {edu["location"]}</span>'
        '</span>'
        f'<span class="education-year">{edu["year"]}</span>'
        '</div>'
        for edu in cv_data['education']
    )
    html = html.replace('{{EDUCATION}}', education_html)

    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_html_path


def html_to_pdf(html_path, pdf_path, base_url=None):
    try:
        from weasyprint import HTML
    except ImportError:
        print("ERROR: weasyprint not installed. Use: uv run --with weasyprint ...")
        raise

    if base_url is None:
        base_url = str(Path(html_path).parent)

    HTML(filename=str(html_path), base_url=base_url).write_pdf(str(pdf_path))
    print(f"OK PDF generated: {pdf_path}")
    return pdf_path


def generate_cv(profile='p1', company_type='t4', lang='en',
                output_filename=None, output_dir=None, data_dir=None,
                company=None, job_title=None,
                container_titles=None, bullet_overrides=None,
                about_override=None, title_override=None):
    """Generate a CV PDF for the given profile × company_type cell."""

    skill_dir = get_skill_dir()

    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    work_dir = output_dir / '.cv_temp'
    work_dir.mkdir(exist_ok=True)

    photo_src = skill_dir / 'assets' / 'photo.jpeg'
    # Fallback: user-managed location outside the (public) repo
    if not photo_src.exists():
        photo_src = Path.home() / '.claude' / 'assets' / 'photo.jpeg'
    photo_dest = work_dir / 'photo.jpeg'
    if photo_src.exists():
        shutil.copy(photo_src, photo_dest)
    else:
        print("INFO: No photo found — CV will render without photo.")
        print("      To add: place photo.jpeg in ~/.claude/assets/photo.jpeg")

    cv_data = load_cv_data(data_dir)

    # Build output filename
    if output_filename is None:
        if company or job_title:
            parts = ['CV', 'Renaud', 'Laborbe']
            if job_title:
                parts.append(slugify(job_title))
            if company:
                parts.append(slugify(company))
            parts.append(lang.upper())
            output_filename = '_'.join(parts) + '.pdf'
        else:
            output_filename = f"CV_Renaud_Laborbe_{profile.upper()}_{company_type.upper()}_{lang.upper()}.pdf"

    output_pdf = output_dir / output_filename
    output_html = work_dir / 'cv_generated.html'

    generate_cv_html(
        output_html_path=output_html,
        cv_data=cv_data,
        profile=profile,
        company_type=company_type,
        lang=lang,
        container_titles=container_titles,
        bullet_overrides=bullet_overrides,
        about_override=about_override,
        title_override=title_override,
        compact_level=0,
    )

    html_to_pdf(output_html, output_pdf, base_url=str(work_dir))

    # Iterative compact retry — try up to 3 progressively tighter CSS levels
    pages = count_pdf_pages(output_pdf)
    if pages is not None and pages > 1:
        for level in range(1, len(COMPACT_CSS_LEVELS) + 1):
            print(f"WARNING: CV is {pages} pages — retrying with compact layout level {level}/{len(COMPACT_CSS_LEVELS)}...")
            generate_cv_html(
                output_html_path=output_html,
                cv_data=cv_data,
                profile=profile,
                company_type=company_type,
                lang=lang,
                container_titles=container_titles,
                bullet_overrides=bullet_overrides,
                about_override=about_override,
                title_override=title_override,
                compact_level=level,
            )
            html_to_pdf(output_html, output_pdf, base_url=str(work_dir))
            pages = count_pdf_pages(output_pdf)
            if pages is None or pages <= 1:
                print(f"OK Compact level {level} applied — CV fits 1 page.")
                break
        else:
            print(f"WARNING: CV still {pages} pages after all compact levels — content needs trimming.")

    try:
        shutil.rmtree(work_dir)
    except Exception:
        pass

    return output_pdf


def main():
    parser = argparse.ArgumentParser(
        description='Generate professional 1-page PDF CVs from a 5x5 matrix',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_cv.py --profile p1 --company-type t5 --lang en
  python generate_cv.py --profile p4 --company-type t5 --lang fr \\
      --company "Yotta" --job-title "Forward Deployed Engineer" \\
      --container-titles '["Architecture & agents IA", "Cycle client & deploiement", "Secteurs"]'
  python generate_cv.py --positioning cto   # retro-compat
        """
    )

    parser.add_argument('--profile', '-p',
                        choices=['p1', 'p2', 'p3', 'p4', 'p5'], default='p1')
    parser.add_argument('--company-type', '-c',
                        choices=['t1', 't2', 't3', 't4', 't5'], default='t4')
    parser.add_argument('--lang', '-l',
                        choices=['en', 'fr'], default='en')
    parser.add_argument('--output', '-o',
                        help='Output PDF filename (overrides auto-generated name)')
    parser.add_argument('--output-dir', '-d',
                        help='Output directory (default: current directory)')
    parser.add_argument('--data-dir',
                        help='Directory containing cv-master.json (overrides plugin default)')
    parser.add_argument('--company',
                        help='Target company name — used in output filename')
    parser.add_argument('--job-title',
                        help='Job title — used in output filename (slugified)')
    parser.add_argument('--container-titles',
                        help='JSON array of 3 competency container titles '
                             '(overrides cell defaults), e.g. \'["AI Eng", "Business", "Sectors"]\'')
    parser.add_argument('--bullet-overrides',
                        help='JSON dict of bullet overrides. '
                             'Key format: "{company}.{profile}.{lang}.{index}" '
                             '(e.g. \'{"blue_green.p4.fr.0": "New bullet"}\')')
    parser.add_argument('--about-override',
                        help='JSON array of exactly 3 strings — replaces the about section')
    parser.add_argument('--title-override',
                        help='Plain string — replaces the job title line on the CV')
    # Hidden retro-compat flag
    parser.add_argument('--positioning',
                        help=argparse.SUPPRESS)

    args = parser.parse_args()

    profile = args.profile
    company_type = args.company_type
    lang = args.lang
    output_filename = args.output

    if args.positioning:
        if args.positioning in RETRO_COMPAT_MAP:
            profile, company_type = RETRO_COMPAT_MAP[args.positioning]
            output_filename = output_filename or f"CV_Renaud_Laborbe_{args.positioning}.pdf"
            print(f"Retro-compat: --positioning {args.positioning} → profile={profile}, company-type={company_type}")
        else:
            parser.error(f"Unknown --positioning value: {args.positioning}. "
                         f"Valid: {list(RETRO_COMPAT_MAP.keys())}")

    container_titles = None
    if args.container_titles:
        try:
            container_titles = json.loads(args.container_titles)
            if not isinstance(container_titles, list) or len(container_titles) != 3:
                parser.error("--container-titles must be a JSON array of exactly 3 strings")
        except json.JSONDecodeError as e:
            parser.error(f"--container-titles is not valid JSON: {e}")

    bullet_overrides = None
    if args.bullet_overrides:
        try:
            bullet_overrides = json.loads(args.bullet_overrides)
            if not isinstance(bullet_overrides, dict):
                parser.error("--bullet-overrides must be a JSON object")
        except json.JSONDecodeError as e:
            parser.error(f"--bullet-overrides is not valid JSON: {e}")

    about_override = None
    if args.about_override:
        try:
            about_override = json.loads(args.about_override)
            if not isinstance(about_override, list) or len(about_override) != 3:
                parser.error("--about-override must be a JSON array of exactly 3 strings")
        except json.JSONDecodeError as e:
            parser.error(f"--about-override is not valid JSON: {e}")

    print(f"Generating CV: profile={profile}, company-type={company_type}, lang={lang}")

    pdf_path = generate_cv(
        profile=profile,
        company_type=company_type,
        lang=lang,
        output_filename=output_filename,
        output_dir=args.output_dir,
        data_dir=args.data_dir,
        company=args.company,
        job_title=args.job_title,
        container_titles=container_titles,
        bullet_overrides=bullet_overrides,
        about_override=about_override,
        title_override=args.title_override,
    )

    print(f"\nCV ready: {pdf_path}")


if __name__ == '__main__':
    main()
