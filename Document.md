### **智能知识库助手项目文档**

**版本**：1.0

**日期**：2025年09月09日

**更新日期**：2025年10月09日

------

### **一、项目概述**

构建一个基于知识库的智能助手系统，支持文件上传、内容解析、权限管理与用户交互功能，适用于企业级知识管理和智能问答场景。

**核心功能**：

1. 用户系统（注册/登录/权限管理）
2. 知识内容管理（文件解析、内容存储）
3. 智能问答（基于语义搜索的聊天式交互）
4. 文件管理（上传、存储、关联）

**技术栈**：

- **编程语言**：Python 3.8+
- **Web框架**：FastAPI（支持异步、自动文档生成）
- **数据库**：PostgreSQL（生产级关系型数据库）
- **ORM**：SQLAlchemy（支持异步会话管理）
- **向量数据库**：Qdrant（高性能向量搜索引擎）
- **对象存储**：MinIO（自托管OSS）
- **辅助工具**：
  - 文件解析：mammoth（Word）、pandas（Excel）
  - 语义搜索：chonkie（文本分块）、sentence-transformers（生成文本嵌入向量）
  - 身份认证：JWT令牌认证

------

### **二、功能需求详述**

#### **1. 用户系统**

- **注册/登录**：
  - 用户名/邮箱注册
  - JWT令牌认证（FastAPI内置OAuth2PasswordBearer）
  - 密码加密存储（passlib）

- **权限控制**：
  - 角色区分：普通用户、管理员等
  - 权限管理：基于角色的访问控制（RBAC）
  - 操作鉴权：用户仅能编辑/删除自己的内容

#### **2. 知识内容管理**

- **文件解析**：
  - 支持Word（.docx）和Excel（.xlsx/.xls）文件上传
  - 提取文本并清洗转换为Markdown格式
  - 支持Word文档中的图片上传至MinIO并替换为URL引用

- **内容存储**：
  - 关联用户ID、来源类型（文件）、原始文件路径、清洗后的文本
  - 使用Qdrant向量数据库存储嵌入向量，支持高效相似度查询

#### **3. 智能问答模块**

- **嵌入向量生成**：
  - 使用嵌入模型将文本转换为向量

- **语义搜索**：
  - 用户输入问题 → 生成问题向量 → 在Qdrant中进行相似度搜索 → 返回最匹配的段落

- **对话历史**：
  - 存储用户对话记录（问题、回答、时间戳），支持按会话ID追溯

#### **4. 文件管理**

- **文件上传**：
  - 前端通过表单上传 → 后端校验文件类型/大小 → 存储到MinIO对象存储

- **元数据记录**：
  - 数据库存储文件名、MinIO路径、关联的知识条目ID

------

### **三、系统架构设计**

#### **1. 分层架构**

```
app/  
├── api/              # API路由层（FastAPI路由端点）  
├── services/         # 业务逻辑（内容处理、语义搜索、文件处理）  
├── models/           # SQLAlchemy数据模型（用户、知识条目、文件）  
├── schemas/          # Pydantic模型（请求/响应数据结构）  
├── dependencies/     # 依赖注入（数据库会话、认证校验）  
├── core/             # 核心组件（数据库、处理器、嵌入模型等）
└── utils/            # 工具类（安全、文件存储等）
```

#### **2. 数据库模型**

- **用户表**（`users`）：
  ```
  id (PK), username, email, hashed_password, is_active, role_id, created_at, updated_at
  ```

- **角色表**（`roles`）：
  ```
  id (PK), name, created_at
  ```

- **权限表**（`permissions`）：
  ```
  id (PK), name, description, created_at
  ```

- **角色权限关联表**（`role_permission`）：
  ```
  id (PK), role_id (FK), permission_id (FK)
  ```

- **知识条目表**（`knowledge_items`）：
  ```
  id (PK), user_id (FK), content_type (enum: "url"/"file"), source (文件路径), cleaned_text, created_at
  ```

- **文件表**（`files`）：
  ```
  id (PK), user_id (FK), minio_path, filename, size, uploaded_at
  ```

- **对话记录表**（`chat_histories`）：
  ```
  id (PK), user_id (FK), session_id, question, answer, timestamp
  ```

> **说明**：使用Qdrant向量数据库存储嵌入向量，支持高效相似度查询。

#### **3. 核心组件**

- **文档处理器**：
  - WordProcessor：处理Word文档（.docx）
  - ExcelProcessor：处理Excel文档（.xlsx/.xls）

- **文档分块器**：
  - DocumentChunker：将文档内容分块处理，便于向量化和检索

- **嵌入模型**：
  - EmbeddingModel：生成文本向量表示

- **Qdrant数据库**：
  - 存储文档向量，支持相似度搜索

------

### **四、API设计（核心端点示例）**

#### **1. 用户系统**

- `POST /register`：用户注册
- `POST /login`：用户登录，返回JWT令牌
- `GET /users/me`：获取当前用户信息
- `GET /users/{user_id}`：获取指定用户信息（需要权限）

#### **2. 角色与权限**

- `POST /roles`：创建角色（需要管理员权限）
- `GET /roles`：获取角色列表
- `POST /permissions`：创建权限（需要管理员权限）
- `GET /permissions`：获取权限列表

#### **3. 文件管理**

- `POST /files/upload`：上传文件到MinIO并保存元数据
- `GET /files/{file_id}`：获取文件信息

#### **4. 智能问答**

- `POST /chat/completions`：基于知识库的智能问答

------

### **五、开发计划**

#### **阶段1：基础框架搭建（已完成）**

- 初始化FastAPI项目，配置SQLAlchemy + PostgreSQL连接池
- 实现用户注册/登录（JWT认证）
- 部署MinIO和Qdrant服务

#### **阶段2：核心功能开发（已完成）**

- 集成文件处理功能（Word、Excel）
- 集成Qdrant向量数据库和嵌入模型
- 实现基于语义搜索的问答功能

#### **阶段3：测试与优化（进行中）**

- 完善API测试
- 优化语义搜索性能
- 生产环境部署优化

------

### **六、扩展方向**

1. **URL内容抓取**：支持网页内容抓取和处理
2. **标签系统**：为知识条目添加多标签分类，支持按标签过滤
3. **分享功能**：生成知识条目的公开分享链接（基于UUID）
4. **实时通知**：通过WebSocket推送处理进度（如文件解析完成）

------

**备注**：
- 生产环境建议启用HTTPS，并通过环境变量管理敏感信息（API密钥、数据库密码）
- 系统支持Docker部署（需配置docker-compose.yml）
