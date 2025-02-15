import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ResearchAssistant from './components/ResearchAssistant';
import { initializeApp } from 'firebase/app';
import { firebaseConfig } from './firebase/config';
import { AuthProvider } from './contexts/AuthContext';
import AuthPage from './components/auth/AuthPage';
import ProtectedRoute from './components/auth/ProtectedRoute';

initializeApp(firebaseConfig);

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/auth" element={<AuthPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <ResearchAssistant />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
