# Open World City Planner

**MIT 开源的开放世界城市规划 Agent Skill**：从世界观、城市轮廓、拓扑或平面图出发，设计城市历史、城区、建筑、POI、阵营和交通，并以可交互文档呈现。

这套 Skill 把城市规划组织成一条可追溯的链：

**背景约束 → 行动者与资源 → 历史事件 → 人口与产业迁移 → 城区、建筑和路网 → 玩家可见痕迹 → 验证计划**。

[使用说明](USAGE.md) · [Skill 入口](skills/open-world-city-planner/SKILL.md) · [MIT 许可证](LICENSE)

## 从这里开始

| 你想做什么 | 入口 |
|---|---|
| 安装、调用或了解完整用法 | [使用说明](USAGE.md) |
| 阅读 Agent 的执行规则 | [SKILL.md](skills/open-world-city-planner/SKILL.md) |
| 查看完整交互范例 | 下载仓库后，用浏览器打开 [demo/index.html](demo/index.html) |
| 查看城市原始数据 | [city.json](demo/city.json) |
| 查看评审与验证边界 | [规划评审](demo/planning-review.md) · [验证报告](validation/verification-report.md) |

## 能做什么

- 推导城市为何在此出现、如何增长、为何衰退或更新，并把历史落实到空间变化。
- 规划城区的功能混合、居民经济与活动、建筑新旧、审美语法、设施和 POI。
- 说明阵营的名义归属、显性控制、暗面秩序及其可见线索。
- 设计新旧路网、区域连接、公共交通、建筑入口及不同移动模式的权限和绕行。
- 区分用户给定、附件概括、一手资料、设计推断、原创设定与实际测量。
- 在关键信息不足时先询问，并给出街宽、镜头、困难地形、连续移动与跨区白盒的验证计划。

输出以**可交互规划文档**为主。Skill 不要求制作游戏或可玩的移动原型；文档中的地图、净宽和路线时间属于规划表达与估算。

## 快速调用

将 [skills/open-world-city-planner](skills/open-world-city-planner) 整个文件夹放入你的 Agent 技能目录，保留内部结构。Codex 的项目内安装方法和个人安装方法见 [使用说明](USAGE.md#安装)。

在新任务中使用：

```text
使用 $open-world-city-planner。

根据我提供的世界观和城市轮廓，设计城市演变、城区、建筑、POI、阵营和路网。
先审计已知信息；会影响骨架、尺度和最高目标的缺口，请合并成一轮关键问题。
区分资料、推断和原创设定，并把空间决策关联到历史原因。
交付可交互规划文档和白盒验证计划，不制作游戏原型。
```

已有城市评审、补充 POI、参考资料使用和修改范例的具体提示词见 [USAGE.md](USAGE.md)。

## 范例：潮痕港

原创海港城市，包含：

- 6 个城区、12 个 POI、12 类建筑设施、3 个阵营。
- 5 个历史时期、18 条历史道路，其中现在有 16 条有效道路。
- 电车与接驳船的服务逻辑、峰谷和等待模型。
- 地图对象选择、年代切换、路径条件比较、来源展开和数据导出。

`demo/index.html` 内嵌地图、数据、样式、脚本、GDC 方法索引及原创世界观，可单独转交和离线阅读。外部参考资料链接需要联网。它是一份示范规划，不是用户既有城市设定，也不是已完成引擎验收的关卡。

## 目录

```text
README.md                         项目介绍与快速入口
USAGE.md                          安装、提示词与工作流
skills/open-world-city-planner/
  SKILL.md                        Skill 入口
  agents/openai.yaml              展示信息与调用提示
  assets/                         输入审计、设计卡与 H5 模板
  references/                     工作流、来源规则、Schema、评审及白盒计划
  scripts/                        文档构建与数据验证

demo/                             交互范例、城市数据与原创世界观
validation/                       回归测试、逻辑检查与验证记录
```

## 修改范例与检查

阅读 HTML 不需要安装依赖。修改数据和重建文档需要 Python 3.8+；文档逻辑回归另外需要 Node.js。

在仓库根目录运行：

```sh
python3 skills/open-world-city-planner/scripts/validate_city.py demo/city.json
python3 skills/open-world-city-planner/scripts/build_demo.py demo/city.json --out demo/index.html
python3 validation/test_invariants.py
python3 validation/check_package.py
```

有 Node.js 时可运行：

```sh
node validation/test_document_runtime.cjs
```

构建器负责安全地内嵌数据和原文；新城市的轮廓、案例文案和移动机制仍需按项目调整，详见 [数据契约](skills/open-world-city-planner/references/data-contract.md)。

## 方法来源与验证状态

设计研究参考用户提供的双场 GDC 二次总结；开源版不分发原附件全文，仅提供独立编写的方法索引和公开来源入口。方法涉及 Miriam Bellard 的环境视觉叙事与 Josue Benavidez 的城市关卡流程。保留“演讲内容概括／城市项目归纳”的区别，不将附件整理或本项目参数写成讲者原话。[方法映射与原始资料入口](skills/open-world-city-planner/references/gdc-method-map.md)。

目前 17 项数据回归和 32 项离线文档逻辑检查通过。真实浏览器视觉、窄屏、辅助技术及打印布局未完成实机验收；三维移动、玩家理解、交通 AI、流式与平台性能均待目标引擎实测。完整范围见 [验证报告](validation/verification-report.md)。

## 开源许可

原创 Skill、脚本、模板和潮痕港示例采用 [MIT License](LICENSE)，可使用、修改和分发，保留许可证及版权声明。用户原附件不随仓库或 HTML 分发；外部参考作品不由本仓库重新授权，具体范围见 [第三方资料说明](THIRD_PARTY_NOTICES.md)。
