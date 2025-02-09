"use client"

import { useState, useEffect, useRef, useCallback, type DragEvent } from "react"
import type { ChangeEvent } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/services/api"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, FileText, Trash2, Minus } from "lucide-react"
import { Sidebar } from "@/components/Sidebar"
import type { Flow } from "@/types/flow"
import type { Dataset } from "@/types/dataset"
import { useToastMessage } from "@/components/ui/use-toast"
import { ApiError } from "@/types/api-error"
import { toast } from "sonner"

interface ProjectPageProps {
  id: string
}

export function ProjectPage({ id }: ProjectPageProps) {
  const showToast = useToastMessage()
  const [project, setProject] = useState<any>(null)
  const [flows, setFlows] = useState<Flow[]>([])
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [selectedFlowDatasets, setSelectedFlowDatasets] = useState<Dataset[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [selectedFlowId, setSelectedFlowId] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()

  const fetchDatasets = useCallback(async () => {
    try {
      const response = await api.getDatasetsByProject(id)
      setDatasets(response.datasets)
    } catch (error) {
      console.error("Failed to fetch datasets:", error)
    }
  }, [id])

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const projectData = await api.getProject(id)
        setProject(projectData)
      } catch (error) {
        console.error("Failed to fetch project:", error)
        router.push("/workspace")
      }
    }

    const fetchFlows = async () => {
      try {
        const response = await api.getFlows(id)
        setFlows(response.flows)
        if (response.flows.length > 0) {
          setSelectedFlowId(response.flows[0].id)
        }
      } catch (error) {
        console.error("Failed to fetch flows:", error)
      }
    }

    fetchProject()
    fetchFlows()
    fetchDatasets()
  }, [id, router, fetchDatasets])

  useEffect(() => {
    setSelectedFlowDatasets(datasets.filter((dataset) => dataset.flow_id === selectedFlowId))
  }, [selectedFlowId, datasets])

  const handleFileSelect = async (event: ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files?.length) return

    setIsUploading(true)
    const files = Array.from(event.target.files)

    try {
      const uploadPromises = files.map(async (file) => {
        try {
          const formData = new FormData()
          formData.append("file", file)

          const uploadResponse = await fetch("/api/upload", {
            method: "POST",
            body: formData,
          })

          if (!uploadResponse.ok) {
            throw new Error("파일 업로드에 실패했습니다.")
          }

          const { path: localPath } = await uploadResponse.json()

          return api.createDataset({
            project_id: id,
            name: file.name,
            size: file.size,
            path: localPath, // 이미 전체 경로이므로 그대로 사용
          })
        } catch (error) {
          console.error("Error processing file:", file.name, error)
          throw error
        }
      })

      await Promise.all(uploadPromises)
      await fetchDatasets()

      showToast({
        title: "업로드 완료",
        description: "파일이 성공적으로 업로드되었습니다.",
      })
    } catch (error) {
      console.error("Failed to upload files:", error)
      showToast({
        title: "업로드 실패",
        description: "파일 업로드 중 오류가 발생했습니다.",
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
      if (event.target) {
        event.target.value = ""
      }
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleDeleteDataset = async (datasetId: string) => {
    try {
      const dataset = datasets.find((d) => d.id === datasetId)
      if (dataset) {
        const deleteResponse = await fetch(`/api/upload?path=${encodeURIComponent(dataset.path)}`, {
          method: "DELETE",
        })

        if (!deleteResponse.ok) {
          throw new Error("파일 삭제에 실패했습니다.")
        }

        await api.deleteDataset(id, datasetId)
        await fetchDatasets()
        showToast({
          title: "삭제 완료",
          description: "데이터셋이 삭제되었습니다.",
        })
      }
    } catch (error) {
      console.error("Failed to delete dataset:", error)
      showToast({
        title: "삭제 실패",
        description: "데이터셋 삭제 중 오류가 발생했습니다.",
        variant: "destructive",
      })
    }
  }

  const onDragStart = (e: DragEvent<HTMLDivElement>, dataset: Dataset) => {
    e.dataTransfer.setData("application/json", JSON.stringify(dataset))
  }

  const onDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
  }

  const onDrop = async (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    if (!selectedFlowId) {
      showToast({
        title: "오류",
        description: "플로우를 선택해주세요.",
        variant: "destructive",
      })
      return
    }
    try {
      const dataset = JSON.parse(e.dataTransfer.getData("application/json")) as Dataset
      await api.updateDataset(dataset.id, selectedFlowId)
      await fetchDatasets()
      showToast({
        title: "데이터셋 업데이트",
        description: "데이터셋이 선택한 플로우로 이동되었습니다.",
      })
    } catch (error) {
      console.error("Failed to update dataset:", error)
      showToast({
        title: "업데이트 실패",
        description: "데이터셋 업데이트 중 오류가 발생했습니다.",
        variant: "destructive",
      })
    }
  }

  const handleRemoveFromFlow = async (datasetId: string) => {
    try {
      await api.updateDataset(datasetId, null)
      await fetchDatasets()
      showToast({
        title: "데이터셋 업데이트",
        description: "데이터셋이 플로우에서 제거되었습니다.",
      })
    } catch (error) {
      console.error("Failed to remove dataset from flow:", error)
      if (error instanceof ApiError && error.status === 405) {
        showToast({
          title: "업데이트 실패",
          description: "서버에서 이 작업을 지원하지 않습니다. 관리자에게 문의하세요.",
          variant: "destructive",
        })
      } else {
        showToast({
          title: "업데이트 실패",
          description: "데이터셋 제거 중 오류가 발생했습니다.",
          variant: "destructive",
        })
      }
    }
  }

  const handleFlowCreate = async () => {
    try {
      const response = await api.getFlows(id)
      setFlows(response.flows)
    } catch (error) {
      console.error("Failed to fetch flows after creation:", error)
    }
  }

  const handleFlowDelete = async (flowId: string) => {
    try {
      await api.deleteFlow(id, flowId)
      setFlows(flows.filter((flow) => flow.id !== flowId))
      if (selectedFlowId === flowId) {
        setSelectedFlowId(flows[0]?.id || null)
      }
    } catch (error) {
      console.error("Failed to delete flow:", error)
    }
  }

  const handleCreateInform = async (datasetId: string) => {
    try {
      await api.createInform(datasetId)
      return true
    } catch (error) {
      console.error("Failed to create Inform:", error)
      toast.error("Inform 생성에 실패했습니다.")
      return false
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  if (!project) {
    return <div>Loading...</div>
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-purple-50 via-purple-100 to-purple-200">
      <Sidebar
        projectId={id}
        projectTitle={project.title}
        flows={flows}
        onFlowCreate={handleFlowCreate}
        onFlowDelete={handleFlowDelete}
        selectedFlowId={selectedFlowId}
        onFlowSelect={setSelectedFlowId}
      />
      <div className="flex-1 p-8 overflow-auto">
        <div className="flex flex-col md:flex-row gap-6">
          <Card className="flex-1 border-2 border-gray-200 shadow-lg">
            <CardContent className="p-6">
              <h2 className="text-xl font-semibold mb-6">파일 업로드</h2>
              <div className="space-y-4">
                <input type="file" ref={fileInputRef} onChange={handleFileSelect} className="hidden" multiple />
                <div
                  onClick={handleUploadClick}
                  className={`border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors ${
                    isUploading ? "opacity-50 cursor-not-allowed" : ""
                  }`}
                >
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-sm text-gray-600">
                    {isUploading ? "업로드 중..." : "클릭하여 파일을 선택하거나 파일을 드래그하세요"}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">여러 파일 선택 가능</p>
                </div>
                {datasets.length > 0 && (
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-gray-700 mb-2">데이터셋 목록 ({datasets.length})</div>
                    {datasets.map((dataset) => (
                      <div
                        key={dataset.id}
                        className={`flex items-center justify-between p-3 bg-white rounded-md shadow-sm border ${
                          dataset.flow_id === selectedFlowId ? "border-blue-500" : "border-gray-100"
                        } hover:border-blue-200 transition-colors`}
                        draggable
                        onDragStart={(e) => onDragStart(e, dataset)}
                      >
                        <div className="flex items-center space-x-3">
                          <FileText className="h-4 w-4 text-gray-500" />
                          <div>
                            <div className="text-sm font-medium text-gray-700">{dataset.name}</div>
                            <div className="text-xs text-gray-500">{formatFileSize(dataset.size)}</div>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteDataset(dataset.id)}
                          className="text-red-500 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
          <Card className="flex-1 border-2 border-gray-200 shadow-lg" onDragOver={onDragOver} onDrop={onDrop}>
            <CardContent className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">
                  파일 선택 (현재 플로우: {flows.find((f) => f.id === selectedFlowId)?.title || "없음"})
                </h2>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={selectedFlowDatasets.length === 0}
                  className="bg-blue-50 text-blue-600 hover:bg-blue-100 disabled:opacity-50"
                  onClick={async () => {
                    if (selectedFlowId) {
                      if (selectedFlowDatasets.length === 0) {
                        toast.error("데이터셋이 없습니다.")
                        return
                      }
                      toast.loading("데이터 설정 중...")
                      const success = await handleCreateInform(selectedFlowDatasets[0].id)
                      toast.dismiss()
                      if (success) {
                        router.push(`/project/${id}/flow/${selectedFlowId}/data-settings`)
                      }
                    } else {
                      toast.error("플로우를 선택해주세요.")
                    }
                  }}
                >
                  데이터 설정
                </Button>
              </div>
              <div className="space-y-2 min-h-[200px] border-2 border-dashed border-gray-300 rounded-lg p-4">
                {selectedFlowDatasets.length === 0 ? (
                  <p className="text-center text-gray-500 mt-8">파일을 이 영역으로 드래그하세요</p>
                ) : (
                  selectedFlowDatasets.map((dataset) => (
                    <div
                      key={dataset.id}
                      className="flex items-center justify-between space-x-2 p-3 bg-white rounded-md border border-gray-100"
                    >
                      <div className="flex items-center space-x-2">
                        <FileText className="h-4 w-4 text-gray-500" />
                        <span className="text-gray-700">{dataset.name}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveFromFlow(dataset.id)}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                      >
                        <Minus className="h-4 w-4" />
                      </Button>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

