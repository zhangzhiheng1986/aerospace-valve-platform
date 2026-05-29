# -*- coding: utf-8 -*-
"""
航空航天阀门研发模板库 - Template Library Module
Industrial-grade research template management with SQLite storage.
"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'templates.db')

TEMPLATE_CATEGORIES = [
    {"name": "设计计算报告", "description": "阀门设计计算与分析报告模板", "icon": "📐", "sort_order": 1},
    {"name": "试验检验报告", "description": "功能性能、环境、寿命试验报告模板", "icon": "🧪", "sort_order": 2},
    {"name": "技术方案文档", "description": "研制方案、可靠性增长等技术方案", "icon": "📋", "sort_order": 3},
    {"name": "合格审定文档", "description": "鉴定/验收试验大纲与合格审定报告", "icon": "✅", "sort_order": 4},
    {"name": "分析评估报告", "description": "FMEA、可靠性、安全性等分析报告", "icon": "📊", "sort_order": 5},
]

TEMPLATE_SEEDS = [
    # === 设计计算报告 ===
    {
        "category": "设计计算报告",
        "title": "电磁阀线圈优化设计计算报告",
        "description": "基于PSO算法的电磁阀线圈多参数优化设计完整报告模板",
        "standard_refs": "GJB 151B-2013, MIL-STD-461F",
        "content": """# 电磁阀线圈优化设计计算报告

## 1. 设计输入

| 参数 | 数值 | 单位 |
|------|------|------|
| 工作电压 | [填写] | V DC |
| 最低吸合电压 | [填写] | V DC |
| 额定行程 | [填写] | mm |
| 阀口直径 | [填写] | mm |
| 工作介质 | [填写] | — |
| 工作温度范围 | [填写] | °C |
| 绝缘等级 | [填写] | — |

## 2. 优化算法配置

- **算法类型**：粒子群优化 (PSO)
- **种群规模**：[填写]
- **迭代次数**：[填写]
- **优化变量**：AWG线径、匝数、电流
- **约束条件**：
  - 线圈温升 ≤ [填写] °C
  - 最大外形尺寸 ≤ [填写] mm
  - 电流 ≤ [填写] A

## 3. 优化结果

| 参数 | 最优值 | 单位 |
|------|--------|------|
| AWG线径 | [填写] | AWG |
| 匝数 | [填写] | 匝 |
| 线圈电阻 | [填写] | Ω |
| 稳态电流 | [填写] | A |
| 电磁力 | [填写] | N |
| 线圈温升 | [填写] | °C |
| 功率消耗 | [填写] | W |

## 4. 关键计算校核

### 4.1 安匝数计算
$$NI = [填写] \\text{ A·turns}$$

### 4.2 电磁力计算
$$F = \\frac{(NI)^2}{2} \\cdot \\frac{dG}{dx} = [填写] \\text{ N}$$

### 4.3 线圈温升
$$\\Delta T = \\frac{I^2 R}{hA} = [填写] \\text{ °C}$$

## 5. 安全裕度分析

| 校核项 | 要求值 | 实际值 | 裕度 | 判定 |
|--------|--------|--------|------|------|
| 电磁力裕度 | ≥1.3 | [填写] | [填写] | [填写] |
| 温升裕度 | ≤[填写]°C | [填写]°C | [填写] | [填写] |
| 电流裕度 | ≤[填写]A | [填写]A | [填写] | [填写] |

## 6. 结论与建议

[填写优化设计结论与工程实施建议]

---
*报告编制：[填写] | 审核：[填写] | 批准：[填写] | 日期：[填写]*"""
    },
    {
        "category": "设计计算报告",
        "title": "减压阀设计计算报告",
        "description": "航空航天减压阀完整设计计算报告，含力平衡、弹簧、密封分析",
        "standard_refs": "QJ 20156-2012, HB 6455-2014, QJ 1142A-2008",
        "content": """# 减压阀设计计算报告

## 1. 设计输入与要求

| 参数 | 要求值 | 单位 |
|------|--------|------|
| 入口压力范围 | [填写] | MPa |
| 额定出口压力 | [填写] | MPa |
| 额定流量 | [填写] | kg/s |
| 工作介质 | [填写] | — |
| 介质温度 | [填写] | °C |
| 出口压力精度 | ±[填写] | % |
| 锁紧压力 | ≤[填写]×额定 | — |
| 内泄漏率 | ≤[填写] | Pa·m³/s |
| 外泄漏率 | ≤[填写] | Pa·m³/s |
| 设计寿命 | [填写] | 次 |
| 总质量 | ≤[填写] | kg |

## 2. 力平衡分析

### 2.1 敏感元件力平衡方程
$$P_{out} A_{eff} + F_s = P_{in} A_{seat} + F_{spring}$$

### 2.2 出口压力计算
$$P_{out} = \\frac{P_{in}A_{seat} + F_{spring} - F_s}{A_{eff}}$$

## 3. 弹簧设计

| 参数 | 数值 | 单位 |
|------|------|------|
| 弹簧材料 | [填写] | — |
| 钢丝直径 | [填写] | mm |
| 中径 | [填写] | mm |
| 总圈数 | [填写] | — |
| 自由长度 | [填写] | mm |
| 刚度 | [填写] | N/mm |
| 最大应力 | [填写] | MPa |
| 疲劳安全系数 | [填写] | — |

## 4. 密封设计

### 4.1 阀座密封
- 密封结构形式：[填写]
- 密封面宽度：[填写] mm
- 密封比压：[填写] MPa
- 密封力：[填写] N

### 4.2 O形圈密封
- O形圈规格：[填写] (AS568 [填写])
- 沟槽尺寸：[填写] mm × [填写] mm
- 压缩率：[填写] %
- 填充率：[填写] %

## 5. 强度校核

| 零部件 | 材料 | 计算应力(MPa) | 许用应力(MPa) | 安全系数 | 判定 |
|--------|------|---------------|---------------|----------|------|
| 阀体 | [填写] | [填写] | [填写] | [填写] | [填写] |
| 阀盖 | [填写] | [填写] | [填写] | [填写] | [填写] |
| 阀座 | [填写] | [填写] | [填写] | [填写] | [填写] |

## 6. 性能预估

| 性能指标 | 计算值 | 要求值 | 判定 |
|----------|--------|--------|------|
| 出口压力偏差 | [填写]% | ±[填写]% | [填写] |
| 锁紧压力 | [填写]×P额定 | ≤[填写]×P额定 | [填写] |
| 内泄漏率 | [填写] Pa·m³/s | ≤[填写] | [填写] |
| 流量特性 | [填写] | — | [填写] |

## 7. 结论

[填写设计结论、关键技术风险与后续工作计划]

---
*报告编制：[填写] | 审核：[填写] | 批准：[填写] | 日期：[填写]*"""
    },
    {
        "category": "设计计算报告",
        "title": "单向阀设计计算报告",
        "description": "航空航天单向阀完整设计报告，含动态响应、气蚀分析",
        "standard_refs": "HB 6456-2014, QJ 1142A-2008",
        "content": """# 单向阀设计计算报告

## 1. 设计输入

| 参数 | 数值 | 单位 |
|------|------|------|
| 公称通径 | [填写] | mm |
| 开启压力 | [填写] | MPa |
| 额定流量 | [填写] | kg/s |
| 工作压力 | [填写] | MPa |
| 工作介质 | [填写] | — |
| 阀体材料 | [填写] | — |
| 密封材料 | [填写] | — |
| 弹簧材料 | [填写] | — |

## 2. 弹簧设计

略...

## 3. 流动分析

$$C_v = Q \\sqrt{\\frac{SG}{\\Delta P}}$$

略...

---
*报告编制：[填写] | 审核：[填写] | 批准：[填写] | 日期：[填写]*"""
    },
    # === 试验检验报告 ===
    {
        "category": "试验检验报告",
        "title": "热真空试验报告",
        "description": "依据QJ 20156-2012的热真空试验完整报告模板",
        "standard_refs": "QJ 20156-2012, GJB 1027A-2005, GJB 150.2A-2009",
        "content": """# 热真空试验报告

## 1. 试验概述

| 项目 | 内容 |
|------|------|
| 试验名称 | [填写]产品热真空试验 |
| 试验依据 | QJ 20156-2012 第4.6.1条 |
| 试验类别 | [ ] 鉴定级 [ ] 验收级 |
| 试验日期 | [填写] |
| 试验地点 | [填写] |

## 2. 被试产品信息

| 项目 | 内容 |
|------|------|
| 产品名称 | [填写] |
| 产品代号 | [填写] |
| 产品编号 | [填写] |
| 技术状态 | [填写] |
| 制造单位 | [填写] |

## 3. 试验设备

| 设备名称 | 型号/编号 | 量程/精度 | 校准有效期 |
|----------|-----------|-----------|------------|
| 热真空试验箱 | [填写] | [填写] | [填写] |
| 压力传感器 | [填写] | [填写] | [填写] |
| 温度传感器 | [填写] | [填写] | [填写] |
| 氦质谱检漏仪 | [填写] | [填写] | [填写] |
| 数据采集系统 | [填写] | [填写] | [填写] |

## 4. 试验条件

### 4.1 真空度要求
- 试验压力：≤ [填写] Pa
- 试验前真空度：≤ [填写] Pa

### 4.2 温度循环剖面

| 循环序号 | 高温(°C) | 低温(°C) | 温变率(°C/min) | 保温时间(h) |
|----------|----------|----------|-----------------|-------------|
| 1 | [填写] | [填写] | [填写] | [填写] |
| 2 | [填写] | [填写] | [填写] | [填写] |
| ... | [填写] | [填写] | [填写] | [填写] |

### 4.3 循环次数
- 鉴定级：[填写] 循环 (Tmax±10°C)
- 验收级：[填写] 循环 (Tmax±5°C)

## 5. 试验过程记录

### 5.1 产品安装状态
[填写产品安装姿态、测点布置等信息]

### 5.2 泄漏检测记录

| 检测节点 | 检测方法 | 泄漏率(Pa·m³/s) | 允许值(Pa·m³/s) | 判定 |
|----------|----------|-----------------|-----------------|------|
| 试验前 | 氦质谱 | [填写] | ≤[填写] | [填写] |
| 1循环后 | 氦质谱 | [填写] | ≤[填写] | [填写] |
| 2循环后 | 氦质谱 | [填写] | ≤[填写] | [填写] |
| ... | 氦质谱 | [填写] | ≤[填写] | [填写] |
| 试验后 | 氦质谱 | [填写] | ≤[填写] | [填写] |

## 6. 性能测试

| 检测项目 | 技术要求 | 试验前 | 试验后 | 变化量 | 判定 |
|----------|----------|--------|--------|--------|------|
| 额定出口压力(MPa) | [填写] | [填写] | [填写] | [填写] | [填写] |
| 锁紧压力(MPa) | ≤[填写] | [填写] | [填写] | [填写] | [填写] |
| 内泄漏(Pa·m³/s) | ≤[填写] | [填写] | [填写] | [填写] | [填写] |
| 外泄漏(Pa·m³/s) | ≤[填写] | [填写] | [填写] | [填写] | [填写] |
| 开启压力(MPa) | [填写] | [填写] | [填写] | [填写] | [填写] |

## 7. 试验异常与处理

[填写试验过程中发生的异常情况及处理措施]

## 8. 试验结论

- [ ] 产品满足QJ 20156-2012热真空试验要求
- [ ] 产品泄漏率满足技术要求
- [ ] 产品性能满足技术要求
- [ ] 产品外观检查合格
- [ ] 其他：[填写]

## 9. 签署

| 岗位 | 姓名 | 日期 |
|------|------|------|
| 试验操作 | [填写] | [填写] |
| 校对 | [填写] | [填写] |
| 审核 | [填写] | [填写] |
| 批准 | [填写] | [填写] |
"""
    },
    {
        "category": "试验检验报告",
        "title": "寿命试验报告",
        "description": "阀门加速寿命/常规寿命试验完整报告模板",
        "standard_refs": "QJ 20156-2012, GJB 899A-2009",
        "content": """# 寿命试验报告

## 1. 试验概述

略...

---
*报告编制：[填写] | 审核：[填写] | 批准：[填写] | 日期：[填写]*"""
    },
    # === 技术方案文档 ===
    {
        "category": "技术方案文档",
        "title": "阀门研制方案",
        "description": "新型航空航天阀门研制全流程方案文档模板",
        "standard_refs": "GJB 9001C-2017, QJ 3125-2000",
        "content": """# [产品名称]研制方案

## 1. 研制依据与范围

### 1.1 任务来源
[填写]

### 1.2 研制依据
- [填写标准/合同/技术要求编号]

### 1.3 适用范围
本方案适用于[产品名称]的工程设计、制造、试验与交付全过程。

## 2. 产品概述

### 2.1 功能用途
[填写]

### 2.2 主要技术指标

| 序号 | 项目 | 指标要求 | 备注 |
|------|------|----------|------|
| 1 | [填写] | [填写] | [填写] |
| 2 | [填写] | [填写] | [填写] |
| ... | [填写] | [填写] | [填写] |

## 3. 设计方案

### 3.1 工作原理
[填写阀门工作原理描述]

### 3.2 结构方案
[填写结构设计方案，附原理图]

### 3.3 关键零部件选材

略...

---
*编制：[填写] | 审核：[填写] | 批准：[填写] | 日期：[填写]*"""
    },
    # === 合格审定文档 ===
    {
        "category": "合格审定文档",
        "title": "鉴定试验大纲",
        "description": "阀门鉴定试验大纲模板，涵盖全部鉴定试验项目",
        "standard_refs": "QJ 20156-2012, GJB 4057-2000",
        "content": """# [产品名称]鉴定试验大纲

## 1. 总则

### 1.1 试验目的
验证产品设计是否满足技术指标要求，确认产品设计的正确性和工艺的可行性。

### 1.2 试验依据
- QJ 20156-2012 空间系统气体减压阀通用规范
- [其他标准]

### 1.3 被试产品
[产品名称、代号、数量等信息]

## 2. 试验矩阵

| 序号 | 试验项目 | 试验条件 | 样品数量 | 验收标准 | 备注 |
|------|----------|----------|----------|----------|------|
| 1 | 外观检查 | 目视 | [填写] | 无缺陷 | — |
| 2 | 尺寸检查 | 量具 | [填写] | 符合图纸 | — |
| 3 | 气密性试验 | [填写]MPa | [填写] | ≤[填写]Pa·m³/s | — |
| 4 | 功能性能试验 | [填写] | [填写] | 符合指标 | — |
| 5 | 振动试验 | [填写] | [填写] | 无损坏 | — |
| 6 | 冲击试验 | [填写] | [填写] | 无损坏 | — |
| 7 | 热真空试验 | [填写] | [填写] | 符合指标 | — |
| 8 | 热循环试验 | [填写] | [填写] | 符合指标 | — |
| 9 | 寿命试验 | [填写] | [填写] | 符合指标 | — |
| 10 | 爆破试验 | [填写] | [填写] | 无破裂 | — |
| ... | ... | ... | ... | ... | ... |

## 3. 试验条件详解

[逐项展开各试验项目的详细条件和步骤]

---
*编制：[填写] | 审核：[填写] | 批准：[填写] | 日期：[填写]*"""
    },
    {
        "category": "合格审定文档",
        "title": "合格审定报告",
        "description": "阀门合格审定/鉴定总结报告模板",
        "standard_refs": "QJ 20156-2012",
        "content": """# [产品名称]合格审定报告

## 1. 概述

略...

---
*编制：[填写] | 审核：[填写] | 批准：[填写] | 日期：[填写]*"""
    },
    # === 分析评估报告 ===
    {
        "category": "分析评估报告",
        "title": "故障模式影响分析 (FMEA)",
        "description": "阀门FMEA分析报告模板，含功能FMEA和硬件FMEA",
        "standard_refs": "GJB 1391-2006, QJ 3050-1998",
        "content": """# 故障模式影响分析 (FMEA) 报告

## 1. 分析范围

产品名称：[填写]
分析级别：[填写]（系统级/分系统级/零部件级）
分析类型：[ ] 功能FMEA [ ] 硬件FMEA

## 2. FMEA表格

| 序号 | 零部件 | 功能 | 故障模式 | 故障原因 | 故障影响 | 严酷度 | 发生概率 | 检测方法 | 补偿措施 | RPN |
|------|--------|------|----------|----------|----------|--------|----------|----------|----------|-----|
| 1 | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] |
| 2 | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] |
| ... | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] | [填写] |

## 3. 严酷度类别定义

| 类别 | 定义 |
|------|------|
| I类（灾难） | 导致系统失效，危及任务和人员安全 |
| II类（严重） | 导致系统主要功能丧失 |
| III类（一般） | 导致系统性能下降 |
| IV类（轻微） | 不影响系统功能 |

## 4. 关键项目清单

| 序号 | 故障模式 | RPN | 是否关键 | 建议措施 |
|------|----------|-----|----------|----------|
| [填写] | [填写] | [填写] | [ ] 是 [ ] 否 | [填写] |

## 5. 结论与建议

[填写FMEA分析总结]

---
*编制：[填写] | 审核：[填写] | 批准：[填写] | 日期：[填写]*"""
    },
    {
        "category": "分析评估报告",
        "title": "可靠性评估报告",
        "description": "阀门可靠性预计与评估分析报告模板",
        "standard_refs": "GJB 813-1990, GJB 299C-2006, GJB 899A-2009",
        "content": """# 可靠性评估报告

## 1. 概述

### 1.1 评估目的
[填写]

### 1.2 评估依据
- GJB 813-1990 可靠性模型的建立和可靠性预计
- GJB 299C-2006 电子设备可靠性预计手册
- [其他标准]

## 2. 可靠性模型

### 2.1 可靠性框图
[附可靠性框图]

### 2.2 可靠性数学模型
$$R_s(t) = \\prod_{i=1}^{n} R_i(t)$$

## 3. 可靠性预计

| 零部件 | 数量 | 基本失效率(10⁻⁶/h) | 环境系数 | 质量系数 | 工作失效率(10⁻⁶/h) |
|--------|------|---------------------|----------|----------|---------------------|
| [填写] | [填写] | [填写] | [填写] | [填写] | [填写] |
| ... | ... | ... | ... | ... | ... |

**总失效率**：[填写] × 10⁻⁶/h
**MTBF**：[填写] h

## 4. 可靠性分配

略...

---
*编制：[填写] | 审核：[填写] | 批准：[填写] | 日期：[填写]*"""
    },
]


def _init_db():
    """Initialize the template database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            icon TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            content TEXT DEFAULT '',
            standard_refs TEXT DEFAULT '',
            version TEXT DEFAULT '1.0',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category_id);
        CREATE INDEX IF NOT EXISTS idx_templates_title ON templates(title);
    ''')
    conn.commit()
    conn.close()


def seed_database():
    """Seed the database with initial template data if empty."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if already seeded
    c.execute('SELECT COUNT(*) FROM categories')
    cat_count = c.fetchone()[0]
    if cat_count > 0:
        conn.close()
        return

    # Insert categories
    for cat in TEMPLATE_CATEGORIES:
        c.execute(
            'INSERT INTO categories (name, description, icon, sort_order) VALUES (?,?,?,?)',
            (cat['name'], cat['description'], cat['icon'], cat['sort_order'])
        )

    # Insert templates
    for tmpl in TEMPLATE_SEEDS:
        c.execute('SELECT id FROM categories WHERE name = ?', (tmpl['category'],))
        row = c.fetchone()
        if not row:
            continue
        cat_id = row[0]
        c.execute(
            'INSERT INTO templates (category_id, title, description, content, standard_refs) VALUES (?,?,?,?,?)',
            (cat_id, tmpl['title'], tmpl['description'], tmpl['content'], tmpl.get('standard_refs', ''))
        )

    conn.commit()
    conn.close()


# ==================== Category CRUD ====================

def get_all_categories():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT c.*, (SELECT COUNT(*) FROM templates WHERE category_id=c.id) as template_count FROM categories c ORDER BY sort_order, id')
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"success": True, "categories": rows}


def get_category(cat_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT c.*, (SELECT COUNT(*) FROM templates WHERE category_id=c.id) as template_count FROM categories c WHERE id=?', (cat_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"success": True, "category": dict(row)}
    return {"success": False, "error": "分类不存在"}


# ==================== Template CRUD ====================

def get_templates(category_id=None, search=None, limit=50, offset=0):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = '''
        SELECT t.*, c.name as category_name, c.icon as category_icon
        FROM templates t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE 1=1
    '''
    params = []

    if category_id:
        query += ' AND t.category_id = ?'
        params.append(category_id)

    if search:
        query += ' AND (t.title LIKE ? OR t.description LIKE ? OR t.content LIKE ? OR t.standard_refs LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term, search_term, search_term])

    query += ' ORDER BY t.updated_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])

    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]

    # Count total
    count_query = 'SELECT COUNT(*) FROM templates t WHERE 1=1'
    count_params = []
    if category_id:
        count_query += ' AND t.category_id = ?'
        count_params.append(category_id)
    if search:
        count_query += ' AND (t.title LIKE ? OR t.description LIKE ?)'
        count_params.extend([f'%{search}%', f'%{search}%'])

    c.execute(count_query, count_params)
    total = c.fetchone()[0]

    conn.close()
    return {"success": True, "templates": rows, "total": total, "limit": limit, "offset": offset}


def get_template(template_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT t.*, c.name as category_name, c.icon as category_icon
        FROM templates t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id = ?
    ''', (template_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"success": True, "template": dict(row)}
    return {"success": False, "error": "模板不存在"}


def create_template(title, content='', category_id=None, description='', standard_refs='', version='1.0'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if category_id:
        c.execute('SELECT id FROM categories WHERE id=?', (category_id,))
        if not c.fetchone():
            conn.close()
            return {"success": False, "error": "分类不存在"}

    c.execute(
        'INSERT INTO templates (category_id, title, description, content, standard_refs, version) VALUES (?,?,?,?,?,?)',
        (category_id, title, description, content, standard_refs, version)
    )
    template_id = c.lastrowid
    conn.commit()
    conn.close()

    return get_template(template_id)


def update_template(template_id, **kwargs):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    allowed = ['title', 'content', 'description', 'standard_refs', 'version', 'category_id']
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}

    if not updates:
        conn.close()
        return {"success": False, "error": "无有效更新字段"}

    updates['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    set_clause = ', '.join(f'{k}=?' for k in updates)
    values = list(updates.values()) + [template_id]

    c.execute(f'UPDATE templates SET {set_clause} WHERE id=?', values)
    conn.commit()
    affected = c.rowcount
    conn.close()

    if affected:
        return get_template(template_id)
    return {"success": False, "error": "模板不存在"}


def delete_template(template_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM templates WHERE id=?', (template_id,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    if affected:
        return {"success": True, "message": "模板已删除"}
    return {"success": False, "error": "模板不存在"}


def get_template_stats():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as total_templates FROM templates')
    t = c.fetchone()['total_templates']
    c.execute('SELECT COUNT(*) as total_categories FROM categories')
    c2 = c.fetchone()['total_categories']
    c.execute('SELECT c.name, c.icon, COUNT(t.id) as cnt FROM categories c LEFT JOIN templates t ON c.id=t.category_id GROUP BY c.id ORDER BY c.sort_order')
    by_cat = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"success": True, "total_templates": t, "total_categories": c2, "by_category": by_cat}


# Initialize on import
_init_db()
seed_database()