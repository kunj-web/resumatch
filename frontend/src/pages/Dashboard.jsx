import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getJobs } from "../api/jobs";
import { getMyResume } from "../api/resume";

const STATUS_STYLES = {
  saved: {
    bg: "bg-gray-100",
    text: "text-gray-600",
    dot: "bg-gray-400",
    label: "Saved",
  },
  applied: {
    bg: "bg-blue-50",
    text: "text-blue-600",
    dot: "bg-blue-500",
    label: "Applied",
  },
  interview: {
    bg: "bg-amber-50",
    text: "text-amber-600",
    dot: "bg-amber-500",
    label: "Interview",
  },
  offer: {
    bg: "bg-emerald-50",
    text: "text-emerald-600",
    dot: "bg-emerald-500",
    label: "Offer",
  },
  rejected: {
    bg: "bg-red-50",
    text: "text-red-600",
    dot: "bg-red-400",
    label: "Rejected",
  },
};

const FILTERS = ["all", "saved", "applied", "interview", "offer", "rejected"];

function ScoreRing({ score }) {
  if (score === null || score === undefined)
    return (
      <div className="w-12 h-12 rounded-full border-2 border-gray-200 flex items-center justify-center">
        <span className="text-xs text-gray-400">—</span>
      </div>
    );
  const color = score >= 75 ? "#10b981" : score >= 50 ? "#f59e0b" : "#ef4444";
  return (
    <div className="relative w-12 h-12">
      <svg className="w-12 h-12 -rotate-90" viewBox="0 0 36 36">
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
      <span
        className="absolute inset-0 flex items-center justify-center text-xs font-bold"
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
    setTimeout(() => setVisible(true), 100);
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
    .filter((j) => filter === "all" || j.status === filter)
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
    applied: jobs.filter((j) => j.status === "applied").length,
    interview: jobs.filter((j) => j.status === "interview").length,
    offer: jobs.filter((j) => j.status === "offer").length,
  };

  return (
    <div
      className="w-full max-w-7xl mx-auto"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(20px)",
        transition: "all 0.5s ease-out",
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">
            Track and manage your job applications
          </p>
        </div>
        <Link
          to="/jobs/new"
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold text-white shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 active:scale-95 transition-all duration-200"
          style={{ background: "linear-gradient(135deg, #10b981, #059669)" }}
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
              d="M12 4v16m8-8H4"
            />
          </svg>
          Add Job
        </Link>
      </div>

      {/* Resume warning */}
      {!resume && (
        <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <svg
              className="w-5 h-5 text-amber-500"
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
            <span className="text-sm text-amber-700 font-medium">
              No resume uploaded — match scores won't be calculated
            </span>
          </div>
          <Link
            to="/jobs/new"
            className="text-xs font-semibold text-amber-600 hover:underline"
          >
            Upload now →
          </Link>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          {
            label: "Total Jobs",
            value: stats.total,
            color: "text-gray-900",
            bg: "bg-white",
          },
          {
            label: "Applied",
            value: stats.applied,
            color: "text-blue-600",
            bg: "bg-blue-50",
          },
          {
            label: "Interviews",
            value: stats.interview,
            color: "text-amber-600",
            bg: "bg-amber-50",
          },
          {
            label: "Offers",
            value: stats.offer,
            color: "text-emerald-600",
            bg: "bg-emerald-50",
          },
        ].map((stat, i) => (
          <div
            key={i}
            className={`${stat.bg} rounded-2xl p-5 border border-gray-100 shadow-sm`}
            style={{
              opacity: visible ? 1 : 0,
              transform: visible ? "translateY(0)" : "translateY(20px)",
              transition: `all 0.5s ease-out ${i * 0.1}s`,
            }}
          >
            <div className={`text-3xl font-bold ${stat.color}`}>
              {stat.value}
            </div>
            <div className="text-gray-500 text-sm mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Filters and Sort */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="flex gap-2 flex-wrap">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all duration-200 ${
                filter === f
                  ? "bg-gray-900 text-white"
                  : "bg-white text-gray-500 border border-gray-200 hover:border-gray-300"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
        <div className="sm:ml-auto">
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="px-3 py-1.5 rounded-lg text-xs font-medium border border-gray-200 bg-white text-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
          >
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
            <option value="score">Highest match</option>
          </select>
        </div>
      </div>

      {/* Jobs List */}
      {isLoading ? (
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
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mb-4">
            <svg
              className="w-8 h-8 text-gray-400"
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
          <h3 className="text-gray-900 font-semibold mb-1">No jobs found</h3>
          <p className="text-gray-500 text-sm mb-4">
            {filter === "all"
              ? "Add your first job to get started"
              : `No jobs with status "${filter}"`}
          </p>
          <Link
            to="/jobs/new"
            className="px-4 py-2 rounded-xl text-sm font-semibold text-white"
            style={{ background: "linear-gradient(135deg, #10b981, #059669)" }}
          >
            Add your first job
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((job, i) => {
            const s = STATUS_STYLES[job.status] || STATUS_STYLES.saved;
            return (
              <Link
                key={job.id}
                to={`/jobs/${job.id}`}
                className="flex items-center gap-4 bg-white rounded-2xl border border-gray-100 p-5 shadow-sm hover:shadow-md hover:border-emerald-200 transition-all duration-200 group"
                style={{
                  opacity: visible ? 1 : 0,
                  transform: visible ? "translateX(0)" : "translateX(-20px)",
                  transition: `all 0.4s ease-out ${i * 0.05}s`,
                }}
              >
                {/* Company initial */}
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-lg flex-shrink-0"
                  style={{
                    background: "linear-gradient(135deg, #0d1b2a, #112240)",
                  }}
                >
                  {job.company ? job.company[0].toUpperCase() : "?"}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-semibold text-gray-900 text-sm group-hover:text-emerald-600 transition-colors duration-200 truncate">
                      {job.title || "Untitled Role"}
                    </h3>
                    {job.extraction_status === "failed" && (
                      <span className="text-xs bg-red-50 text-red-500 border border-red-200 px-2 py-0.5 rounded-full">
                        Extraction failed
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 mt-1 flex-wrap">
                    <span className="text-gray-500 text-xs">
                      {job.company || "Unknown company"}
                    </span>
                    {job.location && (
                      <>
                        <span className="text-gray-300">·</span>
                        <span className="text-gray-500 text-xs">
                          {job.location}
                        </span>
                      </>
                    )}
                    {job.location_type && (
                      <>
                        <span className="text-gray-300">·</span>
                        <span className="text-gray-500 text-xs capitalize">
                          {job.location_type}
                        </span>
                      </>
                    )}
                  </div>
                  <div className="text-gray-400 text-xs mt-1">
                    Added{" "}
                    {new Date(job.created_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    })}
                  </div>
                </div>

                {/* Status + Score */}
                <div className="flex items-center gap-4 flex-shrink-0">
                  <span
                    className={`hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${s.bg} ${s.text}`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
                    {s.label}
                  </span>
                  <ScoreRing score={job.match_score} />
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
