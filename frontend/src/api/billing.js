import api from "./axios";

export const recordUpgradeInterest = () =>
  api.post("/billing/upgrade-interest");
