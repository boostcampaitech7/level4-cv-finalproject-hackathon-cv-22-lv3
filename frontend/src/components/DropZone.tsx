import type React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface DropZoneProps {
  title: string
  onDrop: (e: React.DragEvent) => void
  children: React.ReactNode
}

export const DropZone: React.FC<DropZoneProps> = ({ title, onDrop, children }) => {
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent onDrop={onDrop} onDragOver={handleDragOver} className="min-h-[200px]">
        {children}
      </CardContent>
    </Card>
  )
}

