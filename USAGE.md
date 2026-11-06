# 使用说明

本说明适用于关卡、世界观、城市规划和环境美术协作。你可以让 Agent 从零设计城市、补全已有方案、评审城市逻辑，或仅把现有材料整理成交互文档。

## 安装

仓库地址：<https://github.com/Hammerstein3217/open-world-city-planner>。在 Codex 中，也可以让内置安装器安装本仓库的 Skill：

```text
使用 $skill-installer，安装以下 GitHub 目录中的 Skill：
https://github.com/Hammerstein3217/open-world-city-planner/tree/main/skills/open-world-city-planner
```


安装时复制整个 `skills/open-world-city-planner` 文件夹，不能只复制 `SKILL.md`，因为入口会按相对路径读取模板、数据结构和方法参考。

### Codex 项目内使用

在希望使用 Skill 的项目根目录创建 `.agents/skills`，再将本仓库的 `skills/open-world-city-planner` 复制到其中。目录应为：

```text
你的项目/
  .agents/
    skills/
      open-world-city-planner/
        SKILL.md
        agents/
        assets/
        references/
        scripts/
```

### Codex 个人使用

可将同一文件夹放到 `~/.agents/skills/open-world-city-planner`。技能未显示时重新启动 Codex；使用 `$open-world-city-planner` 显式调用。[安装位置与调用方式依据：OpenAI 官方说明](https://learn.chatgpt.com/docs/build-skills)。

其他支持 Agent Skill 的工具，请按该工具的技能目录规则安装；本仓库不假定各工具共享同一目录。

## 第一次使用时准备什么

不需要把所有设定写完。把现有材料交给 Agent，并指出哪些不能改：

| 输入 | 建议内容 | 缺少时怎样处理 |
|---|---|---|
| 世界观 | 时代、地理、技术、居民、历史、组织与冲突 | 先区分硬设定和可创造内容 |
| 城市图 | 轮廓、拓扑或平面图，比例尺、北向、高程 | 只有轮廓不能推定尺度与步行时间 |
| 游戏目标 | 玩家要做什么，城市最值得记住的体验 | 先确认主题与玩法的优先级 |
| 移动与镜头 | 步行、驾车、跑酷或其他方式；已有参数 | 会改变街宽与骨架的部分先询问 |
| 制作约束 | 目标平台、引擎、内容量、交通与流式边界 | 未知项保留待测，不编造验收结果 |
| 参考资料 | 城市、作品、截图、概念图、论文或分享 | 标注用途、来源与不能照搬的内容 |

如果只是测试范例，可以明确说“允许采用原创假设”。Agent 会记录假设和影响，不必先补完一整套世界观。

## 常用调用

### 1. 设计一座新城市

```text
使用 $open-world-city-planner，设计一座开放世界城市。

已有材料：我附上的世界观大纲与海港轮廓。
必须保留：北侧高地、旧灯塔、两处港口入口。
核心体验：在日常生活中读出城市的历史变化，步行探索为主。
暂未确定：主角速度、可玩面积和平台预算。

先做输入审计；把会改变骨架的未知合并成最多三个关键问题。
确认后推导历史、城区、建筑、POI、阵营与路网。
交付交互规划文档、来源台账和白盒计划，不制作游戏原型。
```

### 2. 创建允许假设的测试范例

```text
使用 $open-world-city-planner，创建一个完整城市规划范例。
允许你为测试自主设定世界观、尺度和玩法前提。
所有新增内容标为原创设定，推断注明前提和可推翻条件。
请交付可独立阅读的交互文档与数据，不把参数目标当成实测。
```

### 3. 补全已有城区或 POI

```text
使用 $open-world-city-planner，补全我提供的 POI 档案。
保留现有城市结构、ID、坐标、时间线、阵营和数据结构。

请具体说明：
- 远处轮廓、接近时看到的体量、入口和重要立面。
- 谁建造、服务谁、经历了哪些改造，为什么建在这里。
- 与道路、高差、水岸、周边建筑和居民活动的关系。
- 玩家如何从两个方向接近、看见、停留和离开。
- 新旧材料、维护与行为痕迹，以及阵营如何控制。
- 可使用的参考作品或参考图、具体看点和不能照搬的内容。

将内容扩写进现有字段，缺少资料时先标注问题。
参考图须区分真实资料、游戏图例与 AI 概念图。
```

### 4. 评审已有城市方案

```text
使用 $open-world-city-planner，评审我附上的规划。
保留已经确认的世界观和城市几何。

重点检查历史因果、区域成因、新旧建筑、生活逻辑、路网权限、
POI 接入和移动连续性。请输出具体问题、证据、最小修改与验证办法。
P0 缺少证据时保持未通过，不用总分覆盖。
```

### 5. 只整理为交互文档

```text
使用 $open-world-city-planner，把现有城市资料整理成交互文档。
保留所有已确认内容，不新增城市历史或修改结构。
地图对象应能关联城区、POI、道路、历史、阵营和资料来源。
缺失字段明确列出；图示和估算不能写成引擎实测。
```

## 工作会怎样推进

1. **输入审计**：已知、未知和冲突分别记录，识别需要先问的问题。
2. **定义目标**：确认主题、玩法、优先级、不可妥协项和可调整项。
3. **研究与骨架**：先地标、自然空间和关键道路，再补普通街区。
4. **演变与区域**：由事件、资源、迁移和地权推导城区、设施与生活。
5. **路网与体验**：分别表达形态和实际路径，考虑模式、权限与绕行。
6. **验证与评审**：列受控实验、玩家视野、困难地形、跨区内容及技术风险。
7. **交付**：城市数据、交互文档、来源和假设、评审与验证计划。

详细规则见 [工作流程](skills/open-world-city-planner/references/workflow.md)。任务较小时按需要使用，不必每次重做完整城市。

## 怎么读潮痕港范例

用浏览器打开 `demo/index.html`：

- **城市图谱**：选择城区、POI 或道路，在右侧阅读对象档案；按年代查看已形成空间和退役道路。
- **演变因果**：选择事件，查看触发、资源、行动、空间后果、遗存与替代方案。
- **权力与秩序**：区分名义地权、实际控制和服务网络；控制图是当前时期快照。
- **建筑与生活**：查看居民经济、功能混合、新旧维护、建筑组合和行为痕迹。
- **道路与交通**：比较步行／骑行、临时封路与联社许可下的合法路径。电车和船渡另列等待模型。
- **白盒验证计划**：比较假设净宽，展开实验、参数和放行门槛。全部游戏实验均待执行。
- **来源与推断**：展开声明、前提和资料定位；可离线阅读开源版方法索引与原创世界观。

文档底部提供城市数据导出、原创世界观阅读和打印。打印保留当前选择，完整内容以 HTML 与 JSON 为准。

## 修改数据并生成文档

以下命令在仓库根目录执行，Python 脚本无需第三方依赖。

先改 `demo/city.json`，不要只改 HTML 中的内嵌副本。若修改原创世界观，同步更新 `demo/worldbuilding.md`、相关声明和引用。

```sh
python3 skills/open-world-city-planner/scripts/validate_city.py demo/city.json
python3 skills/open-world-city-planner/scripts/build_demo.py demo/city.json --out demo/index.html
```

再执行有关检查：

```sh
python3 validation/test_invariants.py
python3 validation/check_package.py
```

有 Node.js 时可补充：

```sh
node validation/test_document_runtime.cjs
```

新建城市时，将新数据和世界观放入单独目录，例如：

```text
my-city/
  city.json
  worldbuilding.md
```

生成时指定数据与输出位置：

```sh
python3 skills/open-world-city-planner/scripts/validate_city.py my-city/city.json
python3 skills/open-world-city-planner/scripts/build_demo.py my-city/city.json --out my-city/index.html
```

模板以潮痕港为案例，采用 1100×800 示意坐标和步行／骑行模式。新项目还需调整案例文案、英文名、轮廓装饰、坐标边界、比例尺与移动参数；生成脚本不会替你重新设计这些内容。[数据契约与适配说明](skills/open-world-city-planner/references/data-contract.md)。

## 如何判断交付是否够用

先检查一个具体空间是否能回答：谁出钱、服务谁、为什么在这里、哪期出现、接哪条路、留下哪些痕迹、玩家如何理解，以及需要怎样验证。

然后检查三类结论是否分开：

| 结论 | 能支持什么 |
|---|---|
| 文档功能和数据检查 | 引用、年代、拓扑、展示和交互逻辑 |
| 公式与几何预算 | 路长、恒速 ETA、净宽等估算 |
| 引擎与玩家实测 | 操控、镜头、识别、连续移动、技术表现与生产放行 |

人口不等于同屏 NPC，设定面积不等于可玩面积；参考图不等于可执行几何。目标参数尚未测试时，保留 `not_run`。具体标准见 [评审规则](skills/open-world-city-planner/references/review-rubric.md) 与 [白盒验证](skills/open-world-city-planner/references/whitebox-validation.md)。

## 文件参考

- [输入审计模板](skills/open-world-city-planner/assets/intake-template.md)
- [事件、城区、建筑、POI、道路、参考与实验模板](skills/open-world-city-planner/assets/design-templates.md)
- [来源分类与信息不足时的处理](skills/open-world-city-planner/references/intake-and-provenance.md)
- [城市 JSON Schema](skills/open-world-city-planner/references/city.schema.json)
- [GDC 方法映射](skills/open-world-city-planner/references/gdc-method-map.md)
- [范例规划评审](demo/planning-review.md)
- [实际验证范围](validation/verification-report.md)
