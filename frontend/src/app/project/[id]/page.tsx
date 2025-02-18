import { use } from "react"
import { ProjectPage } from "./ProjectPage"

export default function Page({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params)
  return <ProjectPage id={resolvedParams.id} />
}

