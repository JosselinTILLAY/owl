document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const pdfInput = document.getElementById('pdf-input');
    const dropZone = document.getElementById('drop-zone');
    const generateBtn = document.getElementById('generate-btn');
    const fileInfo = document.getElementById('file-info');
    const fileNameDisplay = fileInfo.querySelector('.file-name');
    const removeFileBtn = document.getElementById('remove-file');
    
    const loadingState = document.getElementById('loading');
    const loadingText = document.getElementById('loading-text');
    const emptyState = document.getElementById('empty-state');
    const fileStatusHeader = document.getElementById('file-status-header');
    const featureTitle = document.getElementById('feature-title');

    const BACKEND_URL = 'http://localhost:8001';

    // State
    let selectedFile = null;
    let currentFeature = 'podcast';
    let currentMode = 'duo';
    let currentProvider = 'elevenlabs';

    // Feature Definitions
    const features = {
        podcast: { title: "Podcast <span>Generation</span>", endpoint: "/generate-podcast" },
        summary: { title: "Course <span>Summary</span>", endpoint: "/summarize" },
        exercises: { title: "MCQ <span>Exercises</span>", endpoint: "/generate-exercises" },
        video: { title: "Chill <span>Short Video</span>", endpoint: "/generate-short-video" },
        music: { title: "AI Background <span>Music</span>", endpoint: "/generate-music" }
    };

    // Sidebar Navigation
    document.querySelectorAll('.nav-links li').forEach(li => {
        li.addEventListener('click', () => {
            document.querySelectorAll('.nav-links li').forEach(item => item.classList.remove('active'));
            li.classList.add('active');
            
            currentFeature = li.dataset.feature;
            featureTitle.innerHTML = features[currentFeature].title;
            
            // Toggle Config Panels
            document.querySelectorAll('.feature-config').forEach(c => c.classList.add('hidden'));
            const specificConfig = document.getElementById(`config-${currentFeature}`);
            if (specificConfig) specificConfig.classList.remove('hidden');

            // Reset Result View
            resetResultView();
        });
    });

    // Toggle Buttons
    document.querySelectorAll('.toggle-group button').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.target.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            if (e.target.dataset.mode) currentMode = e.target.dataset.mode;
            if (e.target.dataset.provider) currentProvider = e.target.dataset.provider;
        });
    });

    // File Handling
    dropZone.addEventListener('click', () => pdfInput.click());
    pdfInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--accent-primary)'; });
    dropZone.addEventListener('dragleave', () => dropZone.style.borderColor = 'var(--glass-border)');
    dropZone.addEventListener('drop', (e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); });

    function handleFile(file) {
        if (!file || !file.name.endsWith('.pdf')) return alert('PDF file required.');
        selectedFile = file;
        fileNameDisplay.textContent = file.name;
        fileStatusHeader.textContent = `Source: ${file.name}`;
        fileInfo.classList.remove('hidden');
        dropZone.classList.add('hidden');
        generateBtn.disabled = false;
    }

    removeFileBtn.addEventListener('click', () => {
        selectedFile = null; fileInfo.classList.add('hidden'); dropZone.classList.remove('hidden');
        generateBtn.disabled = true; pdfInput.value = ''; fileStatusHeader.textContent = "No PDF selected";
    });

    // Generation Core
    generateBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        resetResultView();
        generateBtn.disabled = true;
        emptyState.classList.add('hidden');
        loadingState.classList.remove('hidden');
        loadingText.textContent = "Analyzing PDF...";

        try {
            // 1. Upload & Extract Text
            const formData = new FormData();
            formData.append('file', selectedFile);
            const uploadRes = await fetch(`${BACKEND_URL}/upload-pdf`, { method: 'POST', body: formData });
            if (!uploadRes.ok) throw new Error('Failed to read PDF');
            const { text } = await uploadRes.json();

            // 2. Feature Specific Generation
            loadingText.textContent = `Generating your ${currentFeature}...`;
            
            const genBody = new FormData();
            genBody.append('text', text);
            genBody.append('mode', currentMode);
            genBody.append('provider', currentProvider);
            if (currentFeature === 'video') genBody.append('music_prompt', document.getElementById('music-prompt').value);
            if (currentFeature === 'music') genBody.append('music_prompt', document.getElementById('music-prompt-standalone').value);

            const res = await fetch(`${BACKEND_URL}${features[currentFeature].endpoint}`, { method: 'POST', body: genBody });
            if (!res.ok) throw new Error('AI generation failed');
            let data = await res.json();

            // If it's an async job, poll for results
            if (data.job_id && currentFeature === 'podcast') {
                data = await pollJobStatus(data.job_id);
            }

            // 3. Render Output
            renderOutput(currentFeature, data);

        } catch (err) {
            alert(err.message);
            emptyState.classList.remove('hidden');
        } finally {
            loadingState.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });

    async function pollJobStatus(jobId) {
        const pollInterval = 2000;
        while (true) {
            const res = await fetch(`${BACKEND_URL}/podcast/job/${jobId}`);
            if (!res.ok) throw new Error('Failed to check job status');
            
            const job = await res.json();
            if (job.status === 'completed') {
                return job.result;
            } else if (job.status === 'failed') {
                throw new Error(job.error || 'Podcast generation failed');
            }
            
            // Update UI with status
            loadingText.textContent = `Podcast status: ${job.status.charAt(0).toUpperCase() + job.status.slice(1)}...`;
            
            await new Promise(resolve => setTimeout(resolve, pollInterval));
        }
    }

    function renderOutput(feature, data) {
        document.querySelectorAll('.result-outlet').forEach(o => o.classList.add('hidden'));
        const outlet = document.getElementById(`result-${feature}`);
        outlet.classList.remove('hidden');

        if (feature === 'podcast') {
            const player = document.getElementById('audio-player');
            player.src = `${BACKEND_URL}${data.audio_url}`;
            document.getElementById('download-link').href = player.src;
            document.getElementById('script-content').innerHTML = data.script.map(line => `
                <div class="script-line ${line.speaker}">
                    <span class="speaker">${line.speaker}</span>
                    <p>${line.content}</p>
                </div>
            `).join('');
            player.play();
        } 
        else if (feature === 'summary') {
            const content = data.summary !== undefined ? data.summary : data;
            document.getElementById('summary-content').innerHTML = formatMarkdown(content || "AI could not generate a summary for this document.");
            triggerMathRendering('summary-content');
        }
        else if (feature === 'exercises') {
            const content = data.exercises !== undefined ? data.exercises : data;
            document.getElementById('exercises-content').innerHTML = formatMarkdown(content || "AI could not generate exercises.");
            triggerMathRendering('exercises-content');
        }
        else if (feature === 'video') {
            const video = document.getElementById('video-player');
            video.src = `${BACKEND_URL}${data.video_url}`;
            document.getElementById('video-download-link').href = video.src;
            video.play();
        }
        else if (feature === 'music') {
            const music = document.getElementById('music-player');
            music.src = `${BACKEND_URL}${data.audio_url || data}`;
            document.getElementById('music-download-link').href = music.src;
            music.play();
        }
    }

    function resetResultView() {
        document.querySelectorAll('.result-outlet').forEach(o => o.classList.add('hidden'));
        emptyState.classList.remove('hidden');
        loadingState.classList.add('hidden');
    }

    function formatMarkdown(text) {
        if (typeof text !== 'string') return JSON.stringify(text);
        return marked.parse(text);
    }

    function triggerMathRendering(elementId) {
        const el = document.getElementById(elementId);
        if (typeof renderMathInElement === 'function') {
            renderMathInElement(el, {
                delimiters: [
                    {left: '$$', right: '$$', display: true},
                    {left: '$', right: '$', display: false},
                    {left: '\\(', right: '\\)', display: false},
                    {left: '\\sqrt', right: ' ', display: false}, // Handle inline sqrt
                    {left: '\\[', right: '\\]', display: true}
                ],
                throwOnError : false
            });
        }
    }
});
