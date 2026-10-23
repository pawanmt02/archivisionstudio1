import axiosClient from './axiosClient';

export const renderApi = {
  generate: (data) => axiosClient.post('/synthesis/generate', data),
  getTunnelStatus: () => axiosClient.get('/synthesis/tunnel-status'),
  updateTunnelUrl: (url) => axiosClient.post('/synthesis/tunnel-config', { colab_url: url }),
};
