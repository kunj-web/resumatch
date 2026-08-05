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
    <main className="relative min-h-screen overflow-hidden bg-[#07110f] px-5 py-6 text-white sm:px-8 lg:px-12">
      <style>{`
        @keyframes signup-rise {
          from { opacity: 0; transform: translateY(18px) scale(0.98); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes signup-float {
          0%, 100% { transform: translate3d(0, 0, 0); }
          50% { transform: translate3d(0, -14px, 0); }
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
        .signup-rise { animation: signup-rise 0.7s cubic-bezier(.2,.8,.2,1) both; }
      `}</style>

      <div className="absolute inset-0 -z-20 bg-[radial-gradient(circle_at_80%_18%,rgba(246,166,66,0.25),transparent_28%),radial-gradient(circle_at_18%_72%,rgba(76,242,198,0.18),transparent_30%),linear-gradient(132deg,#06110f_0%,#11161b_54%,#f3f0e8_140%)]" />
      <div className="absolute bottom-0 left-0 right-0 -z-10 h-[28vh] bg-[#f3f0e8] [clip-path:polygon(0_42%,36%_64%,65%_48%,100%_8%,100%_100%,0_100%)]" />
      <div className="pointer-events-none absolute left-[7%] top-[19%] hidden h-56 w-56 rounded-full border border-[#9bf6d7]/15 lg:block" style={{ animation: "signup-orbit 22s linear infinite" }} />
      <div className="pointer-events-none absolute right-[8%] top-[18%] hidden h-72 w-72 rounded-full border border-[#f6a642]/15 lg:block" style={{ animation: "signup-orbit 30s linear infinite reverse" }} />

      <nav className="mx-auto flex w-full max-w-7xl items-center justify-between py-0">
        <Link to="/" className="flex items-center gap-3">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-[#9bf6d7] text-base font-black text-[#06110f] sm:h-10 sm:w-10 sm:text-lg">
            R
          </span>
          <span className="text-lg font-bold sm:text-xl">Resumatch</span>
        </Link>
        <Link
          to="/login"
          className="rounded-full bg-white/8 px-4 py-2 text-xs font-extrabold text-white transition hover:bg-white/15 sm:px-5 sm:py-2.5 sm:text-sm"
        >
          Sign in
        </Link>
      </nav>

      <section className="mx-auto grid max-w-7xl items-center gap-10 py-12 lg:min-h-[calc(100vh-104px)] lg:grid-cols-[minmax(380px,0.58fr)_minmax(0,0.9fr)] lg:gap-16 lg:py-0">
        <div
          className={`relative mx-auto w-full max-w-[460px] transition-all duration-700 ${
            visible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
          }`}
        >
          <div
            className="pointer-events-none absolute -right-10 top-10 hidden w-48 rounded-3xl border border-white/15 bg-white/10 p-4 shadow-2xl shadow-black/25 backdrop-blur-2xl lg:block"
            style={{ animation: "signup-float 5.8s ease-in-out infinite" }}
          >
            <div className="text-xs font-extrabold uppercase tracking-[0.12em] text-[#9bf6d7]">
              Free workspace
            </div>
            <div className="mt-3 text-3xl font-black">10</div>
            <div className="mt-1 text-xs font-bold uppercase tracking-[0.08em] text-slate-400">
              Tailored resumes
            </div>
          </div>

          <div className="rounded-[34px] border border-white/20 bg-white/10 p-4 shadow-2xl shadow-black/40 backdrop-blur-2xl sm:p-6">
            <form
              onSubmit={handleSubmit}
              className="rounded-[28px] bg-[#f7f5ee] p-6 text-[#15171b] sm:p-8"
            >
              <div className="mb-7">
                <div className="mb-4 inline-flex rounded-full bg-[#101318] px-4 py-2 text-xs font-extrabold uppercase tracking-[0.12em] text-[#9bf6d7]">
                  Create account
                </div>
                <h1 className="text-2xl font-black leading-tight sm:text-3xl">
                  Build your resume command center
                </h1>
                <p className="mt-2 text-sm font-semibold leading-6 text-slate-500">
                  Start free and turn job descriptions into sharper, targeted
                  resumes.
                </p>
              </div>

              {error && (
                <div
                  role="alert"
                  className="mb-5 rounded-2xl border border-[#f1a33b]/30 bg-[#f1a33b]/10 px-4 py-2.5 text-sm font-semibold text-[#8a5a1a]"
                >
                  {error}
                </div>
              )}

              <div className="flex flex-col gap-4">
                <label className="flex flex-col gap-1.5">
                  <span className="text-xs font-black uppercase tracking-[0.08em] text-slate-600">
                    Full name
                  </span>
                  <input
                    type="text"
                    name="full_name"
                    autoComplete="name"
                    value={form.full_name}
                    onChange={handleChange}
                    placeholder="Kunj Bihari"
                    className="h-12 rounded-2xl border border-[#e1ded4] bg-white px-4 text-base font-semibold text-[#15171b] outline-none transition placeholder:text-slate-400 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20 sm:h-14 sm:px-5"
                  />
                </label>

                <label className="flex flex-col gap-1.5">
                  <span className="text-xs font-black uppercase tracking-[0.08em] text-slate-600">
                    Email address
                  </span>
                  <input
                    type="email"
                    name="email"
                    autoComplete="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="you@example.com"
                    className="h-12 rounded-2xl border border-[#e1ded4] bg-white px-4 text-base font-semibold text-[#15171b] outline-none transition placeholder:text-slate-400 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20 sm:h-14 sm:px-5"
                  />
                </label>

                <div className="grid gap-4 sm:grid-cols-2">
                  <label className="flex flex-col gap-1.5">
                    <span className="text-xs font-black uppercase tracking-[0.08em] text-slate-600">
                      Password
                    </span>
                    <input
                      type="password"
                      name="password"
                      autoComplete="new-password"
                      value={form.password}
                      onChange={handleChange}
                      placeholder="Password"
                      className="h-12 rounded-2xl border border-[#e1ded4] bg-white px-4 text-base font-semibold text-[#15171b] outline-none transition placeholder:text-slate-400 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20 sm:h-14 sm:px-5"
                    />
                  </label>

                  <label className="flex flex-col gap-1.5">
                    <span className="text-xs font-black uppercase tracking-[0.08em] text-slate-600">
                      Confirm
                    </span>
                    <input
                      type="password"
                      name="confirmPassword"
                      autoComplete="new-password"
                      value={form.confirmPassword}
                      onChange={handleChange}
                      placeholder="Confirm"
                      className="h-12 rounded-2xl border border-[#e1ded4] bg-white px-4 text-base font-semibold text-[#15171b] outline-none transition placeholder:text-slate-400 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20 sm:h-14 sm:px-5"
                    />
                  </label>
                </div>

                <p className="text-xs font-semibold leading-5 text-slate-500">
                  Use at least 8 characters with uppercase, lowercase, and a
                  number.
                </p>
              </div>

              <button
                type="submit"
                disabled={registerMutation.isPending}
                className="relative mt-6 inline-flex h-12 w-full items-center justify-center overflow-hidden rounded-full bg-[#101318] text-base font-black text-white transition hover:bg-[#22262d] active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60 sm:h-14"
              >
                <span
                  className="absolute inset-y-0 left-0 w-1/3 bg-gradient-to-r from-transparent via-white/25 to-transparent"
                  style={{ animation: "signup-scan 2.8s ease-in-out infinite" }}
                />
                <span className="relative">
                  {registerMutation.isPending
                    ? "Creating workspace…"
                    : "Create free account"}
                </span>
              </button>

              <p className="mt-5 text-center text-sm font-semibold text-slate-500">
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

        <div
          className={`max-w-3xl transition-all delay-100 duration-700 ${
            visible ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0"
          }`}
        >
          <p className="mb-5 text-sm font-extrabold uppercase tracking-[0.18em] text-[#9bf6d7]">
            Start smarter
          </p>
          <h2 className="text-[clamp(2.5rem,6vw,6.2rem)] font-black leading-[0.96] tracking-normal">
            Create once. Tailor every application.
          </h2>
          <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-300 sm:text-xl">
            Resumatch gives every job its own match report, keyword map, and
            rewrite direction so you can apply with focus.
          </p>

          <div className="mt-10 grid gap-4">
            {onboardingSteps.map((item, index) => (
              <div
                key={item.step}
                className="signup-rise flex gap-4 rounded-3xl border border-white/10 bg-white/8 p-5 backdrop-blur-xl"
                style={{ animationDelay: `${0.12 + index * 0.09}s` }}
              >
                <span className="text-sm font-black text-[#9bf6d7]">
                  {item.step}
                </span>
                <div>
                  <h3 className="text-base font-black text-white">
                    {item.title}
                  </h3>
                  <p className="mt-1 text-sm font-semibold leading-6 text-slate-400">
                    {item.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}