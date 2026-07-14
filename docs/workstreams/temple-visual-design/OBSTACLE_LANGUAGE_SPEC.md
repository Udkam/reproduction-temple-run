# Obstacle language specification

此规范只解释已经存在的 `beam`、`ring`、`column`、`gap` 规则；不得由美术增加伤害、减速、跨越或收集规则。距离用以 9 / 14 / 19 m/s 三档速度折算，生产中仍由 generator 的公平反应距离决定。

| Kind / 真实规则 | 远（≥ 2.3s） | 中（1.1–2.3s） | 近（≤ 1.1s） | 可读/碰撞 bounds | 成功与失败 |
| --- | --- | --- | --- | --- | --- |
| **beam**：同 lane，必须 jump | 两根珊瑚端帽之间是一根低、横向的沙棕横梁；轮廓宽 > 高 | 端帽加粗、梁下留出明确空气带 | 梁高达 runner 小腿，底边清晰 | 碰撞高度以现有 jump threshold；视觉 top/bottom 外扩 ≤ 6%，横向 lane bounds 不外扩 | 跳过时脚下落点后留一小段沙尘；未跳为既有 recoverable stumble / shield-broken |
| **ring**：同 lane，必须 slide | 一个下垂、偏扁的双支点门，中心负空间可见 | 上拱变厚，底缘离地有可读净空 | ring 覆盖胸/头部高度，左右支点不与 beam 相似 | 使用现有 slide posture/31 tick；绘制内孔不得小于 canonical safe opening | slide 通过时衣尾贴低；未滑为既有 stumble，不伪造穿透 |
| **column**：同 lane，不可 jump/slide，需换 lane | 不对称的破裂潮蚀柱，顶部向一侧折 | 一面沙白、一面深蓝阴影形成偏心剪影 | 占满单 lane，底部有接地碎屑 | 视觉 y 延至地面，x 不得遮邻 lane；碰撞只为该 lane 的既有 volume | lane shift 后碎屑从边缘掠过；撞上为 stumble / shield-break |
| **gap**：必须 airborne，立即失败 | 路缘潮痕线断开，远岸是一条沙白水平唇 | 近岸珊瑚切口与远岸同时可见 | 路面负空间露出深海，far lip 宽 ≥ 屏幕 route 宽 74% | gap 长度/airborne threshold 完全复用规则；视觉深度不缩短实际 gap | 跳过时落到远唇后 1 个 contact；未过是既有 `gap-fall`，不转为追逐 stumble |

## 预告与移动端

- 最低预告：低/中/高速分别为 2.30 / 1.55 / 1.10 秒，可见危险的 screen-height 在 action point 前分别 ≥ 24 / 32 / 42 CSS px（390 宽）。
- 390x844 以轮廓优先：beam 端帽、ring 中孔、column 偏心顶、gap 双唇是四个必须可见的形状差异；不能只靠 coral 色。
- coral 仅标记切割边/冲击点，且与相邻沙色的相对亮度差 ≥ 3:1；高对比模式再增加沙白 2 px outline。
- 同一时刻不使用漂浮装饰、光雾或追逐者躯体覆盖碰撞区域。render snapshot 应继续报告四类 occurrence 的 clipped CSS-pixel bounds 与正面积。
- V2 原型把 beam 的厚梁、两端支座和投影，ring 的双边厚度/双支点/低位净空，column 的三面实体质量和接地碎屑，gap 的近缘碎裂、远唇和深色洞口全部放在同一透视道路上；生产版应保持这些实体关系而不是退回线框。
