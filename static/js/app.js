// SOP Generator Application JavaScript

// Tab Management
function showTab(tabName) {
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));
    
    document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// Toast Notifications
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Loading Overlay
function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// Convert Markdown to HTML (simple converter)
function markdownToHTML(markdown) {
    let html = markdown
        // Headers
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Lists
        .replace(/^\- (.*$)/gim, '<li>$1</li>')
        .replace(/^(\d+)\. (.*$)/gim, '<li>$2</li>')
        // Paragraphs
        .replace(/\n\n/g, '</p><p>')
        // Line breaks
        .replace(/\n/g, '<br>');
    
    // Wrap lists
    html = html.replace(/(<li>.*?<\/li>)+/gs, '<ul>$&</ul>');
    
    // Wrap in paragraphs if not already wrapped
    if (!html.startsWith('<h') && !html.startsWith('<ul')) {
        html = '<p>' + html + '</p>';
    }
    
    return html;
}

// AI Resolution Suggestion
async function suggestResolution() {
    const shortDesc = document.getElementById('short_description').value;
    const description = document.getElementById('description').value;
    const category = document.getElementById('category').value;
    
    if (!shortDesc && !description) {
        showToast('Please enter problem description first', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/suggest_resolution', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                short_description: shortDesc,
                description: description,
                category: category
            })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success && data.suggested_resolution) {
            // Fill resolution field
            const resolutionField = document.getElementById('resolution_notes');
            resolutionField.value = data.suggested_resolution;
            
            // Show confidence and source
            const confidence = (data.confidence * 100).toFixed(0);
            const source = data.primary_source?.incident || 'multiple incidents';
            
            showToast(`✅ Resolution suggested (${confidence}% match from ${source})`, 'success');
            
            // Highlight the field
            resolutionField.style.border = '2px solid #10b981';
            setTimeout(() => {
                resolutionField.style.border = '';
            }, 2000);
        } else {
            showToast(data.message || 'No similar past incidents found. Please enter resolution manually.', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('Resolution suggestion error:', error);
        showToast('Failed to get resolution suggestion', 'error');
    }
}

// Single Incident Form Handler
document.getElementById('single-incident-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        incident_number: document.getElementById('incident_number').value,
        category: document.getElementById('category').value,
        priority: document.getElementById('priority').value,
        short_description: document.getElementById('short_description').value,
        description: document.getElementById('description').value,
        resolution_notes: document.getElementById('resolution_notes').value
    };
    
    showLoading();
    
    try {
        const response = await fetch('/analyze_single', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (response.ok && data.success) {
            // Display SOP
            const sopContent = document.getElementById('single-sop-content');
            sopContent.innerHTML = markdownToHTML(data.sop);
            document.getElementById('single-sop-result').style.display = 'block';
            
            // Scroll to result
            document.getElementById('single-sop-result').scrollIntoView({ behavior: 'smooth' });
            
            showToast('SOP generated successfully!', 'success');
        } else {
            const errors = data.errors ? data.errors.join(', ') : (data.error || 'Unknown error occurred');
            showToast(`Error: ${errors}`, 'error');
            console.error('Server error:', data);
        }
    } catch (error) {
        hideLoading();
        console.error('Request error:', error);
        showToast(`Network error: ${error.message}`, 'error');
    }
});

// Batch Incident Form Handler
document.getElementById('batch-incident-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        short_description: document.getElementById('batch_short_description').value,
        category: document.getElementById('batch_category').value,
        description: document.getElementById('batch_description').value,
        resolution_notes: document.getElementById('batch_resolution_notes').value,
        priority: '3'
    };
    
    showLoading();
    
    try {
        const response = await fetch('/add_incident', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            showToast(`Incident ${data.incident_number} added successfully!`, 'success');
            
            // Reset form
            document.getElementById('batch-incident-form').reset();
            
            // Refresh incidents list
            loadIncidents();
        } else {
            const errors = data.errors ? data.errors.join(', ') : data.error;
            showToast(`Error: ${errors}`, 'error');
        }
    } catch (error) {
        hideLoading();
        showToast(`Network error: ${error.message}`, 'error');
    }
});

// Load Incidents
async function loadIncidents() {
    try {
        const response = await fetch('/get_incidents');
        const data = await response.json();
        
        if (data.success) {
            const count = data.count;
            
            // Update stats
            document.getElementById('total-incidents').textContent = count;
            document.getElementById('ready-incidents').textContent = count;
            
            // Enable/disable generate button
            const generateBtn = document.getElementById('generate-batch-btn');
            generateBtn.disabled = count < 2;
            
            // Display incidents list
            const listContainer = document.getElementById('incidents-list');
            
            if (count === 0) {
                listContainer.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">No incidents added yet. Add at least 2 incidents for ML categorization.</p>';
            } else {
                listContainer.innerHTML = data.incidents.map(incident => `
                    <div class="incident-item">
                        <div class="incident-header">
                            <span class="incident-number">${incident.number}</span>
                            <span class="incident-category">${incident.category}</span>
                        </div>
                        <div class="incident-description">
                            <strong>${incident.short_description}</strong>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Error loading incidents:', error);
    }
}

// Generate Batch SOPs
async function generateBatchSOPs() {
    showLoading();
    
    try {
        const response = await fetch('/generate_sop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            // Display SOPs
            const resultsContainer = document.getElementById('batch-sop-results');
            
            resultsContainer.innerHTML = data.sops.map((sop, index) => `
                <div class="sop-cluster">
                    <div class="card">
                        <div class="sop-cluster-header">
                            <div class="sop-cluster-title">📋 ${sop.category} Category</div>
                            <div class="sop-cluster-badge">${sop.incident_count} Incidents</div>
                        </div>
                        <div class="card-body">
                            <div class="sop-content">
                                ${markdownToHTML(sop.content)}
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
            
            resultsContainer.style.display = 'block';
            
            // Scroll to results
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
            
            showToast(`Generated ${data.sops.length} SOPs from ${data.total_incidents} incidents!`, 'success');
        } else {
            showToast(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        hideLoading();
        showToast(`Network error: ${error.message}`, 'error');
    }
}

// Clear All Incidents
async function clearAllIncidents() {
    if (!confirm('Are you sure you want to clear all incidents?')) {
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/clear_incidents', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            showToast('All incidents cleared!', 'success');
            loadIncidents();
            document.getElementById('batch-sop-results').style.display = 'none';
        }
    } catch (error) {
        hideLoading();
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Copy SOP to Clipboard
function copySOP(type) {
    let content;
    
    if (type === 'single') {
        const sopDiv = document.getElementById('single-sop-content');
        content = sopDiv.innerText;
    }
    
    navigator.clipboard.writeText(content).then(() => {
        showToast('SOP copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy SOP', 'error');
    });
}

// Download SOP as PDF
function downloadSOPAsPDF(type) {
    showLoading();
    
    let element;
    let filename;
    
    if (type === 'single') {
        element = document.getElementById('single-sop-content');
        const incidentNumber = document.getElementById('incident_number').value || 'INCIDENT';
        filename = `SOP_${incidentNumber}_${new Date().toISOString().split('T')[0]}.pdf`;
    }
    
    const opt = {
        margin: [10, 10, 10, 10],
        filename: filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, letterRendering: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
    };
    
    html2pdf().set(opt).from(element).save().then(() => {
        hideLoading();
        showToast('PDF downloaded successfully!', 'success');
    }).catch((error) => {
        hideLoading();
        console.error('PDF generation error:', error);
        showToast('Failed to generate PDF', 'error');
    });
}

// ===== CSV IMPORT FUNCTIONS =====

// Handle CSV file selection
document.addEventListener('DOMContentLoaded', () => {
    const csvFileInput = document.getElementById('csv-file');
    const fileInputWrapper = document.querySelector('.file-input-wrapper');
    
    if (fileInputWrapper) {
        // Click to select file
        fileInputWrapper.addEventListener('click', () => {
            csvFileInput.click();
        });
        
        // Drag and drop
        fileInputWrapper.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            fileInputWrapper.classList.add('drag-over');
        });
        
        fileInputWrapper.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            fileInputWrapper.classList.remove('drag-over');
        });
        
        fileInputWrapper.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            fileInputWrapper.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                csvFileInput.files = files;
                updateFileName();
            }
        });
    }
    
    if (csvFileInput) {
        csvFileInput.addEventListener('change', updateFileName);
    }
    
    // CSV Import Form
    const csvForm = document.getElementById('csv-import-form');
    if (csvForm) {
        csvForm.addEventListener('submit', (e) => {
            e.preventDefault();
            importCSV();
        });
    }
    
    loadIncidents();
});

function updateFileName() {
    const csvFileInput = document.getElementById('csv-file');
    const fileNameElement = document.getElementById('file-name');
    const file = csvFileInput.files[0];
    
    if (file) {
        fileNameElement.textContent = file.name;
        fileNameElement.classList.add('selected');
    } else {
        fileNameElement.textContent = 'No file selected';
        fileNameElement.classList.remove('selected');
    }
}

// Download CSV Template
function downloadTemplate() {
    showLoading();
    
    fetch('/export_template')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'incident_import_template.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            hideLoading();
            showToast('Template downloaded successfully!', 'success');
        })
        .catch(error => {
            hideLoading();
            console.error('Download error:', error);
            showToast('Failed to download template', 'error');
        });
}

// Import CSV File
function importCSV() {
    const fileInput = document.getElementById('csv-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showToast('Please select a CSV file', 'warning');
        return;
    }
    
    if (!file.name.endsWith('.csv')) {
        showToast('Please select a valid CSV file', 'error');
        return;
    }
    
    showLoading();
    
    const formData = new FormData();
    formData.append('file', file);
    
    const useRAG = document.getElementById('use-rag').checked;
    formData.append('use_rag', useRAG);
    
    fetch('/import_csv', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        const resultsDiv = document.getElementById('import-results');
        const statusDiv = document.getElementById('import-status');
        const errorsDiv = document.getElementById('import-errors');
        const warningsDiv = document.getElementById('import-warnings');
        
        resultsDiv.style.display = 'block';
        
        if (data.success) {
            statusDiv.innerHTML = `
                <h4 style="color: var(--success); margin-bottom: 10px;">✅ Import Successful!</h4>
                <p><strong>Total Imported:</strong> ${data.total_imported} incidents</p>
                <p><strong>Added to Knowledge Base:</strong> ${data.added_to_kb} incidents</p>
                <p><strong>Total in Database:</strong> ${data.added_to_db} incidents</p>
                ${data.message ? `<p style="margin-top: 10px;">${data.message}</p>` : ''}
            `;
            statusDiv.style.background = 'rgba(16, 185, 129, 0.1)';
            statusDiv.style.borderColor = 'var(--success)';
            
            showToast('CSV imported successfully!', 'success');
            
            // Clear form
            document.getElementById('csv-import-form').reset();
            document.getElementById('file-name').textContent = 'No file selected';
            
            // Refresh KB summary
            setTimeout(() => {
                refreshKBSummary();
            }, 500);
            
        } else {
            statusDiv.innerHTML = `
                <h4 style="color: var(--danger); margin-bottom: 10px;">❌ Import Failed</h4>
                <p>${data.error || 'Unknown error occurred'}</p>
            `;
            statusDiv.style.background = 'rgba(239, 68, 68, 0.1)';
            statusDiv.style.borderColor = 'var(--danger)';
            
            showToast('Import failed: ' + (data.error || 'Unknown error'), 'error');
        }
        
        // Display errors
        if (data.errors && data.errors.length > 0) {
            errorsDiv.innerHTML = `
                <h4>❌ Errors (${data.errors.length})</h4>
                <ul style="margin-left: 20px;">
                    ${data.errors.map(e => `<li style="font-size: 0.9rem;">${e}</li>`).join('')}
                </ul>
            `;
            errorsDiv.style.display = 'block';
        }
        
        // Display warnings
        if (data.warnings && data.warnings.length > 0) {
            warningsDiv.innerHTML = `
                <h4>⚠️ Warnings (${data.warnings.length})</h4>
                <ul style="margin-left: 20px;">
                    ${data.warnings.map(w => `<li style="font-size: 0.9rem;">${w}</li>`).join('')}
                </ul>
            `;
            warningsDiv.style.display = 'block';
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Import error:', error);
        showToast('Error during import: ' + error.message, 'error');
    });
}

// Refresh Knowledge Base Summary
function refreshKBSummary() {
    fetch('/get_knowledge_base')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const incidents = data.incidents;
                const total = incidents.length;
                const resolved = incidents.filter(inc => 
                    inc.resolution_notes && inc.resolution_notes.length > 20
                ).length;
                const unresolved = total - resolved;
                
                document.getElementById('kb-total').textContent = total;
                document.getElementById('kb-resolved').textContent = resolved;
                document.getElementById('kb-unresolved').textContent = unresolved;
            }
        })
        .catch(error => console.error('Error refreshing KB summary:', error));
}

// Batch Resolve Unresolved Incidents
function batchResolveUnresolved() {
    showLoading();
    
    fetch('/get_knowledge_base')
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                hideLoading();
                showToast('Failed to load knowledge base', 'error');
                return;
            }
            
            // Find unresolved incidents
            const unresolved = data.incidents.filter(inc => 
                !inc.resolution_notes || inc.resolution_notes.length < 30
            );
            
            if (unresolved.length === 0) {
                hideLoading();
                showToast('All incidents in knowledge base already have resolutions!', 'info');
                return;
            }
            
            const incident_numbers = unresolved.map(inc => inc.number);
            
            // Call batch resolve endpoint
            return fetch('/batch_resolve_incidents', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    incident_numbers: incident_numbers,
                    use_rag_suggestions: true
                })
            })
            .then(response => response.json())
            .then(resolveData => {
                hideLoading();
                
                if (resolveData.success) {
                    showToast(`✅ Resolved ${resolveData.updated_count} incidents using RAG suggestions!`, 'success');
                    
                    // Show details
                    if (resolveData.failed_count > 0) {
                        showToast(`⚠️ Failed to resolve ${resolveData.failed_count} incidents`, 'warning');
                    }
                    
                    // Refresh KB summary
                    setTimeout(() => {
                        refreshKBSummary();
                    }, 500);
                } else {
                    showToast('Error: ' + (resolveData.error || 'Unknown error'), 'error');
                }
            });
        })
        .catch(error => {
            hideLoading();
            console.error('Error:', error);
            showToast('Error: ' + error.message, 'error');
        });
}

// Initialize on page load (modified)
