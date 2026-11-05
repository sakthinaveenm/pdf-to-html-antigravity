import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Table from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import Image from '@tiptap/extension-image';
import {
  Bold,
  Italic,
  Heading1,
  Heading2,
  Heading3,
  List,
  ListOrdered,
  Undo,
  Redo,
  Table as TableIcon,
  Save,
  Code,
  AlertTriangle,
  ArrowLeft,
  Check,
} from 'lucide-react';
import { api } from '../services/api';
import { DocumentMeta } from '../types';

export const EditorScreen: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const [docMeta, setDocMeta] = useState<DocumentMeta | null>(null);
  const [rawSource, setRawSource] = useState<string>('');
  const [isSourceMode, setIsSourceMode] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const editor = useEditor({
    extensions: [
      StarterKit,
      Table.configure({ resizable: true }),
      TableRow,
      TableHeader,
      TableCell,
      Image,
    ],
    content: '<p>Loading document content...</p>',
  });

  useEffect(() => {
    if (!documentId) return;

    Promise.all([
      api.getDocument(documentId),
      api.getDocumentHtml(documentId),
    ]).then(([meta, html]) => {
      setDocMeta(meta);
      setRawSource(html);
      if (editor) {
        editor.commands.setContent(html);
      }
    });
  }, [documentId, editor]);

  const handleSave = async () => {
    if (!documentId) return;
    setSaving(true);
    setSavedSuccess(false);

    const htmlToSave = isSourceMode ? rawSource : (editor?.getHTML() || '');

    try {
      const res = await api.saveRevision(documentId, htmlToSave, 'Edited in TipTap HTML editor');
      if (docMeta) {
        setDocMeta({ ...docMeta, currentRevision: res.revisionNumber });
      }
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to save revision:', err);
    } finally {
      setSaving(false);
    }
  };

  const toggleSourceMode = () => {
    if (!isSourceMode && editor) {
      setRawSource(editor.getHTML());
    } else if (isSourceMode && editor) {
      editor.commands.setContent(rawSource);
    }
    setIsSourceMode(!isSourceMode);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 space-y-4">
      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
        <div className="flex items-center space-x-3">
          <Link
            to={`/preview/${documentId}`}
            className="p-1.5 rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-100"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-xl font-bold text-gray-900">HTML Document Editor</h1>
            <div className="text-xs text-gray-500">
              {docMeta?.title} • Revision #{docMeta?.currentRevision}
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={toggleSourceMode}
            className={`inline-flex items-center px-3 py-1.5 rounded-lg border text-xs font-medium transition ${
              isSourceMode
                ? 'bg-gray-800 text-white border-gray-800'
                : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
            }`}
          >
            <Code className="w-3.5 h-3.5 mr-1" />
            {isSourceMode ? 'Visual Editor' : 'Source HTML'}
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="inline-flex items-center px-4 py-1.5 rounded-lg bg-green-600 text-white text-xs font-semibold hover:bg-green-700 shadow-sm transition"
          >
            {saving ? (
              <span>Saving...</span>
            ) : savedSuccess ? (
              <>
                <Check className="w-3.5 h-3.5 mr-1 text-white" />
                Revision Saved
              </>
            ) : (
              <>
                <Save className="w-3.5 h-3.5 mr-1" />
                Save Revision
              </>
            )}
          </button>
        </div>
      </div>

      {/* Re-anchoring Warning Alert */}
      <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-xl text-xs text-yellow-800 flex items-center">
        <AlertTriangle className="w-4 h-4 mr-2 text-yellow-600 flex-shrink-0" />
        <span>
          Modifying text content will trigger fuzzy re-anchoring of saved annotations. If target text is completely removed, affected highlights will be marked unresolved.
        </span>
      </div>

      {/* Editor Main Canvas */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col min-h-[600px]">
        {/* Editor Toolbar (Visible only in Visual Mode) */}
        {!isSourceMode && editor && (
          <div className="bg-gray-50 border-b border-gray-200 p-2 flex flex-wrap gap-1 items-center text-gray-700">
            <button
              onClick={() => editor.chain().focus().toggleBold().run()}
              className={`p-1.5 rounded hover:bg-gray-200 ${editor.isActive('bold') ? 'bg-gray-200 font-bold' : ''}`}
              title="Bold"
            >
              <Bold className="w-4 h-4" />
            </button>
            <button
              onClick={() => editor.chain().focus().toggleItalic().run()}
              className={`p-1.5 rounded hover:bg-gray-200 ${editor.isActive('italic') ? 'bg-gray-200' : ''}`}
              title="Italic"
            >
              <Italic className="w-4 h-4" />
            </button>
            <div className="w-px h-5 bg-gray-300 mx-1" />
            <button
              onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
              className={`p-1.5 rounded hover:bg-gray-200 ${editor.isActive('heading', { level: 1 }) ? 'bg-gray-200 font-bold' : ''}`}
              title="Heading 1"
            >
              <Heading1 className="w-4 h-4" />
            </button>
            <button
              onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
              className={`p-1.5 rounded hover:bg-gray-200 ${editor.isActive('heading', { level: 2 }) ? 'bg-gray-200 font-bold' : ''}`}
              title="Heading 2"
            >
              <Heading2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
              className={`p-1.5 rounded hover:bg-gray-200 ${editor.isActive('heading', { level: 3 }) ? 'bg-gray-200 font-bold' : ''}`}
              title="Heading 3"
            >
              <Heading3 className="w-4 h-4" />
            </button>
            <div className="w-px h-5 bg-gray-300 mx-1" />
            <button
              onClick={() => editor.chain().focus().toggleBulletList().run()}
              className={`p-1.5 rounded hover:bg-gray-200 ${editor.isActive('bulletList') ? 'bg-gray-200' : ''}`}
              title="Bullet List"
            >
              <List className="w-4 h-4" />
            </button>
            <button
              onClick={() => editor.chain().focus().toggleOrderedList().run()}
              className={`p-1.5 rounded hover:bg-gray-200 ${editor.isActive('orderedList') ? 'bg-gray-200' : ''}`}
              title="Numbered List"
            >
              <ListOrdered className="w-4 h-4" />
            </button>
            <div className="w-px h-5 bg-gray-300 mx-1" />
            <button
              onClick={() => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()}
              className="p-1.5 rounded hover:bg-gray-200"
              title="Insert Table (3x3)"
            >
              <TableIcon className="w-4 h-4" />
            </button>
            <div className="w-px h-5 bg-gray-300 mx-1" />
            <button
              onClick={() => editor.chain().focus().undo().run()}
              disabled={!editor.can().undo()}
              className="p-1.5 rounded hover:bg-gray-200 disabled:opacity-40"
              title="Undo"
            >
              <Undo className="w-4 h-4" />
            </button>
            <button
              onClick={() => editor.chain().focus().redo().run()}
              disabled={!editor.can().redo()}
              className="p-1.5 rounded hover:bg-gray-200 disabled:opacity-40"
              title="Redo"
            >
              <Redo className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Editor Body */}
        <div className="flex-1 p-8">
          {isSourceMode ? (
            <textarea
              value={rawSource}
              onChange={(e) => setRawSource(e.target.value)}
              className="w-full h-full min-h-[500px] font-mono text-xs text-gray-800 bg-gray-50 p-4 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-green-500"
              spellCheck={false}
            />
          ) : (
            <EditorContent editor={editor} className="prose max-w-none text-gray-900" />
          )}
        </div>
      </div>
    </div>
  );
};
