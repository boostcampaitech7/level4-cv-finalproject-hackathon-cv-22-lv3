import type React from "react"
import { Card, CardContent } from "@/components/ui/card"

interface Attribute {
  id: string
  name: string
  type: "numerical" | "categorical"
}

interface DraggableCardProps {
  attribute: Attribute
  onDragStart: (e: React.DragEvent) => void
}

export const DraggableCard: React.FC<DraggableCardProps> = ({ attribute, onDragStart }) => {
  return (
    <Card draggable onDragStart={onDragStart} className="mb-2 cursor-move bg-white">
      <CardContent className="p-2">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium truncate" title={attribute.name}>
            {attribute.name}
          </span>
          <span className="text-xs text-gray-500">{attribute.type === "numerical" ? "수치" : "범주"}</span>
        </div>
      </CardContent>
    </Card>
  )
}

