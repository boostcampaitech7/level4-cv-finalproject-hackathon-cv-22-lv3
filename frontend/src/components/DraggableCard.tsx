import type React from "react"
import { Card } from "@/components/ui/card"
import { Hash, List } from "lucide-react"

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
    <Card
      draggable
      onDragStart={onDragStart}
      className="group cursor-move bg-white hover:bg-gray-50 transition-colors border border-gray-200"
    >
      <div className="px-3 py-2 flex items-center gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate" title={attribute.name}>
            {attribute.name}
          </p>
        </div>
        <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-gray-50 group-hover:bg-white">
          {attribute.type === "numerical" ? (
            <>
              <Hash className="w-3.5 h-3.5 text-blue-500 flex-shrink-0" />
              <span className="text-xs text-gray-600 font-medium">수치</span>
            </>
          ) : (
            <>
              <List className="w-3.5 h-3.5 text-green-500 flex-shrink-0" />
              <span className="text-xs text-gray-600 font-medium">범주</span>
            </>
          )}
        </div>
      </div>
    </Card>
  )
}

