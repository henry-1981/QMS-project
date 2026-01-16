export interface DesignChange {
  id: number;
  change_number: string;
  project_id: number;
  title: string;
  description: string;
  change_type: string;
  justification?: string;
  figma_link?: string;
  gdocs_link?: string;
  workflow_status: string;
  current_assignee?: number;
  created_by: number;
  created_at: string;
  updated_at?: string;
}

export interface DesignChangeCreate {
  project_id: number;
  title: string;
  description: string;
  change_type: string;
  justification?: string;
  figma_link?: string;
  gdocs_link?: string;
}

export interface DesignChangeUpdate {
  title?: string;
  description?: string;
  change_type?: string;
  justification?: string;
  figma_link?: string;
  gdocs_link?: string;
}

export interface WorkflowTransition {
  action: 'submit_for_ra' | 'ra_approve' | 'submit_for_qa' | 'qa_approve' | 'approve' | 'reject';
  comments?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}
