export interface Flow {
    id: string
    project_id: string
    title: string
    description: string
    created_at: string
    updated_at: string
  }
  
  export interface CreateFlowBody {
    project_id: string
    title: string
    description: string
  }
  
  export interface UpdateFlowBody {
    title?: string
    description?: string
  }
  
  export interface GetFlowsResponse {
    total_count: number
    page: number
    flows: Flow[]
  }
  
  