import React, { useState } from 'react';
import { getAuth } from 'firebase/auth';

const Profile = () => {
  const auth = getAuth();
  const user = auth.currentUser;
  const [name, setName] = useState(user?.displayName || '');
  const [email, setEmail] = useState(user?.email || '');

  const handleSave = () => {
    // TODO: Implement save functionality
    console.log('Saving profile changes:', { name, email });
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-gray-800 rounded-lg p-8 space-y-6">
        {/* Name Field */}
        <div className="space-y-2">
          <label className="text-white text-xl font-medium">Name</label>
          <p className="text-gray-400 text-sm">The name associated with this account</p>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Email Field */}
        <div className="space-y-2">
          <label className="text-white text-xl font-medium">Email address</label>
          <p className="text-gray-400 text-sm">The email address associated with this account</p>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200"
        >
          Save
        </button>
      </div>
    </div>
  );
};

export default Profile;