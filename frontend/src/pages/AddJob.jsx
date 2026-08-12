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
    <main className="min-h-screen overflow-hidden bg-[#07110f] text-white">
      <section className="relative isolate px-4 py-8 sm:px-6 sm:py-10 lg:px-12 lg:py-14">
        <div className="absolute inset-0 -z-20 bg-[radial-gradient(circle_at_80%_18%,rgba(246,166,66,0.25),transparent_28%),radial-gradient(circle_at_18%_72%,rgba(76,242,198,0.18),transparent_30%),linear-gradient(132deg,#06110f_0%,#11161b_54%,#f3f0e8_140%)]" />
        <div className="absolute bottom-0 left-0 right-0 -z-10 h-[30vh] bg-[#f3f0e8] [clip-path:polygon(0_36%,36%_62%,64%_48%,100%_8%,100%_100%,0_100%)]" />

        <div className="mx-auto max-w-7xl">
          <div className="rounded-[32px] border border-white/10 bg-white/5 p-6 sm:p-8 shadow-2xl shadow-black/20 backdrop-blur-xl">
            <div className="max-w-3xl">
              <p className="text-sm font-extrabold uppercase tracking-[0.18em] text-[#9bf6d7]">
                AI Resume Matching
              </p>
              <h1 className="mt-4 text-4xl font-black tracking-tight text-white sm:text-5xl md:text-6xl lg:text-[4.5rem]">
                Add a job, upload your resume, and let Resumatch do the rest.
              </h1>
              <p className="mt-6 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
                Submit a job URL or paste the full description to extract role details automatically. Upload your resume to unlock match scores and gap insights.
              </p>
            </div>
          </div>

          <div className="mt-10 grid gap-6 grid-cols-1 lg:grid-cols-[0.9fr_1.1fr]">
            <section className="rounded-[32px] border border-white/10 bg-white/10 p-6 sm:p-8 shadow-xl shadow-black/20 backdrop-blur-xl">
              <div className="grid gap-4 sm:grid-cols-[1fr_auto] sm:items-center mb-5">
                <div>
                  <h2 className="text-sm font-semibold uppercase tracking-[0.12em] text-[#9bf6d7]">
                    Resume Workspace
                  </h2>
                  <p className="mt-2 text-sm text-slate-300">
                    Upload a resume for match scoring, tailored review, and accurate job fit.
                  </p>
                </div>
                {resume && (
                  <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50/20 px-3 py-1 text-xs font-medium text-emerald-200 justify-self-start sm:justify-self-end">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                    Active
                  </span>
                )}
              </div>

              <div className="rounded-[24px] border border-white/10 bg-[#0d1617] p-5 sm:p-6">
                <div className="mb-4 text-sm font-semibold text-slate-300">
                  {resumeLoading
                    ? "Checking resume..."
                    : resume
                    ? `Active resume: ${resume.file_name}`
                    : "No resume uploaded yet."
                  }
                </div>
                <form onSubmit={handleResumeUpload} className="space-y-4">
                  <label className="flex min-h-[64px] flex-col justify-center gap-3 rounded-2xl border border-dashed border-slate-700 bg-slate-950/40 px-4 py-4 text-sm text-slate-300 transition hover:border-emerald-300 hover:bg-[#0f1c1c] cursor-pointer sm:flex-row sm:items-center sm:px-5 sm:py-4">
                    <div className="flex items-center gap-3">
                      <svg className="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <span>
                        {resumeFile
                          ? resumeFile.name
                          : resume
                          ? "Upload a new resume (PDF or DOCX)"
                          : "Choose a PDF or DOCX resume"
                        }
                      </span>
                    </div>
                    <input type="file" accept=".pdf,.docx" className="hidden" onChange={(e) => setResumeFile(e.target.files[0])} />
                  </label>

                  <button
                    type="submit"
                    disabled={!resumeFile || uploadResumeMutation.isPending}
                    className="inline-flex h-14 w-full items-center justify-center rounded-2xl bg-gradient-to-r from-[#10b981] to-[#059669] px-6 text-sm font-semibold text-white shadow-lg shadow-emerald-500/20 transition disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {uploadResumeMutation.isPending ? (
                      <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                      </svg>
                    ) : (
                      "Upload resume"
                    )}
                  </button>
                </form>

                {resumeSuccess && (
                  <div className="mt-4 rounded-2xl bg-emerald-50/20 border border-emerald-200 px-4 py-3 text-sm text-emerald-100">
                    ✓ Resume uploaded successfully — match scores will now be calculated.
                  </div>
                )}
                {uploadResumeMutation.isError && (
                  <div className="mt-4 rounded-2xl bg-red-50/20 border border-red-200 px-4 py-3 text-sm text-red-100">
                    Failed to upload resume. Please try again.
                  </div>
                )}
              </div>
            </section>

            <section className="rounded-[32px] border border-white/10 bg-white/10 p-6 shadow-xl shadow-black/20 backdrop-blur-xl">
              <div className="grid gap-4 sm:grid-cols-[1fr_auto] sm:items-center mb-5">
                <div>
                  <h2 className="text-sm font-semibold uppercase tracking-[0.12em] text-[#9bf6d7]">
                    Job Posting
                  </h2>
                  <p className="mt-2 text-sm text-slate-300">
                    Paste a job URL or description and AI will extract the full role details.
                  </p>
                </div>
                <span className="text-xs text-slate-400 justify-self-start sm:justify-self-end">{tab === "url" ? "URL mode" : "Text mode"}</span>
              </div>

              <div className="rounded-[24px] border border-white/10 bg-[#0d1617] p-5">
                <div className="flex gap-2 rounded-2xl bg-slate-950/70 p-3 text-xs uppercase tracking-[0.15em] text-slate-400">
                  <span className="font-black">Step 1</span>
                  <span>Submit job information</span>
                </div>

                <div className="mt-5">
                  <div className="flex flex-col gap-2 rounded-2xl bg-slate-900/90 p-3 sm:flex-row sm:items-center sm:gap-2">
                    <div className="text-xs uppercase tracking-[0.15em] text-slate-400">
                      <span className="font-black">Step 1</span>
                      <span className="block sm:inline"> Submit job information</span>
                    </div>
                  </div>

                  <div className="mt-5 flex flex-col gap-2 rounded-full bg-slate-900/90 p-1 sm:flex-row">
                    {[
                      { key: "url", label: "Paste URL" },
                      { key: "paste", label: "Paste Text" },
                    ].map((t) => (
                      <button
                        key={t.key}
                        type="button"
                        onClick={() => {
                          setTab(t.key);
                          setError("");
                        }}
                        className={`w-full rounded-2xl px-4 py-2 text-sm font-semibold transition sm:w-auto ${
                          tab === t.key
                            ? "bg-[#111b1c] text-white shadow-inner"
                            : "text-slate-400 hover:text-white"
                        }`}
                      >
                        {t.label}
                      </button>
                    ))}
                  </div>

                  <form onSubmit={handleJobSubmit} className="mt-6 space-y-4">
                    {tab === "url" ? (
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Job post URL
                        </label>
                        <input
                          type="url"
                          value={url}
                          onChange={(e) => setUrl(e.target.value)}
                          placeholder="https://jobs.lever.co/company/job-id"
                          className="w-full rounded-2xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-sm text-white outline-none transition focus:border-emerald-500/70 focus:ring-2 focus:ring-emerald-500/20"
                        />
                        <p className="mt-2 text-xs text-slate-500">
                          ⚠ LinkedIn and Indeed block scraping — use Paste Text for those.
                        </p>
                      </div>
                    ) : (
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Job description
                        </label>
                        <textarea
                          value={description}
                          onChange={(e) => setDescription(e.target.value)}
                          placeholder="Paste the full job description here..."
                          rows={10}
                          className="w-full resize-none rounded-2xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-sm text-white outline-none transition focus:border-emerald-500/70 focus:ring-2 focus:ring-emerald-500/20"
                        />
                      </div>
                    )}

                    {error && (
                      <div className="rounded-2xl bg-red-50/20 border border-red-200 px-4 py-3 text-sm text-red-100">
                        {error}
                      </div>
                    )}

                    {!resume && !resumeLoading && (
                      <div className="rounded-2xl bg-amber-50/20 border border-amber-200 px-4 py-3 text-sm text-amber-100">
                        ⚠ No resume uploaded — job will be saved but match score won't be calculated.
                      </div>
                    )}

                    <button
                      type="submit"
                      disabled={createJobMutation.isPending}
                      className="inline-flex h-14 w-full items-center justify-center rounded-2xl bg-gradient-to-r from-[#10b981] to-[#059669] px-6 text-sm font-semibold text-white shadow-lg shadow-emerald-500/20 transition disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {createJobMutation.isPending ? (
                        <span className="flex items-center gap-2">
                          <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
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
            </section>
          </div>
        </div>
      </section>
    </main>
  );
}
