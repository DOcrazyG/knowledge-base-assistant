### **智能知识库助手需求文档**

**版本**：1.0

**日期**：2025年09月09日

------

### **一、项目概述**

构建一个支持多源知识导入（URL/文件）的智能知识库系统，用户可通过自然语言查询快速定位知识内容。

**核心功能**：

1. 1.

   用户系统（注册/登录/权限管理）

2. 2.

   知识内容管理（URL抓取、文件解析、内容存储）

3. 3.

   智能问答（基于语义搜索的聊天式交互）

4. 4.

   文件管理（上传、存储、关联）

**技术栈**：

- •

  **编程语言**：Python 3.10+

- •

  **Web框架**：FastAPI（支持异步、自动文档生成）

  

- •

  **数据库**：PostgreSQL（生产级关系型数据库）

  

- •

  **ORM**：SQLAlchemy（支持异步会话管理）

  

- •

  **辅助工具**：

  - •

    文件解析：PyPDF2（PDF）、python-docx（Word）

    

  - •

    语义搜索：SentenceTransformers（生成文本嵌入向量）

  - •

    对象存储：MinIO（自托管OSS，Docker部署）

    

------

### **二、功能需求详述**

#### **1. 用户系统**

- •

  **注册/登录**：

  - •

    邮箱验证码注册（SMTP服务发送验证码）

    

  - •

    JWT令牌认证（FastAPI内置OAuth2PasswordBearer）

    

- •

  **权限控制**：

  - •

    角色区分：普通用户（管理个人知识库）、管理员（管理所有内容）

  - •

    操作鉴权：用户仅能编辑/删除自己的内容

#### **2. 知识内容管理**

- •

  **URL内容抓取**：

  - •

    输入URL → 后端通过HTTPX异步抓取网页 → BeautifulSoup清洗HTML → 提取文本存储

- •

  **文件解析**：

  - •

    支持PDF/Word/TXT文件上传 → 提取文本并清洗（移除换行符、冗余空格）

    

- •

  **内容存储**：

  - •

    关联用户ID、来源类型（URL/文件）、原始链接/文件路径、清洗后的文本

#### **3. 智能问答模块**

- •

  **嵌入向量生成**：

  - •

    使用`sentence-transformers`模型将文本转换为向量（如`all-MiniLM-L6-v2`）

- •

  **语义搜索**：

  - •

    用户输入问题 → 生成问题向量 → 计算与知识库内容的余弦相似度 → 返回最匹配的段落

- •

  **对话历史**：

  - •

    存储用户对话记录（问题、回答、时间戳），支持按会话ID追溯

    

#### **4. 文件管理**

- •

  **文件上传**：

  - •

    前端通过表单上传 → 后端校验文件类型/大小 → 存储到MinIO对象存储

    

- •

  **元数据记录**：

  - •

    数据库存储文件名、MinIO路径、关联的知识条目ID

    

------

### **三、系统架构设计**

#### **1. 分层架构**

```
app/  
├── api/              # API路由层（FastAPI路由端点）  
├── services/         # 业务逻辑（内容抓取、语义搜索、文件处理）  
├── models/           # SQLAlchemy数据模型（用户、知识条目、文件）  
├── schemas/          # Pydantic模型（请求/响应数据结构）  
├── dependencies/     # 依赖注入（数据库会话、认证校验）  
└── utils/            # 工具类（邮件发送、文本清洗、向量计算）
```

#### **2. 数据库模型**

- •

  **用户表**（`users`）：

  ```
  id (PK), username, email, hashed_password, is_active, role, created_at
  ```

- •

  **知识条目表**（`knowledge_items`）：

  ```
  id (PK), user_id (FK), content_type (enum: "url"/"file"), source (URL或文件路径), cleaned_text, embedding_vector (pgvector扩展), created_at
  ```

- •

  **文件表**（`files`）：

  ```
  id (PK), knowledge_item_id (FK), minio_path, filename, size, uploaded_at
  ```

- •

  **对话记录表**（`chat_histories`）：

  ```
  id (PK), user_id (FK), session_id, question, answer, timestamp
  ```

> **说明**：使用PostgreSQL的`pgvector`扩展存储嵌入向量，支持高效相似度查询。

------

### **四、API设计（核心端点示例）**

#### **1. 用户系统**

- •

  `POST /register`：发送邮箱验证码 → 验证后创建用户

  

- •

  `POST /login`：返回JWT令牌

  

#### **2. 知识管理**

- •

  `POST /knowledge/url`：提交URL → 返回存储的知识ID

- •

  `POST /knowledge/file`：上传文件 → 返回文件ID及关联知识ID

  

#### **3. 智能问答**

- •

  `POST /chat`：

  ```
  // 请求
  {"knowledge_id": 123, "question": "该文档的核心观点是什么？"}
  
  // 响应
  {"answer": "文档强调可持续能源的重要性...", "source": "knowledge_item_123"}
  ```

------

### **五、开发计划**

#### **阶段1：基础框架搭建（1周）**

- •

  初始化FastAPI项目，配置SQLAlchemy + PostgreSQL连接池

  

- •

  实现用户注册/登录（JWT认证）

  

- •

  部署MinIO服务（Docker Compose）

  

#### **阶段2：核心功能开发（2周）**

- •

  完成URL抓取与文本清洗逻辑

- •

  集成SentenceTransformers生成文本向量

- •

  实现文件上传接口（FastAPI的`UploadFile`）

  

#### **阶段3：测试与优化（1周）**

- •

  使用Pytest覆盖API端点测试

  

- •

  优化语义搜索性能（异步批处理向量计算）

- •

  生产环境部署：Nginx + Gunicorn + Uvicorn

  

------

### **六、扩展方向**

1. 1.

   **实时通知**：通过WebSocket推送处理进度（如文件解析完成）

   

2. 2.

   **标签系统**：为知识条目添加多标签分类，支持按标签过滤

   

3. 3.

   **分享功能**：生成知识条目的公开分享链接（基于UUID）

   

------

**备注**：

- •

  完整代码模板参考：FastAPI分层架构示例

  

- •

  生产环境建议启用HTTPS，并通过环境变量管理敏感信息（API密钥、数据库密码）