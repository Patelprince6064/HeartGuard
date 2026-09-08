import { useState } from 'react'
import api from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import PageHeader from '../../components/common/PageHeader'
import { Activity, Lightbulb } from 'lucide-react'

export default function LifestyleAnalyzerPage() {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    if (!text.trim()) return
    setLoading(true)
    try {
      const res = await api.assessments.create({ lifestyle_text: text })
      setResult(res.data)
    } catch {
      setResult({ error: 'Analysis failed. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <PageHeader title="Lifestyle Analyzer" description="Analyze how your daily habits impact your heart health" />

      <Card>
        <h3 className="text-lg font-semibold text-slate-900 mb-2">Describe Your Lifestyle</h3>
        <p className="text-sm text-slate-500 mb-4">
          Share details about your daily routine, diet, exercise, sleep patterns, and stress levels.
        </p>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={10}
          placeholder="e.g. I walk 30 minutes daily, eat lots of vegetables, drink 2 cups of coffee, sleep 6-7 hours, work in an office with moderate stress..."
          className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
        />
        <div className="mt-4 flex justify-end">
          <Button onClick={handleAnalyze} loading={loading}>
            <Activity className="h-4 w-4" /> Analyze Lifestyle
          </Button>
        </div>
      </Card>

      {result && !result.error && (
        <Card>
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Analysis Results</h3>
          <div className="space-y-4">
            {result.risk_score !== undefined && (
              <div className="bg-slate-50 p-4 rounded-lg">
                <p className="text-sm text-slate-500">Lifestyle Risk Score</p>
                <p className="text-2xl font-bold text-slate-900">{result.risk_score}%</p>
              </div>
            )}
            {result.recommendations && result.recommendations.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-slate-900 mb-2">Recommendations</h4>
                <div className="space-y-2">
                  {result.recommendations.map((r, i) => (
                    <div key={i} className="flex items-start gap-2 p-3 bg-slate-50 rounded-lg">
                      <Lightbulb className="h-4 w-4 text-amber-500 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-slate-700">{typeof r === 'string' ? r : r.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {result?.error && (
        <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg border border-red-200">
          {result.error}
        </div>
      )}
    </div>
  )
}
