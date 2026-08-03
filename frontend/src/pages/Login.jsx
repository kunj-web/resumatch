import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.message || "Couldn't sign you in. Check your details and try again.");
      }

      const data = await response.json();
      localStorage.setItem("access_token", data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Something went wrong. Try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="relative isolate flex h-screen flex-col overflow-hidden bg-[#07110f] px-5 text-white sm:px-8 lg:px-12">
      <div className="absolute inset-0 -z-20 bg-[radial-gradient(circle_at_80%_18%,rgba(246,166,66,0.25),transparent_28%),radial-gradient(circle_at_18%_72%,rgba(76,242,198,0.18),transparent_30%),linear-gradient(132deg,#06110f_0%,#11161b_54%,#f3f0e8_140%)]" />
      <div className="absolute bottom-0 left-0 right-0 -z-10 h-[26vh] bg-[#f3f0e8] [clip-path:polygon(0_36%,36%_62%,64%_48%,100%_8%,100%_100%,0_100%)]" />

      <nav className="mx-auto flex w-full max-w-7xl flex-none items-center justify-between py-5 sm:py-6">
        <Link to="/" className="flex items-center gap-3">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-[#9bf6d7] text-base font-black text-[#06110f] sm:h-10 sm:w-10 sm:text-lg">
            R
          </span>
          <span className="text-lg font-bold sm:text-xl">Resumatch</span>
        </Link>

        <Link
          to="/register"
          className="rounded-full bg-white/8 px-4 py-2 text-xs font-extrabold text-white transition hover:bg-white/15 sm:px-5 sm:py-2.5 sm:text-sm"
        >
          Create account
        </Link>
      </nav>

      <div className="mx-auto flex w-full max-w-7xl min-h-0 flex-1 items-center justify-center py-4">
        <div className="w-full max-w-[420px] rounded-[28px] border border-white/20 bg-white/10 p-4 shadow-2xl shadow-black/40 backdrop-blur-2xl sm:max-w-[440px] sm:rounded-[34px] sm:p-6">
          <div className="max-h-[calc(100svh-9rem)] overflow-y-auto rounded-[22px] bg-[#f7f5ee] p-6 text-[#15171b] sm:max-h-none sm:rounded-[28px] sm:p-8">
            <p className="text-xs font-extrabold uppercase tracking-[0.18em] text-[#28a990] sm:text-sm">
              Welcome back
            </p>
            <h1 className="mt-2 text-2xl font-black leading-tight sm:text-3xl">
              Sign in to Resumatch
            </h1>
            <p className="mt-2 text-sm font-semibold leading-6 text-slate-500">
              Pick up your active roles, tailored resumes, and match reports
              right where you left off.
            </p>

            <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
              <label className="flex flex-col gap-1.5">
                <span className="text-xs font-black uppercase tracking-[0.08em] text-slate-600">
                  Email
                </span>
                <input
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@company.com"
                  className="h-12 rounded-2xl border border-[#e1ded4] bg-white px-4 text-base font-semibold text-[#15171b] outline-none transition placeholder:text-slate-400 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20 sm:h-14 sm:px-5"
                />
              </label>

              <label className="flex flex-col gap-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black uppercase tracking-[0.08em] text-slate-600">
                    Password
                  </span>
                  <Link
                    to="/forgot-password"
                    className="text-xs font-bold text-[#28a990] transition hover:text-[#1c7d6a]"
                  >
                    Forgot password?
                  </Link>
                </div>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    autoComplete="current-password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Enter your password"
                    className="h-12 w-full rounded-2xl border border-[#e1ded4] bg-white px-4 pr-12 text-base font-semibold text-[#15171b] outline-none transition placeholder:text-slate-400 focus:border-[#30d6c2] focus:ring-4 focus:ring-[#30d6c2]/20 sm:h-14 sm:px-5 sm:pr-14"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((value) => !value)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    className="absolute inset-y-0 right-0 grid w-12 place-items-center text-slate-400 transition hover:text-slate-700 sm:w-14"
                  >
                    <svg
                      className="h-5 w-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      {showPassword ? (
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M3 3l18 18M10.58 10.58a2 2 0 002.83 2.83M9.88 4.24A9.77 9.77 0 0112 4c5 0 9 4 9.8 8a10.4 10.4 0 01-2.5 4.06M6.6 6.6C4.4 8.1 2.9 10 2.2 12c.6 1.7 1.7 3.2 3.1 4.4A9.7 9.7 0 0012 20c1.1 0 2.1-.2 3-.5"
                        />
                      ) : (
                        <>
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M2.2 12C3.3 7.6 7.3 4 12 4s8.7 3.6 9.8 8c-1.1 4.4-5.1 8-9.8 8s-8.7-3.6-9.8-8z"
                          />
                          <circle cx="12" cy="12" r="3" strokeLinecap="round" strokeLinejoin="round" />
                        </>
                      )}
                    </svg>
                  </button>
                </div>
              </label>

              {error && (
                <p
                  role="alert"
                  className="rounded-2xl border border-[#f1a33b]/30 bg-[#f1a33b]/10 px-4 py-2.5 text-sm font-semibold text-[#8a5a1a]"
                >
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={isSubmitting}
                className="mt-1 inline-flex h-12 items-center justify-center rounded-full bg-[#101318] text-base font-black text-white transition hover:bg-[#22262d] disabled:cursor-not-allowed disabled:opacity-60 sm:h-14"
              >
                {isSubmitting ? "Signing in…" : "Sign in"}
              </button>
            </form>

            <p className="mt-5 text-center text-sm font-semibold text-slate-500">
              New to Resumatch?{" "}
              <Link to="/register" className="font-black text-[#28a990] hover:text-[#1c7d6a]">
                Create an account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}