import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './layouts/Layout';
import { Dashboard } from './pages/Dashboard';
import { DesignChanges } from './pages/DesignChanges';
import { RiskManagement } from './pages/RiskManagement';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="design-changes" element={<DesignChanges />} />
          <Route path="risk-management" element={<RiskManagement />} />
          <Route path="regulatory" element={<div>Regulatory Compliance</div>} />
          <Route path="agents" element={<div>Agent System</div>} />
          <Route path="settings" element={<div>Settings</div>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
