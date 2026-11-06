import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { SingleScreenWorkspace } from './screens/SingleScreenWorkspace';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SingleScreenWorkspace />} />
        <Route path="/upload" element={<SingleScreenWorkspace />} />
        <Route path="/queue" element={<SingleScreenWorkspace />} />
        <Route path="/preview/:documentId" element={<SingleScreenWorkspace />} />
        <Route path="/editor/:documentId" element={<SingleScreenWorkspace />} />
        <Route path="/reader/:documentId" element={<SingleScreenWorkspace />} />
        <Route path="/export/:documentId" element={<SingleScreenWorkspace />} />
        <Route path="*" element={<SingleScreenWorkspace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;

