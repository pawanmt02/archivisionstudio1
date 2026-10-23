import axiosClient from './axiosClient';

export const projectApi = {
  list: () => axiosClient.get('/projects'),
  create: (data) => axiosClient.post('/projects', data),
  getById: (id) => axiosClient.get(`/projects/${id}`),
  update: (id, data) => axiosClient.put(`/projects/${id}`, data),
  delete: (id) => axiosClient.delete(`/projects/${id}`),
  getRenders: (projectId) => axiosClient.get(`/projects/${projectId}/renders`)
};
