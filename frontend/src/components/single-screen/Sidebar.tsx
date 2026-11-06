import React from 'react';
import {
  ListOrdered,
  Upload,
  FolderOpen,
} from 'lucide-react';
import { SidebarDocuments } from './SidebarDocuments';
import { SidebarQueue } from './SidebarQueue';
import { SidebarUpload } from './SidebarUpload';
import { DocumentMeta, Job } from '../../types';

export type SidebarTab = 'documents' | 'queue' | 'upload';

interface SidebarProps {
  isOpen: boolean;
  activeTab: SidebarTab;
  onTabChange: (tab: SidebarTab) => void;
  documents: DocumentMeta[];
  jobs: Job[];
  activeDocumentId: string | null;
  onSelectDocument: (docId: string) => void;
  onDeleteDocument: (doc: DocumentMeta) => void;
  onCancelJob: (jobId: string) => void;
  onRetryJob: (jobId: string) => void;
  onDeleteJob: (job: Job) => void;
  onRefresh: () => void;
  refreshing: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  activeTab,
  onTabChange,
  documents,
  jobs,
  activeDocumentId,
  onSelectDocument,
  onDeleteDocument,
  onCancelJob,
  onRetryJob,
  onDeleteJob,
  onRefresh,
  refreshing,
}) => {
  if (!isOpen) return null;

  const activeJobs = jobs.filter((j) =>
    ['INSPECTING', 'CONVERTING', 'OCR_PROCESSING', 'NORMALIZING', 'VALIDATING', 'QUEUED'].includes(
      j.status
    )
  );

  return (
    <aside className="w-80 sm:w-88 md:w-96 flex-shrink-0 bg-white border-r border-gray-200 flex flex-col h-[calc(100vh-56px)] select-none">
      {/* Top Tab Bar */}
      <div className="flex border-b border-gray-200 bg-gray-50/70 p-1.5 gap-1 flex-shrink-0">
        <button
          onClick={() => onTabChange('documents')}
          className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold flex items-center justify-center space-x-1.5 transition ${
            activeTab === 'documents'
              ? 'bg-white text-green-800 shadow-xs'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100/60'
          }`}
        >
          <FolderOpen className="w-3.5 h-3.5" />
          <span>Documents</span>
          <span
            className={`text-[10px] px-1.5 py-0.2 rounded-full ${
              activeTab === 'documents'
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-200 text-gray-600'
            }`}
          >
            {documents.length}
          </span>
        </button>

        <button
          onClick={() => onTabChange('queue')}
          className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold flex items-center justify-center space-x-1.5 transition ${
            activeTab === 'queue'
              ? 'bg-white text-green-800 shadow-xs'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100/60'
          }`}
        >
          <ListOrdered className="w-3.5 h-3.5" />
          <span>Queue</span>
          {activeJobs.length > 0 && (
            <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-amber-100 text-amber-800 animate-pulse font-bold">
              {activeJobs.length}
            </span>
          )}
        </button>

        <button
          onClick={() => onTabChange('upload')}
          className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold flex items-center justify-center space-x-1.5 transition ${
            activeTab === 'upload'
              ? 'bg-white text-green-800 shadow-xs'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100/60'
          }`}
        >
          <Upload className="w-3.5 h-3.5" />
          <span>Upload</span>
        </button>
      </div>

      {/* Tab Body */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'documents' && (
          <SidebarDocuments
            documents={documents}
            activeDocumentId={activeDocumentId}
            onSelectDocument={onSelectDocument}
            onDeleteDocument={onDeleteDocument}
            onNewUploadClick={() => onTabChange('upload')}
          />
        )}

        {activeTab === 'queue' && (
          <SidebarQueue
            jobs={jobs}
            onSelectDocument={onSelectDocument}
            onCancelJob={onCancelJob}
            onRetryJob={onRetryJob}
            onDeleteJob={onDeleteJob}
            onRefresh={onRefresh}
            refreshing={refreshing}
          />
        )}

        {activeTab === 'upload' && (
          <SidebarUpload
            onUploadSuccess={() => {
              onRefresh();
              onTabChange('queue');
            }}
          />
        )}
      </div>
    </aside>
  );
};
