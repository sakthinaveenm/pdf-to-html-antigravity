/**
 * React Native WebView Bridge Protocol Types.
 * Version: 1
 * Defines bidirectional JSON messaging between the web reader and the React Native host.
 */

export const BRIDGE_PROTOCOL_VERSION = 1;

export type ReaderToNativeMessageType =
  | 'READER_READY'
  | 'TEXT_SELECTED'
  | 'HIGHLIGHT_CREATED'
  | 'HIGHLIGHT_REMOVED'
  | 'HIGHLIGHT_UPDATED'
  | 'LINK_CLICKED'
  | 'FONT_SIZE_CHANGED'
  | 'READER_ERROR';

export type NativeToReaderMessageType =
  | 'INIT_DOCUMENT'
  | 'SET_FONT_SIZE'
  | 'SET_THEME'
  | 'APPLY_HIGHLIGHT'
  | 'REMOVE_HIGHLIGHT'
  | 'SEARCH_QUERY';

export interface TextQuoteAnchor {
  exact: string;
  prefix: string;
  suffix: string;
}

export interface TextPositionAnchor {
  start: number;
  end: number;
  unit: 'unicode-codepoint' | 'utf16-codeunit';
}

export interface HighlightPayload {
  id: string;
  documentId: string;
  revision: number;
  blockIds: string[];
  quote: TextQuoteAnchor;
  position: TextPositionAnchor;
  color: string;
  note?: string;
  resolved: boolean;
}

export interface ReaderReadyPayload {
  documentId: string;
  pageCount: number;
  activeHighlightsCount: number;
  supportsCustomHighlightApi: boolean;
}

export interface TextSelectedPayload {
  documentId: string;
  blockIds: string[];
  selectedText: string;
  quote: TextQuoteAnchor;
  position: TextPositionAnchor;
  rect: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface ReaderErrorPayload {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ReaderBridgeMessage<T = unknown> {
  version: number;
  type: ReaderToNativeMessageType | NativeToReaderMessageType;
  payload: T;
}

