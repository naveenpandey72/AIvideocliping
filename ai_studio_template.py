# AI Studio HTML Template
AI_STUDIO_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Studio & Ollama Engine | Universal Video Clipper</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #090d16;
            --surface: #111827;
            --surface-card: #182235;
            --border: #28354d;
            --primary: #38bdf8;
            --accent-purple: #a855f7;
            --accent-yellow: #facc15;
            --accent-green: #22c55e;
            --text: #f8fafc;
            --text-muted: #94a3b8;
        }
        * { box-sizing: border-box; }
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 2rem 1rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        .app-container {
            max-width: 950px;
            width: 100%;
        }
        .nav-tabs {
            display: flex;
            gap: 0.75rem;
            justify-content: center;
            margin-bottom: 2rem;
            background: rgba(17, 24, 39, 0.7);
            padding: 0.4rem;
            border-radius: 999px;
            border: 1px solid var(--border);
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
        }
        .nav-tab-btn {
            padding: 0.6rem 1.4rem;
            border-radius: 999px;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 700;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-muted);
        }
        .nav-tab-btn:hover { color: #fff; }
        .nav-tab-btn.active {
            background: linear-gradient(135deg, #a855f7, #38bdf8);
            color: #fff;
            box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
        }
        .header { text-align: center; margin-bottom: 2rem; }
        .badge-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.35rem 0.85rem;
            background: rgba(168, 85, 247, 0.15);
            border: 1px solid rgba(168, 85, 247, 0.4);
            border-radius: 999px;
            color: var(--accent-purple);
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
        }
        h1 {
            font-size: 2.3rem;
            font-weight: 800;
            margin: 0 0 0.5rem;
            background: linear-gradient(135deg, #ffffff 30%, #a855f7 70%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            color: var(--text-muted);
            font-size: 1rem;
            margin: 0 auto;
            max-width: 650px;
        }
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            margin-bottom: 1.5rem;
        }
        .form-group { margin-bottom: 1.25rem; }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-size: 0.85rem;
            font-weight: 700;
            color: #cbd5e1;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .input-box {
            width: 100%;
            padding: 0.85rem 1rem;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text);
            font-size: 0.95rem;
            font-family: inherit;
            outline: none;
            transition: 0.2s;
        }
        .input-box:focus {
            border-color: var(--accent-purple);
            box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.2);
        }
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.25rem;
        }
        @media (max-width: 680px) { .grid-2 { grid-template-columns: 1fr; } }
        .btn-ai-submit {
            width: 100%;
            padding: 1.1rem;
            background: linear-gradient(135deg, #a855f7 0%, #38bdf8 100%);
            color: #090d16;
            border: none;
            border-radius: 12px;
            font-weight: 800;
            font-size: 1.1rem;
            cursor: pointer;
            margin-top: 1rem;
            transition: all 0.2s ease;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.6rem;
        }
        .btn-ai-submit:hover {
            filter: brightness(1.1);
            transform: translateY(-1px);
            box-shadow: 0 10px 25px rgba(168, 85, 247, 0.35);
        }
        .btn-ai-submit:disabled { opacity: 0.5; cursor: not-allowed; }
        .ai-config-accordion {
            background: rgba(168, 85, 247, 0.06);
            border: 1px solid rgba(168, 85, 247, 0.25);
            border-radius: 12px;
            margin-bottom: 1.5rem;
            overflow: hidden;
        }
        .ai-config-header {
            padding: 0.85rem 1.2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            font-weight: 700;
            font-size: 0.9rem;
            color: #e2e8f0;
        }
        .ai-config-body {
            display: none;
            padding: 0 1.2rem 1.2rem;
            border-top: 1px solid rgba(168, 85, 247, 0.2);
        }
        .moment-card {
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            transition: 0.2s;
        }
        .moment-card:hover { border-color: var(--accent-purple); }
        .moment-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        .moment-title { font-weight: 800; font-size: 1.05rem; color: #fff; }
        .moment-badge {
            font-size: 0.75rem;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            background: rgba(168, 85, 247, 0.2);
            color: var(--accent-purple);
            font-weight: 700;
            border: 1px solid rgba(168, 85, 247, 0.4);
        }
        .btn-render-moment {
            padding: 0.65rem 1.25rem;
            background: var(--primary);
            color: #090d16;
            border: none;
            border-radius: 8px;
            font-weight: 800;
            font-size: 0.88rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            align-self: flex-start;
            transition: 0.2s;
        }
        .btn-render-moment:hover {
            background: #38bdf8;
            transform: translateY(-1px);
        }
        .pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Tab Navigation Bar -->
        <div class="nav-tabs">
            <a href="/" class="nav-tab-btn">⚡ Standard Clipper</a>
            <a href="/ai-studio" class="nav-tab-btn active">🤖 AI Studio (Ollama / LLM)</a>
        </div>

        <div class="header">
            <div class="badge-chip">🧠 Next-Gen Multimodal AI Studio</div>
            <h1>Ollama Viral Moments Studio</h1>
            <p class="subtitle">Harness free Ollama models (DeepSeek, Llama, Qwen, Mistral) to analyze any video and automatically discover high-retention viral moments with custom prompts.</p>
        </div>

        <!-- LLM Config Accordion -->
        <div class="ai-config-accordion">
            <div class="ai-config-header" id="configToggle">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <span>⚙️ Ollama & AI Endpoint Configuration</span>
                    <span id="modelBadge" style="font-size: 0.75rem; padding: 2px 8px; border-radius: 999px; background: rgba(56,189,248,0.15); color: var(--primary);">deepseek-v4.1-flash</span>
                </div>
                <span id="configIcon" style="color: var(--text-muted);">▼</span>
            </div>
            <div class="ai-config-body" id="configBody">
                <div class="grid-2" style="margin-top: 1rem;">
                    <div class="form-group">
                        <label for="ollamaBaseUrl">Base URL (Ollama or OpenAI-compatible)</label>
                        <input type="text" id="ollamaBaseUrl" class="input-box" value="https://ollama.com/v1" placeholder="https://ollama.com/v1 or http://localhost:11434/v1">
                    </div>
                    <div class="form-group">
                        <label for="ollamaModel">Model</label>
                        <select id="ollamaModel" class="input-box">
                            <option value="deepseek-v4.1-flash" selected>DeepSeek V4.1 Flash (Fast & Smart)</option>
                            <option value="glm-5.3-flash">GLM 5.3 Flash</option>
                            <option value="mimo-v2.6-flash">Mimo v2.6 Flash</option>
                            <option value="minimax-m3.1-flash">MiniMax M3.1 Flash</option>
                            <option value="gpt-oss:20b">GPT OSS 20B</option>
                            <option value="llama3.3:70b">Llama 3.3 70B (Local Ollama)</option>
                            <option value="qwen2.5:7b">Qwen 2.5 7B (Local Ollama)</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label for="ollamaKey">API Key (Optional / Preconfigured)</label>
                    <input type="text" id="ollamaKey" class="input-box" value="2dbd1d4f7134463f8b1ddeb2cbefb079.29HbK0szjxNkEUa4fWAdJ2Jb" placeholder="Enter Ollama API key or local 'ollama'">
                </div>
            </div>
        </div>

        <div class="card">
            <form id="aiStudioForm">
                <div class="form-group">
                    <label for="aiVideoUrl">🔗 YouTube Video / Stream URL</label>
                    <input type="text" id="aiVideoUrl" class="input-box" required placeholder="https://www.youtube.com/watch?v=..." value="https://www.youtube.com/watch?v=YDNs_sPEcJc">
                </div>

                <div class="grid-2">
                    <div class="form-group">
                        <label for="promptFocus">🎯 Viral Optimization Goal</label>
                        <select id="promptFocus" class="input-box">
                            <option value="viral_hooks" selected>🔥 Maximum Retention Viral Hooks</option>
                            <option value="funny_moments">😂 Funny & Entertaining Highlights</option>
                            <option value="educational_tips">💡 Tips, Hacks & Knowledge Bombs</option>
                            <option value="emotional_story">🎭 Emotional Climax & Story Arc</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="framingStyle">📐 Framing Layout</label>
                        <select id="framingStyle" class="input-box">
                            <option value="auto" selected>Auto-Detect (Subject Track / Blurred 9:16)</option>
                            <option value="crop_blur">9:16 Blurred Background Pillarbox</option>
                        </select>
                    </div>
                </div>

                <div class="form-group">
                    <label for="customInstructions">✍️ Custom AI Prompt Instruction (Optional)</label>
                    <input type="text" id="customInstructions" class="input-box" placeholder="e.g. Focus on unexpected easter eggs, high suspense, or funny reactions">
                </div>

                <button type="submit" id="btnAnalyze" class="btn-ai-submit">
                    <span>✨ Ask Ollama to Find Viral Moments</span>
                </button>
            </form>
        </div>

        <!-- Live Status / Result Area -->
        <div id="aiResultsSection" style="display: none;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 0.5rem;">
                <h2 style="font-size: 1.3rem; margin: 0; color: #fff;">🎬 Discovered High-Retention Moments</h2>
                <span id="aiProviderBadge" style="font-size: 0.78rem; padding: 4px 10px; border-radius: 999px; background: rgba(168,85,247,0.2); color: var(--accent-purple); font-weight: 700;">Engine: Ollama</span>
            </div>
            <div id="momentsList"></div>
        </div>

        <!-- Live Render Console Area -->
        <div id="aiConsole" style="display: none; background: #060911; border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; margin-top: 1.5rem; font-family: 'JetBrains Mono', monospace;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <span id="aiStatusIndicator" class="pulse" style="color: var(--primary); font-weight: bold;">● PROCESSING</span>
                <span id="aiJobIdText" style="color: #94a3b8; font-size: 0.82rem;">Job: -</span>
            </div>
            <div id="aiConsoleLogs" style="font-size: 0.85rem; color: #94a3b8; max-height: 200px; overflow-y: auto; white-space: pre-wrap;">Initializing...</div>
        </div>
    </div>

    <script>
        const configToggle = document.getElementById('configToggle');
        const configBody = document.getElementById('configBody');
        const configIcon = document.getElementById('configIcon');
        const ollamaModel = document.getElementById('ollamaModel');
        const modelBadge = document.getElementById('modelBadge');
        const aiStudioForm = document.getElementById('aiStudioForm');
        const btnAnalyze = document.getElementById('btnAnalyze');
        const aiResultsSection = document.getElementById('aiResultsSection');
        const momentsList = document.getElementById('momentsList');
        const aiProviderBadge = document.getElementById('aiProviderBadge');
        const aiConsole = document.getElementById('aiConsole');
        const aiStatusIndicator = document.getElementById('aiStatusIndicator');
        const aiJobIdText = document.getElementById('aiJobIdText');
        const aiConsoleLogs = document.getElementById('aiConsoleLogs');

        configToggle.addEventListener('click', () => {
            const isHidden = window.getComputedStyle(configBody).display === 'none';
            configBody.style.display = isHidden ? 'block' : 'none';
            configIcon.innerText = isHidden ? '▲' : '▼';
        });

        ollamaModel.addEventListener('change', () => {
            modelBadge.innerText = ollamaModel.value;
        });

        aiStudioForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = document.getElementById('aiVideoUrl').value.trim();
            if (!url) return;

            btnAnalyze.disabled = true;
            btnAnalyze.innerHTML = `<span>⏳ Ollama is analyzing video stream...</span>`;
            aiResultsSection.style.display = "none";
            momentsList.innerHTML = "";

            try {
                const payload = {
                    url: url,
                    api_key: document.getElementById('ollamaKey').value.trim(),
                    model: ollamaModel.value,
                    base_url: document.getElementById('ollamaBaseUrl').value.trim(),
                    prompt_focus: document.getElementById('promptFocus').value,
                    custom_instruction: document.getElementById('customInstructions').value.trim()
                };

                const res = await fetch('/api/ollama/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });

                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || "Analysis failed");
                }

                const data = await res.json();
                renderMoments(data);
            } catch(err) {
                alert("Error: " + err.message);
            } finally {
                btnAnalyze.disabled = false;
                btnAnalyze.innerHTML = `<span>✨ Ask Ollama to Find Viral Moments</span>`;
            }
        });

        function renderMoments(data) {
            aiResultsSection.style.display = "block";
            aiProviderBadge.innerText = `Engine: ${data.provider}`;
            momentsList.innerHTML = "";

            (data.moments || []).forEach((m, idx) => {
                const card = document.createElement('div');
                card.className = "moment-card";
                const dur = Math.round((m.end || 0) - (m.start || 0));
                card.innerHTML = `
                    <div class="moment-header">
                        <div class="moment-title">Clip #${idx+1}: ${m.title || 'Viral Clip'}</div>
                        <span class="moment-badge">🔥 Score: ${m.score || 95}/100</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #cbd5e1; font-style: italic; border-left: 2px solid var(--accent-purple); padding-left: 0.75rem;">
                        Hook: "${m.hook || 'Watch this...'}"
                    </div>
                    <div style="font-size: 0.8rem; color: #94a3b8; display: flex; gap: 1rem; align-items: center;">
                        <span>⏱️ ${m.start}s - ${m.end}s (${dur}s duration)</span>
                        <span>🏷️ ${(m.hashtags || []).join(' ')}</span>
                    </div>
                    <button type="button" class="btn-render-moment" onclick="renderSingleMoment('${encodeURIComponent(JSON.stringify(m))}')">
                        <span>⚡ Render This 9:16 Short Now</span>
                    </button>
                `;
                momentsList.appendChild(card);
            });
        }

        async function renderSingleMoment(encodedMoment) {
            const m = JSON.parse(decodeURIComponent(encodedMoment));
            const url = document.getElementById('aiVideoUrl').value.trim();
            const framing = document.getElementById('framingStyle').value;

            aiConsole.style.display = "block";
            aiStatusIndicator.innerText = "● QUEUED";
            aiStatusIndicator.style.color = "var(--primary)";
            aiConsoleLogs.innerText = `Submitting clip "${m.title}" (${m.start}s - ${m.end}s)...`;

            try {
                const payload = {
                    url: url,
                    num_clips: 1,
                    start_time: String(m.start),
                    end_time: String(m.end),
                    framing_mode: framing,
                    captions_mode: "karaoke",
                    video_quality: "1080",
                    upload_to_gdrive: false
                };

                const res = await fetch('/api/clip', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const job = await res.json();
                pollAiJob(job.job_id, m.title);
            } catch(e) {
                aiConsoleLogs.innerText = "Error: " + e.message;
                aiStatusIndicator.innerText = "● FAILED";
                aiStatusIndicator.style.color = "#ef4444";
            }
        }

        function pollAiJob(jobId, title) {
            aiJobIdText.innerText = "Job ID: " + jobId.slice(0, 8);
            aiStatusIndicator.innerText = "● RENDERING";
            aiStatusIndicator.style.color = "var(--accent-yellow)";

            const interval = setInterval(async () => {
                try {
                    const res = await fetch('/api/jobs/' + jobId);
                    if (!res.ok) return;
                    const job = await res.json();

                    aiConsoleLogs.innerText = (job.logs || []).join(String.fromCharCode(10));
                    aiConsoleLogs.scrollTop = aiConsoleLogs.scrollHeight;

                    if (job.status === 'completed') {
                        clearInterval(interval);
                        aiStatusIndicator.innerText = "● READY FOR DOWNLOAD";
                        aiStatusIndicator.style.color = "var(--accent-green)";
                        aiStatusIndicator.classList.remove('pulse');

                        const clip = (job.clips || [])[0];
                        if (clip) {
                            aiConsoleLogs.innerText += String.fromCharCode(10) + `🎉 Success! Click to download: ${clip.download_url}`;
                            window.open(clip.download_url, '_blank');
                        }
                    } else if (job.status === 'failed') {
                        clearInterval(interval);
                        aiStatusIndicator.innerText = "● FAILED";
                        aiStatusIndicator.style.color = "#ef4444";
                        aiStatusIndicator.classList.remove('pulse');
                    }
                } catch(e) {}
            }, 2500);
        }
    </script>
</body>
</html>
"""
