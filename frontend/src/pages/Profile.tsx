import React, { useState } from 'react';
import { getAuth, updateProfile } from 'firebase/auth';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import Navbar from './Navbar';

const Profile = () => {
  const auth = getAuth();
  const user = auth.currentUser;
  const navigate = useNavigate();
  const [name, setName] = useState(user?.displayName || '');
  const [email, setEmail] = useState(user?.email || '');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleSave = async () => {
    if (!user) return;
    
    setIsSaving(true);
    setError('');
    setSuccessMessage('');

    try {
      if (name !== user.displayName) {
        await updateProfile(user, {
          displayName: name
        });
      }
      
      setSuccessMessage('Profile updated successfully!');
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    } catch (err) {
      setError('Failed to update profile. Please try again.');
      console.error('Error updating profile:', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-blue-900">
      <Navbar />
      <div className="max-w-2xl mx-auto p-6">
        {/* Back button */}
        <button
          onClick={() => navigate(-1)}
          className="mb-6 flex items-center text-gray-200 hover:text-white"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back
        </button>

        <div className="bg-gray-800/80 backdrop-blur-sm rounded-lg p-8 space-y-6 shadow-xl">
          <h1 className="text-2xl text-white font-bold mb-8">Profile Settings</h1>

          {/* Name Field */}
          <div className="space-y-2">
            <label className="text-white text-xl font-medium">Name</label>
            <p className="text-gray-300 text-sm">The name associated with this account</p>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-gray-700/60 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Email Field */}
          <div className="space-y-2">
            <label className="text-white text-xl font-medium">Email address</label>
            <p className="text-gray-300 text-sm">The email address associated with this account</p>
            <input
              type="email"
              value={email}
              disabled
              className="w-full px-4 py-2 rounded-lg bg-gray-700/60 text-gray-400 border border-gray-600 cursor-not-allowed"
            />
            <p className="text-gray-400 text-xs mt-1">Email address cannot be changed</p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="text-red-400 text-sm">{error}</div>
          )}

          {/* Success Message */}
          {successMessage && (
            <div className="text-green-400 text-sm">{successMessage}</div>
          )}

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={isSaving || name === user?.displayName}
            className={`px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg transition-all duration-200 ${
              isSaving || name === user?.displayName
                ? 'opacity-50 cursor-not-allowed'
                : 'hover:from-blue-700 hover:to-purple-700 hover:shadow-lg'
            }`}
          >
            {isSaving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile;