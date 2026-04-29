const API_URL = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost' || window.location.protocol === 'file:') 
    ? 'http://127.0.0.1:8000/api/analyze' 
    : '/api/analyze';

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadSection = document.getElementById('upload-section');
    const loadingSection = document.getElementById('loading-section');
    const errorSection = document.getElementById('error-section');
    const resultsSection = document.getElementById('results-section');
    const retryBtn = document.getElementById('retry-btn');
    const errorMessage = document.getElementById('error-message');

    // Setup drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) {
            handleFile(files[0]);
        }
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length) {
            handleFile(this.files[0]);
        }
    });

    retryBtn.addEventListener('click', () => {
        errorSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        fileInput.value = '';
    });

    async function handleFile(file) {
        // Validate extension
        const validExtensions = ['.xml', '.aecg', '.bin', '.dat'];
        const isValid = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
        
        if (!isValid) {
            showError(`Invalid file format. Please upload an XML or Binary ECG file.`);
            return;
        }

        // Show loading state
        uploadSection.classList.add('hidden');
        errorSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                body: formData
            });

            const textData = await response.text();

            if (!response.ok) {
                let errorMsg = `Server returned ${response.status} ${response.statusText}`;
                try {
                    const errorData = JSON.parse(textData);
                    if (errorData && errorData.detail) {
                        errorMsg = errorData.detail;
                    }
                } catch(e) {
                    // Not JSON, just append the raw text (truncated)
                    errorMsg += ` | Response: ${textData ? textData.substring(0, 100) : 'Empty body'}`;
                }
                throw new Error(errorMsg);
            }

            let data;
            try {
                data = JSON.parse(textData);
            } catch (e) {
                throw new Error(`Server returned invalid JSON (Body: ${textData ? textData.substring(0, 50) : 'Empty'})`);
            }

            renderResults(data);
        } catch (error) {
            console.error('Error:', error);
            showError(error.message);
        }
    }

    function showError(msg) {
        loadingSection.classList.add('hidden');
        errorSection.classList.remove('hidden');
        errorMessage.textContent = msg;
    }

    function renderResults(data) {
        loadingSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        document.getElementById('action-bar').classList.remove('hidden');

        // Render Text Values
        document.getElementById('val-hr').textContent = data.problem1.avg_hr ? data.problem1.avg_hr.toFixed(1) : '--';
        document.getElementById('val-quality').textContent = data.problem1.quality;
        document.getElementById('val-rhythm').textContent = data.problem2.overall_rhythm;
        document.getElementById('val-afib').textContent = data.af_evidence.decision;

        // Render Status badge for HR
        const hrBadge = document.getElementById('status-hr');
        hrBadge.textContent = data.problem1.status;
        hrBadge.className = 'status-badge'; // reset
        if (data.problem1.status.includes('NORMAL')) {
            hrBadge.classList.add('status-good');
        } else if (data.problem1.status.includes('NO PEAKS') || data.problem1.status.includes('INVALID')) {
            hrBadge.classList.add('status-danger');
        } else {
            hrBadge.classList.add('status-warning');
        }

        // Color coding for rhythm and afib based on danger level
        const rhythmEl = document.getElementById('val-rhythm');
        rhythmEl.style.color = data.problem2.overall_rhythm.includes('Normal') ? 'var(--success)' : 'var(--warning)';

        const afibEl = document.getElementById('val-afib');
        if (data.af_evidence.decision.includes('Normal')) {
            afibEl.style.color = 'var(--success)';
        } else if (data.af_evidence.decision.includes('Strong')) {
            afibEl.style.color = 'var(--danger)';
        } else {
            afibEl.style.color = 'var(--warning)';
        }

        // Stress Logic
        const stressEl = document.getElementById('val-stress');
        const stressStateEl = document.getElementById('val-stress-state');
        if (data.stress_analysis) {
            const state = data.stress_analysis.state;
            stressEl.textContent = state;
            if (stressStateEl) stressStateEl.textContent = state;

            const colorSuccess = 'var(--success)';
            const colorDanger = 'var(--danger)';
            const colorWarning = 'var(--warning)';

            let chosenColor = colorWarning;
            if (state.includes('RELAXED') || state.includes('SLEEP') || state.includes('NORMAL')) {
                chosenColor = colorSuccess;
            } else if (state.includes('HIGH STRESS') || state.includes('UNUSUAL')) {
                chosenColor = colorDanger;
            }

            stressEl.style.color = chosenColor;
            if (stressStateEl) stressStateEl.style.color = chosenColor;

            // Populate specific HRV metrics in the Stress tab
            const sdnnEl = document.getElementById('val-sdnn');
            const sRmssdEl = document.getElementById('val-stress-rmssd');
            const confEl = document.getElementById('val-stress-confidence');
            
            if (sdnnEl) sdnnEl.textContent = (data.stress_analysis.sdnn * 1000).toFixed(1) + ' ms';
            if (sRmssdEl) sRmssdEl.textContent = (data.stress_analysis.rmssd * 1000).toFixed(1) + ' ms';
            if (confEl) confEl.textContent = (data.stress_analysis.confidence * 100).toFixed(0) + '%';
        }

        // Advanced Metrics
        document.getElementById('val-cv').textContent = data.problem2.cv ? data.problem2.cv.toFixed(3) : '--';
        document.getElementById('val-rmssd').textContent = data.problem2.rmssd ? (data.problem2.rmssd * 1000).toFixed(1) + ' ms' : '--';
        document.getElementById('val-pwave').textContent = data.af_evidence.p_wave_ratio ? (data.af_evidence.p_wave_ratio * 100).toFixed(1) + '%' : '--';
        document.getElementById('val-atrial').textContent = data.af_evidence.atrial_variability ? data.af_evidence.atrial_variability.toFixed(3) : '--';
        document.getElementById('val-atrial-status').textContent = data.af_evidence.atrial_activity;

        // Render Images (Base64)
        if (data.images) {
            const imgMap = {
                'img-raw': data.images.raw_ecg,
                'img-filtered': data.images.filtered_ecg,
                'img-paper': data.images.ecg_paper,
                'img-hr-trend': data.images.hr_trend,
                'img-rr-dist': data.images.rr_dist,
                'img-poincare': data.images.poincare
            };

            for (const [id, base64Str] of Object.entries(imgMap)) {
                const el = document.getElementById(id);
                if (el && base64Str) {
                    el.src = `data:image/png;base64,${base64Str}`;
                    el.closest('.img-wrapper').style.display = 'block';
                } else if (el) {
                    el.closest('.img-wrapper').style.display = 'none';
                }
            }
        }
    }

    // Modal and Interactions
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-img');
    const modalCaption = document.getElementById('modal-caption');
    const modalClose = document.querySelector('.modal-close');

    modalClose.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });

    // Handle Zoom and Download for all image actions
    document.querySelectorAll('.img-wrapper').forEach(wrapper => {
        const img = wrapper.querySelector('img');
        const zoomBtn = wrapper.querySelector('.zoom-btn');
        const dlBtn = wrapper.querySelector('.dl-img-btn');

        if (zoomBtn && img) {
            zoomBtn.addEventListener('click', () => {
                modal.classList.remove('hidden');
                modalImg.src = img.src;
                modalCaption.textContent = img.alt;
            });
        }

        if (dlBtn && img) {
            dlBtn.addEventListener('click', () => {
                const a = document.createElement('a');
                a.href = img.src;
                const safeName = img.alt.replace(/ /g, '_').toLowerCase();
                a.download = `cardiosync_${safeName}.png`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            });
        }
    });

    // Handle Detailed Report Print/Download
    const dlReportBtn = document.getElementById('download-report-btn');
    if (dlReportBtn) {
        dlReportBtn.addEventListener('click', () => {
            window.print();
        });
    }

    // Handle Reset/Back to Home Page
    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            window.location.reload();
        });
    }

    // Tab Switching Logic
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            // Add active class to clicked button
            btn.classList.add('active');

            const targetId = btn.getAttribute('data-target');
            
            // Handle 'Full Report' special case
            if (targetId === 'tab-full') {
                tabPanes.forEach(p => p.classList.add('active'));
            } else {
                // Show specific pane
                const targetPane = document.getElementById(targetId);
                if (targetPane) {
                    targetPane.classList.add('active');
                }
            }
        });
    });

});
