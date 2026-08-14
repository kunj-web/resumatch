import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getJob, updateJobStatus, deleteJob } from "../api/jobs";
import { createTailoredResume } from "../api/tailoredResumes";
import UpgradeModal from "../components/UpgradeModal";

const STATUS_OPTIONS = [
  { value: "saved", label: "Saved", color: "bg-slate-100 text-slate-700 border-slate-200" },
  { value: "applied", label: "Applied", color: "bg-sky-50 text-sky-700 border-sky-200" },
  { value: "interview", label: "Interview", color: "bg-amber-50 text-amber-700 border-amber-200" },
  { value: "offer", label: "Offer", color: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  { value: "rejected", label: "Rejected", color: "bg-rose-50 text-rose-700 border-rose-200" },
];

const PRIORITY_STYLES = {
  high: "bg-rose-50 text-rose-700 border-rose-200",
  medium: "bg-amber-50 text-amber-700 border-amber-200",
  low: "bg-slate-100 text-slate-700 border-slate-200",
};

const CATEGORY_STYLES = {
  technical: "bg-sky-50 text-sky-700 border-sky-200",
  tool: "bg-violet-50 text-violet-700 border-violet-200",
  soft: "bg-emerald-50 text-emerald-700 border-emerald-200",
  certification: "bg-amber-50 text-amber-700 border-amber-200",
  other: "bg-slate-100 text-slate-700 border-slate-200",
};

function Section({ title, eyebrow, children }) {
  return (
    <section className="rounded-[28px] border border-white/10 bg-[#07110f] p-5 text-white shadow-xl shadow-slate-900/10 sm:p-6">
      {eyebrow && (
        <p className="mb-2 text-xs font-black uppercase tracking-[0.16em] text-[#9bf6d7]">
          {eyebrow}
        </p>
      )}
      <h2 className="mb-4 text-lg font-black text-white">{title}</h2>
      {children}
    </section>
  );
}

function Pill({ children, className = "" }) {
  return (
    <span className={`rounded-full border px-3 py-1 text-xs font-black ${className}`}>
      {children}
    </span>
  );
}

function ScoreRing({ score }) {
  if (score === null || score === undefined) {
    return (
      <div className="grid h-24 w-24 place-items-center rounded-full border-4 border-white/10 bg-white/8">
        <span className="text-sm font-black text-slate-400">N/A</span>
      </div>
    );
  }

  const color = score >= 75 ? "#30d6c2" : score >= 50 ? "#f1a33b" : "#ef4444";
  const label =
    score >= 75 ? "Great match" : score >= 50 ? "Moderate match" : "Low match";

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative h-24 w-24">
        <svg className="h-24 w-24 -rotate-90" viewBox="0 0 36 36">
          <circle cx="18" cy="18" r="15" fill="none" stroke="rgba(255,255,255,0.14)" strokeWidth="3" />
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
        <span className="absolute inset-0 flex items-center justify-center text-xl font-black" style={{ color }}>
          {score}%
        </span>
      </div>
      <span className="text-xs font-black" style={{ color }}>
        {label}
      </span>
    </div>
  );
}

export default function JobDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [visible, setVisible] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [tailoredResume, setTailoredResume] = useState(null);
  const [tailorError, setTailorError] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), 100);
    return () => clearTimeout(timer);
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
      navigate("/dashboard");
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
      if (err.response?.status === 402) {
        setTailorError("");
        setShowUpgradeModal(true);
        return;
      }

      setTailorError(
        err.response?.data?.detail || "Could not tailor this resume yet."
      );
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <svg className="h-8 w-8 animate-spin text-[#28a990]" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
        </svg>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <p className="text-sm font-semibold text-slate-500">Job not found</p>
        <button onClick={() => navigate("/dashboard")} className="mt-4 text-sm font-black text-[#28a990] hover:underline">
          Back to dashboard
        </button>
      </div>
    );
  }

  const currentStatus = STATUS_OPTIONS.find((status) => status.value === job.status);
  const canTailor = job.missing_skills?.length > 0 || job.keyword_gaps?.length > 0;

  return (
    <div
      className="mx-auto w-full max-w-7xl"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(20px)",
        transition: "all 0.5s ease-out",
      }}
    >
      <button
        onClick={() => navigate("/dashboard")}
        className="mb-6 flex items-center gap-2 text-sm font-bold text-slate-500 transition-colors hover:text-[#101318]"
      >
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Dashboard
      </button>

      <header className="relative mb-5 overflow-hidden rounded-[32px] bg-[#07110f] p-6 text-white shadow-2xl shadow-slate-900/20 sm:p-8">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_82%_16%,rgba(246,166,66,0.22),transparent_28%),radial-gradient(circle_at_10%_88%,rgba(76,242,198,0.16),transparent_30%)]" />
        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex gap-4">
            <div className="grid h-14 w-14 flex-none place-items-center rounded-2xl bg-[#9bf6d7] text-xl font-black text-[#06110f] shadow-lg shadow-[#30d6c2]/10">
              {job.company ? job.company[0].toUpperCase() : "?"}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-black uppercase tracking-[0.18em] text-[#9bf6d7]">
                Job Detail
              </p>
              <h1 className="mt-2 text-3xl font-black leading-tight text-white sm:text-4xl">
                {job.title || "Untitled Role"}
              </h1>
              <div className="mt-3 flex flex-wrap items-center gap-2 text-sm font-semibold text-slate-300">
                <span className="font-bold text-slate-100">{job.company || "Unknown company"}</span>
                {job.location && <span className="text-slate-500">/</span>}
                {job.location && <span>{job.location}</span>}
                {job.location_type && <span className="text-slate-500">/</span>}
                {job.location_type && <span className="capitalize">{job.location_type}</span>}
                {job.job_type && <span className="text-slate-500">/</span>}
                {job.job_type && <span className="capitalize">{job.job_type.replace("-", " ")}</span>}
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {job.salary_min && (
                  <Pill className="border-[#9bf6d7] bg-[#9bf6d7] text-[#06110f]">
                    {job.salary_currency} {job.salary_min.toLocaleString()}
                    {job.salary_max ? ` - ${job.salary_max.toLocaleString()}` : "+"}
                  </Pill>
                )}
                {job.experience_min && (
                  <Pill className="border-sky-200 bg-sky-50 text-sky-700">
                    {job.experience_min}
                    {job.experience_max ? `-${job.experience_max}` : "+"} yrs exp
                  </Pill>
                )}
                {job.education && (
                  <Pill className="border-white/15 bg-white/10 text-white">
                    {job.education}
                  </Pill>
                )}
              </div>
              {job.source_url && (
                <a href={job.source_url} target="_blank" rel="noopener noreferrer" className="mt-4 inline-flex items-center gap-1.5 text-xs font-black text-[#9bf6d7] hover:underline">
                  View original job posting
                </a>
              )}
            </div>
          </div>

          <div className="flex flex-col items-start gap-4 rounded-3xl border border-white/15 bg-white/10 p-5 backdrop-blur-xl sm:flex-row sm:items-center lg:flex-col">
            <ScoreRing score={job.match_score} />
            <button
              onClick={() => tailorMutation.mutate()}
              disabled={!canTailor || tailorMutation.isPending}
              className="inline-flex h-11 items-center justify-center rounded-full bg-[#9bf6d7] px-5 text-xs font-black text-[#06110f] shadow-md shadow-[#30d6c2]/20 transition hover:bg-[#b8ffe6] active:scale-95 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {tailorMutation.isPending ? "Tailoring..." : "Tailor Resume"}
            </button>
          </div>
        </div>

        {(tailoredResume || tailorError) && (
          <div className={`relative mt-5 rounded-2xl border px-4 py-3 text-xs font-bold ${tailoredResume ? "border-emerald-300/30 bg-emerald-500/10 text-emerald-200" : "border-rose-300/30 bg-rose-500/10 text-rose-200"}`}>
            {tailoredResume
              ? `Tailored draft ready. ${tailoredResume.unsupported_gaps?.length || 0} unsupported gaps kept out.`
              : tailorError}
          </div>
        )}
      </header>

      <UpgradeModal
        open={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        source="tailor_limit"
        message="You have used your 10 free tailored resumes this month. Upgrade to Pro when you are ready for more tailoring."
      />

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
        <div className="space-y-5 lg:col-span-2">
          <Section title="Application Status" eyebrow="Pipeline">
            <div className="flex flex-wrap gap-2">
              {STATUS_OPTIONS.map((status) => (
                <button
                  key={status.value}
                  onClick={() => statusMutation.mutate(status.value)}
                  disabled={statusMutation.isPending}
                  className={`rounded-full border px-4 py-2 text-xs font-black transition-all duration-200 active:scale-95 disabled:opacity-50 ${
                    job.status === status.value
                      ? `${status.color} shadow-sm`
                      : "border-white/10 bg-white/8 text-slate-300 hover:border-[#30d6c2]/70 hover:text-white"
                  }`}
                >
                  {status.label}
                </button>
              ))}
            </div>
            {job.applied_at && (
              <p className="mt-3 text-xs font-semibold text-slate-400">
                Applied on{" "}
                {new Date(job.applied_at).toLocaleDateString("en-US", {
                  month: "long",
                  day: "numeric",
                  year: "numeric",
                })}
              </p>
            )}
          </Section>

          <Section title="Skills Match" eyebrow="Resume alignment">
            {job.matched_skills?.length > 0 && (
              <div className="mb-5">
                <p className="mb-2 text-xs font-black uppercase tracking-[0.08em] text-[#9bf6d7]">
                  Found in your resume
                </p>
                <div className="flex flex-wrap gap-2">
                  {job.matched_skills.map((skill, index) => (
                    <Pill key={index} className="border-[#9bf6d7] bg-[#9bf6d7] text-[#06110f]">
                      {skill}
                    </Pill>
                  ))}
                </div>
              </div>
            )}

            {job.missing_skills?.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-black uppercase tracking-[0.08em] text-rose-300">
                  Missing from your resume
                </p>
                <div className="flex flex-wrap gap-2">
                  {job.missing_skills.map((skill, index) => (
                    <Pill key={index} className={CATEGORY_STYLES[skill.category] || CATEGORY_STYLES.other}>
                      {skill.name}
                    </Pill>
                  ))}
                </div>
              </div>
            )}

            {!job.matched_skills?.length && !job.missing_skills?.length && (
              <p className="text-sm font-semibold text-slate-300">
                No match data yet. Upload your resume to see results.
              </p>
            )}
          </Section>

          {job.keyword_gaps?.length > 0 && (
            <Section title="Keyword Gaps" eyebrow="Score opportunities">
              <p className="mb-4 text-sm font-semibold text-slate-300">
                Add these keywords to your resume to improve your match score.
              </p>
              <div className="space-y-3">
                {job.keyword_gaps.map((gap, index) => (
                  <div key={index} className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/8 p-4 sm:flex-row sm:items-start sm:justify-between">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm font-black text-white">{gap.keyword}</span>
                      <Pill className={CATEGORY_STYLES[gap.category] || CATEGORY_STYLES.other}>
                        {gap.category}
                      </Pill>
                      <Pill className={PRIORITY_STYLES[gap.priority] || PRIORITY_STYLES.low}>
                        {gap.priority} priority
                      </Pill>
                    </div>
                    <p className="max-w-sm text-sm font-semibold leading-6 text-slate-300 sm:text-right">
                      {gap.context}
                    </p>
                  </div>
                ))}
              </div>
            </Section>
          )}
        </div>

        <aside className="space-y-5">
          <Section title="Job Details" eyebrow="Role snapshot">
            <div className="space-y-3">
              {[
                { label: "Status", value: currentStatus?.label },
                { label: "Job Type", value: job.job_type?.replace("-", " ") },
                { label: "Location Type", value: job.location_type },
                {
                  label: "Experience",
                  value: job.experience_min
                    ? `${job.experience_min}${job.experience_max ? `-${job.experience_max}` : "+"} years`
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
                .map((item, index) => (
                  <div key={index} className="flex items-start justify-between gap-4 border-b border-white/10 pb-3 last:border-0 last:pb-0">
                    <span className="text-xs font-black uppercase tracking-[0.08em] text-slate-400">{item.label}</span>
                    <span className="text-right text-xs font-bold capitalize text-white">{item.value}</span>
                  </div>
                ))}
            </div>
          </Section>

          {job.required_skills?.length > 0 && (
            <Section title="Required Skills">
              <div className="flex flex-wrap gap-2">
                {job.required_skills.map((skill, index) => {
                  const isMatched = job.matched_skills?.includes(skill.name);
                  return (
                    <Pill key={index} className={isMatched ? "border-[#9bf6d7] bg-[#9bf6d7] text-[#06110f]" : CATEGORY_STYLES[skill.category] || CATEGORY_STYLES.other}>
                      {isMatched ? `Found: ${skill.name}` : skill.name}
                    </Pill>
                  );
                })}
              </div>
            </Section>
          )}

          {job.preferred_skills?.length > 0 && (
            <Section title="Preferred Skills">
              <div className="flex flex-wrap gap-2">
                {job.preferred_skills.map((skill, index) => (
                  <Pill key={index} className="border-white/10 bg-white/8 text-slate-200">
                    {skill.name}
                  </Pill>
                ))}
              </div>
            </Section>
          )}

          <section className="rounded-[28px] border border-rose-300/20 bg-[#07110f] p-5 text-white shadow-xl shadow-slate-900/10 sm:p-6">
            <p className="mb-2 text-xs font-black uppercase tracking-[0.16em] text-rose-300">
              Danger Zone
            </p>
            {!showDeleteConfirm ? (
              <button onClick={() => setShowDeleteConfirm(true)} className="w-full rounded-full border border-rose-300/30 bg-rose-500/10 py-2.5 text-xs font-black text-rose-200 transition hover:bg-rose-500/20">
                Delete this job
              </button>
            ) : (
              <div className="space-y-3">
                <p className="text-xs font-semibold text-slate-300">
                  Are you sure? This cannot be undone.
                </p>
                <div className="flex gap-2">
                  <button onClick={() => deleteMutation.mutate()} disabled={deleteMutation.isPending} className="flex-1 rounded-full bg-rose-500 py-2.5 text-xs font-black text-white transition hover:bg-rose-600 disabled:opacity-50">
                    {deleteMutation.isPending ? "Deleting..." : "Yes, delete"}
                  </button>
                  <button onClick={() => setShowDeleteConfirm(false)} className="flex-1 rounded-full border border-white/10 bg-white/8 py-2.5 text-xs font-black text-white transition hover:bg-white/12">
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </section>
        </aside>
      </div>
    </div>
  );
}
