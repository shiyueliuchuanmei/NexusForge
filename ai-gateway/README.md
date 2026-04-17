# AI Gateway - 统一 AI 模型调用网关

Unified AI Model API Gateway supporting multiple providers.

## Features

- 支持多个 AI 提供商：OpenAI、Anthropic、Azure OpenAI、通义千问、文心一言
- 统一接口：`/v1/chat/completions` 和 `/v1/images/generations`
- Token 用量统计记录到数据库
- 管理员接口：设置用户配额、查询用量

## Project Structure

```
ai-gateway/
├── app/
│   ├── api/              # API 路由
│   │   ├── chat.py       # 聊天补全接口
│   │   ├── images.py    # 图片生成接口
│   │   └── admin.py     # 管理员接口
│   ├── models.py         # 数据库模型
│   ├── schemas.py        # Pydantic schemas
│   ├── providers/        # AI 适配器
│   │   ├── base.py      # 基类
│   │   ├── openai.py    # OpenAI 适配器
│   │   ├── anthropic.py # Anthropic 适配器
│   │   ├── azure.py     # Azure 适配器
│   │   ├── qwen.py      # 通义千问适配器
│   │   └── wenxin.py    # 文心一言适配器
│   ├── services/         # 业务服务
│   │   └── quota.py     # 配额服务
│   ├── config.py        # 配置
│   ├── database.py       # 数据库连接
│   └── main.py          # FastAPI 应用
├── tests/                # 单元测试
├── requirements.txt     # 依赖
└── .env.example         # 环境变量示例
```

## Setup

1. 安装依赖：
```bash
cd ai-gateway
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 填入 API keys
```

3. 初始化数据库：
```bash
python -m app.init_db
```

4. 启动服务：
```bash
uvicorn app.main:app --reload --port 8000
```

## API Usage

### Chat Completions

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk-your-api-key" \
  -H "provider: openai" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Image Generation

```bash
curl -X POST http://localhost:8000/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk-your-api-key" \
  -H "provider: openai" \
  -d '{
    "model": "dall-e-3",
    "prompt": "A cute cat"
  }'
```

### Admin - Set Quota

```bash
curl -X POST http://localhost:8000/admin/quota/set \
  -H "x-admin-key: sk-admin-your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "monthly_token_quota": 5000000
  }'
```

## Database Tables

- `users` - 用户表
- `usage_records` - Token 使用记录
- `quota_records` - 每月配额记录

## Running Tests

```bash
pytest tests/ -v
```
