import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getJobs } from "../api/jobs";
import { getMyResume } from "../api/resume";

const STATUS_STYLES = {
  saved: {
    bg: "bg-slate-100",
    text: "text-slate-600",
    dot: "bg-slate-400",
    ring: "ring-slate-200",
    label: "Saved",
  },
  applied: {
    bg: "bg-sky-50",
    text: "text-sky-700",
    dot: "bg-sky-500",
    ring: "ring-sky-100",
    label: "Applied",
  },
  interview: {
    bg: "bg-amber-50",
    text: "text-amber-700",
    dot: "bg-amber-500",
    ring: "ring-amber-100",
    label: "Interview",
  },
  offer: {
    bg: "bg-emerald-50",
    text: "text-emerald-700",
    dot: "bg-emerald-500",
    ring: "ring-emerald-100",
    label: "Offer",
  },
  rejected: {
    bg: "bg-rose-50",
    text: "text-rose-700",
    dot: "bg-rose-400",
    ring: "ring-rose-100",
    label: "Rejected",
  },
};

const FILTERS = ["all", "saved", "applied", "interview", "offer", "rejected"];

const statConfig = [
  { key: "total", label: "Total jobs", accent: "from-[#9bf6d7] to-[#30d6c2]" },
  { key: "applied", label: "Applied", accent: "from-sky-300 to-sky-500" },
  {
    key: "interview",
    label: "Interviews",
    accent: "from-[#ffe6a6] to-[#f6a642]",
  },
  { key: "offer", label: "Offers", accent: "from-emerald-300 to-emerald-500" },
];

function ScoreRing({ score }) {
  if (score === null || score === undefined)
    return (
      <div className="grid h-12 w-12 place-items-center rounded-full border border-slate-200 bg-slate-50">
        <span className="text-xs font-black text-slate-400">-</span>
      </div>
    );

  const color = score >= 75 ? "#28a990" : score >= 50 ? "#f1a33b" : "#ef4444";

  return (
    <div className="relative h-12 w-12">
      <svg className="h-12 w-12 -rotate-90" viewBox="0 0 36 36">
        <circle
          cx="18"
          cy="18"
          r="15"
          fill="none"
          stroke="#e5e0d6"
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
      <span
        className="absolute inset-0 flex items-center justify-center text-xs font-black"
        style={{ color }}
      >
        {score}%
      </span>
    </div>
  );
}

export default function Dashboard() {
  const [filter, setFilter] = useState("all");
  const [sort, setSort] = useState("newest");
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), 80);
    return () => clearTimeout(timer);
  }, []);

  const { data: jobs = [], isLoading } = useQuery({
    queryKey: ["jobs"],
    queryFn: async () => {
      const res = await getJobs();
      return res.data;
    },
  });

  const { data: resume } = useQuery({
    queryKey: ["resume"],
    queryFn: async () => {
      const res = await getMyResume();
      return res.data;
    },
    retry: false,
  });

  const filtered = jobs
    .filter((job) => filter === "all" || job.status === filter)
    .sort((a, b) => {
      if (sort === "newest")
        return new Date(b.created_at) - new Date(a.created_at);
      if (sort === "oldest")
        return new Date(a.created_at) - new Date(b.created_at);
      if (sort === "score")
        return (b.match_score ?? -1) - (a.match_score ?? -1);
      return 0;
    });

  const stats = {
    total: jobs.length,
    applied: jobs.filter((job) => job.status === "applied").length,
    interview: jobs.filter((job) => job.status === "interview").length,
    offer: jobs.filter((job) => job.status === "offer").length,
  };

  const averageScoreJobs = jobs.filter(
    (job) => job.match_score !== null && job.match_score !== undefined,
  );
  const averageScore = averageScoreJobs.length
    ? Math.round(
        averageScoreJobs.reduce((sum, job) => sum + job.match_score, 0) /
          averageScoreJobs.length,
      )
    : null;

  return (
    <div
      className="w-full max-w-7xl mx-auto"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(18px)",
        transition: "all 0.55s cubic-bezier(.2,.8,.2,1)",
      }}
    >
      <div className="relative overflow-hidden rounded-[32px] bg-[#07110f] p-6 text-white shadow-2xl shadow-slate-900/20 sm:p-8 lg:p-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_82%_16%,rgba(246,166,66,0.28),transparent_28%),radial-gradient(circle_at_12%_84%,rgba(76,242,198,0.18),transparent_30%)]" />
        <div className="relative grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-end">
          <div>
            <p className="text-xs font-black uppercase tracking-[0.18em] text-[#9bf6d7]">
              AI Resume Workspace
            </p>
            <h1 className="mt-4 max-w-3xl text-4xl font-black leading-none tracking-normal text-white! sm:text-5xl lg:text-6xl">
              Track every role with match intelligence.
            </h1>
            <p className="mt-5 max-w-2xl text-sm font-semibold leading-6 text-slate-300 sm:text-base">
              Monitor applications, compare scores, and keep every tailored
              resume decision in one focused workspace.
            </p>
          </div>

          <div className="rounded-3xl border border-white/15 bg-white/10 p-5 backdrop-blur-xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.12em] text-slate-400">
                  Avg. match score
                </p>
                <div className="mt-3 text-5xl font-black">
                  {averageScore ?? "--"}
                  <span className="text-2xl text-slate-400">
                    {averageScore === null ? "" : "%"}
                  </span>
                </div>
              </div>
              <div className="grid h-14 w-14 place-items-center rounded-2xl bg-[#9bf6d7] text-xl font-black text-[#06110f]">
                R
              </div>
            </div>
            <div className="mt-5 h-2 rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-gradient-to-r from-[#8af2c9] to-[#30d6c2]"
                style={{ width: `${averageScore ?? 0}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {!resume && (
        <div className="mt-6 flex flex-col gap-4 rounded-3xl border border-[#f6a642]/30 bg-[#fff6df] p-5 text-[#6b4a16] shadow-sm sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="grid h-10 w-10 flex-none place-items-center rounded-2xl bg-[#f6a642]/15">
              <svg
                className="h-5 w-5 text-[#bd7b24]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"
                />
              </svg>
            </div>
            <div>
              <p className="text-sm font-black">No resume uploaded</p>
              <p className="mt-1 text-sm font-semibold text-[#8a6728]">
                Match scores will appear after your first resume upload.
              </p>
            </div>
          </div>
          <Link
            to="/jobs/new"
            className="inline-flex h-11 items-center justify-center rounded-full bg-[#101318] px-5 text-sm font-black text-white transition hover:bg-[#22262d]"
          >
            Upload now
          </Link>
        </div>
      )}

      <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {statConfig.map((stat, index) => (
          <div
            key={stat.key}
            className="relative overflow-hidden rounded-3xl border border-[#e5e0d6] bg-[#f7f5ee] p-5 shadow-sm"
            style={{
              opacity: visible ? 1 : 0,
              transform: visible ? "translateY(0)" : "translateY(16px)",
              transition: `all 0.45s cubic-bezier(.2,.8,.2,1) ${index * 0.08}s`,
            }}
          >
            <div
              className={`absolute right-4 top-4 h-12 w-12 rounded-2xl bg-gradient-to-br ${stat.accent} opacity-80`}
            />
            <div className="relative">
              <p className="text-xs font-black uppercase tracking-[0.1em] text-slate-500">
                {stat.label}
              </p>
              <div className="mt-4 text-4xl font-black text-[#15171b]">
                {stats[stat.key]}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 rounded-[28px] border border-[#e5e0d6] bg-white p-4 shadow-sm sm:p-5">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div>
            <h2 className="text-xl font-black text-[#15171b]">Applications</h2>
            <p className="mt-1 text-sm font-semibold text-slate-500">
              {filtered.length} visible of {jobs.length} saved roles
            </p>
          </div>

          <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
            <div className="flex flex-wrap gap-2">
              {FILTERS.map((filterKey) => (
                <button
                  key={filterKey}
                  type="button"
                  onClick={() => setFilter(filterKey)}
                  className={`rounded-full px-4 py-2 text-xs font-black capitalize transition-all duration-200 ${
                    filter === filterKey
                      ? "bg-[#101318] text-white shadow-lg shadow-slate-900/15"
                      : "border border-[#e5e0d6] bg-[#f7f5ee] text-slate-600 hover:border-[#30d6c2] hover:text-[#15171b]"
                  }`}
                >
                  {filterKey}
                </button>
              ))}
            </div>

            <select
              value={sort}
              onChange={(e) => setSort(e.target.value)}
              className="h-10 rounded-full border border-[#e5e0d6] bg-[#f7f5ee] px-4 text-xs font-black text-slate-700 outline-none transition focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20"
            >
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
              <option value="score">Highest match</option>
            </select>
          </div>
        </div>

        <div className="mt-5">
          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <svg
                className="h-8 w-8 animate-spin text-[#28a990]"
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
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-3xl bg-[#f7f5ee] px-5 py-16 text-center">
              <div className="grid h-16 w-16 place-items-center rounded-2xl bg-[#101318] text-[#9bf6d7]">
                <svg
                  className="h-8 w-8"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
              <h3 className="mt-5 text-lg font-black text-[#15171b]">
                No jobs found
              </h3>
              <p className="mt-2 max-w-sm text-sm font-semibold text-slate-500">
                {filter === "all"
                  ? "Add your first role to start building match intelligence."
                  : `No jobs with status "${filter}" yet.`}
              </p>
              <Link
                to="/jobs/new"
                className="mt-5 inline-flex h-11 items-center justify-center rounded-full bg-[#101318] px-5 text-sm font-black text-white transition hover:bg-[#22262d]"
              >
                Add your first job
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {filtered.map((job, index) => {
                const status = STATUS_STYLES[job.status] || STATUS_STYLES.saved;
                return (
                  <Link
                    key={job.id}
                    to={`/jobs/${job.id}`}
                    className="group grid gap-4 rounded-3xl border border-[#e5e0d6] bg-[#fdfcf8] p-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-[#30d6c2]/60 hover:shadow-xl hover:shadow-slate-900/10 sm:grid-cols-[auto_minmax(0,1fr)_auto] sm:items-center sm:p-5"
                    style={{
                      opacity: visible ? 1 : 0,
                      transform: visible
                        ? "translateX(0)"
                        : "translateX(-16px)",
                      transition: `all 0.4s cubic-bezier(.2,.8,.2,1) ${
                        index * 0.04
                      }s`,
                    }}
                  >
                    <div className="flex items-center gap-4">
                      <div className="grid h-12 w-12 flex-none place-items-center rounded-2xl bg-[#101318] text-lg font-black text-[#9bf6d7] shadow-lg shadow-slate-900/10">
                        {job.company ? job.company[0].toUpperCase() : "?"}
                      </div>
                      <div className="min-w-0 sm:hidden">
                        <h3 className="truncate text-sm font-black text-[#15171b] group-hover:text-[#28a990]">
                          {job.title || "Untitled Role"}
                        </h3>
                        <p className="mt-1 truncate text-xs font-semibold text-slate-500">
                          {job.company || "Unknown company"}
                        </p>
                      </div>
                    </div>

                    <div className="hidden min-w-0 sm:block">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="truncate text-sm font-black text-[#15171b] transition-colors group-hover:text-[#28a990]">
                          {job.title || "Untitled Role"}
                        </h3>
                        {job.extraction_status === "failed" && (
                          <span className="rounded-full border border-rose-200 bg-rose-50 px-2 py-0.5 text-xs font-bold text-rose-600">
                            Extraction failed
                          </span>
                        )}
                      </div>
                      <div className="mt-1 flex flex-wrap items-center gap-2 text-xs font-semibold text-slate-500">
                        <span>{job.company || "Unknown company"}</span>
                        {job.location && (
                          <span className="text-slate-300">/</span>
                        )}
                        {job.location && <span>{job.location}</span>}
                        {job.location_type && (
                          <span className="text-slate-300">/</span>
                        )}
                        {job.location_type && (
                          <span className="capitalize">
                            {job.location_type}
                          </span>
                        )}
                      </div>
                      <div className="mt-1 text-xs font-semibold text-slate-400">
                        Added{" "}
                        {new Date(job.created_at).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })}
                      </div>
                    </div>

                    <div className="flex items-center justify-between gap-4 sm:justify-end">
                      <span
                        className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-black ring-1 ${status.bg} ${status.text} ${status.ring}`}
                      >
                        <span
                          className={`h-1.5 w-1.5 rounded-full ${status.dot}`}
                        />
                        {status.label}
                      </span>
                      <ScoreRing score={job.match_score} />
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
