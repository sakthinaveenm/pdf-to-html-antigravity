"""
Job statuses and lifecycle state machine for document conversion.
"""
from enum import Enum

class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    INSPECTING = "INSPECTING"
    CONVERTING = "CONVERTING"
    OCR_PROCESSING = "OCR_PROCESSING"
    NORMALIZING = "NORMALIZING"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

class QualityStatus(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    FAILED = "FAILED"

class PageClassification(str, Enum):
    DIGITAL_TEXT = "DIGITAL_TEXT"
    SCANNED_IMAGE = "SCANNED_IMAGE"
    MIXED_CONTENT = "MIXED_CONTENT"
    TEXT_ENCODING_PROBLEM = "TEXT_ENCODING_PROBLEM"
    UNKNOWN = "UNKNOWN"

class ConverterType(str, Enum):
    AUTO = "AUTO"
    MARKER = "MARKER"
    DOCLING = "DOCLING"
    NATIVE = "NATIVE"

class BlockType(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    LIST_ITEM = "listItem"
    TABLE = "table"
    IMAGE = "image"
    CAPTION = "caption"
    BLOCKQUOTE = "blockquote"
    EQUATION = "equation"
    CODE = "code"
    PAGE_BREAK = "pageBreak"

