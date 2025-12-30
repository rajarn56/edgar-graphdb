/**
 * Application header component with ticker input, loading states, and controls.
 */

import React, { useState } from 'react';
import { logger } from '../../utils/logger';
import './AppHeader.css';

export interface AppHeaderProps {
  /** Ticker input value */
  ticker?: string;
  /** Whether graph is loading */
  loading?: boolean;
  /** Error message */
  error?: string | null;
  /** Callback when ticker is submitted */
  onTickerSubmit?: (ticker: string) => void;
  /** Graph statistics */
  stats?: {
    filings_count?: number;
    sections_count?: number;
    chunks_count?: number;
  };
}

export default function AppHeader({
  ticker: initialTicker = '',
  loading = false,
  error = null,
  onTickerSubmit,
  stats,
}: AppHeaderProps) {
  const [ticker, setTicker] = useState(initialTicker);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedTicker = ticker.trim().toUpperCase();
    if (trimmedTicker && onTickerSubmit) {
      logger.info('Ticker submitted', { ticker: trimmedTicker }, 'AppHeader');
      onTickerSubmit(trimmedTicker);
    }
  };

  const handleReset = () => {
    logger.debug('Graph reset', {}, 'AppHeader');
    setTicker('');
    if (onTickerSubmit) {
      onTickerSubmit('');
    }
  };

  return (
    <div className="app-header">
      <div className="app-header-left">
        <h1 className="app-header-title">EDGAR Graph Visualizer</h1>
      </div>

      <div className="app-header-center">
        <form onSubmit={handleSubmit} className="app-header-form">
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder="Enter ticker symbol (e.g., AAPL)"
            className="app-header-input"
            disabled={loading}
            maxLength={10}
            autoFocus
          />
          <button
            type="submit"
            className="app-header-submit"
            disabled={loading || !ticker.trim()}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Loading...
              </>
            ) : (
              'Load Graph'
            )}
          </button>
          {ticker && (
            <button
              type="button"
              className="app-header-reset"
              onClick={handleReset}
              disabled={loading}
              title="Reset graph"
            >
              Reset
            </button>
          )}
        </form>
        {error && (
          <div className="app-header-error" role="alert">
            {error}
          </div>
        )}
      </div>

      <div className="app-header-right">
        {stats && (
          <div className="app-header-stats">
            {stats.filings_count !== undefined && (
              <div className="stat-item">
                <span className="stat-label">Filings:</span>
                <span className="stat-value">{stats.filings_count}</span>
              </div>
            )}
            {stats.sections_count !== undefined && (
              <div className="stat-item">
                <span className="stat-label">Sections:</span>
                <span className="stat-value">{stats.sections_count}</span>
              </div>
            )}
            {stats.chunks_count !== undefined && (
              <div className="stat-item">
                <span className="stat-label">Chunks:</span>
                <span className="stat-value">{stats.chunks_count}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

