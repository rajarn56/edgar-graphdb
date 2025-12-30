/**
 * Data formatting utilities for dates, numbers, booleans, etc.
 */

/**
 * Format a value based on its type
 */
export function formatValue(value: any): string {
  if (value === null || value === undefined) {
    return 'N/A';
  }

  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No';
  }

  if (typeof value === 'number') {
    return formatNumber(value);
  }

  if (typeof value === 'string') {
    // Check if it's a date string
    if (isDateString(value)) {
      return formatDate(value);
    }
    return value;
  }

  if (value instanceof Date) {
    return formatDate(value);
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return '[]';
    }
    // Check if it's an embedding array
    if (value.length > 10 && typeof value[0] === 'number') {
      return `[${value.length} dimensions]`;
    }
    return `[${value.length} items]`;
  }

  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2);
  }

  return String(value);
}

/**
 * Format a number with appropriate precision
 */
export function formatNumber(value: number): string {
  if (Number.isInteger(value)) {
    return value.toLocaleString();
  }
  // For floating point numbers, limit decimal places
  return value.toLocaleString(undefined, {
    maximumFractionDigits: 4,
    minimumFractionDigits: 0,
  });
}

/**
 * Format a date string or Date object
 */
export function formatDate(value: string | Date): string {
  try {
    const date = typeof value === 'string' ? new Date(value) : value;
    if (isNaN(date.getTime())) {
      return String(value);
    }
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return String(value);
  }
}

/**
 * Check if a string is a date string
 */
function isDateString(value: string): boolean {
  // Check for ISO date strings or common date formats
  const datePatterns = [
    /^\d{4}-\d{2}-\d{2}/, // ISO date
    /^\d{4}-\d{2}-\d{2}T/, // ISO datetime
    /^\d{2}\/\d{2}\/\d{4}/, // MM/DD/YYYY
  ];
  return datePatterns.some(pattern => pattern.test(value));
}

/**
 * Format file size in bytes
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Truncate text to a maximum length
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength) + '...';
}

/**
 * Format content statistics
 */
export function getContentStats(content: string): {
  characters: number;
  words: number;
  lines: number;
} {
  return {
    characters: content.length,
    words: content.split(/\s+/).filter(w => w.length > 0).length,
    lines: content.split('\n').length,
  };
}

