import type { CreateUserRequest, GetUsersResponse, LoginResponse, UpdateUserRequest, User } from "@/types/user"
import { getAuthHeader } from "./auth"
import type { CreateFlowBody, Flow, GetFlowsResponse, UpdateFlowBody } from "@/types/flow"
import type { CreateDatasetBody, Dataset, GetDatasetsResponse } from "@/types/dataset"
import { ApiError } from "@/types/api-error"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new ApiError(response.status, await response.text())
  }
  if (response.status === 204) {
    return {} as T
  }
  return response.json()
}

export const api = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const formData = new URLSearchParams()
    formData.append("username", email)
    formData.append("password", password)

    const response = await fetch(`${API_BASE_URL}/users/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    })

    return handleResponse<LoginResponse>(response)
  },

  async createUser(data: CreateUserRequest): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })

    return handleResponse<User>(response)
  },

  async updateUser(userId: string, data: UpdateUserRequest): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
    })

    return handleResponse<User>(response)
  },

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      headers: getAuthHeader(),
    })

    return handleResponse<User>(response)
  },

  async getUsers(page = 1, itemsPerPage = 10): Promise<GetUsersResponse> {
    const response = await fetch(`${API_BASE_URL}/users?page=${page}&items_per_page=${itemsPerPage}`, {
      headers: getAuthHeader(),
    })

    return handleResponse<GetUsersResponse>(response)
  },

  async deleteUser(): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/users`, {
      method: "DELETE",
      headers: getAuthHeader(),
    })

    return handleResponse<void>(response)
  },

  // New project-related API calls
  async createProject(data: { title: string; description: string }): Promise<ProjectResponse> {
    const response = await fetch(`${API_BASE_URL}/projects`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
    })

    return handleResponse<ProjectResponse>(response)
  },

  async getProjects(page = 1, itemsPerPage = 10): Promise<GetProjectsResponse> {
    const response = await fetch(`${API_BASE_URL}/projects?page=${page}&items_per_page=${itemsPerPage}`, {
      headers: getAuthHeader(),
    })

    return handleResponse<GetProjectsResponse>(response)
  },

  async getProject(id: string): Promise<ProjectResponse> {
    const response = await fetch(`${API_BASE_URL}/projects/${id}`, {
      headers: getAuthHeader(),
    })

    return handleResponse<ProjectResponse>(response)
  },

  async updateProject(id: string, data: { title?: string; description?: string }): Promise<ProjectResponse> {
    const response = await fetch(`${API_BASE_URL}/projects/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
    })

    return handleResponse<ProjectResponse>(response)
  },

  async deleteProject(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/projects/${id}`, {
      method: "DELETE",
      headers: getAuthHeader(),
    })

    return handleResponse<void>(response)
  },

  // Flow 관련 API 호출 함수 추가
  async createFlow(data: CreateFlowBody): Promise<Flow> {
    const response = await fetch(`${API_BASE_URL}/flows`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
    })

    return handleResponse<Flow>(response)
  },

  async getFlows(projectId: string, page = 1, itemsPerPage = 10): Promise<GetFlowsResponse> {
    const response = await fetch(
      `${API_BASE_URL}/flows?project_id=${projectId}&page=${page}&items_per_page=${itemsPerPage}`,
      {
        headers: getAuthHeader(),
      },
    )

    return handleResponse<GetFlowsResponse>(response)
  },

  async updateFlow(projectId: string, flowId: string, data: UpdateFlowBody): Promise<Flow> {
    const response = await fetch(`${API_BASE_URL}/flows/${flowId}?project_id=${projectId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
    })

    return handleResponse<Flow>(response)
  },

  async deleteFlow(projectId: string, flowId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/flows/${flowId}/${projectId}`, {
      method: "DELETE",
      headers: getAuthHeader(),
    })

    return handleResponse<void>(response)
  },

  // Dataset 관련 API 호출 함수 추가
  async createDataset(data: CreateDatasetBody): Promise<Dataset> {
    const response = await fetch(`${API_BASE_URL}/datasets`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
    })

    return handleResponse<Dataset>(response)
  },

  async getDatasetsByProject(projectId: string, page = 1, itemsPerPage = 10): Promise<GetDatasetsResponse> {
    const response = await fetch(
      `${API_BASE_URL}/datasets/project/${projectId}?page=${page}&items_per_page=${itemsPerPage}`,
      {
        headers: getAuthHeader(),
      },
    )

    return handleResponse<GetDatasetsResponse>(response)
  },

  async getDatasetsByFlow(flowId: string, page = 1, itemsPerPage = 10): Promise<GetDatasetsResponse> {
    const response = await fetch(
      `${API_BASE_URL}/datasets/flow/${flowId}?page=${page}&items_per_page=${itemsPerPage}`,
      {
        headers: getAuthHeader(),
      },
    )

    return handleResponse<GetDatasetsResponse>(response)
  },

  async updateDataset(id: string, flowId: string | null): Promise<Dataset> {
    const response = await fetch(`${API_BASE_URL}/datasets/${id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
      },
      body: JSON.stringify({ id, flow_id: flowId }),
    })

    return handleResponse<Dataset>(response)
  },

  async deleteDataset(projectId: string, datasetId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}/${projectId}`, {
      method: "DELETE",
      headers: getAuthHeader(),
    })

    return handleResponse<void>(response)
  },
  async createInform(datasetId: string): Promise<InformResponse> {
    const response = await fetch(`${API_BASE_URL}/informs/${datasetId}`, {
      method: "POST",
      headers: {
        ...getAuthHeader(),
      },
    })

    return handleResponse<InformResponse>(response)
  },
  async updateInform(informId: string, config_updates: any): Promise<InformResponse> {
    const response = await fetch(`${API_BASE_URL}/informs/${informId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
      },
      body: JSON.stringify(config_updates),
    })

    return handleResponse<InformResponse>(response)
  },
  async getInformByDataset(datasetId: string): Promise<InformResponse> {
    const response = await fetch(`${API_BASE_URL}/informs/dataset/${datasetId}`, {
      headers: getAuthHeader(),
    })

    return handleResponse<InformResponse>(response)
  },
}

// Add these types at the end of the file
export interface ProjectResponse {
  id: string
  user_id: string
  title: string
  description: string
  created_at: string
  updated_at: string
}

export interface GetProjectsResponse {
  total_count: number
  page: number
  projects: ProjectResponse[]
}

// InformResponse 인터페이스 추가
export interface InformResponse {
  id: string
  dataset_id: string
  model_inform_path: string
  user_inform_path: string
}

