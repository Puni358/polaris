import { Component } from 'react'

// Catches render-time errors anywhere in the wrapped tree (e.g. a malformed
// row from the real solver CSVs) and shows a SCADA-themed fallback pane
// instead of white-screening the whole dashboard. Standard React class
// component -- error boundaries cannot be implemented as function components
// (no hook equivalent exists for getDerivedStateFromError/componentDidCatch).
export default class ScadaErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    // eslint-disable-next-line no-console
    console.error('[ScadaErrorBoundary] Render failure:', error, info)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-[200px] flex-col items-center justify-center gap-3 rounded border border-rose-800 bg-black/60 p-8 text-center">
          <span className="text-[18px] font-semibold uppercase tracking-wide text-rose-500">
            ⚠ TELEMETRY INGESTION ERROR
          </span>
          <span className="tnum max-w-md text-[11px] text-zinc-500">
            A render fault occurred while processing station telemetry
            {this.state.error?.message ? ` — ${this.state.error.message}` : ''}. This pane has been isolated;
            the rest of the control terminal is unaffected.
          </span>
          <button
            onClick={this.handleReset}
            className="mt-1 rounded border border-rose-700 bg-rose-950 px-3 py-1 text-[11px] text-rose-400 hover:border-rose-500"
          >
            ⟳ RETRY RENDER
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
