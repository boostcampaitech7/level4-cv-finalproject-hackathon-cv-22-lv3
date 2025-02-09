"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/services/api"
import type { User } from "@/types/user"
import { getToken } from "@/services/auth"
import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Plus, Lock, Star, Minus, Pencil } from "lucide-react"
import { CreateProjectDialog } from "@/components/CreateProjectDialog"
import { EditProjectDialog } from "@/components/EditProjectDialog"
import { toast } from "sonner"

interface ProjectCard {
  id: string
  title: string
  description: string
  isLocked: boolean
  isStarred: boolean
  starredAt: number | null
}

interface EditingProject {
  id: string
  title: string
  description: string
}

export default function Workspace() {
  const [user, setUser] = useState<User | null>(null)
  const [projects, setProjects] = useState<ProjectCard[]>([])
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [editingProject, setEditingProject] = useState<EditingProject | null>(null)
  const router = useRouter()

  const PROJECT_LIMIT = 5

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await api.getCurrentUser()
        setUser(userData)
      } catch (error) {
        console.error("Failed to fetch user data:", error)
        router.push("/login")
      }
    }

    const fetchProjects = async () => {
      try {
        const response = await api.getProjects()
        setProjects(
          response.projects.map((project) => ({
            ...project,
            isLocked: false,
            isStarred: false,
            starredAt: null,
          })),
        )
      } catch (error) {
        console.error("Failed to fetch projects:", error)
      }
    }

    if (!getToken()) {
      router.push("/login")
    } else {
      fetchUser()
      fetchProjects()
    }
  }, [router])

  const handleCreateProject = async (title: string, description: string) => {
    if (projects.length >= PROJECT_LIMIT) {
      toast.error("프로젝트 생성 실패", {
        description: "더 이상 생성할 수 없습니다.",
      })
      return
    }

    try {
      const newProject = await api.createProject({ title, description })
      setProjects((prevProjects) => [
        ...prevProjects,
        { ...newProject, isLocked: false, isStarred: false, starredAt: null },
      ])
      setIsCreateDialogOpen(false)
    } catch (error) {
      console.error("Failed to create project:", error)
    }
  }

  const handleEditProject = async (title: string, description: string) => {
    if (!editingProject) return

    try {
      const updatedProject = await api.updateProject(editingProject.id, { title, description })
      setProjects(
        projects.map((p) =>
          p.id === editingProject.id
            ? { ...p, title: updatedProject.title, description: updatedProject.description }
            : p,
        ),
      )
      setEditingProject(null)
    } catch (error) {
      console.error("Failed to update project:", error)
    }
  }

  const handleToggleStar = (projectId: string) => {
    setProjects((prevProjects) => {
      const updatedProjects = prevProjects.map((project) => {
        if (project.id === projectId) {
          return {
            ...project,
            isStarred: !project.isStarred,
            starredAt: project.isStarred ? null : Date.now(),
          }
        }
        return project
      })

      // Sort projects: starred first (most recently starred at the top), then non-starred
      return updatedProjects.sort((a, b) => {
        if (a.isStarred && b.isStarred) {
          return (b.starredAt || 0) - (a.starredAt || 0)
        }
        if (a.isStarred) return -1
        if (b.isStarred) return 1
        return 0
      })
    })
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-purple-50 via-purple-100 to-purple-200">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PGNsaXBQYXRoIGlkPSJhIj48cGF0aCBmaWxsPSJub25lIiBkPSJNMCAwaDYwdjYwSDB6Ii8+PC9jbGlwUGF0aD48L2RlZnM+PGcgY2xpcC1wYXRoPSJ1cmwoI2EpIj48cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiNlMmU4ZjAiIHN0cm9rZS13aWR0aD0iLjUiIGQ9Ik0tMTAgMzBoODBNMzAtMTB2ODAiLz48L2c+PC9zdmc+')] opacity-30"></div>

      <div className="relative z-10 p-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Card className="group overflow-hidden relative hover:shadow-lg transition-all duration-500 bg-white rounded-2xl">
            <div className="absolute inset-x-0 top-0 h-1 bg-emerald-500"></div>
            <CardContent className="relative p-6 z-10">
              <h3 className="text-lg font-medium mb-4 text-emerald-700">데이터 사용량</h3>
              <div className="flex items-end justify-between mb-2">
                <span className="text-4xl font-bold text-emerald-900">0/1</span>
                <span className="text-sm text-emerald-600">GB</span>
              </div>
              <p className="text-sm text-emerald-600 mb-3">사용 가능한 데이터 1GB</p>
              <Progress value={0} className="h-1.5" variant="emerald" />
            </CardContent>
          </Card>

          <Card className="group overflow-hidden relative hover:shadow-lg transition-all duration-500 bg-white rounded-2xl">
            <div className="absolute inset-x-0 top-0 h-1 bg-blue-500"></div>
            <CardContent className="relative p-6 z-10">
              <h3 className="text-lg font-medium mb-4 text-blue-700">현재 프로젝트 수</h3>
              <div className="flex items-end justify-between mb-2">
                <span className="text-4xl font-bold text-blue-900">
                  {projects.length}/{PROJECT_LIMIT}
                </span>
                <span className="text-sm text-blue-600">개</span>
              </div>
              <p className="text-sm text-blue-600 mb-3">
                사용 가능한 프로젝트 {Math.max(0, PROJECT_LIMIT - projects.length)}개
              </p>
              <Progress value={(projects.length / PROJECT_LIMIT) * 100} className="h-1.5" variant="blue" />
            </CardContent>
          </Card>

          <Card className="group overflow-hidden relative hover:shadow-lg transition-all duration-500 bg-white rounded-2xl">
            <div className="absolute inset-x-0 top-0 h-1 bg-purple-500"></div>
            <CardContent className="relative p-6 z-10">
              <h3 className="text-lg font-medium mb-4 text-purple-700">생성한 직접 지시서 수</h3>
              <div className="flex items-end justify-between mb-2">
                <span className="text-4xl font-bold text-purple-900">1/20</span>
                <span className="text-sm text-purple-600">개</span>
              </div>
              <p className="text-sm text-purple-600 mb-3">생성 가능한 직접 지시서 19개</p>
              <Progress value={5} className="h-1.5" variant="purple" />
            </CardContent>
          </Card>
        </div>

        <div className="relative mb-20">
          <h2 className="text-xl font-semibold mb-6 text-gray-900">프로젝트 목록</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card
              className="group relative hover:shadow-lg transition-all duration-500 cursor-pointer overflow-hidden bg-white border-2 border-dashed border-gray-200 hover:border-blue-400 rounded-2xl hover:bg-blue-50/50"
              onClick={() => {
                if (projects.length >= PROJECT_LIMIT) {
                  toast.error("프로젝트 생성 실패", {
                    description: "더 이상 생성할 수 없습니다.",
                  })
                } else {
                  setIsCreateDialogOpen(true)
                }
              }}
            >
              <CardContent className="relative h-[200px] flex items-center justify-center">
                <div className="text-center group-hover:scale-105 transition-transform duration-300">
                  <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-4 group-hover:bg-blue-200 transition-colors">
                    <Plus className="h-8 w-8 text-blue-600 group-hover:text-blue-700 transition-colors" />
                  </div>
                  <p className="text-sm font-medium text-gray-500 group-hover:text-blue-500 transition-colors">
                    새로운 프로젝트 생성
                  </p>
                  <p className="text-xs text-gray-400 mt-1 group-hover:text-blue-400 transition-colors">
                    클릭하여 시작하기
                  </p>
                </div>
              </CardContent>
            </Card>

            {projects.map((project) => (
              <Card
                key={project.id}
                className="group relative hover:shadow-lg transition-all duration-500 overflow-hidden bg-white rounded-2xl cursor-pointer"
                onClick={() => router.push(`/project/${project.id}`)}
              >
                <div className="absolute inset-x-0 top-0 h-1 bg-blue-500"></div>
                <CardContent className="relative p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">{project.title}</h3>
                    <div className="flex items-center space-x-2">
                      {project.isLocked && (
                        <Lock className="h-5 w-5 text-gray-400 hover:text-gray-600 transition-colors" />
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleToggleStar(project.id)
                        }}
                        className="p-1 hover:bg-yellow-100 rounded-full transition-colors"
                      >
                        <Star
                          className={`h-5 w-5 ${
                            project.isStarred
                              ? "text-yellow-400 hover:text-yellow-500"
                              : "text-gray-400 hover:text-gray-600"
                          } transition-colors cursor-pointer`}
                        />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setEditingProject({
                            id: project.id,
                            title: project.title,
                            description: project.description,
                          })
                        }}
                        className="p-1 hover:bg-blue-100 rounded-full transition-colors"
                      >
                        <Pencil className="h-5 w-5 text-blue-500 hover:text-blue-600 transition-colors" />
                      </button>
                      <button
                        onClick={async (e) => {
                          e.stopPropagation()
                          if (window.confirm("이 프로젝트를 삭제하시겠습니까?")) {
                            try {
                              await api.deleteProject(project.id)
                              setProjects(projects.filter((p) => p.id !== project.id))
                            } catch (error) {
                              console.error("Failed to delete project:", error)
                            }
                          }
                        }}
                        className="p-1 hover:bg-red-100 rounded-full transition-colors"
                      >
                        <Minus className="h-5 w-5 text-red-500 hover:text-red-600 transition-colors" />
                      </button>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">{project.description}</p>
                  <div className="h-24 bg-slate-50 rounded-lg border border-slate-200"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        <div className="fixed bottom-0 left-0 right-0 pointer-events-none">
          <div className="relative h-64">
            <div className="absolute inset-0 bg-gradient-to-t from-white/80 to-transparent"></div>
            <div className="absolute bottom-0 left-0 right-0">
              <svg className="w-full h-auto" viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M0 60L48 65C96 70 192 80 288 75C384 70 480 50 576 45C672 40 768 50 864 55C960 60 1056 60 1152 55C1248 50 1344 40 1392 35L1440 30V120H1392C1344 120 1248 120 1152 120C1056 120 960 120 864 120C768 120 672 120 576 120C480 120 384 120 288 120C192 120 96 120 48 120H0V60Z"
                  fill="url(#gradient)"
                  fillOpacity="0.1"
                />
                <defs>
                  <linearGradient id="gradient" x1="720" y1="0" x2="720" y2="120" gradientUnits="userSpaceOnUse">
                    <stop stopColor="#3B82F6" />
                    <stop offset="1" stopColor="#6366F1" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMTAiIGN5PSIxMCIgcj0iMSIgZmlsbD0iIzMzMzMzMyIgZmlsbC1vcGFjaXR5PSIwLjEiLz48L3N2Zz4=')] opacity-30"></div>
          </div>
        </div>
      </div>
      <CreateProjectDialog
        isOpen={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
        onCreateProject={handleCreateProject}
      />
      {editingProject && (
        <EditProjectDialog
          isOpen={!!editingProject}
          onClose={() => setEditingProject(null)}
          onEditProject={handleEditProject}
          initialTitle={editingProject.title}
          initialDescription={editingProject.description}
        />
      )}
    </div>
  )
}

