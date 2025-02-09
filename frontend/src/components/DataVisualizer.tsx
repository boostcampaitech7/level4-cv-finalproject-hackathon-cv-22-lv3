"use client"

import { useEffect, useState } from "react"
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from "chart.js"
import { Bar, Doughnut } from "react-chartjs-2"
import { Card, CardContent } from "@/components/ui/card"
import { determineColumnType, preprocessData } from "@/utils/dataAnalysis"
import { Hash, Clock } from 'lucide-react'
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement)

interface DataVisualizerProps {
  dataset: {
    path: string
  }
}

const CHART_COLORS = [
  "rgba(54, 162, 235, 0.8)",
  "rgba(75, 192, 192, 0.8)",
  "rgba(153, 102, 255, 0.8)",
  "rgba(255, 99, 132, 0.8)",
  "rgba(255, 159, 64, 0.8)",
]

export function DataVisualizer({ dataset }: DataVisualizerProps) {
  const [data, setData] = useState<any[]>([])
  const [columns, setColumns] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("/api/parse-csv", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ filepath: dataset.path }),
        })

        if (!response.ok) {
          throw new Error("Failed to fetch data")
        }

        const csvData = await response.json()
        setData(csvData)
        if (csvData.length > 0) {
          setColumns(Object.keys(csvData[0]))
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred")
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [dataset.path])

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  if (!data.length) return <div>No data available</div>

  return (
    <div className="border border-gray-200 rounded-lg p-4 bg-white">
      <div className="h-[calc(100vh-16rem)]">
        <ScrollArea className="h-full w-full">
          <div className="flex gap-6 pb-4" style={{ minWidth: `${columns.length * 266}px` }}>
            {columns.map((column) => {
              const values = data.map((row) => row[column])
              const columnType = determineColumnType(values)
              const processedData = preprocessData(data, column)

              const chartData = {
                labels: processedData.labels,
                datasets: [
                  {
                    label: column,
                    data: processedData.values,
                    backgroundColor: CHART_COLORS,
                    borderColor: CHART_COLORS.map((color) => color.replace("0.8", "1")),
                    borderWidth: 1,
                  },
                ],
              }

              return (
                <Card 
                  key={column} 
                  className="w-[250px] flex-shrink-0 rounded-xl shadow-sm hover:shadow-md transition-shadow"
                >
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-3">
                      {columnType === "numerical" ? (
                        <Hash className="w-4 h-4 text-gray-500" />
                      ) : (
                        <Clock className="w-4 h-4 text-gray-500" />
                      )}
                      <h3 className="text-sm font-medium text-gray-700 truncate" title={column}>
                        {column}
                      </h3>
                    </div>
                    <div className="h-[150px] bg-white flex items-center justify-center">
                      <div className="w-[90%] h-[90%]">
                        {columnType === "numerical" ? (
                          <Bar
                            data={chartData}
                            options={{
                              responsive: true,
                              maintainAspectRatio: false,
                              plugins: {
                                legend: {
                                  display: false,
                                },
                                tooltip: {
                                  callbacks: {
                                    label: (context) => `${context.parsed.y}`,
                                  },
                                },
                              },
                              scales: {
                                y: {
                                  beginAtZero: true,
                                  grid: {
                                    color: "rgba(0, 0, 0, 0.1)",
                                  },
                                  ticks: {
                                    maxTicksLimit: 5,
                                  },
                                },
                                x: {
                                  display: false,
                                },
                              },
                            }}
                          />
                        ) : (
                          <Doughnut
                            data={chartData}
                            options={{
                              responsive: true,
                              maintainAspectRatio: false,
                              plugins: {
                                legend: {
                                  display: false,
                                },
                                tooltip: {
                                  callbacks: {
                                    label: (context) => `${context.label}: ${context.parsed}`,
                                  },
                                },
                              },
                            }}
                          />
                        )}
                      </div>
                    </div>
                    <div className="mt-3 border-t pt-3">
                      <table className="w-full text-sm">
                        <tbody>
                          {data.slice(0, 15).map((row, i) => (
                            <tr key={i} className="border-b last:border-0">
                              <td className="py-1 text-gray-600 truncate text-center" title={row[column]}>
                                {row[column]}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
          <ScrollBar orientation="horizontal" />
        </ScrollArea>
      </div>
    </div>
  )
}

