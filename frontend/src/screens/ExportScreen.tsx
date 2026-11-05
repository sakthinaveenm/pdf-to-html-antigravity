import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Download, FileArchive, FileCode, FileText, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { DocumentMeta } from '../types';

export const ExportScreen: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const [docMeta, setDocMeta] = useState<DocumentMeta | null>(null);

  useEffect(() => {
    if (documentId) {
      api.getDocument(documentId).then(setDocMeta).catch(console.error);
    }
  }, [documentId]);

  if (!documentId) return null;

  const exportZipUrl = api.getExportZipUrl(documentId);

  const exportCards = [
    {
      title: 'Complete Offline Bundle (ZIP)',
      desc: 'Self-contained archive with document.html, reader.css, embedded images, metadata, and quality report. Ready for offline deployment.',
      icon: FileArchive,
      actionText: 'Download ZIP',
      href: exportZipUrl,
      primary: true,
    },
    {
      title: 'Semantic HTML5 Document',
      desc: 'Standalone HTML document with bundled CSS styles and real selectable text nodes.',
      icon: FileCode,
      actionText: 'Open HTML',
      href: `/api/v1/documents/${documentId}/html`,
      primary: false,
    },
    {
      title: 'Canonical Document Model (JSON AST)',
      desc: 'Versioned intermediate representation with block IDs, reading order, provenance, and table geometry.',
      icon: FileText,
      actionText: 'View JSON AST',
      href: `/api/v1/documents/${documentId}/ast`,
      primary: false,
    },
    {
      title: 'Verification Quality Report',
      desc: 'Complete validation report with text selectability scores, Unicode integrity checks, and structure analytics.',
      icon: CheckCircle2,
      actionText: 'View Quality JSON',
      href: `/api/v1/documents/${documentId}/quality`,
      primary: false,
    },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center space-x-3">
        <Link
          to={`/preview/${documentId}`}
          className="p-1.5 rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-100"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Export Document Files</h1>
          <p className="text-sm text-gray-500 mt-1">
            {docMeta?.title} ({docMeta?.filename})
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {exportCards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.title}
              className={`p-6 rounded-2xl border transition shadow-sm flex flex-col justify-between ${
                card.primary
                  ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-200 ring-1 ring-green-600/10'
                  : 'bg-white border-gray-200 hover:border-gray-300'
              }`}
            >
              <div>
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 ${
                    card.primary ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-gray-900 mb-1">{card.title}</h3>
                <p className="text-xs text-gray-600 leading-relaxed mb-6">{card.desc}</p>
              </div>

              <a
                href={card.href}
                download={card.primary}
                target={card.primary ? undefined : '_blank'}
                rel="noreferrer"
                className={`inline-flex items-center justify-center py-2.5 px-4 rounded-xl text-xs font-semibold shadow-xs transition ${
                  card.primary
                    ? 'bg-green-600 text-white hover:bg-green-700'
                    : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                }`}
              >
                <Download className="w-4 h-4 mr-1.5" />
                {card.actionText}
              </a>
            </div>
          );
        })}
      </div>
    </div>
  );
};
