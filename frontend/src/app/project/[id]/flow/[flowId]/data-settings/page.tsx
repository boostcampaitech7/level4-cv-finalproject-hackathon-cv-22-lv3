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

  if (loading) return <div>Loading...</div>

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-purple-100 to-purple-200">
      <div className="container mx-auto p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">데이터 설정</h1>
          <Button
            onClick={() => router.push(`/project/${projectId}/flow/${flowId}/attribute-settings`)}
            variant="outline"
          >
            속성 설정
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 min-h-[calc(100vh-12rem)]">
          <div className="md:col-span-1 h-full">
            {datasets.map((dataset) => (
              <DataSummary key={dataset.id} rowCount={1470} columnCount={columns.length} fileSize={dataset.size} />
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

