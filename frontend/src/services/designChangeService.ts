import client from '../api/client';
import type { DesignChange, DesignChangeCreate, DesignChangeUpdate, WorkflowTransition } from '../types';

interface GetAllParams {
  skip: number;
  limit: number;
  project_id?: number;
}

export const designChangeService = {
  getAll: async (skip = 0, limit = 100, projectId?: number) => {
    const params: GetAllParams = { skip, limit };
    if (projectId) params.project_id = projectId;
    
    const response = await client.get<DesignChange[]>('/design_changes/', { params });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await client.get<DesignChange>(`/design_changes/${id}`);
    return response.data;
  },

  create: async (data: DesignChangeCreate) => {
    const response = await client.post<DesignChange>('/design_changes/', data);
    return response.data;
  },

  update: async (id: number, data: DesignChangeUpdate) => {
    const response = await client.put<DesignChange>(`/design_changes/${id}`, data);
    return response.data;
  },

  transition: async (id: number, transition: WorkflowTransition) => {
    const response = await client.post<DesignChange>(`/design_changes/${id}/transition`, transition);
    return response.data;
  },
};
