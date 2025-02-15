import React, { useState, useRef, useEffect } from 'react';
import { Sun, Moon, LogOut } from 'lucide-react';
import { getAuth, signOut } from 'firebase/auth';

const UserDropdown = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const dropdownRef = useRef(null);
  const auth = getAuth();
  const user = auth.currentUser;

  // Function to get proper Google profile picture
  const getGooglePhotoUrl = () => {
    if (!user?.providerData?.[0]?.photoURL) return null;
    
    const photoUrl = user.providerData[0].photoURL;
    if (photoUrl.includes('googleusercontent.com')) {
      // Remove any existing size parameters and force high-quality image
      return photoUrl.split('=')[0] + '=s96-c';
    }
    return photoUrl;
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    try {
      await signOut(auth);
      window.location.href = '/auth';
    } catch (error) {
      console.error('Failed to log out:', error);
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-8 h-8 rounded-full overflow-hidden flex items-center justify-center bg-orange-500"
      >
        {getGooglePhotoUrl() ? (
          <img 
            src={getGooglePhotoUrl()} 
            alt="Profile"
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="text-white text-lg font-semibold">
            {user?.displayName?.charAt(0)?.toUpperCase() || 'U'}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-gray-800 rounded-lg shadow-lg py-2 z-50">
          <div className="px-4 py-2 flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full overflow-hidden flex items-center justify-center bg-orange-500">
              {getGooglePhotoUrl() ? (
                <img 
                  src={getGooglePhotoUrl()} 
                  alt="Profile"
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-white text-xl font-semibold">
                  {user?.displayName?.charAt(0)?.toUpperCase() || 'U'}
                </span>
              )}
            </div>
            <div>
              <div className="text-white text-lg font-semibold">
                {user?.displayName || 'User'}
              </div>
              <div className="text-gray-400 text-sm">{user?.email}</div>
            </div>
          </div>

          <div className="border-t border-gray-700">
            <div className="px-4 py-2 flex items-center justify-between">
              <div className="text-gray-300 text-sm">Your profile</div>
            </div>
          </div>

          <div className="px-4 py-2 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {isDark ? (
                <Moon className="w-4 h-4 text-gray-400" />
              ) : (
                <Sun className="w-4 h-4 text-gray-400" />
              )}
            </div>
            <button
              onClick={() => setIsDark(!isDark)}
              className="w-10 h-5 bg-gray-700 rounded-full relative"
            >
              <div
                className={`w-4 h-4 rounded-full bg-white absolute top-0.5 transition-all ${
                  isDark ? 'left-5' : 'left-1'
                }`}
              />
            </button>
          </div>

          <div className="border-t border-gray-700">
            <button
              onClick={handleLogout}
              className="w-full px-4 py-2 text-left text-gray-300 hover:bg-gray-700 flex items-center space-x-2"
            >
              <LogOut className="w-4 h-4" />
              <span>Log out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserDropdown;