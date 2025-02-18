"use client"

import { useParams } from "next/navigation"
import { Card, CardContent } from "@/components/ui/card"

export default function AnalysisResultPage() {
  const params = useParams()

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-purple-100 to-purple-200">
      <div className="container mx-auto py-6 px-4">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">분석 결과</h1>
        <Card>
          <CardContent className="p-6">
            <p className="text-lg text-gray-700">분석이 완료되었습니다.</p>
            {/* 여기에 추가적인 분석 결과를 표시할 수 있습니다 */}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

