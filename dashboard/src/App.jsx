import { useState, useCallback, useEffect } from 'react'
import View1Overview from './views/View1Overview.jsx'
import View2Dispatch from './views/View2Dispatch.jsx'
import View3Safety from './views/View3Safety.jsx'
import View4Tradeoffs from './views/View4Tradeoffs.jsx'
import View5Pipeline from './views/View5Pipeline.jsx'
import View6Forecaster from './views/View6Forecaster.jsx'
import View7Optimizer from './views/View7Optimizer.jsx'
import ScadaErrorBoundary from './components/ScadaErrorBoundary.jsx'

const TABS = [
  { id: 'overview', label: '1 · SYSTEM' },
  { id: 'dispatch', label: '2 · INSPECTOR' },
  { id: 'safety', label: '3 · DECISION MAP' },
  { id: 'tradeoffs', label: '4 · PROOF' },
  { id: 'pipeline', label: '5 · PIPELINE' },
  { id: 'forecaster', label: '6 · FORECASTER' },
  { id: 'optimizer', label: '7 · OPTIMIZER' },
]

export default function App() {
  const [tab, setTab] = useState('overview')
  // Shared cross-view playhead: clicking an event/anomaly marker in View 1 or
  // View 3 jumps straight to that exact hour in View 2 (Decision Inspector).
  // `nonce` forces View 2 to re-sync even if the same scenario/hour is
  // clicked twice in a row.
  const [jumpTarget, setJumpTarget] = useState(null)
  useEffect(() => { window.scrollTo({ top: 0 }) }, [tab])

  const navigateToHour = useCallback((scenarioId, hourIndex, variant) => {
    setJumpTarget({ scenarioId, hourIndex, variant, nonce: Date.now() })
    setTab('dispatch')
  }, [])

  return (
    <div className="min-h-screen bg-scada-bg text-zinc-200">
      <header className="flex flex-wrap items-center justify-between gap-x-6 gap-y-2 border-b border-scada-border bg-scada-panel px-4 py-2">
        <div className="flex items-center gap-3">
          <span className="text-[18px] font-semibold tracking-tight text-zinc-100">POLARIS</span>
          <span className="text-[16px] text-zinc-300">Evidence-Backed XAI Diagnostic Terminal</span>
        </div>
        <nav className="flex flex-wrap gap-1">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`whitespace-nowrap rounded px-3 py-1.5 text-[16px] font-semibold tracking-wide transition-colors ${
                tab === t.id ? 'bg-zinc-800 text-zinc-100 border border-zinc-500' : 'text-zinc-300 hover:text-white'
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>

      <main className={`mx-auto px-4 py-4 ${(tab === 'pipeline' || tab === 'forecaster' || tab === 'optimizer') ? 'max-w-[1760px]' : 'max-w-7xl'}`}>
        {/* Keyed per-tab so switching views resets a tripped boundary rather
            than leaving a stale error pane behind when the underlying data changes. */}
        <ScadaErrorBoundary key={tab}>
          {tab === 'overview' && <View1Overview />}
          {tab === 'dispatch' && <View2Dispatch jumpTarget={jumpTarget} />}
          {tab === 'safety' && <View3Safety onNavigateToHour={navigateToHour} />}
          {tab === 'tradeoffs' && <View4Tradeoffs />}
          {tab === 'pipeline' && <View5Pipeline />}
          {tab === 'forecaster' && <View6Forecaster />}
          {tab === 'optimizer' && <View7Optimizer />}
        </ScadaErrorBoundary>
      </main>
    </div>
  )
}
