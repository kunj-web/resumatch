import { useMemo, useState } from "react";

const tones = ["confident", "warm", "concise"];

export default function CoverLetter() {
  const [form, setForm] = useState({
    role: "",
    company: "",
    hiringManager: "",
    highlights: "",
    tone: "confident",
  });

  const draft = useMemo(() => {
    const role = form.role.trim() || "the role";
    const company = form.company.trim() || "your team";
    const greeting = form.hiringManager.trim()
      ? `Dear ${form.hiringManager.trim()},`
      : "Dear Hiring Team,";
    const highlights =
      form.highlights.trim() ||
      "my experience building measurable outcomes, collaborating across teams, and learning quickly in fast-moving environments";
    const toneLine =
      form.tone === "warm"
        ? "I am genuinely excited by the chance to bring thoughtful energy and practical execution to"
        : form.tone === "concise"
          ? "I am interested in bringing focused execution and measurable impact to"
          : "I am excited to bring strong ownership, clear judgment, and measurable impact to";

    return `${greeting}

${toneLine} ${company} as ${role}. Across my work, I have developed strengths in ${highlights}.

What stands out to me about this opportunity is the chance to connect business needs with crisp execution. I would bring a practical, user-focused approach, strong communication, and the ability to turn ambiguous goals into clear next steps.

I would welcome the chance to discuss how my background can support ${company}'s goals for this role.

Sincerely,`;
  }, [form]);

  const handleChange = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value });
  };

  const copyDraft = async () => {
    await navigator.clipboard.writeText(draft);
  };

  return (
    <div className="mx-auto w-full max-w-7xl">
      <section className="relative overflow-hidden rounded-[32px] bg-[#07110f] p-6 text-white shadow-2xl shadow-slate-900/20 sm:p-8 lg:p-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_82%_16%,rgba(246,166,66,0.24),transparent_28%),radial-gradient(circle_at_12%_84%,rgba(76,242,198,0.18),transparent_30%)]" />
        <div className="relative max-w-3xl">
          <p className="text-xs font-black uppercase tracking-[0.18em] text-[#9bf6d7]">
            Cover Letter Studio
          </p>
          <h1 className="mt-4 text-4xl font-black leading-none tracking-normal !text-white sm:text-5xl lg:text-6xl">
            Create a sharper first impression.
          </h1>
          <p className="mt-5 text-sm font-semibold leading-6 text-slate-300 sm:text-base">
            Draft a focused cover letter from the role, company, and your best
            evidence. Keep it human, direct, and ready to edit.
          </p>
        </div>
      </section>

      <div className="mt-6 grid gap-5 lg:grid-cols-[minmax(0,0.8fr)_minmax(420px,1fr)]">
        <section className="rounded-[28px] border border-white/10 bg-[#07110f] p-5 text-white shadow-xl shadow-slate-900/10 sm:p-6">
          <p className="mb-2 text-xs font-black uppercase tracking-[0.16em] text-[#9bf6d7]">
            Inputs
          </p>
          <h2 className="mb-5 text-xl font-black !text-white">
            Letter details
          </h2>

          <div className="space-y-4">
            <label className="block">
              <span className="text-xs font-black uppercase tracking-[0.08em] text-slate-300">
                Role
              </span>
              <input
                name="role"
                value={form.role}
                onChange={handleChange}
                placeholder="Senior Product Designer"
                className="mt-2 h-12 w-full rounded-2xl border border-white/10 bg-white/8 px-4 text-sm font-semibold text-white outline-none placeholder:text-slate-500 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20"
              />
            </label>

            <label className="block">
              <span className="text-xs font-black uppercase tracking-[0.08em] text-slate-300">
                Company
              </span>
              <input
                name="company"
                value={form.company}
                onChange={handleChange}
                placeholder="Acme"
                className="mt-2 h-12 w-full rounded-2xl border border-white/10 bg-white/8 px-4 text-sm font-semibold text-white outline-none placeholder:text-slate-500 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20"
              />
            </label>

            <label className="block">
              <span className="text-xs font-black uppercase tracking-[0.08em] text-slate-300">
                Hiring manager
              </span>
              <input
                name="hiringManager"
                value={form.hiringManager}
                onChange={handleChange}
                placeholder="Optional"
                className="mt-2 h-12 w-full rounded-2xl border border-white/10 bg-white/8 px-4 text-sm font-semibold text-white outline-none placeholder:text-slate-500 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20"
              />
            </label>

            <label className="block">
              <span className="text-xs font-black uppercase tracking-[0.08em] text-slate-300">
                Strongest highlights
              </span>
              <textarea
                name="highlights"
                value={form.highlights}
                onChange={handleChange}
                rows={6}
                placeholder="Example: improving conversion by 18%, leading cross-functional discovery, shipping dashboard workflows..."
                className="mt-2 w-full resize-none rounded-2xl border border-white/10 bg-white/8 px-4 py-3 text-sm font-semibold leading-6 text-white outline-none placeholder:text-slate-500 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20"
              />
            </label>

            <div>
              <span className="text-xs font-black uppercase tracking-[0.08em] text-slate-300">
                Tone
              </span>
              <div className="mt-2 flex flex-wrap gap-2">
                {tones.map((tone) => (
                  <button
                    key={tone}
                    type="button"
                    onClick={() => setForm({ ...form, tone })}
                    className={`rounded-full px-4 py-2 text-xs font-black capitalize transition ${
                      form.tone === tone
                        ? "bg-[#9bf6d7] text-[#06110f]"
                        : "border border-white/10 bg-white/8 text-slate-300 hover:text-white"
                    }`}
                  >
                    {tone}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="rounded-[28px] border border-[#e5e0d6] bg-[#f7f5ee] p-5 text-[#15171b] shadow-sm sm:p-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.16em] text-[#28a990]">
                Draft
              </p>
              <h2 className="mt-2 text-xl font-black">Cover letter preview</h2>
            </div>
            <button
              type="button"
              onClick={copyDraft}
              className="inline-flex h-11 items-center justify-center rounded-full bg-[#101318] px-5 text-sm font-black text-white transition hover:bg-[#22262d]"
            >
              Copy draft
            </button>
          </div>

          <div className="mt-5 whitespace-pre-wrap rounded-3xl border border-[#e5e0d6] bg-white p-5 text-sm font-semibold leading-7 text-slate-700">
            {draft}
          </div>
        </section>
      </div>
    </div>
  );
}
