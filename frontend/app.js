document.addEventListener('DOMContentLoaded', () => {
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

    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat-btn');
    const chatHistory = document.getElementById('chat-history');

    const BACKEND_URL = 'http://localhost:8001';

    let selectedFile = null;
    let currentFeature = 'podcast';
    let contextId = null;

    const features = {
        podcast: { title: "Podcast <span>Duo</span>", endpoint: "/generate-podcast" },
        summary: { title: "Résumé <span>de cours</span>", endpoint: "/rag/query", mode: "summarize" },
        exercises: { title: "QCM <span>interactifs</span>", endpoint: "/rag/query", mode: "exercises" },
        chat: { title: "Chat <span>Cours</span>", endpoint: "/rag/query", mode: "chat" }
    };

    const loadingMessages = {
        podcast: "Génération du podcast Owl & Billie...",
        summary: "Rédaction du résumé...",
        exercises: "Création des QCM...",
        chat: "Recherche dans le cours..."
    };

    // Sidebar Navigation
    document.querySelectorAll('.nav-links li').forEach(li => {
        li.addEventListener('click', () => {
            document.querySelectorAll('.nav-links li').forEach(item => item.classList.remove('active'));
            li.classList.add('active');
            currentFeature = li.dataset.feature;
            featureTitle.innerHTML = features[currentFeature].title;

            document.querySelectorAll('.feature-config').forEach(c => c.classList.add('hidden'));
            const specificConfig = document.getElementById(`config-${currentFeature}`);
            if (specificConfig) specificConfig.classList.remove('hidden');

            resetResultView();
        });
    });

    // File Handling
    dropZone.addEventListener('click', () => pdfInput.click());
    pdfInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--accent-primary)'; });
    dropZone.addEventListener('dragleave', () => dropZone.style.borderColor = 'var(--glass-border)');
    dropZone.addEventListener('drop', (e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); });

    function handleFile(file) {
        if (!file || !file.name.endsWith('.pdf')) return alert('Un fichier PDF est requis.');
        selectedFile = file;
        fileNameDisplay.textContent = file.name;
        fileStatusHeader.textContent = `Source : ${file.name}`;
        fileInfo.classList.remove('hidden');
        dropZone.classList.add('hidden');
        generateBtn.disabled = false;
        if (!contextId) contextId = 'ctx_' + Math.random().toString(36).substring(2, 10);
    }

    removeFileBtn.addEventListener('click', () => {
        selectedFile = null; fileInfo.classList.add('hidden'); dropZone.classList.remove('hidden');
        generateBtn.disabled = true; pdfInput.value = ''; fileStatusHeader.textContent = "Aucun PDF sélectionné";
    });

    // Generation Core
    generateBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        resetResultView();
        generateBtn.disabled = true;
        emptyState.classList.add('hidden');
        loadingState.classList.remove('hidden');
        loadingText.textContent = "Ingestion du PDF...";

        try {
            // 1. Ingest PDF (RAG)
            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('context_id', contextId);

            const ingestRes = await fetch(`${BACKEND_URL}/rag/ingest`, { method: 'POST', body: formData });
            if (!ingestRes.ok) throw new Error("Échec de l'ingestion du PDF");

            // 2. Feature specific
            loadingText.textContent = loadingMessages[currentFeature] || "Génération en cours...";

            if (currentFeature === 'podcast') {
                await handlePodcastGeneration();
            } else {
                await handleRAGStreaming(currentFeature);
            }
        } catch (err) {
            alert(err.message);
            emptyState.classList.remove('hidden');
        } finally {
            loadingState.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });

    async function handlePodcastGeneration() {
        loadingText.textContent = "Génération du podcast Owl & Billie...";

        const res = await fetch(`${BACKEND_URL}/upload-pdf`, {
            method: 'POST',
            body: (() => { const fd = new FormData(); fd.append('file', selectedFile); return fd; })()
        });
        const { text } = await res.json();

        const genBody = new FormData();
        genBody.append('text', text);
        genBody.append('mode', 'duo');
        genBody.append('provider', 'elevenlabs');

        const podRes = await fetch(`${BACKEND_URL}/generate-podcast`, { method: 'POST', body: genBody });
        const podData = await podRes.json();
        const finalData = await pollJobStatus(podData.job_id);
        renderOutput('podcast', finalData);
    }

    async function handleRAGStreaming(featureId) {
        const outlet = document.getElementById(`result-${featureId}`);
        const contentArea = featureId === 'chat' ? null : document.getElementById(`${featureId}-content`);

        outlet.classList.remove('hidden');
        if (contentArea) contentArea.innerHTML = '<div class="streaming-cursor"></div>';

        const body = new FormData();
        body.append('context_id', contextId);
        body.append('mode', features[featureId].mode);

        let query = "Résume le contenu du cours.";
        if (featureId === 'exercises') query = "Génère 5 QCM.";
        if (featureId === 'chat') query = chatInput.value || "Parle-moi de ce cours.";
        body.append('query', query);

        const response = await fetch(`${BACKEND_URL}/rag/query`, { method: 'POST', body: body });
        if (!response.ok) throw new Error('Échec du streaming');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = '';

        if (featureId === 'chat') appendChatBubble('ai', '');

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            fullText += chunk;

            if (featureId === 'chat') {
                updateLastChatBubble(fullText);
            } else {
                contentArea.innerHTML = formatMarkdown(fullText) + '<div class="streaming-cursor"></div>';
            }
        }

        if (contentArea) {
            contentArea.innerHTML = formatMarkdown(fullText);
            triggerMathRendering(`${featureId}-content`);
        } else if (featureId === 'chat') {
            updateLastChatBubble(fullText, false);
            triggerMathRendering('chat-history');
        }
    }

    // Chat
    sendChatBtn.addEventListener('click', async () => {
        const query = chatInput.value.trim();
        if (!query || !contextId) return;
        appendChatBubble('user', query);
        chatInput.value = '';
        await handleRAGStreaming('chat');
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatBtn.click();
    });

    function appendChatBubble(role, text) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${role} ${role === 'ai' ? 'streaming-cursor' : ''}`;
        bubble.innerHTML = role === 'user' ? text : formatMarkdown(text);
        chatHistory.appendChild(bubble);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function updateLastChatBubble(text, isStreaming = true) {
        const bubbles = chatHistory.querySelectorAll('.chat-bubble.ai');
        const lastBubble = bubbles[bubbles.length - 1];
        if (lastBubble) {
            lastBubble.innerHTML = formatMarkdown(text);
            lastBubble.classList.toggle('streaming-cursor', isStreaming);
        }
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    async function pollJobStatus(jobId) {
        while (true) {
            const res = await fetch(`${BACKEND_URL}/podcast/job/${jobId}`);
            const job = await res.json();
            if (job.status === 'completed') return job.result;
            if (job.status === 'failed') throw new Error(job.error || 'Échec de la génération');
            const labels = { pending: 'En attente...', processing: 'Génération en cours...' };
            loadingText.textContent = labels[job.status] || `Statut : ${job.status}...`;
            await new Promise(r => setTimeout(r, 2000));
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
    }

    function resetResultView() {
        document.querySelectorAll('.result-outlet').forEach(o => o.classList.add('hidden'));
        emptyState.classList.remove('hidden');
        loadingState.classList.add('hidden');
        if (currentFeature === 'chat') {
            document.getElementById('result-chat').classList.remove('hidden');
            emptyState.classList.add('hidden');
        }
    }

    function formatMarkdown(text) {
        if (typeof text !== 'string') return JSON.stringify(text);
        return marked.parse(text);
    }

    function triggerMathRendering(elementId) {
        const el = typeof elementId === 'string' ? document.getElementById(elementId) : elementId;
        if (typeof renderMathInElement === 'function' && el) {
            renderMathInElement(el, {
                delimiters: [
                    {left: '$$', right: '$$', display: true},
                    {left: '$', right: '$', display: false},
                    {left: '\\(', right: '\\)', display: false},
                    {left: '\\[', right: '\\]', display: true}
                ],
                throwOnError: false
            });
        }
    }
});
