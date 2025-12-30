/**
 * Filter panel component for graph filtering.
 */

import React, { useState } from 'react';
import './FilterPanel.css';

export interface FilterOptions {
  formType?: string;
  fiscalYear?: number;
  nodeTypes: string[];
}

interface FilterPanelProps {
  onFilterChange: (filters: FilterOptions) => void;
  availableFormTypes?: string[];
  availableYears?: number[];
}

export default function FilterPanel({
  onFilterChange,
  availableFormTypes = [],
  availableYears = [],
}: FilterPanelProps) {
  const [formType, setFormType] = useState<string>('');
  const [fiscalYear, setFiscalYear] = useState<string>('');
  const [nodeTypes, setNodeTypes] = useState<string[]>(['Company', 'Filing', 'Section', 'Chunk']);

  const nodeTypeOptions = ['Company', 'Filing', 'Section', 'Chunk', 'Period', 'FinancialStatement'];

  const handleNodeTypeToggle = (nodeType: string) => {
    setNodeTypes(prev => {
      const newTypes = prev.includes(nodeType)
        ? prev.filter(t => t !== nodeType)
        : [...prev, nodeType];
      applyFilters(formType, fiscalYear, newTypes);
      return newTypes;
    });
  };

  const applyFilters = (ft: string, fy: string, nt: string[]) => {
    onFilterChange({
      formType: ft || undefined,
      fiscalYear: fy ? parseInt(fy) : undefined,
      nodeTypes: nt,
    });
  };

  const handleFormTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setFormType(value);
    applyFilters(value, fiscalYear, nodeTypes);
  };

  const handleFiscalYearChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setFiscalYear(value);
    applyFilters(formType, value, nodeTypes);
  };

  const clearFilters = () => {
    setFormType('');
    setFiscalYear('');
    setNodeTypes(['Company', 'Filing', 'Section', 'Chunk']);
    applyFilters('', '', ['Company', 'Filing', 'Section', 'Chunk']);
  };

  return (
    <div className="filter-panel">
      <div className="filter-header">
        <h3>Filters</h3>
        <button className="clear-filters" onClick={clearFilters}>Clear</button>
      </div>

      <div className="filter-section">
        <label className="filter-label">Form Type</label>
        <select
          className="filter-select"
          value={formType}
          onChange={handleFormTypeChange}
        >
          <option value="">All Forms</option>
          {availableFormTypes.map(ft => (
            <option key={ft} value={ft}>{ft}</option>
          ))}
        </select>
      </div>

      <div className="filter-section">
        <label className="filter-label">Fiscal Year</label>
        <select
          className="filter-select"
          value={fiscalYear}
          onChange={handleFiscalYearChange}
        >
          <option value="">All Years</option>
          {availableYears.map(year => (
            <option key={year} value={year}>{year}</option>
          ))}
        </select>
      </div>

      <div className="filter-section">
        <label className="filter-label">Node Types</label>
        <div className="node-type-checkboxes">
          {nodeTypeOptions.map(nodeType => (
            <label key={nodeType} className="checkbox-label">
              <input
                type="checkbox"
                checked={nodeTypes.includes(nodeType)}
                onChange={() => handleNodeTypeToggle(nodeType)}
              />
              <span>{nodeType}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}

