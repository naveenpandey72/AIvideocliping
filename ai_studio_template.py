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
        .cookie-accordion {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid var(--border);
            border-radius: 12px;
            margin-bottom: 1.5rem;
            overflow: hidden;
        }
        .cookie-accordion-header {
            padding: 0.85rem 1.2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            font-weight: 700;
            font-size: 0.9rem;
            color: #e2e8f0;
        }
        .cookie-accordion-body {
            display: none;
            padding: 0 1.2rem 1.2rem;
            border-top: 1px solid var(--border);
            background: rgba(0, 0, 0, 0.15);
        }
        .cookie-textarea {
            width: 100%;
            height: 90px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: #cbd5e1;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            padding: 0.75rem;
            box-sizing: border-box;
            margin: 0.75rem 0;
        }
        .cookie-btn {
            padding: 0.5rem 1.1rem;
            background: var(--accent-green);
            color: #090d16;
            border: none;
            border-radius: 6px;
            font-weight: 700;
            cursor: pointer;
        }
        .cookie-status-tag {
            font-size: 0.75rem;
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            font-weight: 700;
        }
        .tag-active { background: rgba(34, 197, 94, 0.15); color: var(--accent-green); border: 1px solid rgba(34, 197, 94, 0.3); }
        .tag-missing { background: rgba(234, 179, 8, 0.15); color: var(--accent-yellow); border: 1px solid rgba(234, 179, 8, 0.3); }
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
            <a href="/gta-auto-clipper" class="nav-tab-btn">🎮 GTA-Auto-Clipper</a>
        </div>

        <div class="header">
            <div class="badge-chip">🧠 Next-Gen Multimodal AI Studio</div>
            <h1>Ollama Viral Moments Studio</h1>
            <p class="subtitle">Harness free Ollama models (DeepSeek, Llama, Qwen, Mistral) to analyze any video and automatically discover high-retention viral moments with custom prompts.</p>
        </div>

        <!-- LLM & AI Provider Config Accordion -->
        <div class="ai-config-accordion">
            <div class="ai-config-header" id="configToggle">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <span>⚙️ AI Engine & Model Settings</span>
                    <span id="modelBadge" style="font-size: 0.75rem; padding: 2px 8px; border-radius: 999px; background: rgba(56,189,248,0.15); color: var(--primary); font-weight: 700;">🌐 OpenRouter Free (openrouter/free)</span>
                </div>
                <span id="configIcon" style="color: var(--text-muted);">▼</span>
            </div>
            <div class="ai-config-body" id="configBody">
                <div class="form-group" style="margin-top: 1rem;">
                    <label for="aiProviderSelect">🤖 Select AI Engine</label>
                    <select id="aiProviderSelect" class="input-box" style="font-weight: 700;">
                        <option value="openrouter-free" selected>🌐 OpenRouter Free (openrouter/free - 100% Free Reasoning with Key)</option>
                        <option value="autonomous-free">⚡ Autonomous AI Engine (100% Free - Built-in, No Key & No Credits Needed)</option>
                        <option value="groq-free">⚡ Groq Cloud (Free Tier - Super Fast Llama 3.3 70B)</option>
                        <option value="ollama-local">💻 Local Ollama (http://localhost:11434/v1 - 100% Free)</option>
                        <option value="ollama-cloud">☁️ Ollama Cloud (https://ollama.com/v1 - Requires paid credits on ollama.com)</option>
                    </select>
                </div>
                <div class="grid-2">
                    <div class="form-group">
                        <label for="ollamaBaseUrl">Base URL (OpenAI / OpenRouter compatible)</label>
                        <input type="text" id="ollamaBaseUrl" class="input-box" value="https://openrouter.ai/api/v1" placeholder="https://openrouter.ai/api/v1">
                    </div>
                    <div class="form-group">
                        <label for="ollamaModel">Model</label>
                        <input type="text" id="ollamaModel" class="input-box" value="openrouter/free" placeholder="openrouter/free">
                    </div>
                </div>
                <div class="form-group">
                    <label for="ollamaKey">API Key (Preconfigured)</label>
                    <input type="password" id="ollamaKey" class="input-box" value="" placeholder="Preconfigured OpenRouter Key">
                </div>
            </div>
        </div>

        <!-- Cookie Authentication Panel (Required on Cloud Hosts) -->
        <div class="cookie-accordion">
            <div class="cookie-accordion-header" id="cookieAccordionToggle">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <span>🍪 Cloud Server Authentication (YouTube Cookies)</span>
                    <span id="cookieBadge" class="cookie-status-tag tag-missing">Checking...</span>
                </div>
                <span id="cookieAccordionIcon" style="color: var(--text-muted);">▼</span>
            </div>
            <div class="cookie-accordion-body" id="cookieAccordionBody">
                <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 1rem;">
                    <b>Why this is needed:</b> Commercial cloud servers (like Render) are blocked by YouTube without cookies. Pasting your browser's YouTube cookies bypasses bot detection 100%.
                </p>
                <ol style="font-size: 0.82rem; color: #cbd5e1; padding-left: 1.25rem; line-height: 1.6;">
                    <li>Install free extension <b>Get cookies.txt locally</b> (Chrome/Edge/Firefox).</li>
                    <li>Open <a href="https://www.youtube.com" target="_blank" style="color: var(--primary);">youtube.com</a> in your browser.</li>
                    <li>Click the extension, copy exported cookies, and paste below:</li>
                </ol>
                <textarea id="cookiesInput" class="cookie-textarea" placeholder="# Netscape HTTP Cookie File&#10;.youtube.com&#9;TRUE&#9;/&#9;TRUE&#9;..."></textarea>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <button type="button" id="btnSaveCookies" class="cookie-btn">Save Cookies to Server</button>
                    <span id="cookieSaveMsg" style="font-size: 0.82rem;"></span>
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
            <div id="aiNoticeBanner" style="display: none; padding: 0.85rem 1.1rem; border-radius: 10px; margin-bottom: 1.25rem; font-size: 0.86rem; line-height: 1.5;"></div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 0.5rem;">
                <h2 style="font-size: 1.3rem; margin: 0; color: #fff;">🎬 Discovered High-Retention Moments</h2>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <a id="sheetLinkBtn" href="https://docs.google.com/spreadsheets/d/1Bcbi86o-flI9J6uq4pg1H1tw1iCVXqu1sSZfZnBDMHU/edit?gid=0#gid=0" target="_blank" style="text-decoration: none; font-size: 0.78rem; padding: 4px 10px; border-radius: 999px; background: rgba(34,197,94,0.15); color: var(--accent-green); border: 1px solid rgba(34,197,94,0.4); font-weight: 700;">📊 Google Sheet (Synced)</a>
                    <a href="/api/dataset/download" style="text-decoration: none; font-size: 0.78rem; padding: 4px 10px; border-radius: 999px; background: rgba(56,189,248,0.15); color: var(--primary); border: 1px solid rgba(56,189,248,0.4); font-weight: 700;">💾 Download JSONL</a>
                    <span id="aiProviderBadge" style="font-size: 0.78rem; padding: 4px 10px; border-radius: 999px; background: rgba(168,85,247,0.2); color: var(--accent-purple); font-weight: 700;">Engine: Autonomous</span>
                </div>
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
        const aiProviderSelect = document.getElementById('aiProviderSelect');
        const ollamaBaseUrl = document.getElementById('ollamaBaseUrl');
        const ollamaModel = document.getElementById('ollamaModel');
        const ollamaKey = document.getElementById('ollamaKey');
        const modelBadge = document.getElementById('modelBadge');
        const aiStudioForm = document.getElementById('aiStudioForm');
        const btnAnalyze = document.getElementById('btnAnalyze');
        const aiResultsSection = document.getElementById('aiResultsSection');
        const aiNoticeBanner = document.getElementById('aiNoticeBanner');
        const momentsList = document.getElementById('momentsList');
        const aiProviderBadge = document.getElementById('aiProviderBadge');
        const aiConsole = document.getElementById('aiConsole');
        const aiStatusIndicator = document.getElementById('aiStatusIndicator');
        const aiJobIdText = document.getElementById('aiJobIdText');
        const aiConsoleLogs = document.getElementById('aiConsoleLogs');

        // Default OpenRouter free initialization
        ollamaKey.value = atob('c2stb3ItdjEtZGM1ZWMxZGE0ZDIyYjZiNDk1ZjAyYjQ4MjNmZmRkNzI1ZGRkMWY0YjJmMjE1NGM3ZjdkMzkxMDExMWQ5NTdhNw==');

        // Cookie Authentication Panel logic
        const cookieAccordionToggle = document.getElementById('cookieAccordionToggle');
        const cookieAccordionBody = document.getElementById('cookieAccordionBody');
        const cookieAccordionIcon = document.getElementById('cookieAccordionIcon');
        const cookieBadge = document.getElementById('cookieBadge');
        const cookiesInput = document.getElementById('cookiesInput');
        const btnSaveCookies = document.getElementById('btnSaveCookies');
        const cookieSaveMsg = document.getElementById('cookieSaveMsg');

        cookieAccordionToggle.addEventListener('click', () => {
            const isHidden = window.getComputedStyle(cookieAccordionBody).display === 'none';
            cookieAccordionBody.style.display = isHidden ? 'block' : 'none';
            cookieAccordionIcon.innerText = isHidden ? '▲' : '▼';
        });

        async function checkCookies() {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 6000);
                const res = await fetch('/api/cookie-status', { signal: controller.signal });
                clearTimeout(timeoutId);
                if (!res.ok) throw new Error("Status " + res.status);
                const data = await res.json();
                if (data.has_cookies) {
                    cookieBadge.innerText = '● Cookies Active';
                    cookieBadge.className = 'cookie-status-tag tag-active';
                } else {
                    cookieBadge.innerText = '⚠️ No Cookies (Click to Setup)';
                    cookieBadge.className = 'cookie-status-tag tag-missing';
                }
            } catch(e) {
                cookieBadge.innerText = '⚠️ No Cookies (Click to Setup)';
                cookieBadge.className = 'cookie-status-tag tag-missing';
            }
        }
        checkCookies();
        setInterval(checkCookies, 15000);

        btnSaveCookies.addEventListener('click', async () => {
            const text = cookiesInput.value.trim();
            if (!text) {
                cookieSaveMsg.innerHTML = '<span style="color:#ef4444;">Please paste cookies first</span>';
                return;
            }
            btnSaveCookies.disabled = true;
            btnSaveCookies.innerText = "Saving...";
            try {
                const res = await fetch('/api/save-cookies', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ cookies_text: text })
                });
                const d = await res.json();
                if (d.success) {
                    cookieSaveMsg.innerHTML = '<span style="color:#22c55e;">✅ Saved!</span>';
                    cookieBadge.innerText = '● Cookies Active';
                    cookieBadge.className = 'cookie-status-tag tag-active';
                    cookiesInput.value = "";
                } else {
                    cookieSaveMsg.innerHTML = '<span style="color:#ef4444;">❌ Failed</span>';
                }
            } catch(e) {
                cookieSaveMsg.innerText = "Error: " + e;
            } finally {
                btnSaveCookies.disabled = false;
                btnSaveCookies.innerText = "Save Cookies to Server";
            }
        });

        configToggle.addEventListener('click', () => {
            const isHidden = window.getComputedStyle(configBody).display === 'none';
            configBody.style.display = isHidden ? 'block' : 'none';
            configIcon.innerText = isHidden ? '▲' : '▼';
        });

        // Provider switcher
        aiProviderSelect.addEventListener('change', () => {
            const val = aiProviderSelect.value;
            if (val === 'autonomous-free') {
                ollamaBaseUrl.value = 'builtin';
                ollamaModel.value = 'autonomous-free';
                ollamaKey.value = '';
                modelBadge.innerText = '⚡ 100% Free Engine';
                modelBadge.style.background = 'rgba(34,197,94,0.15)';
                modelBadge.style.color = 'var(--accent-green)';
            } else if (val === 'openrouter-free') {
                ollamaBaseUrl.value = 'https://openrouter.ai/api/v1';
                ollamaModel.value = 'openrouter/free';
                ollamaKey.value = atob('c2stb3ItdjEtZGM1ZWMxZGE0ZDIyYjZiNDk1ZjAyYjQ4MjNmZmRkNzI1ZGRkMWY0YjJmMjE1NGM3ZjdkMzkxMDExMWQ5NTdhNw==');
                modelBadge.innerText = '🌐 OpenRouter Free';
                modelBadge.style.background = 'rgba(56,189,248,0.15)';
                modelBadge.style.color = 'var(--primary)';
            } else if (val === 'groq-free') {
                ollamaBaseUrl.value = 'https://api.groq.com/openai/v1';
                ollamaModel.value = 'llama-3.3-70b-versatile';
                modelBadge.innerText = '⚡ Groq Fast Tier';
                modelBadge.style.background = 'rgba(234,179,8,0.15)';
                modelBadge.style.color = 'var(--accent-yellow)';
            } else if (val === 'ollama-local') {
                ollamaBaseUrl.value = 'http://localhost:11434/v1';
                ollamaModel.value = 'llama3.3:70b';
                ollamaKey.value = 'ollama';
                modelBadge.innerText = '💻 Local Ollama';
                modelBadge.style.background = 'rgba(168,85,247,0.15)';
                modelBadge.style.color = 'var(--accent-purple)';
            } else if (val === 'ollama-cloud') {
                ollamaBaseUrl.value = 'https://ollama.com/v1';
                ollamaModel.value = 'deepseek-v4.1-flash';
                ollamaKey.value = '2dbd1d4f7134463f8b1ddeb2cbefb079.29HbK0szjxNkEUa4fWAdJ2Jb';
                modelBadge.innerText = '☁️ Ollama Cloud (Paid)';
                modelBadge.style.background = 'rgba(239,68,68,0.15)';
                modelBadge.style.color = '#f87171';
            }
        });

        ollamaModel.addEventListener('input', () => {
            modelBadge.innerText = ollamaModel.value;
        });

        aiStudioForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = document.getElementById('aiVideoUrl').value.trim();
            if (!url) return;

            btnAnalyze.disabled = true;
            btnAnalyze.innerHTML = `<span>⏳ Analyzing video for viral retention...</span>`;
            aiResultsSection.style.display = "none";
            momentsList.innerHTML = "";

            try {
                const payload = {
                    url: url,
                    api_key: ollamaKey.value.trim(),
                    model: ollamaModel.value.trim(),
                    base_url: ollamaBaseUrl.value.trim(),
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
                alert("Notice: " + err.message);
            } finally {
                btnAnalyze.disabled = false;
                btnAnalyze.innerHTML = `<span>✨ Discover Viral Moments</span>`;
            }
        });

        function renderMoments(data) {
            aiResultsSection.style.display = "block";
            aiProviderBadge.innerText = `Engine: ${data.provider}`;
            momentsList.innerHTML = "";

            if (data.error_notice) {
                aiNoticeBanner.style.display = "block";
                if (data.error_notice.includes("402") || data.error_notice.includes("Payment")) {
                    aiNoticeBanner.style.background = "rgba(234, 179, 8, 0.12)";
                    aiNoticeBanner.style.border = "1px solid rgba(234, 179, 8, 0.4)";
                    aiNoticeBanner.style.color = "#fef08a";
                    aiNoticeBanner.innerHTML = `<b>💡 Cloud Provider Notice:</b> The external endpoint returned <i>Payment Required (402)</i> because <code>ollama.com</code> requires paid usage credits.<br><b>✅ Automatically switched to 100% Free Autonomous Engine:</b> Your clips were generated free of charge, logged to your local training dataset, and synced with your Google Sheet!`;
                } else {
                    aiNoticeBanner.style.background = "rgba(56, 189, 248, 0.12)";
                    aiNoticeBanner.style.border = "1px solid rgba(56, 189, 248, 0.4)";
                    aiNoticeBanner.style.color = "#bae6fd";
                    aiNoticeBanner.innerHTML = `<b>Notice:</b> ${data.error_notice}`;
                }
            } else {
                aiNoticeBanner.style.display = "none";
            }

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
                    <div style="display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; margin-top: 0.5rem;">
                        <button type="button" class="btn-render-moment">
                            <span>⚡ Render This 9:16 Short Now</span>
                        </button>
                        <span class="moment-status-indicator" style="font-size: 0.85rem; font-weight: 700;"></span>
                    </div>
                `;
                momentsList.appendChild(card);

                const btn = card.querySelector('.btn-render-moment');
                const statusSpan = card.querySelector('.moment-status-indicator');
                btn.addEventListener('click', () => {
                    renderSingleMoment(m, btn, statusSpan);
                });
            });
        }

        async function renderSingleMoment(m, btn, statusSpan) {
            const urlInput = document.getElementById('aiVideoUrl');
            const url = urlInput ? urlInput.value.trim() : "";
            const framing = document.getElementById('framingStyle').value;

            if (!url) {
                alert("Please enter a valid YouTube Video URL.");
                return;
            }

            btn.disabled = true;
            btn.innerHTML = `<span>⏳ Processing Short...</span>`;
            if (statusSpan) {
                statusSpan.style.color = "var(--primary)";
                statusSpan.innerText = "⏳ Submitting to pipeline...";
            }

            aiConsole.style.display = "block";
            aiConsole.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || "Clip submission failed");
                }
                const job = await res.json();
                pollAiJob(job.job_id, m.title, btn, statusSpan);
            } catch(e) {
                btn.disabled = false;
                btn.innerHTML = `<span>⚡ Retry Render</span>`;
                if (statusSpan) {
                    statusSpan.style.color = "#ef4444";
                    statusSpan.innerText = "❌ " + e.message;
                }
                aiConsoleLogs.innerText = "Error: " + e.message;
                aiStatusIndicator.innerText = "● FAILED";
                aiStatusIndicator.style.color = "#ef4444";
            }
        }

        function pollAiJob(jobId, title, btn, statusSpan) {
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
                            btn.disabled = false;
                            btn.style.background = "var(--accent-green)";
                            btn.innerHTML = `<span>⬇️ Download Short</span>`;
                            btn.onclick = () => window.open(clip.download_url, '_blank');
                            if (statusSpan) {
                                statusSpan.style.color = "var(--accent-green)";
                                statusSpan.innerHTML = `✅ Ready! <a href="${clip.download_url}" target="_blank" style="color:var(--primary); font-weight:bold;">Download Clip</a>`;
                            }
                            aiConsoleLogs.innerText += String.fromCharCode(10) + `🎉 Success! Click to download: ${clip.download_url}`;
                            window.open(clip.download_url, '_blank');
                        }
                    } else if (job.status === 'failed') {
                        clearInterval(interval);
                        btn.disabled = false;
                        btn.innerHTML = `<span>⚡ Retry Render</span>`;
                        if (statusSpan) {
                            statusSpan.style.color = "#ef4444";
                            statusSpan.innerText = "❌ " + (job.error || "Rendering failed");
                        }
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
