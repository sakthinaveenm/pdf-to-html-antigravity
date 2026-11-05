import axios from 'axios';
import { Job, DocumentMeta, Highlight, QualityReport, SystemCapabilities } from '../types';

const API_BASE = '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE,
});

export const api = {
  // System
  getHealth: async () => (await apiClient.get('/health')).data,
  getCapabilities: async (): Promise<SystemCapabilities> => (await apiClient.get('/capabilities')).data,

  // Jobs
  uploadJobs: async (
    files: File[],
    converter: string,
    ocrLanguages: string,
    forceOcr: boolean
  ): Promise<{ jobs: Job[] }> => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    formData.append('converter', converter);
    formData.append('ocr_languages', ocrLanguages);
    formData.append('force_ocr', String(forceOcr));

    return (await apiClient.post('/jobs', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })).data;
  },

  listJobs: async (page = 1, limit = 20, status?: string): Promise<{ total: number; items: Job[] }> => {
    const params: Record<string, unknown> = { page, limit };
    if (status) params.status = status;
    return (await apiClient.get('/jobs', { params })).data;
  },

  getJob: async (jobId: string): Promise<Job> => (await apiClient.get(`/jobs/${jobId}`)).data,
  cancelJob: async (jobId: string) => (await apiClient.post(`/jobs/${jobId}/cancel`)).data,
  retryJob: async (jobId: string) => (await apiClient.post(`/jobs/${jobId}/retry`)).data,

  // Documents
  getDocument: async (documentId: string): Promise<DocumentMeta> =>
    (await apiClient.get(`/documents/${documentId}`)).data,

  getDocumentHtml: async (documentId: string): Promise<string> =>
    (await apiClient.get(`/documents/${documentId}/html`)).data,

  getDocumentAst: async (documentId: string) =>
    (await apiClient.get(`/documents/${documentId}/ast`)).data,

  getDocumentQuality: async (documentId: string): Promise<QualityReport> =>
    (await apiClient.get(`/documents/${documentId}/quality`)).data,

  saveRevision: async (documentId: string, html: string, changeSummary = 'Edited in HTML editor') =>
    (await apiClient.put(`/documents/${documentId}/revisions`, { html, changeSummary })).data,

  // Highlights
  listHighlights: async (documentId: string): Promise<Highlight[]> =>
    (await apiClient.get(`/documents/${documentId}/highlights`)).data,

  createHighlight: async (documentId: string, data: Omit<Highlight, 'id' | 'documentId' | 'revision' | 'createdAt' | 'updatedAt' | 'resolved'>): Promise<Highlight> =>
    (await apiClient.post(`/documents/${documentId}/highlights`, data)).data,

  updateHighlight: async (documentId: string, highlightId: string, data: Partial<Highlight>): Promise<Highlight> =>
    (await apiClient.patch(`/documents/${documentId}/highlights/${highlightId}`, data)).data,

  deleteHighlight: async (documentId: string, highlightId: string) =>
    (await apiClient.delete(`/documents/${documentId}/highlights/${highlightId}`)).data,

  // Export URLs
  getExportZipUrl: (documentId: string) => `${API_BASE}/documents/${documentId}/export`,
  getOriginalPdfUrl: (documentId: string) => `${API_BASE}/documents/${documentId}/pdf`,
};
