#!/usr/bin/env python3
"""
gta_clipper_template.py
HTML Template for GTA-Auto-Clipper interface based on https://github.com/AnIntellectualBeing/GTA-Auto-Clipper
"""

GTA_CLIPPER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GTA Auto Clipper | 9:16 Vice City Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&family=Pricedown&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #070913;
            --surface: #0f1322;
            --surface-card: #141a2e;
            --border: #232c48;
            --gta-pink: #f43f5e;
            --gta-cyan: #38bdf8;
            --gta-yellow: #fde047;
            --gta-purple: #c084fc;
            --accent-green: #22c55e;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            min-height: 100vh;
            padding: 1.5rem 1rem 4rem;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(244, 63, 94, 0.12) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(56, 189, 248, 0.12) 0%, transparent 40%),
                radial-gradient(circle at 50% 50%, rgba(192, 132, 252, 0.08) 0%, transparent 60%);
        }

        .app-container { max-width: 900px; margin: 0 auto; }

        /* Top Nav Tabs */
        .nav-tabs {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 2rem;
            background: rgba(15, 23, 42, 0.8);
            padding: 0.4rem;
            border-radius: 999px;
            border: 1px solid var(--border);
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
            flex-wrap: wrap;
            justify-content: center;
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
            background: linear-gradient(135deg, var(--gta-pink), var(--gta-purple));
            color: #fff;
            box-shadow: 0 4px 18px rgba(244, 63, 94, 0.4);
        }

        .header { text-align: center; margin-bottom: 2rem; }
        .badge-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.35rem 0.85rem;
            background: rgba(244, 63, 94, 0.15);
            border: 1px solid rgba(244, 63, 94, 0.4);
            border-radius: 999px;
            color: var(--gta-pink);
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
        }
        h1 {
            font-size: 2.4rem;
            font-weight: 800;
            margin: 0 0 0.5rem;
            background: linear-gradient(135deg, #ffffff 20%, var(--gta-pink) 60%, var(--gta-cyan) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.02em;
        }
        .subtitle {
            color: var(--text-muted);
            font-size: 1rem;
            margin: 0 auto;
            max-width: 680px;
            line-height: 1.6;
        }

        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.75rem;
            margin-bottom: 1.75rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }

        .form-group { margin-bottom: 1.25rem; }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 700;
            font-size: 0.88rem;
            color: #e2e8f0;
        }
        .input-box {
            width: 100%;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.85rem 1rem;
            color: var(--text-main);
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s ease;
        }
        .input-box:focus {
            border-color: var(--gta-pink);
            box-shadow: 0 0 0 3px rgba(244, 63, 94, 0.25);
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.25rem;
        }
        @media (max-width: 640px) { .grid-2 { grid-template-columns: 1fr; } }

        /* Gameplay confirmation banner */
        .confirm-box {
            background: rgba(244, 63, 94, 0.08);
            border: 1px solid rgba(244, 63, 94, 0.3);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1.25rem;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }
        .confirm-box input[type="checkbox"] {
            margin-top: 0.25rem;
            width: 18px;
            height: 18px;
            accent-color: var(--gta-pink);
            cursor: pointer;
        }
        .confirm-box label {
            margin: 0;
            font-size: 0.88rem;
            color: #fecdd3;
            font-weight: 600;
            cursor: pointer;
            line-height: 1.5;
        }

        /* Buttons */
        .btn-gta-submit {
            width: 100%;
            padding: 1.1rem;
            background: linear-gradient(135deg, var(--gta-pink), #e11d48);
            color: #ffffff;
            border: none;
            border-radius: 12px;
            font-weight: 800;
            font-size: 1.05rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.6rem;
            box-shadow: 0 4px 15px rgba(244, 63, 94, 0.3);
        }
        .btn-gta-submit:hover {
            filter: brightness(1.1);
            transform: translateY(-1px);
            box-shadow: 0 8px 25px rgba(244, 63, 94, 0.45);
        }
        .btn-gta-submit:disabled { opacity: 0.5; cursor: not-allowed; }

        /* Cookie Accordion */
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
        .tag-missing { background: rgba(234, 179, 8, 0.15); color: var(--gta-yellow); border: 1px solid rgba(234, 179, 8, 0.3); }

        /* Moments Cards */
        .gta-card {
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            border-left: 4px solid var(--gta-pink);
            transition: 0.2s;
        }
        .gta-card:hover { border-color: var(--gta-pink); box-shadow: 0 4px 20px rgba(244, 63, 94, 0.2); }
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
            background: rgba(244, 63, 94, 0.15);
            color: var(--gta-pink);
            font-weight: 800;
            border: 1px solid rgba(244, 63, 94, 0.4);
        }
        .btn-render-moment {
            padding: 0.65rem 1.25rem;
            background: linear-gradient(135deg, var(--gta-cyan), #0284c7);
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
            filter: brightness(1.1);
            transform: translateY(-1px);
        }

        .pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Top Nav Tabs -->
        <div class="nav-tabs">
            <a href="/" class="nav-tab-btn">⚡ Standard Clipper</a>
            <a href="/ai-studio" class="nav-tab-btn">🤖 AI Studio (Ollama / LLM)</a>
            <a href="/gta-auto-clipper" class="nav-tab-btn active">🎮 GTA-Auto-Clipper</a>
        </div>

        <div class="header">
            <div class="badge-chip">🌴 Vice City Autonomous Clipper</div>
            <h1>GTA Auto Clipper</h1>
            <p class="subtitle">Extract 9:16 high-energy GTA clips with <b>Pop-up Bouncing Yellow captions</b>, 6-second lead-in, profanity masking, player centering, and OpenRouter Free AI reasoning.</p>
        </div>

        <!-- Cookie Authentication Panel -->
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
                    <li>Open <a href="https://www.youtube.com" target="_blank" style="color: var(--gta-cyan);">youtube.com</a> in your browser.</li>
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
            <form id="gtaClipperForm">
                <div class="form-group">
                    <label for="videoUrl">🔗 GTA Gameplay Video / Stream URL</label>
                    <input type="text" id="videoUrl" class="input-box" required placeholder="https://www.youtube.com/watch?v=..." value="https://www.youtube.com/watch?v=YDNs_sPEcJc">
                </div>

                <!-- Visual Gameplay Confirmation (Core Rule from GTA-Auto-Clipper) -->
                <div class="confirm-box">
                    <input type="checkbox" id="gameplayConfirmed" checked required>
                    <label for="gameplayConfirmed">
                        <b>Visual Gameplay Confirmed:</b> I visually checked this video and verified actual GTA gameplay is visible on screen (not a talking-head podcast, discussion, or static thumbnail).
                    </label>
                </div>

                <div class="grid-2">
                    <div class="form-group">
                        <label for="layoutMode">📐 Screen Framing Layout</label>
                        <select id="layoutMode" class="input-box">
                            <option value="fill" selected>Fill 9:16 (Gameplay covers full canvas, centered on player)</option>
                            <option value="fit">Fit 9:16 (Original 16:9 gameplay over blurred background)</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="clipLength">⏱️ Highlight Duration & Lead-In</label>
                        <select id="clipLength" class="input-box">
                            <option value="30" selected>30 seconds (Starts 6s before peak reaction)</option>
                            <option value="45">45 seconds (Starts 6s before peak reaction)</option>
                            <option value="20">20 seconds (Short punchy spike)</option>
                            <option value="55">55 seconds (Full sequence)</option>
                        </select>
                    </div>
                </div>

                <div class="grid-2">
                    <div class="form-group">
                        <label for="captionStyle">💬 Caption Animation Style</label>
                        <select id="captionStyle" class="input-box">
                            <option value="popup_yellow" selected>✨ Pop-up Bouncing Yellow (GTA-Auto-Clipper ASS)</option>
                            <option value="karaoke">🟡 Continuous Hormozi Karaoke</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="creditTag">🏷️ Creator Attribution Credit (Watermark)</label>
                        <input type="text" id="creditTag" class="input-box" placeholder="@streamer (optional)">
                    </div>
                </div>

                <button type="submit" id="btnAnalyze" class="btn-gta-submit">
                    <span>🎮 Find GTA Gameplay Moments (OpenRouter Free AI)</span>
                </button>
            </form>
        </div>

        <!-- Discovered Moments Section -->
        <div id="gtaResultsSection" style="display: none;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 0.5rem;">
                <h2 style="font-size: 1.3rem; margin: 0; color: #fff;">🌴 High-Energy GTA Moments</h2>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <a href="https://docs.google.com/spreadsheets/d/1Bcbi86o-flI9J6uq4pg1H1tw1iCVXqu1sSZfZnBDMHU/edit?gid=0#gid=0" target="_blank" style="text-decoration: none; font-size: 0.78rem; padding: 4px 10px; border-radius: 999px; background: rgba(34,197,94,0.15); color: var(--accent-green); border: 1px solid rgba(34,197,94,0.4); font-weight: 700;">📊 Google Sheet</a>
                    <span id="gtaEngineBadge" style="font-size: 0.78rem; padding: 4px 10px; border-radius: 999px; background: rgba(244,63,94,0.2); color: var(--gta-pink); font-weight: 700;">Engine: OpenRouter Free</span>
                </div>
            </div>
            <div id="momentsList"></div>
        </div>

        <!-- Live Render Console Area -->
        <div id="gtaConsole" style="display: none; background: #060911; border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; margin-top: 1.5rem; font-family: 'JetBrains Mono', monospace;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <span id="gtaStatusIndicator" class="pulse" style="color: var(--gta-cyan); font-weight: bold;">● PROCESSING</span>
                <span id="gtaJobIdText" style="color: #94a3b8; font-size: 0.82rem;">Job: -</span>
            </div>
            <div id="gtaConsoleLogs" style="font-size: 0.85rem; color: #94a3b8; max-height: 200px; overflow-y: auto; white-space: pre-wrap;">Initializing...</div>
        </div>
    </div>

    <script>
        // Cookie panel
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

        // Form Submission
        const gtaClipperForm = document.getElementById('gtaClipperForm');
        const btnAnalyze = document.getElementById('btnAnalyze');
        const gtaResultsSection = document.getElementById('gtaResultsSection');
        const momentsList = document.getElementById('momentsList');
        const gtaConsole = document.getElementById('gtaConsole');
        const gtaStatusIndicator = document.getElementById('gtaStatusIndicator');
        const gtaJobIdText = document.getElementById('gtaJobIdText');
        const gtaConsoleLogs = document.getElementById('gtaConsoleLogs');
        const gtaEngineBadge = document.getElementById('gtaEngineBadge');

        gtaClipperForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = document.getElementById('videoUrl').value.trim();
            if (!url) return;

            btnAnalyze.disabled = true;
            btnAnalyze.innerHTML = `<span>⏳ Finding GTA Gameplay Moments...</span>`;
            gtaResultsSection.style.display = "none";
            momentsList.innerHTML = "";

            try {
                const payload = {
                    url: url,
                    gameplay_confirmed: document.getElementById('gameplayConfirmed').checked,
                    clip_len: parseInt(document.getElementById('clipLength').value, 10),
                    layout: document.getElementById('layoutMode').value,
                    caption_style: document.getElementById('captionStyle').value,
                    credit: document.getElementById('creditTag').value.trim()
                };

                const res = await fetch('/api/gta/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });

                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || "Analysis failed");
                }

                const data = await res.json();
                renderGtaMoments(data);
            } catch(err) {
                alert("Notice: " + err.message);
            } finally {
                btnAnalyze.disabled = false;
                btnAnalyze.innerHTML = `<span>🎮 Find GTA Gameplay Moments (OpenRouter Free AI)</span>`;
            }
        });

        function renderGtaMoments(data) {
            gtaResultsSection.style.display = "block";
            gtaEngineBadge.innerText = `Engine: ${data.provider || 'OpenRouter Free'}`;
            momentsList.innerHTML = "";

            (data.moments || []).forEach((m, idx) => {
                const card = document.createElement('div');
                card.className = "gta-card";
                const dur = Math.round((m.end || 0) - (m.start || 0));
                card.innerHTML = `
                    <div class="moment-header">
                        <div class="moment-title">GTA Moment #${idx+1}: ${m.title || 'GTA Gameplay Highlight'}</div>
                        <span class="moment-badge">🔥 Score: ${m.score || 95}/100</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #cbd5e1; font-style: italic; border-left: 2px solid var(--gta-pink); padding-left: 0.75rem;">
                        Spoken Hook: "${m.hook || 'Watch this GTA action...'}"
                    </div>
                    <div style="font-size: 0.8rem; color: #94a3b8; display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                        <span>⏱️ ${m.start}s - ${m.end}s (${dur}s duration • Starts 6s before reaction)</span>
                        <span>🏷️ ${(m.hashtags || ['#GTA6', '#GTAV', '#GamingShorts']).join(' ')}</span>
                    </div>
                    <button type="button" class="btn-render-moment" onclick="renderGtaMoment('${encodeURIComponent(JSON.stringify(m))}')">
                        <span>⚡ Render This 9:16 GTA Short (Pop-up Yellow Subtitles)</span>
                    </button>
                `;
                momentsList.appendChild(card);
            });
        }

        async function renderGtaMoment(encodedMoment) {
            const m = JSON.parse(decodeURIComponent(encodedMoment));
            const url = document.getElementById('videoUrl').value.trim();
            const layout = document.getElementById('layoutMode').value;
            const captionStyle = document.getElementById('captionStyle').value;
            const credit = document.getElementById('creditTag').value.trim();

            gtaConsole.style.display = "block";
            gtaStatusIndicator.innerText = "● QUEUED";
            gtaStatusIndicator.style.color = "var(--gta-cyan)";
            gtaConsoleLogs.innerText = `Submitting GTA clip "${m.title}" (${m.start}s - ${m.end}s)...`;

            try {
                const payload = {
                    url: url,
                    num_clips: 1,
                    start_time: String(m.start),
                    end_time: String(m.end),
                    framing_mode: layout === 'fill' ? 'split' : 'auto',
                    captions_mode: captionStyle === 'popup_yellow' ? 'gta_popup' : 'karaoke',
                    video_quality: "1080",
                    credit: credit,
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
                pollGtaJob(job.job_id, m.title);
            } catch(e) {
                gtaConsoleLogs.innerText = "Error: " + e.message;
                gtaStatusIndicator.innerText = "● FAILED";
                gtaStatusIndicator.style.color = "#ef4444";
            }
        }

        function pollGtaJob(jobId, title) {
            gtaJobIdText.innerText = "Job ID: " + jobId.slice(0, 8);
            gtaStatusIndicator.innerText = "● RENDERING";
            gtaStatusIndicator.style.color = "var(--gta-yellow)";

            const interval = setInterval(async () => {
                try {
                    const res = await fetch('/api/jobs/' + jobId);
                    if (!res.ok) return;
                    const job = await res.json();

                    gtaConsoleLogs.innerText = (job.logs || []).join(String.fromCharCode(10));
                    gtaConsoleLogs.scrollTop = gtaConsoleLogs.scrollHeight;

                    if (job.status === 'completed') {
                        clearInterval(interval);
                        gtaStatusIndicator.innerText = "● READY FOR DOWNLOAD";
                        gtaStatusIndicator.style.color = "var(--accent-green)";
                        gtaStatusIndicator.classList.remove('pulse');

                        const clip = (job.clips || [])[0];
                        if (clip) {
                            gtaConsoleLogs.innerText += String.fromCharCode(10) + `🎉 Success! Click to download: ${clip.download_url}`;
                            window.open(clip.download_url, '_blank');
                        }
                    } else if (job.status === 'failed') {
                        clearInterval(interval);
                        gtaStatusIndicator.innerText = "● FAILED";
                        gtaStatusIndicator.style.color = "#ef4444";
                        gtaStatusIndicator.classList.remove('pulse');
                    }
                } catch(e) {}
            }, 2500);
        }
    </script>
</body>
</html>
"""
