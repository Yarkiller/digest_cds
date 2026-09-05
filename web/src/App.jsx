import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppShell from './components/AppShell.jsx'
import IssuePage from './pages/IssuePage.jsx'
import KnowledgePage from './pages/KnowledgePage.jsx'
import MaterialPage from './pages/MaterialPage.jsx'
import VotingPage from './pages/VotingPage.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<IssuePage />} />
          <Route path="voting" element={<VotingPage />} />
          <Route path="knowledge" element={<KnowledgePage />} />
          <Route path="materials/:id" element={<MaterialPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
