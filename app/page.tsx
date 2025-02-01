import Layout from "@/components/Layout"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Link from "next/link"
import { ArrowRight, Clock, MapPin, Shield, Building2, Code, Zap,
         Globe, ChartBar, Users, Lock, Radio, Bell, Database } from "lucide-react"

export default function Home() {
  return (
    <Layout>
      <nav className="fixed w-full z-50 bg-white/80 backdrop-blur-sm border-b">
        <div className="max-w-7xl mx-auto py-3 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className="flex items-center space-x-8">
            <h2 className="text-2xl font-bold text-indigo-600">EVS</h2>
            <div className="hidden md:flex space-x-6">
              <NavLink href="#features">Features</NavLink>
              <NavLink href="#solutions">Solutions</NavLink>
              <NavLink href="#enterprise">Enterprise</NavLink>
              <NavLink href="#testimonials">Testimonials</NavLink>
            </div>
          </div>
          <div className="flex space-x-4">
            <Link href="/login">
              <Button variant="outline" className="text-indigo-600 border-indigo-600 hover:bg-indigo-50">
                Login
              </Button>
            </Link>
            <Link href="/signup">
              <Button className="bg-indigo-600 text-white hover:bg-indigo-700">Start Free Trial</Button>
            </Link>
          </div>
        </div>
      </nav>

      <main className="pt-16">
        {/* Hero Section */}
        <section className="relative bg-gradient-to-b from-indigo-50 to-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
            <div className="text-center">
              <h1 className="text-5xl md:text-6xl font-extrabold text-indigo-600 mb-6">
                Next-Gen Emergency Response Platform
              </h1>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
                Empowering emergency services with AI-driven solutions for faster response times,
                seamless coordination, and enhanced safety protocols.
              </p>
              <div className="flex justify-center space-x-4">
                <Button size="lg" className="bg-indigo-600 text-white hover:bg-indigo-700">
                  Schedule Demo
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
                <Button size="lg" variant="outline" className="text-indigo-600 border-indigo-600">
                  View Documentation
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Statistics */}
        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <StatCard number="30%" text="Faster Response Time" />
              <StatCard number="99.9%" text="System Uptime" />
              <StatCard number="5000+" text="Active Vehicles" />
              <StatCard number="24/7" text="Expert Support" />
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <SectionHeader
              title="Advanced Features"
              subtitle="Comprehensive tools for modern emergency response"
            />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
              <FeatureCard
                icon={<Clock className="h-8 w-8 text-indigo-600" />}
                title="Real-time Tracking"
                description="GPS-powered real-time vehicle tracking with predictive ETAs and smart routing."
              />
              <FeatureCard
                icon={<Radio className="h-8 w-8 text-indigo-600" />}
                title="Communication Hub"
                description="Unified communication platform integrating radio, mobile, and digital channels."
              />
              <FeatureCard
                icon={<Database className="h-8 w-8 text-indigo-600" />}
                title="Data Analytics"
                description="Advanced analytics dashboard with ML-powered insights and predictive modeling."
              />
              <FeatureCard
                icon={<Bell className="h-8 w-8 text-indigo-600" />}
                title="Smart Alerts"
                description="Automated incident detection and intelligent notification system."
              />
              <FeatureCard
                icon={<Users className="h-8 w-8 text-indigo-600" />}
                title="Team Management"
                description="Comprehensive staff scheduling and resource allocation tools."
              />
              <FeatureCard
                icon={<Lock className="h-8 w-8 text-indigo-600" />}
                title="Security"
                description="Enterprise-grade security with end-to-end encryption and compliance."
              />
            </div>
          </div>
        </section>

        {/* Enterprise Solutions */}
        <section id="enterprise" className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <SectionHeader
              title="Enterprise Solutions"
              subtitle="Scalable solutions for organizations of all sizes"
            />
            <Tabs defaultValue="global" className="mt-12">
              <TabsList className="grid w-full grid-cols-1 md:grid-cols-3">
                <TabsTrigger value="global">Global Operations</TabsTrigger>
                <TabsTrigger value="compliance">Compliance & Security</TabsTrigger>
                <TabsTrigger value="integration">Custom Integration</TabsTrigger>
              </TabsList>
              <TabsContent value="global" className="mt-6">
                <EnterpriseCard
                  icon={<Globe className="h-8 w-8 text-indigo-600" />}
                  title="Global Emergency Response"
                  features={[
                    "Multi-jurisdiction coordination",
                    "24/7 global support centers",
                    "Multi-language interface",
                    "Regional compliance automation"
                  ]}
                />
              </TabsContent>
              <TabsContent value="compliance" className="mt-6">
                <EnterpriseCard
                  icon={<Shield className="h-8 w-8 text-indigo-600" />}
                  title="Security & Compliance"
                  features={[
                    "HIPAA, GDPR, ISO 27001 compliance",
                    "End-to-end encryption",
                    "Audit logging & reporting",
                    "Role-based access control"
                  ]}
                />
              </TabsContent>
              <TabsContent value="integration" className="mt-6">
                <EnterpriseCard
                  icon={<Code className="h-8 w-8 text-indigo-600" />}
                  title="Integration & Development"
                  features={[
                    "REST API & webhooks",
                    "Custom workflow automation",
                    "Legacy system integration",
                    "Dedicated support team"
                  ]}
                />
              </TabsContent>
            </Tabs>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-indigo-600 py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to transform your emergency response?
            </h2>
            <p className="text-xl text-indigo-100 mb-8">
              Join thousands of organizations already using our platform
            </p>
            <Button size="lg" variant="secondary" className="bg-white text-indigo-600 hover:bg-gray-100">
              Get Started Now
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>
        </section>
      </main>
    </Layout>
  )
}

interface NavLinkProps {
  href: string;
  children: React.ReactNode;
}

function NavLink({ href, children }: NavLinkProps) {
  return (
    <a href={href} className="text-gray-600 hover:text-indigo-600 font-medium">
      {children}
    </a>
  )
}

interface StatCardProps {
  number: string;
  text: string;
}

function StatCard({ number, text }: StatCardProps) {
  return (
    <div className="text-center">
      <h3 className="text-4xl font-bold text-indigo-600 mb-2">{number}</h3>
      <p className="text-gray-600">{text}</p>
    </div>
  )
}

interface SectionHeaderProps {
  title: string;
  subtitle: string;
}

function SectionHeader({ title, subtitle }: SectionHeaderProps) {
  return (
    <div className="text-center">
      <h2 className="text-3xl font-bold text-indigo-600 mb-4">{title}</h2>
      <p className="text-xl text-gray-600">{subtitle}</p>
    </div>
  )
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <Card className="flex flex-col items-center text-center">
      <CardHeader>
        {icon}
        <CardTitle className="text-xl font-bold text-indigo-600">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <CardDescription className="text-gray-600">{description}</CardDescription>
      </CardContent>
    </Card>
  )
}

interface EnterpriseCardProps {
  icon: React.ReactNode;
  title: string;
  features: string[];
}

function EnterpriseCard({ icon, title, features }: EnterpriseCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center space-x-2">
          {icon}
          <CardTitle className="text-2xl font-bold text-indigo-600">{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <ul className="space-y-4">
          {features.map((feature: string, index: number) => (
            <li key={index} className="flex items-center space-x-2">
              <Zap className="h-5 w-5 text-indigo-600" />
              <span className="text-gray-600">{feature}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
