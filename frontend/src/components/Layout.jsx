import { Link, useNavigate, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getMe } from "../api/auth";

export default function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const accessToken = localStorage.getItem("access_token");

  const { data: user } = useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const res = await getMe();
      return res.data;
    },
    enabled: Boolean(accessToken),
    retry: false,
  });

  const isPro = user?.plan === "pro";
  const creditLimit = user?.tailor_resume_credit_limit;
  const creditsRemaining = user?.tailor_resume_credits_remaining;
  const creditsUsed =
    typeof creditLimit === "number" && typeof creditsRemaining === "number"
      ? creditLimit - creditsRemaining
      : null;

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  const navItems = [
    {
      label: "Dashboard",
      path: "/",
      icon: (
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
          />
        </svg>
      ),
    },
    {
      label: "Add Job",
      path: "/jobs/new",
      icon: (
        <svg
          className="w-5 h-5"
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
      ),
    },
  ];

  return (
    <div className="min-h-screen flex" style={{ background: "#f8fafc" }}>
      {/* Sidebar */}
      <aside
        className="hidden lg:flex flex-col w-64 min-h-screen fixed left-0 top-0 z-20 border-r border-gray-200"
        style={{ background: "#0d1b2a" }}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-white/10">
          <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center shadow-lg shadow-emerald-500/30">
            <span className="text-white font-bold text-sm">R</span>
          </div>
          <span className="text-white font-bold text-lg">ResuMatch</span>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-4 py-6 space-y-1">
          {navItems.map((item) => {
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                  active
                    ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                    : "text-gray-400 hover:bg-white/5 hover:text-white"
                }`}
              >
                {item.icon}
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Bottom */}
        <div className="px-4 py-6 border-t border-white/10 space-y-3">
          {user && (
            <div className="rounded-xl border border-white/10 bg-white/[0.04] p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-normal text-gray-400">
                    {isPro ? "Pro plan" : "Free plan"}
                  </div>
                  <div className="mt-1 text-sm font-semibold text-white">
                    {isPro
                      ? "Unlimited tailoring"
                      : `${creditsRemaining ?? 0} / ${
                          creditLimit ?? 10
                        } resumes left`}
                  </div>
                </div>
                <span
                  className={`h-2.5 w-2.5 rounded-full ${
                    isPro ? "bg-emerald-400" : "bg-amber-400"
                  }`}
                />
              </div>
              {!isPro && typeof creditsUsed === "number" && (
                <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/10">
                  <div
                    className="h-full rounded-full bg-emerald-400"
                    style={{
                      width: `${Math.min(
                        Math.max((creditsUsed / (creditLimit || 10)) * 100, 0),
                        100
                      )}%`,
                    }}
                  />
                </div>
              )}
              {!isPro && (
                <button
                  type="button"
                  className="mt-3 w-full rounded-lg bg-white px-3 py-2 text-xs font-semibold text-gray-900 transition-all duration-200 hover:bg-emerald-50 active:scale-95"
                >
                  Upgrade
                </button>
              )}
            </div>
          )}

          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-gray-400 hover:bg-white/5 hover:text-red-400 transition-all duration-200 w-full"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              />
            </svg>
            Sign out
          </button>
        </div>
      </aside>

      {/* Mobile top navbar */}
      <div
        className="lg:hidden fixed top-0 left-0 right-0 z-20 flex items-center justify-between px-4 py-3 border-b border-white/10"
        style={{ background: "#0d1b2a" }}
      >
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-emerald-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xs">R</span>
          </div>
          <span className="text-white font-bold">ResuMatch</span>
        </div>
        <div className="flex items-center gap-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`p-2 rounded-lg transition-all duration-200 ${
                location.pathname === item.path
                  ? "bg-emerald-500/20 text-emerald-400"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {item.icon}
            </Link>
          ))}
          <button
            onClick={handleLogout}
            className="p-2 rounded-lg text-gray-400 hover:text-red-400 transition-all duration-200"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Main content */}
      <main className="flex-1 lg:ml-64 pt-16 lg:pt-0 min-w-0">
        <div className="p-6 lg:p-10 xl:p-12">{children}</div>
      </main>
    </div>
  );
}
