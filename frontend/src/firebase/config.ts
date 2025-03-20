// Check for environment variables
const missingVars = [];
if (!process.env.REACT_APP_FIREBASE_API_KEY) missingVars.push('REACT_APP_FIREBASE_API_KEY');
if (!process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID) missingVars.push('REACT_APP_FIREBASE_MESSAGING_SENDER_ID');
if (!process.env.REACT_APP_FIREBASE_APP_ID) missingVars.push('REACT_APP_FIREBASE_APP_ID');

// Log any missing environment variables
if (missingVars.length > 0) {
  console.error(`Missing Firebase environment variables: ${missingVars.join(', ')}`);
  console.log('Current environment variables:', Object.keys(process.env).filter(key => key.startsWith('REACT_APP_')));
}

export const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: "summarization-3a05c.firebaseapp.com",
  projectId: "summarization-3a05c",
  storageBucket: "summarization-3a05c.firebasestorage.app",
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
  measurementId: "G-8Y2T0SPS7D"
};