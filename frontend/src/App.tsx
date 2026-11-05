import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { DashboardScreen } from './screens/DashboardScreen';
import { UploadScreen } from './screens/UploadScreen';
import { QueueScreen } from './screens/QueueScreen';
import { DocumentPreviewScreen } from './screens/DocumentPreviewScreen';
import { EditorScreen } from './screens/EditorScreen';
import { ReaderScreen } from './screens/ReaderScreen';
import { ExportScreen } from './screens/ExportScreen';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<DashboardScreen />} />
            <Route path="/upload" element={<UploadScreen />} />
            <Route path="/queue" element={<QueueScreen />} />
            <Route path="/preview/:documentId" element={<DocumentPreviewScreen />} />
            <Route path="/editor/:documentId" element={<EditorScreen />} />
            <Route path="/reader/:documentId" element={<ReaderScreen />} />
            <Route path="/export/:documentId" element={<ExportScreen />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;

