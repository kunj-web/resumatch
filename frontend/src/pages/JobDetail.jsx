import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getJob, updateJobStatus, deleteJob } from "../api/jobs";
import { createTailoredResume } from "../api/tailoredResumes";

const STATUS_OPTIONS = [
  {
    value: "saved",
    label: "Saved",
    color: "bg-gray-100 text-gray-600 border-gray-200",
  },
  {
    value: "applied",
    label: "Applied",
    color: "bg-blue-50 text-blue-600 border-blue-200",
  },
  {
    value: "interview",
    label: "Interview",
    color: "bg-amber-50 text-amber-600 border-amber-200",
  },
  {
    value: "offer",
    label: "Offer",
    color: "bg-emerald-50 text-emerald-600 border-emerald-200",
  },
  {
    value: "rejected",
    label: "Rejected",
    color: "bg-red-50 text-red-600 border-red-200",
  },
];

const PRIORITY_STYLES = {
  high: { bg: "bg-red-50", text: "text-red-600", border: "border-red-200" },
  medium: {
    bg: "bg-amber-50",
    text: "text-amber-600",
    border: "border-amber-200",
  },
  low: { bg: "bg-gray-50", text: "text-gray-500", border: "border-gray-200" },
};

const CATEGORY_STYLES = {
  technical: {
    bg: "bg-blue-50",
    text: "text-blue-700",
    border: "border-blue-200",
  },
  tool: {
    bg: "bg-violet-50",
    text: "text-violet-700",
    border: "border-violet-200",
  },
  soft: {
    bg: "bg-emerald-50",
    text: "text-emerald-700",
    border: "border-emerald-200",
  },
  certification: {
    bg: "bg-amber-50",
    text: "text-amber-700",
    border: "border-amber-200",
  },
  other: { bg: "bg-gray-50", text: "text-gray-600", border: "border-gray-200" },
};

function ScoreRing({ score }) {
  if (score === null || score === undefined)
    return (
      <div className="w-24 h-24 rounded-full border-4 border-gray-200 flex items-center justify-center">
        <span className="text-sm text-gray-400">N/A</span>
      </div>
    );
  const color = score >= 75 ? "#10b981" : score >= 50 ? "#f59e0b" : "#ef4444";
  const label =
    score >= 75 ? "Great match" : score >= 50 ? "Moderate match" : "Low match";
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-24 h-24">
        <svg className="w-24 h-24 -rotate-90" viewBox="0 0 36 36">
          <circle
            cx="18"
            cy="18"
            r="15"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="3"
          />
          <circle
            cx="18"
            cy="18"
            r="15"
            fill="none"
            stroke={color}
            strokeWidth="3"
            strokeDasharray={`${(score / 100) * 94} 94`}
            strokeLinecap="round"
            style={{ transition: "stroke-dasharray 1s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-bold" style={{ color }}>
            {score}%
          </span>
        </div>
      </div>
      <span className="text-xs font-medium" style={{ color }}>
        {label}
      </span>
    </div>
  );
}

export default function JobDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // All state declarations first
  const [visible, setVisible] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [tailoredResume, setTailoredResume] = useState(null);
  const [tailorError, setTailorError] = useState("");

  // Visibility animation
  useEffect(() => {
    setTimeout(() => setVisible(true), 100);
  }, []);

  const { data: job, isLoading } = useQuery({
    queryKey: ["job", id],
    queryFn: async () => {
      const res = await getJob(id);
      return res.data;
    },
  });

  const statusMutation = useMutation({
    mutationFn: async (status) => {
      const res = await updateJobStatus(id, status);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(["job", id]);
      queryClient.invalidateQueries(["jobs"]);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async () => {
      await deleteJob(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(["jobs"]);
      navigate("/");
    },
  });

  const tailorMutation = useMutation({
    mutationFn: async () => {
      const res = await createTailoredResume(id);
      return res.data;
    },
    onSuccess: async (data) => {
      setTailoredResume(data);
      setTailorError("");
      await queryClient.invalidateQueries({ queryKey: ["me"] });
      await queryClient.refetchQueries({ queryKey: ["me"] });
      navigate(`/tailored-resumes/${data.id}`);
    },
    onError: (err) => {
      setTailorError(
        err.response?.data?.detail || "Could not tailor this resume yet."
      );
    },
  });

  if (isLoading)
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

  if (!job)
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <p className="text-gray-500">Job not found</p>
        <button
          onClick={() => navigate("/")}
          className="mt-4 text-emerald-600 text-sm hover:underline"
        >
          Back to dashboard
        </button>
      </div>
    );

  const currentStatus = STATUS_OPTIONS.find((s) => s.value === job.status);
  const canTailor =
    job.missing_skills?.length > 0 || job.keyword_gaps?.length > 0;

  return (
    <div
      className="w-full max-w-7xl mx-auto"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(20px)",
        transition: "all 0.5s ease-out",
      }}
    >
      {/* Back */}
      <button
        onClick={() => navigate("/")}
        className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-900 transition-colors duration-200 mb-6"
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
        Back to Dashboard
      </button>

      {/* Header */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-5">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex items-start gap-4">
            <div
              className="w-14 h-14 rounded-xl flex items-center justify-center text-white font-bold text-xl flex-shrink-0"
              style={{
                background: "linear-gradient(135deg, #0d1b2a, #112240)",
              }}
            >
              {job.company ? job.company[0].toUpperCase() : "?"}
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {job.title || "Untitled Role"}
              </h1>
              <div className="flex items-center gap-2 mt-1 flex-wrap">
                <span className="text-gray-600 text-sm font-medium">
                  {job.company || "Unknown company"}
                </span>
                {job.location && (
                  <>
                    <span className="text-gray-300">·</span>
                    <span className="text-gray-500 text-sm">
                      {job.location}
                    </span>
                  </>
                )}
                {job.location_type && (
                  <>
                    <span className="text-gray-300">·</span>
                    <span className="text-gray-500 text-sm capitalize">
                      {job.location_type}
                    </span>
                  </>
                )}
                {job.job_type && (
                  <>
                    <span className="text-gray-300">·</span>
                    <span className="text-gray-500 text-sm capitalize">
                      {job.job_type.replace("-", " ")}
                    </span>
                  </>
                )}
              </div>
              <div className="flex items-center gap-3 mt-2 flex-wrap">
                {job.salary_min && (
                  <span className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-medium">
                    {job.salary_currency} {job.salary_min.toLocaleString()}
                    {job.salary_max
                      ? ` — ${job.salary_max.toLocaleString()}`
                      : "+"}
                  </span>
                )}
                {job.experience_min && (
                  <span className="text-xs bg-blue-50 text-blue-700 border border-blue-200 px-2.5 py-1 rounded-full font-medium">
                    {job.experience_min}
                    {job.experience_max ? `—${job.experience_max}` : "+"} yrs
                    exp
                  </span>
                )}
                {job.education && (
                  <span className="text-xs bg-gray-100 text-gray-600 border border-gray-200 px-2.5 py-1 rounded-full font-medium">
                    {job.education}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Score + Tailor */}
          <div className="flex flex-col items-center gap-3">
            <ScoreRing score={job.match_score} />
            <button
              onClick={() => tailorMutation.mutate()}
              disabled={!canTailor || tailorMutation.isPending}
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold text-white disabled:opacity-40 disabled:cursor-not-allowed active:scale-95 transition-all duration-200 shadow-md shadow-emerald-500/20"
              style={{ background: "linear-gradient(135deg, #10b981, #059669)" }}
            >
              {tailorMutation.isPending ? (
                <>
                  <svg
                    className="animate-spin h-3.5 w-3.5 text-white"
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
                  Tailoring...
                </>
              ) : (
                "Tailor Resume"
              )}
            </button>
          </div>
        </div>

        {(tailoredResume || tailorError) && (
          <div
            className={`mt-4 px-3 py-2 rounded-lg border text-xs ${
              tailoredResume
                ? "bg-emerald-50 border-emerald-200 text-emerald-700"
                : "bg-red-50 border-red-200 text-red-600"
            }`}
          >
            {tailoredResume
              ? `Tailored draft ready. ${
                  tailoredResume.unsupported_gaps?.length || 0
                } unsupported gaps kept out.`
              : tailorError}
          </div>
        )}

        {/* Source URL */}
        {job.source_url && (
          <a
            href={job.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs text-emerald-600 hover:underline mt-4"
          >
            <svg
              className="w-3.5 h-3.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
            View original job posting
          </a>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left column */}
        <div className="lg:col-span-2 space-y-5">
          {/* Status */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">
              Application Status
            </h2>
            <div className="flex gap-2 flex-wrap">
              {STATUS_OPTIONS.map((s) => (
                <button
                  key={s.value}
                  onClick={() => statusMutation.mutate(s.value)}
                  disabled={statusMutation.isPending}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all duration-200 active:scale-95 ${
                    job.status === s.value
                      ? s.color + " shadow-sm scale-105"
                      : "bg-gray-50 text-gray-400 border-gray-200 hover:border-gray-300"
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
            {job.applied_at && (
              <p className="text-xs text-gray-400 mt-3">
                Applied on{" "}
                {new Date(job.applied_at).toLocaleDateString("en-US", {
                  month: "long",
                  day: "numeric",
                  year: "numeric",
                })}
              </p>
            )}
          </div>

          {/* Skills Match */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">
              Skills Match
            </h2>

            {job.matched_skills?.length > 0 && (
              <div className="mb-4">
                <p className="text-xs font-medium text-emerald-600 mb-2">
                  ✓ Found in your resume
                </p>
                <div className="flex flex-wrap gap-2">
                  {job.matched_skills.map((skill, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-xs font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {job.missing_skills?.length > 0 && (
              <div>
                <p className="text-xs font-medium text-red-500 mb-2">
                  ✗ Missing from your resume
                </p>
                <div className="flex flex-wrap gap-2">
                  {job.missing_skills.map((skill, i) => {
                    const cat =
                      CATEGORY_STYLES[skill.category] || CATEGORY_STYLES.other;
                    return (
                      <span
                        key={i}
                        className={`px-3 py-1 ${cat.bg} ${cat.text} border ${cat.border} rounded-full text-xs font-medium`}
                      >
                        {skill.name}
                      </span>
                    );
                  })}
                </div>
              </div>
            )}

            {!job.matched_skills?.length && !job.missing_skills?.length && (
              <p className="text-sm text-gray-400">
                No match data — upload your resume to see results.
              </p>
            )}
          </div>

          {/* Keyword Gaps */}
          {job.keyword_gaps?.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <h2 className="text-sm font-semibold text-gray-900 mb-1">
                Keyword Gaps
              </h2>
              <p className="text-xs text-gray-400 mb-4">
                Add these keywords to your resume to improve your match score
              </p>
              <div className="space-y-3">
                {job.keyword_gaps.map((gap, i) => {
                  const p =
                    PRIORITY_STYLES[gap.priority] || PRIORITY_STYLES.low;
                  const cat =
                    CATEGORY_STYLES[gap.category] || CATEGORY_STYLES.other;
                  return (
                    <div
                      key={i}
                      className="flex items-start justify-between gap-3 p-3 bg-gray-50 rounded-xl border border-gray-100"
                    >
                      <div className="flex items-start gap-2 flex-wrap">
                        <span className="font-semibold text-gray-900 text-sm">
                          {gap.keyword}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium border ${cat.bg} ${cat.text} ${cat.border}`}
                        >
                          {gap.category}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium border ${p.bg} ${p.text} ${p.border}`}
                        >
                          {gap.priority} priority
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 text-right max-w-[200px]">
                        {gap.context}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Right column */}
        <div className="space-y-5">
          {/* Job Info */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">
              Job Details
            </h2>
            <div className="space-y-3">
              {[
                { label: "Status", value: currentStatus?.label },
                { label: "Job Type", value: job.job_type?.replace("-", " ") },
                { label: "Location Type", value: job.location_type },
                {
                  label: "Experience",
                  value: job.experience_min
                    ? `${job.experience_min}${job.experience_max ? `—${job.experience_max}` : "+"} years`
                    : null,
                },
                { label: "Education", value: job.education },
                {
                  label: "Added",
                  value: new Date(job.created_at).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  }),
                },
              ]
                .filter((item) => item.value)
                .map((item, i) => (
                  <div
                    key={i}
                    className="flex items-start justify-between gap-2"
                  >
                    <span className="text-xs text-gray-400">{item.label}</span>
                    <span className="text-xs font-medium text-gray-700 capitalize text-right">
                      {item.value}
                    </span>
                  </div>
                ))}
            </div>
          </div>

          {/* Required Skills */}
          {job.required_skills?.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <h2 className="text-sm font-semibold text-gray-900 mb-3">
                Required Skills
              </h2>
              <div className="flex flex-wrap gap-2">
                {job.required_skills.map((skill, i) => {
                  const cat =
                    CATEGORY_STYLES[skill.category] || CATEGORY_STYLES.other;
                  const isMatched = job.matched_skills?.includes(skill.name);
                  return (
                    <span
                      key={i}
                      className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                        isMatched
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : `${cat.bg} ${cat.text} ${cat.border}`
                      }`}
                    >
                      {isMatched ? "✓ " : ""}
                      {skill.name}
                    </span>
                  );
                })}
              </div>
            </div>
          )}

          {/* Preferred Skills */}
          {job.preferred_skills?.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <h2 className="text-sm font-semibold text-gray-900 mb-3">
                Preferred Skills
              </h2>
              <div className="flex flex-wrap gap-2">
                {job.preferred_skills.map((skill, i) => (
                  <span
                    key={i}
                    className="px-2.5 py-1 bg-gray-50 text-gray-500 border border-gray-200 rounded-full text-xs font-medium"
                  >
                    {skill.name}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Danger zone */}
          <div className="bg-white rounded-2xl border border-red-100 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-red-500 mb-3">
              Danger Zone
            </h2>
            {!showDeleteConfirm ? (
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="w-full py-2 rounded-xl text-xs font-semibold text-red-500 border border-red-200 hover:bg-red-50 transition-all duration-200"
              >
                Delete this job
              </button>
            ) : (
              <div className="space-y-2">
                <p className="text-xs text-gray-500">
                  Are you sure? This cannot be undone.
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => deleteMutation.mutate()}
                    disabled={deleteMutation.isPending}
                    className="flex-1 py-2 rounded-xl text-xs font-semibold text-white bg-red-500 hover:bg-red-600 transition-all duration-200 disabled:opacity-50"
                  >
                    {deleteMutation.isPending ? "Deleting..." : "Yes, delete"}
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(false)}
                    className="flex-1 py-2 rounded-xl text-xs font-semibold text-gray-600 border border-gray-200 hover:bg-gray-50 transition-all duration-200"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
