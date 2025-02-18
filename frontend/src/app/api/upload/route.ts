import { type NextRequest, NextResponse } from "next/server"
import { writeFile, mkdir, unlink } from "fs/promises"
import path from "path"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get("file") as File

    if (!file) {
      return NextResponse.json({ error: "파일이 없습니다." }, { status: 400 })
    }

    const timestamp = new Date().getTime()
    const fileName = `${timestamp}_${file.name}`
    const uploadDir = "/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/frontend/uploads"
    const filePath = path.join(uploadDir, fileName)

    try {
      await mkdir(uploadDir, { recursive: true })
    } catch (error) {
      console.error("Error creating uploads directory:", error)
    }

    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)

    await writeFile(filePath, buffer)

    return NextResponse.json({
      success: true,
      path: filePath,
    })
  } catch (error) {
    console.error("Error in upload handler:", error)
    return NextResponse.json({ error: "파일 업로드 중 오류가 발생했습니다." }, { status: 500 })
  }
}

export async function DELETE(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const filePath = searchParams.get("path")

  if (!filePath) {
    return NextResponse.json({ error: "파일 경로가 제공되지 않았습니다." }, { status: 400 })
  }

  try {
    await unlink(filePath) // 전체 경로를 그대로 사용
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Error deleting file:", error)
    return NextResponse.json({ error: "파일 삭제 중 오류가 발생했습니다." }, { status: 500 })
  }
}

