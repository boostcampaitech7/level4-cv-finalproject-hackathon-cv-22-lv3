export interface Dataset {
    id: string
    project_id: string
    flow_id: string | null
    name: string
    size: number
    path: string
  }
  
  export interface CreateDatasetBody {
    project_id: string
    flow_id?: string | null
    name: string
    size: number
    path: string
  }
  
  export interface UpdateDatasetBody {
    id: string
    flow_id: string | null
  }
  
  export interface GetDatasetsResponse {
    total_count: number
    page: number
    datasets: Dataset[]
  }
  
  