/**
 * Enhanced filter panel component with improved UI/UX and visual feedback.
 */

import React from 'react';
import type { FilterOptions } from '../../types/ui';
import { logger } from '../../utils/logger';
import './FilterPanel.css';

export interface FilterPanelProps {
  /** Current filter options */
  filters: FilterOptions;
  /** Callback when filters change */
  onFilterChange: (filters: FilterOptions) => void;
  /** Available form types */
  availableFormTypes?: string[];
  /** Available fiscal years */
  availableYears?: number[];
  /** Active filter count */
  activeFilterCount?: number;
}

const NODE_TYPE_OPTIONS = ['Company', 'Filing', 'Section', 'Chunk', 'Period', 'FinancialStatement'];

export default function FilterPanel({
  filters,
  onFilterChange,
  availableFormTypes = [],
  availableYears = [],
  activeFilterCount = 0,
}: FilterPanelProps) {
  const handleFormTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    const newFilters: FilterOptions = {
      ...filters,
      formType: value || undefined,
    };
    logger.debug('Form type filter changed', { formType: value }, 'FilterPanel');
    onFilterChange(newFilters);
  };

  const handleFiscalYearChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    const newFilters: FilterOptions = {
      ...filters,
      fiscalYear: value ? parseInt(value) : undefined,
    };
    logger.debug('Fiscal year filter changed', { fiscalYear: value }, 'FilterPanel');
    onFilterChange(newFilters);
  };

  const handleNodeTypeToggle = (nodeType: string) => {
    const currentTypes = filters.nodeTypes || [];
    const newTypes = currentTypes.includes(nodeType)
      ? currentTypes.filter(t => t !== nodeType)
      : [...currentTypes, nodeType];
    
    const newFilters: FilterOptions = {
      ...filters,
      nodeTypes: newTypes,
    };
    logger.debug('Node type filter toggled', { nodeType, enabled: !currentTypes.includes(nodeType) }, 'FilterPanel');
    onFilterChange(newFilters);
  };

  const clearFilters = () => {
    const defaultFilters: FilterOptions = {
      nodeTypes: ['Company', 'Filing', 'Section', 'Chunk'],
    };
    logger.debug('Filters cleared', {}, 'FilterPanel');
    onFilterChange(defaultFilters);
  };

  const hasActiveFilters = activeFilterCount > 0 || 
    (filters.formType !== undefined && filters.formType !== '') ||
    (filters.fiscalYear !== undefined);

  return (
    <div className="filter-panel">
      <div className="filter-panel-header">
        <h3 className="filter-panel-title">Filters</h3>
        {hasActiveFilters && (
          <button
            className="filter-clear-button"
            onClick={clearFilters}
            title="Clear all filters"
          >
            Clear
          </button>
        )}
        {activeFilterCount > 0 && (
          <span className="filter-count-badge">{activeFilterCount}</span>
        )}
      </div>

      <div className="filter-panel-content">
        {/* Form Type Filter */}
        <div className="filter-section">
          <label className="filter-label">
            Form Type
            {filters.formType && (
              <span className="filter-active-indicator" title="Filter active" />
            )}
          </label>
          <select
            className="filter-select"
            value={filters.formType || ''}
            onChange={handleFormTypeChange}
          >
            <option value="">All Forms</option>
            {availableFormTypes.map(ft => (
              <option key={ft} value={ft}>
                {ft}
              </option>
            ))}
          </select>
        </div>

        {/* Fiscal Year Filter */}
        <div className="filter-section">
          <label className="filter-label">
            Fiscal Year
            {filters.fiscalYear !== undefined && (
              <span className="filter-active-indicator" title="Filter active" />
            )}
          </label>
          <select
            className="filter-select"
            value={filters.fiscalYear?.toString() || ''}
            onChange={handleFiscalYearChange}
          >
            <option value="">All Years</option>
            {availableYears.map(year => (
              <option key={year} value={year.toString()}>
                {year}
              </option>
            ))}
          </select>
        </div>

        {/* Node Types Filter */}
        <div className="filter-section">
          <label className="filter-label">
            Node Types
            {filters.nodeTypes && filters.nodeTypes.length < NODE_TYPE_OPTIONS.length && (
              <span className="filter-active-indicator" title="Filter active" />
            )}
          </label>
          <div className="node-type-checkboxes">
            {NODE_TYPE_OPTIONS.map(nodeType => {
              const isChecked = filters.nodeTypes?.includes(nodeType) ?? false;
              return (
                <label
                  key={nodeType}
                  className={`checkbox-label ${isChecked ? 'checked' : ''}`}
                >
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => handleNodeTypeToggle(nodeType)}
                  />
                  <span className="checkbox-custom"></span>
                  <span className="checkbox-text">{nodeType}</span>
                </label>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

