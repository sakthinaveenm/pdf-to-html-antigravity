import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { api } from '../services/api';
import { DocumentMeta, Job, SystemCapabilities } from '../types';
import { WorkspaceHeader } from '../components/single-screen/WorkspaceHeader';
import { Sidebar, SidebarTab } from '../components/single-screen/Sidebar';
import { DocumentWorkspace, StudioTab } from '../components/single-screen/DocumentWorkspace';
import { EmptyWorkspace } from '../components/single-screen/EmptyWorkspace';

export const SingleScreenWorkspace: React.FC = () => {
  const { documentId: routeDocId } = useParams<{ documentId?: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  const [documents, setDocuments] = useState<DocumentMeta[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [caps, setCaps] = useState<SystemCapabilities | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  // Layout State
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [sidebarTab, setSidebarTab] = useState<SidebarTab>('documents');
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(routeDocId || null);
  const [studioTab, setStudioTab] = useState<StudioTab>('split');

  // Detect route type on initial mount or route change
  useEffect(() => {
    const path = location.pathname;
    if (path.startsWith('/upload')) {
      setSidebarTab('upload');
      setIsSidebarOpen(true);
    } else if (path.startsWith('/queue')) {
      setSidebarTab('queue');
      setIsSidebarOpen(true);
    } else if (path.startsWith('/editor/') && routeDocId) {
      setActiveDocumentId(routeDocId);
      setStudioTab('editor');
    } else if (path.startsWith('/reader/') && routeDocId) {
      setActiveDocumentId(routeDocId);
      setStudioTab('reader');
    } else if (path.startsWith('/export/') && routeDocId) {
      setActiveDocumentId(routeDocId);
      setStudioTab('export');
    } else if (path.startsWith('/preview/') && routeDocId) {
      setActiveDocumentId(routeDocId);
      setStudioTab('split');
    } else if (routeDocId) {
      setActiveDocumentId(routeDocId);
    }
  }, [location.pathname, routeDocId]);

  // Fetch initial documents and capabilities
  const fetchAllData = useCallback(async () => {
    setRefreshing(true);
    try {
      const [docsRes, jobsRes, capsRes] = await Promise.all([
        api.listDocuments(1, 100),
        api.listJobs(1, 50),
        api.getCapabilities().catch(() => null),
      ]);

      setDocuments(docsRes.items);
      setJobs(jobsRes.items);
      if (capsRes) setCaps(capsRes);

      // Auto-select latest document if none selected
      if (!activeDocumentId && docsRes.items.length > 0) {
        setActiveDocumentId(docsRes.items[0].id);
      }
    } catch (err) {
      console.error('Error fetching workspace data:', err);
    } finally {
      setRefreshing(false);
    }
  }, [activeDocumentId]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Periodic polling for conversion queue progress
  useEffect(() => {
    const pollInterval = setInterval(() => {
      api.listJobs(1, 50)
        .then((jobsRes) => {
          setJobs(jobsRes.items);
          // If a job just completed and we have no document selected, refresh documents
          const hasRunning = jobsRes.items.some((j) =>
            ['INSPECTING', 'CONVERTING', 'OCR_PROCESSING', 'NORMALIZING', 'VALIDATING'].includes(j.status)
          );
          if (hasRunning) {
            api.listDocuments(1, 100).then((docsRes) => setDocuments(docsRes.items));
          }
        })
        .catch(() => null);
    }, 2500);

    return () => clearInterval(pollInterval);
  }, []);

  const handleSelectDocument = (docId: string) => {
    setActiveDocumentId(docId);
    navigate(`/preview/${docId}`, { replace: true });
  };

  const handleDeleteDocument = async (doc: DocumentMeta) => {
    const confirmed = window.confirm(
      `Permanently delete "${doc.title}"?\n\nThis removes the document, HTML, highlights, and original PDF.`
    );
    if (!confirmed) return;

    try {
      await api.deleteDocument(doc.id);
      setDocuments((prev) => prev.filter((d) => d.id !== doc.id));
      setJobs((prev) => prev.filter((j) => j.documentId !== doc.id));
      if (activeDocumentId === doc.id) {
        const remaining = documents.filter((d) => d.id !== doc.id);
        if (remaining.length > 0) {
          setActiveDocumentId(remaining[0].id);
          navigate(`/preview/${remaining[0].id}`, { replace: true });
        } else {
          setActiveDocumentId(null);
          navigate('/', { replace: true });
        }
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to delete document.';
      alert(msg);
    }
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      await api.cancelJob(jobId);
      const jobsRes = await api.listJobs(1, 50);
      setJobs(jobsRes.items);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRetryJob = async (jobId: string) => {
    try {
      await api.retryJob(jobId);
      const jobsRes = await api.listJobs(1, 50);
      setJobs(jobsRes.items);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteJob = async (job: Job) => {
    const confirmed = window.confirm(
      `Delete job "${job.filename}"?`
    );
    if (!confirmed) return;

    try {
      if (job.documentId) {
        await api.deleteDocument(job.documentId);
        setDocuments((prev) => prev.filter((d) => d.id !== job.documentId));
        if (activeDocumentId === job.documentId) {
          setActiveDocumentId(null);
        }
      } else {
        await api.deleteJob(job.id);
      }
      setJobs((prev) => prev.filter((j) => j.id !== job.id));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to delete job.';
      alert(msg);
    }
  };

  const activeJobsCount = jobs.filter((j) =>
    ['INSPECTING', 'CONVERTING', 'OCR_PROCESSING', 'NORMALIZING', 'VALIDATING'].includes(j.status)
  ).length;

  return (
    <div className="h-screen w-screen overflow-hidden flex flex-col bg-gray-50 font-sans">
      {/* Top Workspace Header */}
      <WorkspaceHeader
        documents={documents}
        activeDocumentId={activeDocumentId}
        onSelectDocument={handleSelectDocument}
        activeJobsCount={activeJobsCount}
        caps={caps}
        onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
        isSidebarOpen={isSidebarOpen}
        onOpenUpload={() => {
          setIsSidebarOpen(true);
          setSidebarTab('upload');
        }}
        onRefresh={fetchAllData}
        refreshing={refreshing}
      />

      {/* Main Single-Screen Workspace Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar
          isOpen={isSidebarOpen}
          activeTab={sidebarTab}
          onTabChange={setSidebarTab}
          documents={documents}
          jobs={jobs}
          activeDocumentId={activeDocumentId}
          onSelectDocument={handleSelectDocument}
          onDeleteDocument={handleDeleteDocument}
          onCancelJob={handleCancelJob}
          onRetryJob={handleRetryJob}
          onDeleteJob={handleDeleteJob}
          onRefresh={fetchAllData}
          refreshing={refreshing}
        />

        {/* Right Main Studio Area */}
        <main className="flex-1 flex overflow-hidden">
          {activeDocumentId ? (
            <DocumentWorkspace
              key={activeDocumentId}
              documentId={activeDocumentId}
              initialTab={studioTab}
              onDeleteDocument={handleDeleteDocument}
            />
          ) : (
            <EmptyWorkspace
              documents={documents}
              caps={caps}
              onSelectDocument={handleSelectDocument}
              onOpenUpload={() => {
                setIsSidebarOpen(true);
                setSidebarTab('upload');
              }}
            />
          )}
        </main>
      </div>
    </div>
  );
};

