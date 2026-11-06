export interface DocLanguageOption {
  code: string;
  name: string;
  bcp47: string;
}

export interface OcrLanguageOption {
  code: string;
  name: string;
}

export const POPULAR_DOC_LANGUAGES: DocLanguageOption[] = [
  { code: 'AUTO', name: 'Auto-Detect (Recommended)', bcp47: 'auto' },
  { code: 'en', name: 'English', bcp47: 'en-US' },
  { code: 'hi', name: 'Hindi (हिन्दी)', bcp47: 'hi-IN' },
  { code: 'ta', name: 'Tamil (தமிழ்)', bcp47: 'ta-IN' },
  { code: 'te', name: 'Telugu (తెలుగు)', bcp47: 'te-IN' },
  { code: 'kn', name: 'Kannada (ಕನ್ನಡ)', bcp47: 'kn-IN' },
  { code: 'ml', name: 'Malayalam (മലയാളം)', bcp47: 'ml-IN' },
  { code: 'bn', name: 'Bengali (বাংলা)', bcp47: 'bn-BD' },
  { code: 'mr', name: 'Marathi (मराठी)', bcp47: 'mr-IN' },
  { code: 'gu', name: 'Gujarati (ગુજરાતી)', bcp47: 'gu-IN' },
  { code: 'pa', name: 'Punjabi (ਪੰਜਾਬੀ)', bcp47: 'pa-IN' },
  { code: 'sa', name: 'Sanskrit (संस्कृतम्)', bcp47: 'sa-IN' },
  { code: 'ar', name: 'Arabic (العربية)', bcp47: 'ar-SA' },
  { code: 'ur', name: 'Urdu (اردو)', bcp47: 'ur-PK' },
  { code: 'ru', name: 'Russian (Русский)', bcp47: 'ru-RU' },
  { code: 'zh', name: 'Chinese (简体中文)', bcp47: 'zh-CN' },
  { code: 'ja', name: 'Japanese (日本語)', bcp47: 'ja-JP' },
  { code: 'ko', name: 'Korean (한국어)', bcp47: 'ko-KR' },
  { code: 'es', name: 'Spanish (Español)', bcp47: 'es-ES' },
  { code: 'fr', name: 'French (Français)', bcp47: 'fr-FR' },
  { code: 'de', name: 'German (Deutsch)', bcp47: 'de-DE' },
  { code: 'he', name: 'Hebrew (עברית)', bcp47: 'he-IL' },
  { code: 'th', name: 'Thai (ไทย)', bcp47: 'th-TH' },
  { code: 'fa', name: 'Persian (فارسی)', bcp47: 'fa-IR' },
  { code: 'vi', name: 'Vietnamese (Tiếng Việt)', bcp47: 'vi-VN' },
];

export const POPULAR_OCR_LANGS: OcrLanguageOption[] = [
  { code: 'eng', name: 'English' },
  { code: 'tam', name: 'Tamil (தமிழ்)' },
  { code: 'hin', name: 'Hindi (हिन्दी)' },
  { code: 'tel', name: 'Telugu (తెలుగు)' },
  { code: 'mal', name: 'Malayalam (മലയാളം)' },
  { code: 'kan', name: 'Kannada (ಕನ್ನಡ)' },
  { code: 'ben', name: 'Bengali (বাংলা)' },
  { code: 'mar', name: 'Marathi (मराठी)' },
  { code: 'guj', name: 'Gujarati (ગુજરાતી)' },
  { code: 'pan', name: 'Punjabi (ਪੰਜਾਬੀ)' },
  { code: 'san', name: 'Sanskrit (संस्कृतम्)' },
  { code: 'ara', name: 'Arabic (العربية)' },
  { code: 'urd', name: 'Urdu (اردو)' },
  { code: 'rus', name: 'Russian (Русский)' },
  { code: 'heb', name: 'Hebrew (עברית)' },
  { code: 'tha', name: 'Thai (ไทย)' },
  { code: 'chi_sim', name: 'Chinese Simp (简体)' },
  { code: 'jpn', name: 'Japanese (日本語)' },
  { code: 'kor', name: 'Korean (한국어)' },
  { code: 'fra', name: 'French' },
  { code: 'deu', name: 'German' },
  { code: 'spa', name: 'Spanish' },
];
