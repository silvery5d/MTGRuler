import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import cytoscape from 'cytoscape'
import fcose from 'cytoscape-fcose'
import './index.css'
import App from './App.tsx'

cytoscape.use(fcose)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
