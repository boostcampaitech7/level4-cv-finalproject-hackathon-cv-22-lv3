"use client"

import { useParams, useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { DataVisualizer } from "@/components/DataVisualizer"
import { DataSummary } from "@/components/DataSummary"
import { api } from "@/services/api"
import type { Dataset } from "@/types/dataset"

export default function DataSettingsPage() {
  const params = useParams()
  const router = useRouter()
  const flowId = params.flowId as string
  const projectId = params.id as string
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [loading, setLoading] = useState(true)
  const [columns, setColumns] = useState<string[]>([])
  const [rowCount, setRowCount] = useState(0)
  // 제거
  // const [isCreatingInform, setIsCreatingInform] = useState(false)

  useEffect(() => {
    const fetchDatasets = async () => {
      try {
        const response = await api.getDatasetsByFlow(flowId)
        setDatasets(response.datasets)

        if (response.datasets.length > 0) {
          const csvResponse = await fetch("/api/parse-csv", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ filepath: response.datasets[0].path }),
          })

          if (csvResponse.ok) {
            const csvData = await csvResponse.json()
            if (csvData.length > 0) {
              setColumns(Object.keys(csvData[0]))
              setRowCount(csvData.length)
            }
          }
        }
      } catch (error) {
        console.error("Failed to fetch datasets:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchDatasets()
  }, [flowId])

  // handleCreateInform 함수 전체 제거
  // const handleCreateInform = async () => {
  //   if (datasets.length === 0) {
  //     toast.error("데이터셋이 없습니다.")
  //     return
  //   }

  //   setIsCreatingInform(true)
  //   try {
  //     const result = await api.createInform(datasets[0].id)
  //     toast.success("Inform이 성공적으로 생성되었습니다.")
  //     console.log("Created Inform:", result)
  //     // TODO: 생성된 Inform 정보를 활용하여 추가 작업 수행
  //   } catch (error) {
  //     console.error("Failed to create Inform:", error)
  //     toast.error("Inform 생성에 실패했습니다.")
  //   } finally {
  //     setIsCreatingInform(false)
  //   }
  // }

  if (loading) return <div>Loading...</div>

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-purple-100 to-purple-200">
      <div className="container mx-auto p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">데이터 설정</h1>
          <div className="space-x-4">
            {/* 다음 버튼을 제거 */}
            {/* <Button
              onClick={handleCreateInform}
              disabled={isCreatingInform}
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              {isCreatingInform ? "생성 중..." : "Inform 생성"}
            </Button> */}
            <Button
              onClick={() => router.push(`/project/${projectId}/flow/${flowId}/attribute-settings`)}
              variant="outline"
            >
              속성 설정
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 min-h-[calc(100vh-12rem)]">
          <div className="md:col-span-1 h-full">
            {datasets.map((dataset) => (
              <DataSummary key={dataset.id} rowCount={rowCount} columnCount={columns.length} fileSize={dataset.size} />
            ))}
          </div>

          <div className="md:col-span-4">
            <Card className="w-full h-full">
              <CardContent className="p-4 md:p-6">
                {datasets.length > 0 ? (
                  datasets.map((dataset) => (
                    <div key={dataset.id} className="space-y-4">
                      <div className="flex justify-between items-center">
                        <h2 className="text-xl font-semibold text-gray-700">{dataset.name}</h2>
                      </div>
                      <DataVisualizer dataset={dataset} />
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">No datasets available for this flow</div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

