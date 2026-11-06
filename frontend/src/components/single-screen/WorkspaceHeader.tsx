import React from 'react';
import {
  FileText,
  Upload,
  RefreshCw,
  Cpu,
  PanelLeftClose,
  PanelLeft,
  ChevronDown,
} from 'lucide-react';
import { DocumentMeta, SystemCapabilities } from '../../types';

interface WorkspaceHeaderProps {
  documents: DocumentMeta[];
  activeDocumentId: string | null;
  onSelectDocument: (docId: string) => void;
  activeJobsCount: number;
  caps: SystemCapabilities | null;
  onToggleSidebar: () => void;
  isSidebarOpen: boolean;
  onOpenUpload: () => void;
  onRefresh: () => void;
  refreshing: boolean;
}

export const WorkspaceHeader: React.FC<WorkspaceHeaderProps> = ({
  documents,
  activeDocumentId,
  onSelectDocument,
  activeJobsCount,
  caps,
  onToggleSidebar,
  isSidebarOpen,
  onOpenUpload,
  onRefresh,
  refreshing,
}) => {
  const activeDoc = documents.find((d) => d.id === activeDocumentId);

  return (
    <header className="h-14 bg-white border-b border-gray-200 px-3 sm:px-4 flex items-center justify-between flex-shrink-0 z-30 select-none">
      {/* Left side: Toggle Sidebar + Brand + Document Selector */}
      <div className="flex items-center space-x-2 sm:space-x-3 min-w-0">
        <button
          onClick={onToggleSidebar}
          title={isSidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          className="p-1.5 rounded-lg text-gray-500 hover:text-gray-900 hover:bg-gray-100 transition"
        >
          {isSidebarOpen ? <PanelLeftClose className="w-5 h-5" /> : <PanelLeft className="w-5 h-5 text-green-700" />}
        </button>

        {/* Brand */}
        <div className="flex items-center space-x-2 flex-shrink-0">
          <div className="w-8 h-8 rounded-lg bg-green-600 flex items-center justify-center text-white font-bold text-base shadow-sm">
            Ω
          </div>
          <div className="hidden md:block">
            <span className="font-bold text-gray-900 text-sm leading-none block">
              Multilingual PDF → HTML
            </span>
            <span className="text-[10px] text-gray-500 font-medium">Single-Screen Studio</span>
          </div>
        </div>

        {/* Divider */}
        <div className="h-5 w-px bg-gray-200 hidden sm:block" />

        {/* Quick Document Switcher Dropdown */}
        <div className="relative group max-w-xs sm:max-w-sm">
          <div className="flex items-center bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg px-2.5 py-1 text-xs cursor-pointer transition">
            <FileText className="w-3.5 h-3.5 text-green-600 mr-1.5 flex-shrink-0" />
            <span className="font-medium text-gray-800 truncate max-w-[140px] sm:max-w-[200px]">
              {activeDoc ? activeDoc.title : 'Select document...'}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-gray-400 ml-1.5 flex-shrink-0" />
          </div>

          {/* Dropdown Menu */}
          <div className="absolute left-0 mt-1 w-64 bg-white border border-gray-200 rounded-xl shadow-lg py-1 hidden group-hover:block z-50 max-h-72 overflow-y-auto">
            <div className="px-3 py-1.5 text-[11px] font-semibold text-gray-400 uppercase tracking-wider border-b border-gray-100">
              Loaded Documents ({documents.length})
            </div>
            {documents.length === 0 ? (
              <div className="px-3 py-2 text-xs text-gray-400">No documents converted yet</div>
            ) : (
              documents.map((doc) => (
                <button
                  key={doc.id}
                  onClick={() => onSelectDocument(doc.id)}
                  className={`w-full text-left px-3 py-1.5 text-xs flex items-center justify-between hover:bg-green-50 ${
                    doc.id === activeDocumentId ? 'bg-green-50/80 font-semibold text-green-800' : 'text-gray-700'
                  }`}
                >
                  <span className="truncate mr-2">{doc.title}</span>
                  <span className="text-[10px] text-gray-400 uppercase flex-shrink-0">
                    {doc.language || 'DOC'}
                  </span>
                </button>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Right side: Active Jobs + System Status + Upload Button + Refresh */}
      <div className="flex items-center space-x-2 sm:space-x-3 flex-shrink-0">
        {/* Active Jobs Pill */}
        {activeJobsCount > 0 ? (
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-xs font-medium animate-pulse">
            <RefreshCw className="w-3 h-3 animate-spin text-amber-600" />
            <span>{activeJobsCount} processing</span>
          </div>
        ) : (
          <div className="hidden lg:flex items-center space-x-1 text-xs text-gray-500 bg-gray-50 px-2 py-0.5 rounded-full border border-gray-200">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 inline-block mr-1"></span>
            <span>Idle</span>
          </div>
        )}

        {/* Hardware badge */}
        {caps && (
          <div className="hidden xl:flex items-center space-x-1.5 text-[11px] text-gray-600 bg-gray-100 px-2.5 py-1 rounded-full border border-gray-200">
            <Cpu className="w-3 h-3 text-gray-500" />
            <span className="truncate max-w-[150px]">
              {caps.defaultConverter} • {caps.platform.split('-')[0]}
            </span>
          </div>
        )}

        {/* Refresh button */}
        <button
          onClick={onRefresh}
          disabled={refreshing}
          title="Refresh documents and queue"
          className="p-1.5 rounded-lg text-gray-500 hover:text-gray-800 hover:bg-gray-100 border border-gray-200 transition"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-green-600' : ''}`} />
        </button>

        {/* + Upload PDF Button */}
        <button
          onClick={onOpenUpload}
          className="inline-flex items-center px-3 py-1.5 rounded-lg bg-green-600 hover:bg-green-700 text-white text-xs font-semibold shadow-sm transition"
        >
          <Upload className="w-3.5 h-3.5 mr-1.5" />
          <span>Upload PDF</span>
        </button>
      </div>
    </header>
  );
};
