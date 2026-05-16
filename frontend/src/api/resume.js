import api from "./axios";

export const uploadResume = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/resume/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const getMyResume = () => api.get("/resume/me");
export const deleteResume = () => api.delete("/resume/me");
