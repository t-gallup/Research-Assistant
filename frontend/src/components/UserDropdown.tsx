import React, { useState, useRef, useEffect } from 'react';
import { LogOut, User } from 'lucide-react';
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

    if (photoUrl.includes('googleusercontent.com')) {
      const baseUrl = photoUrl.split('=')[0];
      return `${baseUrl}=s96-c`;
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

  const handleProfileClick = () => {
    navigate('/profile');
    setIsOpen(false);
  };

  return (
    <>
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
      </div>

      {isOpen && (
        <div className="fixed inset-0 bg-transparent z-50" onClick={() => setIsOpen(false)}>
          <div 
            className="fixed right-4 top-16 w-64 bg-gray-800 rounded-lg shadow-lg py-2"
            onClick={e => e.stopPropagation()}
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
        </div>
      )}
    </>
  );
};

export default UserDropdown;