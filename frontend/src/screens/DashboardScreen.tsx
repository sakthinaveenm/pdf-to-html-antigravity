import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  Clock,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Upload,
  ArrowRight,
  Eye,
  Edit,
  BookOpen,
  Download,
} from 'lucide-react';
import { api } from '../services/api';
import { Job, SystemCapabilities } from '../types';

export const DashboardScreen: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [caps, setCaps] = useState<SystemCapabilities | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.listJobs(1, 100),
      api.getCapabilities(),
    ])
      .then(([jobsData, capsData]) => {
        setJobs(jobsData.items);
        setCaps(capsData);
      })
      .finally(() => setLoading(false));
  }, []);

  const total = jobs.length;
  const pending = jobs.filter((j) => j.status === 'QUEUED').length;
  const processing = jobs.filter((j) =>
    ['INSPECTING', 'CONVERTING', 'OCR_PROCESSING', 'NORMALIZING', 'VALIDATING'].includes(j.status)
  ).length;
  const completed = jobs.filter((j) => j.status === 'COMPLETED').length;
  const failed = jobs.filter((j) => j.status === 'FAILED').length;

  const cards = [
    { label: 'Total Documents', value: total, icon: FileText, color: 'bg-blue-500' },
    { label: 'Pending Queue', value: pending, icon: Clock, color: 'bg-yellow-500' },
    { label: 'Processing', value: processing, icon: RefreshCw, color: 'bg-indigo-500' },
    { label: 'Completed', value: completed, icon: CheckCircle, color: 'bg-green-500' },
    { label: 'Failed', value: failed, icon: AlertTriangle, color: 'bg-red-500' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-green-700 to-emerald-800 rounded-2xl p-6 sm:p-8 text-white shadow-md flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Multilingual PDF to HTML Platform</h1>
          <p className="mt-2 text-green-100 max-w-2xl text-sm sm:text-base">
            Local-first conversion of multi-page multilingual PDFs into clean, semantic, selectable, and durable HTML with full Indic, Arabic RTL, and CJK language support.
          </p>
        </div>
        <Link
          to="/upload"
          className="inline-flex items-center px-5 py-2.5 rounded-xl bg-white text-green-800 font-semibold text-sm shadow hover:bg-green-50 transition"
        >
          <Upload className="w-4 h-4 mr-2" />
          Batch Upload PDFs
        </Link>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        {cards.map((c) => {
          const Icon = c.icon;
          return (
            <div key={c.label} className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-500 uppercase">{c.label}</span>
                <div className={`w-8 h-8 rounded-lg ${c.color} text-white flex items-center justify-center`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3 text-2xl font-bold text-gray-900">{loading ? '...' : c.value}</div>
            </div>
          );
        })}
      </div>

      {/* Hardware & OCR Engine Status Card */}
      {caps && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center">
            <span className="w-2.5 h-2.5 rounded-full bg-green-500 mr-2"></span>
            Hardware & Local Engine Environment
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
            <div className="space-y-1">
              <span className="text-gray-500 block text-xs">Host Machine & CPU</span>
              <p className="font-medium text-gray-800">{caps.platform}</p>
              <p className="text-xs text-gray-600">{caps.cpuCount} Cores • {caps.totalRamGb} GB RAM</p>
            </div>
            <div className="space-y-1">
              <span className="text-gray-500 block text-xs">Installed Document Converters</span>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {caps.converters.map((cv) => (
                  <span
                    key={cv.name}
                    className={`px-2 py-0.5 rounded text-xs font-semibold ${
                      cv.available ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {cv.name} {cv.version ? `v${cv.version}` : ''}
                  </span>
                ))}
              </div>
            </div>
            <div className="space-y-1">
              <span className="text-gray-500 block text-xs">Tesseract OCR Language Packs</span>
              <p className="font-medium text-gray-800">{caps.installedOcrLanguages.length} Languages Installed</p>
              <p className="text-xs text-gray-600 truncate">
                {caps.installedOcrLanguages.slice(0, 10).join(', ')}...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Recent Conversions Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-900">Recent Conversion Jobs</h2>
          <Link to="/queue" className="text-sm font-medium text-green-600 hover:text-green-700 flex items-center">
            View all in Queue <ArrowRight className="w-4 h-4 ml-1" />
          </Link>
        </div>

        {jobs.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <FileText className="w-12 h-12 mx-auto text-gray-400 mb-3" />
            <p className="font-medium">No documents processed yet.</p>
            <p className="text-sm text-gray-400 mt-1">Upload PDF files to start converting.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50 text-gray-500">
                <tr>
                  <th className="px-6 py-3 text-left font-medium">Filename</th>
                  <th className="px-6 py-3 text-left font-medium">Status</th>
                  <th className="px-6 py-3 text-left font-medium">Engine</th>
                  <th className="px-6 py-3 text-left font-medium">OCR Languages</th>
                  <th className="px-6 py-3 text-right font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {jobs.slice(0, 8).map((job) => (
                  <tr key={job.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900 flex items-center">
                      <FileText className="w-4 h-4 mr-2 text-gray-400" />
                      {job.filename}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          job.status === 'COMPLETED'
                            ? 'bg-green-100 text-green-800'
                            : job.status === 'FAILED'
                            ? 'bg-red-100 text-red-800'
                            : job.status === 'CANCELED'
                            ? 'bg-gray-100 text-gray-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {job.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-600">{job.converter}</td>
                    <td className="px-6 py-4 text-gray-600">{job.ocrLanguages}</td>
                    <td className="px-6 py-4 text-right space-x-2">
                      {job.status === 'COMPLETED' && (
                        <>
                          <Link
                            to={`/preview/${job.documentId}`}
                            className="inline-flex items-center p-1.5 text-gray-600 hover:text-green-600 hover:bg-gray-100 rounded"
                            title="Side-by-side Preview"
                          >
                            <Eye className="w-4 h-4" />
                          </Link>
                          <Link
                            to={`/editor/${job.documentId}`}
                            className="inline-flex items-center p-1.5 text-gray-600 hover:text-blue-600 hover:bg-gray-100 rounded"
                            title="HTML Editor"
                          >
                            <Edit className="w-4 h-4" />
                          </Link>
                          <Link
                            to={`/reader/${job.documentId}`}
                            className="inline-flex items-center p-1.5 text-gray-600 hover:text-purple-600 hover:bg-gray-100 rounded"
                            title="Interactive Reader & Highlights"
                          >
                            <BookOpen className="w-4 h-4" />
                          </Link>
                          <Link
                            to={`/export/${job.documentId}`}
                            className="inline-flex items-center p-1.5 text-gray-600 hover:text-emerald-600 hover:bg-gray-100 rounded"
                            title="Export Bundle"
                          >
                            <Download className="w-4 h-4" />
                          </Link>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
