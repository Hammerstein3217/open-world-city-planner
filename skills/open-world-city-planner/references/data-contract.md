# 数据契约与复用约定

`city.schema.json` 使用 JSON Schema 2020-12。随包脚本只执行该 schema 实际用到的约束（$ref、type、const、enum、required、properties、additionalProperties、items、长度、范围、uniqueItems、pattern），无需安装依赖；不是通用 JSON Schema 引擎。

## 对象关系

```
sources ← claims（来源、推断前提、原创声明）
claims ← events（时代、条件、决策、空间后果）
events ← districts / buildings / pois / roads
factions → districts（当前主导控制，非排他地权）
pois → nodes ← roads（模式、年代、权限、几何）
transit → nodes / roads（单独的公共交通估算）
experiments → targets / observations（目标和实测分开）
review → gates（不能由均分覆盖的P0状态）
```

- `schemaVersion` 固定1.0.0。`version` 是内容版本；修改后旧测量需要重新判定有效性。
- 每类对象有稳定ID，并要求全局唯一。引用字段使用ID；文案、名字和数组顺序不承担引用。
- `eras.index` 从0连续，年份严格增加；`since` 为起始下标（含），`retired` 为退出下标（不含），null表示持续至今。
- 道路的两个端点必须已形成，长度必须等于折线长度乘米制比例。道路交叉不自动视为连通，必须共享节点；桥、层间连接要另做引擎验证。
- 节点与POI分开：旧雨院路口可早于273年诊所存在。POI的成立不是后来所有功能变化的发生时间，历史模式档案为当前回顾快照。
- `event.dependsOn` 为更早事件；事件和声明前提均不可形成循环。`inference` 有前提和解释，`measurement` 额外要有 `measurementEvidence` 原始证据定位。
- `observations` 为空的实验不能标 `passed`；所有本例实验均 `not_run`。用户接受风险也需在证据中记录实际负责人、后果、日期与回退。
- 面积分设定与可玩。人口按设定面积算密度；可玩面积由各区多边形×比例尺²得出。脚本没有做多边形布尔并集，因此更换几何时需人工确认各区不重叠。
- `claimIds` 可以指当前回顾；对象成立后的改造用 `eventIds` 描述。不能因对象存在得早，就把后续灾害或重建提前。

## 示例地图与生成器

模板为潮痕港的完整交互文档起点，采用1100×800坐标、1单位=2m、五期历史、第三人称步行／骑行的案例表达。构建脚本负责安全内嵌数据和原文，不会自动重新设计地图、翻译主视觉文案、设定移动机制或生成引擎。

换城市时先改城市数据、世界观和声明，再调整 `assets/atlas-template.html` 的案例标题、英文名、轮廓装饰、纪年说明、地图边界和实验参数。若改为摆荡／驾车，必须改schema模式、权限、寻路成本和实验计划，不能沿用本例步行／骑行速度。变化涉及坐标尺寸时同步改viewBox、缩放／拖动比例、背景轮廓和方向标。

## 验证覆盖与边界

`validate_city.py` 检字段、ID、引用、时间依赖、声明前提、坐标与POI归属、路长、人口密度与面积、各期步行连通、路口度数预算、实验和生产状态。它不能自动判断历史是否有说服力、道路转弯是否可驾驶、混合功能是否有趣或地标在镜头里是否可见。

`validation/test_invariants.py` 包含正例和故障注入：断引用、未来因果、推断循环、早生道路、错误长度、脱离城区的POI、伪实测、假通过和假生产放行，并覆盖绕路与模式限制。

`validation/test_document_runtime.cjs` 在最小DOM测试环境中执行文档脚本，检查初始化、选择、年代、来源、搜索、参数、导出及路由。它不等于真实浏览器渲染或视觉验收；报告必须保留此局限。
