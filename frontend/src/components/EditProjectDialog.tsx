"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { FileText, Type } from "lucide-react"

interface EditProjectDialogProps {
  isOpen: boolean
  onClose: () => void
  onEditProject: (title: string, description: string) => void
  initialTitle: string
  initialDescription: string
}

export function EditProjectDialog({
  isOpen,
  onClose,
  onEditProject,
  initialTitle,
  initialDescription,
}: EditProjectDialogProps) {
  const [title, setTitle] = useState(initialTitle)
  const [description, setDescription] = useState(initialDescription)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onEditProject(title, description)
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px] border-gray-300 rounded-lg">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-center pb-2">프로젝트 수정</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title" className="text-sm font-medium flex items-center gap-2 text-gray-700">
                <Type className="h-4 w-4" />
                프로젝트명
              </Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full"
                required
                maxLength={64}
                placeholder="프로젝트 이름을 입력하세요"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description" className="text-sm font-medium flex items-center gap-2 text-gray-700">
                <FileText className="h-4 w-4" />
                설명
              </Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full min-h-[100px]"
                placeholder="프로젝트에 대한 설명을 입력하세요"
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} className="w-full sm:w-auto">
              취소
            </Button>
            <Button type="submit" className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700">
              수정
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

