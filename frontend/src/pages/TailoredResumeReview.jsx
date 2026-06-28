import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getTailoredResume,
  updateTailoredResume,
} from "../api/tailoredResumes";

const emptyForm = {
  summary: "",
  skillsText: "",
  experienceBullets: [],
  projectBullets: [],
  atsFixesText: "",
  templateKey: "ats_classic",
  outputFormat: "docx",
};

const resumeTemplates = [
  {
    key: "ats_classic",
    name: "ATS Classic",
    description: "Single-column format for broad ATS compatibility.",
  },
  {
    key: "modern_professional",
    name: "Modern Professional",
    description: "Clean layout with polished section hierarchy.",
  },
  {
    key: "technical",
    name: "Technical",
    description: "Highlights skills, projects, and engineering detail.",
  },
  {
    key: "executive",
    name: "Executive",
    description: "Built around leadership scope and business impact.",
  },
  {
    key: "compact",
    name: "Compact",
    description: "Dense format for shorter final resumes.",
  },
];

function toTextList(items = []) {
  return items.filter(Boolean).join("\n");
}

function fromTextList(text) {
  return text
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function EditableBulletList({ title, items, onChange }) {
  if (!items.length) return null;

  return (
    <section className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <h2 className="text-sm font-semibold text-gray-900 mb-4">{title}</h2>
      <div className="space-y-4">
        {items.map((item, index) => (
          <div key={index} className="rounded-xl border border-gray-100 bg-gray-50 p-4">
            {item.original && (
              <p className="text-xs text-gray-400 mb-2">{item.original}</p>
            )}
            <textarea
              value={item.revised || ""}
              onChange={(event) => {
                const next = [...items];
                next[index] = { ...item, revised: event.target.value };
                onChange(next);
              }}
              rows={3}
              className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500 resize-none"
            />
            {item.inserted_keywords?.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-3">
                {item.inserted_keywords.map((keyword, keywordIndex) => (
                  <span
                    key={keywordIndex}
                    className="px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            )}
            {item.evidence && (
              <p className="text-xs text-gray-500 mt-3">{item.evidence}</p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

export default function TailoredResumeReview() {
  const { id } = useParams();
  const queryClient = useQueryClient();
  const [localForm, setLocalForm] = useState({ id: null, value: null });
  const [saved, setSaved] = useState(false);

  const { data: tailoredResume, isLoading } = useQuery({
    queryKey: ["tailored-resume", id],
    queryFn: async () => {
      const res = await getTailoredResume(id);
      return res.data;
    },
  });

  const activeContent = useMemo(() => {
    if (!tailoredResume) return null;
    return tailoredResume.edited_content || tailoredResume.draft_content || {};
  }, [tailoredResume]);

  const hydratedForm = useMemo(() => {
    if (!activeContent) return emptyForm;
    const sections = activeContent.tailored_sections || {};

    return {
      summary: sections.summary || "",
      skillsText: toTextList(sections.skills || []),
      experienceBullets: sections.experience_bullets || [],
      projectBullets: sections.project_bullets || [],
      atsFixesText: toTextList(activeContent.ats_fixes || []),
      templateKey: tailoredResume.template_key || "ats_classic",
      outputFormat: tailoredResume.output_format || "docx",
    };
  }, [activeContent, tailoredResume]);

  const form = localForm.id === id && localForm.value ? localForm.value : hydratedForm;
  const setForm = (updater) => {
    setLocalForm((current) => {
      const currentValue =
        current.id === id && current.value ? current.value : hydratedForm;
      const nextValue =
        typeof updater === "function" ? updater(currentValue) : updater;

      return { id, value: nextValue };
    });
  };

  const saveMutation = useMutation({
    mutationFn: async () => {
      const original = activeContent || {};
      const originalSections = original.tailored_sections || {};
      const editedContent = {
        ...original,
        tailored_sections: {
          ...originalSections,
          summary: form.summary,
          skills: fromTextList(form.skillsText),
          experience_bullets: form.experienceBullets,
          project_bullets: form.projectBullets,
        },
        ats_fixes: fromTextList(form.atsFixesText),
      };

      const res = await updateTailoredResume(id, {
        editedContent,
        templateKey: form.templateKey,
        outputFormat: form.outputFormat,
      });
      return res.data;
    },
    onSuccess: () => {
      setSaved(true);
      queryClient.invalidateQueries(["tailored-resume", id]);
      setTimeout(() => setSaved(false), 2500);
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <svg
          className="animate-spin h-8 w-8 text-emerald-500"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v8z"
          />
        </svg>
      </div>
    );
  }

  if (!tailoredResume) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <p className="text-gray-500">Tailored resume not found</p>
        <Link to="/" className="mt-4 text-emerald-600 text-sm hover:underline">
          Back to dashboard
        </Link>
      </div>
    );
  }

  const draft = tailoredResume.draft_content || {};
  const job = draft.job || {};
  const unsupportedGaps = tailoredResume.unsupported_gaps || [];

  return (
    <div className="w-full max-w-7xl mx-auto">
      <div className="mb-6">
        <Link
          to={`/jobs/${tailoredResume.job_id}`}
          className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-900 transition-colors duration-200"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to job
        </Link>
      </div>

      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tailored Resume Draft</h1>
          <p className="text-sm text-gray-500 mt-1">
            {job.title || "Untitled Role"}
            {job.company ? ` at ${job.company}` : ""}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {saved && (
            <span className="text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-2 rounded-xl">
              Saved
            </span>
          )}
          {saveMutation.isError && (
            <span className="text-xs font-medium text-red-600 bg-red-50 border border-red-200 px-3 py-2 rounded-xl">
              Save failed
            </span>
          )}
          <button
            onClick={() => saveMutation.mutate()}
            disabled={saveMutation.isPending}
            className="px-4 py-2.5 rounded-xl text-sm font-semibold text-white disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 transition-all duration-200 shadow-md shadow-emerald-500/20"
            style={{ background: "linear-gradient(135deg, #10b981, #059669)" }}
          >
            {saveMutation.isPending ? "Saving..." : "Save Edits"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 space-y-5">
          <section className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">Summary</h2>
            <textarea
              value={form.summary}
              onChange={(event) =>
                setForm((current) => ({ ...current, summary: event.target.value }))
              }
              rows={5}
              className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500 resize-none"
            />
          </section>

          <section className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">Skills</h2>
            <textarea
              value={form.skillsText}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  skillsText: event.target.value,
                }))
              }
              rows={6}
              className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500 resize-none"
            />
          </section>

          <EditableBulletList
            title="Experience Bullets"
            items={form.experienceBullets}
            onChange={(items) =>
              setForm((current) => ({ ...current, experienceBullets: items }))
            }
          />

          <EditableBulletList
            title="Project Bullets"
            items={form.projectBullets}
            onChange={(items) =>
              setForm((current) => ({ ...current, projectBullets: items }))
            }
          />

          <section className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">ATS Fixes</h2>
            <textarea
              value={form.atsFixesText}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  atsFixesText: event.target.value,
                }))
              }
              rows={5}
              className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500 resize-none"
            />
          </section>
        </div>

        <div className="space-y-5">
          <section className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">Template</h2>
            <div className="space-y-2">
              {resumeTemplates.map((template) => {
                const isSelected = form.templateKey === template.key;

                return (
                  <button
                    key={template.key}
                    type="button"
                    onClick={() =>
                      setForm((current) => ({
                        ...current,
                        templateKey: template.key,
                      }))
                    }
                    className={`w-full text-left rounded-xl border p-3 transition-all duration-200 ${
                      isSelected
                        ? "border-emerald-300 bg-emerald-50 shadow-sm"
                        : "border-gray-100 bg-gray-50 hover:border-gray-200 hover:bg-white"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="text-sm font-semibold text-gray-900">
                          {template.name}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {template.description}
                        </p>
                      </div>
                      <span
                        className={`mt-0.5 h-4 w-4 shrink-0 rounded-full border ${
                          isSelected
                            ? "border-emerald-500 bg-emerald-500"
                            : "border-gray-300 bg-white"
                        }`}
                      />
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="mt-5">
              <h3 className="text-xs font-semibold text-gray-500 mb-2">
                Output Format
              </h3>
              <div className="grid grid-cols-2 gap-2">
                {["docx", "pdf"].map((format) => {
                  const isSelected = form.outputFormat === format;

                  return (
                    <button
                      key={format}
                      type="button"
                      onClick={() =>
                        setForm((current) => ({
                          ...current,
                          outputFormat: format,
                        }))
                      }
                      className={`px-3 py-2 rounded-xl text-sm font-semibold uppercase transition-all duration-200 ${
                        isSelected
                          ? "bg-gray-900 text-white"
                          : "bg-gray-50 text-gray-600 border border-gray-100 hover:bg-white"
                      }`}
                    >
                      {format}
                    </button>
                  );
                })}
              </div>
            </div>
          </section>

          <section className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">Draft Info</h2>
            <div className="space-y-3">
              {[
                { label: "Status", value: tailoredResume.status },
                {
                  label: "Template",
                  value: resumeTemplates.find(
                    (template) => template.key === tailoredResume.template_key
                  )?.name,
                },
                {
                  label: "Format",
                  value: tailoredResume.output_format?.toUpperCase(),
                },
                {
                  label: "Source",
                  value: draft.source_resume?.file_name,
                },
                {
                  label: "Created",
                  value: new Date(tailoredResume.created_at).toLocaleDateString(
                    "en-US",
                    { month: "short", day: "numeric", year: "numeric" }
                  ),
                },
              ]
                .filter((item) => item.value)
                .map((item, index) => (
                  <div
                    key={index}
                    className="flex items-start justify-between gap-3"
                  >
                    <span className="text-xs text-gray-400">{item.label}</span>
                    <span className="text-xs font-medium text-gray-700 text-right">
                      {item.value}
                    </span>
                  </div>
                ))}
            </div>
          </section>

          <section className="bg-white rounded-2xl border border-amber-100 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-3">
              Unsupported Gaps
            </h2>
            {unsupportedGaps.length > 0 ? (
              <div className="space-y-3">
                {unsupportedGaps.map((gap, index) => (
                  <div
                    key={index}
                    className="p-3 rounded-xl bg-amber-50 border border-amber-100"
                  >
                    <div className="text-sm font-semibold text-amber-800">
                      {gap.name}
                    </div>
                    {gap.category && (
                      <div className="text-xs text-amber-600 mt-0.5">
                        {gap.category}
                      </div>
                    )}
                    {gap.reason && (
                      <p className="text-xs text-amber-700 mt-2">{gap.reason}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-400">No unsupported gaps.</p>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
