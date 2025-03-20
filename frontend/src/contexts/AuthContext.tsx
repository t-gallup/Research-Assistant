import React, { createContext, useContext, useState, useEffect } from 'react';
import { getAuth, onAuthStateChanged, User as FirebaseUser } from 'firebase/auth';
import { AuthContextType, User } from '../types/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      const auth = getAuth();
      const unsubscribe = onAuthStateChanged(
        auth, 
        (firebaseUser: FirebaseUser | null) => {
          if (firebaseUser) {
            setUser({
              uid: firebaseUser.uid,
              email: firebaseUser.email,
              displayName: firebaseUser.displayName,
              photoURL: firebaseUser.photoURL,
            });
          } else {
            setUser(null);
          }
          setLoading(false);
        },
        (error) => {
          console.error('Firebase auth state error:', error);
          setError(error.message);
          setLoading(false);
        }
      );

      return unsubscribe;
    } catch (err) {
      console.error('Error setting up Firebase auth:', err);
      setError(err instanceof Error ? err.message : 'Firebase authentication error');
      setLoading(false);
      return () => {};
    }
  }, []);

  // Show a basic error UI if Firebase auth fails completely
  if (error && !loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-800 text-white p-6">
        <div className="max-w-md w-full space-y-8 bg-gray-700 p-6 rounded-lg">
          <h2 className="text-center text-2xl font-bold">Authentication Error</h2>
          <p className="text-red-400">{error}</p>
          <p>
            There was a problem with the authentication service. This might be due to:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Missing Firebase configuration</li>
            <li>Invalid API keys</li>
            <li>Network connectivity issues</li>
          </ul>
          <div className="pt-4">
            <button 
              onClick={() => window.location.reload()}
              className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, loading, error }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};