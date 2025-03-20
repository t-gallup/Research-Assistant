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
import Usage from './pages/Usage';
import Payment from "./pages/Payment";

// Check if Firebase config is valid before initializing
const initFirebase = () => {
  try {
    // Log Firebase config for debugging (don't log the actual keys in production)
    console.log('Firebase Config Keys Provided:', {
      apiKey: firebaseConfig.apiKey ? 'YES' : 'NO',
      authDomain: firebaseConfig.authDomain ? 'YES' : 'NO', 
      projectId: firebaseConfig.projectId ? 'YES' : 'NO',
      appId: firebaseConfig.appId ? 'YES' : 'NO',
      messagingSenderId: firebaseConfig.messagingSenderId ? 'YES' : 'NO'
    });

    // Validate required Firebase config values
    if (!firebaseConfig.apiKey) {
      console.error('Firebase API key is missing. Authentication will not work.');
      return false;
    }
    
    if (!firebaseConfig.appId) {
      console.error('Firebase App ID is missing. Authentication will not work.');
      return false;
    }
    
    // Initialize Firebase if config is valid
    initializeApp(firebaseConfig);
    console.log('Firebase successfully initialized');
    return true;
  } catch (error) {
    console.error('Error initializing Firebase:', error);
    return false;
  }
};

// Initialize Firebase with error handling
const firebaseInitialized = initFirebase();
if (!firebaseInitialized) {
  console.warn('Firebase initialization failed. Authentication features may not work correctly.');
}

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
            <Route
              path="/usage"
              element={
                <ProtectedRoute>
                  <Usage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/payment"
              element={
                <ProtectedRoute>
                  <Payment />
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