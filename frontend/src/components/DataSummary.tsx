import { Database, Columns, HardDrive } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface DataSummaryProps {
  rowCount: number
  columnCount: number
  fileSize: number
}

export function DataSummary({ rowCount, columnCount, fileSize }: DataSummaryProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
  }

  return (
    <Card className="w-full h-full">
      <CardContent className="p-4 md:p-5 sticky top-0">
        <h3 className="text-lg font-semibold mb-4">데이터 정보</h3>
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
              <Database className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">전체 행</p>
              <p className="text-lg font-semibold">{rowCount.toLocaleString()}행</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
              <Columns className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">속성</p>
              <p className="text-lg font-semibold">{columnCount.toLocaleString()}개</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
              <HardDrive className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">파일 크기</p>
              <p className="text-lg font-semibold">{formatFileSize(fileSize)}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

