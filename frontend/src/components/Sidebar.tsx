"use client"

import { useState } from "react"
import { Plus, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import type { Flow } from "@/types/flow"
import { api } from "@/services/api"

interface SidebarProps {
  projectId: string
  projectTitle: string
  flows: Flow[]
  onFlowCreate: () => void
  onFlowDelete: (flowId: string) => void
  selectedFlowId: string | null
  onFlowSelect: (flowId: string) => void
}

export function Sidebar({
  projectId,
  projectTitle,
  flows,
  onFlowCreate,
  onFlowDelete,
  selectedFlowId,
  onFlowSelect,
}: SidebarProps) {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [newFlowTitle, setNewFlowTitle] = useState("")
  const [newFlowDescription, setNewFlowDescription] = useState("")

  const handleCreateFlow = async () => {
    try {
      await api.createFlow({
        project_id: projectId,
        title: newFlowTitle,
        description: newFlowDescription,
      })
      setIsCreateDialogOpen(false)
      setNewFlowTitle("")
      setNewFlowDescription("")
      onFlowCreate()
    } catch (error) {
      console.error("Failed to create flow:", error)
    }
  }

  return (
    <div className="w-64 bg-green-50 h-full shadow-lg p-4">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">{projectTitle}</h2>
      <div className="space-y-2">
        <Button onClick={() => setIsCreateDialogOpen(true)} className="w-full">
          <Plus className="mr-2 h-4 w-4" /> 새 플로우 생성
        </Button>
        {flows.map((flow) => (
          <div
            key={flow.id}
            className={`flex items-center justify-between p-2 rounded-md cursor-pointer ${
              selectedFlowId === flow.id ? "bg-blue-100 text-blue-700" : "bg-white text-gray-700 hover:bg-gray-100"
            }`}
            onClick={() => onFlowSelect(flow.id)}
          >
            <span className="text-sm truncate">{flow.title}</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onFlowDelete(flow.id)
              }}
              className="text-red-500 hover:text-red-700 hover:bg-red-50"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>

      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>새 플로우 생성</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="flow-title">제목</Label>
              <Input
                id="flow-title"
                value={newFlowTitle}
                onChange={(e) => setNewFlowTitle(e.target.value)}
                maxLength={64}
              />
            </div>
            <div>
              <Label htmlFor="flow-description">설명</Label>
              <Textarea
                id="flow-description"
                value={newFlowDescription}
                onChange={(e) => setNewFlowDescription(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
              취소
            </Button>
            <Button onClick={handleCreateFlow}>생성</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

