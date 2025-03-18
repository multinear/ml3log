let allLogs = [];
let searchTerm = '';
let activeLevel = null;
let activeLogger = '';
let searchWords = [];
let autoUpdate = true;
let lastLogId = 0;  // Track the last log ID we've received

// Log level numeric values (matching Python's logging levels)
const LOG_LEVELS = {
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50
};

// Configuration for log truncation
const SHOW_MAX_LINES = 15;
const SHOW_MAX_CHARS = 1500;
const TRUNCATE_MAX_LINES = 5;
const TRUNCATE_MAX_CHARS = 1000;
const TRUNCATION_MESSAGE = 'expand entry';
const COLLAPSE_MESSAGE = 'collapse entry';

// Add a map to track expanded entries by their log ID
const expandedEntries = new Map();

function fetchLogs() {
    // Only fetch if auto-update is enabled
    if (!autoUpdate) return;
    
    // Include the last log ID in the request
    fetch(`/api/logs?last_id=${lastLogId}`)
        .then(response => response.json())
        .then(data => {
            // Check if we have new logs
            if (data.logs && data.logs.length > 0) {
                // Add new logs to our collection
                allLogs = [...allLogs, ...data.logs];
                
                // Update the last log ID
                lastLogId = data.last_id || lastLogId;
                
                // Update UI with new logs
                updateButtonVisibility(allLogs);
                updateLoggerSelect(allLogs);
                renderLogs(allLogs);
            }
        })
        .catch(error => console.error('Error fetching logs:', error));
}

function updateButtonVisibility(logs) {
    // Get unique log levels from current logs
    const levels = new Set(logs.map(log => log.levelname));
    
    // Show/hide buttons based on available levels
    document.querySelectorAll('.level-btn').forEach(btn => {
        const level = btn.dataset.level;
        btn.classList.toggle('hidden', !levels.has(level));
    });
}

function highlightText(text, words) {
    if (!words || words.length === 0) return text;
    
    // Escape special regex characters in search words
    const escapedWords = words.map(word => 
        word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    );
    
    // Create a regex pattern that matches any of the search words
    const pattern = new RegExp(`(${escapedWords.join('|')})`, 'gi');
    
    // Split the text by HTML tags and only apply highlighting to text content
    const parts = text.split(/(<[^>]*>)/);
    
    // Process each part - if it's an HTML tag (starts with <), leave it as is
    // Otherwise, apply the highlighting
    return parts.map(part => {
        if (part.startsWith('<') && part.endsWith('>')) {
            return part; // Don't modify HTML tags
        } else {
            return part.replace(pattern, '<span class="highlight">$1</span>');
        }
    }).join('');
}

function highlightJsonProperties(text) {
    // First highlight property names (keys) in the format: "key":
    let highlighted = text.replace(/"([^"]+)":/g, '<span class="json-property">"$1"</span>:');
    
    // Improved regex for string values that may contain escaped quotes
    // Look for strings that come after a colon (with optional whitespace)
    highlighted = highlighted.replace(/: "((?:\\"|[^"])*)"/g, ': <span class="json-string">"$1"</span>');
    
    // Highlight string values in arrays (between square brackets)
    highlighted = highlighted.replace(/(\[|\,)(\s*)"((?:\\"|[^"])*)"/g, '$1$2<span class="json-string">"$3"</span>');
    
    // Highlight null, true, and false values
    highlighted = highlighted.replace(/: (null|true|false)\b/g, ': <span class="json-null">$1</span>');
    
    // Highlight numeric values (integers and floats)
    highlighted = highlighted.replace(/: (-?\d+(\.\d+)?)/g, ': <span class="json-number">$1</span>');
    
    return highlighted;
}

function formatIsoTimestamps(text) {
    // Match ISO timestamp pattern: YYYY-MM-DDThh:mm:ss.ssssss or similar formats
    return text.replace(/\b(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\b/g, 
        function(match) {
            // Simply wrap the timestamp in a styled span without changing its format
            return `<span class="iso-timestamp">${match}</span>`;
        }
    );
}

function highlightFilePaths(text) {
    // Simple regex to match file paths with optional line numbers
    // Added word boundary to avoid matching URLs
    // Also handle paths that may be surrounded by quotes
    return text.replace(/(?:^|\s|["'])(\/((?:[\w\.-]+\/)*[\w\.-]+\.\w+))(?::(\d+))?(?:["'])?/g, 
        function(match, path, _, lineNum) {
            // Preserve leading characters (space or quote)
            const leadingChar = match.match(/^[\s"']/)?.[0] || '';
            // Preserve trailing quote if present
            const trailingChar = match.match(/["']$/)?.[0] || '';
            
            return lineNum ? 
                `${leadingChar}<span class="filepath">${path}</span>:${lineNum}${trailingChar}` : 
                `${leadingChar}<span class="filepath">${path}</span>${trailingChar}`;
        }
    );
}

function highlightUrls(text) {
    // Match URLs starting with http:// or https://
    return text.replace(/\b(https?:\/\/[^\s<>"]+)/g, 
        '<a href="$1" class="url" target="_blank" rel="noopener noreferrer">$1</a>'
    );
}

function updateLoggerSelect(logs) {
    const loggerSelect = document.getElementById('logger-select');
    const currentValue = loggerSelect.value;
    
    // Get unique logger names in order of appearance
    const loggerNames = [];
    logs.forEach(log => {
        if (!loggerNames.includes(log.name)) {
            loggerNames.push(log.name);
        }
    });
    
    // Save current selection
    const currentSelection = loggerSelect.value;
    
    // Clear all options except the first one (All Loggers)
    while (loggerSelect.options.length > 1) {
        loggerSelect.remove(1);
    }
    
    // Add logger names as options
    loggerNames.forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        loggerSelect.appendChild(option);
    });
    
    // Restore selection if it still exists
    if (loggerNames.includes(currentSelection)) {
        loggerSelect.value = currentSelection;
    }
}

function truncateLogMessage(message) {
    // Count the number of lines
    const lines = message.split('\n');
    
    // Check if the message should be truncated
    if (lines.length > SHOW_MAX_LINES || message.length > SHOW_MAX_CHARS) {
        // Create truncated version (first few lines)
        let truncated = lines.slice(0, TRUNCATE_MAX_LINES).join('\n');
        
        // If the truncated text is still too long, truncate by characters
        if (truncated.length > SHOW_MAX_CHARS) {
            truncated = truncated.substring(0, TRUNCATE_MAX_CHARS);
        }
        
        return {
            isTruncated: true,
            truncatedContent: truncated,
            fullContent: message
        };
    }
    
    // No truncation needed
    return {
        isTruncated: false,
        fullContent: message
    };
}

// Helper function to add navigation arrows to a log entry
function addNavigationArrows(entry) {
    // Create up arrow
    const upArrow = document.createElement('div');
    upArrow.className = 'nav-arrow nav-arrow-up';
    upArrow.innerHTML = '&#9650;'; // Unicode for up arrow
    upArrow.title = 'Go to previous log';
    
    // Create down arrow
    const downArrow = document.createElement('div');
    downArrow.className = 'nav-arrow nav-arrow-down';
    downArrow.innerHTML = '&#9660;'; // Unicode for down arrow
    downArrow.title = 'Go to next log';
    
    // Add click handlers
    upArrow.addEventListener('click', function(e) {
        e.stopPropagation();
        const prevEntry = entry.previousElementSibling;
        if (prevEntry) {
            prevEntry.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
    
    downArrow.addEventListener('click', function(e) {
        e.stopPropagation();
        const nextEntry = entry.nextElementSibling;
        if (nextEntry) {
            nextEntry.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
    
    // Add arrows to entry
    entry.appendChild(upArrow);
    entry.appendChild(downArrow);
}

function renderLogs(logs) {
    const logsContainer = document.getElementById('logs');
    logsContainer.innerHTML = '';
    
    // Filter logs by search term and level
    let filteredLogs = logs;
    
    // Apply level filter if active
    if (activeLevel) {
        const minLevel = LOG_LEVELS[activeLevel];
        filteredLogs = filteredLogs.filter(log => LOG_LEVELS[log.levelname] >= minLevel);
    }
    
    // Apply logger filter if active
    if (activeLogger) {
        filteredLogs = filteredLogs.filter(log => log.name === activeLogger);
    }
    
    // Apply search filter if exists
    if (searchTerm) {
        // Split search term into words and filter out empty strings
        searchWords = searchTerm.toLowerCase().split(/\s+/).filter(word => word.length > 0);
        
        if (searchWords.length > 0) {
            filteredLogs = filteredLogs.filter(log => {
                const logText = `${log.levelname.toLowerCase()} ${log.name.toLowerCase()} ${log.message.toLowerCase()}`;
                
                // Check if ALL search words are found in the log text (AND condition)
                return searchWords.every(word => logText.includes(word));
            });
        }
    } else {
        searchWords = [];
    }
    
    // Show logs in chronological order (oldest first, newest last)
    filteredLogs.forEach(log => {
        const entry = document.createElement('div');
        entry.className = `log-entry level-${log.levelname}`;
        
        const content = document.createElement('pre');
        
        // Create metadata container for level tag and timestamp
        const metaContainer = document.createElement('div');
        metaContainer.className = 'log-meta';
        
        // Format timestamp in a more readable way
        const date = new Date(log.created * 1000);
        const formattedDate = `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
        
        // Create timestamp element
        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp';
        timestamp.textContent = formattedDate;
        
        // Create colored level tag
        const levelTag = document.createElement('span');
        levelTag.className = `level-tag level-tag-${log.levelname}`;
        levelTag.textContent = `[${log.levelname}]`;
        
        // Add level tag and timestamp to meta container
        metaContainer.appendChild(levelTag);
        metaContainer.appendChild(timestamp);
        
        const messageText = `<b>${log.name}</b>: ${log.message}`;
        const highlightedMessage = document.createElement('span');
        highlightedMessage.className = 'log-message';
        
        // Check if the message needs to be truncated
        const truncatedLog = truncateLogMessage(messageText);
        let processedText;
        
        if (truncatedLog.isTruncated) {
            // For truncated logs, store both versions and add click handler
            const truncatedContent = truncatedLog.truncatedContent;
            const fullContent = truncatedLog.fullContent;
            
            // Check if this log was previously expanded
            const wasExpanded = expandedEntries.has(log.id);
            
            // Process the appropriate content based on previous state
            processedText = wasExpanded ? 
                processHighlightedText(fullContent) : 
                processHighlightedText(truncatedContent);
            
            // Set the processed text to the highlighted message
            highlightedMessage.innerHTML = processedText;
            
            // Create an expandable indicator as a separate element
            const expandIndicator = document.createElement('div');
            expandIndicator.className = 'truncation-indicator';
            expandIndicator.textContent = wasExpanded ? COLLAPSE_MESSAGE : TRUNCATION_MESSAGE;
            
            // Function to toggle expansion state
            const toggleExpansion = function(indicator) {
                if (indicator.dataset.expanded === 'true') {
                    // Collapse
                    highlightedMessage.innerHTML = processHighlightedText(truncatedContent);
                    indicator.textContent = TRUNCATION_MESSAGE;
                    indicator.dataset.expanded = 'false';
                    // Remove from expanded entries map
                    expandedEntries.delete(log.id);
                } else {
                    // Expand
                    highlightedMessage.innerHTML = processHighlightedText(fullContent);
                    indicator.textContent = COLLAPSE_MESSAGE;
                    indicator.dataset.expanded = 'true';
                    // Add to expanded entries map
                    expandedEntries.set(log.id, true);
                }
            };
            
            // Add click handler only to the indicator
            expandIndicator.onclick = function(e) {
                e.stopPropagation(); // Prevent event bubbling
                toggleExpansion(this);
            };
            
            // Add click handler to left border (using the ::before pseudo-element)
            entry.addEventListener('click', function(e) {
                // Check if click is on the left border area (first 5px)
                if (e.offsetX <= 5) {
                    toggleExpansion(expandIndicator);
                }
            });
            
            // Set initial expanded state based on previous state
            expandIndicator.dataset.expanded = wasExpanded ? 'true' : 'false';
            
            // Add message and meta container to content
            content.appendChild(highlightedMessage);
            content.appendChild(metaContainer);
            
            // Add content and expand indicator to entry
            entry.appendChild(content);
            entry.appendChild(expandIndicator);
        } else {
            // For normal logs, just process the content
            processedText = processHighlightedText(truncatedLog.fullContent);
            highlightedMessage.innerHTML = processedText;
            
            // Add message and meta container to content
            content.appendChild(highlightedMessage);
            content.appendChild(metaContainer);
            
            // Add content to entry
            entry.appendChild(content);
        }
        
        // Add navigation arrows to each entry
        addNavigationArrows(entry);
        
        logsContainer.appendChild(entry);
    });
    
    // Auto-scroll to bottom if enabled
    if (autoUpdate) {
        scrollToBottom();
    }
}

function scrollToBottom() {
    const container = document.getElementById('logs-container');
    container.scrollTop = container.scrollHeight;
}

function handleSearch() {
    searchTerm = document.getElementById('search-input').value.trim();
    renderLogs(allLogs);
}

function clearSearch() {
    document.getElementById('search-input').value = '';
    searchTerm = '';
    searchWords = [];
    renderLogs(allLogs);

    // Focus on search input after clearing
    document.getElementById('search-input').focus();
}

function clearLogs() {
    // Clear all logs but keep the last log ID
    allLogs = [];
    updateButtonVisibility(allLogs);
    renderLogs(allLogs);
}

function setLevelFilter(level) {
    // Update active level
    if (activeLevel === level) {
        // If clicking the active level, clear the filter
        activeLevel = null;
        document.querySelectorAll('.level-btn').forEach(btn => {
            btn.classList.remove('active');
        });
    } else {
        // Set new active level
        activeLevel = level;
        
        // Update button states
        document.querySelectorAll('.level-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`.level-btn.${level.toLowerCase()}`).classList.add('active');
    }
    
    // Re-render logs with the new filter
    renderLogs(allLogs);
}

function toggleAutoUpdate() {
    autoUpdate = document.getElementById('autoupdate-checkbox').checked;
    if (autoUpdate) {
        scrollToBottom();
    }
}

function setLoggerFilter(loggerName) {
    activeLogger = loggerName;
    renderLogs(allLogs);
}

// Helper function to apply all highlighting to a text
function processHighlightedText(text) {
    let processedText = highlightUrls(
        highlightFilePaths(
            highlightJsonProperties(
                formatIsoTimestamps(text)
            )
        )
    );
    
    if (searchWords.length > 0) {
        processedText = highlightText(processedText, searchWords);
    }
    
    return processedText;
}

document.addEventListener('DOMContentLoaded', () => {
    // Initial fetch - get all logs the first time
    fetch('/api/logs')
        .then(response => response.json())
        .then(data => {
            if (data.logs && data.logs.length > 0) {
                allLogs = data.logs;
                lastLogId = data.last_id || 0;
                updateButtonVisibility(allLogs);
                updateLoggerSelect(allLogs);
                renderLogs(allLogs);
            }
        })
        .catch(error => console.error('Error fetching initial logs:', error));
    
    // Set up search functionality
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', handleSearch);
    
    // Focus on search input by default
    searchInput.focus();
    
    // Set up clear search button
    document.getElementById('clear-search-btn').addEventListener('click', clearSearch);
    
    // Set up clear logs button
    document.getElementById('clear-logs-btn').addEventListener('click', clearLogs);
    
    // Set up autoupdate checkbox
    document.getElementById('autoupdate-checkbox').addEventListener('change', toggleAutoUpdate);
    
    // Set up level filter buttons
    document.querySelectorAll('.level-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const level = e.target.dataset.level;
            setLevelFilter(level);
        });
    });
    
    // Set up logger select
    document.getElementById('logger-select').addEventListener('change', (e) => {
        setLoggerFilter(e.target.value);
    });
    
    // Poll for new logs every second
    setInterval(fetchLogs, 1000);
});
