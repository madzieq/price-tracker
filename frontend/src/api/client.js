import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL + "/api/v1",
  headers: { "Content-Type": "application/json" },
});

export const productsApi = {
  list: () => api.get("/products/").then((r) => r.data),
  get: (id) => api.get(`/products/${id}`).then((r) => r.data),
  create: (data) => api.post("/products/", data).then((r) => r.data),
  delete: (id) => api.delete(`/products/${id}`),
  getForecast: (id, days = 7) =>
    api.get(`/products/${id}/forecast?days=${days}`).then((r) => r.data),
  addAlert: (id, data) =>
    api.post(`/products/${id}/alerts`, data).then((r) => r.data),
};

export default api;
