import React from 'react';
import {
  FileArchive,
  FileCode,
  FileText,
  CheckCircle2,
  Download,
  ExternalLink,
} from 'lucide-react';
import { DocumentMeta } from '../../types';
import { api } from '../../services/api';

interface ExportViewProps {
  documentId: string;
  docMeta: DocumentMeta;
}

export const ExportView: React.FC<ExportViewProps> = ({
  documentId,
  docMeta,
}) => {
  const exportZipUrl = api.getExportZipUrl(documentId);

  const exportCards = [
    {
      title: 'Complete Offline Bundle (ZIP)',
      desc: 'Self-contained archive with document.html, reader.css, embedded images, metadata, and quality report. Ready for offline deployment.',
      icon: FileArchive,
      actionText: 'Download ZIP Archive',
      href: exportZipUrl,
      primary: true,
      download: true,
    },
    {
      title: 'Semantic HTML5 Document',
      desc: 'Standalone HTML document with bundled CSS styles and real selectable text nodes.',
      icon: FileCode,
      actionText: 'Open HTML Document',
      href: `/api/v1/documents/${documentId}/html`,
      primary: false,
      download: false,
    },
    {
      title: 'Canonical Document Model (JSON AST)',
      desc: 'Versioned intermediate representation with block IDs, reading order, provenance, and table geometry.',
      icon: FileText,
      actionText: 'View JSON AST',
      href: `/api/v1/documents/${documentId}/ast`,
      primary: false,
      download: false,
    },
    {
      title: 'Verification Quality Report',
      desc: 'Complete validation report with text selectability scores, Unicode integrity checks, and structure analytics.',
      icon: CheckCircle2,
      actionText: 'View Quality Report',
      href: `/api/v1/documents/${documentId}/quality`,
      primary: false,
      download: false,
    },
  ];

  return (
    <div className="flex-1 overflow-y-auto p-6 sm:p-8 bg-gray-50 flex justify-center">
      <div className="max-w-4xl w-full space-y-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Export Document Deliverables</h2>
          <p className="text-xs text-gray-500 mt-1">
            Download self-contained offline archives, semantic HTML, or canonical JSON models for "{docMeta.title}".
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {exportCards.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.title}
                className={`p-6 rounded-2xl border transition shadow-2xs flex flex-col justify-between ${
                  card.primary
                    ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-300 ring-1 ring-green-600/10'
                    : 'bg-white border-gray-200 hover:border-gray-300'
                }`}
              >
                <div>
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 ${
                      card.primary ? 'bg-green-600 text-white shadow-sm' : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="text-sm font-bold text-gray-900 mb-1">{card.title}</h3>
                  <p className="text-xs text-gray-600 leading-relaxed mb-6">{card.desc}</p>
                </div>

                <a
                  href={card.href}
                  download={card.download}
                  target={card.download ? undefined : '_blank'}
                  rel="noreferrer"
                  className={`inline-flex items-center justify-center px-4 py-2 rounded-xl text-xs font-bold transition shadow-xs ${
                    card.primary
                      ? 'bg-green-600 hover:bg-green-700 text-white'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
                  }`}
                >
                  {card.download ? (
                    <Download className="w-3.5 h-3.5 mr-1.5" />
                  ) : (
                    <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
                  )}
                  <span>{card.actionText}</span>
                </a>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

