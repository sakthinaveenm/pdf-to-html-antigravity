import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FileText, Upload, ListOrdered, Cpu, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { SystemCapabilities } from '../types';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [caps, setCaps] = useState<SystemCapabilities | null>(null);

  useEffect(() => {
    api.getCapabilities().then(setCaps).catch(() => null);
  }, []);

  const navItems = [
    { label: 'Dashboard', path: '/', icon: FileText },
    { label: 'Batch Upload', path: '/upload', icon: Upload },
    { label: 'Conversion Queue', path: '/queue', icon: ListOrdered },
  ];

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-green-600 flex items-center justify-center text-white font-bold text-xl shadow-sm">
              Ω
            </div>
            <div>
              <Link to="/" className="text-lg font-bold text-gray-900 leading-tight block">
                Multilingual PDF → HTML
              </Link>
              <span className="text-xs text-gray-500 font-medium">Local-First Document Platform</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex space-x-1 sm:space-x-3">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-green-50 text-green-700 font-semibold'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-1.5" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* Capabilities Badge */}
          <div className="hidden md:flex items-center space-x-2 text-xs text-gray-600 bg-gray-100 px-3 py-1.5 rounded-full border border-gray-200">
            <Cpu className="w-3.5 h-3.5 text-gray-500" />
            <span>
              {caps ? `${caps.platform.split('-')[0]} • ${caps.defaultConverter}` : 'Detecting hardware...'}
            </span>
            <CheckCircle2 className="w-3.5 h-3.5 text-green-500 ml-1" />
          </div>
        </div>
      </div>
    </header>
  );
};
