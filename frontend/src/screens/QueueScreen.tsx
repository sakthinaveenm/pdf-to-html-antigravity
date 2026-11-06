import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  RefreshCw,
  XCircle,
  RotateCcw,
  Eye,
  Edit,
  BookOpen,
  FileText,
  AlertCircle,
  Download,
  Trash2,
} from 'lucide-react';
import { api } from '../services/api';
import { Job } from '../types';

export const QueueScreen: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchJobs = () => {
    api.listJobs(1, 50)
      .then((data) => setJobs(data.items))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchJobs();
    // Live polling every 2 seconds for conversion progress
    const interval = setInterval(fetchJobs, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleCancel = async (jobId: string) => {
    try {
      await api.cancelJob(jobId);
      fetchJobs();
    } catch (err) {
      console.error(err);
    }
  };

  const handleRetry = async (jobId: string) => {
    try {
      await api.retryJob(jobId);
      fetchJobs();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteJob = async (job: Job) => {
    const confirmed = window.confirm(
      `Are you sure you want to permanently delete "${job.filename}" and any associated files?`
    );
    if (!confirmed) return;

    try {
      if (job.documentId) {
        await api.deleteDocument(job.documentId);
      } else {
        await api.deleteJob(job.id);
      }
      setJobs((prev) => prev.filter((j) => j.id !== job.id));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to delete.';
      alert(msg);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Conversion Queue</h1>
          <p className="text-sm text-gray-500 mt-1">
            Real-time status of document inspection, OCR extraction, normalization, and semantic generation.
          </p>
        </div>
        <button
          onClick={fetchJobs}
          className="inline-flex items-center px-3 py-1.5 rounded-lg border border-gray-200 bg-white text-gray-700 text-xs font-medium hover:bg-gray-50 shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1 text-gray-500" />
          Refresh
        </button>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {jobs.length === 0 && !loading ? (
          <div className="text-center py-16 text-gray-500">
            <FileText className="w-12 h-12 mx-auto text-gray-400 mb-3" />
            <p className="font-semibold text-gray-800">No jobs in queue</p>
            <p className="text-sm text-gray-400 mt-1">Upload PDF files to start processing.</p>
            <Link
              to="/upload"
              className="mt-4 inline-flex items-center px-4 py-2 rounded-lg bg-green-600 text-white text-sm font-medium hover:bg-green-700"
            >
              Upload PDFs
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50 text-gray-500">
                <tr>
                  <th className="px-6 py-3.5 text-left font-medium">Document</th>
                  <th className="px-6 py-3.5 text-left font-medium">Status & Step</th>
                  <th className="px-6 py-3.5 text-left font-medium">Engine / Languages</th>
                  <th className="px-6 py-3.5 text-left font-medium w-48">Progress</th>
                  <th className="px-6 py-3.5 text-right font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {jobs.map((job) => {
                  const isProcessing = ['INSPECTING', 'CONVERTING', 'OCR_PROCESSING', 'NORMALIZING', 'VALIDATING'].includes(job.status);
                  const isFailed = job.status === 'FAILED';
                  const isCompleted = job.status === 'COMPLETED';

                  return (
                    <tr key={job.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900 flex items-center">
                          <FileText className="w-4 h-4 mr-2 text-gray-400 flex-shrink-0" />
                          <span className="truncate max-w-xs">{job.filename}</span>
                        </div>
                        <div className="text-xs text-gray-400 mt-0.5">
                          {(job.fileSize / (1024 * 1024)).toFixed(2)} MB • ID: {job.id.slice(0, 8)}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${
                              isCompleted
                                ? 'bg-green-100 text-green-800'
                                : isFailed
                                ? 'bg-red-100 text-red-800'
                                : job.status === 'CANCELED'
                                ? 'bg-gray-100 text-gray-700'
                                : 'bg-blue-100 text-blue-800'
                            }`}
                          >
                            {isProcessing && <RefreshCw className="w-3 h-3 mr-1 animate-spin" />}
                            {job.status}
                          </span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1 truncate max-w-xs" title={job.currentStep}>
                          {job.currentStep}
                        </div>
                        {job.errorMessage && (
                          <div className="text-xs text-red-600 mt-1 flex items-center" title={job.errorMessage}>
                            <AlertCircle className="w-3 h-3 mr-1 flex-shrink-0" />
                            <span className="truncate max-w-xs">{job.errorMessage}</span>
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-xs font-semibold text-gray-800">{job.converter}</div>
                        <div className="text-xs text-gray-500 truncate max-w-[120px]" title={job.ocrLanguages}>
                          {job.ocrLanguages}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full transition-all duration-300 ${
                                isCompleted ? 'bg-green-600' : isFailed ? 'bg-red-500' : 'bg-blue-600'
                              }`}
                              style={{ width: `${job.progress}%` }}
                            />
                          </div>
                          <span className="text-xs font-medium text-gray-600 w-8">{job.progress}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right space-x-2 whitespace-nowrap">
                        {isProcessing && (
                          <button
                            onClick={() => handleCancel(job.id)}
                            className="inline-flex items-center px-2 py-1 text-xs text-red-600 hover:bg-red-50 rounded"
                            title="Cancel Job"
                          >
                            <XCircle className="w-4 h-4 mr-1" />
                            Cancel
                          </button>
                        )}
                        {(isFailed || job.status === 'CANCELED') && (
                          <button
                            onClick={() => handleRetry(job.id)}
                            className="inline-flex items-center px-2 py-1 text-xs text-blue-600 hover:bg-blue-50 rounded"
                            title="Retry Job"
                          >
                            <RotateCcw className="w-4 h-4 mr-1" />
                            Retry
                          </button>
                        )}
                        {isCompleted && (
                          <>
                            <Link
                              to={`/preview/${job.documentId}`}
                              className="inline-flex items-center px-2 py-1 text-xs text-gray-700 hover:text-green-600 hover:bg-gray-100 rounded"
                              title="Side-by-side Preview"
                            >
                              <Eye className="w-3.5 h-3.5 mr-1" />
                              Preview
                            </Link>
                            <Link
                              to={`/editor/${job.documentId}`}
                              className="inline-flex items-center px-2 py-1 text-xs text-gray-700 hover:text-blue-600 hover:bg-gray-100 rounded"
                              title="Edit HTML"
                            >
                              <Edit className="w-3.5 h-3.5 mr-1" />
                              Editor
                            </Link>
                            <Link
                              to={`/reader/${job.documentId}`}
                              className="inline-flex items-center px-2 py-1 text-xs text-gray-700 hover:text-purple-600 hover:bg-gray-100 rounded"
                              title="Reader Mode & Highlights"
                            >
                              <BookOpen className="w-3.5 h-3.5 mr-1" />
                              Reader
                            </Link>
                            <Link
                              to={`/export/${job.documentId}`}
                              className="inline-flex items-center p-1 text-gray-500 hover:text-gray-900 rounded"
                              title="Export ZIP"
                            >
                              <Download className="w-3.5 h-3.5" />
                            </Link>
                          </>
                        )}
                        <button
                          type="button"
                          onClick={() => handleDeleteJob(job)}
                          className="inline-flex items-center px-2 py-1 text-xs text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition"
                          title="Delete Document"
                        >
                          <Trash2 className="w-3.5 h-3.5 mr-1" />
                          Delete
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

