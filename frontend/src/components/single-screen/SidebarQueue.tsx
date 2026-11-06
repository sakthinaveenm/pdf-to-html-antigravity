import React from 'react';
import {
  RefreshCw,
  XCircle,
  RotateCcw,
  Trash2,
  CheckCircle2,
  AlertCircle,
  FileText,
  Clock,
  ArrowRight,
} from 'lucide-react';
import { Job } from '../../types';

interface SidebarQueueProps {
  jobs: Job[];
  onSelectDocument: (docId: string) => void;
  onCancelJob: (jobId: string) => void;
  onRetryJob: (jobId: string) => void;
  onDeleteJob: (job: Job) => void;
  onRefresh: () => void;
  refreshing: boolean;
}

export const SidebarQueue: React.FC<SidebarQueueProps> = ({
  jobs,
  onSelectDocument,
  onCancelJob,
  onRetryJob,
  onDeleteJob,
  onRefresh,
  refreshing,
}) => {
  const getStatusBadge = (status: Job['status']) => {
    switch (status) {
      case 'QUEUED':
        return (
          <span className="inline-flex items-center text-[10px] font-semibold text-yellow-700 bg-yellow-50 px-2 py-0.5 rounded-full border border-yellow-200">
            <Clock className="w-2.5 h-2.5 mr-1" />
            Queued
          </span>
        );
      case 'INSPECTING':
      case 'CONVERTING':
      case 'OCR_PROCESSING':
      case 'NORMALIZING':
      case 'VALIDATING':
        return (
          <span className="inline-flex items-center text-[10px] font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-200">
            <RefreshCw className="w-2.5 h-2.5 mr-1 animate-spin" />
            {status.replace('_', ' ')}
          </span>
        );
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center text-[10px] font-semibold text-green-700 bg-green-50 px-2 py-0.5 rounded-full border border-green-200">
            <CheckCircle2 className="w-2.5 h-2.5 mr-1" />
            Completed
          </span>
        );
      case 'FAILED':
        return (
          <span className="inline-flex items-center text-[10px] font-semibold text-red-700 bg-red-50 px-2 py-0.5 rounded-full border border-red-200">
            <AlertCircle className="w-2.5 h-2.5 mr-1" />
            Failed
          </span>
        );
      case 'CANCELED':
        return (
          <span className="inline-flex items-center text-[10px] font-semibold text-gray-600 bg-gray-100 px-2 py-0.5 rounded-full border border-gray-200">
            Canceled
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header with refresh */}
      <div className="p-3 border-b border-gray-100 flex items-center justify-between flex-shrink-0">
        <span className="text-xs font-semibold text-gray-700">
          Conversion Pipeline ({jobs.length})
        </span>
        <button
          onClick={onRefresh}
          disabled={refreshing}
          className="text-gray-400 hover:text-gray-600 p-1 rounded"
          title="Refresh Queue"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin text-green-600' : ''}`} />
        </button>
      </div>

      {/* Queue items */}
      <div className="flex-1 overflow-y-auto divide-y divide-gray-100 p-2 space-y-2">
        {jobs.length === 0 ? (
          <div className="text-center py-10 px-4 text-gray-400">
            <FileText className="w-8 h-8 mx-auto text-gray-300 mb-2" />
            <p className="text-xs font-medium text-gray-600">No jobs in queue</p>
            <p className="text-[11px] text-gray-400 mt-1">
              Upload a document to see live conversion status
            </p>
          </div>
        ) : (
          jobs.map((job) => {
            const isProcessing = [
              'INSPECTING',
              'CONVERTING',
              'OCR_PROCESSING',
              'NORMALIZING',
              'VALIDATING',
            ].includes(job.status);
            const isFailed = job.status === 'FAILED';
            const isCompleted = job.status === 'COMPLETED';

            return (
              <div
                key={job.id}
                className="bg-white border border-gray-200 rounded-xl p-3 shadow-xs space-y-2"
              >
                <div className="flex items-start justify-between">
                  <div className="min-w-0 flex-1 pr-2">
                    <h5 className="text-xs font-semibold text-gray-900 truncate" title={job.filename}>
                      {job.filename}
                    </h5>
                    <div className="flex items-center space-x-1.5 mt-1">
                      {getStatusBadge(job.status)}
                      <span className="text-[10px] text-gray-400 uppercase font-mono">
                        {job.converter}
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-1">
                    {isProcessing && (
                      <button
                        onClick={() => onCancelJob(job.id)}
                        title="Cancel conversion"
                        className="p-1 rounded text-gray-400 hover:text-red-600 hover:bg-red-50"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                      </button>
                    )}
                    {isFailed && (
                      <button
                        onClick={() => onRetryJob(job.id)}
                        title="Retry job"
                        className="p-1 rounded text-gray-400 hover:text-indigo-600 hover:bg-indigo-50"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                      </button>
                    )}
                    <button
                      onClick={() => onDeleteJob(job)}
                      title="Delete job and associated files"
                      className="p-1 rounded text-gray-400 hover:text-red-600 hover:bg-red-50"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                {/* Progress bar */}
                {(isProcessing || isCompleted) && (
                  <div>
                    <div className="flex justify-between text-[10px] text-gray-500 mb-1">
                      <span>{job.currentStep || 'Processing...'}</span>
                      <span className="font-semibold">{job.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                      <div
                        className={`h-1.5 rounded-full transition-all duration-300 ${
                          isCompleted
                            ? 'bg-green-500'
                            : 'bg-indigo-600 animate-pulse'
                        }`}
                        style={{ width: `${job.progress}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Error message */}
                {isFailed && job.errorMessage && (
                  <div className="text-[11px] text-red-600 bg-red-50 p-2 rounded-lg break-words">
                    {job.errorMessage}
                  </div>
                )}

                {/* Completed - View link */}
                {isCompleted && job.documentId && (
                  <button
                    onClick={() => onSelectDocument(job.documentId!)}
                    className="w-full flex items-center justify-center space-x-1 text-[11px] text-green-700 font-semibold bg-green-50 hover:bg-green-100 py-1.5 rounded-lg transition"
                  >
                    <span>Open in Studio</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
