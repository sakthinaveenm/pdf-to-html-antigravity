import React, { useState } from 'react';
import {
  FileText,
  Search,
  Trash2,
  ChevronRight,
} from 'lucide-react';
import { DocumentMeta } from '../../types';

interface SidebarDocumentsProps {
  documents: DocumentMeta[];
  activeDocumentId: string | null;
  onSelectDocument: (docId: string) => void;
  onDeleteDocument: (doc: DocumentMeta) => void;
  onNewUploadClick: () => void;
}

export const SidebarDocuments: React.FC<SidebarDocumentsProps> = ({
  documents,
  activeDocumentId,
  onSelectDocument,
  onDeleteDocument,
  onNewUploadClick,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredDocs = documents.filter((doc) => {
    const q = searchQuery.toLowerCase();
    return (
      doc.title.toLowerCase().includes(q) ||
      doc.filename.toLowerCase().includes(q) ||
      (doc.language && doc.language.toLowerCase().includes(q))
    );
  });

  return (
    <div className="flex flex-col h-full">
      {/* Search Bar */}
      <div className="p-3 border-b border-gray-100 flex-shrink-0">
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-gray-400 absolute left-2.5 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documents or language..."
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-green-500 focus:bg-white transition"
          />
        </div>
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-y-auto divide-y divide-gray-100 p-2 space-y-1">
        {filteredDocs.length === 0 ? (
          <div className="text-center py-10 px-4 text-gray-400">
            <FileText className="w-8 h-8 mx-auto text-gray-300 mb-2" />
            <p className="text-xs font-medium text-gray-600">
              {documents.length === 0 ? 'No documents converted' : 'No matching documents'}
            </p>
            <p className="text-[11px] text-gray-400 mt-1">
              {documents.length === 0
                ? 'Upload your first PDF to generate semantic HTML'
                : 'Try adjusting your search terms'}
            </p>
            {documents.length === 0 && (
              <button
                onClick={onNewUploadClick}
                className="mt-3 inline-flex items-center px-3 py-1.5 rounded-lg bg-green-50 text-green-700 text-xs font-semibold hover:bg-green-100 transition"
              >
                Upload PDF
              </button>
            )}
          </div>
        ) : (
          filteredDocs.map((doc) => {
            const isActive = doc.id === activeDocumentId;
            return (
              <div
                key={doc.id}
                onClick={() => onSelectDocument(doc.id)}
                className={`group relative rounded-xl p-2.5 cursor-pointer transition border ${
                  isActive
                    ? 'bg-green-50/70 border-green-300 shadow-xs'
                    : 'bg-white hover:bg-gray-50/80 border-transparent hover:border-gray-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="min-w-0 flex-1 pr-2">
                    <div className="flex items-center space-x-1.5">
                      <span
                        className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                          isActive ? 'bg-green-600' : 'bg-gray-300'
                        }`}
                      />
                      <h4
                        className={`text-xs font-semibold truncate ${
                          isActive ? 'text-green-950' : 'text-gray-800'
                        }`}
                        title={doc.title}
                      >
                        {doc.title}
                      </h4>
                    </div>

                    <p className="text-[11px] text-gray-500 truncate mt-0.5 ml-3">
                      {doc.filename}
                    </p>

                    <div className="flex items-center space-x-1.5 mt-2 ml-3">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-700 uppercase">
                        {doc.language || 'DOC'}
                      </span>
                      <span className="text-[10px] text-gray-400">
                        {doc.pageCount} {doc.pageCount === 1 ? 'page' : 'pages'}
                      </span>
                      <span className="text-[10px] text-gray-400">•</span>
                      <span className="text-[10px] text-gray-400">
                        r#{doc.currentRevision}
                      </span>
                    </div>
                  </div>

                  {/* Actions: Delete button */}
                  <div className="flex items-center space-x-1 flex-shrink-0">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteDocument(doc);
                      }}
                      title="Permanently delete document"
                      className="p-1 rounded text-gray-400 hover:text-red-600 hover:bg-red-50 transition opacity-0 group-hover:opacity-100 focus:opacity-100"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                    <ChevronRight
                      className={`w-4 h-4 transition ${
                        isActive ? 'text-green-600' : 'text-gray-300 group-hover:text-gray-400'
                      }`}
                    />
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
