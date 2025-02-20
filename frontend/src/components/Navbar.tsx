import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, Search } from 'lucide-react';
import UserDropdown from './UserDropdown';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleHomeClick = () => {
    navigate('/');
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <nav className="bg-gray-800/80 backdrop-blur-sm border-b border-gray-700" style={{ position: 'relative', zIndex: 50 }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-300 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 md:hidden"
            >
              <Menu className="h-6 w-6" />
            </button>
            <div className="text-xl font-bold ml-2 text-white">
              <button onClick={handleHomeClick}>
                Research Assistant
              </button>
            </div>
          </div>

          <div className="hidden md:block">
            {/* Desktop navigation links */}
          </div>

          <div className="flex items-center space-x-4" style={{ position: 'relative', zIndex: 1000 }}>
            <form onSubmit={handleSearch} className="hidden md:block relative w-64">
              <div className="hidden md:block relative w-64">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-gray-600 rounded-md leading-5 bg-gray-700/60 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Search for articles"
                />
              </div>
            </form>
            <UserDropdown />
          </div>
        </div>

        {isMenuOpen && (
          <div className="md:hidden">
            {/* Mobile menu */}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;