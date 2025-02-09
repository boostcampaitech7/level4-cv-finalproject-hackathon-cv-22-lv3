export interface User {
    id: string
    name: string
    email: string
    created_at: string
    updated_at: string
  }
  
  export interface CreateUserRequest {
    name: string
    email: string
    password: string
  }
  
  export interface UpdateUserRequest {
    name?: string
    password?: string
  }
  
  export interface LoginResponse {
    access_token: string
    token_type: string
  }
  
  export interface GetUsersResponse {
    total_count: number
    page: number
    users: User[]
  }
  
  