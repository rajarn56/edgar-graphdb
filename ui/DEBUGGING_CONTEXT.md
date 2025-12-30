# EDGAR Graph UI - Right Panel Debugging Context

## 🔴 CRITICAL ISSUE

**Problem**: Right panel does NOT appear when nodes are clicked, despite:
- ✅ Backend API calls succeeding (confirmed in logs)
- ✅ Node click events being registered (API calls prove this)
- ✅ Panel state management code appearing correct
- ✅ CSS transforms and visibility rules in place

## 📊 Evidence from Logs

### Backend Logs (Working ✅)
```
2025-12-30 00:13:39.879 | INFO | Request: GET /api/graph/node/0000320193-24-000102
2025-12-30 00:13:39.894 | INFO | Response: GET /api/graph/node/0000320193-24-000102 | Status: 200 | Time: 0.015s
```
**Conclusion**: API calls ARE happening and succeeding when nodes are clicked.

### Frontend Console (Missing Logs ❌)
- No "Node clicked in GraphCanvas" logs visible
- No "Right panel expanded" logs visible  
- No panel state change logs visible

**Conclusion**: Either:
1. Click events aren't reaching the handler
2. Logs are being suppressed/filtered
3. Panel expansion is happening but CSS is hiding it
4. React state updates aren't triggering re-renders

## 🔍 What Has Been Tried

### 1. Node Type Normalization ✅
- **File**: `frontend/src/types/graph.ts`
- **Change**: Normalized section variants (PeriodicReportSection, ProxySection, Form8KItem) → "Section"
- **Status**: Fixed React Flow warnings, but didn't solve panel issue

### 2. Enhanced Click Handler ✅
- **File**: `frontend/src/components/graph/GraphCanvas.tsx`
- **Changes**:
  - Added `preventDefault()` and `stopPropagation()`
  - Added try-catch error handling
  - Enhanced logging
- **Status**: Improved error handling, but panel still not showing

### 3. Panel Expansion Logic ✅
- **File**: `frontend/src/App.tsx` - `handleNodeClick()`
- **Changes**:
  - Call `expandRightPanel()` BEFORE `selectNode()`
  - Added `requestAnimationFrame()` for DOM updates
  - Added timeout check to force expansion if width still 0
- **Status**: Multiple safeguards added, but panel still not visible

### 4. CSS Transform Fixes ✅
- **File**: `frontend/src/components/layout/AppLayout.css`
- **Changes**:
  - Simplified transform rules
  - Added `!important` flags for visibility
  - Added opacity and visibility transitions
- **Status**: CSS rules look correct, but may not be applied

### 5. Panel State Management ✅
- **File**: `frontend/src/hooks/usePanelState.ts`
- **Status**: Logic appears correct:
  - `getRightPanelWidth()` returns 0 when collapsed, `expandedWidth` when not collapsed
  - `expandRightPanel()` sets `collapsed: false, visible: true`
  - Default width is 400px

## 🏗️ Architecture Flow

### Click Flow (Expected)
1. User clicks node in `GraphCanvas`
2. `onNodeClickHandler` fires → logs "Node clicked in GraphCanvas"
3. Calls `onNodeClick(graphNode.id, graphNode.labels)` prop
4. `App.handleNodeClick()` receives call → logs "Node clicked in App"
5. Calls `panelState.expandRightPanel()` → should log "Right panel expanded"
6. Calls `nodeSelection.selectNode()` → triggers API call
7. `AppLayout` receives `rightWidth` from `getRightPanelWidth()`
8. Panel div gets width style and `collapsed` class removed
9. Panel should be visible

### Current State (Actual)
- Step 2-4: ✅ Working (API calls prove clicks work)
- Step 5: ❓ Unknown (no logs visible)
- Step 6: ✅ Working (API calls succeed)
- Step 7-9: ❌ Panel not visible

## 🔎 Key Files to Investigate

### Critical Files
1. **`frontend/src/components/layout/AppLayout.tsx`** (Lines 93-109)
   - Right panel rendering logic
   - Width calculation and CSS class application
   - **Check**: Is `rightWidth` actually > 0 when expanded?

2. **`frontend/src/hooks/usePanelState.ts`** (Lines 102-123, 148-168)
   - `expandRightPanel()` implementation
   - `getRightPanelWidth()` calculation
   - **Check**: Is state actually updating?

3. **`frontend/src/components/layout/AppLayout.css`** (Lines 57-81)
   - CSS transform rules
   - Visibility and opacity rules
   - **Check**: Are CSS rules being applied? Is there a specificity issue?

4. **`frontend/src/App.tsx`** (Lines 97-133)
   - `handleNodeClick()` implementation
   - Panel expansion timing
   - **Check**: Is `expandRightPanel()` actually being called?

5. **`frontend/src/components/graph/GraphCanvas.tsx`** (Lines 155-172)
   - Click handler implementation
   - **Check**: Is click event reaching the handler?

### Supporting Files
- `frontend/src/hooks/useNodeSelection.ts` - Node selection logic
- `frontend/src/components/layout/RightPanel.tsx` - Panel component
- `frontend/src/components/details/NodeDetailsPanel.tsx` - Panel content

## 🧪 Debugging Steps

### Step 1: Verify Click Events
```javascript
// In browser console, check:
// 1. Are there ANY click-related logs?
// 2. Check React DevTools → Components → GraphCanvas → props.onNodeClick
// 3. Manually trigger: document.querySelector('.react-flow__node')?.click()
```

### Step 2: Verify Panel State
```javascript
// In browser console (if hooks are exposed) or React DevTools:
// 1. Check AppLayout component state
// 2. Verify panelState.panelStates.rightPanel.collapsed === false
// 3. Verify panelState.getRightPanelWidth() > 0
```

### Step 3: Verify DOM Rendering
```javascript
// In browser console:
// 1. Check if panel exists: document.querySelector('.app-layout-right-panel')
// 2. Check computed styles: getComputedStyle(panel)
// 3. Check width: panel.style.width
// 4. Check transform: panel.style.transform
// 5. Check visibility: getComputedStyle(panel).visibility
```

### Step 4: Check CSS Specificity
```css
/* Check if these rules are actually applied: */
.app-layout-right-panel:not(.collapsed) {
  transform: translateX(0) !important;
  pointer-events: auto !important;
  opacity: 1 !important;
  visibility: visible !important;
}
```

### Step 5: Check React Re-renders
- Use React DevTools Profiler
- Check if AppLayout re-renders when panel state changes
- Check if RightPanel component receives updated props

## 🎯 Hypotheses to Test

### Hypothesis 1: State Not Updating
**Test**: Add console.log directly in `expandRightPanel()` to verify it's called
**Fix**: Check React state batching or closure issues

### Hypothesis 2: CSS Not Applied
**Test**: Manually set panel width/transform in browser DevTools
**Fix**: Check CSS specificity or conflicting styles

### Hypothesis 3: Component Not Re-rendering
**Test**: Check React DevTools for component updates
**Fix**: Ensure state changes trigger re-renders

### Hypothesis 4: Width Calculation Issue
**Test**: Log `rightWidth` value in AppLayout render
**Fix**: Verify `getRightPanelWidth()` returns correct value

### Hypothesis 5: Z-index or Positioning Issue
**Test**: Check if panel is behind other elements
**Fix**: Adjust z-index or positioning

### Hypothesis 6: Conditional Rendering Issue
**Test**: Check if panel content is conditionally hidden
**Fix**: Verify `rightPanelContent` prop is passed correctly

## 📝 Current Code State

### Panel Width Calculation
```typescript
// usePanelState.ts - getRightPanelWidth()
if (rightPanelState.collapsed) {
  return 0;  // Panel hidden
}
return rightPanelState.expandedWidth;  // Should be 400px
```

### Panel Expansion
```typescript
// usePanelState.ts - expandRightPanel()
setRightPanelStateInternal(prev => ({
  ...prev,
  collapsed: false,  // Should make panel visible
  visible: true,
}));
```

### Panel Rendering
```tsx
// AppLayout.tsx
<div
  className={`app-layout-right-panel ${collapsed ? 'collapsed' : ''}`}
  style={{ width: `${rightWidth}px` }}
>
  <RightPanel collapsed={collapsed}>
    {rightPanelContent}
  </RightPanel>
</div>
```

### CSS Rules
```css
.app-layout-right-panel:not(.collapsed) {
  transform: translateX(0) !important;
  opacity: 1 !important;
  visibility: visible !important;
}
```

## 🚨 Immediate Next Steps

1. **Add Direct Console Logging**
   - Add `console.log` in `expandRightPanel()` (bypass logger)
   - Add `console.log` in `getRightPanelWidth()` 
   - Add `console.log` in `AppLayout` render with `rightWidth`

2. **Check Browser DevTools**
   - Inspect `.app-layout-right-panel` element
   - Check computed styles
   - Check if element exists in DOM
   - Check if width > 0

3. **Test Manual Panel Expansion**
   - Add a test button that calls `expandRightPanel()` directly
   - See if panel appears when called manually

4. **Check React DevTools**
   - Inspect AppLayout component props
   - Check panelState values
   - Check if component re-renders on state change

5. **Verify Logger Configuration**
   - Check if logger is filtering out logs
   - Try using `console.log` instead of logger
   - Check logger level settings

## 📦 Environment

- **Frontend**: React 18 + TypeScript + Vite + React Flow
- **Backend**: FastAPI + Neo4j
- **Browser**: Check which browser and version
- **Logs Location**: 
  - Backend: `backend/logs/ui_backend_*.log`
  - Frontend: Browser console (F12)

## 🔗 Related Files

- Context: `CONTEXT_FOR_NEW_CHAT.md`
- Backend API: `backend/api/graph.py`
- Frontend App: `frontend/src/App.tsx`
- Panel Layout: `frontend/src/components/layout/AppLayout.tsx`
- Panel State: `frontend/src/hooks/usePanelState.ts`

## 💡 Key Insight

**The API calls prove clicks ARE working**, but the panel isn't showing. This suggests:
- Either the panel expansion isn't happening (state not updating)
- Or the panel expansion IS happening but CSS/DOM isn't reflecting it
- Or the panel is rendering but hidden behind something else

Focus on verifying the state update → DOM update → CSS application chain.

