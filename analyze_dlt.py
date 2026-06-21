#!/usr/bin/env python3
"""
体彩大乐透历史数据分析与号码推荐引擎
"""
import json
import os
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta

# ============ 1. 数据解析 ============
def parse_data(filepath):
    draws = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('TcDLT') or line.startswith('SCO'):
                continue
            parts = line.split()
            if len(parts) < 9:
                continue
            # 跳过非期号行(如ver行)
            if not parts[0].isdigit() or len(parts[0]) < 7:
                continue
            issue = parts[0]
            date_str = parts[1]
            front = [int(x) for x in parts[2:7]]
            back = [int(x) for x in parts[7:9]]
            draws.append({
                'issue': issue,
                'date': date_str,
                'front': sorted(front),
                'back': sorted(back)
            })
    # 文件从新到旧排列，反转使得draws[0]最早, draws[-1]最新
    draws.reverse()
    return draws

# ============ 2. 频率分析 ============
def frequency_analysis(draws, recent_n=None):
    """分析前区和后区号码出现频率"""
    data = draws[-recent_n:] if recent_n else draws
    front_counter = Counter()
    back_counter = Counter()
    for d in data:
        for n in d['front']:
            front_counter[n] += 1
        for n in d['back']:
            back_counter[n] += 1
    return front_counter, back_counter

# ============ 3. 冷热号分析 ============
def hot_cold_analysis(draws, recent_n=50, total_range_front=35, total_range_back=12):
    """基于近期频率判断冷热号"""
    front_freq, back_freq = frequency_analysis(draws, recent_n)
    
    # 前区
    front_total = sum(front_freq.values())
    front_avg = front_total / total_range_front
    
    front_hot = sorted([n for n in range(1, total_range_front+1) if front_freq.get(n, 0) > front_avg * 1.2], 
                       key=lambda x: front_freq.get(x, 0), reverse=True)
    front_warm = sorted([n for n in range(1, total_range_front+1) if front_avg * 0.8 <= front_freq.get(n, 0) <= front_avg * 1.2],
                        key=lambda x: front_freq.get(x, 0), reverse=True)
    front_cold = sorted([n for n in range(1, total_range_front+1) if front_freq.get(n, 0) < front_avg * 0.8],
                        key=lambda x: front_freq.get(x, 0))
    
    # 后区
    back_total = sum(back_freq.values())
    back_avg = back_total / total_range_back
    
    back_hot = sorted([n for n in range(1, total_range_back+1) if back_freq.get(n, 0) > back_avg * 1.2],
                      key=lambda x: back_freq.get(x, 0), reverse=True)
    back_warm = sorted([n for n in range(1, total_range_back+1) if back_avg * 0.8 <= back_freq.get(n, 0) <= back_avg * 1.2],
                       key=lambda x: back_freq.get(x, 0), reverse=True)
    back_cold = sorted([n for n in range(1, total_range_back+1) if back_freq.get(n, 0) < back_avg * 0.8],
                       key=lambda x: back_freq.get(x, 0))
    
    return {
        'front': {'hot': front_hot, 'warm': front_warm, 'cold': front_cold, 'freq': dict(front_freq)},
        'back': {'hot': back_hot, 'warm': back_warm, 'cold': back_cold, 'freq': dict(back_freq)}
    }

# ============ 4. 遗漏分析 ============
def missing_analysis(draws):
    """计算每个号码当前遗漏期数"""
    front_missing = {}
    back_missing = {}
    
    for n in range(1, 36):
        missing = 0
        for d in reversed(draws):
            if n in d['front']:
                break
            missing += 1
        front_missing[n] = missing
    
    for n in range(1, 13):
        missing = 0
        for d in reversed(draws):
            if n in d['back']:
                break
            missing += 1
        back_missing[n] = missing
    
    # 找出遗漏较长的号码
    front_missing_sorted = sorted(front_missing.items(), key=lambda x: x[1], reverse=True)
    back_missing_sorted = sorted(back_missing.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'front': dict(front_missing_sorted),
        'back': dict(back_missing_sorted),
        'front_top_missing': front_missing_sorted[:10],
        'back_top_missing': back_missing_sorted[:6]
    }

# ============ 5. 奇偶比分析 ============
def odd_even_analysis(draws, recent_n=50):
    """分析奇偶比趋势"""
    data = draws[-recent_n:]
    front_ratios = Counter()
    back_ratios = Counter()
    
    for d in data:
        front_odd = sum(1 for n in d['front'] if n % 2 == 1)
        front_even = 5 - front_odd
        front_ratios[f"{front_odd}:{front_even}"] += 1
        
        back_odd = sum(1 for n in d['back'] if n % 2 == 1)
        back_even = 2 - back_odd
        back_ratios[f"{back_odd}:{back_even}"] += 1
    
    return {
        'front': dict(front_ratios.most_common()),
        'back': dict(back_ratios.most_common())
    }

# ============ 6. 区间分布分析 ============
def zone_analysis(draws, recent_n=50):
    """分析前区三区分布: 1区1-12, 2区13-24, 3区25-35"""
    data = draws[-recent_n:]
    zones = Counter()
    
    for d in data:
        z1 = sum(1 for n in d['front'] if 1 <= n <= 12)
        z2 = sum(1 for n in d['front'] if 13 <= n <= 24)
        z3 = sum(1 for n in d['front'] if 25 <= n <= 35)
        zones[f"{z1}:{z2}:{z3}"] += 1
    
    return dict(zones.most_common())

# ============ 7. 连号分析 ============
def consecutive_analysis(draws, recent_n=100):
    """分析连号出现频率"""
    data = draws[-recent_n:]
    consecutive_count = 0
    consecutive_pairs = Counter()
    
    for d in data:
        has_consecutive = False
        for i in range(len(d['front']) - 1):
            if d['front'][i+1] - d['front'][i] == 1:
                has_consecutive = True
                consecutive_pairs[(d['front'][i], d['front'][i+1])] += 1
        for i in range(len(d['back']) - 1):
            if d['back'][i+1] - d['back'][i] == 1:
                has_consecutive = True
        if has_consecutive:
            consecutive_count += 1
    
    return {
        'rate': consecutive_count / len(data) if data else 0,
        'count': consecutive_count,
        'total': len(data),
        'pairs': dict(consecutive_pairs.most_common(10))
    }

# ============ 8. 和值分析 ============
def sum_analysis(draws, recent_n=50):
    """分析和值范围趋势"""
    data = draws[-recent_n:]
    front_sums = [sum(d['front']) for d in data]
    back_sums = [sum(d['back']) for d in data]
    
    avg_front = sum(front_sums) / len(front_sums)
    avg_back = sum(back_sums) / len(back_sums)
    
    return {
        'front': {
            'avg': round(avg_front, 1),
            'min': min(front_sums),
            'max': max(front_sums),
            'recent': front_sums[-10:]
        },
        'back': {
            'avg': round(avg_back, 1),
            'min': min(back_sums),
            'max': max(back_sums),
            'recent': back_sums[-10:]
        }
    }

# ============ 8b. 跨度分析 ============
def span_analysis(draws, recent_n=50):
    """分析前区跨度（最大-最小）趋势"""
    data = draws[-recent_n:]
    spans = [max(d['front']) - min(d['front']) for d in data]
    
    avg_span = round(sum(spans) / len(spans), 1) if spans else 0
    span_counter = Counter(spans)
    
    return {
        'avg': avg_span,
        'min': min(spans),
        'max': max(spans),
        'recent': spans[-10:],
        'distribution': dict(span_counter.most_common(8)),
        'most_common': span_counter.most_common(3)
    }

# ============ 9. 号码推荐引擎 (v3.0 - 蓝球优先+历史去重+区间比多样性+跨度优化) ============
def _check_historical_duplicate(front, back, draws, threshold=4, min_count=2):
    """检查一组号码历史上是否出现过>=threshold个相同号码>=min_count次"""
    f_set = set(front)
    b_set = set(back)
    count = 0
    for d in draws:
        match = sum(1 for n in d['front'] if n in f_set) + sum(1 for n in d['back'] if n in b_set)
        if match >= threshold:
            count += 1
    return count >= min_count

def _get_back_pair_freq(draws, recent_n=200):
    """分析后区号码对出现频率"""
    pair_counter = Counter()
    recent = draws[-recent_n:]
    for d in recent:
        pair = tuple(sorted(d['back']))
        pair_counter[pair] += 1
    # 找出最常见的后区对
    top_pairs = pair_counter.most_common(10)
    return dict(top_pairs), pair_counter

def generate_recommendations(draws, num_sets=5):
    """基于多维度分析生成推荐号码 — v3.1 大奖命中优化版"""
    all_draws = len(draws)
    
    # 全面分析
    hc_50 = hot_cold_analysis(draws, 50)
    hc_100 = hot_cold_analysis(draws, 100)
    hc_10 = hot_cold_analysis(draws, 10)    # 新增: 近10期超级热号
    hc_all = hot_cold_analysis(draws, all_draws)
    
    missing = missing_analysis(draws)
    oe = odd_even_analysis(draws, 50)
    zone = zone_analysis(draws, 50)
    consec = consecutive_analysis(draws, 100)
    sums = sum_analysis(draws, 50)
    
    # 上期开奖号 (用于延续加权)
    latest_draw = draws[-1]
    latest_front_set = set(latest_draw['front'])
    latest_back_set = set(latest_draw['back'])
    
    # 上上期开奖号 (用于跨期延续分析)
    if len(draws) >= 2:
        prev2_draw = draws[-2]
        prev2_front_set = set(prev2_draw['front'])
    else:
        prev2_front_set = set()
    
    # 后区号码对频率分析
    back_pair_freq, back_pair_counter = _get_back_pair_freq(draws, 200)
    most_common_back_pairs = set(k for k, v in back_pair_freq.items() if v >= 5)
    
    # ---- 前区评分 (v3.1 增强版) ----
    front_scores = {}
    for n in range(1, 36):
        score = 0
        reasons = []
        
        f10 = hc_10['front']['freq'].get(n, 0)
        f50 = hc_50['front']['freq'].get(n, 0)
        fall = hc_all['front']['freq'].get(n, 0)
        
        # 1. 频率评分 (近50期)
        f50 = hc_50['front']['freq'].get(n, 0)
        f100 = hc_100['front']['freq'].get(n, 0)
        fall = hc_all['front']['freq'].get(n, 0)
        
        if n in hc_50['front']['hot']:
            score += 3
            reasons.append(f"近50期热号(出现{f50}次)")
        elif n in hc_50['front']['warm']:
            score += 2
        elif n in hc_50['front']['cold']:
            score += 1
        
        # 2. 遗漏回补评分
        miss = missing['front'].get(n, 0)
        if miss >= 10 and f50 >= 3:
            score += 3
            reasons.append(f"遗漏{miss}期,历史热号,回补概率高")
        elif miss >= 8:
            score += 2
            reasons.append(f"遗漏{miss}期,冷号回补")
        elif miss <= 2 and f50 >= 2:
            score += 2
            reasons.append(f"近期活跃,仅遗漏{miss}期")
        
        # 5. 长期频率
        if fall >= 40:
            score += 1
        
        front_scores[n] = {'score': score, 'reasons': reasons, 'freq50': f50, 'freq10': f10, 'miss': miss}
    
    # ---- 后区评分 (v4.0 - 对评分 + 路数分析 + 近期回避) ----
    # 策略升级：
    # 1. 直接对后区"对"评分, 而非单独评分再组合
    # 2. 路数分析：避免同路对(00路,11路,22路), 优先0-1/0-2/1-2交叉
    # 3. 对"近期刚出现"的号码轻罚分, 对"长期未出"的加重权重
    # 4. 大小平衡：大(7-12)小(1-6)搭配优先
    
    # 分析最近几期后区奇偶状态
    recent_back_oe = []
    for d in draws[-10:]:
        recent_back_oe.append(sum(1 for n in d['back'] if n % 2 == 1))
    
    force_balanced = False
    if len(recent_back_oe) >= 2:
        if recent_back_oe[-1] in (0, 2) and recent_back_oe[-2] in (0, 2):
            force_balanced = True
    
    # 近期后区号码 (最近5期的号码, 给轻微罚分)
    recent_back_nums = set()
    for d in draws[-3:]:
        recent_back_nums.update(d['back'])
    
    # 计算每个后区对最近一次出现的距离
    pair_last_seen = {}
    for i in range(len(draws) - 1, -1, -1):
        d = draws[i]
        pair = tuple(sorted(d['back']))
        if pair not in pair_last_seen:
            pair_last_seen[pair] = len(draws) - i - 1
    
    # 路数分类 (0路:3,6,9,12; 1路:1,4,7,10; 2路:2,5,8,11)
    def road(n):
        return n % 3
    
    # 个体评分 (简化版, 用于候选排序)
    back_scores = {}
    for n in range(1, 13):
        score = 0
        f50 = hc_50['back']['freq'].get(n, 0)
        if n in hc_50['back']['hot']:
            score += 3
        elif n in hc_50['back']['warm']:
            score += 2
        elif n in hc_50['back']['cold']:
            score += 1
        
        miss = missing['back'].get(n, 0)
        if miss >= 12:
            score += 5  # 极冷强回补
        elif miss >= 8:
            score += 3
        elif miss >= 5:
            score += 2
        
        # 近期刚出罚分
        if n in recent_back_nums:
            score -= 1
        
        back_scores[n] = {'score': score, 'freq50': f50, 'miss': miss}
    
    back_ranked = sorted(back_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    
    # ---- 对所有后区对直接评分 ----
    all_pairs = []
    for i in range(1, 13):
        for j in range(i + 1, 13):
            n1, n2 = i, j
            pair = (n1, n2)
            s1, s2 = back_scores[n1]['score'], back_scores[n2]['score']
            
            pair_score = s1 + s2
            
            # 和值加分
            pair_sum = n1 + n2
            if 13 <= pair_sum <= 18:
                pair_score += 4
            elif 10 <= pair_sum <= 20:
                pair_score += 2
            
            # 奇偶平衡 (1奇1偶加2分)
            if (n1 % 2) != (n2 % 2):
                pair_score += 2
            
            # 大小平衡 (1大1小)
            big = (n1 >= 7) + (n2 >= 7)
            if big == 1:
                pair_score += 2
            
            # 路数交叉 (不同路加1分, 同路扣1分)
            r1, r2 = road(n1), road(n2)
            if r1 != r2:
                pair_score += 1
            else:
                pair_score -= 1
            
            # 对最近出现距离加分 (适度距离最优, 太远反而不好)
            last_seen = pair_last_seen.get(pair, len(draws))
            if last_seen >= 100:
                pair_score -= 1  # 太久没出反而轻罚分 (可能是历史上不常见的组合)
            elif last_seen >= 30:
                pair_score += 2  # 30-100期: 适度距离, 最优
            elif last_seen >= 15:
                pair_score += 1  # 15-30期: 可接受
            # <15期: 不加分, 也不扣分
            
            # 避免过于常见的对
            if pair in most_common_back_pairs:
                pair_score -= 4  # 加重扣分
            
            # 避免与上期后区完全相同
            if set(pair) == latest_back_set:
                pair_score -= 8  # 加重扣分, 几乎不选上期完全相同对
            
            # 检查对中是否有极度冷号 (个体遗漏>20期且近50期频率<2)
            for n in pair:
                if missing['back'].get(n, 0) > 20 and hc_50['back']['freq'].get(n, 0) < 2:
                    pair_score -= 2  # 极度冷号降分
            
            all_pairs.append({
                'pair': pair,
                'score': pair_score,
                'sum': pair_sum,
                'odd_even': f"{sum(1 for x in pair if x%2)}:{sum(1 for x in pair if x%2==0)}",
                'last_seen': last_seen
            })
    
    # 按评分排序所有对
    all_pairs.sort(key=lambda x: -x['score'])
    
    # 前区候选池 (在pair评分前定义)
    front_ranked = sorted(front_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    hot_front = [n for n, _ in front_ranked if n in hc_50['front']['hot']][:10]
    warm_front = [n for n, _ in front_ranked if n in hc_50['front']['warm']][:8]
    cold_front = [n for n, _ in front_ranked if n in hc_50['front']['cold'] and missing['front'].get(n, 0) >= 8][:6]
    
    import random
    
    def pick_front(pool_hot, pool_warm, pool_cold, n_hot, n_warm, n_cold):
        result = []
        if n_hot > 0 and pool_hot:
            result.extend(random.sample(pool_hot, min(n_hot, len(pool_hot))))
        if n_warm > 0 and pool_warm:
            result.extend(random.sample(pool_warm, min(n_warm, len(pool_warm))))
        if n_cold > 0 and pool_cold:
            result.extend(random.sample(pool_cold, min(n_cold, len(pool_cold))))
        while len(result) < 5:
            remaining = [n for n in range(1, 36) if n not in result and front_scores[n]['score'] >= 2]
            if remaining:
                result.append(random.choice(remaining))
            else:
                avail = [n for n in range(1, 36) if n not in result]
                result.append(random.choice(avail))
        return sorted(result[:5])
    
    
    # 从排名最高的5个对中选后区 (允许每个号最多出现2次, 让高分号有机会重复)
    selected_pairs = []
    num_freq = {i: 0 for i in range(1, 13)}  # 每个号码出现次数
    for ap in all_pairs:
        n1, n2 = ap['pair']
        if num_freq[n1] < 2 and num_freq[n2] < 2:
            selected_pairs.append(ap)
            num_freq[n1] += 1
            num_freq[n2] += 1
        if len(selected_pairs) >= 5:
            break
    
    # ---- 生成推荐 ----
    strategies = [
        {
            'name': '热号追踪', 'desc': '以近期热号为主搭配温号, 追求高频号码的持续热度',
            'front_hot': 3, 'front_warm': 2, 'front_cold': 0
        },
        {
            'name': '冷热均衡', 'desc': '热号与冷号回补各半, 平衡热度与回补机会',
            'front_hot': 2, 'front_warm': 1, 'front_cold': 2
        },
        {
            'name': '遗漏回补', 'desc': '重点关注遗漏较多的冷号, 捕捉回补时机',
            'front_hot': 1, 'front_warm': 1, 'front_cold': 3
        },
        {
            'name': '奇偶均衡', 'desc': '前区3:2或2:3, 后区1奇1偶, 追求结构合理性',
            'front_hot': 2, 'front_warm': 2, 'front_cold': 1
        },
        {
            'name': '综合优选', 'desc': '综合评分最高组合, 兼顾频率/遗漏/区间/蓝球命中率',
            'front_hot': 2, 'front_warm': 2, 'front_cold': 1
        }
    ]
    
    max_retries = 50  # 历史去重重试次数
    
    recommendations = []
    used_zone_ratios = set()
    target_zone_ratios = ['2:2:1', '2:1:2', '1:2:2', '3:1:1', '1:3:1']
    
    def get_zone_ratio(front_nums):
        z1 = sum(1 for n in front_nums if n <= 12)
        z2 = sum(1 for n in front_nums if 13 <= n <= 24)
        z3 = sum(1 for n in front_nums if 25 <= n <= 35)
        return f"{z1}:{z2}:{z3}"
    
    for i, strat in enumerate(strategies):
        random.seed(i * 73 + 42)
        
        # 后区: 直接从预计算的最高分对中取 (已保证去重+多样性)
        if i < len(selected_pairs):
            back_nums = sorted(list(selected_pairs[i]['pair']))
        else:
            back_nums = sorted(random.sample(list(range(1, 13)), 2))
        
        # 前区选择 — 强制区间比多样化
        target_zr = target_zone_ratios[i] if i < len(target_zone_ratios) else None
        front_nums = None
        zr = None
        
        for zr_retry in range(30):
            if i == 3:  # 奇偶均衡
                random.seed(100 + i + zr_retry * 7)
                odd_candidates = [n for n, s in front_ranked if n % 2 == 1 and s['score'] >= 2]
                even_candidates = [n for n, s in front_ranked if n % 2 == 0 and s['score'] >= 2]
                if len(odd_candidates) >= 3 and len(even_candidates) >= 2:
                    front_nums = sorted(random.sample(odd_candidates, 3) + random.sample(even_candidates, 2))
                elif len(odd_candidates) >= 2 and len(even_candidates) >= 3:
                    front_nums = sorted(random.sample(odd_candidates, 2) + random.sample(even_candidates, 3))
                else:
                    front_nums = pick_front(hot_front, warm_front, cold_front, 2, 2, 1)
            elif i == 4:  # 综合优选
                random.seed(200 + i + zr_retry * 11)
                top_front = [n for n, s in front_ranked[:20]]
                z1p = [n for n in top_front if 1 <= n <= 12]
                z2p = [n for n in top_front if 13 <= n <= 24]
                z3p = [n for n in top_front if 25 <= n <= 35]
                if z1p and z2p and z3p:
                    a, b, c = random.choice(z1p), random.choice(z2p), random.choice(z3p)
                    remaining = [n for n in top_front if n not in (a, b, c)]
                    front_nums = sorted([a, b, c] + random.sample(remaining, min(2, len(remaining))))
                else:
                    front_nums = sorted(random.sample(top_front[:15], min(5, len(top_front))))
            else:
                random.seed(i * 50 + i * 7 + zr_retry * 13)
                # 按目标区间比调整冷热池的区分布
                front_nums = pick_front(hot_front, warm_front, cold_front, 
                                        strat['front_hot'], strat['front_warm'], strat['front_cold'])
            
            zr = get_zone_ratio(front_nums)
            if zr not in used_zone_ratios:
                used_zone_ratios.add(zr)
                break
            if zr_retry == 29:
                used_zone_ratios.add(zr)  # 放弃，允许重复
        
        # 历史去重 (仅前区,后区已预选最优对)
        retry_count = 0
        while _check_historical_duplicate(front_nums, back_nums, draws) and retry_count < max_retries:
            retry_count += 1
            random.seed(i * 73 + retry_count * 137)
            front_nums = pick_front(hot_front, warm_front, cold_front, 
                                    strat['front_hot'], strat['front_warm'], strat['front_cold'])
        
        # 去重检查
        if len(set(front_nums)) < 5:
            seen = set()
            unique = []
            for n in front_nums:
                if n not in seen:
                    seen.add(n)
                    unique.append(n)
            while len(unique) < 5:
                avail = [n for n in range(1, 36) if n not in set(unique)]
                unique.append(random.choice(avail))
            front_nums = sorted(unique[:5])
        
        # 生成推荐理由
        reasons = []
        front_odd = sum(1 for n in front_nums if n % 2 == 1)
        back_odd = sum(1 for n in back_nums if n % 2 == 1)
        
        reasons.append(f"策略: {strat['name']} - {strat['desc']}")
        reasons.append(f"前区奇偶比 {front_odd}:{5-front_odd}，后区奇偶比 {back_odd}:{2-back_odd}")
        
        # 后区分析
        back_sum = sum(back_nums)
        reasons.append(f"后区和值: {back_sum} {'(黄金区间13-18)' if 13 <= back_sum <= 18 else ''}")
        
        front_miss = [(n, missing['front'].get(n, 0)) for n in front_nums]
        missing_long = [n for n, m in front_miss if m >= 8]
        if missing_long:
            reasons.append(f"前区含遗漏较长的回补号: {missing_long}")
        
        zone_dist = {}
        for n in front_nums:
            if n <= 12: z = "一区(01-12)"
            elif n <= 24: z = "二区(13-24)"
            else: z = "三区(25-35)"
            zone_dist[z] = zone_dist.get(z, 0) + 1
        reasons.append(f"前区区间分布: {dict(zone_dist)}")
        
        # 跨度 (新浪走势图引入指标)
        front_span = max(front_nums) - min(front_nums)
        span_tag = ''
        if 15 <= front_span <= 25:
            span_tag = '(常见跨度区间15-25)'
        elif front_span > 25:
            span_tag = '(大跨度)'
        else:
            span_tag = '(小跨度)'
        reasons.append(f"前区跨度: {front_span} {span_tag}")
        
        front_sum = sum(front_nums)
        in_range = 80 <= front_sum <= 121
        reasons.append(f"前区和值: {front_sum} {'(在80-121黄金区间内)' if in_range else '(历史均值约'+str(sums['front']['avg'])+')'}")
        
        front_total_score = sum(front_scores[n]['score'] for n in front_nums)
        
        recommendations.append({
            'index': i + 1,
            'strategy': strat['name'],
            'description': strat['desc'],
            'front': front_nums,
            'back': back_nums,
            'front_odd_even': f"{front_odd}:{5-front_odd}",
            'back_odd_even': f"{back_odd}:{2-back_odd}",
            'zone_ratio': zr if zr else get_zone_ratio(front_nums),
            'span': front_span,
            'reasons': reasons,
            'confidence_score': min(round(front_total_score / 25 * 100, 1), 95.0)
        })
    
    # 最终强制去重：确保10个后区号码完全无重复，区间比多样化
    all_back_nums = []
    for r in recommendations:
        all_back_nums.extend(r['back'])
    
    # 后区号码去重：每个号最多出现1次
    if len(set(all_back_nums)) < 10:
        used = set()
        for i, r in enumerate(recommendations):
            new_back = []
            for n in r['back']:
                if n not in used:
                    new_back.append(n)
                    used.add(n)
                else:
                    # 找未使用的高评分替代号
                    for alt, s in back_ranked[:12]:
                        if alt not in used and alt not in new_back:
                            new_back.append(alt)
                            used.add(alt)
                            break
            if len(new_back) < 2:
                for x in range(1, 13):
                    if x not in used and x not in new_back:
                        new_back.append(x)
                        used.add(x)
                        if len(new_back) == 2:
                            break
            r['back'] = sorted(new_back[:2])
            # 更新后区奇偶比
            bo = sum(1 for x in r['back'] if x % 2 == 1)
            r['back_odd_even'] = f"{bo}:{2-bo}"
    
    return recommendations


# ============ 10. 回测分析 ============
def backtest_recommendations(draws, prev_rec_path):
    """加载上次推荐，与已开奖数据对比分析"""
    if not os.path.exists(prev_rec_path):
        return None
    
    with open(prev_rec_path, 'r', encoding='utf-8') as f:
        prev = json.load(f)
    
    target_issue = prev.get('target_issue', '')
    # 在历史数据中查找目标期号
    target_draw = None
    for d in draws:
        if d['issue'] == target_issue:
            target_draw = d
            break
    
    if not target_draw:
        return {
            'status': 'pending',
            'message': f'第{target_issue}期尚未开奖或数据未更新',
            'target_issue': target_issue,
            'prev_recommendations': prev.get('recommendations', [])
        }
    
    # 已开奖，逐注对比
    actual_front = set(target_draw['front'])
    actual_back = set(target_draw['back'])
    
    results_detail = []
    best_front_match = 0
    best_back_match = 0
    best_combined = 0
    total_front_hits = 0
    total_back_hits = 0
    
    for rec in prev.get('recommendations', []):
        rec_front = set(rec['front'])
        rec_back = set(rec['back'])
        
        front_hit = rec_front & actual_front
        back_hit = rec_back & actual_back
        
        f_count = len(front_hit)
        b_count = len(back_hit)
        
        total_front_hits += f_count
        total_back_hits += b_count
        best_front_match = max(best_front_match, f_count)
        best_back_match = max(best_back_match, b_count)
        best_combined = max(best_combined, f_count + b_count)
        
        results_detail.append({
            'strategy': rec['strategy'],
            'recommended_front': rec['front'],
            'recommended_back': rec['back'],
            'front_hit': sorted(list(front_hit)),
            'back_hit': sorted(list(back_hit)),
            'front_hit_count': f_count,
            'back_hit_count': b_count
        })
    
    # 评分
    prize_level = '未中奖'
    if best_front_match >= 5 and best_back_match >= 2:
        prize_level = '一等奖'
    elif best_front_match >= 5 and best_back_match >= 1:
        prize_level = '二等奖'
    elif best_front_match >= 5:
        prize_level = '三等奖'
    elif best_front_match >= 4 and best_back_match >= 2:
        prize_level = '四等奖'
    elif best_front_match >= 4 and best_back_match >= 1:
        prize_level = '五等奖'
    elif best_front_match >= 3 and best_back_match >= 2:
        prize_level = '六等奖'
    elif best_front_match >= 4:
        prize_level = '七等奖'
    elif best_front_match >= 3 and best_back_match >= 1:
        prize_level = '八等奖'
    elif best_front_match >= 2 and best_back_match >= 2:
        prize_level = '九等奖'
    elif (best_front_match >= 3) or (best_front_match >= 2 and best_back_match >= 1) or (best_front_match >= 1 and best_back_match >= 2) or (best_back_match >= 2):
        prize_level = '九等奖'
    elif best_front_match >= 1 and best_back_match >= 1:
        prize_level = '未中奖(仅1+1)'
    elif best_front_match >= 1 or best_back_match >= 1:
        prize_level = '未中奖(仅中1个)'
    
    return {
        'status': 'drawn',
        'target_issue': target_issue,
        'target_date': target_draw['date'],
        'actual_front': target_draw['front'],
        'actual_back': target_draw['back'],
        'prev_recommendations': prev.get('recommendations', []),
        'results': results_detail,
        'summary': {
            'best_front_match': best_front_match,
            'best_back_match': best_back_match,
            'best_combined': best_combined,
            'total_front_hits': total_front_hits,
            'total_back_hits': total_back_hits,
            'prize_level': prize_level
        }
    }


def save_recommendations(recs, target_issue, save_path):
    """保存本次推荐，供下次回测使用"""
    data = {
        'target_issue': target_issue,
        'generated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'recommendations': [
            {
                'strategy': r['strategy'],
                'front': r['front'],
                'back': r['back'],
                'description': r.get('description', '')
            }
            for r in recs
        ]
    }
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


# ============ 11. 主程序 ============
def main():
    base_dir = r"C:\Users\Administrator\WorkBuddy\2026-06-19-16-28-32"
    filepath = os.path.join(base_dir, "TcDLT355history.txt")
    prev_rec_path = os.path.join(base_dir, "last_recommendation.json")
    json_path = os.path.join(base_dir, "analysis_result.json")
    
    draws = parse_data(filepath)
    print(f"解析完成: 共 {len(draws)} 期数据")
    print(f"最新一期: {draws[-1]['issue']} ({draws[-1]['date']})")
    
    latest = draws[-1]
    print(f"\n最新开奖: {latest['issue']}期 {latest['date']}")
    print(f"  前区: {' '.join(f'{n:02d}' for n in latest['front'])}")
    print(f"  后区: {' '.join(f'{n:02d}' for n in latest['back'])}")
    
    # ---- 回测：检查上次推荐是否已开奖 ----
    backtest = backtest_recommendations(draws, prev_rec_path)
    if backtest and backtest['status'] == 'drawn':
        print("\n" + "="*60)
        print(f"【回测分析】上次推荐目标期号: {backtest['target_issue']}")
        print(f"实际开奖日期: {backtest['target_date']}")
        print(f"实际前区: {' '.join(f'{n:02d}' for n in backtest['actual_front'])}")
        print(f"实际后区: {' '.join(f'{n:02d}' for n in backtest['actual_back'])}")
        s = backtest['summary']
        print(f"\n最佳成绩: 前区中{s['best_front_match']}个 / 后区中{s['best_back_match']}个 = 合计{s['best_combined']}个")
        print(f"可能奖项: {s['prize_level']}")
        print(f"\n逐注对比:")
        for r in backtest['results']:
            print(f"  [{r['strategy']}] 前区:{r['front_hit_count']}个 {r['front_hit']} | 后区:{r['back_hit_count']}个 {r['back_hit']}")
    elif backtest and backtest['status'] == 'pending':
        print(f"\n【回测状态】{backtest['message']} ⏳")
    else:
        print("\n【回测状态】无历史推荐记录，首次运行")
    
    # 全面分析
    hc = hot_cold_analysis(draws, 50)
    missing = missing_analysis(draws)
    oe = odd_even_analysis(draws, 50)
    zone = zone_analysis(draws, 50)
    consec = consecutive_analysis(draws, 100)
    sums = sum_analysis(draws, 50)
    sp = span_analysis(draws, 50)
    
    # 生成推荐（目标：下一期）
    recs = generate_recommendations(draws, 5)
    next_issue = f"2026{int(draws[-1]['issue'][4:]) + 1:03d}"
    
    # 保存本次推荐供下次回测
    save_recommendations(recs, next_issue, prev_rec_path)
    print(f"\n已保存推荐记录 -> {prev_rec_path} (目标期号: {next_issue})")
    
    # 输出分析结果
    print("\n" + "="*60)
    print("【近50期冷热号分析】")
    print(f"前区热号: {hc['front']['hot']}")
    print(f"前区冷号: {hc['front']['cold']}")
    print(f"后区热号: {hc['back']['hot']}")
    print(f"后区冷号: {hc['back']['cold']}")
    
    print("\n【遗漏分析 - 遗漏最长前10】")
    for n, m in missing['front_top_missing']:
        print(f"  前区 {n:02d}: 遗漏 {m} 期")
    print("后区遗漏最长:")
    for n, m in missing['back_top_missing'][:6]:
        print(f"  后区 {n:02d}: 遗漏 {m} 期")
    
    print("\n【奇偶比趋势(近50期)】")
    print(f"  前区: {oe['front']}")
    print(f"  后区: {oe['back']}")
    
    print("\n【和值分析(近50期)】")
    print(f"  前区均值和: {sums['front']['avg']} (范围 {sums['front']['min']}-{sums['front']['max']})")
    print(f"  后区均值和: {sums['back']['avg']} (范围 {sums['back']['min']}-{sums['back']['max']})")
    
    print(f"\n【跨度分析(近50期, 新浪走势图引入)】")
    print(f"  前区跨度均值: {sp['avg']} (范围 {sp['min']}-{sp['max']})")
    print(f"  最常见跨度: {sp['most_common']}")
    
    print("\n【连号概率(近100期)】")
    print(f"  出现连号: {consec['count']}/{consec['total']} = {consec['rate']:.1%}")
    
    print("\n" + "="*60)
    print(f"【推荐号码 — 第{next_issue}期】")
    for r in recs:
        print(f"\n第{r['index']}注 — {r['strategy']}")
        print(f"  前区: {' '.join(f'{n:02d}' for n in r['front'])}")
        print(f"  后区: {' '.join(f'{n:02d}' for n in r['back'])}")
        print(f"  奇偶: 前{r['front_odd_even']} 后{r['back_odd_even']}")
        print(f"  推荐理由:")
        for reason in r['reasons']:
            print(f"    - {reason}")
    
    # 保存完整分析结果到JSON
    result = {
        'meta': {
            'total_draws': len(draws),
            'latest_issue': draws[-1]['issue'],
            'latest_date': draws[-1]['date'],
            'latest_front': draws[-1]['front'],
            'latest_back': draws[-1]['back'],
            'next_issue': next_issue,
            'next_date': '2026/06/20',  # approximate
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'backtest': backtest,
        'hot_cold': hc,
        'missing': {
            'front': dict(missing['front']),
            'back': dict(missing['back']),
            'front_top': [[n, m] for n, m in missing['front_top_missing']],
            'back_top': [[n, m] for n, m in missing['back_top_missing']]
        },
        'odd_even': oe,
        'zone': zone,
        'consecutive': {
            'rate': consec['rate'],
            'count': consec['count'],
            'total': consec['total'],
            'pairs': {str(k): v for k, v in consec.get('pairs', {}).items()}
        },
        'sum': sums,
        'span': sp,
        'recommendations': recs,
        # 前区频率数据 (用于HTML)
        'front_freq_all': [{'num': n, 'count': hc['front']['freq'].get(n, 0)} for n in range(1, 36)],
        'back_freq_all': [{'num': n, 'count': hc['back']['freq'].get(n, 0)} for n in range(1, 13)],
        # 全历史前区频率
        'front_freq_total': [{'num': n, 'count': sum(1 for d in draws if n in d['front'])} for n in range(1, 36)],
        'back_freq_total': [{'num': n, 'count': sum(1 for d in draws if n in d['back'])} for n in range(1, 13)],
        # 最近10期
        'recent_10': draws[-10:],
        # 连号对
        'consecutive_pairs': {str(k): v for k, v in consec.get('pairs', {}).items()},
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n分析结果已保存至: {json_path}")
    
    return result

if __name__ == '__main__':
    main()
