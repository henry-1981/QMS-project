import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './layouts/Layout';
import { Dashboard } from './pages/Dashboard';
import { DesignChanges } from './pages/DesignChanges';
import { RiskManagement } from './pages/RiskManagement';
import { Login } from './pages/Login';
import { AuthCallback } from './pages/AuthCallback';
import { Settings } from './pages/Settings';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="design-changes" element={<DesignChanges />} />
            <Route path="risk-management" element={<RiskManagement />} />
            <Route path="regulatory" element={<div>Regulatory Compliance</div>} />
            <Route path="agents" element={<div>Agent System</div>} />
            <Route path="settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
