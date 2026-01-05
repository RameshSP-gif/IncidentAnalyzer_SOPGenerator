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

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadIncidents();
});
