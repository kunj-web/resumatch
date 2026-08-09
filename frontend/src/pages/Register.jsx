import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { register } from "../api/auth";
import { validateEmail, getPasswordError } from "../utils/validation";

const onboardingSteps = [
  {
    step: "01",
    title: "Create your workspace",
    desc: "Set up a private resume and job tracking hub.",
  },
  {
    step: "02",
    title: "Upload once",
    desc: "Reuse your resume across every role you save.",
  },
  {
    step: "03",
    title: "Tailor fast",
    desc: "Get score, gaps, and rewrite guidance per job.",
  },
];

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), 80);
    return () => clearTimeout(timer);
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const registerMutation = useMutation({
    mutationFn: async (credentials) => {
      const res = await register(credentials);
      return res.data;
    },
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
      navigate("/dashboard");
    },
    onError: (err) => {
      setError(err.response?.data?.detail || "Something went wrong");
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (!form.full_name.trim()) {
      setError("Full name is required");
      return;
    }
    if (form.full_name.trim().length < 2) {
      setError("Full name must be at least 2 characters");
      return;
    }
    if (!form.email.trim()) {
      setError("Email is required");
      return;
    }
    if (!validateEmail(form.email)) {
      setError("Please enter a valid email address");
      return;
    }

    const passwordError = getPasswordError(form.password);
    if (passwordError) {
      setError(passwordError);
      return;
    }
    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    registerMutation.mutate({
      full_name: form.full_name,
      email: form.email.toLowerCase(),
      password: form.password,
    });
  };

  return (
    <main className="relative h-screen w-screen overflow-hidden bg-[#07110f] text-white">
      <style>{`
        @keyframes signup-rise {
          from { opacity: 0; transform: translateY(14px) scale(0.98); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes signup-orbit {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes signup-scan {
          0% { transform: translateX(-100%); opacity: 0; }
          18%, 80% { opacity: 1; }
          100% { transform: translateX(280%); opacity: 0; }
        }
        .signup-rise { animation: signup-rise 0.6s cubic-bezier(.2,.8,.2,1) both; }
      `}</style>

      {/* Background layers — all behind content, never intersect it visually */}
      <div className="absolute inset-0 -z-20 bg-[radial-gradient(circle_at_80%_18%,rgba(246,166,66,0.22),transparent_28%),radial-gradient(circle_at_18%_72%,rgba(76,242,198,0.16),transparent_30%),linear-gradient(132deg,#06110f_0%,#11161b_54%,#171b16_140%)]" />
      <div
        className="pointer-events-none absolute left-[6%] top-[14%] -z-10 hidden h-48 w-48 rounded-full border border-[#9bf6d7]/10 lg:block"
        style={{ animation: "signup-orbit 24s linear infinite" }}
      />
      <div
        className="pointer-events-none absolute right-[6%] bottom-[8%] -z-10 hidden h-56 w-56 rounded-full border border-[#f6a642]/10 lg:block"
        style={{ animation: "signup-orbit 30s linear infinite reverse" }}
      />

      <div className="mx-auto flex h-full max-w-7xl flex-col px-5 sm:px-8 lg:px-12">
        {/* Nav */}
        <nav className="flex shrink-0 items-center justify-between py-2 sm:py-3">
          <Link to="/" className="flex items-center gap-3">
            <span className="grid h-8 w-8 place-items-center rounded-xl bg-[#9bf6d7] text-sm font-black text-[#06110f]">
              R
            </span>
            <span className="text-base font-bold sm:text-lg">Resumatch</span>
          </Link>
          <Link
            to="/login"
            className="rounded-full bg-white/8 px-3.5 py-1.5 text-[11px] font-extrabold text-white transition hover:bg-white/15 sm:px-4 sm:py-2 sm:text-xs"
          >
            Sign in
          </Link>
        </nav>

        {/* Content */}
        <section className="grid min-h-0 flex-1 items-center gap-6 py-2 lg:grid-cols-[minmax(340px,0.5fr)_minmax(0,0.9fr)] lg:gap-10">
          {/* Form card — scrolls internally if it ever runs taller than the viewport, so fields stay reachable without scrolling the page itself */}
          <div
            className={`mx-auto flex h-full w-full max-w-[440px] items-center transition-all duration-700 ${
              visible ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0"
            }`}
          >
            <div className="max-h-full w-full overflow-y-auto rounded-[22px] border border-white/20 bg-white/10 p-1.5 shadow-2xl shadow-black/40 backdrop-blur-2xl [scrollbar-width:thin] sm:p-2">
              <form
                onSubmit={handleSubmit}
                className="rounded-[18px] bg-[#f7f5ee] p-3.5 text-[#15171b] sm:p-4"
              >
                <div className="mb-2 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <div className="inline-flex shrink-0 rounded-full bg-[#101318] px-2.5 py-1 text-[9px] font-extrabold uppercase tracking-[0.1em] text-[#9bf6d7]">
                      New
                    </div>
                    <h1 className="text-sm font-black leading-tight sm:text-base">
                      Build your resume command center
                    </h1>
                  </div>
                  <div className="hidden shrink-0 rounded-xl border border-[#e1ded4] bg-white px-2.5 py-1 text-center sm:block">
                    <div className="text-sm font-black leading-none text-[#28a990]">
                      10
                    </div>
                    <div className="text-[8px] font-bold uppercase tracking-[0.06em] text-slate-500">
                      Free
                    </div>
                  </div>
                </div>

                {error && (
                  <div
                    role="alert"
                    className="mb-2 rounded-xl border border-[#f1a33b]/30 bg-[#f1a33b]/10 px-3.5 py-1.5 text-xs font-semibold text-[#8a5a1a]"
                  >
                    {error}
                  </div>
                )}

                <div className="flex flex-col gap-1.5">
                  <div className="grid gap-2 sm:grid-cols-2">
                    <label className="flex flex-col gap-0.5">
                      <span className="text-[10px] font-black uppercase tracking-[0.08em] text-slate-600">
                        Full name
                      </span>
                      <input
                        type="text"
                        name="full_name"
                        autoComplete="name"
                        value={form.full_name}
                        onChange={handleChange}
                        placeholder="Kunj Bihari"
                        className="h-9 rounded-xl border border-[#e1ded4] bg-white px-3.5 text-sm font-semibold text-[#15171b] outline-none transition placeholder:text-slate-400 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20"
                      />
                    </label>

                    <label className="flex flex-col gap-0.5">
                      <span className="text-[10px] font-black uppercase tracking-[0.08em] text-slate-600">
                        Email address
                      </span>
                      <input
                        type="email"
                        name="email"
                        autoComplete="email"
                        value={form.email}
                        onChange={handleChange}
                        placeholder="you@example.com"
                        className="h-9 rounded-xl border border-[#e1ded4] bg-white px-3.5 text-sm font-semibold text-[#15171b] outline-none transition placeholder:text-slate-400 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20"
                      />
                    </label>
                  </div>

                  <div className="grid gap-2 sm:grid-cols-2">
                    <label className="flex flex-col gap-0.5">
                      <span className="text-[10px] font-black uppercase tracking-[0.08em] text-slate-600">
                        Password
                      </span>
                      <input
                        type="password"
                        name="password"
                        autoComplete="new-password"
                        value={form.password}
                        onChange={handleChange}
                        placeholder="Password"
                        className="h-9 rounded-xl border border-[#e1ded4] bg-white px-3.5 text-sm font-semibold text-[#15171b] outline-none transition placeholder:text-slate-400 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20"
                      />
                    </label>

                    <label className="flex flex-col gap-0.5">
                      <span className="text-[10px] font-black uppercase tracking-[0.08em] text-slate-600">
                        Confirm
                      </span>
                      <input
                        type="password"
                        name="confirmPassword"
                        autoComplete="new-password"
                        value={form.confirmPassword}
                        onChange={handleChange}
                        placeholder="Confirm"
                        className="h-9 rounded-xl border border-[#e1ded4] bg-white px-3.5 text-sm font-semibold text-[#15171b] outline-none transition placeholder:text-slate-400 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20"
                      />
                    </label>
                  </div>

                  <p className="text-[10px] font-semibold leading-4 text-slate-500">
                    Use at least 8 characters with uppercase, lowercase, and a
                    number.
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={registerMutation.isPending}
                  className="relative mt-2.5 inline-flex h-9 w-full items-center justify-center overflow-hidden rounded-full bg-[#101318] text-sm font-black text-white transition hover:bg-[#22262d] active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60 sm:h-9"
                >
                  <span
                    className="absolute inset-y-0 left-0 w-1/3 bg-gradient-to-r from-transparent via-white/25 to-transparent"
                    style={{
                      animation: "signup-scan 2.8s ease-in-out infinite",
                    }}
                  />
                  <span className="relative">
                    {registerMutation.isPending
                      ? "Creating workspace…"
                      : "Create free account"}
                  </span>
                </button>

                <p className="mt-2 text-center text-xs font-semibold text-slate-500">
                  Already have an account?{" "}
                  <Link
                    to="/login"
                    className="font-black text-[#28a990] transition hover:text-[#1c7d6a]"
                  >
                    Sign in
                  </Link>
                </p>
              </form>
            </div>
          </div>

          {/* Marketing column */}
          <div
            className={`hidden max-w-3xl lg:block transition-all delay-100 duration-700 ${
              visible ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"
            }`}
          >
            <p className="mb-2 text-[11px] font-extrabold uppercase tracking-[0.18em] text-[#9bf6d7]">
              Start smarter
            </p>
            <h2 className="text-[clamp(1.5rem,2.6vw,2.4rem)] font-black leading-[1.05] tracking-normal text-white!">
              Create once. Tailor every application.
            </h2>
            <p className="mt-2 max-w-xl text-sm leading-6 text-slate-300">
              Resumatch gives every job its own match report, keyword map, and
              rewrite direction so you can apply with focus.
            </p>

            <div className="mt-4 grid gap-2">
              {onboardingSteps.map((item, index) => (
                <div
                  key={item.step}
                  className="signup-rise flex gap-3 rounded-2xl border border-white/10 bg-white/8 p-3 backdrop-blur-xl"
                  style={{ animationDelay: `${0.1 + index * 0.08}s` }}
                >
                  <span className="text-xs font-black text-[#9bf6d7]">
                    {item.step}
                  </span>
                  <div>
                    <h3 className="text-xs font-black text-white">
                      {item.title}
                    </h3>
                    <p className="mt-0.5 text-[11px] font-semibold leading-4 text-slate-400">
                      {item.desc}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
