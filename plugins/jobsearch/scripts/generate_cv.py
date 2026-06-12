#!/usr/bin/env python3
"""
CV Generator — generates 1-page PDF CVs from a 5-profile × 5-company-type matrix.

Usage:
    python generate_cv.py --profile p1 --company-type t5 --lang en
    python generate_cv.py --positioning cto   # retro-compat
"""

import json
import os
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

CORPORATE_FIRST_CELLS = {('p1', 't4'), ('p2', 't4'), ('p5', 't5')}


def get_skill_dir():
    """Return the plugin root (parent of scripts/)."""
    return Path(__file__).parent.parent


def load_cv_data():
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


def generate_cv_html(output_html_path, cv_data, profile, company_type, lang,
                     output_dir=None):
    """Generate customised HTML from template for the given profile×company_type cell."""

    template_path = get_skill_dir() / 'templates' / 'cv_template.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

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
    html = html.replace('{{TITLE}}', cell['title'])

    # === ABOUT ===
    about = cell['about']
    html = html.replace('{{ABOUT_1}}', about[0])
    html = html.replace('{{ABOUT_2}}', about[1])
    html = html.replace('{{ABOUT_3}}', about[2])

    # === COMPETENCY CONTAINER TITLES ===
    containers = cell['containers']
    html = html.replace('{{COMP_AI_TITLE}}', containers[0]['title'])
    html = html.replace('{{COMP_BUSINESS_TITLE}}', containers[1]['title'])
    html = html.replace('{{COMP_SECTOR_TITLE}}', containers[2]['title'])

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
        title = job['titles'][profile][lang]
        period = job['period']
        if lang == 'fr':
            period = period.replace('Present', "Aujourd'hui")
        company_str = f"{job['company']} — {job['location']}"
        bullets = job['bullets'][profile][lang]

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
                output_filename=None, output_dir=None):
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

    cv_data = load_cv_data()

    output_html = work_dir / 'cv_generated.html'
    generate_cv_html(
        output_html_path=output_html,
        cv_data=cv_data,
        profile=profile,
        company_type=company_type,
        lang=lang,
        output_dir=output_dir,
    )

    if output_filename is None:
        output_filename = f"CV_Renaud_Laborbe_{profile.upper()}_{company_type.upper()}_{lang.upper()}.pdf"
    output_pdf = output_dir / output_filename

    html_to_pdf(output_html, output_pdf, base_url=str(work_dir))

    try:
        shutil.rmtree(work_dir)
    except Exception:
        pass

    return output_pdf


def main():
    parser = argparse.ArgumentParser(
        description='Generate professional 1-page PDF CVs from a 5×5 matrix',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_cv.py --profile p1 --company-type t5 --lang en
  python generate_cv.py --profile p3 --company-type t1 --lang fr
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
                        help='Output PDF filename')
    parser.add_argument('--output-dir', '-d',
                        help='Output directory (default: current directory)')
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

    print(f"Generating CV: profile={profile}, company-type={company_type}, lang={lang}")

    pdf_path = generate_cv(
        profile=profile,
        company_type=company_type,
        lang=lang,
        output_filename=output_filename,
        output_dir=args.output_dir,
    )

    print(f"\nCV ready: {pdf_path}")


if __name__ == '__main__':
    main()
