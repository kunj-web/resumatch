import api from "./axios";

export const createTailoredResume = (jobId) =>
  api.post(`/jobs/${jobId}/tailored-resumes`);
