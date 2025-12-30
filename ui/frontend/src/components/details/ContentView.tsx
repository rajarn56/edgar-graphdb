/**
 * Content view component to properly display chunk content.
 * Critical component for fixing chunk content display issue.
 */

import React, { useState, useMemo } from 'react';
import { formatValue, getContentStats, truncateText } from '../../utils/formatters';
import { logger } from '../../utils/logger';
import './ContentView.css';

export interface ContentViewProps {
  /** Content to display */
  content: string;
  /** Maximum length before truncation */
  maxPreviewLength?: number;
}

export default function ContentView({ 
  content, 
  maxPreviewLength = 500 
}: ContentViewProps) {
  const [expanded, setExpanded] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const stats = useMemo(() => getContentStats(content), [content]);
  const shouldTruncate = content.length > maxPreviewLength;
  const displayContent = expanded || !shouldTruncate ? content : truncateText(content, maxPreviewLength);

  // Highlight search term in content
  const highlightedContent = useMemo(() => {
    if (!searchTerm) {
      return displayContent;
    }

    const regex = new RegExp(`(${searchTerm})`, 'gi');
    const parts = displayContent.split(regex);
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="content-search-highlight">{part}</mark>
      ) : (
        part
      )
    );
  }, [displayContent, searchTerm]);

  const handleToggleExpand = () => {
    const newExpanded = !expanded;
    setExpanded(newExpanded);
    logger.debug('Content expanded/collapsed', { expanded: newExpanded, contentLength: content.length }, 'ContentView');
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const clearSearch = () => {
    setSearchTerm('');
  };

  const copyContent = async () => {
    try {
      await navigator.clipboard.writeText(content);
      logger.debug('Content copied to clipboard', { contentLength: content.length }, 'ContentView');
    } catch (err) {
      logger.warn('Failed to copy content', { error: err }, 'ContentView');
    }
  };

  logger.debug('Rendering content view', { 
    contentLength: content.length,
    expanded,
    hasSearchTerm: !!searchTerm
  }, 'ContentView');

  return (
    <div className="content-view">
      <div className="content-view-header">
        <h3 className="content-view-title">Content</h3>
        <div className="content-view-stats">
          <span className="content-stat">
            {stats.characters.toLocaleString()} chars
          </span>
          <span className="content-stat">
            {stats.words.toLocaleString()} words
          </span>
          <span className="content-stat">
            {stats.lines} lines
          </span>
        </div>
      </div>

      {/* Search bar */}
      <div className="content-search-bar">
        <input
          type="text"
          placeholder="Search in content..."
          value={searchTerm}
          onChange={handleSearchChange}
          className="content-search-input"
        />
        {searchTerm && (
          <button
            className="content-search-clear"
            onClick={clearSearch}
            aria-label="Clear search"
          >
            ×
          </button>
        )}
      </div>

      {/* Content display */}
      <div className="content-display">
        <div className={`content-text ${expanded ? 'expanded' : 'collapsed'}`}>
          {highlightedContent}
        </div>
      </div>

      {/* Actions */}
      <div className="content-actions">
        {shouldTruncate && (
          <button
            className="content-expand-button"
            onClick={handleToggleExpand}
          >
            {expanded ? 'Collapse' : 'Expand'}
          </button>
        )}
        <button
          className="content-copy-button"
          onClick={copyContent}
          title="Copy content to clipboard"
        >
          Copy
        </button>
      </div>
    </div>
  );
}

