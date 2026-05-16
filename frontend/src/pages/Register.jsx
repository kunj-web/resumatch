import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { register } from "../api/auth";
import { validateEmail, getPasswordError } from "../utils/validation";

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
    setTimeout(() => setVisible(true), 100);
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const registerMutation = useMutation({
    mutationFn: async (credentials) => {
      const res = await register(credentials);
      return res.data;
    },
    onSuccess: () => {
      navigate("/login");
    },
    onError: (err) => {
      setError(err.response?.data?.detail || "Something went wrong");
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    // Validation
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
    <div
      className="min-h-screen flex overflow-hidden"
      style={{ background: "#0d1b2a" }}
    >
      <style>{`
        @keyframes slideLeft {
          from { opacity: 0; transform: translateX(-40px); }
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes slideRight {
          from { opacity: 0; transform: translateX(40px); }
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes floatUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse-slow {
          0%, 100% { opacity: 0.15; transform: scale(1); }
          50% { opacity: 0.25; transform: scale(1.05); }
        }
        @keyframes pulse-slow2 {
          0%, 100% { opacity: 0.1; transform: scale(1); }
          50% { opacity: 0.2; transform: scale(1.08); }
        }
        @keyframes drift {
          0%, 100% { transform: translateY(0px) translateX(0px); }
          25% { transform: translateY(-15px) translateX(10px); }
          50% { transform: translateY(-8px) translateX(-10px); }
          75% { transform: translateY(-20px) translateX(5px); }
        }
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes meteor {
          0% { transform: translateX(0) translateY(0); opacity: 1; }
          100% { transform: translateX(-300px) translateY(300px); opacity: 0; }
        }
        @keyframes gridMove {
          0% { transform: translateY(0); }
          100% { transform: translateY(4rem); }
        }
        .animate-slide-left { animation: slideLeft 0.7s ease-out forwards; }
        .animate-slide-right { animation: slideRight 0.7s ease-out forwards; }
        .stagger-1 { animation: floatUp 0.5s ease-out 0.1s both; }
        .stagger-2 { animation: floatUp 0.5s ease-out 0.2s both; }
        .stagger-3 { animation: floatUp 0.5s ease-out 0.3s both; }
        .stagger-4 { animation: floatUp 0.5s ease-out 0.4s both; }
        .stagger-5 { animation: floatUp 0.5s ease-out 0.5s both; }
        .stagger-6 { animation: floatUp 0.5s ease-out 0.6s both; }
        .stagger-7 { animation: floatUp 0.5s ease-out 0.7s both; }
      `}</style>

      {/* Left Panel */}
      <div
        className={`hidden lg:flex w-1/2 flex-col justify-between p-12 relative overflow-hidden ${visible ? "animate-slide-left" : "opacity-0"}`}
        style={{
          background:
            "linear-gradient(135deg, #0d1b2a 0%, #112240 60%, #0d2137 100%)",
        }}
      >
        {/* Moving grid */}
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage:
              "linear-gradient(to right, #10b981 1px, transparent 1px), linear-gradient(to bottom, #10b981 1px, transparent 1px)",
            backgroundSize: "3rem 3rem",
            animation: "gridMove 8s linear infinite",
          }}
        />

        {/* Orbs */}
        <div
          className="absolute top-20 left-20 w-80 h-80 rounded-full"
          style={{
            background: "radial-gradient(circle, #10b981 0%, transparent 70%)",
            animation: "pulse-slow 6s ease-in-out infinite",
          }}
        />
        <div
          className="absolute bottom-20 right-10 w-64 h-64 rounded-full"
          style={{
            background: "radial-gradient(circle, #059669 0%, transparent 70%)",
            animation: "pulse-slow2 8s ease-in-out infinite",
          }}
        />

        {/* Meteors */}
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="absolute w-px bg-gradient-to-b from-emerald-400 to-transparent"
            style={{
              height: `${60 + i * 20}px`,
              right: `${10 + i * 18}%`,
              top: `${5 + i * 12}%`,
              opacity: 0.3,
              animation: `meteor ${3 + i * 1.5}s linear ${i * 2}s infinite`,
            }}
          />
        ))}

        {/* Floating dots */}
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full"
            style={{
              width: `${4 + (i % 3) * 2}px`,
              height: `${4 + (i % 3) * 2}px`,
              background: "#10b981",
              opacity: 0.2 + (i % 4) * 0.1,
              left: `${10 + i * 11}%`,
              top: `${15 + (i % 5) * 16}%`,
              animation: `drift ${5 + i}s ease-in-out infinite`,
            }}
          />
        ))}

        {/* Spinning rings */}
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full border border-emerald-500/10"
          style={{ animation: "spin-slow 20s linear infinite" }}
        />
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-72 h-72 rounded-full border border-emerald-500/10"
          style={{ animation: "spin-slow 15s linear infinite reverse" }}
        />
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 rounded-full border border-emerald-500/10"
          style={{ animation: "spin-slow 10s linear infinite" }}
        />

        {/* Logo */}
        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/30">
              <span className="text-white font-bold text-lg">R</span>
            </div>
            <span className="text-white font-bold text-xl">ResuMatch</span>
          </div>
        </div>

        {/* Center content */}
        <div className="relative z-10">
          <h2 className="text-4xl font-bold text-white leading-tight mb-4">
            Your job search
            <br />
            <span className="text-emerald-400">starts here</span>
          </h2>
          <p className="text-gray-400 text-base leading-relaxed mb-8">
            Create your free account and start matching your resume to any job
            posting in seconds. No credit card required.
          </p>

          {/* Steps */}
          <div className="space-y-4">
            {[
              {
                step: "01",
                title: "Upload your resume",
                desc: "PDF supported, parsed instantly",
              },
              {
                step: "02",
                title: "Paste a job posting",
                desc: "URL or raw text, we handle both",
              },
              {
                step: "03",
                title: "Get your match score",
                desc: "See exactly what to improve",
              },
            ].map((item, i) => (
              <div
                key={i}
                className="flex items-start gap-4 bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm"
              >
                <span className="text-emerald-400 font-bold text-sm mt-0.5">
                  {item.step}
                </span>
                <div>
                  <div className="text-white text-sm font-medium">
                    {item.title}
                  </div>
                  <div className="text-gray-500 text-xs mt-0.5">
                    {item.desc}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom */}
        <div className="relative z-10 bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
          <p className="text-gray-400 text-sm italic">
            "Stop guessing and start applying smarter."
          </p>
          <p className="text-emerald-400 text-xs mt-2 font-medium">
            — ResuMatch AI
          </p>
        </div>
      </div>

      {/* Right Panel — Register Form */}
      <div
        className={`w-full lg:w-1/2 flex items-center justify-center p-8 ${visible ? "animate-slide-right" : "opacity-0"}`}
        style={{ background: "#f8fafc" }}
      >
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">R</span>
            </div>
            <span className="font-bold text-gray-900">ResuMatch</span>
          </div>

          {/* Heading */}
          <div className="mb-8 stagger-1">
            <h1 className="text-2xl font-bold text-gray-900">
              Create your account
            </h1>
            <p className="text-gray-500 text-sm mt-1">
              Free forever. No credit card needed.
            </p>
          </div>

          {error && (
            <div className="mb-5 p-3 bg-red-50 border border-red-200 text-red-600 text-sm rounded-xl stagger-1">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="stagger-2">
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Full name
              </label>
              <input
                type="text"
                name="full_name"
                value={form.full_name}
                onChange={handleChange}
                placeholder="Kunj Bihari"
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500 transition-all duration-200 shadow-sm"
              />
            </div>

            <div className="stagger-3">
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Email address
              </label>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                placeholder="you@example.com"
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500 transition-all duration-200 shadow-sm"
              />
            </div>

            <div className="stagger-4">
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Password
              </label>
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500 transition-all duration-200 shadow-sm"
              />
              <p className="text-xs text-gray-500 mt-1">
                Min 8 chars, 1 uppercase, 1 lowercase, 1 number
              </p>
            </div>

            <div className="stagger-4">
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Confirm password
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={form.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500 transition-all duration-200 shadow-sm"
              />
            </div>

            <div className="stagger-5 pt-1">
              <button
                type="submit"
                disabled={registerMutation.isPending}
                className="w-full py-3 rounded-xl text-sm font-semibold text-white transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40"
                style={{
                  background: "linear-gradient(135deg, #10b981, #059669)",
                }}
              >
                {registerMutation.isPending ? (
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
                    Creating account...
                  </span>
                ) : (
                  "Create account"
                )}
              </button>
            </div>
          </form>

          <div className="stagger-6 relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-xs text-gray-400 bg-gray-50 px-3">
              Already have an account?
            </div>
          </div>

          <div className="stagger-7">
            <Link
              to="/login"
              className="block w-full text-center py-3 rounded-xl text-sm font-semibold text-emerald-700 border-2 border-emerald-200 hover:bg-emerald-50 hover:border-emerald-300 transition-all duration-200"
            >
              Sign in instead
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
