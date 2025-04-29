import React, { useState, useRef, useEffect } from 'react';
import { LogOut, User, LineChart } from 'lucide-react';
import { getAuth, signOut } from 'firebase/auth';
import { useNavigate } from 'react-router-dom';

const UserDropdown = () => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const auth = getAuth();
  const user = auth.currentUser;
  const navigate = useNavigate();

  const getGooglePhotoUrl = () => {
    if (!user) return null;
    
    const photoUrl = user.photoURL || user.providerData?.[0]?.photoURL;
    if (!photoUrl) return null;
    console.log('Original photo URL:', photoUrl);
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

  const handleProfileClick = () => {
    navigate('/profile');
    setIsOpen(false);
  };

  const handleUsageClick = () => {
    navigate('/usage');
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-8 h-8 rounded-full overflow-hidden flex items-center justify-center"
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
        <div 
          className="absolute right-0 mt-2 w-64 bg-gray-800 rounded-lg shadow-lg py-2"
          style={{ 
            zIndex: 1000,
            position: 'fixed',
            top: '4rem',
            right: '1rem'
          }}
        >
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
            <button
              onClick={handleProfileClick}
              className="w-full px-4 py-2 text-left text-gray-300 hover:bg-gray-700 flex items-center space-x-2"
            >
              <User className="w-4 h-4" />
              <span>Your profile</span>
            </button>
            <button
              onClick={handleUsageClick}
              className="w-full px-4 py-2 text-left text-gray-300 hover:bg-gray-700 flex items-center space-x-2"
            >
              <LineChart className="w-4 h-4" />
              <span>Usage Dashboard</span>
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