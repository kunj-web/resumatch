import api from "./axios";

export const createCheckoutSession = () =>
  api.post("/billing/create-checkout-session");

export const recordUpgradeInterest = (source = "upgrade_modal") =>
  api.post("/billing/upgrade-interest", { source });
