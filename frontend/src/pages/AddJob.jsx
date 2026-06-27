import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createJob } from "../api/jobs";
import { uploadResume, getMyResume } from "../api/resume";

export default function AddJob() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState("url");
  const [url, setUrl] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [visible, setVisible] = useState(false);
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeSuccess, setResumeSuccess] = useState(false);

  useEffect(() => {
    setTimeout(() => setVisible(true), 100);
  }, []);

  // Uses shared React Query cache — same data as Dashboard, no extra fetch if cached
  const { data: resume, isLoading: resumeLoading } = useQuery({
    queryKey: ["resume"],
    queryFn: async () => {
      const res = await getMyResume();
      return res.data;
    },
    retry: false,
    // Don't throw on 404 — just return null
    throwOnError: false,
  });

  const uploadResumeMutation = useMutation({
    mutationFn: async (file) => {
      const res = await uploadResume(file);
      return res.data;
    },
    onSuccess: (data) => {
      // Update the cache directly with the new resume — no refetch needed
      queryClient.setQueryData(["resume"], data);
      // Also invalidate to confirm from server
      queryClient.invalidateQueries({ queryKey: ["resume"] });
      setResumeSuccess(true);
      setResumeFile(null);
      setTimeout(() => setResumeSuccess(false), 3000);
    },
    onError: () => {
      setResumeSuccess(false);
    },
  });

  const createJobMutation = useMutation({
    mutationFn: async (data) => {
      const res = await createJob(data);
      return res.data;
    },
    onSuccess: (job) => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      navigate(`/jobs/${job.id}`);
    },
    onError: (err) => {
      setError(err.response?.data?.detail || "Something went wrong");
    },
  });

  const handleJobSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (tab === "url" && !url.trim()) {
      setError("Please enter a job URL");
      return;
    }
    if (tab === "paste" && !description.trim()) {
      setError("Please paste a job description");
      return;
    }

    createJobMutation.mutate(
      tab === "url"
        ? { source_url: url.trim() }
        : { raw_description: description.trim() }
    );
  };

  const handleResumeUpload = (e) => {
    e.preventDefault();
    if (!resumeFile) return;
    uploadResumeMutation.mutate(resumeFile);
  };

  return (
    <div
      className="w-full max-w-4xl mx-auto"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(20px)",
        transition: "all 0.5s ease-out",
      }}
    >
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Add a Job</h1>
        <p className="text-gray-500 text-sm mt-1">
          Paste a job URL or description and AI will extract everything
          automatically
        </p>
      </div>

      {/* Resume Section */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-semibold text-gray-900">Your Resume</h2>
            <p className="text-xs text-gray-500 mt-0.5">
              {resumeLoading
                ? "Checking resume..."
                : resume
                ? `Active: ${resume.file_name}`
                : "Upload PDF for matching or DOCX for future tailoring"}
            </p>
          </div>
          {resume && (
            <span className="flex items-center gap-1.5 text-xs text-emerald-600 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              Active
            </span>
          )}
        </div>

        <form onSubmit={handleResumeUpload} className="flex items-center gap-3">
          <label className="flex-1 flex items-center gap-3 px-4 py-3 border-2 border-dashed border-gray-200 rounded-xl cursor-pointer hover:border-emerald-300 hover:bg-emerald-50/50 transition-all duration-200">
            <svg
              className="w-5 h-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <span className="text-sm text-gray-500">
              {resumeFile
                ? resumeFile.name
                : resume
                ? "Upload new resume (PDF or DOCX)"
                : "Choose PDF or DOCX file"}
            </span>
            <input
              type="file"
              accept=".pdf,.docx"
              className="hidden"
              onChange={(e) => setResumeFile(e.target.files[0])}
            />
          </label>
          <button
            type="submit"
            disabled={!resumeFile || uploadResumeMutation.isPending}
            className="px-4 py-3 rounded-xl text-sm font-semibold text-white disabled:opacity-40 disabled:cursor-not-allowed active:scale-95 transition-all duration-200 shadow-md shadow-emerald-500/20"
            style={{ background: "linear-gradient(135deg, #10b981, #059669)" }}
          >
            {uploadResumeMutation.isPending ? (
              <svg
                className="animate-spin h-4 w-4 text-white"
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
            ) : (
              "Upload"
            )}
          </button>
        </form>

        {resumeSuccess && (
          <div className="mt-3 text-xs text-emerald-600 bg-emerald-50 border border-emerald-200 px-3 py-2 rounded-lg">
            ✓ Resume uploaded successfully — match scores will now be calculated
          </div>
        )}
        {uploadResumeMutation.isError && (
          <div className="mt-3 text-xs text-red-600 bg-red-50 border border-red-200 px-3 py-2 rounded-lg">
            Failed to upload resume. Please try again.
          </div>
        )}
      </div>

      {/* Job Input Section */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          Job Posting
        </h2>

        {/* Tabs */}
        <div className="flex gap-1 bg-gray-100 p-1 rounded-xl mb-5 w-fit">
          {[
            { key: "url", label: "Paste URL" },
            { key: "paste", label: "Paste Text" },
          ].map((t) => (
            <button
              key={t.key}
              onClick={() => {
                setTab(t.key);
                setError("");
              }}
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all duration-200 ${
                tab === t.key
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleJobSubmit} className="space-y-4">
          {tab === "url" ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Job post URL
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://jobs.lever.co/company/job-id"
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500 transition-all duration-200"
              />
              <p className="text-xs text-gray-400 mt-2">
                ⚠ LinkedIn and Indeed block scraping — use Paste Text for those.
              </p>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Job description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Paste the full job description here..."
                rows={10}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500 transition-all duration-200 resize-none"
              />
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-600 text-sm rounded-xl">
              {error}
            </div>
          )}

          {!resume && !resumeLoading && (
            <div className="p-3 bg-amber-50 border border-amber-200 text-amber-700 text-xs rounded-xl">
              ⚠ No resume uploaded — job will be saved but match score won't be calculated
            </div>
          )}

          <button
            type="submit"
            disabled={createJobMutation.isPending}
            className="w-full py-3 rounded-xl text-sm font-semibold text-white transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-500/25"
            style={{ background: "linear-gradient(135deg, #10b981, #059669)" }}
          >
            {createJobMutation.isPending ? (
              <span className="flex items-center justify-center gap-2">
                <svg
                  className="animate-spin h-4 w-4 text-white"
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
                AI is extracting job details...
              </span>
            ) : (
              "Extract & Save Job"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
