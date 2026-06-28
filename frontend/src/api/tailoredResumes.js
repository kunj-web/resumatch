import api from "./axios";

export const createTailoredResume = (jobId) =>
  api.post(`/jobs/${jobId}/tailored-resumes`);

export const getTailoredResume = (id) => api.get(`/tailored-resumes/${id}`);

export const updateTailoredResume = (
  id,
  { editedContent, templateKey, outputFormat }
) =>
  api.patch(`/tailored-resumes/${id}`, {
    edited_content: editedContent,
    template_key: templateKey,
    output_format: outputFormat,
  });

export const finalizeTailoredResume = (id, { templateKey, outputFormat }) =>
  api.post(`/tailored-resumes/${id}/finalize`, {
    template_key: templateKey,
    output_format: outputFormat,
  });

export const downloadTailoredResume = (id) =>
  api.get(`/tailored-resumes/${id}/download`);
