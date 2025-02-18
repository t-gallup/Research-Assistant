import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ResearchAssistant from "./pages/ResearchAssistant";
import { initializeApp } from "firebase/app";
import { firebaseConfig } from "./firebase/config";
import { AuthProvider } from "./contexts/AuthContext";
import AuthPage from "./components/Auth/AuthPage";
import ProtectedRoute from "./components/Auth/ProtectedRoute";
import Profile from "./pages/Profile";
import SearchResults from './pages/SearchResults';

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
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
            <Route path="/search" element={<SearchResults />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
