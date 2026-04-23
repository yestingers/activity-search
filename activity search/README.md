# Activity Search 系统

## 概述

这是一个专为无人机领域专业人士设计的活动追踪系统，使用OpenClaw框架实现定时搜索和报告功能。系统通过cron作业定期执行，利用多个技能模块完成搜索、处理和报告生成任务。

## 系统架构

整个系统由以下组件构成：

### 1. Cron 作业 (`cron-jobs/drone-activity-tracker.json`)
- 每日中午12:00自动执行
- 调用各个技能模块完成任务
- 最终通过WeChat发送报告

### 2. 技能模块

#### 搜索引擎技能 (`skills/search-engine/*`)
- **功能**: 执行通用搜索和定向抓取
- **通用搜索**: 使用SearxNG在Bing、百度、搜狗、360搜索上进行广泛搜索，结果存储到搜索结果库1
- **定向抓取**: 从专业站点列表获取特定内容，结果存储到搜索结果库2

#### 结果处理器技能 (`skills/result-processor/*`)
- **功能**: 过滤、去重和价值评估
- **过滤**: 去除无效或低质量结果
- **去重**: 消除重复条目
- **价值评估**: 根据用户专业背景评估结果价值
- **排序**: 按价值排名生成报告准备结果

#### 报告生成器技能 (`skills/report-generator/*`)
- **功能**: 格式化报告并发送
- **丰富详情**: 为选定结果补充更多信息
- **格式化**: 应用美观易读的模板
- **验证**: 确保报告质量
- **发送**: 通过WeChat渠道发送报告
- **归档**: 存储历史报告

## 数据库结构

系统使用SQLite数据库存储各个阶段的结果：

- `search_results.db`: 存储原始搜索结果
  - `universal_search_results`: 通用搜索结果（来自SearxNG）
  - `targeted_fetch_results`: 定向抓取结果
  
- `report_ready_results.db`: 存储处理后的报告准备结果
  - `report_ready_results`: 评估和排序后的结果

- `historical_reports.db`: 存储历史报告
  - `historical_reports`: 历史报告存档

## 配置要求

### SearxNG 设置
- 必须在 `http://localhost:8080` 运行
- 配置支持以下搜索引擎: Bing, Baidu, Sogou, 360search

### 微信集成
- 系统配置为通过 `openclaw-weixin` 渠道发送报告
- 目标用户: `3bd6edc5c6f1-im-bot`

## 使用方法

### 手动执行
```bash
python run_activity_search.py
```

### 系统自动执行
系统将根据cron配置每日自动执行。

## 技能调用流程

1. **第一步**: 通用搜索
   - 调用 `search-engine` 技能的 `universal_search` 方法
   - 在多个搜索引擎上进行广泛搜索
   - 结果存储到搜索结果库1

2. **第二步**: 定向抓取
   - 调用 `search-engine` 技能的 `targeted_fetch` 方法
   - 从专业站点列表抓取内容
   - 结果存储到搜索结果库2

3. **第三步**: 结果处理
   - 调用 `result-processor` 技能的 `compile_report_ready_results` 方法
   - 提取两个搜索结果库的内容
   - 去除重复无效结果
   - 对剩余结果进行价值评估
   - 挑选出最有用的结果存入结果汇报库

4. **第四步**: 报告生成与发送
   - 调用 `report-generator` 技能的 `generate_and_deliver_report` 方法
   - 对结果汇报库中的结果按模板处理
   - 格式化为美观易读的报告
   - 通过WeChat发送并存档

## 报告格式

系统生成专业级活动报告，包含：
- 按类别分组的活动信息
- 价值评分和优先级
- 活动详情（时间、地点、组织方等）
- 个性化建议和行动计划
- 数据统计概览

## 维护

- 定期检查SearxNG服务可用性
- 监控cron作业执行日志
- 更新专业站点列表以保持内容质量