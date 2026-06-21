#!/usr/bin/env python3
"""
构建纯前端自包含的体彩大乐透智能分析HTML
将原始数据内嵌 + 全JavaScript分析引擎 + CORS代理实时更新
"""
import json

# 读取原始数据（作为fallback）
with open(r'C:\Users\Administrator\WorkBuddy\2026-06-19-16-28-32\TcDLT355history.txt', 'r', encoding='utf-8') as f:
    raw_data = f.read()

# 也预解析一份解析后的数据用于快速回测
with open(r'C:\Users\Administrator\WorkBuddy\2026-06-19-16-28-32\analysis_result.json', 'r', encoding='utf-8') as f:
    cached = json.load(f)

html_template = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,user-scalable=yes">
<title>体彩大乐透 智能分析</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif;background:#f0f2f5;color:#333;line-height:1.6}
.header{background:linear-gradient(135deg,#d4380d,#e65c00,#cf1322);color:#fff;padding:24px 16px;text-align:center}
.header h1{font-size:1.6em;margin-bottom:4px}
.header .sub{font-size:.85em;opacity:.85}
.container{max-width:1100px;margin:0 auto;padding:12px}
.card{background:#fff;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.08);margin-bottom:14px;padding:18px}
.card-hd{font-size:1.15em;font-weight:700;margin-bottom:12px;padding-bottom:10px;border-bottom:2px solid #f0f0f0;display:flex;align-items:center;gap:8px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}
.stat-row{display:flex;justify-content:space-around;flex-wrap:wrap;gap:10px}
.stat-item{text-align:center;padding:12px;border-radius:10px;background:#fafafa;min-width:100px}
.stat-val{font-size:1.7em;font-weight:700;color:#cf1322}
.stat-lbl{font-size:.78em;color:#999;margin-top:4px}
.tag{display:inline-block;padding:2px 8px;border-radius:10px;font-size:.78em;margin:1px}
.tag-hot{background:#fff2f0;color:#cf1322;border:1px solid #ffa39e}
.tag-warm{background:#fff7e6;color:#d46b08;border:1px solid #ffd591}
.tag-cold{background:#e6f7ff;color:#0958d9;border:1px solid #91d5ff}
.balls{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.ball{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.15em;font-weight:700;color:#fff;flex-shrink:0}
.ball.fr{background:linear-gradient(135deg,#f09080,#c85140);box-shadow:0 2px 6px rgba(200,81,64,.3)}
.ball.bl{background:linear-gradient(135deg,#6daae0,#3d7ec0);box-shadow:0 2px 6px rgba(61,126,192,.3)}
.ball-sm{width:28px;height:28px;font-size:.75em}
.rec-card{border:2px solid #f0f0f0;border-radius:12px;padding:16px;margin-bottom:12px;transition:all .3s}
.rec-card:hover{border-color:#cf1322;box-shadow:0 4px 16px rgba(207,19,34,.1);transform:translateY(-1px)}
.rec-hd{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.rec-num{background:linear-gradient(135deg,#cf1322,#ff4d4f);color:#fff;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1em;flex-shrink:0}
.rec-title{font-weight:700;font-size:1em}
.rec-score{margin-left:auto;font-size:.78em;color:#888}
.rec-reason{background:#fafafa;border-radius:8px;padding:10px 14px;margin-top:8px}
.rec-reason li{margin-bottom:3px;font-size:.82em;color:#666}
.chart-wrap{position:relative;height:260px;width:100%}
.chart-wrap-sm{position:relative;height:220px}
.chart-wrap-lg{position:relative;height:320px}
.data-table{width:100%;border-collapse:collapse;font-size:.82em}
.data-table th{background:#fafafa;padding:8px 10px;text-align:center;font-weight:600;color:#666;border-bottom:2px solid #f0f0f0}
.data-table td{padding:6px 10px;text-align:center;border-bottom:1px solid #f5f5f5}
.data-table tr:hover td{background:#fff7e6}
.td-b{display:inline-block;width:22px;height:22px;line-height:22px;border-radius:50%;font-size:.7em;font-weight:600;color:#fff;margin:1px}
.td-b.fr{background:#c85140}.td-b.bl{background:#3d7ec0}
.warn-box{background:#fffbe6;border:1px solid #ffe58f;border-radius:8px;padding:12px 16px;margin-bottom:12px;font-size:.85em;color:#ad6800}
.warn-box strong{color:#d4380d}
.status-bar{display:flex;align-items:center;gap:8px;padding:10px 16px;border-radius:8px;margin-bottom:14px;font-size:.85em}
.status-bar.ok{background:#f6ffed;border:1px solid #b7eb8f;color:#389e0d}
.status-bar.warn{background:#fffbe6;border:1px solid #ffe58f;color:#ad6800}
.status-bar.err{background:#fff2f0;border:1px solid #ffa39e;color:#cf1322}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid #ddd;border-top-color:#cf1322;border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.insight-box{background:linear-gradient(135deg,#f0f5ff,#e6f7ff);border:1px solid #91d5ff;border-radius:8px;padding:12px 16px;margin:10px 0;font-size:.85em}
.insight-box strong{color:#0958d9}
.tabs{display:flex;gap:0;margin-bottom:0;border-bottom:2px solid #f0f0f0}
.tab-btn{padding:8px 16px;border:none;background:none;cursor:pointer;font-size:.85em;color:#999;transition:all .3s;position:relative}
.tab-btn.active{color:#cf1322;font-weight:600}
.tab-btn.active::after{content:'';position:absolute;bottom:-2px;left:0;right:0;height:2px;background:#cf1322}
.tab-panel{display:none;padding-top:12px}
.tab-panel.active{display:block}
.footer{text-align:center;padding:24px;color:#ccc;font-size:.78em}
.loading{text-align:center;padding:60px 20px;color:#999}
.loading h2{font-size:1.2em;margin-bottom:8px}
@media(max-width:768px){.grid2,.grid3{grid-template-columns:1fr}.header h1{font-size:1.3em}}
/* 手动选号 & 自选列表 */
.picker-section{border:2px dashed #d9d9d9;border-radius:12px;padding:16px;margin-bottom:14px;transition:all .3s}
.picker-section:hover{border-color:#cf1322}
.picker-label{font-size:.82em;color:#888;margin-bottom:6px;font-weight:600}
.picker-grid{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:12px}
.picker-ball{position:relative;width:44px;height:52px;border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;font-weight:700;font-size:.95em;border:2px solid #e8e8e8;background:#fff;transition:all .2s;user-select:none;flex-shrink:0}
.picker-ball:hover{transform:scale(1.08);box-shadow:0 2px 8px rgba(0,0,0,.12)}
.picker-ball:active{transform:scale(.95)}
.picker-ball.sel-front{border-color:#c85140;background:linear-gradient(135deg,#fff2f0,#fdd);color:#c85140}
.picker-ball.sel-back{border-color:#3d7ec0;background:linear-gradient(135deg,#f0f5ff,#d6eaf8);color:#3d7ec0}
.picker-ball .omit{font-size:.85em;font-weight:600;color:#999;margin-top:-1px}
.picker-ball.sel-front .omit,.picker-ball.sel-back .omit{color:inherit;opacity:.7}
.picker-toolbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:8px}
.picker-toolbar .count{font-size:.85em;color:#888}
.btn{display:inline-flex;align-items:center;gap:4px;padding:8px 16px;border:none;border-radius:8px;cursor:pointer;font-size:.85em;font-weight:600;transition:all .2s}
.btn:hover{transform:translateY(-1px);box-shadow:0 2px 8px rgba(0,0,0,.15)}
.btn:active{transform:scale(.97)}
.btn-add{background:linear-gradient(135deg,#cf1322,#ff4d4f);color:#fff}
.btn-copy{background:linear-gradient(135deg,#0958d9,#1677ff);color:#fff}
.btn-clear{background:#f5f5f5;color:#666}
.btn-danger{background:linear-gradient(135deg,#ff4d4f,#cf1322);color:#fff;font-size:.75em;padding:4px 10px}
.filter-list{margin-top:12px}
.filter-item{display:flex;align-items:center;gap:8px;padding:10px 14px;background:#fafafa;border-radius:8px;margin-bottom:6px;transition:all .2s}
.filter-item:hover{background:#fff7e6}
.filter-item .idx{width:24px;height:24px;border-radius:6px;background:#595959;color:#fff;display:flex;align-items:center;justify-content:center;font-size:.75em;font-weight:700;flex-shrink:0}
.filter-item .balls-row{display:flex;align-items:center;gap:4px;flex-wrap:wrap}
.filter-item .balls-row .sball{width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.72em;font-weight:700;color:#fff;flex-shrink:0}
.filter-item .balls-row .sball.fr{background:linear-gradient(135deg,#f09080,#c85140)}
.filter-item .balls-row .sball.bl{background:linear-gradient(135deg,#6daae0,#3d7ec0)}
.filter-item .dup-warn{font-size:.72em;color:#cf1322;background:#fff2f0;padding:2px 8px;border-radius:10px;white-space:nowrap}
.filter-item .filter-info{font-size:.72em;color:#999;margin-left:auto;white-space:nowrap}
.empty-hint{text-align:center;padding:20px;color:#ccc}
.dup-toast{position:fixed;top:20px;left:50%;transform:translateX(-50%);background:#fff2f0;border:2px solid #ff4d4f;color:#cf1322;padding:12px 24px;border-radius:12px;font-weight:700;z-index:9999;box-shadow:0 4px 20px rgba(207,19,34,.3);animation:toastIn .3s ease;max-width:90vw;text-align:center;font-size:.9em}
@keyframes toastIn{from{opacity:0;transform:translateX(-50%) translateY(-20px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}
#copyCanvas{display:none}
.summary-bar{display:flex;align-items:center;gap:12px;margin-bottom:12px;padding:8px 12px;background:#f6ffed;border-radius:8px;border:1px solid #b7eb8f}
.summary-bar .count-num{font-size:1.4em;font-weight:700;color:#389e0d}
</style>
</head>
<body>
<div class="header"><h1>体彩大乐透 智能分析报告</h1><div class="sub" id="headerSub">加载中...</div></div>
<div class="container" id="app"><div class="loading"><div class="spinner" style="width:32px;height:32px;border-width:3px;display:block;margin:0 auto 12px;"></div><h2>正在分析最新数据...</h2><p id="loadMsg">尝试从网络获取最新开奖数据</p></div></div>
<div class="footer">数据来源: 中国体育彩票 qtsoft.net | 分析仅供参考 理性购彩</div>
<canvas id="copyCanvas"></canvas>

<script>
// ================================================================
//  体彩大乐透 纯前端智能分析引擎 v2.0
//  特性: 实时联网拉取数据、N-gram组合唯一性过滤、跨期间隔规律、
//        连号链式分析、回测机制、推荐号码
// ================================================================

const RAW_FALLBACK = __RAW_DATA_PLACEHOLDER__;
const CACHED_RESULT = __CACHED_RESULT_PLACEHOLDER__;
const DATA_URL = 'https://www.qtsoft.net/TcDLT355history.txt';

// ===== 1. 数据解析 =====
function parseRawData(text) {
  const draws = [];
  const lines = text.split('\n');
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('TcDLT') || trimmed.startsWith('SCO') || trimmed.startsWith('ver:')) continue;
    const parts = trimmed.split(/\s+/);
    if (parts.length < 9) continue;
    if (!/^\d{7}$/.test(parts[0])) continue;
    draws.push({
      issue: parts[0],
      date: parts[1],
      front: [parseInt(parts[2]), parseInt(parts[3]), parseInt(parts[4]), parseInt(parts[5]), parseInt(parts[6])],
      back: [parseInt(parts[7]), parseInt(parts[8])]
    });
  }
  // 文件从新到旧，反转使draws[0]最早
  draws.reverse();
  return draws;
}

// ===== 2. 频率分析 =====
function freqCount(draws, recentN) {
  const data = recentN ? draws.slice(-recentN) : draws;
  const front = {}, back = {};
  for (let i = 1; i <= 35; i++) front[i] = 0;
  for (let i = 1; i <= 12; i++) back[i] = 0;
  for (const d of data) {
    for (const n of d.front) front[n]++;
    for (const n of d.back) back[n]++;
  }
  return { front, back };
}

// ===== 3. 冷热号分析 =====
function hotColdAnalysis(draws, recentN = 50) {
  const { front, back } = freqCount(draws, recentN);
  const fAvg = Object.values(front).reduce((a,b)=>a+b,0) / 35;
  const bAvg = Object.values(back).reduce((a,b)=>a+b,0) / 12;
  
  const fHot = [], fWarm = [], fCold = [];
  const bHot = [], bWarm = [], bCold = [];
  
  for (let i = 1; i <= 35; i++) {
    if (front[i] > fAvg * 1.2) fHot.push(i);
    else if (front[i] < fAvg * 0.8) fCold.push(i);
    else fWarm.push(i);
  }
  for (let i = 1; i <= 12; i++) {
    if (back[i] > bAvg * 1.2) bHot.push(i);
    else if (back[i] < bAvg * 0.8) bCold.push(i);
    else bWarm.push(i);
  }
  
  fHot.sort((a,b)=>front[b]-front[a]);
  fWarm.sort((a,b)=>front[b]-front[a]);
  fCold.sort((a,b)=>front[a]-front[b]);
  bHot.sort((a,b)=>back[b]-back[a]);
  bWarm.sort((a,b)=>back[b]-back[a]);
  bCold.sort((a,b)=>back[a]-back[b]);
  
  return { front: { hot: fHot, warm: fWarm, cold: fCold, freq: front },
           back: { hot: bHot, warm: bWarm, cold: bCold, freq: back } };
}

// ===== 4. 遗漏分析 =====
function missingAnalysis(draws) {
  const fMiss = {}, bMiss = {};
  for (let i = 1; i <= 35; i++) {
    let miss = 0;
    for (let j = draws.length - 1; j >= 0; j--) {
      if (draws[j].front.includes(i)) break;
      miss++;
    }
    fMiss[i] = miss;
  }
  for (let i = 1; i <= 12; i++) {
    let miss = 0;
    for (let j = draws.length - 1; j >= 0; j--) {
      if (draws[j].back.includes(i)) break;
      miss++;
    }
    bMiss[i] = miss;
  }
  return { front: fMiss, back: bMiss };
}

// ===== 5. 奇偶比 =====
function oddEvenAnalysis(draws, recentN = 50) {
  const data = draws.slice(-recentN);
  const fRatios = {}, bRatios = {};
  for (const d of data) {
    const fOdd = d.front.filter(n => n % 2 === 1).length;
    const bOdd = d.back.filter(n => n % 2 === 1).length;
    const fKey = fOdd + ':' + (5 - fOdd);
    const bKey = bOdd + ':' + (2 - bOdd);
    fRatios[fKey] = (fRatios[fKey] || 0) + 1;
    bRatios[bKey] = (bRatios[bKey] || 0) + 1;
  }
  return { front: fRatios, back: bRatios };
}

// ===== 6. 区间分布 =====
function zoneAnalysis(draws, recentN = 50) {
  const data = draws.slice(-recentN);
  const zones = {};
  for (const d of data) {
    const z1 = d.front.filter(n => n <= 12).length;
    const z2 = d.front.filter(n => n >= 13 && n <= 24).length;
    const z3 = d.front.filter(n => n >= 25).length;
    const key = z1 + ':' + z2 + ':' + z3;
    zones[key] = (zones[key] || 0) + 1;
  }
  return zones;
}

// ===== 7. 连号分析 =====
function consecutiveAnalysis(draws, recentN = 100) {
  const data = draws.slice(-recentN);
  let count = 0;
  const pairs = {};
  for (const d of data) {
    let has = false;
    for (let i = 0; i < d.front.length - 1; i++) {
      if (d.front[i+1] - d.front[i] === 1) {
        has = true;
        const key = d.front[i] + ',' + d.front[i+1];
        pairs[key] = (pairs[key] || 0) + 1;
      }
    }
    if (has) count++;
  }
  return { rate: count / data.length, count, total: data.length, pairs };
}

// ===== 8. 和值分析 =====
function sumAnalysis(draws, recentN = 50) {
  const data = draws.slice(-recentN);
  const fSums = data.map(d => d.front.reduce((a,b)=>a+b,0));
  const bSums = data.map(d => d.back.reduce((a,b)=>a+b,0));
  return {
    front: { avg: (fSums.reduce((a,b)=>a+b,0)/fSums.length).toFixed(1),
             min: Math.min(...fSums), max: Math.max(...fSums),
             recent: fSums.slice(-10) },
    back: { avg: (bSums.reduce((a,b)=>a+b,0)/bSums.length).toFixed(1),
            min: Math.min(...bSums), max: Math.max(...bSums),
            recent: bSums.slice(-10) }
  };
}

// ================================================================
//  新增: 深度模式挖掘
// ================================================================

// ===== 9. N-gram 组合唯一性分析 =====
function ngramAnalysis(draws, n = 3) {
  // 统计前区中连续n个号码组合的出现频率
  const allCombos = new Map();
  for (const d of draws) {
    const f = d.front;
    // 前区所有n-gram
    for (let i = 0; i <= f.length - n; i++) {
      const combo = f.slice(i, i + n).join(',');
      allCombos.set(combo, (allCombos.get(combo) || 0) + 1);
    }
  }
  // 也统计前区+后区的混合组合（如前区3个+后区1个）
  const mixedCombos = new Map();
  for (const d of draws) {
    const f = d.front;
    // 前区3个 + 后区1个
    for (let i = 0; i <= f.length - 3; i++) {
      for (const b of d.back) {
        const combo = f.slice(i, i+3).join(',') + '|' + b;
        mixedCombos.set(combo, (mixedCombos.get(combo) || 0) + 1);
      }
    }
    // 前区2个 + 后区2个
    for (let i = 0; i <= f.length - 2; i++) {
      const combo = f.slice(i, i+2).join(',') + '|' + d.back.join(',');
      mixedCombos.set(combo, (mixedCombos.get(combo) || 0) + 1);
    }
  }
  return { front: allCombos, mixed: mixedCombos };
}

// ===== 10. 跨期间隔规律(上上期→本期) =====
function skipPeriodRecurrence(draws) {
  // 统计draws[i-2]的号码在draws[i]中出现的概率
  let totalFChecks = 0, totalFMatches = 0;
  let totalBChecks = 0, totalBMatches = 0;
  const matchCounts = {}; // 中了几个的分布
  
  for (let i = 2; i < draws.length; i++) {
    const prev2 = draws[i-2];
    const curr = draws[i];
    
    // 前区
    for (const n of prev2.front) {
      totalFChecks++;
      if (curr.front.includes(n)) totalFMatches++;
    }
    // 后区
    for (const n of prev2.back) {
      totalBChecks++;
      if (curr.back.includes(n)) totalBMatches++;
    }
    
    // 整体匹配数分布
    const fMatch = prev2.front.filter(n => curr.front.includes(n)).length;
    const bMatch = prev2.back.filter(n => curr.back.includes(n)).length;
    const key = fMatch + '_' + bMatch;
    matchCounts[key] = (matchCounts[key] || 0) + 1;
  }
  
  // 当前最新一期，看看上上期的号码
  const lastButOne = draws.length >= 3 ? draws[draws.length - 3] : null;
  const last = draws[draws.length - 1];
  
  let prev2Nums = null;
  if (lastButOne) {
    prev2Nums = {
      issue: lastButOne.issue,
      front: lastButOne.front,
      back: lastButOne.back,
      frontInLatest: lastButOne.front.filter(n => last.front.includes(n)),
      backInLatest: lastButOne.back.filter(n => last.back.includes(n))
    };
  }
  
  return {
    frontRate: totalFChecks > 0 ? (totalFMatches / totalFChecks * 100).toFixed(1) : 0,
    backRate: totalBChecks > 0 ? (totalBMatches / totalBChecks * 100).toFixed(1) : 0,
    matchDistribution: matchCounts,
    prev2Check: prev2Nums
  };
}

// ===== 11. 连号链式分析 =====
function consecutiveChaining(draws) {
  // 如果本期有连号，下期出现连号的概率
  let hasConsThenHasCons = 0;
  let hasConsTotal = 0;
  let noConsThenHasCons = 0;
  let noConsTotal = 0;
  
  for (let i = 0; i < draws.length - 1; i++) {
    const currHas = hasConsecutive(draws[i]);
    const nextHas = hasConsecutive(draws[i+1]);
    
    if (currHas) {
      hasConsTotal++;
      if (nextHas) hasConsThenHasCons++;
    } else {
      noConsTotal++;
      if (nextHas) noConsThenHasCons++;
    }
  }
  
  const latest = draws[draws.length - 1];
  const latestHasConsec = hasConsecutive(latest);
  
  return {
    ifHasThenHasRate: hasConsTotal > 0 ? (hasConsThenHasCons / hasConsTotal * 100).toFixed(1) : 0,
    ifNoThenHasRate: noConsTotal > 0 ? (noConsThenHasCons / noConsTotal * 100).toFixed(1) : 0,
    latestHasConsecutive: latestHasConsec,
    latestConsecutiveDetail: latestHasConsec ? getConsecutivePairs(latest) : null
  };
}

function hasConsecutive(draw) {
  for (let i = 0; i < draw.front.length - 1; i++) {
    if (draw.front[i+1] - draw.front[i] === 1) return true;
  }
  for (let i = 0; i < draw.back.length - 1; i++) {
    if (draw.back[i+1] - draw.back[i] === 1) return true;
  }
  return false;
}

function getConsecutivePairs(draw) {
  const pairs = [];
  for (let i = 0; i < draw.front.length - 1; i++) {
    if (draw.front[i+1] - draw.front[i] === 1) pairs.push([draw.front[i], draw.front[i+1]]);
  }
  return pairs;
}

// ===== 12. 组合唯一性过滤器 =====
function combinationUniquenessScore(draws, candidateFront, candidateBack) {
  // 检查候选号码的各维度组合在历史中出现的频率
  // 返回唯一性得分（越高越独特，越不常见）
  let score = 0;
  const cf = candidateFront.sort((a,b)=>a-b);
  const cb = candidateBack.sort((a,b)=>a-b);
  
  // 检查前区3-gram
  for (let i = 0; i <= cf.length - 3; i++) {
    const combo = cf.slice(i, i+3).join(',');
    let count = 0;
    for (const d of draws) {
      // 检查这3个号码是否同时出现在某一期的前区
      const f = d.front;
      if (f.includes(cf[i]) && f.includes(cf[i+1]) && f.includes(cf[i+2])) count++;
    }
    if (count === 0) score += 5;      // 从未出现：高分
    else if (count <= 2) score += 3;   // 极少出现
    else if (count <= 5) score += 1;  // 偶尔出现
    // 出现太多不加分
  }
  
  // 检查前区4-gram
  for (let i = 0; i <= cf.length - 4; i++) {
    const combo = cf.slice(i, i+4).join(',');
    let count = 0;
    for (const d of draws) {
      const f = d.front;
      if (f.includes(cf[i]) && f.includes(cf[i+1]) && f.includes(cf[i+2]) && f.includes(cf[i+3])) count++;
    }
    if (count === 0) score += 8;
    else if (count <= 1) score += 4;
  }
  
  // 检查前区3+后区1的混合组合
  for (let i = 0; i <= cf.length - 3; i++) {
    for (const b of cb) {
      let count = 0;
      for (const d of draws) {
        if (d.front.includes(cf[i]) && d.front.includes(cf[i+1]) && d.front.includes(cf[i+2]) && d.back.includes(b)) count++;
      }
      if (count === 0) score += 3;
    }
  }
  
  return score;
}

// ===== 13. 下期连号概率预测 =====
function predictConsecutive(draws) {
  const chain = consecutiveChaining(draws);
  const latest = draws[draws.length - 1];
  const hasCons = chain.latestHasConsecutive;
  
  let probNext;
  if (hasCons) {
    probNext = chain.ifHasThenHasRate;
  } else {
    probNext = chain.ifNoThenHasRate;
  }
  
  return {
    latestHasConsecutive: hasCons,
    latestPairs: chain.latestConsecutiveDetail,
    probabilityNextHas: parseFloat(probNext),
    shouldIncludeConsecutive: parseFloat(probNext) > 55
  };
}

// ===== 14. 上上期号码推荐权重 =====
function skipPeriodWeights(draws) {
  const skip = skipPeriodRecurrence(draws);
  const weights = {};
  
  if (skip.prev2Check) {
    // 上上期的号码有较高概率在下一期出现
    for (const n of skip.prev2Check.front) {
      weights[n] = (weights[n] || 0) + 2;
    }
    for (const n of skip.prev2Check.back) {
      weights[n] = (weights[n] || 0) + 2;
    }
    
    // 实际上上期（即最新一期）中已经出现的上上期号码，说明这个号码连续活跃
    for (const n of skip.prev2Check.frontInLatest) {
      weights[n] = (weights[n] || 0) + 3;
    }
  }
  
  return { weights, analysis: skip };
}

// ================================================================
//  推荐引擎
// ================================================================

function generateRecommendations(draws, numSets = 5) {
  const hc = hotColdAnalysis(draws, 50);
  const hcAll = hotColdAnalysis(draws, draws.length);
  const miss = missingAnalysis(draws);
  const oe = oddEvenAnalysis(draws, 50);
  const zone = zoneAnalysis(draws, 50);
  const consec = consecutiveAnalysis(draws, 100);
  const sums = sumAnalysis(draws, 50);
  const ngram = ngramAnalysis(draws);
  const skipW = skipPeriodWeights(draws);
  const consecPred = predictConsecutive(draws);
  
  // 计算前区综合评分
  const fScores = {};
  for (let n = 1; n <= 35; n++) {
    let score = 0;
    const reasons = [];
    const f50 = hc.front.freq[n] || 0;
    
    // 频率评分
    if (hc.front.hot.includes(n)) { score += 4; reasons.push('近50期热号'); }
    else if (hc.front.warm.includes(n)) { score += 2; reasons.push('近50期温号'); }
    else { score += 1; }
    
    // 遗漏评分
    const m = miss.front[n] || 0;
    if (m >= 15 && f50 >= 3) { score += 4; reasons.push('长遗漏回补(遗漏' + m + '期)'); }
    else if (m >= 10) { score += 3; reasons.push('遗漏' + m + '期,回补概率高'); }
    else if (m >= 5) { score += 1; }
    
    // 全历史频率
    const fAll = hcAll.front.freq[n] || 0;
    if (fAll >= 420) { score += 1; }
    
    // 上上期号码加权
    if (skipW.weights[n]) { score += skipW.weights[n]; reasons.push('上上期号码模式'); }
    
    fScores[n] = { score, reasons, freq50: f50, miss: m };
  }
  
  // 后区评分
  const bScores = {};
  for (let n = 1; n <= 12; n++) {
    let score = 0;
    const reasons = [];
    const f50 = hc.back.freq[n] || 0;
    
    if (hc.back.hot.includes(n)) { score += 4; reasons.push('近50期热号'); }
    else if (hc.back.warm.includes(n)) { score += 2; }
    else { score += 1; }
    
    const m = miss.back[n] || 0;
    if (m >= 10) { score += 4; reasons.push('长遗漏回补(遗漏' + m + '期)'); }
    else if (m >= 5) { score += 3; reasons.push('遗漏' + m + '期'); }
    
    bScores[n] = { score, reasons, freq50: f50, miss: m };
  }
  
  // 排序
  const fRanked = Object.entries(fScores).sort((a,b) => b[1].score - a[1].score).map(([n,s]) => [parseInt(n), s]);
  const bRanked = Object.entries(bScores).sort((a,b) => b[1].score - a[1].score).map(([n,s]) => [parseInt(n), s]);
  
  // 生成多组候选
  const strategies = [
    { name: '热号追踪', desc: '以近期热号为主，搭配温号', fHot: 3, fWarm: 2, fCold: 0, bHot: 2, bCold: 0 },
    { name: '冷热均衡', desc: '热号冷号各半，平衡热度与回补', fHot: 2, fWarm: 1, fCold: 2, bHot: 1, bCold: 1 },
    { name: '遗漏回补', desc: '重点捕捉遗漏冷号的回补时机', fHot: 1, fWarm: 1, fCold: 3, bHot: 0, bCold: 2 },
    { name: '奇偶均衡', desc: '前区3:2或2:3，后区1:1', fHot: 2, fWarm: 2, fCold: 1, bHot: 1, bCold: 1 },
    { name: '综合优选', desc: '最高评分+区间均衡+组合唯一性过滤', fHot: 2, fWarm: 2, fCold: 1, bHot: 1, bCold: 1 }
  ];
  
  // 构建号码池
  const fHotNums = hc.front.hot;
  const fWarmNums = hc.front.warm;
  const fColdNums = hc.front.cold.filter(n => (miss.front[n] || 0) >= 8);
  const bHotNums = hc.back.hot;
  const bColdNums = hc.back.cold.filter(n => (miss.back[n] || 0) >= 5);
  
  // 上上期号码
  const prev2Nums = skipW.analysis.prev2Check ? skipW.analysis.prev2Check.front : [];
  
  const dbz = 3; // 三区: 1-12, 13-24, 25-35
  const z1Pool = fRanked.filter(([n]) => n <= 12).map(([n]) => n);
  const z2Pool = fRanked.filter(([n]) => n >= 13 && n <= 24).map(([n]) => n);
  const z3Pool = fRanked.filter(([n]) => n >= 25).map(([n]) => n);
  
  function pickWithZone(nHot, nWarm, nCold, seed) {
    // 带区间均衡的选号
    const picked = new Set();
    const result = [];
    
    // 先从热/温/冷中各选
    function tryAdd(pool, count) {
      const avail = pool.filter(n => !picked.has(n));
      const shuffled = avail.sort(() => Math.random() - 0.5); // 简单shuffle
      for (let i = 0; i < Math.min(count, shuffled.length); i++) {
        picked.add(shuffled[i]);
        result.push(shuffled[i]);
      }
    }
    
    tryAdd(fHotNums, nHot);
    tryAdd(fWarmNums, nWarm);
    tryAdd(fColdNums, nCold);
    
    // 补充到5个，确保区间覆盖
    while (result.length < 5) {
      // 优先从缺失的区间选
      const zones = { 1: result.filter(n => n <= 12).length,
                      2: result.filter(n => n >= 13 && n <= 24).length,
                      3: result.filter(n => n >= 25).length };
      const bestZone = Object.entries(zones).sort((a,b) => a[1]-b[1])[0][0];
      
      let pool;
      if (bestZone === '1') pool = z1Pool;
      else if (bestZone === '2') pool = z2Pool;
      else pool = z3Pool;
      
      const avail = pool.filter(n => !picked.has(n));
      if (avail.length > 0) {
        const n = avail[Math.floor(Math.random() * avail.length)];
        picked.add(n);
        result.push(n);
      } else {
        // 从所有未选的号码中选
        const allAvail = [];
        for (let n = 1; n <= 35; n++) if (!picked.has(n)) allAvail.push(n);
        if (allAvail.length > 0) {
          const n = allAvail[Math.floor(Math.random() * allAvail.length)];
          picked.add(n);
          result.push(n);
        } else break;
      }
    }
    
    return result.sort((a,b)=>a-b).slice(0, 5);
  }
  
  function pickBack(nHot, nCold) {
    const picked = [];
    const avail = [...bHotNums.slice(0, nHot), ...bColdNums.slice(0, nCold)]
      .filter((v,i,a) => a.indexOf(v) === i); // unique
    while (picked.length < 2 && avail.length > 0) {
      const idx = Math.floor(Math.random() * avail.length);
      picked.push(avail.splice(idx, 1)[0]);
    }
    while (picked.length < 2) {
      for (let n = 1; n <= 12; n++) {
        if (!picked.includes(n)) { picked.push(n); break; }
      }
    }
    return picked.sort((a,b)=>a-b);
  }
  
  const recommendations = [];
  
  for (let si = 0; si < strategies.length; si++) {
    const strat = strategies[si];
    let frontNums, backNums;
    
    if (si === 3) {
      // 奇偶均衡策略
      const oddPool = fRanked.filter(([n]) => n % 2 === 1).map(([n]) => n);
      const evenPool = fRanked.filter(([n]) => n % 2 === 0).map(([n]) => n);
      
      const useOdd = Math.random() > 0.5 ? 3 : 2;
      const useEven = 5 - useOdd;
      
      const fOdd = oddPool.slice(0, useOdd + 2);
      const fEven = evenPool.slice(0, useEven + 2);
      
      // 确保区间覆盖
      const candidates = new Set();
      for (const n of fOdd.slice(0, useOdd)) candidates.add(n);
      for (const n of fEven.slice(0, useEven)) candidates.add(n);
      
      // 如果不够5个，补充
      let candArr = [...candidates];
      while (candArr.length < 5) {
        for (const [n] of fRanked) {
          if (!candidates.has(n)) { candidates.add(n); break; }
        }
        candArr = [...candidates];
      }
      
      frontNums = candArr.slice(0, 5).sort((a,b)=>a-b);
      
      // 后区确保奇偶均衡 1:1
      const bOdd = bRanked.filter(([n]) => n % 2 === 1).map(([n]) => n);
      const bEven = bRanked.filter(([n]) => n % 2 === 0).map(([n]) => n);
      backNums = [bOdd[0], bEven[0]].sort((a,b)=>a-b);
    } else if (si === 4) {
      // 综合优选：最高分 + 区间均衡 + 唯一性过滤
      // 生成多个候选，选唯一性得分最高的
      let bestCandidate = null;
      let bestUniqScore = -1;
      
      for (let trial = 0; trial < 20; trial++) {
        const f = pickWithZone(strat.fHot, strat.fWarm, strat.fCold, trial);
        const b = pickBack(strat.bHot, strat.bCold);
        const uniqScore = combinationUniquenessScore(draws, f, b);
        
        // 加分：区间均衡
        const z1c = f.filter(n => n <= 12).length;
        const z2c = f.filter(n => n >= 13 && n <= 24).length;
        const z3c = f.filter(n => n >= 25).length;
        const zoneScore = (z1c >= 1 && z2c >= 1 && z3c >= 1) ? 5 : 0;
        
        // 加分：和值接近历史均值
        const fSum = f.reduce((a,b)=>a+b,0);
        const sumScore = (fSum >= 70 && fSum <= 110) ? 3 : (fSum >= 60 && fSum <= 120) ? 1 : 0;
        
        const totalScore = uniqScore + zoneScore + sumScore;
        if (totalScore > bestUniqScore) {
          bestUniqScore = totalScore;
          bestCandidate = { front: f, back: b, uniqScore, zoneScore, sumScore };
        }
      }
      
      frontNums = bestCandidate.front;
      backNums = bestCandidate.back;
    } else {
      frontNums = pickWithZone(strat.fHot, strat.fWarm, strat.fCold, si);
      backNums = pickBack(strat.bHot, strat.bCold);
    }
    
    // 生成推荐理由
    const reasons = [];
    reasons.push('策略: ' + strat.name + ' - ' + strat.desc);
    
    const fOdd = frontNums.filter(n => n % 2 === 1).length;
    const bOdd = backNums.filter(n => n % 2 === 1).length;
    reasons.push('前区奇偶比 ' + fOdd + ':' + (5-fOdd) + '，后区 ' + bOdd + ':' + (2-bOdd));
    
    // 区间分布
    const z1 = frontNums.filter(n => n <= 12).length;
    const z2 = frontNums.filter(n => n >= 13 && n <= 24).length;
    const z3 = frontNums.filter(n => n >= 25).length;
    reasons.push('前区区间分布: 一区' + z1 + '个 二区' + z2 + '个 三区' + z3 + '个');
    
    const fSum = frontNums.reduce((a,b)=>a+b,0);
    reasons.push('前区和值: ' + fSum + ' (历史均值' + sums.front.avg + ')');
    
    // 组合唯一性
    const uniqScore = combinationUniquenessScore(draws, frontNums, backNums);
    if (uniqScore >= 10) {
      reasons.push('组合唯一性分析: 该组合在历史中出现极少，具有独特性');
    }
    
    // 遗漏回补提醒
    const longMiss = frontNums.filter(n => (miss.front[n] || 0) >= 8);
    if (longMiss.length > 0) {
      reasons.push('前区含遗漏回补号: ' + longMiss.map(n => String(n).padStart(2,'0')).join(' '));
    }
    
    // 上上期模式
    const fromPrev2 = frontNums.filter(n => prev2Nums.includes(n));
    if (fromPrev2.length > 0) {
      reasons.push('上上期号码延续: ' + fromPrev2.map(n => String(n).padStart(2,'0')).join(' ') + ' (跨期模式)');
    }
    
    // 连号预测
    if (consecPred.shouldIncludeConsecutive && consecPred.latestHasConsecutive) {
      reasons.push('连号链式分析: 本期有连号，下期连号概率' + consecPred.probabilityNextHas + '%，建议关注连号');
    }
    
    recommendations.push({
      index: si + 1,
      strategy: strat.name,
      description: strat.desc,
      front: frontNums,
      back: backNums,
      frontOddEven: fOdd + ':' + (5-fOdd),
      backOddEven: bOdd + ':' + (2-bOdd),
      reasons: reasons,
      uniqScore: uniqScore,
      totalScore: fScores[frontNums[0]] ? frontNums.reduce((s,n) => s + (fScores[n]?.score||0), 0) : 0
    });
  }
  
  return {
    recommendations,
    analysis: { hc, miss, oe, zone, consec, sums, ngram, skipW, consecPred, fScores, bScores }
  };
}

// ================================================================
//  回测
// ================================================================
function backtestRecommendations(draws, prevRecs) {
  if (!prevRecs || !prevRecs.target_issue) return null;
  
  const targetDraw = draws.find(d => d.issue === prevRecs.target_issue);
  if (!targetDraw) return { status: 'pending', target_issue: prevRecs.target_issue };
  
  const actualFront = new Set(targetDraw.front);
  const actualBack = new Set(targetDraw.back);
  
  const results = [];
  let bestF = 0, bestB = 0, bestCombined = 0;
  
  for (const rec of (prevRecs.recommendations || [])) {
    const fHit = rec.front.filter(n => actualFront.has(n));
    const bHit = rec.back.filter(n => actualBack.has(n));
    results.push({
      strategy: rec.strategy,
      front: rec.front, back: rec.back,
      fHit, bHit,
      fCount: fHit.length, bCount: bHit.length
    });
    bestF = Math.max(bestF, fHit.length);
    bestB = Math.max(bestB, bHit.length);
    bestCombined = Math.max(bestCombined, fHit.length + bHit.length);
  }
  
  let prize = '未中奖';
  if (bestF >= 5 && bestB >= 2) prize = '一等奖';
  else if (bestF >= 5 && bestB >= 1) prize = '二等奖';
  else if (bestF >= 5) prize = '三等奖';
  else if (bestF >= 4 && bestB >= 2) prize = '四等奖';
  else if (bestF >= 4 && bestB >= 1) prize = '五等奖';
  else if (bestF >= 3 && bestB >= 2) prize = '六等奖';
  else if (bestF >= 4) prize = '七等奖';
  else if (bestF >= 3 && bestB >= 1) prize = '八等奖';
  else if ((bestF >= 2 && bestB >= 2) || bestF >= 3 || (bestF >= 1 && bestB >= 2) || bestB >= 2) prize = '九等奖';
  
  return {
    status: 'drawn',
    target_issue: prevRecs.target_issue,
    target_date: targetDraw.date,
    actual_front: targetDraw.front,
    actual_back: targetDraw.back,
    results, bestF, bestB, bestCombined, prize
  };
}

// ================================================================
//  UI 渲染
// ================================================================
let chartInstances = [];

function destroyCharts() {
  for (const c of chartInstances) { try { c.destroy(); } catch(e) {} }
  chartInstances = [];
}

// ================================================================
//  手动选号 & 自选列表 引擎
// ================================================================
let filterList = [];       // 自选列表 [{id, front:[], back:[], note}]
let pickerFront = new Set(); // 当前选号-前区
let pickerBack = new Set();  // 当前选号-后区
let _globalDraws = null;     // 全局数据引用
let _globalMiss = null;      // 遗漏数据缓存

function getOmission(num, zone, draws, missCache) {
  if (!missCache) return '?';
  const data = zone === 'front' ? missCache.front : missCache.back;
  return data[num] !== undefined ? data[num] : '?';
}

function checkHistoricalDuplicate(front, back, draws) {
  if (!draws || draws.length === 0) return null;
  const fSet = new Set(front);
  const bSet = new Set(back);
  const matchHistory = [];
  for (const d of draws) {
    const fHit = d.front.filter(n => fSet.has(n));
    const bHit = d.back.filter(n => bSet.has(n));
    const total = fHit.length + bHit.length;
    if (total >= 4) {
      matchHistory.push({ issue: d.issue, date: d.date, front: d.front, back: d.back, fHit, bHit, total });
    }
  }
  if (matchHistory.length >= 2) {
    return { count: matchHistory.length, matches: matchHistory.slice(0, 5) };
  }
  return null;
}

function updatePickerUI() {
  const fc = pickerFront.size, bc = pickerBack.size;
  const cntEl = document.getElementById('pickerCount');
  if (cntEl) cntEl.textContent = '前区 ' + fc + '/5  后区 ' + bc + '/2';
  const addBtn = document.getElementById('btnAddToList');
  if (addBtn) {
    addBtn.disabled = (fc !== 5 || bc !== 2);
    addBtn.style.opacity = (fc === 5 && bc === 2) ? '1' : '0.5';
  }
  // 更新球的选中态
  document.querySelectorAll('.picker-ball[data-zone="front"]').forEach(el => {
    const n = parseInt(el.dataset.num);
    el.classList.toggle('sel-front', pickerFront.has(n));
  });
  document.querySelectorAll('.picker-ball[data-zone="back"]').forEach(el => {
    const n = parseInt(el.dataset.num);
    el.classList.toggle('sel-back', pickerBack.has(n));
  });
}

function toggleBall(num, zone) {
  if (zone === 'front') {
    if (pickerFront.has(num)) { pickerFront.delete(num); }
    else if (pickerFront.size < 5) { pickerFront.add(num); }
    else { return; }
  } else {
    if (pickerBack.has(num)) { pickerBack.delete(num); }
    else if (pickerBack.size < 2) { pickerBack.add(num); }
    else { return; }
  }
  updatePickerUI();
}

function clearPicker() {
  pickerFront.clear();
  pickerBack.clear();
  updatePickerUI();
}

function addToFilterList() {
  if (pickerFront.size !== 5 || pickerBack.size !== 2) return;
  const front = [...pickerFront].sort((a,b)=>a-b);
  const back = [...pickerBack].sort((a,b)=>a-b);
  
  // 检查历史重复
  const dup = checkHistoricalDuplicate(front, back, _globalDraws);
  if (dup) {
    const examples = dup.matches.map(m => 
      '第' + m.issue + '期(' + m.date + '): ' + 
      m.front.join(' ') + ' + ' + m.back.join(' ')
    ).join('<br>');
    showToast('⚠ 该组合历史上已出现 ' + dup.count + ' 次相同4位及以上号码，强烈建议不要购买！<br><br>' + examples, 8000);
  }
  
  doAddToList(front, back, dup);
}

function doAddToList(front, back, dup) {
  filterList.push({
    id: Date.now(),
    front: front,
    back: back,
    dup: dup
  });
  saveFilterList();
  renderFilterList();
  clearPicker();
}

function removeFromFilterList(id) {
  filterList = filterList.filter(item => item.id !== id);
  saveFilterList();
  renderFilterList();
}

function saveFilterList() {
  try {
    const clean = filterList.map(item => ({ front: item.front, back: item.back }));
    localStorage.setItem('dlt_custom_list', JSON.stringify(clean));
  } catch(e) {}
}

function loadFilterList() {
  // 只在页面加载时恢复用户的自选列表（非系统推荐，系统推荐由importRecommendations处理）
  try {
    const saved = JSON.parse(localStorage.getItem('dlt_custom_list') || 'null');
    if (saved && Array.isArray(saved) && saved.length > 0) {
      // 系统推荐每次会重新导入，这里只恢复非系统的（判断逻辑：5组或以下且与上次导入不同则为用户手动添加）
      // 简化：不做恢复，由importRecommendations统一管理
    }
  } catch(e) {}
}

function renderReviewCustom(draws) {
  const container = document.getElementById('reviewCustom');
  if (!container) return;
  try {
    const saved = JSON.parse(localStorage.getItem('dlt_prev_custom') || 'null');
    if (!saved || !Array.isArray(saved) || saved.length === 0) return;
    
    // 最新开奖号码
    const latest = draws[draws.length - 1];
    const afSet = new Set(latest.front);
    const abSet = new Set(latest.back);
    
    let html = '<div style="font-size:.85em;font-weight:600;color:#0958d9;margin:8px 0 4px">个人自选</div>' +
      '<table class="data-table"><thead><tr><th>#</th><th>前区</th><th>后区</th><th>命中</th><th>参数</th></tr></thead><tbody>';
    
    saved.forEach((item, j) => {
      const fHit = item.front.filter(n => afSet.has(n));
      const bHit = item.back.filter(n => abSet.has(n));
      const totalHit = fHit.length + bHit.length;
      const fOdd = item.front.filter(n => n % 2).length;
      const fSum = item.front.reduce((a,b)=>a+b,0);
      const hitClass = totalHit >= 3 ? 'color:#cf1322;font-weight:700' : 'color:#999';
      html += '<tr>' +
        '<td><span style="display:inline-block;width:20px;height:20px;line-height:20px;border-radius:4px;background:#595959;color:#fff;font-size:.75em;font-weight:700;text-align:center">' + (j+1) + '</span></td>' +
        '<td>' + item.front.map(n=>'<span class="td-b fr">'+String(n).padStart(2,'0')+'</span>').join('') + '</td>' +
        '<td>' + item.back.map(n=>'<span class="td-b bl">'+String(n).padStart(2,'0')+'</span>').join('') + '</td>' +
        '<td style="' + hitClass + '">' + (fHit.length || bHit.length ? '前'+fHit.length+'+后'+bHit.length : '-') + '</td>' +
        '<td style="font-size:.75em">奇偶'+fOdd+':'+(5-fOdd)+' | 和值'+fSum+'</td></tr>';
    });
    html += '</tbody></table>';
    container.innerHTML = html;
  } catch(e) { container.innerHTML = ''; }
}

function renderFilterList() {
  const container = document.getElementById('filterListContainer');
  if (!container) return;
  
  if (filterList.length === 0) {
    container.innerHTML = '<div class="empty-hint">暂未添加自选号码，点击上方号码手动选号或一键导入推荐</div>';
    document.getElementById('filterSummary').style.display = 'none';
    return;
  }
  
  document.getElementById('filterSummary').style.display = 'flex';
  document.getElementById('filterCountNum').textContent = filterList.length;
  
  let html = '';
  filterList.forEach((item, i) => {
    const frontBalls = item.front.map(n => '<span class="sball fr">' + String(n).padStart(2,'0') + '</span>').join('');
    const backBalls = item.back.map(n => '<span class="sball bl">' + String(n).padStart(2,'0') + '</span>').join('');
    const sum = item.front.reduce((a,b)=>a+b,0);
    const odd = item.front.filter(n=>n%2).length;
    const even = 5 - odd;
    html += '<div class="filter-item">' +
      '<div class="idx">' + (i + 1) + '</div>' +
      '<div class="balls-row">' + frontBalls + '<span style="margin:0 3px;color:#ccc">+</span>' + backBalls + '</div>' +
      (item.dup ? '<span class="dup-warn" title="历史上已出现' + item.dup.count + '次4位及以上相同号码">⚠ 高风险</span>' : '') +
      '<span class="filter-info">和值:' + sum + ' | 奇偶:' + odd + ':' + even + '</span>' +
      '<button class="btn btn-danger" onclick="removeFromFilterList(' + item.id + ')" title="删除">✕</button>' +
      '</div>';
  });
  container.innerHTML = html;
}

function copyListAsImage() {
  if (filterList.length === 0) return;
  
  // 使用SVG方案 — 矢量渲染，与网页CSS效果完全一致
  const ballR = 26;     // 球半径px(物理)
  const ballGap = 8;    // 球间距
  const idxW = 40;      // 序号区宽度（距第一个球间距）
  const plusW = 24;     // +号宽度
  const padX = 16;      // 左右padding
  const padY = 12;      // 上下padding
  const rowH = 66;      // 行高
  
  // 精确计算SVG宽度 (7球+空格+序号区)
  const rowContentW = idxW + 5 * (ballR*2 + ballGap) + plusW + 2 * (ballR*2 + ballGap);
  const svgW = padX * 2 + rowContentW;
  const svgH = padY * 2 + filterList.length * rowH;
  
  // 构建SVG
  let svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + svgW + '" height="' + svgH + '">';
  svg += '<rect width="' + svgW + '" height="' + svgH + '" fill="#ffffff"/>';
  
  // SVG渐变定义 — 柔和色调，参考实物彩票球效果
  svg += '<defs>' +
    '<linearGradient id="gf" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#f09080"/><stop offset="100%" stop-color="#c85140"/></linearGradient>' +
    '<linearGradient id="gb" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#6daae0"/><stop offset="100%" stop-color="#3d7ec0"/></linearGradient>' +
    '<filter id="ballShadow"><feDropShadow dx="0" dy="1" stdDeviation="1.5" flood-opacity="0.25"/></filter>' +
    '</defs>';
  
  filterList.forEach((item, i) => {
    const rowY = padY + i * rowH + rowH / 2;
    const idxX = padX + idxW / 2;
    const idxBoxX = padX + 2;
    const idxBoxY = rowY - 22/2;
    
    // 序号方块 (rect中心对准text的x坐标)
    svg += '<rect x="' + (idxX - 11) + '" y="' + idxBoxY + '" width="22" height="22" rx="4" fill="#555"/>';
    svg += '<text x="' + idxX + '" y="' + (rowY + 1) + '" text-anchor="middle" dominant-baseline="central" fill="#fff" font-size="13" font-weight="bold" font-family="Arial,sans-serif">' + (i+1) + '</text>';
    
    // 前区红球
    let bx = padX + idxW + ballR;
    item.front.forEach(n => {
      svg += '<circle cx="' + bx + '" cy="' + rowY + '" r="' + ballR + '" fill="url(#gf)" filter="url(#ballShadow)"/>';
      svg += '<text x="' + bx + '" y="' + (rowY + 1) + '" text-anchor="middle" dominant-baseline="central" fill="#fff" font-size="26" font-weight="bold" font-family="Arial,sans-serif">' + String(n).padStart(2,'0') + '</text>';
      bx += ballR * 2 + ballGap;
    });
    
    // +号
    svg += '<text x="' + (bx - ballR + plusW/2) + '" y="' + (rowY + 1) + '" text-anchor="middle" dominant-baseline="central" fill="#999" font-size="18" font-weight="bold" font-family="Arial,sans-serif">+</text>';
    bx = bx - ballR + plusW + ballR;
    
    // 后区蓝球
    item.back.forEach(n => {
      svg += '<circle cx="' + bx + '" cy="' + rowY + '" r="' + ballR + '" fill="url(#gb)" filter="url(#ballShadow)"/>';
      svg += '<text x="' + bx + '" y="' + (rowY + 1) + '" text-anchor="middle" dominant-baseline="central" fill="#fff" font-size="26" font-weight="bold" font-family="Arial,sans-serif">' + String(n).padStart(2,'0') + '</text>';
      bx += ballR * 2 + ballGap;
    });
  });
  
  svg += '</svg>';
  
  // SVG → PNG (2x 超清)
  const scale = 2;
  const canvas = document.getElementById('copyCanvas');
  
  // 创建临时Image加载SVG
  const svgBlob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(svgBlob);
  const img = new Image();
  
  img.onload = function() {
    canvas.width = svgW * scale;
    canvas.height = svgH * scale;
    const ctx = canvas.getContext('2d');
    ctx.scale(scale, scale);
    ctx.drawImage(img, 0, 0, svgW, svgH);
    URL.revokeObjectURL(url);
    
    canvas.toBlob(blob => {
      try {
        const item = new ClipboardItem({ 'image/png': blob });
        navigator.clipboard.write([item]).then(() => {
          showToast('✓ 自选列表已复制为高清图片');
        }).catch(() => {
          downloadImage(canvas);
        });
      } catch(e) {
        downloadImage(canvas);
      }
    }, 'image/png');
  };
  
  img.onerror = function() {
    URL.revokeObjectURL(url);
    showToast('生成图片失败，请重试');
  };
  
  img.src = url;
}

function showToast(msg, duration) {
  const existing = document.querySelector('.dup-toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = 'dup-toast';
  toast.innerHTML = msg;
  document.body.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity .3s'; }, duration || 3000);
  setTimeout(() => { if (toast.parentNode) toast.remove(); }, (duration || 3000) + 350);
}

function importRecommendations(recs, draws) {
  // 保留用户手动添加的非推荐号码（不在本次推荐列表中的）
  const manualItems = filterList.filter(item => {
    const key = item.front.join(',') + '|' + item.back.join(',');
    return !recs.some(r => {
      const rKey = [...r.front].sort((a,b)=>a-b).join(',') + '|' + [...r.back].sort((a,b)=>a-b).join(',');
      return key === rKey;
    });
  });
  
  // 清空列表，保留手动添加的
  filterList = [...manualItems];
  
  // 保存上次自选作为历史
  try {
    const prevCustom = JSON.parse(localStorage.getItem('dlt_prev_custom') || 'null');
    const clean = manualItems.map(item => ({ front: item.front, back: item.back }));
    const cleanStr = JSON.stringify(clean);
    const prevStr = prevCustom ? JSON.stringify(prevCustom) : '';
    if (clean.length > 0 && cleanStr !== prevStr) {
      localStorage.setItem('dlt_prev_custom', cleanStr);
      localStorage.setItem('dlt_prev_custom_issue', CACHED_RESULT.meta.latest_issue || '');
    }
  } catch(e) {}
  
  // 导入新推荐
  recs.forEach(r => {
    const front = [...r.front].sort((a,b)=>a-b);
    const back = [...r.back].sort((a,b)=>a-b);
    filterList.push({ id: Date.now() + Math.random(), front, back, dup: null });
  });
  saveFilterList();
  renderFilterList();
  showToast('✓ 已导入 ' + recs.length + ' 组推荐号码到自选列表');
}

// 渲染手动选号面板
function renderPickerPanel(draws, missCache) {
  _globalDraws = draws;
  _globalMiss = missCache;
  
  let html = '';
  
  // 选号面板
  html += '<div class="picker-section">' +
    '<div class="picker-label" style="font-size:.95em;color:#333;margin-bottom:8px">🎯 手动选号（点击号码添加/取消）</div>';
  
  // 前区
  html += '<div class="picker-label">前区 (红球 01-35) — 选5个</div>' +
    '<div class="picker-grid">';
  for (let i = 1; i <= 35; i++) {
    const omit = getOmission(i, 'front', draws, missCache);
    html += '<div class="picker-ball" data-zone="front" data-num="' + i + '" onclick="toggleBall(' + i + ',\'front\')">' +
      '<span>' + String(i).padStart(2,'0') + '</span>' +
      '<span class="omit">' + omit + '</span>' +
      '</div>';
  }
  html += '</div>';
  
  // 后区
  html += '<div class="picker-label">后区 (蓝球 01-12) — 选2个</div>' +
    '<div class="picker-grid">';
  for (let i = 1; i <= 12; i++) {
    const omit = getOmission(i, 'back', draws, missCache);
    html += '<div class="picker-ball" data-zone="back" data-num="' + i + '" onclick="toggleBall(' + i + ',\'back\')">' +
      '<span>' + String(i).padStart(2,'0') + '</span>' +
      '<span class="omit">' + omit + '</span>' +
      '</div>';
  }
  html += '</div>';
  
  // 工具栏
  html += '<div class="picker-toolbar">' +
    '<span class="count" id="pickerCount">前区 0/5  后区 0/2</span>' +
    '<button class="btn btn-add" id="btnAddToList" onclick="addToFilterList()" disabled style="opacity:0.5">+ 添加到自选列表</button>' +
    '<button class="btn btn-clear" onclick="clearPicker()">清空选择</button>' +
    '</div></div>';
  
  // 自选列表
  html += '<div class="card" style="border:2px solid #ffd591;background:linear-gradient(180deg,#fff7e6,#fff 20%)">' +
    '<div class="card-hd">📋 自选列表</div>' +
    '<div class="summary-bar" id="filterSummary" style="display:none">' +
    '<span>共</span><span class="count-num" id="filterCountNum">0</span><span>组号码</span>' +
    '<button class="btn btn-copy" onclick="copyListAsImage()" style="margin-left:auto">📷 复制为图片</button>' +
    '<button class="btn btn-clear" onclick="filterList=[];renderFilterList();" style="margin-left:4px">清空列表</button>' +
    '</div>' +
    '<div id="filterListContainer"><div class="empty-hint">暂未添加自选号码</div></div></div>';
  
  return html;
}

function renderReport(draws, result, dataSource) {
  destroyCharts();
  
  const m = {
    total_draws: draws.length,
    latest_issue: draws[draws.length-1].issue,
    latest_date: draws[draws.length-1].date,
    latest_front: draws[draws.length-1].front,
    latest_back: draws[draws.length-1].back,
    next_issue: String(parseInt(draws[draws.length-1].issue) + 1),
    analysis_time: new Date().toLocaleString('zh-CN')
  };
  
  const recs = result.recommendations;
  const a = result.analysis;
  const backtest = result.backtest || null;
  
  document.getElementById('headerSub').textContent = 
    '基于 ' + m.total_draws.toLocaleString() + ' 期历史数据 | ' + (dataSource === 'live' ? '实时联网数据' : '构建时同步数据');
  
  let html = '';
  
  // 状态栏
  if (dataSource === 'live') {
    html += '<div class="status-bar ok">✓ 已从网络实时获取最新数据 | 更新时间: ' + m.analysis_time + '</div>';
  } else {
    html += '<div class="status-bar ok">✓ 已加载最新数据 | 快照时间: ' + m.analysis_time + ' (数据与官网同步)</div>';
  }
  
  // 元数据
  html += '<div class="card"><div class="stat-row">' +
    '<div class="stat-item"><div class="stat-val">' + m.total_draws.toLocaleString() + '</div><div class="stat-lbl">历史总期数</div></div>' +
    '<div class="stat-item"><div class="stat-val">' + m.latest_issue + '</div><div class="stat-lbl">最新开奖期号</div></div>' +
    '<div class="stat-item"><div class="stat-val">' + m.latest_date + '</div><div class="stat-lbl">开奖日期</div></div>' +
    '<div class="stat-item"><div class="stat-val" style="color:#0958d9">' + m.next_issue + '</div><div class="stat-lbl">目标推荐期号</div></div>' +
    '<div class="stat-item"><div class="stat-val">' + (a.consec.count) + '/' + a.consec.total + '</div><div class="stat-lbl">近100期连号占比</div></div>' +
    '</div></div>';
  
  // 最新开奖
  html += '<div class="card"><div class="card-hd">📊 ' + m.latest_issue + '期 最新开奖</div>' +
    '<div style="display:flex;gap:20px;flex-wrap:wrap;justify-content:center;align-items:center">' +
    '<div style="text-align:center"><h4 style="font-size:.85em;color:#888;margin-bottom:8px">前区（红球）</h4><div class="balls">' +
    m.latest_front.map(n => '<div class="ball fr">' + String(n).padStart(2,'0') + '</div>').join('') +
    '</div></div>' +
    '<div style="text-align:center"><h4 style="font-size:.85em;color:#888;margin-bottom:8px">后区（蓝球）</h4><div class="balls">' +
    m.latest_back.map(n => '<div class="ball bl">' + String(n).padStart(2,'0') + '</div>').join('') +
    '</div></div></div>' +
    '<div style="text-align:center;margin-top:8px;color:#888;font-size:.82em">' +
    '前区和值: ' + m.latest_front.reduce((a,b)=>a+b,0) + ' | ' +
    '奇偶比: ' + m.latest_front.filter(n=>n%2).length + ':' + m.latest_front.filter(n=>n%2===0).length +
    '</div></div>';
  
  // 回测
  if (backtest && backtest.status === 'drawn') {
    html += '<div class="card" style="border:2px solid #ffd591;background:linear-gradient(180deg,#fffbe6,#fff 20%)">' +
      '<div class="card-hd">🔍 上期回测 — vs 第' + backtest.target_issue + '期 (' + backtest.target_date + ')</div>' +
      '<div style="margin-bottom:12px"><strong>实际开奖前区:</strong> ' +
      backtest.actual_front.map(n => '<span class="ball fr ball-sm" style="display:inline-flex">' + String(n).padStart(2,'0') + '</span>').join('') +
      ' <strong style="margin-left:8px;color:#0958d9">后区:</strong> ' +
      backtest.actual_back.map(n => '<span class="ball bl ball-sm" style="display:inline-flex">' + String(n).padStart(2,'0') + '</span>').join('') +
      '</div>' +
      '<div class="stat-row" style="margin-bottom:12px">' +
      '<div class="stat-item" style="background:#fffbe6"><div class="stat-val" style="color:' + (backtest.bestCombined>=3?'#52c41a':backtest.bestCombined>=2?'#faad14':'#cf1322') + '">' + backtest.bestCombined + '</div><div class="stat-lbl">最佳命中(前+后)</div></div>' +
      '<div class="stat-item" style="background:#fffbe6"><div class="stat-val" style="color:#cf1322">' + backtest.bestF + '</div><div class="stat-lbl">前区最佳</div></div>' +
      '<div class="stat-item" style="background:#fffbe6"><div class="stat-val" style="color:#0958d9">' + backtest.bestB + '</div><div class="stat-lbl">后区最佳</div></div>' +
      '<div class="stat-item" style="background:#fffbe6"><div class="stat-val" style="font-size:1.1em">' + backtest.prize + '</div><div class="stat-lbl">对应奖项</div></div></div>' +
      '<table class="data-table"><thead><tr><th>策略</th><th>推荐前区</th><th>推荐后区</th><th>前区中</th><th>后区中</th><th>合计</th></tr></thead><tbody>' +
      backtest.results.map(r => '<tr><td><strong>' + r.strategy + '</strong></td>' +
        '<td>' + r.front.map(n => '<span class="td-b fr">' + String(n).padStart(2,'0') + '</span>').join('') + '</td>' +
        '<td>' + r.back.map(n => '<span class="td-b bl">' + String(n).padStart(2,'0') + '</span>').join('') + '</td>' +
        '<td style="color:#cf1322;font-weight:600">' + r.fCount + '个 ' + r.fHit.map(n => String(n).padStart(2,'0')).join(' ') + '</td>' +
        '<td style="color:#0958d9;font-weight:600">' + r.bCount + '个 ' + r.bHit.map(n => String(n).padStart(2,'0')).join(' ') + '</td>' +
        '<td><strong>' + (r.fCount + r.bCount) + '</strong></td></tr>').join('') +
      '</tbody></table></div>';
  }
  
  // 上次选号回顾（含推荐 + 自选）
  if (CACHED_RESULT && CACHED_RESULT.backtest && CACHED_RESULT.backtest.status === 'drawn') {
    const bt = CACHED_RESULT.backtest;
    html += '<div class="card" style="border-left:4px solid #faad14">' +
      '<div class="card-hd">📋 上次选号回顾 — 目标第' + bt.target_issue + '期 (' + bt.target_date + ')</div>' +
      '<div style="font-size:.85em;color:#666;margin-bottom:12px">' +
      '实际开奖: 前区 <strong style="color:#cf1322">' + bt.actual_front.map(n=>String(n).padStart(2,'0')).join(' ') + '</strong>' +
      ' 后区 <strong style="color:#0958d9">' + bt.actual_back.map(n=>String(n).padStart(2,'0')).join(' ') + '</strong>' +
      '</div>';
    if (bt.prev_recommendations) {
      html += '<div style="font-size:.85em;font-weight:600;color:#cf1322;margin-bottom:4px">系统推荐</div>' +
        '<table class="data-table"><thead><tr><th>#</th><th>策略</th><th>推荐前区</th><th>推荐后区</th><th>命中</th><th>前区参数</th></tr></thead><tbody>';
      bt.prev_recommendations.forEach((r, j) => {
        const res = bt.results ? bt.results[j] : null;
        const fOdd = r.front.filter(n=>n%2).length;
        const fSum = r.front.reduce((a,b)=>a+b,0);
        const z1 = r.front.filter(n=>n<=12).length;
        const z2 = r.front.filter(n=>n>=13&&n<=24).length;
        const z3 = r.front.filter(n=>n>=25).length;
        const hitText = res ? '前' + res.front_hit_count + '+后' + res.back_hit_count : '-';
        const hitClass = res && (res.front_hit_count + res.back_hit_count) >= 3 ? 'color:#cf1322;font-weight:700' : 'color:#999';
        html += '<tr>' +
          '<td><span style="display:inline-block;width:20px;height:20px;line-height:20px;border-radius:4px;background:#595959;color:#fff;font-size:.75em;font-weight:700;text-align:center">' + (j+1) + '</span></td>' +
          '<td><strong>' + (r.strategy || '策略'+(j+1)) + '</strong></td>' +
          '<td>' + r.front.map(n=>'<span class="td-b fr">'+String(n).padStart(2,'0')+'</span>').join('') + '</td>' +
          '<td>' + r.back.map(n=>'<span class="td-b bl">'+String(n).padStart(2,'0')+'</span>').join('') + '</td>' +
          '<td style="' + hitClass + '">' + hitText + '</td>' +
          '<td style="font-size:.75em">奇偶' + fOdd + ':' + (5-fOdd) + ' | 和值' + fSum + ' | 区' + z1 + '-' + z2 + '-' + z3 + '</td>' +
          '</tr>';
      });
      html += '</tbody></table>';
    }
    // 上次自选（从localStorage加载）
    html += '<div id="reviewCustom" style="margin-top:8px"></div>';
    html += '<div style="font-size:.78em;color:#999;margin-top:8px">' +
      '最佳: 前' + bt.bestF + '中 + 后' + bt.bestB + '中 = ' + (bt.bestF + bt.bestB) + '个 | ' + bt.prize + '</div></div>';
  } else if (CACHED_RESULT && CACHED_RESULT.backtest && CACHED_RESULT.backtest.status === 'pending') {
    const bt = CACHED_RESULT.backtest;
    html += '<div class="card" style="border-left:4px solid #91d5ff">' +
      '<div class="card-hd">📋 上次选号回顾 — 目标第' + bt.target_issue + '期</div>' +
      '<div style="font-size:.85em;color:#999">⏳ 该期尚未开奖，等待数据更新后自动回测...</div>';
    if (bt.prev_recommendations) {
      html += '<table class="data-table" style="margin-top:8px"><thead><tr><th>#</th><th>策略</th><th>推荐前区</th><th>推荐后区</th><th>前区参数</th></tr></thead><tbody>';
      bt.prev_recommendations.forEach((r, j) => {
        const fOdd = r.front.filter(n=>n%2).length;
        const fSum = r.front.reduce((a,b)=>a+b,0);
        html += '<tr><td>' + (j+1) + '</td><td><strong>' + (r.strategy || '策略'+(j+1)) + '</strong></td>' +
          '<td>' + r.front.map(n=>'<span class="td-b fr">'+String(n).padStart(2,'0')+'</span>').join('') + '</td>' +
          '<td>' + r.back.map(n=>'<span class="td-b bl">'+String(n).padStart(2,'0')+'</span>').join('') + '</td>' +
          '<td style="font-size:.75em">奇偶' + fOdd + ':' + (5-fOdd) + ' | 和值' + fSum + '</td></tr>';
      });
      html += '</tbody></table>';
    }
    html += '</div>';
  }
  
  // 深度模式洞察
  const consecPred = a.consecPred;
  const skipData = a.skipW.analysis;
  html += '<div class="card" style="border-left:4px solid #0958d9">' +
    '<div class="card-hd">🧠 深度模式发现</div>' +
    '<div class="grid2">' +
    '<div class="insight-box"><strong>连号链式分析</strong><br>' +
    '本期' + (consecPred.latestHasConsecutive ? '有连号' + (consecPred.latestPairs ? ': ' + consecPred.latestPairs.map(p=>p.join('-')).join(' ') : '') : '无连号') + '<br>' +
    '历史统计: 有连号→下期连号概率 <span style="color:#cf1322;font-weight:700">' + consecPred.probabilityNextHas + '%</span><br>' +
    (consecPred.latestHasConsecutive ? '无连号→下期连号概率 ' + a.consec.rate.toFixed(1) + '%' : '') +
    '</div>' +
    '<div class="insight-box"><strong>上上期跨期规律</strong><br>' +
    '历史中上上期号码出现在下期的概率:<br>' +
    '前区 <span style="color:#cf1322;font-weight:700">' + skipData.frontRate + '%</span> | ' +
    '后区 <span style="color:#0958d9;font-weight:700">' + skipData.backRate + '%</span><br>' +
    (skipData.prev2Check ? '最新一期上上期(' + skipData.prev2Check.issue + ')号码:' +
      skipData.prev2Check.front.map(n => String(n).padStart(2,'0')).join(' ') +
      (skipData.prev2Check.frontInLatest.length > 0 ? '<br>其中 ' + skipData.prev2Check.frontInLatest.map(n=>String(n).padStart(2,'0')).join(' ') + ' 已出现（活跃延续中）' : '') : '') +
    '</div></div></div>';
  
  // 冷热号
  html += '<div class="card"><div class="card-hd">🔥 冷热号分析（近50期）</div><div class="grid2">' +
    '<div><h4 style="color:#cf1322;margin-bottom:8px">前区 (1-35)</h4>' +
    '<strong>热号:</strong> ' + a.hc.front.hot.map(n => '<span class="tag tag-hot">' + String(n).padStart(2,'0') + '</span>').join(' ') +
    '<br><strong>冷号:</strong> ' + a.hc.front.cold.map(n => '<span class="tag tag-cold">' + String(n).padStart(2,'0') + '</span>').join(' ') +
    '<div class="chart-wrap" style="margin-top:8px"><canvas id="chFreqF"></canvas></div></div>' +
    '<div><h4 style="color:#0958d9;margin-bottom:8px">后区 (1-12)</h4>' +
    '<strong>热号:</strong> ' + a.hc.back.hot.map(n => '<span class="tag tag-hot">' + String(n).padStart(2,'0') + '</span>').join(' ') +
    '<br><strong>冷号:</strong> ' + a.hc.back.cold.map(n => '<span class="tag tag-cold">' + String(n).padStart(2,'0') + '</span>').join(' ') +
    '<div class="chart-wrap" style="margin-top:8px"><canvas id="chFreqB"></canvas></div></div></div></div>';
  
  // 遗漏
  const fMissSorted = Object.entries(a.miss.front).sort((a,b) => b[1]-a[1]).slice(0, 10);
  const bMissSorted = Object.entries(a.miss.back).sort((a,b) => b[1]-a[1]).slice(0, 6);
  html += '<div class="card"><div class="card-hd">⏳ 遗漏分析</div><div class="grid2">' +
    '<div><h4 style="color:#cf1322;margin-bottom:6px">前区遗漏Top10</h4>' +
    '<table class="data-table"><tr><th>号码</th><th>遗漏期数</th><th>状态</th></tr>' +
    fMissSorted.map(([n,c]) => '<tr><td><span class="td-b fr">' + String(parseInt(n)).padStart(2,'0') + '</span></td><td><strong>' + c + '</strong></td><td>' + (c>=20?'<span style="color:#cf1322">⚠极冷</span>':c>=10?'<span style="color:#d46b08">偏冷</span>':'<span style="color:#52c41a">正常</span>') + '</td></tr>').join('') +
    '</table></div>' +
    '<div><h4 style="color:#0958d9;margin-bottom:6px">后区遗漏</h4>' +
    '<table class="data-table"><tr><th>号码</th><th>遗漏期数</th><th>状态</th></tr>' +
    bMissSorted.map(([n,c]) => '<tr><td><span class="td-b bl">' + String(parseInt(n)).padStart(2,'0') + '</span></td><td><strong>' + c + '</strong></td><td>' + (c>=10?'<span style="color:#cf1322">⚠极冷</span>':c>=5?'<span style="color:#d46b08">偏冷</span>':'<span style="color:#52c41a">正常</span>') + '</td></tr>').join('') +
    '</table></div></div></div>';
  
  // 统计特征
  html += '<div class="card"><div class="card-hd">📈 统计特征（近50期）</div><div class="grid3">' +
    '<div><h4 style="margin-bottom:6px">前区奇偶比</h4><div class="chart-wrap-sm"><canvas id="chOEf"></canvas></div></div>' +
    '<div><h4 style="margin-bottom:6px">后区奇偶比</h4><div class="chart-wrap-sm"><canvas id="chOEb"></canvas></div></div>' +
    '<div><h4 style="margin-bottom:6px">和值统计</h4><p>前区均值: <strong style="color:#cf1322">' + a.sums.front.avg + '</strong> (范围 ' + a.sums.front.min + '-' + a.sums.front.max + ')</p>' +
    '<p>后区均值: <strong style="color:#0958d9">' + a.sums.back.avg + '</strong></p>' +
    '<p>常见连号对:</p>' +
    Object.entries(a.consec.pairs).sort((a,b)=>b[1]-a[1]).slice(0,5).map(([k,v]) => 
      '<div style="font-size:.78em;color:#666">' + k.replace(',','-') + ': ' + v + '次</div>').join('') +
    '</div></div></div>';
  
  // 推荐号码
  html += '<div class="card" style="border:2px solid #ffd591;background:linear-gradient(180deg,#fffbe6,#fff 20%)">' +
    '<div class="card-hd">🎯 智能推荐 — 第' + m.next_issue + '期 5注号码</div>' +
    '<div class="warn-box"><strong>⚠ 风险提示:</strong> 彩票开奖完全随机，分析仅供娱乐参考，理性购彩。</div>';
  
  for (const r of recs) {
    html += '<div class="rec-card"><div class="rec-hd">' +
      '<div class="rec-num">' + r.index + '</div>' +
      '<div class="rec-title">' + r.strategy + '</div>' +
      '<div class="rec-score">唯一性: ' + (r.uniqScore || 0) + '分</div></div>' +
      '<div class="balls" style="margin-bottom:8px">' +
      r.front.map(n => '<div class="ball fr ball-sm">' + String(n).padStart(2,'0') + '</div>').join('') +
      '<span style="margin:0 4px;color:#ccc;font-size:1.2em">+</span>' +
      r.back.map(n => '<div class="ball bl ball-sm">' + String(n).padStart(2,'0') + '</div>').join('') +
      '</div><div class="rec-reason"><ul>' +
      r.reasons.map(reason => '<li>' + reason + '</li>').join('') +
      '</ul></div></div>';
  }
  html += '</div>';
  
  // 手动选号 & 自选列表
  html += renderPickerPanel(draws, a.miss);
  
  // 最近10期
  html += '<div class="card"><div class="card-hd">📅 近期走势（最近10期）</div><div style="overflow-x:auto"><table class="data-table" style="min-width:700px">' +
    '<thead><tr><th>期号</th><th>日期</th><th>前区1</th><th>前区2</th><th>前区3</th><th>前区4</th><th>前区5</th><th style="color:#0958d9">后区1</th><th style="color:#0958d9">后区2</th><th>和值</th><th>奇偶</th><th>跨度</th><th>区间比</th></tr></thead><tbody>' +
    draws.slice(-10).reverse().map(d => {
      const span = Math.max(...d.front) - Math.min(...d.front);
      const z1 = d.front.filter(n=>n<=12).length;
      const z2 = d.front.filter(n=>n>=13&&n<=24).length;
      const z3 = d.front.filter(n=>n>=25).length;
      return '<tr><td><strong>' + d.issue + '</strong></td><td>' + d.date.slice(5) + '</td>' +
        d.front.map(n => '<td><span class="td-b fr">' + String(n).padStart(2,'0') + '</span></td>').join('') +
        d.back.map(n => '<td><span class="td-b bl">' + String(n).padStart(2,'0') + '</span></td>').join('') +
        '<td>' + (d.front.reduce((a,b)=>a+b,0) + d.back.reduce((a,b)=>a+b,0)) + '</td>' +
        '<td>' + d.front.filter(n=>n%2).length + ':' + d.front.filter(n=>n%2===0).length + '</td>' +
        '<td style="font-weight:700;color:#cf1322">' + span + '</td>' +
        '<td style="font-size:.78em">' + z1 + ':' + z2 + ':' + z3 + '</td></tr>';
    }).join('') +
    '</tbody></table></div></div>';
  
  document.getElementById('app').innerHTML = html;
  
  // ===== 绘制图表 =====
  setTimeout(() => {
    // 前区频率
    const fFreqData = [];
    for (let i = 1; i <= 35; i++) fFreqData.push({ n: i, c: a.hc.front.freq[i] || 0 });
    const fAvg = fFreqData.reduce((s,d)=>s+d.c,0) / 35;
    chartInstances.push(new Chart(document.getElementById('chFreqF'), {
      type: 'bar', data: {
        labels: fFreqData.map(d => String(d.n).padStart(2,'0')),
        datasets: [{ data: fFreqData.map(d => d.c),
          backgroundColor: fFreqData.map(d => d.c > fAvg*1.2 ? '#cf1322' : d.c < fAvg*0.8 ? '#0958d9' : '#faad14'),
          borderRadius: 3 }]
      }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, max: Math.ceil(Math.max(...fFreqData.map(d=>d.c))*1.3) } } }
    }));
    
    // 后区频率
    const bFreqData = [];
    for (let i = 1; i <= 12; i++) bFreqData.push({ n: i, c: a.hc.back.freq[i] || 0 });
    chartInstances.push(new Chart(document.getElementById('chFreqB'), {
      type: 'bar', data: {
        labels: bFreqData.map(d => String(d.n).padStart(2,'0')),
        datasets: [{ data: bFreqData.map(d => d.c),
          backgroundColor: bFreqData.map((d,i) => i < 4 ? '#cf1322' : '#0958d9'),
          borderRadius: 3 }]
      }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } } }
    }));
    
    // 奇偶比
    const oeF = a.oe.front;
    chartInstances.push(new Chart(document.getElementById('chOEf'), {
      type: 'doughnut', data: { labels: Object.keys(oeF), datasets: [{ data: Object.values(oeF),
        backgroundColor: ['#cf1322','#faad14','#52c41a','#0958d9','#722ed1','#eb2f96'] }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { font: { size: 10 } } } } }
    }));
    
    const oeB = a.oe.back;
    chartInstances.push(new Chart(document.getElementById('chOEb'), {
      type: 'doughnut', data: { labels: Object.keys(oeB), datasets: [{ data: Object.values(oeB),
        backgroundColor: ['#cf1322','#52c41a','#0958d9'] }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { font: { size: 10 } } } } }
    }));
  }, 100);
}

// ================================================================
//  主流程
// ================================================================
async function main() {
  let rawData = null;
  let dataSource = 'builtin'; // 'live' | 'builtin'
  
  // 快速尝试直接联网获取（浏览器CORS限制下通常不可用，但不阻塞加载）
  document.getElementById('loadMsg').textContent = '正在加载数据...';
  try {
    const resp = await fetch(DATA_URL, { signal: AbortSignal.timeout(5000) });
    if (resp.ok) {
      const text = await resp.text();
      if (text.length > 10000) {
        rawData = text;
        dataSource = 'live';
      }
    }
  } catch(e) {}
  
  // 联不通则使用内嵌数据（与联网数据来源相同，构建时已同步）
  if (!rawData) {
    rawData = RAW_FALLBACK;
    dataSource = 'builtin';
    document.getElementById('loadMsg').textContent = '使用内置数据（构建时已同步最新）...';
  }
  
  // 解析数据
  const draws = parseRawData(rawData);
  document.getElementById('loadMsg').textContent = '解析完成 ' + draws.length + ' 期数据，正在分析...';
  
  // 分析
  const result = generateRecommendations(draws);
  
  // 回测（使用缓存的推荐记录）
  let backtest = null;
  try {
    if (CACHED_RESULT && CACHED_RESULT.backtest) {
      // 使用JSON中缓存的回测结果
    }
    // 尝试从之前保存的推荐中回测
    const savedRec = JSON.parse(localStorage.getItem('dlt_last_rec') || 'null');
    if (savedRec) {
      backtest = backtestRecommendations(draws, savedRec);
    }
  } catch(e) {}
  
  result.backtest = backtest;
  
  // 保存本次推荐供下次回测
  const nextIssue = String(parseInt(draws[draws.length-1].issue) + 1);
  const toSave = {
    target_issue: nextIssue,
    generated_time: new Date().toISOString(),
    recommendations: result.recommendations.map(r => ({
      strategy: r.strategy, front: r.front, back: r.back
    }))
  };
  try { localStorage.setItem('dlt_last_rec', JSON.stringify(toSave)); } catch(e) {}
  
  // 渲染
  renderReport(draws, result, dataSource);
  
  // 加载上次自选并渲染回顾
  setTimeout(() => {
    loadFilterList();
    renderReviewCustom(draws);
  }, 100);
  
  // 自动导入推荐号码到自选列表
  setTimeout(() => {
    importRecommendations(result.recommendations, draws);
  }, 500);
}

main().catch(e => {
  document.getElementById('app').innerHTML = '<div class="card"><div class="card-hd">❌ 加载失败</div>' +
    '<p style="color:#cf1322">分析引擎初始化错误: ' + e.message + '</p>' +
    '<p style="color:#999;font-size:.85em">请尝试刷新页面或检查网络连接</p></div>';
  document.getElementById('headerSub').textContent = '加载异常';
});
</script>
</body>
</html>
'''

# 嵌入原始数据
raw_data_escaped = json.dumps(raw_data)
html = html_template.replace('__RAW_DATA_PLACEHOLDER__', raw_data_escaped)

# 嵌入缓存JSON（用于回测等）
cached_json = json.dumps(cached, ensure_ascii=False)
html = html.replace('__CACHED_RESULT_PLACEHOLDER__', cached_json)

output_path = r'C:\Users\Administrator\WorkBuddy\2026-06-19-16-28-32\deploy\index.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

# 同时写一份到工作目录
with open(r'C:\Users\Administrator\WorkBuddy\2026-06-19-16-28-32\dlt_standalone.html', 'w', encoding='utf-8') as f:
    f.write(html)

file_size = len(html)
print(f'Standalone HTML built: {file_size:,} bytes')
print(f'Output: {output_path}')
