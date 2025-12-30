/**
 * API client for backend communication.
 */

import axios from 'axios';
import type { GraphData, NodeDetails, CompanyInfo, FilingInfo, GraphStats } from '../types/graph';
import { apiLogger } from '../utils/logger';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    apiLogger.logRequest(config.method?.toUpperCase() || 'GET', config.url || '', config.params);
    return config;
  },
  (error) => {
    apiLogger.logError('REQUEST', error.config?.url || 'unknown', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for logging
api.interceptors.response.use(
  (response) => {
    apiLogger.logResponse(
      response.config.method?.toUpperCase() || 'GET',
      response.config.url || '',
      response.status,
      response.data
    );
    return response;
  },
  (error) => {
    if (error.response) {
      apiLogger.logResponse(
        error.config?.method?.toUpperCase() || 'GET',
        error.config?.url || '',
        error.response.status,
        error.response.data
      );
    } else {
      apiLogger.logError(error.config?.method?.toUpperCase() || 'GET', error.config?.url || 'unknown', error);
    }
    return Promise.reject(error);
  }
);

export const graphApi = {
  /**
   * Get graph data for a ticker
   */
  getGraph: async (ticker: string): Promise<GraphData> => {
    const response = await api.get<GraphData>(`/api/graph/${ticker}`);
    return response.data;
  },

  /**
   * Expand a node (filing or section)
   */
  expandNode: async (ticker: string, nodeId: string, nodeType: 'filing' | 'section'): Promise<GraphData> => {
    const response = await api.get<GraphData>(`/api/graph/${ticker}/expand/${nodeId}`, {
      params: { node_type: nodeType },
    });
    return response.data;
  },

  /**
   * Get node details
   */
  getNodeDetails: async (nodeId: string, labels: string[]): Promise<NodeDetails> => {
    const response = await api.get<NodeDetails>(`/api/graph/node/${nodeId}`, {
      params: { labels: labels.join(',') },
    });
    return response.data;
  },

  /**
   * Get node relationships
   */
  getNodeRelationships: async (nodeId: string, labels: string[]): Promise<{ incoming: any[]; outgoing: any[] }> => {
    const response = await api.get(`/api/graph/node/${nodeId}/relationships`, {
      params: { labels: labels.join(',') },
    });
    return response.data;
  },
};

export const tickerApi = {
  /**
   * Get company info
   */
  getCompanyInfo: async (ticker: string): Promise<CompanyInfo> => {
    const response = await api.get<CompanyInfo>(`/api/ticker/${ticker}/info`);
    return response.data;
  },

  /**
   * Get filings for a ticker
   */
  getFilings: async (ticker: string, formType?: string): Promise<FilingInfo[]> => {
    const response = await api.get<FilingInfo[]>(`/api/ticker/${ticker}/filings`, {
      params: formType ? { form_type: formType } : {},
    });
    return response.data;
  },

  /**
   * Get graph statistics
   */
  getStats: async (ticker: string): Promise<GraphStats> => {
    const response = await api.get<GraphStats>(`/api/ticker/${ticker}/stats`);
    return response.data;
  },
};

export default api;

