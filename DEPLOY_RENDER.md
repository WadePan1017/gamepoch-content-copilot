# Render 部署说明

## 目标

把 FastAPI 后端部署成公网 Demo，让对方能实际操作：

- 实时抓取 Steam / 海外资讯
- 输入游戏名生成内容包
- 下载 Word / Markdown 简报
- 使用图片代理避免 Steam CDN 图片加载失败

## 部署步骤

1. 打开 Render，新建 Web Service。
2. 连接 GitHub 仓库：`WadePan1017/gamepoch-content-copilot`。
3. Render 会读取项目根目录的 `render.yaml`。
4. 确认配置：
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
   - Health Check Path: `/api/demo/status`
5. 部署完成后打开服务 URL。

默认预计 URL：

```text
https://gamepoch-content-copilot.onrender.com
```

如果 Render 分配了不同 URL，需要把 `templates/index.html` 里的 `RENDER_DEMO_URL` 改成实际地址，然后重新运行：

```powershell
python scripts\export_static_pages.py
```

再提交并推送 GitHub Pages 仓库。

## 部署后检查

访问：

```text
/api/demo/status
/api/content/opportunities?refresh=1
```

页面里重点测试：

- 点击“刷新”后热点是否更新
- 输入任意游戏名能否生成内容包
- 点击热点卡片能否跳到内容生成
- 图片是否正常显示，失败时是否显示 GamePoch fallback 图
- Word / Markdown 是否能下载

## 注意

Render 免费 Web Service 会冷启动。给面试官发送前，先自己打开一次实时 Demo，让服务进入热状态。

不要把长期历史数据写在 Render 免费层本地文件里。免费层文件系统不适合持久存储；后续如果做“昨日 / 7日 / 30日趋势”，建议用 GitHub Actions 写入仓库 JSON，或接 Supabase / Neon / Render Postgres。
