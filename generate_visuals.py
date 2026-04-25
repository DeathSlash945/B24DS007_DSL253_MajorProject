import json
import pandas as pd
import numpy as np

def build_final_dashboard(payload_file="dashboard_payload.json"):
    with open(payload_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    blacklist = [
        'Sexual Content', 'Nudity', 'Gore', 'Violent', 'NSFW', 'Hentai', 'Adult',
        'Utilities', 'Design & Illustration', 'Education', 'Software Training', 
        'Web Publishing', 'Audio Production', 'Video Production', 'Photo Editing',
        'Accounting', 'Game Development', 'Documentary', 'Tutorial', 'Animation & Modeling','Sports','Early Access'
    ]
    data['genre_list'] = [g for g in data['genre_list'] if g not in blacklist]
    
    data['top_games'] = [
        game for game in data['top_games'] 
        if not any(tag in str(game.get('genres', '')) for tag in blacklist)
    ]

    temp_df = pd.DataFrame(data['top_games'])
    temp_df['genres'] = temp_df['genres'].astype(str).replace('nan', '')
    temp_df = temp_df.replace([np.nan, np.inf, -np.inf], 0)
    data['top_games'] = temp_df.to_dict(orient='records')
    
    clean_json = json.dumps(data, allow_nan=False).replace("'", "\\'")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Steam Gaming Market Analysis</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            :root {{ --bg: #0f1113; --card: #1a1d1f; --border: #2d3135; --accent: #818cf8; }}
            body {{ background-color: var(--bg); color: #e2e8f0; padding-top: 80px; font-family: 'Inter', sans-serif; }}
            .nav-bar {{ position: fixed; top: 0; left: 0; right: 0; height: 65px; background: var(--card); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 2000; }}
            .studio-card {{ background: var(--card); border-radius: 12px; padding: 20px; border: 1px solid var(--border); }}
            .kpi-card {{ background: #1a1d1f; border: 1px solid var(--border); border-radius: 8px; padding: 12px; flex: 1; }}
            .dropdown-trigger {{ background: #2d3135; border: 1px solid #3f444a; color: #fff; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; }}
            .dropdown-menu {{ position: absolute; background: #2d3135; border: 1px solid #3f444a; border-radius: 6px; display: none; margin-top: 8px; width: 100%; max-height: 350px; overflow-y: auto; z-index: 2100; }}
            .dropdown-menu label {{ display: flex; align-items: center; padding: 10px; cursor: pointer; }}
            .chart-header {{ font-size: 10px; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem; }}
            .nav-btn {{ background: #2d3135; border: 1px solid #3f444a; padding: 4px 12px; border-radius: 4px; font-size: 11px; transition: all 0.2s; }}
            .nav-btn:hover:not(:disabled) {{ background: #3f444a; color: #818cf8; }}
            .nav-btn:disabled {{ opacity: 0.3; cursor: not-allowed; }}
        </style>
    </head>
    <body>

        <div class="nav-bar">
            <h1 class="text-lg font-bold tracking-tight">Steam Market <span class="text-indigo-400 text-sm italic">Analysis</span></h1>
            <div class="relative w-72">
                <button class="dropdown-trigger w-full flex justify-between items-center" onclick="toggleDrop()">
                    <span>Genre Selector</span>
                    <span id="count" class="bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded text-xs">0</span>
                </button>
                <div id="dropList" class="dropdown-menu"></div>
            </div>
        </div>

        <div class="px-10 pb-10 space-y-6">
            <div class="flex gap-4 items-stretch">
                <div class="kpi-card">
                    <p class="text-[9px] uppercase text-slate-500 font-bold mb-1">Avg Score</p>
                    <p id="kpi-score" class="text-xl font-bold text-indigo-400">--</p>
                </div>
                <div class="kpi-card">
                    <p class="text-[9px] uppercase text-slate-500 font-bold mb-1">Median Price</p>
                    <p id="kpi-price" class="text-xl font-bold text-emerald-400">--</p>
                </div>
                <div class="flex-[3] flex gap-3 bg-indigo-500/5 border border-indigo-500/20 rounded-lg p-3">
                    <div class="flex-1">
                        <p class="text-[9px] text-indigo-300 font-bold mb-1">PRICE GAP</p>
                        <p id="vac-price" class="text-[11px] font-medium text-slate-300">Calculating...</p>
                    </div>
                    <div class="w-px bg-indigo-500/20"></div>
                    <div class="flex-1">
                        <p class="text-[9px] text-indigo-300 font-bold mb-1">CONTENT GAP</p>
                        <p id="vac-length" class="text-[11px] font-medium text-slate-300">Calculating...</p>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div class="studio-card lg:col-span-7 h-[400px]">
                    <h2 class="chart-header">Performance Leaderboard (Top 10)</h2>
                    <div id="barLegend" class="flex flex-wrap gap-2 mb-3"></div>
                    <div style="height: 300px;"><canvas id="top10Chart"></canvas></div>
                </div>
                <div class="studio-card lg:col-span-5 h-[400px]">
                    <h2 class="chart-header">Market Seasonality</h2>
                    <div style="height: 320px;"><canvas id="lineChart"></canvas></div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div class="studio-card lg:col-span-6 h-[380px]">
                    <h2 class="chart-header">Price Tier Concentration</h2>
                    <div style="height: 300px;"><canvas id="tierChart"></canvas></div>
                </div>
                <div class="studio-card lg:col-span-6 h-[380px]">
                    <h2 class="chart-header">Genre Performance Benchmarking</h2>
                    <div style="height: 300px;"><canvas id="genreCompareChart"></canvas></div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div class="studio-card lg:col-span-8 h-[450px]">
                    <h2 class="chart-header">Positioning Matrix (Price vs Content Length)</h2>
                    <div style="height: 380px;"><canvas id="bubbleChart"></canvas></div>
                </div>
                <div class="studio-card lg:col-span-4 h-[450px]">
                    <h2 class="chart-header">Success Predictors</h2>
                    <div style="height: 380px;"><canvas id="factorChart"></canvas></div>
                </div>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-xl p-8">
                <h2 class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-6 text-center">Executive Strategic Narrative</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-10">
                    <div class="space-y-3">
                        <h3 class="text-xs font-bold text-indigo-400 uppercase tracking-wider">Market Landscape</h3>
                        <p id="sum-landscape" class="text-sm text-slate-400 leading-relaxed italic">--</p>
                    </div>
                    <div class="space-y-3">
                        <h3 class="text-xs font-bold text-emerald-400 uppercase tracking-wider">Value Opportunity</h3>
                        <p id="sum-opp" class="text-sm text-slate-400 leading-relaxed italic">--</p>
                    </div>
                    <div class="space-y-3">
                        <h3 class="text-xs font-bold text-amber-400 uppercase tracking-wider">Strategic Verdict</h3>
                        <p id="sum-rec" class="text-sm text-slate-400 leading-relaxed italic">--</p>
                    </div>
                </div>
            </div>

            <div class="studio-card">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="chart-header m-0">Detailed Market Leaders</h2>
                    <div class="flex items-center gap-3">
                        <span id="pageInfo" class="text-[10px] font-bold text-slate-500 uppercase tracking-widest"></span>
                        <div class="flex gap-1">
                            <button onclick="prevPage()" id="prevBtn" class="nav-btn">←</button>
                            <button onclick="nextPage()" id="nextBtn" class="nav-btn">→</button>
                        </div>
                    </div>
                </div>
                <div id="topGamesList" class="divide-y divide-slate-800"></div>
            </div>
        </div>

        <script>
            let appData = JSON.parse('{clean_json}');
            const COLORS = ['#818cf8', '#34d399', '#fbbf24', '#f87171', '#fb7185', '#2dd4bf', '#a78bfa'];
            const GENRE_COLORS = {{'Action': '#818cf8', 'Adventure': '#34d399', 'RPG': '#a78bfa', 'Strategy': '#fbbf24', 'Simulation': '#2dd4bf', 'Indie': '#f472b6'}};

            // Pagination State
            let currentListPool = [];
            let currentPage = 0;
            const PAGE_SIZE = 10;

            const dropList = document.getElementById('dropList');
            appData.genre_list.forEach(g => {{ dropList.innerHTML += `<label><input type="checkbox" value="${{g}}" onchange="refresh()" class="mr-3"> ${{g}}</label>`; }});

            function toggleDrop() {{ const d = document.getElementById('dropList'); d.style.display = d.style.display === 'block' ? 'none' : 'block'; }}

            let charts = {{}};

            function refresh() {{
                const selected = Array.from(document.querySelectorAll('#dropList input:checked')).map(i => i.value);
                document.getElementById('count').innerText = selected.length;

                let pool = [];
                selected.forEach(genre => {{ pool = pool.concat(appData.top_games.filter(g => g.genres.includes(genre))); }});

                if (pool.length > 0) {{
                    // Update KPIs and Logic
                    const avgScoreTotal = pool.reduce((a,b) => a + b.overall_success_score, 0) / pool.length;
                    const prices = pool.map(g => g.price).sort((a,b) => a-b);
                    const medianPrice = prices[Math.floor(prices.length/2)];
                    const topFeatures = appData.feature_importance.slice(0, 2).map(f => f.feat.replace('feat_','').toUpperCase());

                    document.getElementById('kpi-score').innerText = avgScoreTotal.toFixed(1);
                    document.getElementById('kpi-price').innerText = '$' + medianPrice.toFixed(2);
                    
                    const lowRange = pool.filter(g => g.price < 15).length;
                    const midRange = pool.filter(g => g.price >= 15 && g.price <= 40).length;
                    document.getElementById('vac-price').innerText = lowRange > midRange ? "Underserved: $20 - $40 Mid-Tier" : "Underserved: $0 - $15 Entry-Tier";
                    document.getElementById('vac-length').innerText = pool.filter(g => g.main_story > 20).length < (pool.length * 0.2) ? "Shortage of 20hr+ Content" : "20hr+ Market Saturated";

                    document.getElementById('sum-landscape').innerText = `Data for ${{selected.join(' & ')}} shows an avg score of ${{avgScoreTotal.toFixed(1)}}.`;
                    document.getElementById('sum-opp').innerText = `Median pricing at $${{medianPrice.toFixed(2)}} reveals a clear mid-range gap.`;
                    document.getElementById('sum-rec').innerText = `Focus on ${{topFeatures[0]}} and ${{topFeatures[1]}} for the highest probability of success.`;

                    // Set up Pool for List and Chart
                    const sortedUnique = Array.from(new Map(pool.map(g => [g.name, g])).values()).sort((a,b) => b.overall_success_score - a.overall_success_score);
                    currentListPool = sortedUnique;
                    currentPage = 0;
                    renderPaginatedList();

                    const top10 = sortedUnique.slice(0, 10);
                    const usedGenres = [...new Set(top10.map(g => g.genres.split('|')[0]))];
                    document.getElementById('barLegend').innerHTML = usedGenres.map(g => `<div class="flex items-center text-[10px] font-bold text-slate-500"><div class="w-2 h-2 rounded-sm mr-1" style="background:${{GENRE_COLORS[g] || '#475569'}}"></div>${{g.toUpperCase()}}</div>`).join('');

                    // Update Charts
                    const tiers = {{'0-10':0, '10-20':0, '20-40':0, '40-60':0, '60+':0}};
                    pool.forEach(g => {{ if(g.price < 10) tiers['0-10']++; else if(g.price < 20) tiers['10-20']++; else if(g.price < 40) tiers['20-40']++; else if(g.price < 60) tiers['40-60']++; else tiers['60+']++; }});
                    
                    const genreAverages = selected.map(genre => {{
                        const subPool = appData.top_games.filter(g => g.genres.includes(genre));
                        const avg = subPool.reduce((a,b) => a + b.overall_success_score, 0) / subPool.length;
                        return {{ genre, avg }};
                    }}).sort((a,b) => b.avg - a.avg);

                    updateChart('top10Chart', 'bar', top10.map(g => g.name), [{{ data: top10.map(g => g.overall_success_score), backgroundColor: top10.map(g => GENRE_COLORS[g.genres.split('|')[0]] || '#475569'), borderRadius: 4, barThickness: 15 }}], {{ indexAxis: 'y', plugins: {{ legend: {{ display: false }} }} }});
                    updateChart('lineChart', 'line', ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], selected.map((genre, idx) => ({{ label: genre, data: Array.from({{length: 12}}, (_, i) => {{ const games = appData.top_games.filter(g => g.genres.includes(genre) && new Date(g.release_date).getMonth() === i); return games.length ? games.reduce((a,c) => a + c.overall_success_score, 0) / games.length : 0; }}), borderColor: COLORS[idx % COLORS.length], tension: 0.3, fill: false }})));
                    updateChart('tierChart', 'bar', Object.keys(tiers), [{{ label: 'Game Count', data: Object.values(tiers), backgroundColor: '#818cf8', borderRadius: 4 }}], {{ scales: {{ y: {{ beginAtZero: true }} }} }});
                    
                    const minAvg = Math.min(...genreAverages.map(d => d.avg));
                    updateChart('genreCompareChart', 'bar', genreAverages.map(d => d.genre), [{{ label: 'Avg Success Score', data: genreAverages.map(d => d.avg), backgroundColor: '#34d399', borderRadius: 4 }}], {{ scales: {{ y: {{ min: Math.floor(minAvg - 5), ticks: {{ color: '#94a3b8' }} }} }} }});

                    updateChart('bubbleChart', 'bubble', [], selected.map((genre, idx) => ({{ label: genre, data: appData.top_games.filter(g => g.genres.includes(genre)).slice(0, 30).map(g => ({{ x: g.price, y: g.main_story, r: Math.max(g.overall_success_score/4, 4), name: g.name }})), backgroundColor: COLORS[idx % COLORS.length] + '44', borderColor: COLORS[idx % COLORS.length], borderWidth: 1 }})), {{ scales: {{ x: {{ type: 'logarithmic', title: {{ display: true, text: 'Price ($)' }} }}, y: {{ title: {{ display: true, text: 'Hours' }} }} }}, plugins: {{ tooltip: {{ callbacks: {{ label: (ctx) => `${{ctx.raw.name}}: $${{ctx.raw.x}} | ${{ctx.raw.y}}h` }} }} }} }});
                    updateChart('factorChart', 'doughnut', appData.feature_importance.map(f => f.feat.replace('feat_','').toUpperCase()), [{{ data: appData.feature_importance.map(f => f.val), backgroundColor: COLORS }}], {{ cutout: '80%' }});
                }}
            }}

            function renderPaginatedList() {{
                const start = currentPage * PAGE_SIZE;
                const end = start + PAGE_SIZE;
                const items = currentListPool.slice(start, end);
                const total = currentListPool.length;

                document.getElementById('pageInfo').innerText = `Showing ${{start + 1}}-${{Math.min(end, total)}} of ${{total}}`;
                document.getElementById('prevBtn').disabled = currentPage === 0;
                document.getElementById('nextBtn').disabled = end >= total;

                document.getElementById('topGamesList').innerHTML = items.map((g, i) => `
                    <div class="flex justify-between items-center py-4">
                        <div class="flex items-center gap-4"><span class="text-slate-500 font-black text-lg">#${{start + i + 1}}</span>
                            <div><p class="font-bold text-white text-sm">${{g.name}}</p><p class="text-[10px] text-slate-500 uppercase">${{g.genres.replace(/\|/g, ' / ')}}</p></div>
                        </div>
                        <div class="text-right"><p class="text-xs font-bold text-indigo-400">${{g.overall_success_score.toFixed(1)}} pts</p><p class="text-[10px] text-slate-400">$${{g.price.toFixed(2)}} | ${{g.main_story}} hrs</p></div>
                    </div>`).join('');
            }}

            function nextPage() {{ currentPage++; renderPaginatedList(); }}
            function prevPage() {{ currentPage--; renderPaginatedList(); }}

            function updateChart(id, type, labels, datasets, opts = {{}}) {{
                if (charts[id]) charts[id].destroy();
                charts[id] = new Chart(document.getElementById(id), {{ type: type, data: {{ labels: labels, datasets: datasets }}, options: Object.assign({{ maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 9 }} }} }} }} }}, opts) }});
            }}

            if(appData.genre_list.length > 0) {{ const first = document.querySelector('#dropList input'); if(first) {{ first.checked = true; refresh(); }} }}
        </script>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    build_final_dashboard()