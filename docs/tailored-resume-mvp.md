# Tailored Resume MVP

## Goal

Add a paid resume tailoring flow where users can generate an editable tailored resume for a specific job while keeping the original uploaded resume unchanged.

The tailored resume must be useful, honest, and reviewable before download.

## Core User Flow

1. User uploads a resume.
2. User adds a job description or job URL.
3. App extracts job details and calculates match score, missing skills, and keyword gaps.
4. User opens the job detail page.
5. User clicks `Tailor Resume`.
6. App checks whether the user can generate a tailored resume.
7. App generates a tailored resume draft using the active resume and the selected job.
8. User reviews and edits the tailored draft.
9. User finalizes the tailored resume.
10. User downloads the final tailored resume.

## Button Placement

Primary placement:

- Job detail page header, near the match score.

Secondary placement later:

- Under the `Keyword Gaps` section as a softer call to action.

## Access Rules

Free plan:

- User gets 10 free tailored resumes.
- Each successful tailored resume generation uses 1 credit.
- Credits should not be charged for failed generations.

Pro plan:

- User gets unlimited tailored resumes.
- Backend rate limiting should still exist to prevent abuse.

Blocked states:

- No active resume uploaded.
- Job extraction failed.
- Job has no missing skills or keyword gaps.
- Free user has used all free tailored resume credits.

## Resume Format Rule

The tailored resume should preserve the user's original resume format as much as possible.

Preferred implementation:

- Use DOCX for tailoring because it allows the app to preserve layout, sections, fonts, and spacing more reliably.
- Keep PDF support for matching and analysis.

MVP product rule:

- PDF resumes can be used for match score and missing skills.
- DOCX resumes should be used for format-preserving tailoring.

## Honesty Rule

Tailoring must only add missing skills and keyword gaps when they are supported by the original resume.

Allowed changes:

- Reword existing bullets to include supported keywords.
- Add skills already proven somewhere else in the resume.
- Move existing skills into a better section.
- Improve ATS wording.
- Align the summary/profile with the job when supported by the resume.

Not allowed:

- Fake experience.
- Fake education.
- Fake certifications.
- Fake companies or job titles.
- Fake dates or years of experience.
- Fake tools or skills.
- Fake metrics, outcomes, or achievements.

Unsupported missing items should be shown separately as recommendations, not inserted into the tailored resume.

## Editing Rule

The tailored resume should have a review-and-edit step before download.

MVP editing approach:

- Show the generated tailored resume as editable sections/text.
- Let the user edit the draft manually.
- Save the edited draft.
- Generate the final downloadable file from the edited draft.

Avoid for MVP:

- A full visual resume designer.
- Drag-and-drop layout editing.
- Pixel-perfect PDF editing.

## Suggested Screens

Job detail page:

- `Tailor Resume` button.
- If a tailored resume already exists, show `Review Tailored Resume` or `Download Tailored Resume`.

Tailored resume review screen or modal:

- Editable resume content.
- Unsupported missing skills/keyword gaps panel.
- Save changes.
- Finalize/download button.

Upgrade modal:

- Shown when a free user has used all 10 free tailored resume credits.

## Success Criteria

- Original uploaded resume is never overwritten.
- User can generate a tailored draft for one job.
- User can edit the tailored draft before download.
- The generated content only includes supported skills and keyword gaps.
- Free credits are counted correctly.
- Pro users are not blocked by credit count.
- Downloaded resume is tied to the selected job and source resume.
