import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import ScadaErrorBoundary from './components/ScadaErrorBoundary.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ScadaErrorBoundary>
      <App />
    </ScadaErrorBoundary>
  </React.StrictMode>
)
