from dataclasses import dataclass


@dataclass(frozen=True)
class ResumeTemplate:
    key: str
    name: str
    description: str


RESUME_TEMPLATES: tuple[ResumeTemplate, ...] = (
    ResumeTemplate(
        key="ats_classic",
        name="ATS Classic",
        description="Single-column, parser-friendly layout for most applications.",
    ),
    ResumeTemplate(
        key="modern_professional",
        name="Modern Professional",
        description="Clean contemporary layout with restrained section styling.",
    ),
    ResumeTemplate(
        key="technical",
        name="Technical",
        description="Emphasizes skills, projects, and engineering detail.",
    ),
    ResumeTemplate(
        key="executive",
        name="Executive",
        description="Leadership-focused structure for senior roles.",
    ),
    ResumeTemplate(
        key="compact",
        name="Compact",
        description="Dense layout for keeping strong content to fewer pages.",
    ),
)

ALLOWED_TEMPLATE_KEYS = {template.key for template in RESUME_TEMPLATES}
ALLOWED_OUTPUT_FORMATS = {"docx", "pdf"}


def is_allowed_template_key(template_key: str) -> bool:
    return template_key in ALLOWED_TEMPLATE_KEYS


def is_allowed_output_format(output_format: str) -> bool:
    return output_format in ALLOWED_OUTPUT_FORMATS
