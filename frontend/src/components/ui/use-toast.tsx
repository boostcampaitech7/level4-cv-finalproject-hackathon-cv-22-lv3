"use client"

import * as React from "react"

export type ToastType = {
  id: string
  title?: string
  description?: string
  duration?: number
  variant?: "default" | "destructive"
}

type ToastContextType = {
  toasts: ToastType[]
  addToast: (toast: Omit<ToastType, "id">) => void
  removeToast: (id: string) => void
}

const ToastContext = React.createContext<ToastContextType | undefined>(undefined)

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = React.useState<ToastType[]>([])

  const addToast = React.useCallback((toast: Omit<ToastType, "id">) => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts((prevToasts) => [...prevToasts, { ...toast, id }])
  }, [])

  const removeToast = React.useCallback((id: string) => {
    setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id))
  }, [])

  React.useEffect(() => {
    const timer = setInterval(() => {
      setToasts((prevToasts) =>
        prevToasts.filter((toast) => {
          if (toast.duration && Date.now() - new Date(toast.id).getTime() > toast.duration) {
            return false
          }
          return true
        }),
      )
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const contextValue = React.useMemo(() => ({ toasts, addToast, removeToast }), [toasts, addToast, removeToast])

  return <ToastContext.Provider value={contextValue}>{children}</ToastContext.Provider>
}

export const useToast = (): ToastContextType => {
  const context = React.useContext(ToastContext)
  if (context === undefined) {
    throw new Error("useToast must be used within a ToastProvider")
  }
  return context
}

// This is a custom hook that can be used in functional components
export const useToastMessage = () => {
  const { addToast } = useToast()
  return React.useCallback(
    (props: Omit<ToastType, "id">) => {
      addToast(props)
    },
    [addToast],
  )
}

