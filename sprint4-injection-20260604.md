# Sprint 4 完整注入 — 流体力学扩展 (25公式, 3类别)

**时间**: 2026-06-04 22:00-22:50  
**目标**: 将 Sprint 4 的 25 条计算函数注入到流体力学计算器全线（后端引擎 + i18n + 前端渲染）

## 成果

### 注入的文件
| 文件 | 操作 | 注入内容 |
|------|------|----------|
| `fluid_mechanics_calc.py` | 修改 | import 25函数 + catalog增3类 + compute dispatch增25条elif |
| `fluid_mechanics_i18n.py` | 修改 | 25条公式i18n + 3条category i18n |
| `fluid_mechanics_sprint4.py` | 新建 | 25条计算函数 (21KB) |

### 三类新公式 (25条)

**14_non_newtonian 非牛顿流体 (8)**: bingham_shear, bingham_pipe_Q, power_law_mu_app, power_law_pipe_V, re_gen_power_law, dodge_metzner_f, hb_shear, casson_shear

**15_multiphase 多相流 (9)**: hom_void_frac, hom_tp_density, mcadams_visc, LM_X, chisholm_phi2, drift_flux_alpha, baker_map, taitel_dukler, slug_freq

**16_cavitation 空化与气蚀 (8)**: cav_number, thoma_param, npsh_a, npsh_r, rayleigh_plesset, bubble_freq, cav_erosion, crit_cav_factor

### 验证结果
- 6/6 计算测试通过 (bingham=60, cav_number=1.98, npsh_a=11.61, LM_X=0.11, bubble_freq=328653)
- 搜索索引: 135 → 160 (+25条)
- 类别数: 13 → 16 (+3)
- i18n语法检查通过
- calc语法检查通过

### 遇到的Bug
- i18n文件原有 `13_gas_flow` 条目缺少尾逗号 (已修复)
- 首次calc注入将dispatch挤为一行 (git checkout后重做, split('\n')方式修复)
