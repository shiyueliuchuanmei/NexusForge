# AI Gateway

Unified AI Model API Gateway - 统一 AI 模型调用网关

## 技术栈

- **Backend**: Python FastAPI + SQLAlchemy + PostgreSQL
- **AI Providers**: OpenAI, Anthropic, Azure OpenAI, 通义千问, 文心一言

## 项目结构

```
ai-gateway/
├── app/
│   ├── api/              # API 路由
│   │   ├── chat.py       # /v1/chat/completions
│   │   ├── images.py     # /v1/images/generations
│   │   └── admin.py      # 管理员接口
│   ├── providers/        # AI 适配器
│   │   ├── base.py       # BaseAdapter 基类
│   │   ├── openai.py     # OpenAI (GPT-4, DALL-E)
│   │   ├── anthropic.py  # Anthropic (Claude)
│   │   ├── azure.py      # Azure OpenAI
│   │   ├── qwen.py      # 通义千问
│   │   └── wenxin.py    # 文心一言
│   ├── services/         # 业务服务
│   │   └── quota.py     # 配额服务
│   ├── models.py         # 数据库模型
│   ├── schemas.py        # Pydantic schemas
│   ├── config.py        # 配置管理
│   ├── database.py       # 数据库连接
│   └── main.py          # FastAPI 入口
├── tests/                # 单元测试
├── start.bat            # 启动脚本
└── requirements.txt    # 依赖
```

## 快速启动

```bash
cd ai-gateway
pip install -r requirements.txt
python -m app.init_db  # 初始化数据库
uvicorn app.main:app --reload --port 8000
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/v1/chat/completions` | 统一聊天补全 |
| POST | `/v1/images/generations` | 统一图片生成 |
| POST | `/admin/quota/set` | 设置用户配额 |
| GET | `/admin/quota/{user_id}` | 查询用户配额 |
| GET | `/admin/usage/records` | 查询用量记录 |
| GET | `/admin/users` | 列出所有用户 |

## 认证

- **用户 API**: 通过 `x-api-key` header 传递用户 API key
- **管理员 API**: 通过 `x-admin-key` header 传递管理员 API key

## 开发指南

### 添加新的 AI Provider

1. 在 `app/providers/` 创建新适配器类，继承 `BaseAdapter`
2. 实现 `generate_text()` 和 `generate_image()` 方法
3. 在 `app/providers/__init__.py` 中注册

### 运行测试

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

## 数据库

使用 PostgreSQL，连接信息在 `.env` 中配置。
