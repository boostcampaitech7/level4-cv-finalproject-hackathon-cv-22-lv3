import type React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"

interface DropZoneProps {
  title: string
  onDrop: (e: React.DragEvent) => void
  children: React.ReactNode
  count: number
  maxItems?: number // 새로운 prop 추가
}

export const DropZone: React.FC<DropZoneProps> = ({ title, onDrop, children, count, maxItems }) => {
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    if (maxItems && count >= maxItems) {
      // 최대 아이템 수에 도달했을 때 드롭을 막습니다
      return
    }
    onDrop(e)
  }

  return (
    <Card className="flex flex-col h-[calc(100vh-180px)]">
      <CardHeader className="flex-shrink-0 pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">{title}</CardTitle>
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
            {count}
          </span>
        </div>
      </CardHeader>
      <CardContent className="flex-1 p-3 overflow-hidden" onDrop={handleDrop} onDragOver={handleDragOver}>
        <ScrollArea className="h-full pr-4">
          <div className="space-y-2">{children}</div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}

