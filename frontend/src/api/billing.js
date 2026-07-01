import api from "./axios";

export const recordUpgradeInterest = (source = "upgrade_modal") =>
  api.post("/billing/upgrade-interest", { source });
