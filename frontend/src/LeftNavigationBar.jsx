import React, { useState } from 'react';
import { 
  Search, 
  Library, 
  GraduationCap,
  Settings,
  User,
  LogIn,
  LogOut,
  ScrollText,
  Home
} from 'lucide-react';

const LeftNavigation = ({ onHomeClick, onProfileClick, onArchivesClick }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(true);
  const [userProfile, setUserProfile] = useState({
    name: 'Leslie Jiang',
    role: 'Research Staff',
    imageUrl: 'https://lh3.googleusercontent.com/a-/ALV-UjWuC5hyWcRkPxjamU0YAoH91fbpGv04ZaeOjzfhH4nVKULabvU=s141-p-k-rw-no'
  });

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  return (
    <nav className="w-32 h-screen bg-white border-r border-[#E8E8D0] flex flex-col ">
      {/* User Profile Section */}
      <div className="px-2 py-4 bg-white border-b border-[#E8E8D0] text-center">
        {isLoggedIn ? (
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 rounded-full overflow-hidden mb-2 border-2 border-[#E8E8D0] shadow-sm">
              <img
                src={userProfile.imageUrl}
                alt="User avatar"
                className="w-full h-full object-cover"
              />
            </div>
            <h3 className="text-sm font-medium text-gray-800 leading-tight truncate">
              {userProfile.name}
            </h3>
            <span className="text-xs text-gray-600 truncate">
              {userProfile.role}
            </span>
          </div>
        ) : (
          <div className="flex flex-col items-center py-2">
            <div className="w-12 h-12 rounded-full bg-[#F5F5DC] flex items-center justify-center mb-2">
              <User className="w-8 h-8 text-gray-500" />
            </div>
            <button onClick={handleLogin} className="text-sm text-gray-600 hover:text-gray-800 flex items-center space-x-1">
              <LogIn className="w-4 h-4" />
              <span>Sign In</span>
            </button>
          </div>
        )}
      </div>

      {/* Navigation Items */}
      <div className="flex-1 pt-3">
        <div className="space-y-1">
          <button onClick={onHomeClick} className="flex flex-col items-center w-full px-1 py-3 text-gray-600 rounded hover:bg-[#F5F5DC] transition-colors">
            <Home className="w-7 h-7 mb-1.5" />
            <span className="text-sm font-medium">Home</span>
          </button>

          <button onClick={onProfileClick} className="flex flex-col items-center w-full px-1 py-3 text-gray-600 rounded hover:bg-[#F5F5DC] transition-colors">
            <GraduationCap className="w-7 h-7 mb-1.5" />
            <span className="text-sm font-medium">My Profile</span>
          </button>

          <button onClick={onArchivesClick} className="flex flex-col items-center w-full px-1 py-3 text-gray-600 rounded hover:bg-[#F5F5DC] transition-colors">
            <Library className="w-7 h-7 mb-1.5" />
            <span className="text-sm font-medium">Archives</span>
          </button>

          <button className="flex flex-col items-center w-full px-1 py-3 text-gray-600 rounded hover:bg-[#F5F5DC] transition-colors">
            <Search className="w-7 h-7 mb-1.5" />
            <span className="text-sm font-medium">Search</span>
          </button>

          <button className="flex flex-col items-center w-full px-1 py-3 text-gray-600 rounded hover:bg-[#F5F5DC] transition-colors">
            <ScrollText className="w-7 h-7 mb-1.5" />
            <span className="text-sm font-medium">Papers</span>
          </button>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="mt-8 border-t border-[#E8E8D0] bg-white">
        <div className="p-2 flex justify-between items-center">
          <button className="text-gray-500 hover:text-gray-700 transition-colors">
            <Settings className="w-6 h-6" />
          </button>
          {isLoggedIn && (
            <button onClick={handleLogout} className="text-gray-500 hover:text-gray-700 transition-colors">
              <LogOut className="w-6 h-6" />
            </button>
          )}
        </div>
      </div>
    </nav>
  );
};

export default LeftNavigation;
