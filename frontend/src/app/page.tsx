"use client"

import Link from "next/link"
import { ArrowRight, TrendingUp, Users, Brain, DollarSign } from "lucide-react"
import type { ReactNode } from "react"
import { useAuth } from "@/contexts/AuthContext"

interface FeatureCardProps {
  icon: ReactNode
  title: string
  description: string
}

export default function Home() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen flex flex-col">
      {/* Main Content */}
      <main className="flex-grow">
        {/* Hero Section */}
        <section className="text-center py-20 px-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white">
          <h1 className="text-5xl font-bold mb-4">최적의 연봉 협상 서비스</h1>
          <p className="text-xl mb-8">AI 기반 인사이트로 직원 유지와 균형 잡힌 보상을 실현하세요</p>
          {user ? (
            <Link
              href="/workspace"
              className="bg-white text-blue-600 px-6 py-3 rounded-full inline-flex items-center hover:bg-gray-100 transition duration-300"
            >
              Workspace
              <ArrowRight className="ml-2" size={20} />
            </Link>
          ) : (
            <Link
              href="/login"
              className="bg-white text-blue-600 px-6 py-3 rounded-full inline-flex items-center hover:bg-gray-100 transition duration-300"
            >
              Get Started
              <ArrowRight className="ml-2" size={20} />
            </Link>
          )}
        </section>

        {/* Features Section */}
        <section className="py-20 bg-gray-50">
          <div className="max-w-5xl mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12">Why choose the BigStar</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <FeatureCard
                icon={<TrendingUp size={24} />}
                title="데이터 기반 인사이트"
                description="AI와 빅데이터를 활용한 정확한 연봉 벤치마크 제공"
              />
              <FeatureCard
                icon={<Users size={24} />}
                title="직원 유지 중심"
                description="핵심 인재 유출 방지를 위한 최적의 제안"
              />
              <FeatureCard
                icon={<Brain size={24} />}
                title="AI 기반 추천"
                description="귀사에 맞춤화된 지능형 연봉 제안"
              />
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-gray-100">
          <div className="max-w-4xl mx-auto text-center px-4">
            <h2 className="text-3xl font-bold mb-4">연봉 협상 전략의 혁신을 경험하세요</h2>
            <p className="text-xl mb-8">빅스타와 함께 데이터에 기반한 현명한 연봉 결정으로 한국 최고의 기업이 되세요</p>
            {user ? (
              <Link
                href="/workspace"
                className="bg-blue-600 text-white px-8 py-3 rounded-full inline-flex items-center hover:bg-blue-700 transition duration-300"
              >
                Demo
                <DollarSign className="ml-2" size={20} />
              </Link>
            ) : (
              <Link
                href="/login"
                className="bg-blue-600 text-white px-8 py-3 rounded-full inline-flex items-center hover:bg-blue-700 transition duration-300"
              >
                Demo
                <DollarSign className="ml-2" size={20} />
              </Link>
            )}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 text-center">
        <p>&copy; 2025 BigStar. 모든 권리 보유.</p>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md text-center">
      <div className="text-blue-600 mb-4 flex justify-center">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

