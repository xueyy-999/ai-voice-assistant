# Git 推送指南

## 当前Git状态
- ✅ 本地仓库已创建
- ✅ 已有2个提交记录
- ❌ 需要推送到远程仓库

## 推送步骤

### 1. 检查网络连接
```bash
ping github.com
```

### 2. 查看当前状态
```bash
git status
git log --oneline
```

### 3. 推送到GitHub
```bash
# 如果网络正常，执行：
git push -u origin master
```

### 4. 如果推送失败

#### 方案A：使用代理
```bash
# 设置代理（如果有）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 推送
git push -u origin master

# 完成后取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

#### 方案B：使用SSH
```bash
# 生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "xueyy-999@github.com"

# 添加到GitHub（Settings -> SSH Keys）
cat ~/.ssh/id_rsa.pub

# 修改远程地址
git remote set-url origin git@github.com:xueyy-999/ai-voice-assistant.git

# 推送
git push -u origin master
```

#### 方案C：手动上传
1. 在GitHub仓库页面点击 "uploading an existing file"
2. 将整个项目文件夹拖拽上传
3. 填写提交信息

## 后续提交

为了符合评审要求，建议每天都有提交记录：

### Day 1 - 今天的提交
```bash
# 优化前端UI
git add frontend/
git commit -m "style: improve UI design and user experience"
git push

# 添加单元测试
git add tests/
git commit -m "test: add unit tests for core modules"
git push
```

### Day 2 - 性能优化
```bash
git commit -m "perf: optimize audio streaming performance"
git commit -m "feat: add voice command shortcuts"
```

### Day 3 - 功能增强
```bash
git commit -m "feat: add more voice commands"
git commit -m "docs: update user guide"
```

### Day 4 - Bug修复
```bash
git commit -m "fix: resolve audio capture issues"
git commit -m "chore: update dependencies"
```

### Day 5 - 最终准备
```bash
git commit -m "docs: add demo video link"
git commit -m "chore: final cleanup before submission"
```

## 重要提醒

1. **保持提交频率**：每天至少1-2个有意义的提交
2. **提交信息规范**：使用 feat/fix/docs/style/perf/test/chore 前缀
3. **避免大量修改**：将改动分解成多个小提交
4. **记录开发过程**：展示迭代和改进的过程

## 当前仓库信息
- 仓库地址：https://github.com/xueyy-999/ai-voice-assistant
- 主分支：master
- 提交数量：2个

---

**请尽快完成推送，确保评审时能看到完整的开发历史！**
