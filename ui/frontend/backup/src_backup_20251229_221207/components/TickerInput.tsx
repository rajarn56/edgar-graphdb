/**
 * Ticker input component with form handling.
 */

import React, { useState } from 'react';
import './TickerInput.css';

interface TickerInputProps {
  onSubmit: (ticker: string) => void;
  loading?: boolean;
  error?: string | null;
}

export default function TickerInput({ onSubmit, loading = false, error = null }: TickerInputProps) {
  const [ticker, setTicker] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (ticker.trim()) {
      onSubmit(ticker.trim().toUpperCase());
    }
  };

  return (
    <div className="ticker-input-container">
      <form onSubmit={handleSubmit} className="ticker-form">
        <label htmlFor="ticker-input" className="ticker-label">
          Enter Ticker Symbol:
        </label>
        <div className="ticker-input-group">
          <input
            id="ticker-input"
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder="e.g., AAPL"
            className="ticker-input"
            disabled={loading}
            maxLength={10}
          />
          <button
            type="submit"
            className="ticker-submit"
            disabled={loading || !ticker.trim()}
          >
            {loading ? 'Loading...' : 'Load Graph'}
          </button>
        </div>
        {error && (
          <div className="ticker-error">
            {error}
          </div>
        )}
      </form>
    </div>
  );
}

