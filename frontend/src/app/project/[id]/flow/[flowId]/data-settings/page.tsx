"use client"

import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export default function DataSettingsPage() {
  const params = useParams()
  const router = useRouter()
  const flowId = params.flowId as string
  const projectId = params.id as string

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-purple-100 to-purple-200">
      <div className="container mx-auto p-8">
        <Card className="w-full max-w-4xl mx-auto">
          <CardContent className="p-6">
            <h1 className="text-3xl font-bold mb-6 text-gray-800">데이터 설정</h1>
            <p className="mb-6 text-lg text-gray-600">현재 플로우 ID: {flowId}</p>
            <div className="space-y-4">
              {/* 여기에 데이터 설정 관련 컴포넌트들을 추가할 수 있습니다 */}
              <div className="bg-white p-4 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-2 text-gray-700">데이터 소스</h2>
                <p className="text-gray-600">현재 선택된 데이터 소스가 여기에 표시됩니다.</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-2 text-gray-700">데이터 전처리</h2>
                <p className="text-gray-600">데이터 전처리 옵션을 여기에서 설정할 수 있습니다.</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-2 text-gray-700">특성 선택</h2>
                <p className="text-gray-600">분석에 사용할 특성을 여기에서 선택할 수 있습니다.</p>
              </div>
            </div>
            <div className="mt-8 flex justify-between">
              <Button onClick={() => router.push(`/project/${projectId}`)} variant="outline">
                프로젝트로 돌아가기
              </Button>
              <Button>설정 저장</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

