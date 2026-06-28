import api from "./axios";

export const createTailoredResume = (jobId) =>
  api.post(`/jobs/${jobId}/tailored-resumes`);

export const getTailoredResume = (id) => api.get(`/tailored-resumes/${id}`);

export const updateTailoredResume = (id, editedContent) =>
  api.patch(`/tailored-resumes/${id}`, { edited_content: editedContent });
