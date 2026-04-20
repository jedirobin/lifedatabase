# 🍪 Cookie 配置详细指南

> 配置Cookie后可以获取真实数据，否则为演示数据

---

## 📋 准备工作

### 1. 复制环境变量文件
```bash
cd scraper
copy .env.example .env
```

### 2. 推荐使用浏览器
- ✅ **Chrome / Edge**（操作方法完全相同）
- ❌ 不推荐Firefox（Cookie格式有差异）

---

## 🔴 小红书 Cookie 配置（最重要！）

### 步骤 1 - 打开开发者工具
1. 打开 **Chrome/Edge**，访问：https://www.xiaohongshu.com
2. **登录你的账号**（一定要登录！）
3. 按 **F12** 打开开发者工具
4. 点击 **「应用程序」** 标签页（Application）

### 步骤 2 - 获取Cookie
5. 左侧展开 **「Cookie」** → 点击 `https://www.xiaohongshu.com`
6. 找到这三个关键值：
   | Cookie名 | 必须 | 说明 |
   |---------|------|------|
   | `a1` | ✅ 必须 | 最重要 |
   | `webId` | ✅ 必须 | |
   | `web_session` | ✅ 必须 | |

7. **完整复制所有Cookie**：
   - 切换到「网络」标签页 → 按F5刷新
   - 点击第一个请求 → 「请求标头」→ 找到 `Cookie:`
   - 复制冒号后面的**全部内容**

### 步骤 3 - 填入.env
```env
XIAOHONGSHU_COOKIE=a1=xxxxxx; webId=xxxxxx; web_session=xxxxxx;
```

---

## 🟠 抖音 Cookie 配置

### 步骤 1 - 获取Cookie
1. 访问：https://www.douyin.com
2. **登录账号**
3. F12 → 「应用程序」→ Cookie
4. 关键Cookie：`sessionid`, `msToken`, `odin_tt`

### 步骤 2 - 填入.env
```env
DOUYIN_COOKIE=sessionid=xxxxxx; msToken=xxxxxx; odin_tt=xxxxxx;
```

---

## 🟢 B站 Cookie 配置（可选）

B站不配置也可以爬热门，配置后可以获取更高权限数据：

1. 访问：https://www.bilibili.com
2. F12 → 应用程序 → Cookie
3. 关键Cookie：`SESSDATA`, `bili_jct`
4. 填入：
```env
BILIBILI_COOKIE=SESSDATA=xxxxxx; bili_jct=xxxxxx;
```

---

## ✅ 验证配置是否生效

运行爬虫测试：
```bash
python main.py -p xiaohongshu -l 10
```

**验证输出：**
- ❌ 如出现「演示数据」= Cookie未配置/失效
- ✅ 如获取真实标题 = 配置成功

---

## ⚠️ 常见问题

### Q1: Cookie过期了怎么办？
A: 重新登录小红书/抖音，按上述步骤重新复制即可。Cookie一般有效期7-30天。

### Q2: 要不要担心账号安全？
A: Cookie只保存在你本地`.env`文件中，**不会上传**。`.env`已在`.gitignore`中。

### Q3: 获取多少数据会被封？
A: 默认配置2秒请求间隔，完全模拟人操作，非常安全。

### Q4: 为什么还是演示数据？
A: 检查这三点：
   1. 文件名是不是 `.env`（不是 .env.example！）
   2. Cookie前后有没有空格
   3. 有没有重新登录导致Cookie失效

---

## 📝 最终检查清单

- [ ] 复制 `.env.example` → `.env`
- [ ] Chrome/Firefox登录小红书
- [ ] F12获取完整Cookie字符串
- [ ] 粘贴到 `XIAOHONGSHU_COOKIE=` 后面
- [ ] 运行 `python main.py -p xiaohongshu` 测试

---

🎉 配置完成！现在可以获取真实的爆款数据了！
