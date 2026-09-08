import { useState, useEffect } from 'react'
import api from '../../services/api'
import Card from '../../components/common/Card'
import Loading from '../../components/common/Loading'
import EmptyState from '../../components/common/EmptyState'
import PageHeader from '../../components/common/PageHeader'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { BarChart3 } from 'lucide-react'

const COLORS = ['#16A34A', '#D97706', '#F59E0B', '#DC2626']

export default function PatientAnalyticsPage() {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.dashboard.getDashboard()
        setAnalytics(res.data)
      } catch {
        setAnalytics(null)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <Loading text="Loading analytics..." />

  const riskDistribution = analytics?.risk_distribution
    ? Object.entries(analytics.risk_distribution).map(([name, value]) => ({ name, value }))
    : []

  const trendData = analytics?.risk_trend || []

  return (
    <div className="space-y-6">
      <PageHeader title="My Analytics" description="View your personal health analytics and trends" />

      {!analytics ? (
        <EmptyState icon={BarChart3} title="No analytics data" message="Complete assessments to see your analytics." />
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card header="Risk Trend Over Time">
              {trendData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                    <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="risk_score" fill="#DC2626" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-sm text-slate-500 text-center py-8">No trend data yet</p>
              )}
            </Card>

            <Card header="Risk Distribution">
              {riskDistribution.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie data={riskDistribution} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                      {riskDistribution.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-sm text-slate-500 text-center py-8">No distribution data yet</p>
              )}
            </Card>
          </div>

          <Card header="Summary Stats">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-2xl font-bold text-slate-900">{analytics.total_assessments || 0}</p>
                <p className="text-sm text-slate-500">Total Assessments</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-2xl font-bold text-slate-900">{analytics.avg_risk || 0}%</p>
                <p className="text-sm text-slate-500">Average Risk</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{analytics.low_risk_count || 0}</p>
                <p className="text-sm text-slate-500">Low Risk</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-2xl font-bold text-red-600">{analytics.critical_alerts || 0}</p>
                <p className="text-sm text-slate-500">Critical Alerts</p>
              </div>
            </div>
          </Card>
        </>
      )}
    </div>
  )
}
