import { Link } from "react-router-dom";
import { useEffect, useState } from "react";

const metrics = [
  { value: "94%", label: "Match clarity" },
  { value: "3m", label: "Tailoring time" },
  { value: "12", label: "Active roles" },
];

const features = [
  {
    title: "Keyword lift",
    value: "+31%",
    tone: "text-teal-600",
  },
  {
    title: "ATS health",
    value: "92",
    tone: "text-amber-500",
  },
];

export default function Landing() {
  const [showHeader, setShowHeader] = useState(false);
  const isAuthed = Boolean(localStorage.getItem("access_token"));
  const appPath = isAuthed ? "/dashboard" : "/register";

  useEffect(() => {
    const handleScroll = () => {
      setShowHeader(window.scrollY > 120);
    };

    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <main className="min-h-screen overflow-hidden bg-[#07110f] text-white">
      <section className="relative isolate min-h-screen px-5 py-6 sm:px-8 lg:px-12">
        <div className="absolute inset-0 -z-20 bg-[radial-gradient(circle_at_80%_18%,rgba(246,166,66,0.25),transparent_28%),radial-gradient(circle_at_18%_72%,rgba(76,242,198,0.18),transparent_30%),linear-gradient(132deg,#06110f_0%,#11161b_54%,#f3f0e8_140%)]" />
        <div className="absolute bottom-0 left-0 right-0 -z-10 h-[30vh] bg-[#f3f0e8] [clip-path:polygon(0_36%,36%_62%,64%_48%,100%_8%,100%_100%,0_100%)]" />

        <nav
          className={`fixed inset-x-0 top-5 z-50 mx-auto flex max-w-7xl items-center justify-between rounded-[28px] border border-white/15 px-4 py-3 backdrop-blur-xl transition-all duration-500 ease-out sm:px-6 ${
            showHeader
              ? "bg-[#07110f]/80 shadow-2xl shadow-black/25"
              : "bg-white/8 shadow-none"
          }`}
        >
          <Link to="/" className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-[#9bf6d7] text-lg font-black text-[#06110f]">
              R
            </span>
            <span className="text-xl font-bold">Resumatch</span>
          </Link>

          <div className="hidden items-center gap-8 text-sm font-semibold text-slate-200 md:flex">
            <a href="#product" className="transition hover:text-[#9bf6d7]">
              Product
            </a>
            <a href="#workflow" className="transition hover:text-[#9bf6d7]">
              Workflow
            </a>
            <a href="#security" className="transition hover:text-[#9bf6d7]">
              Security
            </a>
          </div>

          <Link
            to={isAuthed ? "/dashboard" : "/login"}
            className="rounded-full bg-[#f3f0e8] px-5 py-2.5 text-sm font-extrabold text-[#101318] transition hover:bg-white"
          >
            Open app
          </Link>
        </nav>

        <div className="mx-auto grid max-w-7xl items-center gap-12 pb-20 pt-16 lg:grid-cols-[minmax(0,0.95fr)_minmax(420px,0.72fr)] lg:gap-14 lg:pb-28 lg:pt-20">
          <div className="max-w-3xl">
            <p className="mb-6 text-sm font-extrabold uppercase tracking-[0.18em] text-[#9bf6d7]">
              AI Resume Matching
            </p>
            <h1 className="max-w-[780px] text-[clamp(3rem,7vw,6.5rem)] font-black leading-[0.96] tracking-normal text-white!">
              Resumatch turns each job into your strongest resume.
            </h1>
            <p className="mt-8 max-w-2xl text-lg leading-8 text-slate-300 sm:text-xl">
              Upload once. Track roles. Generate tailored resume reviews with
              clear gaps, match scores, and interview-ready positioning.
            </p>

            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              <Link
                to={appPath}
                className="inline-flex h-14 items-center justify-center rounded-full bg-[#9bf6d7] px-8 text-base font-black text-[#06110f] transition hover:bg-[#b8ffe6]"
              >
                Start matching
              </Link>
              <a
                href="#product"
                className="inline-flex h-14 items-center justify-center rounded-full border border-white/15 bg-white/10 px-8 text-base font-extrabold text-white transition hover:bg-white/15"
              >
                View demo
              </a>
            </div>

            <div className="mt-14 grid max-w-xl grid-cols-3 gap-5">
              {metrics.map((metric) => (
                <div key={metric.label}>
                  <div className="text-3xl font-black sm:text-4xl">
                    {metric.value}
                  </div>
                  <div className="mt-2 text-[0.68rem] font-bold uppercase tracking-[0.08em] text-slate-400 sm:text-xs">
                    {metric.label}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div
            id="product"
            className="relative mx-auto w-full max-w-[520px] rounded-[34px] border border-white/20 bg-white/10 p-5 shadow-2xl shadow-black/40 backdrop-blur-2xl sm:p-7"
          >
            <div className="rounded-[28px] bg-[#f7f5ee] p-6 text-[#15171b] sm:p-7">
              <div className="flex items-center justify-between rounded-2xl bg-[#101318] p-5 text-white">
                <div>
                  <div className="text-xs font-extrabold uppercase tracking-[0.12em] text-[#9bf6d7]">
                    Live match report
                  </div>
                  <div className="mt-2 text-base font-extrabold">
                    Senior Product Designer
                  </div>
                </div>
                <div className="grid h-10 w-10 place-items-center rounded-full bg-[#9bf6d7] text-sm font-black text-[#06110f]">
                  A
                </div>
              </div>

              <div className="mt-8">
                <div className="flex flex-wrap items-end gap-x-5 gap-y-2">
                  <div className="text-6xl font-black leading-none">86</div>
                  <div className="pb-1">
                    <div className="text-2xl font-black">match score</div>
                    <div className="mt-1 text-sm font-semibold text-slate-500">
                      Strong fit, 4 gaps to close
                    </div>
                  </div>
                </div>
                <div className="mt-6 h-3 rounded-full bg-[#e1ded4]">
                  <div className="h-full w-[86%] rounded-full bg-gradient-to-r from-[#8af2c9] to-[#30d6c2]" />
                </div>
              </div>

              <div className="mt-8 grid grid-cols-2 gap-4">
                {features.map((feature) => (
                  <div key={feature.title} className="rounded-2xl bg-white p-5">
                    <div className="text-sm font-black">{feature.title}</div>
                    <div className={`mt-3 text-4xl font-black ${feature.tone}`}>
                      {feature.value}
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 rounded-3xl bg-[#101318] p-5 text-white">
                <div className="text-base font-black">Suggested rewrite</div>
                <p className="mt-3 text-sm leading-6 text-slate-300">
                  Lead with metrics, systems thinking, and B2B workflow
                  outcomes.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div
          id="workflow"
          className="relative mx-auto -mt-4 flex max-w-7xl flex-col gap-6 rounded-[32px] border border-[#e5e0d6] bg-white p-6 text-[#15171b] shadow-xl shadow-black/10 sm:p-8 lg:flex-row lg:items-center lg:justify-between"
        >
          <div className="flex gap-5">
            <div className="grid h-16 w-16 flex-none place-items-center rounded-2xl bg-[#101318]">
              <svg
                className="h-8 w-8 text-[#9bf6d7]"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth="2.4"
              >
                <path d="M7 7h10M7 12h10M7 17h6" strokeLinecap="round" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-black sm:text-2xl">
                Track every application in one intelligent workspace
              </h2>
              <p className="mt-2 max-w-3xl text-sm font-semibold leading-6 text-slate-500 sm:text-base">
                Jobs, resumes, billing upgrades, and tailored reviews become one
                fast decision loop.
              </p>
            </div>
          </div>
          <Link
            to={appPath}
            className="inline-flex h-14 items-center justify-center rounded-full bg-[#101318] px-8 text-sm font-black text-white transition hover:bg-[#22262d] sm:min-w-[200px]"
          >
            Try Resumatch
          </Link>
        </div>
      </section>

      <section
        id="security"
        className="bg-[#f3f0e8] px-5 pb-16 pt-8 text-[#15171b] sm:px-8 lg:px-12"
      >
        <div className="mx-auto grid max-w-7xl gap-4 md:grid-cols-3">
          {[
            "Private resume workspace",
            "Fast role-by-role comparison",
            "Clear next best actions",
          ].map((item) => (
            <div
              key={item}
              className="border-t border-[#d7d1c4] py-5 text-sm font-black uppercase tracking-[0.08em] text-slate-700"
            >
              {item}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
