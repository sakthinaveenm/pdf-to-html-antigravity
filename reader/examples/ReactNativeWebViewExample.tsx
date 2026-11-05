/**
 * React Native WebView Integration Example.
 * Demonstrates loading offline converted HTML, handling bidirectional JS bridge messages,
 * text selection detection, floating highlight creation toolbar, font scaling, and theme toggling.
 *
 * Requirements:
 * npm install react-native-webview
 */

import React, { useState, useRef, useCallback } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  Modal,
  Alert,
  Linking,
  Platform,
} from 'react-native';
import { WebView, WebViewMessageEvent } from 'react-native-webview';
import {
  ReaderBridgeMessage,
  TextSelectedPayload,
  HighlightPayload,
  ReaderReadyPayload,
  BRIDGE_PROTOCOL_VERSION,
} from '../src/bridge_types';

interface ReaderProps {
  documentHtml: string;
  documentId: string;
  initialHighlights?: HighlightPayload[];
}

export const MultilingualDocReader: React.FC<ReaderProps> = ({
  documentHtml,
  documentId,
  initialHighlights = [],
}) => {
  const webViewRef = useRef<WebView>(null);
  const [selectedTextData, setSelectedTextData] = useState<TextSelectedPayload | null>(null);
  const [highlights, setHighlights] = useState<HighlightPayload[]>(initialHighlights);
  const [fontScale, setFontScale] = useState<number>(1.0);
  const [theme, setTheme] = useState<'light' | 'dark' | 'sepia'>('light');
  const [isReady, setIsReady] = useState<boolean>(false);

  // Send message to WebView JavaScript engine
  const postToReader = useCallback((type: string, payload: unknown) => {
    const message = JSON.stringify({
      version: BRIDGE_PROTOCOL_VERSION,
      type,
      payload,
    });
    webViewRef.current?.postMessage(message);
  }, []);

  // Handle messages received from Reader WebView
  const handleMessage = useCallback((event: WebViewMessageEvent) => {
    try {
      const data: ReaderBridgeMessage = JSON.parse(event.nativeEvent.data);
      if (!data || data.version !== BRIDGE_PROTOCOL_VERSION) return;

      switch (data.type) {
        case 'READER_READY': {
          const payload = data.payload as ReaderReadyPayload;
          setIsReady(true);
          // Restore existing saved highlights
          if (highlights.length > 0) {
            postToReader('RESTORE_HIGHLIGHTS', { highlights });
          }
          break;
        }

        case 'TEXT_SELECTED': {
          const payload = data.payload as TextSelectedPayload;
          setSelectedTextData(payload);
          break;
        }

        case 'HIGHLIGHT_CREATED': {
          const newHl = data.payload as HighlightPayload;
          setHighlights((prev) => [...prev, newHl]);
          setSelectedTextData(null);
          break;
        }

        case 'HIGHLIGHT_REMOVED': {
          const { id } = data.payload as { id: string };
          setHighlights((prev) => prev.filter((h) => h.id !== id));
          break;
        }

        case 'LINK_CLICKED': {
          const { href } = data.payload as { href: string; text: string };
          Alert.alert('External Link', `Open ${href} in default browser?`, [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Open', onPress: () => Linking.openURL(href) },
          ]);
          break;
        }

        case 'READER_ERROR': {
          console.error('Reader error received:', data.payload);
          break;
        }
      }
    } catch (err) {
      console.warn('Failed parsing WebView message:', err);
    }
  }, [highlights, postToReader]);

  // Create highlight from current selection
  const createHighlight = (color: string) => {
    if (!selectedTextData) return;

    const highlightId = `hl-rn-${Date.now()}`;
    const newHighlight: HighlightPayload = {
      id: highlightId,
      documentId: selectedTextData.documentId,
      revision: 1,
      blockIds: selectedTextData.blockIds,
      quote: selectedTextData.quote,
      position: selectedTextData.position,
      color: color,
      resolved: true,
    };

    postToReader('APPLY_HIGHLIGHT', newHighlight);
  };

  // Font scaling controls
  const changeFontSize = (delta: number) => {
    const nextScale = Math.max(0.8, Math.min(2.0, fontScale + delta));
    setFontScale(nextScale);
    postToReader('SET_FONT_SIZE', { scale: nextScale });
  };

  // Theme switching
  const cycleTheme = () => {
    const nextTheme = theme === 'light' ? 'sepia' : theme === 'sepia' ? 'dark' : 'light';
    setTheme(nextTheme);
    postToReader('SET_THEME', { theme: nextTheme });
  };

  return (
    <SafeAreaView style={[styles.container, theme === 'dark' && styles.darkContainer]}>
      {/* Header Controls */}
      <View style={styles.toolbar}>
        <TouchableOpacity style={styles.toolBtn} onPress={() => changeFontSize(-0.1)}>
          <Text style={styles.toolText}>A-</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.toolBtn} onPress={() => changeFontSize(0.1)}>
          <Text style={styles.toolText}>A+</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.toolBtn} onPress={cycleTheme}>
          <Text style={styles.toolText}>{theme.toUpperCase()}</Text>
        </TouchableOpacity>
        <Text style={styles.badgeText}>{highlights.length} Highlights</Text>
      </View>

      {/* Embedded HTML Reader WebView */}
      <WebView
        ref={webViewRef}
        originWhitelist={['*']}
        source={{
          html: documentHtml,
          baseUrl: Platform.OS === 'android' ? 'file:///android_asset/' : undefined,
        }}
        onMessage={handleMessage}
        javaScriptEnabled={true}
        domStorageEnabled={true}
        allowFileAccess={true}
        allowFileAccessFromFileURLs={true}
        allowUniversalAccessFromFileURLs={true}
        style={styles.webview}
      />

      {/* Floating Selection Toolbar for Highlighting */}
      {selectedTextData && (
        <View style={styles.selectionModal}>
          <Text style={styles.selectionTitle} numberOfLines={1}>
            "{selectedTextData.selectedText}"
          </Text>
          <View style={styles.colorPalette}>
            {['#FFEB3B', '#A7F3D0', '#BAE6FD', '#FBCFE8', '#FED7AA'].map((col) => (
              <TouchableOpacity
                key={col}
                style={[styles.colorCircle, { backgroundColor: col }]}
                onPress={() => createHighlight(col)}
              />
            ))}
            <TouchableOpacity
              style={styles.cancelBtn}
              onPress={() => setSelectedTextData(null)}
            >
              <Text style={styles.cancelText}>✕</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  darkContainer: {
    backgroundColor: '#121212',
  },
  toolbar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  toolBtn: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#f3f4f6',
    borderRadius: 6,
    marginRight: 8,
  },
  toolText: {
    fontWeight: '600',
    color: '#374151',
  },
  badgeText: {
    marginLeft: 'auto',
    fontSize: 13,
    color: '#6b7280',
  },
  webview: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  selectionModal: {
    position: 'absolute',
    bottom: 30,
    left: 20,
    right: 20,
    backgroundColor: '#ffffff',
    padding: 14,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 10,
    elevation: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  selectionTitle: {
    fontSize: 13,
    fontStyle: 'italic',
    color: '#4b5563',
    marginBottom: 10,
  },
  colorPalette: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  colorCircle: {
    width: 34,
    height: 34,
    borderRadius: 17,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.1)',
  },
  cancelBtn: {
    paddingHorizontal: 10,
    paddingVertical: 6,
  },
  cancelText: {
    fontSize: 16,
    color: '#9ca3af',
  },
});

