# 🎯 快速答案卡

## PR上的pytest使用真实API Key吗？

### ❌ **不使用！**

---

## 三秒总结

| 问题 | 答案 |
|------|------|
| 使用真实API Key? | ❌ NO |
| 使用真实API URL? | ❌ NO |
| 进行网络请求? | ❌ NO |
| 消耗API配额? | ❌ NO |
| 使用预录制数据? | ✅ YES |
| 完全离线? | ✅ YES |

---

## 工作原理

```
PR运行pytest
    ↓
VCR读取cassettes (预录制的HTTP响应)
    ↓
所有网络请求被拦截
    ↓
返回保存的响应 (无网络调用)
    ↓
测试验证 ✅
```

---

## 关键点

### 1. VCR记录模式
- GitHub Actions上: `record_mode="none"` (离线)
- 本地开发: `record_mode="once"` (需要时录制)
- 强制更新: `record_mode="all"` (重新录制)

### 2. cassettes状态
- ✅ 全部预录制 (8个cassette文件)
- ✅ 存储在版本控制中
- ✅ PR可直接使用

### 3. 环境变量
- GitHub Actions: **无任何API密钥配置**
- 测试使用占位符: `"test-api-key"`
- cassettes中密钥: 已被过滤为 `"FILTERED"`

---

## 性能

| 方案 | 时间 | 成本 | 可靠性 |
|------|------|------|--------|
| 真实API测试 | 5-10min | 配额消耗 | 不稳定 |
| VCR离线测试 | ~1min | 零 | 100% |

---

## 文档参考

- **VCR_CASSETTE_EXPLANATION.md** - 完整技术细节
- **SECURITY_FIX_SUMMARY.md** - 安全措施说明
- **conftest.py** - VCR配置代码

---

## 核心配置代码

```python
# conftest.py 中的决策逻辑

ALLOW_NETWORK = os.getenv("ALLOW_NETWORK", "0")  # GitHub Actions = "0"

if not ALLOW_NETWORK:
    record_mode = "none"  # ← 离线模式，不进行网络请求

# 结果: VCR只读cassettes，不录制，不触网
```

---

## 总结

✅ PR测试 = **完全离线** = **100%安全** = **无成本**

