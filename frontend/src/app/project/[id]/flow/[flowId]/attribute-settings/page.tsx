"use client"

import { useParams, useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { api } from "@/services/api"
import { DraggableCard } from "@/components/DraggableCard"
import { DropZone } from "@/components/DropZone"
import type React from "react"

interface Attribute {
  id: string
  name: string
  type: "numerical" | "categorical"
}

type VariableCategory = "all" | "environment" | "control" | "target"

export default function AttributeSettingsPage() {
  const params = useParams()
  const router = useRouter()
  const flowId = params.flowId as string
  const projectId = params.id as string
  const [attributes, setAttributes] = useState<Attribute[]>([])
  const [variableCategories, setVariableCategories] = useState<Record<VariableCategory, Attribute[]>>({
    all: [],
    environment: [],
    control: [],
    target: [],
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAttributes = async () => {
      try {
        const response = await api.getDatasetsByFlow(flowId)
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
              const columns = Object.keys(csvData[0])
              const newAttributes: Attribute[] = columns.map((column, index) => ({
                id: `attr-${index}`,
                name: column,
                type: typeof csvData[0][column] === "number" ? "numerical" : "categorical",
              }))
              setAttributes(newAttributes)
              setVariableCategories((prev) => ({ ...prev, all: newAttributes }))
            }
          }
        }
      } catch (error) {
        console.error("Failed to fetch attributes:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchAttributes()
  }, [flowId])

  const handleDragStart = (e: React.DragEvent, id: string, sourceCategory: VariableCategory) => {
    e.dataTransfer.setData("text/plain", JSON.stringify({ id, sourceCategory }))
  }

  const handleDrop = (e: React.DragEvent, targetCategory: VariableCategory) => {
    e.preventDefault()
    const { id, sourceCategory } = JSON.parse(e.dataTransfer.getData("text/plain")) as {
      id: string
      sourceCategory: VariableCategory
    }

    if (sourceCategory !== targetCategory) {
      setVariableCategories((prev) => {
        const attribute = prev[sourceCategory].find((attr) => attr.id === id)
        if (!attribute) return prev

        const newSourceCategory = prev[sourceCategory].filter((attr) => attr.id !== id)
        const newTargetCategory = [...prev[targetCategory], attribute]

        return {
          ...prev,
          [sourceCategory]: newSourceCategory,
          [targetCategory]: newTargetCategory,
        }
      })
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-purple-100 to-purple-200">
      <div className="container mx-auto p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">속성 설정</h1>
          <Button onClick={() => router.push(`/project/${projectId}/flow/${flowId}/data-settings`)} variant="outline">
            데이터 설정으로 돌아가기
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {(["all", "environment", "control", "target"] as const).map((category) => (
            <DropZone
              key={category}
              title={
                category === "all"
                  ? "전체 변수"
                  : category === "environment"
                    ? "환경 변수"
                    : category === "control"
                      ? "제어 변수"
                      : "타겟 변수"
              }
              onDrop={(e) => handleDrop(e, category)}
            >
              {variableCategories[category].map((attribute) => (
                <DraggableCard
                  key={attribute.id}
                  attribute={attribute}
                  onDragStart={(e) => handleDragStart(e, attribute.id, category)}
                />
              ))}
            </DropZone>
          ))}
        </div>
      </div>
    </div>
  )
}

