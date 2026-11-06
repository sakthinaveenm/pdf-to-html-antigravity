import React, { useState, useEffect } from 'react';
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
  Check,
  AlertCircle,
} from 'lucide-react';
import { DocumentMeta } from '../../types';
import { api } from '../../services/api';

interface EditorViewProps {
  documentId: string;
  docMeta: DocumentMeta;
  initialHtml: string;
  onRevisionSaved: (newRevNumber: number) => void;
}

export const EditorView: React.FC<EditorViewProps> = ({
  documentId,
  docMeta,
  initialHtml,
  onRevisionSaved,
}) => {
  const [rawSource, setRawSource] = useState<string>(initialHtml);
  const [isSourceMode, setIsSourceMode] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const editor = useEditor({
    extensions: [
      StarterKit,
      Table.configure({ resizable: true }),
      TableRow,
      TableHeader,
      TableCell,
      Image,
    ],
    content: initialHtml || '<p>Loading document content...</p>',
  });

  // When initialHtml changes (e.g. document switched), update editor content
  useEffect(() => {
    setRawSource(initialHtml);
    if (editor && initialHtml) {
      editor.commands.setContent(initialHtml);
    }
  }, [initialHtml, editor]);

  const handleSave = async () => {
    if (!documentId) return;
    setSaving(true);
    setSavedSuccess(false);
    setErrorMessage(null);

    const htmlToSave = isSourceMode ? rawSource : (editor?.getHTML() || '');

    try {
      const res = await api.saveRevision(documentId, htmlToSave, 'Edited in TipTap Studio');
      onRevisionSaved(res.revisionNumber);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to save revision.';
      setErrorMessage(msg);
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
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-white">
      {/* Editor Toolbar */}
      <div className="bg-gray-50 border-b border-gray-200 px-4 py-2 flex flex-wrap items-center justify-between gap-2 flex-shrink-0">
        {/* Left: Formatting tools (when not in source mode) */}
        {!isSourceMode && editor ? (
          <div className="flex items-center space-x-1">
            <button
              onClick={() => editor.chain().focus().toggleBold().run()}
              className={`p-1.5 rounded hover:bg-gray-200 transition ${
                editor.isActive('bold') ? 'bg-gray-200 text-green-700' : 'text-gray-600'
              }`}
              title="Bold"
            >
              <Bold className="w-4 h-4" />
            </button>
            <button
              onClick={() => editor.chain().focus().toggleItalic().run()}
              className={`p-1.5 rounded hover:bg-gray-200 transition ${
                editor.isActive('italic') ? 'bg-gray-200 text-green-700' : 'text-gray-600'
              }`}
              title="Italic"
            >
              <Italic className="w-4 h-4" />
            </button>

            <div className="h-4 w-px bg-gray-300 mx-1" />

            <button
              onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
              className={`p-1.5 rounded hover:bg-gray-200 transition ${
                editor.isActive('heading', { level: 1 }) ? 'bg-gray-200 text-green-700' : 'text-gray-600'
              }`}
              title="Heading 1"
            >
              <Heading1 className="w-4 h-4" />
            </button>
            <button
              onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
              className={`p-1.5 rounded hover:bg-gray-200 transition ${
                editor.isActive('heading', { level: 2 }) ? 'bg-gray-200 text-green-700' : 'text-gray-600'
              }`}
              title="Heading 2"
            >
              <Heading2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
              className={`p-1.5 rounded hover:bg-gray-200 transition ${
                editor.isActive('heading', { level: 3 }) ? 'bg-gray-200 text-green-700' : 'text-gray-600'
              }`}
              title="Heading 3"
            >
              <Heading3 className="w-4 h-4" />
            </button>

            <div className="h-4 w-px bg-gray-300 mx-1" />

            <button
              onClick={() => editor.chain().focus().toggleBulletList().run()}
              className={`p-1.5 rounded hover:bg-gray-200 transition ${
                editor.isActive('bulletList') ? 'bg-gray-200 text-green-700' : 'text-gray-600'
              }`}
              title="Bullet List"
            >
              <List className="w-4 h-4" />
            </button>
            <button
              onClick={() => editor.chain().focus().toggleOrderedList().run()}
              className={`p-1.5 rounded hover:bg-gray-200 transition ${
                editor.isActive('orderedList') ? 'bg-gray-200 text-green-700' : 'text-gray-600'
              }`}
              title="Numbered List"
            >
              <ListOrdered className="w-4 h-4" />
            </button>

            <div className="h-4 w-px bg-gray-300 mx-1" />

            <button
              onClick={() =>
                editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
              }
              className="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition"
              title="Insert 3x3 Table"
            >
              <TableIcon className="w-4 h-4" />
            </button>

            <div className="h-4 w-px bg-gray-300 mx-1" />

            <button
              onClick={() => editor.chain().focus().undo().run()}
              disabled={!editor.can().undo()}
              className="p-1.5 rounded hover:bg-gray-200 disabled:opacity-30 text-gray-600 transition"
              title="Undo"
            >
              <Undo className="w-4 h-4" />
            </button>
            <button
              onClick={() => editor.chain().focus().redo().run()}
              disabled={!editor.can().redo()}
              className="p-1.5 rounded hover:bg-gray-200 disabled:opacity-30 text-gray-600 transition"
              title="Redo"
            >
              <Redo className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <span className="text-xs font-mono text-gray-500 font-semibold">
            &lt;&gt; Raw HTML Source Code Editor
          </span>
        )}

        {/* Right: Mode Toggle + Save Action */}
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleSourceMode}
            className={`inline-flex items-center px-3 py-1.5 rounded-lg border text-xs font-semibold transition ${
              isSourceMode
                ? 'bg-indigo-50 border-indigo-300 text-indigo-700'
                : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Code className="w-3.5 h-3.5 mr-1.5" />
            {isSourceMode ? 'Switch to Visual' : 'Switch to Source'}
          </button>

          <button
            onClick={handleSave}
            disabled={saving}
            className="inline-flex items-center px-3.5 py-1.5 rounded-lg bg-green-600 hover:bg-green-700 text-white text-xs font-bold shadow-xs transition disabled:opacity-50"
          >
            {savedSuccess ? (
              <>
                <Check className="w-3.5 h-3.5 mr-1 text-white" />
                <span>Revision Saved!</span>
              </>
            ) : (
              <>
                <Save className="w-3.5 h-3.5 mr-1" />
                <span>{saving ? 'Saving...' : `Save Revision (r#${docMeta.currentRevision})`}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Notice */}
      {errorMessage && (
        <div className="bg-red-50 border-b border-red-200 px-4 py-2 text-xs text-red-700 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Editor Body */}
      <div className="flex-1 overflow-auto p-6 bg-gray-50 flex justify-center">
        {isSourceMode ? (
          <textarea
            value={rawSource}
            onChange={(e) => setRawSource(e.target.value)}
            className="w-full max-w-4xl h-full font-mono text-xs p-4 bg-gray-900 text-gray-100 rounded-xl border border-gray-700 shadow-sm focus:outline-none focus:ring-1 focus:ring-green-500 resize-none leading-relaxed"
            spellCheck={false}
          />
        ) : (
          <div className="w-full max-w-4xl bg-white rounded-xl shadow-sm border border-gray-200 p-8 min-h-full">
            <EditorContent
              editor={editor}
              className="prose prose-sm max-w-none focus:outline-none min-h-[500px]"
            />
          </div>
        )}
      </div>
    </div>
  );
};
