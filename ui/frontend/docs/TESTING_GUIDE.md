# Testing Guide

## Overview

This guide provides a comprehensive testing checklist for the EDGAR Graph Visualization UI. Test each feature systematically to ensure all functionality works as expected.

## Prerequisites

1. Backend API running on `http://localhost:8000`
2. Neo4j database populated with EDGAR data
3. Frontend application running (`npm run dev`)

## Test Checklist

### 1. Application Initialization

- [ ] Application loads without errors
- [ ] Header displays correctly
- [ ] Left panel (filters) is visible and expanded
- [ ] Center panel (graph) is visible
- [ ] Right panel (details) is collapsed
- [ ] No console errors on initial load

### 2. Ticker Input and Graph Loading

- [ ] Enter ticker symbol (e.g., `AAPL`) in header
- [ ] Click "Load Graph" button
- [ ] Loading spinner appears
- [ ] Graph loads successfully
- [ ] Nodes and edges render correctly
- [ ] Graph fits view automatically
- [ ] Stats display in header and footer
- [ ] Error handling works for invalid ticker

### 3. Panel Functionality

#### Left Panel (Filters)
- [ ] Panel can be collapsed/expanded
- [ ] Panel releases space when collapsed
- [ ] Panel regains space when expanded
- [ ] Smooth transition animation works
- [ ] Toggle button functions correctly

#### Right Panel (Node Details)
- [ ] Panel expands when node is selected
- [ ] Panel collapses when closed
- [ ] Panel releases space when closed
- [ ] Smooth transition animation works
- [ ] Close button functions correctly
- [ ] Toggle button functions correctly

### 4. Graph Interaction

#### Node Selection
- [ ] Click on Company node → Details appear in right panel
- [ ] Click on Filing node → Details appear in right panel
- [ ] Click on Section node → Details appear in right panel
- [ ] Click on Chunk node → Details appear in right panel
- [ ] Right panel expands automatically on selection
- [ ] Node appears selected (highlighted) in graph

#### Node Expansion
- [ ] Double-click Filing node → Sections load
- [ ] Double-click Section node → Chunks load
- [ ] Expanded nodes appear in graph
- [ ] Graph layout updates correctly
- [ ] Expanded nodes are tracked (no duplicate expansion)

#### Graph Navigation
- [ ] Drag nodes → Nodes move smoothly
- [ ] Zoom in/out → Zoom controls work
- [ ] Pan graph → Panning works
- [ ] Fit view → Graph fits to viewport
- [ ] MiniMap → MiniMap displays correctly

### 5. Node Details Display

#### Properties View
- [ ] Properties display correctly
- [ ] Properties grouped by category (Basic, Dates, Metadata, Other)
- [ ] Property groups can be expanded/collapsed
- [ ] Property values formatted correctly (dates, numbers, booleans)
- [ ] Copy-to-clipboard works for property values
- [ ] Long property values display correctly

#### Content View (Chunk Nodes)
- [ ] Chunk content displays in right panel
- [ ] Content is properly formatted
- [ ] Long content can be expanded/collapsed
- [ ] Search functionality works within content
- [ ] Search highlights matching text
- [ ] Content statistics display (chars, words, lines)
- [ ] Copy content button works
- [ ] Content scrolls properly for long text

#### Relationships View
- [ ] Relationships display correctly
- [ ] Incoming relationships shown separately
- [ ] Outgoing relationships shown separately
- [ ] Relationship types displayed with badges
- [ ] Clicking relationship navigates to connected node (if implemented)

### 6. Filtering

#### Form Type Filter
- [ ] Select form type from dropdown
- [ ] Graph filters to show only selected form type
- [ ] Filter indicator appears when active
- [ ] Clear filter works

#### Fiscal Year Filter
- [ ] Select fiscal year from dropdown
- [ ] Graph filters to show only selected year
- [ ] Filter indicator appears when active
- [ ] Clear filter works

#### Node Type Filter
- [ ] Toggle node types on/off
- [ ] Graph updates to show/hide node types
- [ ] Filter indicator appears when active
- [ ] All node types can be toggled independently

#### Combined Filters
- [ ] Multiple filters work together
- [ ] Active filter count displays correctly
- [ ] Clear all filters button works
- [ ] Graph updates correctly when filters change

### 7. Error Handling

- [ ] Invalid ticker shows error message
- [ ] Network errors handled gracefully
- [ ] API errors display user-friendly messages
- [ ] Error messages clear when new request succeeds
- [ ] Application doesn't crash on errors

### 8. Logging

- [ ] Logs are written to file/localStorage
- [ ] Logs include user interactions
- [ ] Logs include API calls
- [ ] Logs include errors with stack traces
- [ ] Log download works (`logger.downloadLogs()`)
- [ ] Log levels work correctly (debug, info, warn, error)

### 9. Responsive Design

- [ ] Layout works on desktop (1920x1080)
- [ ] Layout works on laptop (1366x768)
- [ ] Layout works on tablet (768x1024)
- [ ] Panels collapse appropriately on smaller screens
- [ ] Graph remains usable on smaller screens

### 10. Performance

- [ ] Graph loads within reasonable time (< 5 seconds)
- [ ] Node expansion is responsive (< 2 seconds)
- [ ] Filtering is instant
- [ ] No lag when interacting with graph
- [ ] Memory usage is reasonable
- [ ] No memory leaks after multiple operations

## Common Issues and Solutions

### Issue: Right Panel Doesn't Release Space
**Solution**: Check that `collapsed` state is properly set and CSS transitions are working.

### Issue: Chunk Content Not Displaying
**Solution**: 
1. Verify chunk node has `content` property
2. Check API response includes content
3. Verify ContentView component is rendering
4. Check browser console for errors

### Issue: Graph Not Loading
**Solution**:
1. Verify backend API is running
2. Check `VITE_API_BASE_URL` environment variable
3. Check browser network tab for API calls
4. Review logs for API errors

### Issue: Filters Not Working
**Solution**:
1. Verify filter state is updating
2. Check filter application logic in `useFilters` hook
3. Verify filtered data is passed to GraphCanvas
4. Check browser console for errors

## Automated Testing (Future)

Consider adding:
- Unit tests for hooks
- Component tests for key components
- Integration tests for API calls
- E2E tests for user workflows

## Reporting Issues

When reporting issues, include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Browser and version
5. Console errors
6. Logs (use `logger.downloadLogs()`)

