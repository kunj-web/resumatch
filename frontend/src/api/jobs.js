import api from "./axios";

export const createJob = (data) => api.post("/jobs/", data);
export const getJobs = () => api.get("/jobs/");
export const getJob = (id) => api.get(`/jobs/${id}`);
export const updateJobStatus = (id, status) =>
  api.patch(`/jobs/${id}/status`, { status });
export const updateJobNotes = (id, notes) =>
  api.patch(`/jobs/${id}/notes`, { notes });
export const deleteJob = (id) => api.delete(`/jobs/${id}`);
