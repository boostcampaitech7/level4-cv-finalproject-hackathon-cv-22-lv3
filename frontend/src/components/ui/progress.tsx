"use client"

import * as React from "react"
import * as ProgressPrimitive from "@radix-ui/react-progress"
import { cn } from "@/lib/utils"

interface ProgressProps extends React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root> {
  variant?: "emerald" | "blue" | "purple"
}

const Progress = React.forwardRef<React.ElementRef<typeof ProgressPrimitive.Root>, ProgressProps>(
  ({ className, value, variant = "blue", ...props }, ref) => {
    const variantStyles = {
      emerald: "bg-emerald-100 [&>div]:bg-emerald-500",
      blue: "bg-blue-100 [&>div]:bg-blue-500",
      purple: "bg-purple-100 [&>div]:bg-purple-500",
    }

    return (
      <ProgressPrimitive.Root
        ref={ref}
        className={cn("relative w-full overflow-hidden rounded-full", variantStyles[variant], className)}
        {...props}
      >
        <ProgressPrimitive.Indicator
          className="h-full w-full flex-1 transition-all duration-500"
          style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
        />
      </ProgressPrimitive.Root>
    )
  },
)
Progress.displayName = ProgressPrimitive.Root.displayName

export { Progress }

