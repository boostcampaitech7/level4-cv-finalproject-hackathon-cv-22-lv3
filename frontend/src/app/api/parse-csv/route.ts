import { type NextRequest, NextResponse } from "next/server"
import { promises as fs } from "fs"
import Papa from "papaparse"

export async function POST(req: NextRequest) {
  try {
    const { filepath } = await req.json()

    // CSV 파일 읽기
    const fileContent = await fs.readFile(filepath, "utf-8")

    // CSV 파싱
    const results = Papa.parse(fileContent, {
      header: true,
      dynamicTyping: true,
    })

    return NextResponse.json(results.data)
  } catch (error) {
    console.error("Error parsing CSV:", error)
    return NextResponse.json({ error: "Failed to parse CSV file" }, { status: 500 })
  }
}

