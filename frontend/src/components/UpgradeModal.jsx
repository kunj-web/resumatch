import { useState } from "react";
import { recordUpgradeInterest } from "../api/billing";

export default function UpgradeModal({
  open,
  onClose,
  title = "Upgrade to Pro",
  message = "You have used your free tailored resumes for this month.",
  source = "upgrade_modal",
}) {
  const [status, setStatus] = useState("idle");
  const [feedback, setFeedback] = useState("");

  if (!open) return null;

  const handleClose = () => {
    setStatus("idle");
    setFeedback("");
    onClose();
  };

  const handleUpgradeInterest = async () => {
    setStatus("pending");
    setFeedback("");

    try {
      const res = await recordUpgradeInterest(source);
      setStatus("success");
      setFeedback(
        res.data?.message ||
          "You are on the Pro interest list. Checkout will be connected next."
      );
    } catch (err) {
      setStatus("error");
      setFeedback(
        err.response?.data?.detail ||
          "Could not record upgrade interest. Please try again."
      );
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <button
        type="button"
        aria-label="Close upgrade modal"
        className="absolute inset-0 bg-gray-950/45"
        onClick={handleClose}
      />

      <div className="relative w-full max-w-md rounded-2xl bg-white shadow-2xl shadow-gray-900/20 border border-gray-100 overflow-hidden">
        <div className="px-6 pt-6 pb-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-100">
                <svg
                  className="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <h2 className="mt-4 text-lg font-bold text-gray-900">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-gray-600">{message}</p>
            </div>

            <button
              type="button"
              onClick={handleClose}
              className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-colors duration-200"
              aria-label="Close"
            >
              <svg
                className="h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <div className="mt-5 rounded-xl border border-gray-100 bg-gray-50 p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-semibold text-gray-900">Pro</div>
                <div className="mt-1 text-xs text-gray-500">
                  Built for active job search
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-gray-900">Coming soon</div>
                <div className="text-xs text-gray-500">checkout pending</div>
              </div>
            </div>

            <div className="mt-4 space-y-2 text-sm text-gray-700">
              {[
                "More tailored resumes each month",
                "ATS Classic after the free monthly limit",
                "All resume templates",
                "PDF and DOCX export",
              ].map((item) => (
                <div key={item} className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>

          {feedback && (
            <div
              className={`mt-4 rounded-lg border px-3 py-2 text-xs ${
                status === "success"
                  ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                  : "border-red-200 bg-red-50 text-red-600"
              }`}
            >
              {feedback}
            </div>
          )}
        </div>

        <div className="flex flex-col-reverse gap-2 border-t border-gray-100 bg-gray-50 px-6 py-4 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={handleClose}
            className="rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-100 transition-colors duration-200"
          >
            Maybe later
          </button>
          <button
            type="button"
            onClick={handleUpgradeInterest}
            disabled={status === "pending" || status === "success"}
            className="rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm shadow-emerald-600/20 hover:bg-emerald-700 active:scale-95 transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {status === "pending"
              ? "Saving..."
              : status === "success"
              ? "Interest saved"
              : "Upgrade to Pro"}
          </button>
        </div>
      </div>
    </div>
  );
}
