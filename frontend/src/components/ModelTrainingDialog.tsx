"use client"

import * as React from "react"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ChevronDown } from "lucide-react"

interface ModelTrainingDialogProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: ModelTrainingData) => void
}

export interface ModelTrainingData {
  maxAttributes: number
  trainingTime: number
  modelQuality: string
}

export function ModelTrainingDialog({ isOpen, onClose, onSubmit }: ModelTrainingDialogProps) {
  const [maxAttributes, setMaxAttributes] = React.useState("")
  const [trainingTime, setTrainingTime] = React.useState("")
  const [modelQuality, setModelQuality] = React.useState("high")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      maxAttributes: Number(maxAttributes),
      trainingTime: Number(trainingTime),
      modelQuality: modelQuality,
    })
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>모델 학습</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="maxAttributes">최대 속성 개수</Label>
              <Input
                id="maxAttributes"
                type="number"
                value={maxAttributes}
                onChange={(e) => setMaxAttributes(e.target.value)}
                className="col-span-3"
                min={1}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="trainingTime">학습 시간</Label>
              <Input
                id="trainingTime"
                type="number"
                value={trainingTime}
                onChange={(e) => setTrainingTime(e.target.value)}
                className="col-span-3"
                min={1}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="modelQuality">모델 퀄리티</Label>
              <div className="relative">
                <select
                  id="modelQuality"
                  value={modelQuality}
                  onChange={(e) => setModelQuality(e.target.value)}
                  className="w-full h-10 px-3 py-2 bg-background border border-input rounded-md appearance-none focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                >
                  <option value="best">best</option>
                  <option value="high">high</option>
                  <option value="good">good</option>
                  <option value="medium">medium</option>
                </select>
                <ChevronDown className="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none" />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              취소
            </Button>
            <Button type="submit">완료</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

