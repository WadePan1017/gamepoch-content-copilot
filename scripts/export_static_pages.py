import asyncio
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import (
    api_content_brief,
    api_content_calendar,
    api_event_planner,
    api_event_planner_detail,
    build_topic_opportunity,
    get_content_opportunities,
)


TEMPLATE = ROOT / "templates" / "index.html"
OUT_DIR = ROOT / "docs"
OUT_FILE = OUT_DIR / "index.html"


def js_string(value):
    return json.dumps(value, ensure_ascii=False)


async def collect_data():
    opportunities = await get_content_opportunities(refresh=True)
    enhance_opportunities(opportunities)
    brief = await api_content_brief()
    calendar = await api_content_calendar()
    events = await api_event_planner()
    event_details = {}
    for event in events.get("events", []):
        event_details[event["id"]] = await api_event_planner_detail(event["id"])

    topic_examples = {}
    for topic in [
        "影之刃零 Phantom Blade Zero",
        "黑神话：悟空",
        "艾尔登法环：黑夜君临",
        "Steam Next Fest 试玩节",
    ]:
        topic_examples[topic] = await build_topic_opportunity(topic)

    return {
        "opportunities": opportunities,
        "brief": brief,
        "calendar": calendar,
        "events": events,
        "eventDetails": event_details,
        "topicExamples": topic_examples,
    }


def svg_image(label, bg="#e0f2fe", fg="#2563eb"):
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 640 360'>"
        f"<rect width='640' height='360' fill='{bg}'/>"
        "<circle cx='560' cy='80' r='140' fill='rgba(255,255,255,.34)'/>"
        "<circle cx='80' cy='320' r='180' fill='rgba(255,255,255,.28)'/>"
        f"<text x='48' y='178' font-size='42' font-weight='700' font-family='Arial, sans-serif' fill='{fg}'>{label}</text>"
        f"<text x='50' y='226' font-size='20' font-family='Arial, sans-serif' fill='{fg}' opacity='.72'>Content Opportunity</text>"
        "</svg>"
    )
    return "data:image/svg+xml;charset=utf-8," + svg.replace("#", "%23").replace(" ", "%20")


def enhance_opportunities(data):
    image_by_id = {
        "curated-phantom-blade-zero": svg_image("Phantom Blade Zero", "#e0e7ff", "#3730a3"),
        "curated-black-myth": "https://cdn.akamai.steamstatic.com/steam/apps/2358720/header.jpg",
        "curated-elden-ring-nightreign": "https://cdn.akamai.steamstatic.com/steam/apps/2622380/header.jpg",
        "curated-split-fiction": "https://cdn.akamai.steamstatic.com/steam/apps/2001120/header.jpg",
        "curated-steam-next-fest": svg_image("Steam Next Fest"),
    }
    extra = [
        {
            "id": "rank-monster-hunter-wilds",
            "type": "game",
            "source": "Steam热度榜",
            "bucket": "rank",
            "title": "Monster Hunter Wilds",
            "summary": "大型动作共斗游戏适合做版本更新、玩家回流、装备流派和多人联机体验内容。",
            "angle": "共斗游戏更新后，玩家最关心哪些变化？",
            "image": "https://cdn.akamai.steamstatic.com/steam/apps/2246340/header.jpg",
            "url": "https://store.steampowered.com/app/2246340/",
            "heat": 87,
            "trend": "+18%",
            "tags": ["Steam热度", "共斗", "版本更新"],
            "recommended_formats": ["30秒脚本", "B站解析", "小红书清单", "日报条目"],
        },
        {
            "id": "rank-stellar-blade",
            "type": "game",
            "source": "Steam热度榜",
            "bucket": "rank",
            "title": "Stellar Blade",
            "summary": "主机移植与PC玩家讨论度高，适合做配置表现、画面对比、入坑建议和海外评价整理。",
            "angle": "主机游戏登陆PC后，内容团队应该先看什么？",
            "image": "https://cdn.akamai.steamstatic.com/steam/apps/3489700/header.jpg",
            "url": "https://store.steampowered.com/app/3489700/",
            "heat": 86,
            "trend": "+15%",
            "tags": ["主机移植", "PC表现", "海外口碑"],
            "recommended_formats": ["短视频切片", "购买建议", "海外资讯", "封面文案"],
        },
        {
            "id": "rank-marvel-rivals",
            "type": "game",
            "source": "Steam热度榜",
            "bucket": "rank",
            "title": "Marvel Rivals",
            "summary": "多人竞技游戏适合持续跟进赛季更新、角色强度、玩家情绪和社区争议。",
            "angle": "竞技游戏赛季内容怎样拆成连续选题？",
            "image": "https://cdn.akamai.steamstatic.com/steam/apps/2767030/header.jpg",
            "url": "https://store.steampowered.com/app/2767030/",
            "heat": 85,
            "trend": "+11%",
            "tags": ["赛季更新", "竞技", "玩家情绪"],
            "recommended_formats": ["15秒短视频", "30秒脚本", "争议点分析", "日报"],
        },
        {
            "id": "rank-silk-song",
            "type": "game",
            "source": "愿望单观察",
            "bucket": "rank",
            "title": "Hollow Knight: Silksong",
            "summary": "高期待独立游戏适合做愿望单观察、发布节奏、玩家期待和同类游戏推荐。",
            "angle": "高期待独立游戏为什么适合提前做内容池？",
            "image": "https://cdn.akamai.steamstatic.com/steam/apps/1030300/header.jpg",
            "url": "https://store.steampowered.com/app/1030300/",
            "heat": 84,
            "trend": "+9%",
            "tags": ["独立游戏", "愿望单", "期待值"],
            "recommended_formats": ["B站解析", "小红书笔记", "选题池", "日报"],
        },
        {
            "id": "rank-hades-ii",
            "type": "game",
            "source": "Steam热度榜",
            "bucket": "rank",
            "title": "Hades II",
            "summary": "高口碑续作适合做版本更新、流派推荐、玩家评价和同类动作Roguelike内容。",
            "angle": "高口碑续作更新后，内容团队怎么判断是否值得跟进？",
            "image": "https://cdn.akamai.steamstatic.com/steam/apps/1145350/header.jpg",
            "url": "https://store.steampowered.com/app/1145350/",
            "heat": 83,
            "trend": "+8%",
            "tags": ["Roguelike", "口碑", "版本更新"],
            "recommended_formats": ["B站解析", "短视频脚本", "小红书清单", "日报"],
        },
        {
            "id": "rank-dont-starve-together",
            "type": "game",
            "source": "Steam热度榜",
            "bucket": "rank",
            "title": "Don't Starve Together",
            "summary": "长线运营游戏适合做促销节点、好友联机、入坑指南和老玩家回流内容。",
            "angle": "长线联机游戏为什么适合反复做入坑内容？",
            "image": "https://cdn.akamai.steamstatic.com/steam/apps/322330/header.jpg",
            "url": "https://store.steampowered.com/app/322330/",
            "heat": 81,
            "trend": "+6%",
            "tags": ["长线运营", "联机", "入坑指南"],
            "recommended_formats": ["入坑建议", "30秒脚本", "促销提醒", "日报条目"],
        },
        {
            "id": "rank-indie-radar",
            "type": "news",
            "source": "海外资讯",
            "bucket": "rank",
            "title": "独立游戏黑马监控",
            "summary": "适合从Steam新品、试玩节和Reddit讨论中筛选潜力项目，形成每日选题池。",
            "angle": "发行团队怎样更早发现可能爆的独立游戏？",
            "image": svg_image("Indie Radar", "#dcfce7", "#15803d"),
            "url": "",
            "heat": 80,
            "trend": "+7%",
            "tags": ["黑马预测", "试玩节", "选题池"],
            "recommended_formats": ["日报条目", "B站清单", "短视频脚本", "市场观察"],
        },
    ]

    event_only_ids = {"curated-gamescom", "rank-tga-watch"}
    opportunities = [item for item in data.get("opportunities", []) if item.get("id") not in event_only_ids]
    seen = {item.get("id") for item in opportunities}
    for idx, item in enumerate(opportunities):
        item.setdefault("trend", f"+{max(5, 26 - idx * 2)}%")
        if not item.get("image"):
            item["image"] = image_by_id.get(item.get("id"), svg_image("Game Radar"))
    for item in extra:
        if item["id"] not in seen:
            opportunities.append(item)
    opportunities.sort(key=lambda item: item.get("heat", 0), reverse=True)
    data["opportunities"] = opportunities[:12]
    data["hero"] = data["opportunities"][0] if data["opportunities"] else data.get("hero")
    data["stats"]["opportunities"] = len(data["opportunities"])
    data["stats"]["short_video_topics"] = min(28, len(data["opportunities"]) * 2)
    data["stats"]["news_items"] = len([item for item in data["opportunities"] if item.get("type") == "news"])
    data["stats"]["risk_items"] = len([item for item in data["opportunities"] if item.get("heat", 0) >= 85])


def build_static_api_script(data):
    return f"""
<script>
window.__GAMEPOCH_STATIC_DATA__ = {js_string(data)};
(function(){{
    const staticData = window.__GAMEPOCH_STATIC_DATA__;
    const nativeFetch = window.fetch.bind(window);

    function responseJson(data){{
        return Promise.resolve(new Response(JSON.stringify(data), {{
            status: 200,
            headers: {{'Content-Type':'application/json;charset=utf-8'}}
        }}));
    }}

    function pick(options, seed){{
        return options[Math.abs(seed) % options.length];
    }}

    function topicProfile(item){{
        const text = `${{item.title || ''}} ${{item.summary || ''}} ${{(item.tags || []).join(' ')}}`.toLowerCase();
        if(text.includes('gamescom') || text.includes('展会')) {{
            return {{
                audience: '发行团队、现场跟拍、内容运营',
                selling: '活动前就能拆出镜头清单、采访问题和复盘内容',
                emotion: '提前准备，减少现场漏拍',
                proof: '展会信息密度高，必须把必拍镜头和素材归档提前列清楚',
                cta: '把它拆成活动前、中、后三段内容包'
            }};
        }}
        if(text.includes('next fest') || text.includes('试玩')) {{
            return {{
                audience: 'Steam玩家、独立游戏关注者、选题运营',
                selling: '试玩节适合快速筛选潜力新品和内容切入点',
                emotion: '趁讨论刚起来，先做第一波内容',
                proof: '试玩节期间玩家评论、愿望单和主播反馈会集中出现',
                cta: '优先做试玩清单和黑马预测'
            }};
        }}
        if(text.includes('影之刃') || text.includes('phantom')) {{
            return {{
                audience: '主机玩家、动作游戏玩家、海外玩家',
                selling: '国产动作游戏的视觉、战斗和海外传播点',
                emotion: '国产动作游戏能不能打动海外主机玩家',
                proof: '玩家会关注实机质量、战斗节奏、Boss演出和平台表现',
                cta: '评论区选一个你最关心的实机问题'
            }};
        }}
        if(text.includes('黑神话') || text.includes('悟空')) {{
            return {{
                audience: '国产游戏玩家、海外媒体关注者、主机玩家',
                selling: '高认知IP适合做长尾复盘和海外口碑整理',
                emotion: '爆款之后还能继续讲什么',
                proof: '玩家仍在讨论优化、Boss设计、DLC预期和同类游戏机会',
                cta: '收藏这份国产游戏内容复盘清单'
            }};
        }}
        if(text.includes('elden') || text.includes('艾尔登') || text.includes('黑夜')) {{
            return {{
                audience: '魂系玩家、动作RPG玩家、Steam玩家',
                selling: '利用玩家争议点做版本判断和购买建议',
                emotion: '别只看热度，先看它到底适不适合你',
                proof: '同类游戏玩家会关注难度、联机、地图重复度和内容量',
                cta: '想看详细评测还是入坑建议，评论区选一个'
            }};
        }}
        return {{
            audience: '核心玩家、内容运营、发行团队',
            selling: '把热点拆成标题、脚本、素材和发布动作',
            emotion: '这个热点值不值得今天做',
            proof: '热度、玩家讨论和可获得素材决定内容优先级',
            cta: '需要完整内容包可以继续生成'
        }};
    }}

    function buildTopic(q){{
        const cached = staticData.topicExamples[q];
        if(cached) return cached;
        return {{
            id: `custom-${{Date.now()}}`,
            type: 'custom',
            source: '手动输入',
            bucket: 'custom',
            title: q,
            summary: `${{q}} 是手动输入的内容方向，可快速生成平台标题、短视频脚本、素材清单和团队工作单。`,
            angle: `${{q}} 今天为什么值得内容团队跟进？`,
            image: '',
            url: '',
            heat: 82,
            tags: ['手动选题','内容生成','快速拆解'],
            recommended_formats: ['B站解析','30秒脚本','小红书笔记','团队简报']
        }};
    }}

    function buildDeliveryWorkOrder(title, angle, profile){{
        return `# ${{title}} 剪辑交付工作单

## 1. 今天为什么剪
- 推荐角度：${{angle}}
- 目标受众：${{profile.audience}}
- 核心价值：${{profile.selling}}
- 判断标准：能不能在30秒内讲清“为什么值得关注、适合谁、风险是什么”。

## 2. 30秒成片结构
- 0-3秒：强问题开场，必须出现游戏名和核心判断。
- 3-8秒：放来源画面，证明不是空泛跟热点。
- 8-18秒：三段信息，分别讲亮点、玩家关注点、争议/风险。
- 18-25秒：给购买建议、入坑建议或内容判断。
- 25-30秒：评论区问题，引导用户选择下一条内容方向。

## 3. 素材准备
- 01_key_visual：主视觉 / Steam页 / 官方图。
- 02_gameplay：实机或预告片高能片段3段。
- 03_social_proof：玩家评论、海外媒体标题、热度截图。
- 04_compare：同类游戏或平台标签对比素材。
- 05_cover：封面底图、标题短句、字幕关键词。

## 4. 剪辑要求
- 画幅：9:16优先，兼容16:9二次裁切。
- 字幕：每屏不超过18个字，只保留关键词。
- 节奏：前10秒至少3次画面变化，避免纯口播。
- 封面：一版问题式，一版判断式，一版入坑/避坑式。

## 5. 发布前核查
- 游戏名、平台、发售/活动时间是否准确。
- 素材是否来自官方或可引用来源。
- 标题是否过度承诺或容易引战。
- 评论截图是否遮挡个人隐私信息。

## 6. 团队分工
- 剪辑：产出30秒短视频、字幕版和工程文件。
- 运营：选平台标题，安排发布时间。
- 素材：补齐来源链接和素材文件夹。
- 负责人：审核风险点，决定是否扩展成长视频。`;
    }}

    function buildPack(item){{
        const variant = Number(item._variant || 0);
        const title = item.title || '今日游戏热点';
        const angle = item.angle || `${{title}} 今天为什么值得做内容？`;
        const profile = topicProfile(item);
        const hook = pick([
            `${{title}}突然被玩家讨论，真正原因可能不是你想的那样`,
            `别只看热度，${{title}}更值得拆的是这三个内容点`,
            `${{title}}适不适合今天做内容？先看玩家最关心什么`
        ], variant);

        const titles = {{
            bilibili: [
                `${{title}}为什么值得做一期深度解析？`,
                `看完这3点，再决定要不要跟进${{title}}`,
                `${{title}}：玩家关注点、争议和内容机会一次讲清`
            ],
            douyin: [
                `${{title}}最近为什么突然这么多人讨论？`,
                `别急着跟风，${{title}}先看这3点`,
                `30秒看懂${{title}}值不值得做内容`
            ],
            xiaohongshu: [
                `${{title}}适合现在入坑吗？`,
                `${{title}}内容选题笔记：亮点、风险、受众`,
                `今天刷到${{title}}，我建议先看这几个点`
            ],
            wechat: [
                `海外游戏内容日报：${{title}}带来的内容机会`,
                `从${{title}}看近期玩家关注趋势`,
                `${{title}}热点观察：发行团队可以怎么跟进`
            ]
        }};

        const scripts = {{
            '15s': `0-3秒：${{title}}今天值得关注。\\n3-9秒：核心不是单纯热度，而是${{profile.selling}}。\\n9-15秒：先用一个短视频测试玩家反馈，再决定是否做长内容。`,
            '30s': `0-3秒：${{hook}}。\\n3-10秒：交代背景，${{title}}正在形成新的讨论热度。\\n10-22秒：拆三点：${{profile.selling}}、${{profile.proof}}、目标受众是${{profile.audience}}。\\n22-30秒：行动号召：${{profile.cta}}。`,
            '60s': `开场：${{hook}}。\\n背景：这类内容适合先判断玩家讨论是否真实增长，而不是只看一个热搜。\\n第一点：受众是谁。${{profile.audience}}最容易被这个选题触达。\\n第二点：为什么现在做。${{profile.proof}}。\\n第三点：怎么做。先做30秒短视频验证反馈，再扩展成B站解析、小红书笔记和团队日报。\\n结尾：${{profile.cta}}。`
        }};

        const shotList = [
            {{time:'0-3秒', screen:'游戏主视觉/Steam页面/活动Logo快速切入', voice: hook, edit:'大字标题压屏，节奏快'}},
            {{time:'3-8秒', screen:'玩家评论、热度榜、资讯标题三连切', voice:`先证明它不是随便挑的热点，而是有讨论、有素材、有受众。`, edit:'用箭头或高亮标出讨论点'}},
            {{time:'8-16秒', screen:'实机片段或官方素材', voice:`核心卖点：${{profile.selling}}。`, edit:'保留关键动作或画面冲击点'}},
            {{time:'16-24秒', screen:'争议点/风险点/适合人群卡片', voice:`但要注意：内容角度不能只夸，要把适合谁、不适合谁讲清楚。`, edit:'三栏信息卡'}},
            {{time:'24-30秒', screen:'封面文案+评论区引导', voice: profile.cta, edit:'结尾停留1秒，方便截图和转发'}}
        ];

        const workOrder = `# ${{title}} 内容工作单\\n\\n## 选题判断\\n- 推荐角度：${{angle}}\\n- 目标受众：${{profile.audience}}\\n- 今天价值：${{profile.selling}}\\n\\n## 剪辑任务\\n- 产出1条30秒短视频，按5段分镜执行。\\n- 准备3张封面文案版本，优先测试强问题式标题。\\n- 素材按“主视觉 / 实机 / 评论 / 风险点 / CTA”归档。\\n\\n## 运营任务\\n- B站做解析标题，抖音做问题式钩子，小红书做清单式笔记。\\n- 发布后30分钟记录评论关键词，决定是否追加长视频。\\n\\n## 发布前核查\\n- 核对游戏名、平台、时间和来源。\\n- 避免未确认爆料和过度承诺。\\n- 标注素材来源，避免版权风险。`;

        return {{
            titles,
            scripts,
            shot_list: shotList,
            cover_copy: [
                `${{title}}\\n今天为什么火？`,
                `别急着跟风\\n先看这3点`,
                `玩家真正关心的\\n不是表面热度`
            ],
            publish_copy: {{
                douyin: `${{title}}今天适合快速跟一个短视频。重点不是堆信息，而是把玩家为什么关注、有什么争议、值不值得继续看讲清楚。#游戏资讯 #主机游戏 #Steam`,
                xiaohongshu: `${{title}}内容选题笔记：\\n1. 适合人群：${{profile.audience}}\\n2. 核心亮点：${{profile.selling}}\\n3. 风险：注意来源、素材和过度标题\\n建议先收藏，做内容前对照检查。`,
                bilibili_desc: `本期从玩家关注点、内容机会和发布风险三个角度拆解${{title}}。适合关注游戏发行、海外资讯和短视频选题的同学参考。`
            }},
            asset_checklist: [
                '官方主视觉或Steam页面截图',
                '15-30秒实机/预告片关键片段',
                '玩家评论或海外媒体标题截图',
                '平台信息、发售时间、价格或活动时间',
                '封面三版文案和字幕模板'
            ],
            risk_checklist: [
                '未确认爆料不写成事实',
                '避免绝对化标题，例如必爆、封神、完胜',
                '素材来源保留链接，避免版权争议',
                '涉及评价时区分玩家反馈和个人判断'
            ],
            editing_notes: [
                '前3秒必须出现明确问题，不要铺垫太长',
                '每8秒切一次信息层级，避免纯旁白',
                '评论/数据截图只保留关键词，高亮重点',
                '结尾给出可执行互动问题'
            ],
            interview: [
                `你认为${{title}}最能打动目标玩家的点是什么？`,
                '如果只能剪30秒，必须保留哪一个镜头？',
                '这个选题最大的传播风险是什么？',
                '后续是否适合扩展成长视频或日报条目？'
            ],
            owner_tasks: [
                {{role:'剪辑', task:'按5段分镜剪一条30秒短视频', output:'30秒成片+字幕版'}},
                {{role:'运营', task:'选择平台标题并安排发布时间', output:'B站/抖音/小红书标题'}},
                {{role:'素材', task:'补齐主视觉、实机、评论、来源链接', output:'素材文件夹'}},
                {{role:'负责人', task:'审核风险点和发布优先级', output:'是否发布/是否扩展长内容'}}
            ],
            value_summary: {{
                time_saved:'约60-90分钟',
                team_value:'把选题、脚本、素材和分工合成一张可执行工作单，减少内容团队反复沟通。',
                best_use:'适合晨会选题和活动前准备'
            }},
            work_order_markdown: buildDeliveryWorkOrder(title, angle, profile)
        }};
    }}

    window.fetch = async function(input, init = {{}}){{
        const url = typeof input === 'string' ? input : input.url;
        const parsed = new URL(url, window.location.href);
        if(!parsed.pathname.startsWith('/api/')) return nativeFetch(input, init);

        if(parsed.pathname === '/api/content/opportunities') {{
            const copy = JSON.parse(JSON.stringify(staticData.opportunities));
            if(parsed.searchParams.get('refresh') === '1') {{
                copy.opportunities.push(copy.opportunities.shift());
                copy.hero = copy.opportunities[0];
            }}
            return responseJson(copy);
        }}
        if(parsed.pathname === '/api/content/brief') return responseJson(staticData.brief);
        if(parsed.pathname === '/api/content/calendar') return responseJson(staticData.calendar);
        if(parsed.pathname === '/api/events/planner') return responseJson(staticData.events);
        if(parsed.pathname.startsWith('/api/events/planner/')) {{
            const id = decodeURIComponent(parsed.pathname.split('/').pop());
            return responseJson(staticData.eventDetails[id] || {{error:'event not found'}});
        }}
        if(parsed.pathname === '/api/content/topic') {{
            return responseJson(buildTopic(parsed.searchParams.get('q') || '自定义游戏选题'));
        }}
        if(parsed.pathname === '/api/content/generate') {{
            let item = {{}};
            try {{ item = JSON.parse(init.body || '{{}}'); }} catch(e) {{}}
            return responseJson(buildPack(item));
        }}
        return responseJson({{error:'static endpoint not found'}});
    }};
}})();
</script>
"""


def patch_docx_download(html):
    replacement = """function downloadBriefDocx(){
    const text = state.daily || state.brief?.markdown || '';
    const blob = new Blob([text], {type:'application/msword;charset=utf-8'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `GamePoch_Content_Brief_${new Date().toISOString().slice(0,10)}.doc`;
    a.click();
    URL.revokeObjectURL(a.href);
}"""
    return re.sub(
        r"function downloadBriefDocx\(\)\{\s*window\.open\('/api/content/brief/docx','_blank'\);\s*\}",
        replacement,
        html,
    )


async def main():
    data = await collect_data()
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("<script>\nconst state =", build_static_api_script(data) + "\n<script>\nconst state =", 1)
    html = patch_docx_download(html)
    OUT_DIR.mkdir(exist_ok=True)
    OUT_FILE.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
