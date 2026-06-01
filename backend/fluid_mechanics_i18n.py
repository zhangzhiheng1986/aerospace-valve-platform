# -*- coding: utf-8 -*-
"""
Fluid Mechanics Super Calculator - Chinese I18N Data Module
===========================================================
121 formulas across 12 categories, 14 fluids, 9 pipe materials.
All Chinese terminology follows Chinese Fluid Mechanics standards (GB/T).
"""

# =============================================================================
# Category I18N
# =============================================================================

CATEGORY_I18N = {
    "1_basic_properties": {
        "name_zh": "\u6d41\u4f53\u57fa\u672c\u6027\u8d28",
        "desc_zh": "\u5bc6\u5ea6\u3001\u7c98\u5ea6\u3001\u4f53\u79ef\u6a21\u91cf\u3001\u8868\u9762\u5f20\u529b\u3001\u84b8\u6c7d\u538b\u7b49\u6d41\u4f53\u57fa\u7840\u7269\u7406\u6027\u8d28\u8ba1\u7b97"
    },
    "2_hydrostatics": {
        "name_zh": "\u6d41\u4f53\u9759\u529b\u5b66",
        "desc_zh": "\u9759\u6b62\u6d41\u4f53\u7684\u538b\u529b\u5206\u5e03\u3001\u6d6e\u529b\u3001\u6bdb\u7ec6\u73b0\u8c61\u4e0e\u7a33\u6027\u8ba1\u7b97"
    },
    "3_bernoulli": {
        "name_zh": "\u8fde\u7eed\u6027\u4e0e\u4f2f\u52aa\u5229\u65b9\u7a0b",
        "desc_zh": "\u6d41\u91cf\u5b88\u6046\u3001\u4f2f\u52aa\u5229\u80fd\u91cf\u65b9\u7a0b\u3001\u52a8\u91cf\u5b9a\u7406\u3001\u7a7a\u5316\u6570\u7b49\u5de5\u7a0b\u6838\u5fc3\u65b9\u7a0b"
    },
    "4_pipe_flow": {
        "name_zh": "\u7ba1\u9053\u6d41\u52a8",
        "desc_zh": "\u96f7\u8bfa\u6570\u3001\u6469\u64e6\u7cfb\u6570\u3001Darcy-Weisbach\u6cbf\u7a0b\u635f\u5931\u3001\u5c40\u90e8\u635f\u5931\u4e0e\u7ba1\u7f51\u8ba1\u7b97"
    },
    "5_open_channel": {
        "name_zh": "\u660e\u6e20\u6d41\u52a8",
        "desc_zh": "\u4f5b\u6c9b\u5fb7\u6570\u3001\u66fc\u5b81\u516c\u5f0f\u3001\u4e34\u754c\u6df1\u5ea6\u3001\u6c34\u8dc3\u4e0e\u5830\u6d41\u91cf\u8ba1\u7b97"
    },
    "6_compressible": {
        "name_zh": "\u53ef\u538b\u7f29\u6d41\u52a8",
        "desc_zh": "\u58f0\u901f\u3001\u9a6c\u8d6b\u6570\u3001\u7b49\u71b5\u5173\u7cfb\u3001\u6fc0\u6ce2\u3001Prandtl-Meyer\u6d41\u52a8\u4e0e\u55b7\u7ba1\u8ba1\u7b97"
    },
    "7_orifice_valve": {
        "name_zh": "\u5b54\u677f\u4e0e\u9600\u95e8",
        "desc_zh": "\u5b54\u677f\u6d41\u91cf\u3001\u9600\u95e8Cv/Kv\u7cfb\u5217\u3001\u6587\u4e18\u91cc\u6d41\u91cf\u8ba1\u3001\u6d41\u901a\u80fd\u529b\u4e0e\u7a7a\u5316\u8bc4\u4f30"
    },
    "8_boundary_layer": {
        "name_zh": "\u8fb9\u754c\u5c42\u4e0e\u963b\u529b",
        "desc_zh": "\u8fb9\u754c\u5c42\u539a\u5ea6\u3001\u8868\u9762\u6469\u64e6\u7cfb\u6570\u3001\u963b\u529b/\u5347\u529b\u8ba1\u7b97\u4e0e\u7403\u4f53\u62d6\u66f3\u6a21\u578b"
    },
    "9_fluid_power": {
        "name_zh": "\u6db2\u538b\u4e0e\u6d41\u4f53\u52a8\u529b",
        "desc_zh": "\u6cf5\u529f\u7387\u3001\u6db2\u538b\u7f38/\u9a6c\u8fbe\u8ba1\u7b97\u3001\u84c4\u80fd\u5668\u3001\u6db2\u538b\u5f39\u7c27\u4e0e\u65f6\u95f4\u5e38\u6570"
    },
    "10_water_hammer": {
        "name_zh": "\u6c34\u9524\u4e0e\u6d8c\u6d6a",
        "desc_zh": "Joukowsky\u6c34\u9524\u538b\u529b\u3001\u6ce2\u901f\u3001\u77ac\u6001\u5173\u9600\u6d8c\u538b\u4e0e\u7ba1\u9053\u5468\u671f\u8ba1\u7b97"
    },
    "11_dimensional": {
        "name_zh": "\u91cf\u7eb2\u5206\u6790",
        "desc_zh": "\u96f7\u8bfa\u6570\u3001\u4f5b\u6c9b\u5fb7\u6570\u3001\u9a6c\u8d6b\u6570\u3001\u97e6\u4f2f\u6570\u3001\u6b27\u62c9\u6570\u3001\u65af\u7279\u52b3\u54c8\u5c14\u6570\u4e0e\pi\u5b9a\u7406"
    },
    "12_fsi": {
        "name_zh": "\u6d41\u56fa\u8026\u5408",
        "desc_zh": "\u6d41\u4f53\u67f1\u56fa\u6709\u9891\u7387\u3001\u9644\u52a0\u8d28\u91cf\u3001\u6da1\u8857\u8131\u843d\u3001\u6d41\u81f4\u632f\u52a8\u4e0e\u5f39\u6027\u5931\u7a33"
    }
}

# =============================================================================
# Fluid I18N (14 fluids)
# =============================================================================

FLUID_I18N = {
    "water_20C":      "\u6c34 (20\u2103)",
    "water_50C":      "\u6c34 (50\u2103)",
    "air_20C":        "\u7a7a\u6c14 (20\u2103, 1atm)",
    "helium_20C":     "\u6c26\u6c14 (20\u2103, 1atm)",
    "nitrogen_20C":   "\u6c2e\u6c14 (20\u2103, 1atm)",
    "oxygen_20C":     "\u6c27\u6c14 (20\u2103, 1atm)",
    "kerosene":       "RP-1 \u706b\u6cb9",
    "hydrazine":      "\u80bc (N\u2082H\u2084)",
    "hydraulic_oil":  "\u6db2\u538b\u6cb9 VG32",
    "lh2":            "\u6db2\u6c22 (LH2)",
    "lox":            "\u6db2\u6c27 (LOX)",
    "diesel":         "\u67f4\u6cb9",
    "sea_water":      "\u6d77\u6c34 (20\u2103)",
    "ethanol":        "\u4e59\u9187 (20\u2103)"
}

# =============================================================================
# Pipe Roughness I18N (9 materials)
# =============================================================================

PIPE_ROUGHNESS_I18N = {
    "drawn_tube":       "\u62c9\u5236\u7ba1",
    "steel_commercial": "\u5546\u4e1a\u94a2\u7ba1",
    "steel_riveted":    "\u94c6\u63a5\u94a2\u7ba1",
    "cast_iron":        "\u94f8\u94c1\u7ba1",
    "galvanized_iron":  "\u9540\u950c\u94c1\u7ba1",
    "concrete":         "\u6df7\u51dd\u571f\u7ba1",
    "smooth_plastic":   "\u5149\u6ed1\u5851\u6599\u7ba1",
    "brass":            "\u9ec4\u94dc\u7ba1",
    "copper":           "\u7d2b\u94dc\u7ba1"
}

# =============================================================================
# Formula I18N (121 formulas across 12 categories)
# =============================================================================

FORMULA_I18N = {

    # ====== Category 1: Basic Fluid Properties (8) ======

    "density": {
        "name_zh": "\u5bc6\u5ea6",
        "desc_zh": "\u8ba1\u7b97\u7269\u8d28\u5355\u4f4d\u4f53\u79ef\u7684\u8d28\u91cf",
        "latex": r"\rho = \frac{m}{V}",
        "inputs": {
            "mass":   {"label_zh": "\u8d28\u91cf",   "unit": "kg",  "desc_zh": "\u7269\u8d28\u7684\u603b\u8d28\u91cf"},
            "volume": {"label_zh": "\u4f53\u79ef",   "unit": "m\u00b3", "desc_zh": "\u7269\u8d28\u5360\u636e\u7684\u7a7a\u95f4\u4f53\u79ef"}
        },
        "output": {"density": {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3"}},
        "application_zh": "\u9002\u7528\u4e8e\u6240\u6709\u6d41\u4f53\u548c\u56fa\u4f53\u7684\u5bc6\u5ea6\u57fa\u7840\u8ba1\u7b97\uff0c\u662f\u6d41\u4f53\u529b\u5b66\u6700\u57fa\u7840\u7684\u7269\u6027\u53c2\u6570\uff0c\u76f4\u63a5\u5f71\u54cd\u96f7\u8bfa\u6570\u3001\u6d41\u91cf\u8ba1\u7b97\u548c\u538b\u529b\u635f\u5931\u8bc4\u4f30"
    },

    "specific_weight": {
        "name_zh": "\u91cd\u5ea6",
        "desc_zh": "\u8ba1\u7b97\u5355\u4f4d\u4f53\u79ef\u6d41\u4f53\u7684\u91cd\u91cf",
        "latex": r"\gamma = \rho g",
        "inputs": {
            "rho": {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"},
            "g":   {"label_zh": "\u91cd\u529b\u52a0\u901f\u5ea6", "unit": "m/s\u00b2", "desc_zh": "\u91cd\u529b\u52a0\u901f\u5ea6\uff0c\u9ed8\u8ba4\u5730\u7403\u8868\u9762\u503c9.81"}
        },
        "output": {"gamma": {"label_zh": "\u91cd\u5ea6", "unit": "N/m\u00b3"}},
        "application_zh": "\u7528\u4e8e\u8ba1\u7b97\u9759\u6b62\u6d41\u4f53\u7684\u538b\u529b\u5206\u5e03\u548c\u6d6e\u529b\uff0c\u5728\u6db2\u538b\u7cfb\u7edf\u8bbe\u8ba1\u548c\u6c34\u5e93\u538b\u529b\u8ba1\u7b97\u4e2d\u5e7f\u6cdb\u5e94\u7528"
    },

    "specific_gravity": {
        "name_zh": "\u76f8\u5bf9\u5bc6\u5ea6\uff08\u6bd4\u91cd\uff09",
        "desc_zh": "\u8ba1\u7b97\u6d41\u4f53\u5bc6\u5ea6\u4e0e\u53c2\u8003\u5bc6\u5ea6\u7684\u6bd4\u503c",
        "latex": r"\text{SG} = \frac{\rho}{\rho_{\text{ref}}}",
        "inputs": {
            "rho":     {"label_zh": "\u6d41\u4f53\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u5f85\u6d4b\u6d41\u4f53\u7684\u5bc6\u5ea6"},
            "rho_ref": {"label_zh": "\u53c2\u8003\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u53c2\u8003\u6d41\u4f53\u5bc6\u5ea6\uff0c\u901a\u5e384\u2103\u6c34=1000 kg/m\u00b3"}
        },
        "output": {"SG": {"label_zh": "\u76f8\u5bf9\u5bc6\u5ea6", "unit": "\u65e0\u91cf\u7eb2"}},
        "application_zh": "\u5e7f\u6cdb\u7528\u4e8e\u9600\u95e8Cv\u8ba1\u7b97\u3001\u6cf5\u9009\u578b\u548c\u6d41\u4f53\u5206\u5c42\u5224\u65ad\uff0c\u662f\u5de5\u7a0b\u73b0\u573a\u5feb\u901f\u5224\u65ad\u6d41\u4f53\u7c7b\u578b\u7684\u91cd\u8981\u65e0\u91cf\u7eb2\u53c2\u6570"
    },

    "dynamic_viscosity": {
        "name_zh": "\u52a8\u529b\u7c98\u5ea6",
        "desc_zh": "\u7531\u8fd0\u52a8\u7c98\u5ea6\u548c\u5bc6\u5ea6\u8ba1\u7b97\u52a8\u529b\u7c98\u5ea6",
        "latex": r"\mu = \nu\rho",
        "inputs": {
            "nu":  {"label_zh": "\u8fd0\u52a8\u7c98\u5ea6", "unit": "m\u00b2/s", "desc_zh": "\u6d41\u4f53\u7684\u8fd0\u52a8\u7c98\u5ea6"},
            "rho": {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"}
        },
        "output": {"mu": {"label_zh": "\u52a8\u529b\u7c98\u5ea6", "unit": "Pa\u00b7s"}},
        "application_zh": "\u52a8\u529b\u7c98\u5ea6\u662f\u8ba1\u7b97\u96f7\u8bfa\u6570\u548c\u6d41\u4f53\u526a\u5207\u5e94\u529b\u7684\u5173\u952e\u53c2\u6570\uff0c\u5728\u6da6\u6ed1\u6cb9\u9009\u62e9\u3001\u8f74\u627f\u8bbe\u8ba1\u548c\u6d41\u4f53\u52a8\u529b\u5206\u6790\u4e2d\u4e0d\u53ef\u6216\u7f3a"
    },

    "kinematic_viscosity": {
        "name_zh": "\u8fd0\u52a8\u7c98\u5ea6",
        "desc_zh": "\u7531\u52a8\u529b\u7c98\u5ea6\u548c\u5bc6\u5ea6\u8ba1\u7b97\u8fd0\u52a8\u7c98\u5ea6",
        "latex": r"\nu = \frac{\mu}{\rho}",
        "inputs": {
            "mu":  {"label_zh": "\u52a8\u529b\u7c98\u5ea6", "unit": "Pa\u00b7s", "desc_zh": "\u6d41\u4f53\u7684\u52a8\u529b\u7c98\u5ea6"},
            "rho": {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"}
        },
        "output": {"nu": {"label_zh": "\u8fd0\u52a8\u7c98\u5ea6", "unit": "m\u00b2/s"}},
        "application_zh": "\u8fd0\u52a8\u7c98\u5ea6\u76f4\u63a5\u51fa\u73b0\u5728\u96f7\u8bfa\u6570\u8ba1\u7b97\u4e2d\uff0c\u5bf9\u6d41\u6001\u8bc6\u522b\uff08\u5c42\u6d41/\u6e4d\u6d41\uff09\u548c\u6362\u70ed\u8ba1\u7b97\u81f3\u5173\u91cd\u8981"
    },

    "bulk_modulus": {
        "name_zh": "\u4f53\u79ef\u5f39\u6027\u6a21\u91cf",
        "desc_zh": "\u8ba1\u7b97\u6d41\u4f53\u62b5\u6297\u538b\u7f29\u7684\u80fd\u529b",
        "latex": r"K = -V\frac{dP}{dV}",
        "inputs": {
            "dp": {"label_zh": "\u538b\u529b\u53d8\u5316", "unit": "Pa", "desc_zh": "\u538b\u529b\u53d8\u5316\u91cf"},
            "dV": {"label_zh": "\u4f53\u79ef\u53d8\u5316", "unit": "m\u00b3", "desc_zh": "\u4f53\u79ef\u53d8\u5316\u91cf"},
            "V":  {"label_zh": "\u521d\u59cb\u4f53\u79ef", "unit": "m\u00b3", "desc_zh": "\u6d41\u4f53\u7684\u521d\u59cb\u4f53\u79ef"}
        },
        "output": {"K": {"label_zh": "\u4f53\u79ef\u5f39\u6027\u6a21\u91cf", "unit": "Pa"}},
        "application_zh": "\u76f4\u63a5\u5f71\u54cd\u6db2\u538b\u7cfb\u7edf\u7684\u521a\u5ea6\u548c\u54cd\u5e94\u901f\u5ea6\uff0c\u6c34\u9524\u5206\u6790\u3001\u6db2\u538b\u5f39\u7c27\u8ba1\u7b97\u548c\u58f0\u901f\u8ba1\u7b97\u7684\u57fa\u7840\u53c2\u6570"
    },

    "surface_tension": {
        "name_zh": "\u8868\u9762\u5f20\u529b",
        "desc_zh": "\u8ba1\u7b97\u6db2\u4f53\u8868\u9762\u5f20\u529b\u4ea7\u751f\u7684\u529b",
        "latex": r"F_{\sigma} = \sigma L",
        "inputs": {
            "sigma": {"label_zh": "\u8868\u9762\u5f20\u529b\u7cfb\u6570", "unit": "N/m", "desc_zh": "\u6d41\u4f53\u7684\u8868\u9762\u5f20\u529b\u7cfb\u6570"},
            "L":     {"label_zh": "\u63a5\u89e6\u957f\u5ea6", "unit": "m", "desc_zh": "\u6db2\u4f53\u8868\u9762\u7684\u63a5\u89e6\u7ebf\u957f\u5ea6"}
        },
        "output": {"F_sigma": {"label_zh": "\u8868\u9762\u5f20\u529b", "unit": "N"}},
        "application_zh": "\u5728\u6bdb\u7ec6\u7ba1\u9053\u6d41\u52a8\u3001\u6db2\u6ef4\u5f62\u6210\u3001\u55b7\u96fe\u5316\u548c\u71c3\u6cb9\u96fe\u5316\u8bbe\u8ba1\u4e2d\u8d77\u5173\u952e\u4f5c\u7528\uff0c\u5f71\u54cd\u5c0f\u5c3a\u5bf8\u6d41\u52a8\u7279\u6027"
    },

    "vapor_pressure": {
        "name_zh": "\u84b8\u6c7d\u538b\uff08Antoine\u65b9\u7a0b\uff09",
        "desc_zh": "\u901a\u8fc7Antoine\u65b9\u7a0b\u8ba1\u7b97\u6d41\u4f53\u5728\u7ed9\u5b9a\u6e29\u5ea6\u4e0b\u7684\u84b8\u6c7d\u538b",
        "latex": r"\log_{10}P_v = A - \frac{B}{C + T}",
        "inputs": {
            "A": {"label_zh": "Antoine\u5e38\u6570A", "unit": "\u65e0\u91cf\u7eb2", "desc_zh": "Antoine\u65b9\u7a0b\u5e38\u6570A"},
            "B": {"label_zh": "Antoine\u5e38\u6570B", "unit": "\u65e0\u91cf\u7eb2", "desc_zh": "Antoine\u65b9\u7a0b\u5e38\u6570B"},
            "C": {"label_zh": "Antoine\u5e38\u6570C", "unit": "\u2103", "desc_zh": "Antoine\u65b9\u7a0b\u5e38\u6570C"},
            "T": {"label_zh": "\u6e29\u5ea6", "unit": "\u2103", "desc_zh": "\u6d41\u4f53\u6e29\u5ea6"}
        },
        "output": {"P_v": {"label_zh": "\u84b8\u6c7d\u538b", "unit": "Pa"}},
        "application_zh": "\u84b8\u6c7d\u538b\u662f\u5224\u65ad\u7a7a\u5316\u98ce\u9669\u7684\u5173\u952e\u53c2\u6570\uff0c\u5728\u6cf5\u6c7d\u8680\u4f59\u91cf\u8ba1\u7b97\u3001\u9600\u95e8\u7a7a\u5316\u9884\u9632\u548c\u71c3\u6599\u50a8\u7f50\u8bbe\u8ba1\u4e2d\u5fc5\u987b\u8003\u8651"
    },

    # ====== Category 2: Hydrostatics (8) ======

    "hydrostatic_pressure": {
        "name_zh": "\u9759\u538b\u5206\u5e03",
        "desc_zh": "\u8ba1\u7b97\u9759\u6b62\u6d41\u4f53\u5728\u6307\u5b9a\u6df1\u5ea6\u5904\u7684\u603b\u538b\u529b",
        "latex": r"P = P_0 + \rho g h",
        "inputs": {
            "rho": {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"},
            "g":   {"label_zh": "\u91cd\u529b\u52a0\u901f\u5ea6", "unit": "m/s\u00b2", "desc_zh": "\u91cd\u529b\u52a0\u901f\u5ea6"},
            "h":   {"label_zh": "\u6df1\u5ea6", "unit": "m", "desc_zh": "\u81ea\u7531\u6db2\u9762\u4ee5\u4e0b\u7684\u6df1\u5ea6"},
            "P0":  {"label_zh": "\u8868\u9762\u538b\u529b", "unit": "Pa", "desc_zh": "\u81ea\u7531\u6db2\u9762\u5904\u7684\u538b\u529b\uff0c\u9ed8\u8ba4101325 Pa"}
        },
        "output": {"P": {"label_zh": "\u9759\u538b", "unit": "Pa"}},
        "application_zh": "\u6c34\u5e93\u5927\u575d\u3001\u50a8\u7f50\u58c1\u9762\u548c\u6f5c\u6c34\u5668\u5916\u58f3\u7684\u538b\u529b\u8ba1\u7b97\u57fa\u7840\uff0c\u76f4\u63a5\u5f71\u54cd\u7ed3\u6784\u58c1\u539a\u548c\u5f3a\u5ea6\u8bbe\u8ba1"
    },

    "manometer": {
        "name_zh": "\u6db2\u67f1\u538b\u5dee\u8ba1",
        "desc_zh": "\u901a\u8fc7U\u5f62\u7ba1\u6db2\u67f1\u9ad8\u5ea6\u5dee\u8ba1\u7b97\u538b\u529b\u5dee",
        "latex": r"\Delta P = \rho_{\text{fluid}} g \Delta h",
        "inputs": {
            "rho_fluid": {"label_zh": "\u6d4b\u538b\u6d41\u4f53\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d4b\u538b\u7ba1\u5185\u6db2\u4f53\u7684\u5bc6\u5ea6"},
            "g":         {"label_zh": "\u91cd\u529b\u52a0\u901f\u5ea6", "unit": "m/s\u00b2", "desc_zh": "\u91cd\u529b\u52a0\u901f\u5ea6"},
            "h_diff":    {"label_zh": "\u6db2\u67f1\u9ad8\u5ea6\u5dee", "unit": "m", "desc_zh": "U\u5f62\u7ba1\u4e24\u4fa7\u6db2\u67f1\u9ad8\u5ea6\u5dee"}
        },
        "output": {"dP": {"label_zh": "\u538b\u529b\u5dee", "unit": "Pa"}},
        "application_zh": "\u5b9e\u9a8c\u5ba4\u538b\u529b\u6d4b\u91cf\u7684\u7ecf\u5178\u65b9\u6cd5\uff0c\u5e7f\u6cdb\u7528\u4e8e\u98ce\u6d1e\u538b\u5dee\u6d4b\u91cf\u3001\u6d41\u91cf\u8ba1\u683c\u6807\u5b9a\u548c\u901a\u98ce\u7cfb\u7edf\u8c03\u8bd5"
    },

    "hydrostatic_force_plane": {
        "name_zh": "\u5e73\u9762\u9759\u6c34\u603b\u538b\u529b",
        "desc_zh": "\u8ba1\u7b97\u4f5c\u7528\u5728\u5e73\u9762\u4e0a\u7684\u9759\u6c34\u603b\u538b\u529b",
        "latex": r"F = \rho g h_c A",
        "inputs": {
            "rho": {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"},
            "g":   {"label_zh": "\u91cd\u529b\u52a0\u901f\u5ea6", "unit": "m/s\u00b2", "desc_zh": "\u91cd\u529b\u52a0\u901f\u5ea6"},
            "h_c": {"label_zh": "\u5f62\u5fc3\u6df1\u5ea6", "unit": "m", "desc_zh": "\u5e73\u9762\u5f62\u5fc3\u5230\u81ea\u7531\u6db2\u9762\u7684\u5782\u76f4\u8ddd\u79bb"},
            "A":   {"label_zh": "\u5e73\u9762\u9762\u79ef", "unit": "m\u00b2", "desc_zh": "\u5e73\u9762\u7684\u6d78\u6ca1\u9762\u79ef"}
        },
        "output": {"F": {"label_zh": "\u9759\u6c34\u603b\u538b\u529b", "unit": "N"}},
        "application_zh": "\u6c34\u575d\u95f8\u95e8\u3001\u8230\u8239\u8231\u58c1\u3001\u5bb9\u5668\u5e95\u90e8\u7ed3\u6784\u5f3a\u5ea6\u8ba1\u7b97\u7684\u6838\u5fc3\u516c\u5f0f\uff0c\u76f4\u63a5\u51b3\u5b9a\u627f\u538b\u7ed3\u6784\u7684\u6750\u6599\u548c\u539a\u5ea6"
    },

    "center_of_pressure": {
        "name_zh": "\u538b\u529b\u4e2d\u5fc3",
        "desc_zh": "\u8ba1\u7b97\u5e73\u9762\u4e0a\u9759\u6c34\u603b\u538b\u529b\u7684\u4f5c\u7528\u70b9\u4f4d\u7f6e",
        "latex": r"h_{\text{cp}} \approx h_c + \frac{I_{xx,c}}{h_c A}",
        "inputs": {
            "h_c":     {"label_zh": "\u5f62\u5fc3\u6df1\u5ea6", "unit": "m", "desc_zh": "\u5e73\u9762\u5f62\u5fc3\u7684\u5782\u76f4\u6df1\u5ea6"},
            "I_xx_c":  {"label_zh": "\u9762\u79ef\u60ef\u6027\u77e9", "unit": "m\u2074", "desc_zh": "\u5e73\u9762\u5bf9\u901a\u8fc7\u5f62\u5fc3\u7684\u6c34\u5e73\u8f74\u7684\u9762\u79ef\u60ef\u6027\u77e9"},
            "A":       {"label_zh": "\u5e73\u9762\u9762\u79ef", "unit": "m\u00b2", "desc_zh": "\u5e73\u9762\u7684\u6d78\u6ca1\u9762\u79ef"}
        },
        "output": {"h_cp": {"label_zh": "\u538b\u529b\u4e2d\u5fc3\u6df1\u5ea6", "unit": "m"}},
        "application_zh": "\u538b\u529b\u4e2d\u5fc3\u4f4d\u7f6e\u662f\u6c34\u575d\u95f8\u95e8\u5f00\u542f\u529b\u77e9\u8ba1\u7b97\u548c\u6d41\u4f53\u5bb9\u5668\u52a0\u52b2\u7ed3\u6784\u8bbe\u8ba1\u7684\u5173\u952e\u53c2\u6570"
    },

    "buoyancy": {
        "name_zh": "\u6d6e\u529b\uff08\u963f\u57fa\u7c73\u5fb7\u539f\u7406\uff09",
        "desc_zh": "\u8ba1\u7b97\u7269\u4f53\u5728\u6d41\u4f53\u4e2d\u6240\u53d7\u7684\u6d6e\u529b",
        "latex": r"F_b = \rho_f g V_{\text{disp}}",
        "inputs": {
            "rho_fluid":   {"label_zh": "\u6d41\u4f53\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"},
            "g":           {"label_zh": "\u91cd\u529b\u52a0\u901f\u5ea6", "unit": "m/s\u00b2", "desc_zh": "\u91cd\u529b\u52a0\u901f\u5ea6"},
            "V_displaced": {"label_zh": "\u6392\u5f00\u4f53\u79ef", "unit": "m\u00b3", "desc_zh": "\u7269\u4f53\u6392\u5f00\u6d41\u4f53\u7684\u4f53\u79ef"}
        },
        "output": {"F_b": {"label_zh": "\u6d6e\u529b", "unit": "N"}},
        "application_zh": "\u8230\u8239\u6d6e\u6027\u8bbe\u8ba1\u3001\u6d6e\u5b50\u6d41\u91cf\u8ba1\u6807\u5b9a\u548c\u6f5c\u6c34\u5668\u538b\u8f7d\u6c34\u8231\u6d6e\u529b\u8ba1\u7b97\u7684\u7406\u8bba\u57fa\u7840"
    },

    "metacenter": {
        "name_zh": "\u7a33\u5fc3\u9ad8\u5ea6",
        "desc_zh": "\u8ba1\u7b97\u6d6e\u4f53\u7a33\u5fc3\u9ad8\u5ea6\uff0c\u5224\u65ad\u6d6e\u4f53\u7a33\u5b9a\u6027",
        "latex": r"\text{GM} = \frac{I_{\text{wl}}}{V_{\text{disp}}} - \text{BG}",
        "inputs": {
            "I_waterline": {"label_zh": "\u6c34\u7ebf\u9762\u60ef\u6027\u77e9", "unit": "m\u2074", "desc_zh": "\u6d6e\u4f53\u6c34\u7ebf\u9762\u5bf9\u7eb5\u5411\u8f74\u7684\u9762\u79ef\u60ef\u6027\u77e9"},
            "V_displaced": {"label_zh": "\u6392\u5f00\u4f53\u79ef", "unit": "m\u00b3", "desc_zh": "\u6d6e\u4f53\u6392\u5f00\u6d41\u4f53\u7684\u4f53\u79ef"},
            "BG":          {"label_zh": "\u6d6e\u5fc3-\u91cd\u5fc3\u8ddd", "unit": "m", "desc_zh": "\u6d6e\u5fc3\u5230\u91cd\u5fc3\u7684\u5782\u76f4\u8ddd\u79bb\uff0c\u9ed8\u8ba40"}
        },
        "output": {"GM": {"label_zh": "\u7a33\u5fc3\u9ad8\u5ea6", "unit": "m"}},
        "application_zh": "\u8230\u8239\u7a33\u6027\u8bbe\u8ba1\u7684\u6838\u5fc3\u6307\u6807\uff0cGM>0\u8868\u793a\u7a33\u5b9a\uff0c\u8d8a\u5927\u8d8a\u7a33\uff1b\u8d1f\u503c\u8868\u793a\u503e\u8986\u98ce\u9669\uff0c\u5fc5\u987b\u91cd\u65b0\u8bbe\u8ba1\u538b\u8f7d\u65b9\u6848"
    },

    "tank_height": {
        "name_zh": "\u50a8\u7f50\u6db2\u4f4d\u9ad8\u5ea6",
        "desc_zh": "\u6839\u636e\u6db2\u4f53\u8d28\u91cf\u548c\u50a8\u7f50\u622a\u9762\u79ef\u8ba1\u7b97\u6db2\u4f4d\u9ad8\u5ea6",
        "latex": r"h = \frac{m}{\rho A}",
        "inputs": {
            "mass": {"label_zh": "\u6db2\u4f53\u8d28\u91cf", "unit": "kg", "desc_zh": "\u50a8\u7f50\u5185\u6db2\u4f53\u7684\u603b\u8d28\u91cf"},
            "rho":  {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6db2\u4f53\u5bc6\u5ea6"},
            "area": {"label_zh": "\u50a8\u7f50\u622a\u9762\u79ef", "unit": "m\u00b2", "desc_zh": "\u50a8\u7f50\u7684\u6c34\u5e73\u622a\u9762\u79ef"}
        },
        "output": {"h": {"label_zh": "\u6db2\u4f4d\u9ad8\u5ea6", "unit": "m"}},
        "application_zh": "\u7528\u4e8e\u71c3\u6599\u50a8\u7f50\u6db2\u4f4d\u76d1\u6d4b\u3001\u5316\u5de5\u53cd\u5e94\u91dc\u6599\u4f4d\u63a7\u5236\u548c\u706b\u7bad\u63a8\u8fdb\u5242\u50a8\u7bb1\u6d88\u8017\u91cf\u5b9e\u65f6\u8ba1\u7b97"
    },

    "capillary_rise": {
        "name_zh": "\u6bdb\u7ec6\u4e0a\u5347\u9ad8\u5ea6",
        "desc_zh": "\u8ba1\u7b97\u6db2\u4f53\u5728\u7ec6\u7ba1\u4e2d\u7684\u6bdb\u7ec6\u4e0a\u5347\u9ad8\u5ea6",
        "latex": r"h = \frac{2\sigma \cos\theta}{\rho g R}",
        "inputs": {
            "sigma": {"label_zh": "\u8868\u9762\u5f20\u529b\u7cfb\u6570", "unit": "N/m", "desc_zh": "\u6db2\u4f53\u8868\u9762\u5f20\u529b\u7cfb\u6570"},
            "theta": {"label_zh": "\u63a5\u89e6\u89d2", "unit": "\u00b0", "desc_zh": "\u6db2\u4f53\u4e0e\u7ba1\u58c1\u7684\u63a5\u89e6\u89d2"},
            "rho":   {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6db2\u4f53\u5bc6\u5ea6"},
            "g":     {"label_zh": "\u91cd\u529b\u52a0\u901f\u5ea6", "unit": "m/s\u00b2", "desc_zh": "\u91cd\u529b\u52a0\u901f\u5ea6"},
            "R":     {"label_zh": "\u6bdb\u7ec6\u7ba1\u534a\u5f84", "unit": "m", "desc_zh": "\u7ec6\u7ba1\u7684\u5185\u534a\u5f84"}
        },
        "output": {"h": {"label_zh": "\u6bdb\u7ec6\u4e0a\u5347\u9ad8\u5ea6", "unit": "m"}},
        "application_zh": "\u5728\u5fae\u7ec6\u7ba1\u9053\u3001\u591a\u5b54\u4ecb\u8d28\u6e17\u6d41\u548c\u71c3\u6cb9\u6bdb\u7ec6\u8f93\u9001\u4e2d\u91cd\u8981\uff0c\u5c24\u5176\u5728\u5fae\u91cd\u529b\u73af\u5883\u4e0b\u6210\u4e3a\u4e3b\u5bfc\u6d41\u52a8\u673a\u5236"
    },

    # ====== Category 3: Continuity & Bernoulli (10) ======

    "continuity": {
        "name_zh": "\u8fde\u7eed\u6027\u65b9\u7a0b",
        "desc_zh": "\u6839\u636e\u8d28\u91cf\u5b88\u6046\u8ba1\u7b97\u53d8\u622a\u9762\u540e\u7684\u6d41\u901f",
        "latex": r"V_2 = \frac{A_1 V_1}{A_2}",
        "inputs": {
            "A1": {"label_zh": "\u5165\u53e3\u622a\u9762\u79ef", "unit": "m\u00b2", "desc_zh": "\u7ba1\u9053\u5165\u53e3\u622a\u9762\u79ef"},
            "V1": {"label_zh": "\u5165\u53e3\u901f\u5ea6", "unit": "m/s", "desc_zh": "\u5165\u53e3\u622a\u9762\u5904\u7684\u5e73\u5747\u6d41\u901f"},
            "A2": {"label_zh": "\u51fa\u53e3\u622a\u9762\u79ef", "unit": "m\u00b2", "desc_zh": "\u7ba1\u9053\u51fa\u53e3\u622a\u9762\u79ef"}
        },
        "output": {"V2": {"label_zh": "\u51fa\u53e3\u901f\u5ea6", "unit": "m/s"}},
        "application_zh": "\u6d41\u91cf\u5b88\u6046\u662f\u7ba1\u9053\u8bbe\u8ba1\u548c\u6d41\u91cf\u8ba1\u7684\u57fa\u672c\u539f\u7406\uff0c\u5e7f\u6cdb\u5e94\u7528\u4e8e\u55b7\u5634\u901f\u5ea6\u8ba1\u7b97\u3001\u7ba1\u5f84\u9009\u578b\u548c\u6d41\u91cf\u5206\u914d\u8bbe\u8ba1"
    },

    "bernoulli_total_pressure": {
        "name_zh": "\u4f2f\u52aa\u5229\u603b\u538b",
        "desc_zh": "\u8ba1\u7b97\u6d41\u7ebf\u4e0a\u4efb\u610f\u70b9\u7684\u603b\u538b\uff08\u9759\u538b+\u52a8\u538b+\u4f4d\u538b\uff09",
        "latex": r"P_{\text{total}} = P + \frac{1}{2}\rho V^2 + \rho g z",
        "inputs": {
            "P":   {"label_zh": "\u9759\u538b", "unit": "Pa", "desc_zh": "\u6d41\u4f53\u9759\u538b"},
            "rho": {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"},
            "V":   {"label_zh": "\u901f\u5ea6", "unit": "m/s", "desc_zh": "\u6d41\u4f53\u901f\u5ea6"},
            "z":   {"label_zh": "\u9ad8\u5ea6", "unit": "m", "desc_zh": "\u53c2\u8003\u9ad8\u5ea6\uff0c\u9ed8\u8ba40"},
            "g":   {"label_zh": "\u91cd\u529b\u52a0\u901f\u5ea6", "unit": "m/s\u00b2", "desc_zh": "\u91cd\u529b\u52a0\u901f\u5ea6"}
        },
        "output": {"P_total": {"label_zh": "\u4f2f\u52aa\u5229\u603b\u538b", "unit": "Pa"}},
        "application_zh": "\u4f2f\u52aa\u5229\u603b\u538b\u5728\u7406\u60f3\u6d41\u52a8\u4e2d\u6cbf\u6d41\u7ebf\u4fdd\u6301\u6052\u5b9a\uff0c\u662f\u8bbe\u8ba1\u98de\u673a\u7a7a\u901f\u7ba1(Pitot\u7ba1)\u3001\u6587\u4e18\u91cc\u7ba1\u548c\u55b7\u5634\u6d41\u91cf\u8ba1\u7684\u7406\u8bba\u57fa\u7840"
    },

    "bernoulli_velocity": {
        "name_zh": "\u4f2f\u52aa\u5229\u6d41\u901f",
        "desc_zh": "\u7531\u4e24\u70b9\u538b\u5dee\u548c\u9ad8\u5ea6\u5dee\u8ba1\u7b97\u6d41\u4f53\u901f\u5ea6",
        "latex": r"V_2 = \sqrt{\frac{2(P_1-P_2)}{\rho} + 2g(z_1-z_2) + V_1^2}",
        "inputs": {
            "P1": {"label_zh": "\u70b9\u00b9\u538b\u529b", "unit": "Pa", "desc_zh": "\u4e0a\u6e38\u6d4b\u70b9\u538b\u529b"},
            "P2": {"label_zh": "\u70b9\u00b2\u538b\u529b", "unit": "Pa", "desc_zh": "\u4e0b\u6e38\u6d4b\u70b9\u538b\u529b"},
            "rho":{"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"},
            "z1": {"label_zh": "\u70b9\u00b9\u9ad8\u5ea6", "unit": "m", "desc_zh": "\u4e0a\u6e38\u6d4b\u70b9\u9ad8\u5ea6"},
            "z2": {"label_zh": "\u70b9\u00b2\u9ad8\u5ea6", "unit": "m", "desc_zh": "\u4e0b\u6e38\u6d4b\u70b9\u9ad8\u5ea6"},
            "V1": {"label_zh": "\u70b9\u00b9\u901f\u5ea6", "unit": "m/s", "desc_zh": "\u4e0a\u6e38\u6d4b\u70b9\u901f\u5ea6"},
            "g":  {"label_zh": "\u91cd\u529b\u52a0\u901f\u5ea6", "unit": "m/s\u00b2", "desc_zh": "\u91cd\u529b\u52a0\u901f\u5ea6"}
        },
        "output": {"V2": {"label_zh": "\u70b9\u00b2\u901f\u5ea6", "unit": "m/s"}},
        "application_zh": "\u901a\u8fc7\u6d4b\u91cf\u538b\u5dee\u53cd\u63a8\u6d41\u901f\uff0c\u662f\u6d41\u91cf\u8ba1\u3001\u98ce\u901f\u4eea\u548c\u5de5\u4e1a\u6d41\u901f\u4f20\u611f\u5668\u7684\u6838\u5fc3\u539f\u7406"
    },

    "bernoulli_dp": {
        "name_zh": "\u4f2f\u52aa\u5229\u538b\u964d",
        "desc_zh": "\u8ba1\u7b97\u7406\u60f3\u6d41\u52a8\u4e2d\u901f\u5ea6\u53d8\u5316\u5f15\u8d77\u7684\u538b\u529b\u53d8\u5316",
        "latex": r"\Delta P_{\text{ideal}} = \frac{1}{2}\rho(V_2^2 - V_1^2) + \rho g(z_2 - z_1)",
        "inputs": {
            "rho": {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"},
            "V1":  {"label_zh": "\u5165\u53e3\u901f\u5ea6", "unit": "m/s", "desc_zh": "\u5165\u53e3\u622a\u9762\u901f\u5ea6"},
            "V2":  {"label_zh": "\u51fa\u53e3\u901f\u5ea6", "unit": "m/s", "desc_zh": "\u51fa\u53e3\u622a\u9762\u901f\u5ea6"},
            "z1":  {"label_zh": "\u5165\u53e3\u9ad8\u5ea6", "unit": "m", "desc_zh": "\u5165\u53e3\u9ad8\u7a0b"},
            "z2":  {"label_zh": "\u51fa\u53e3\u9ad8\u5ea6", "unit": "m", "desc_zh": "\u51fa\u53e3\u9ad8\u7a0b"},
            "g":   {"label_zh": "\u91cd\u529b\u52a0\u901f\u5ea6", "unit": "m/s\u00b2", "desc_zh": "\u91cd\u529b\u52a0\u901f\u5ea6"}
        },
        "output": {"dP": {"label_zh": "\u7406\u60f3\u538b\u964d", "unit": "Pa"}},
        "application_zh": "\u7528\u4e8e\u55b7\u7ba1\u3001\u6269\u538b\u7ba1\u548c\u5f15\u5c04\u5668\u8bbe\u8ba1\u4e2d\u7684\u538b\u529b\u53d8\u5316\u9884\u6d4b\uff0c\u662f\u7406\u60f3\u60c5\u51b5\u4e0b\u7684\u57fa\u51c6\u53c2\u8003\u503c"
    },

    "energy_eq": {
        "name_zh": "\u80fd\u91cf\u65b9\u7a0b\uff08\u5de5\u7a0b\u4f2f\u52aa\u5229\uff09",
        "desc_zh": "\u5305\u542b\u6cf5\u3001\u6c34\u8f6e\u673a\u548c\u635f\u5931\u7684\u5b9e\u9645\u80fd\u91cf\u65b9\u7a0b",
        "latex": r"h_p - h_t - h_L = \Delta z + \frac{\Delta V^2}{2g} + \frac{\Delta P}{\rho g}",
        "inputs": {
            "h_pump":   {"label_zh": "\u6cf5\u626c\u7a0b", "unit": "m", "desc_zh": "\u6cf5\u63d0\u4f9b\u7684\u626c\u7a0b"},
            "h_turbine":{"label_zh": "\u6c34\u8f6e\u673a\u63d0\u53d6\u626c\u7a0b", "unit": "m", "desc_zh": "\u6c34\u8f6e\u673a\u63d0\u53d6\u7684\u626c\u7a0b"},
            "h_loss":   {"label_zh": "\u635f\u5931\u626c\u7a0b", "unit": "m", "desc_zh": "\u7cfb\u7edf\u603b\u6c34\u5934\u635f\u5931"},
            "z1":       {"label_zh": "\u5165\u53e3\u9ad8\u5ea6", "unit": "m", "desc_zh": "\u5165\u53e3\u622a\u9762\u9ad8\u7a0b"},
            "z2":       {"label_zh": "\u51fa\u53e3\u9ad8\u5ea6", "unit": "m", "desc_zh": "\u51fa\u53e3\u622a\u9762\u9ad8\u7a0b"},
            "V1":       {"label_zh": "\u5165\u53e3\u901f\u5ea6", "unit": "m/s", "desc_zh": "\u5165\u53e3\u5e73\u5747\u901f\u5ea6"},
            "V2":       {"label_zh": "\u51fa\u53e3\u901f\u5ea6", "unit": "m/s", "desc_zh": "\u51fa\u53e3\u5e73\u5747\u901f\u5ea6"},
            "P1":       {"label_zh": "\u5165\u53e3\u538b\u529b", "unit": "Pa", "desc_zh": "\u5165\u53e3\u622a\u9762\u538b\u529b"},
            "P2":       {"label_zh": "\u51fa\u53e3\u538b\u529b", "unit": "Pa", "desc_zh": "\u51fa\u53e3\u622a\u9762\u538b\u529b"},
            "rho":      {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"},
            "g":        {"label_zh": "\u91cd\u529b\u52a0\u901f\u5ea6", "unit": "m/s\u00b2", "desc_zh": "\u91cd\u529b\u52a0\u901f\u5ea6"}
        },
        "output": {"balance": {"label_zh": "\u80fd\u91cf\u5e73\u8861\u6b8b\u5dee", "unit": "m"}},
        "application_zh": "\u5de5\u7a0b\u5b9e\u9645\u7cfb\u7edf\u4e2d\u6cf5\u7ad9\u3001\u6c34\u7535\u7ad9\u548c\u4f9b\u6c34\u7ba1\u7f51\u7684\u80fd\u91cf\u5e73\u8861\u5206\u6790\uff0c\u662f\u7cfb\u7edf\u65b9\u6848\u8bbe\u8ba1\u7684\u57fa\u672c\u65b9\u7a0b"
    },

    "momentum_force": {
        "name_zh": "\u52a8\u91cf\u529b",
        "desc_zh": "\u8ba1\u7b97\u6d41\u4f53\u52a8\u91cf\u53d8\u5316\u4ea7\u751f\u7684\u4f5c\u7528\u529b",
        "latex": r"F = \rho Q (\beta V_{\text{out}} - \beta V_{\text{in}})",
        "inputs": {
            "rho":   {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"},
            "Q":     {"label_zh": "\u4f53\u79ef\u6d41\u91cf", "unit": "m\u00b3/s", "desc_zh": "\u4f53\u79ef\u6d41\u91cf"},
            "V_out": {"label_zh": "\u51fa\u53e3\u901f\u5ea6", "unit": "m/s", "desc_zh": "\u63a7\u5236\u4f53\u51fa\u53e3\u901f\u5ea6"},
            "V_in":  {"label_zh": "\u5165\u53e3\u901f\u5ea6", "unit": "m/s", "desc_zh": "\u63a7\u5236\u4f53\u5165\u53e3\u901f\u5ea6"},
            "beta":  {"label_zh": "\u52a8\u91cf\u4fee\u6b63\u7cfb\u6570", "unit": "\u65e0\u91cf\u7eb2", "desc_zh": "\u52a8\u91cf\u4fee\u6b63\u7cfb\u6570\uff0c\u5c42\u6d41\u22481.33\uff0c\u6e4d\u6d41\u22481.02"}
        },
        "output": {"F": {"label_zh": "\u52a8\u91cf\u4f5c\u7528\u529b", "unit": "N"}},
        "application_zh": "\u7528\u4e8e\u8ba1\u7b97\u55b7\u6c14\u53e3\u3001\u706b\u7bad\u53d1\u52a8\u673a\u55b7\u7ba1\u3001\u5f2f\u7ba1\u652f\u67b6\u53d7\u529b\u548c\u6d41\u4f53\u8f6c\u5411\u88c5\u7f6e\u7684\u4f5c\u7528\u529b"
    },

    "cavitation_number": {
        "name_zh": "\u7a7a\u5316\u6570",
        "desc_zh": "\u8bc4\u4f30\u6d41\u4f53\u53d1\u751f\u7a7a\u5316\u7684\u98ce\u9669\u7a0b\u5ea6",
        "latex": r"\sigma = \frac{P - P_v}{\frac{1}{2}\rho V^2}",
        "inputs": {
            "P":   {"label_zh": "\u5f53\u5730\u9759\u538b", "unit": "Pa", "desc_zh": "\u6d41\u4f53\u5f53\u5730\u9759\u538b"},
            "P_v": {"label_zh": "\u84b8\u6c7d\u538b", "unit": "Pa", "desc_zh": "\u5de5\u4f5c\u6e29\u5ea6\u4e0b\u6d41\u4f53\u7684\u84b8\u6c7d\u538b"},
            "rho": {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"},
            "V":   {"label_zh": "\u6d41\u901f", "unit": "m/s", "desc_zh": "\u7279\u5f81\u901f\u5ea6"}
        },
        "output": {"sigma": {"label_zh": "\u7a7a\u5316\u6570", "unit": "\u65e0\u91cf\u7eb2"}},
        "application_zh": "\sigma<1\u65f6\u7a7a\u5316\u53ef\u80fd\u53d1\u751f\uff0c\u662f\u6cf5\u7ad9\u3001\u87ba\u65cb\u6868\u548c\u9600\u95e8\u7a7a\u5316\u9884\u9632\u7684\u5173\u952e\u65e0\u91cf\u7eb2\u5224\u636e\uff0c\u76f4\u63a5\u5f71\u54cd\u8bbe\u5907\u5bff\u547d"
    },

    "stagnation": {
        "name_zh": "\u6ede\u6b62\u538b\u529b",
        "desc_zh": "\u8ba1\u7b97\u6d41\u4f53\u6ede\u6b62\u70b9\u5904\u7684\u603b\u538b\u529b",
        "latex": r"P_0 = P_{\infty} + \frac{1}{2}\rho V_{\infty}^2",
        "inputs": {
            "P_static": {"label_zh": "\u6765\u6d41\u9759\u538b", "unit": "Pa", "desc_zh": "\u81ea\u7531\u6d41\u7684\u9759\u538b"},
            "rho":      {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"},
            "V":        {"label_zh": "\u6765\u6d41\u901f\u5ea6", "unit": "m/s", "desc_zh": "\u81ea\u7531\u6d41\u901f\u5ea6"}
        },
        "output": {"P0": {"label_zh": "\u6ede\u6b62\u538b\u529b", "unit": "Pa"}},
        "application_zh": "\u6ede\u6b62\u538b\u662fPitot\u7ba1\u6d4b\u901f\u7684\u6838\u5fc3\u53c2\u6570\uff0c\u5728\u822a\u7a7a\u7a7a\u901f\u6d4b\u91cf\u3001\u98ce\u6d1e\u6807\u5b9a\u548c\u53d1\u52a8\u673a\u8fdb\u6c14\u8bbe\u8ba1\u4e2d\u4e0d\u53ef\u6216\u7f3a"
    },

    "volume_flow": {
        "name_zh": "\u4f53\u79ef\u6d41\u91cf",
        "desc_zh": "\u8ba1\u7b97\u901a\u8fc7\u7ed9\u5b9a\u622a\u9762\u7684\u4f53\u79ef\u6d41\u91cf",
        "latex": r"Q = A V",
        "inputs": {
            "A": {"label_zh": "\u6d41\u901a\u622a\u9762\u79ef", "unit": "m\u00b2", "desc_zh": "\u7ba1\u9053\u622a\u9762\u79ef"},
            "V": {"label_zh": "\u5e73\u5747\u6d41\u901f", "unit": "m/s", "desc_zh": "\u622a\u9762\u4e0a\u7684\u5e73\u5747\u6d41\u901f"}
        },
        "output": {"Q": {"label_zh": "\u4f53\u79ef\u6d41\u91cf", "unit": "m\u00b3/s"}},
        "application_zh": "\u6700\u57fa\u672c\u7684\u6d41\u91cf\u8ba1\u7b97\u516c\u5f0f\uff0c\u6240\u6709\u6d41\u4f53\u8f93\u9001\u7cfb\u7edf\u8bbe\u8ba1\u3001\u6cf5\u9009\u578b\u548c\u6d41\u91cf\u8ba1\u6821\u9a8c\u7684\u8d77\u70b9"
    },

    "mass_flow": {
        "name_zh": "\u8d28\u91cf\u6d41\u91cf",
        "desc_zh": "\u8ba1\u7b97\u5355\u4f4d\u65f6\u95f4\u901a\u8fc7\u622a\u9762\u7684\u6d41\u4f53\u8d28\u91cf",
        "latex": r"\dot{m} = \rho Q",
        "inputs": {
            "rho": {"label_zh": "\u5bc6\u5ea6", "unit": "kg/m\u00b3", "desc_zh": "\u6d41\u4f53\u5bc6\u5ea6"},
            "Q":   {"label_zh": "\u4f53\u79ef\u6d41\u91cf", "unit": "m\u00b3/s", "desc_zh": "\u4f53\u79ef\u6d41\u91cf"}
        },
        "output": {"m_dot": {"label_zh": "\u8d28\u91cf\u6d41\u91cf", "unit": "kg/s"}},
        "application_zh": "\u8d28\u91cf\u6d41\u91cf\u662f\u53d1\u52a8\u673a\u63a8\u529b\u8ba1\u7b97\u3001\u71c3\u70e7\u7cfb\u7edf\u8bbe\u8ba1\u548c\u5316\u5de5\u8f93\u9001\u63a7\u5236\u7684\u6838\u5fc3\u53c2\u6570\uff0c\u6bd4\u4f53\u79ef\u6d41\u91cf\u66f4\u80fd\u53cd\u6620\u7269\u8d28\u8f93\u9001\u80fd\u529b"
    },

    "reynolds": {
        "name_zh": "雷诺数",
        "desc_zh": "计算流体惯性力与粘性力之比，判断流态",
        "latex": r"\text{Re} = \frac{\rho V D}{\mu}",
        "inputs": {
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "V":   {"label_zh": "特征速度", "unit": "m/s", "desc_zh": "管道平均流速"},
            "D":   {"label_zh": "特征长度", "unit": "m", "desc_zh": "管道内径"},
            "mu":  {"label_zh": "动力粘度", "unit": "Pa·s", "desc_zh": "流体动力粘度"}
        },
        "output": {"Re": {"label_zh": "雷诺数", "unit": "无量纲"}},
        "application_zh": "Re<2300层流、2300<Re<4000过渡区、Re>4000湍流。是所有管道流动计算的起点，直接决定摩擦系数选用和压降计算方法"
    },

    "reynolds_nu": {
        "name_zh": "雷诺数(运动粘度)",
        "desc_zh": "通过运动粘度计算雷诺数",
        "latex": r"\text{Re} = \frac{V D}{\nu}",
        "inputs": {
            "V":  {"label_zh": "特征速度", "unit": "m/s", "desc_zh": "管道平均流速"},
            "D":  {"label_zh": "特征长度", "unit": "m", "desc_zh": "管道内径"},
            "nu": {"label_zh": "运动粘度", "unit": "m²/s", "desc_zh": "流体运动粘度"}
        },
        "output": {"Re": {"label_zh": "雷诺数", "unit": "无量纲"}},
        "application_zh": "当已知运动粘度（如查表获得）时使用此公式，在航空燃油、液压油等工程计算中更为便捷"
    },

    "f_laminar": {
        "name_zh": "层流摩擦系数",
        "desc_zh": "计算层流状态下的Darcy摩擦系数",
        "latex": r"f = \frac{64}{\text{Re}}",
        "inputs": {
            "Re": {"label_zh": "雷诺数", "unit": "无量纲", "desc_zh": "管道雷诺数，需<2300"}
        },
        "output": {"f": {"label_zh": "Darcy摩擦系数", "unit": "无量纲"}},
        "application_zh": "仅适用于层流(Re<2300)，f与Re成反比，不依赖壁面粗糙度。是管道压降计算最简单的摩擦系数模型"
    },

    "f_blasius": {
        "name_zh": "Blasius摩擦系数",
        "desc_zh": "光滑管湍流摩擦系数的Blasius经验公式",
        "latex": r"f = 0.316\,\text{Re}^{-0.25}",
        "inputs": {
            "Re": {"label_zh": "雷诺数", "unit": "无量纲", "desc_zh": "管道雷诺数，适用范围4000<Re<10\u2075"}
        },
        "output": {"f": {"label_zh": "Darcy摩擦系数", "unit": "无量纲"}},
        "application_zh": "Blasius公式是光滑管湍流的经典经验公式，适用于Re<10\u2075，计算简便，广泛用于初步设计和教学场景"
    },

    "f_colebrook": {
        "name_zh": "Colebrook摩擦系数",
        "desc_zh": "Colebrook-White公式的迭代求解，湍流摩擦系数",
        "latex": r"\frac{1}{\sqrt{f}} = -2.0\log_{10}\!\left(\frac{\varepsilon/D}{3.7} + \frac{2.51}{\text{Re}\sqrt{f}}\right)",
        "inputs": {
            "Re":      {"label_zh": "雷诺数", "unit": "无量纲", "desc_zh": "管道雷诺数"},
            "epsilon": {"label_zh": "绝对粗糙度", "unit": "mm", "desc_zh": "管道内壁绝对粗糙度"},
            "D":       {"label_zh": "管道内径", "unit": "m", "desc_zh": "管道内径（需与粗糙度单位统一）"}
        },
        "output": {"f": {"label_zh": "Darcy摩擦系数", "unit": "无量纲"}},
        "application_zh": "Colebrook-White公式是最广泛使用的湍流摩擦系数模型，覆盖光滑管到完全粗糙管全范围，迭代30次精度可达1e-10。是工程管道设计的黄金标准"
    },

    "f_swamee_jain": {
        "name_zh": "Swamee-Jain摩擦系数",
        "desc_zh": "Colebrook公式的显式近似，无需迭代",
        "latex": r"f = \frac{0.25}{\left[\log_{10}\!\left(\frac{\varepsilon/D}{3.7} + \frac{5.74}{\text{Re}^{0.9}}\right)\right]^2}",
        "inputs": {
            "Re":      {"label_zh": "雷诺数", "unit": "无量纲", "desc_zh": "管道雷诺数"},
            "epsilon": {"label_zh": "绝对粗糙度", "unit": "mm", "desc_zh": "管道内壁绝对粗糙度"},
            "D":       {"label_zh": "管道内径", "unit": "m", "desc_zh": "管道内径"}
        },
        "output": {"f": {"label_zh": "Darcy摩擦系数", "unit": "无量纲"}},
        "application_zh": "Swamee-Jain是Colebrook的高精度显式近似（误差<1%），无需迭代，特别适合自动化计算和实时控制系统"
    },

    "darcy_hf": {
        "name_zh": "Darcy-Weisbach沿程水头损失",
        "desc_zh": "计算管道沿程摩擦水头损失",
        "latex": r"h_f = \frac{f L V^2}{D \cdot 2g}",
        "inputs": {
            "f": {"label_zh": "Darcy摩擦系数", "unit": "无量纲", "desc_zh": "Darcy摩擦系数"},
            "L": {"label_zh": "管道长度", "unit": "m", "desc_zh": "管道总长度"},
            "D": {"label_zh": "管道内径", "unit": "m", "desc_zh": "管道内径"},
            "V": {"label_zh": "平均流速", "unit": "m/s", "desc_zh": "管道截面平均流速"},
            "g": {"label_zh": "重力加速度", "unit": "m/s²", "desc_zh": "重力加速度"}
        },
        "output": {"hf": {"label_zh": "沿程水头损失", "unit": "m"}},
        "application_zh": "Darcy-Weisbach是最准确、最通用的管道摩擦损失计算公式，适用所有流体（液/气）、所有流态，是管道系统工程设计的核心公式"
    },

    "darcy_dp": {
        "name_zh": "Darcy-Weisbach沿程压降",
        "desc_zh": "计算管道沿程摩擦压力损失",
        "latex": r"\Delta P = f\frac{L}{D}\frac{1}{2}\rho V^2",
        "inputs": {
            "f":   {"label_zh": "Darcy摩擦系数", "unit": "无量纲", "desc_zh": "Darcy摩擦系数"},
            "L":   {"label_zh": "管道长度", "unit": "m", "desc_zh": "管道总长度"},
            "D":   {"label_zh": "管道内径", "unit": "m", "desc_zh": "管道内径"},
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "V":   {"label_zh": "平均流速", "unit": "m/s", "desc_zh": "管道平均流速"}
        },
        "output": {"dP": {"label_zh": "沿程压降", "unit": "Pa"}},
        "application_zh": "以压力单位表达的沿程损失，直接用于泵扬程选型、管道承压设计和管网水力平衡计算"
    },

    "hazen_williams": {
        "name_zh": "Hazen-Williams流速",
        "desc_zh": "给排水工程常用的经验流速公式",
        "latex": r"V = 0.849\,C\,R_h^{0.63}\,S^{0.54}",
        "inputs": {
            "C":   {"label_zh": "Hazen-Williams系数", "unit": "无量纲", "desc_zh": "管材系数，新钢管≈120-140"},
            "R_h": {"label_zh": "水力半径", "unit": "m", "desc_zh": "管道水力半径"},
            "S":   {"label_zh": "水力坡度", "unit": "m/m", "desc_zh": "单位长度的水头损失"}
        },
        "output": {"V": {"label_zh": "平均流速", "unit": "m/s"}},
        "application_zh": "Hazen-Williams是美国给排水工程标准公式，适用于常温水的满管流动，计算简便但限于D>50mm、V<3m/s的工况"
    },

    "hydraulic_radius": {
        "name_zh": "水力半径",
        "desc_zh": "计算非圆形截面管道的水力半径",
        "latex": r"R_h = \frac{A}{P_w}",
        "inputs": {
            "A":       {"label_zh": "过流截面积", "unit": "m²", "desc_zh": "管道过流截面积"},
            "P_wetted":{"label_zh": "湿周", "unit": "m", "desc_zh": "流体与管壁接触的周界长度"}
        },
        "output": {"R_h": {"label_zh": "水力半径", "unit": "m"}},
        "application_zh": "水力半径是处理非圆形截面管道（矩形风管、椭圆形管）的等效参数，将复杂截面转化为等效圆形管道进行分析"
    },

    "hydraulic_diameter": {
        "name_zh": "水力直径",
        "desc_zh": "计算非圆形截面的等效水力直径",
        "latex": r"D_h = \frac{4A}{P_w}",
        "inputs": {
            "A":       {"label_zh": "过流截面积", "unit": "m²", "desc_zh": "管道过流截面积"},
            "P_wetted":{"label_zh": "湿周", "unit": "m", "desc_zh": "管壁接触周界长度"}
        },
        "output": {"D_h": {"label_zh": "水力直径", "unit": "m"}},
        "application_zh": "水力直径使雷诺数和摩擦系数计算可扩展到任意截面形状，在换热气通道设计、微通道散热器和航空航天紧凑式换热器中极为重要"
    },

    "minor_loss_head": {
        "name_zh": "局部水头损失",
        "desc_zh": "计算阀门、弯头等管件的局部水头损失",
        "latex": r"h_m = \frac{K V^2}{2g}",
        "inputs": {
            "K": {"label_zh": "局部损失系数", "unit": "无量纲", "desc_zh": "管件的局部阻力系数"},
            "V": {"label_zh": "管道流速", "unit": "m/s", "desc_zh": "管道内平均流速"},
            "g": {"label_zh": "重力加速度", "unit": "m/s²", "desc_zh": "重力加速度"}
        },
        "output": {"hm": {"label_zh": "局部水头损失", "unit": "m"}},
        "application_zh": "用于叠加阀门、弯头、三通、过滤器等管件的阻力损失，在复杂管网水力计算中与沿程损失合并求总损失"
    },

    "minor_loss_dp": {
        "name_zh": "局部压力损失",
        "desc_zh": "以压力单位计算管件的局部损失",
        "latex": r"\Delta P_m = K \frac{1}{2}\rho V^2",
        "inputs": {
            "K":   {"label_zh": "局部损失系数", "unit": "无量纲", "desc_zh": "管件的局部阻力系数"},
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "V":   {"label_zh": "流速", "unit": "m/s", "desc_zh": "管道内流速"}
        },
        "output": {"dP_m": {"label_zh": "局部压力损失", "unit": "Pa"}},
        "application_zh": "以压力表达的局部损失，便于与沿程压降直接求和，在液压系统、气动系统和阀门管路设计中广泛应用"
    },

    "sudden_expansion": {
        "name_zh": "突然扩大损失",
        "desc_zh": "计算管道截面突然扩大引起的压力损失",
        "latex": r"\Delta P_e = \left(1 - \frac{A_1}{A_2}\right)^2 \cdot \frac{1}{2}\rho V_1^2",
        "inputs": {
            "A1":  {"label_zh": "小管截面积", "unit": "m²", "desc_zh": "扩大前的小管截面积"},
            "A2":  {"label_zh": "大管截面积", "unit": "m²", "desc_zh": "扩大后的大管截面积"},
            "V1":  {"label_zh": "小管流速", "unit": "m/s", "desc_zh": "小管内的平均流速"},
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"}
        },
        "output": {"dP_e": {"label_zh": "扩大压力损失", "unit": "Pa"}},
        "application_zh": "管道突然扩大的损失来源于流动分离和涡流耗散，在扩压管设计时需权衡恢复压力与减小损失的矛盾"
    },

    "sudden_contraction": {
        "name_zh": "突然缩小损失",
        "desc_zh": "计算管道截面突然缩小引起的压力损失",
        "latex": r"\Delta P_c = K_c \cdot \frac{1}{2}\rho V_2^2,\quad K_c \approx 0.5\left(1 - \frac{A_2}{A_1}\right)^{2.5}",
        "inputs": {
            "A1":  {"label_zh": "大管截面积", "unit": "m²", "desc_zh": "缩小前的大管截面积"},
            "A2":  {"label_zh": "小管截面积", "unit": "m²", "desc_zh": "缩小后的小管截面积"},
            "V2":  {"label_zh": "小管流速", "unit": "m/s", "desc_zh": "缩小后小管内的平均流速"},
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"}
        },
        "output": {"dP_c": {"label_zh": "缩小压力损失", "unit": "Pa"}},
        "application_zh": "缩小的损失系数通常小于扩大，但在阀门入口、喷嘴收缩段等位置仍需精确计算以确保设计裕量"
    },

    "equiv_length": {
        "name_zh": "等效长度",
        "desc_zh": "将局部损失折算为等压降的直管长度",
        "latex": r"L_e = \frac{K D}{f}",
        "inputs": {
            "K_total": {"label_zh": "总局部损失系数", "unit": "无量纲", "desc_zh": "所有管件的局部损失系数之和"},
            "D":       {"label_zh": "管道内径", "unit": "m", "desc_zh": "管道内径"},
            "f":       {"label_zh": "Darcy摩擦系数", "unit": "无量纲", "desc_zh": "管道Darcy摩擦系数"}
        },
        "output": {"Le": {"label_zh": "等效长度", "unit": "m"}},
        "application_zh": "等效长度法将复杂的局部损失简化为一截直管，在供水管网、消防系统和长输管道初步估算中非常实用"
    },
    "pipe_bend": {
        "name_zh": "弯头损失",
        "desc_zh": "计算管道弯头引起的局部水头损失",
        "latex": r"h_L = K \frac{V^2}{2g}, \quad K = f(\theta, R/D)",
        "inputs": {
            "V": {"label_zh": "流速", "unit": "m/s", "desc_zh": "管道平均流速"},
            "g": {"label_zh": "重力加速度", "unit": "m/s²", "desc_zh": "重力加速度，默认9.81"}
        },
        "output": {"head_loss": {"label_zh": "弯头水头损失", "unit": "m"}},
        "application_zh": "管道系统中90°弯头、45°弯头等引起的局部阻力损失，取决于弯头角度和曲率半径比"
    },
    "pipe_entrance": {
        "name_zh": "管入口损失",
        "desc_zh": "计算流体从大容器进入管道时的入口损失系数",
        "latex": r"h_L = K \frac{V^2}{2g}, \quad K = 0.5 \text{ (尖锐) } \text{ or } 0.04 \text{ (圆滑)}",
        "inputs": {
            "V": {"label_zh": "流速", "unit": "m/s", "desc_zh": "管道入口平均流速"},
            "g": {"label_zh": "重力加速度", "unit": "m/s²", "desc_zh": "重力加速度，默认9.81"}
        },
        "output": {"head_loss": {"label_zh": "入口水头损失", "unit": "m"}},
        "application_zh": "储罐出口、泵入口等从大容器进入管道的局部损失计算，尖锐入口K=0.5，圆滑入口K=0.04"
    },
    "pipe_exit": {
        "name_zh": "管出口损失",
        "desc_zh": "计算流体从管道流入大容器时的出口损失系数",
        "latex": r"h_L = K \frac{V^2}{2g}, \quad K \approx 1.0",
        "inputs": {
            "V": {"label_zh": "流速", "unit": "m/s", "desc_zh": "管道出口平均流速"},
            "g": {"label_zh": "重力加速度", "unit": "m/s²", "desc_zh": "重力加速度，默认9.81"}
        },
        "output": {"head_loss": {"label_zh": "出口水头损失", "unit": "m"}},
        "application_zh": "管道出口到水池、储罐等大容器的局部损失计算，K值通常取1.0（动能全部耗散）"
    },

    "pipe_exit": {
        "name_zh": "管道出口损失",
        "desc_zh": "计算流体从管道排入大容器时的出口损失",
        "latex": r"\Delta P_{\text{exit}} = K_{\text{exit}} \frac{1}{2}\rho V^2,\quad K_{\text{exit}} \approx 1.0",
        "inputs": {
            "V":   {"label_zh": "出口流速", "unit": "m/s", "desc_zh": "管道出口处流速"},
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "K":   {"label_zh": "出口损失系数", "unit": "无量纲", "desc_zh": "出口损失系数，管道突入大容器≈1.0"}
        },
        "output": {"dP_exit": {"label_zh": "出口压力损失", "unit": "Pa"}},
        "application_zh": "管道出口排入大容器（如储罐、水池）时，所有动能均耗散为损失，K_exit≈1是理论极限值"
    },

    "pipe_entrance": {
        "name_zh": "管道入口损失",
        "desc_zh": "计算流体从大容器进入管道时的入口损失",
        "latex": r"\Delta P_{\text{inlet}} = K_e \frac{1}{2}\rho V^2",
        "inputs": {
            "V":   {"label_zh": "入口流速", "unit": "m/s", "desc_zh": "管道入口处流速"},
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "r_D": {"label_zh": "入口圆角比(r/D)", "unit": "无量纲", "desc_zh": "入口圆角半径与管径之比"}
        },
        "output": {"dP_inlet": {"label_zh": "入口压力损失", "unit": "Pa"}},
        "application_zh": "入口损失取决于入口形状：锐缘Ke≈0.5、稍加圆角Ke≈0.25、喇叭口Ke≈0.03。在泵吸入管设计中减小入口损失至关重要"
    },

    "pipe_bend": {
        "name_zh": "弯头损失",
        "desc_zh": "计算90°或其他角度弯头的局部压力损失",
        "latex": r"\Delta P_{\text{bend}} = K_b \frac{1}{2}\rho V^2,\quad K_b = \left(0.131 + 0.163\left(\frac{D}{R}\right)^{3.5}\right)\frac{\theta}{\pi/2}",
        "inputs": {
            "V":         {"label_zh": "管道流速", "unit": "m/s", "desc_zh": "管道内平均流速"},
            "rho":       {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "R_bend":    {"label_zh": "弯曲半径", "unit": "m", "desc_zh": "弯头中心线弯曲半径"},
            "D":         {"label_zh": "管道内径", "unit": "m", "desc_zh": "管道内径"},
            "theta_deg": {"label_zh": "弯曲角度", "unit": "°", "desc_zh": "弯头的角度，默认90°"}
        },
        "output": {"dP_bend": {"label_zh": "弯头压力损失", "unit": "Pa"}},
        "application_zh": "弯头损失在航空航天管路中不可忽略，R/D越小损失越大，长半径弯头(R/D>1.5)可大幅降低损失"
    },

    # ====== Category 5: Open Channel Flow (9) ======

    "froude": {
        "name_zh": "弗汝德数",
        "desc_zh": "计算明渠流动的弗汝德数，判断流态",
        "latex": r"\text{Fr} = \frac{V}{\sqrt{g y_h}}",
        "inputs": {
            "V":   {"label_zh": "平均流速", "unit": "m/s", "desc_zh": "明渠断面平均流速"},
            "g":   {"label_zh": "重力加速度", "unit": "m/s²", "desc_zh": "重力加速度"},
            "y_h": {"label_zh": "水力深度", "unit": "m", "desc_zh": "断面过流面积与水面宽度之比"}
        },
        "output": {"Fr": {"label_zh": "弗汝德数", "unit": "无量纲"}},
        "application_zh": "Fr<1缓流、Fr=1临界流、Fr>1急流。弗汝德数是明渠流动和水跃分析的基础判据，也是水工模型实验相似的关键参数"
    },

    "manning_v": {
        "name_zh": "Manning流速",
        "desc_zh": "用Manning公式计算明渠均匀流平均流速",
        "latex": r"V = \frac{1}{n}R_h^{2/3} S^{1/2}",
        "inputs": {
            "n":   {"label_zh": "Manning糙率系数", "unit": "s/m^{1/3}", "desc_zh": "渠道粗糙度系数"},
            "R_h": {"label_zh": "水力半径", "unit": "m", "desc_zh": "渠道断面水力半径"},
            "S":   {"label_zh": "底坡", "unit": "m/m", "desc_zh": "渠道底坡坡度"}
        },
        "output": {"V": {"label_zh": "平均流速", "unit": "m/s"}},
        "application_zh": "Manning公式是全球最广泛使用的明渠均匀流计算公式，适用于河道、排水沟、灌溉渠的流量和断面设计"
    },

    "manning_q": {
        "name_zh": "Manning流量",
        "desc_zh": "用Manning公式直接计算明渠流量",
        "latex": r"Q = \frac{A}{n}R_h^{2/3} S^{1/2}",
        "inputs": {
            "n":   {"label_zh": "Manning糙率系数", "unit": "s/m^{1/3}", "desc_zh": "渠道粗糙度系数"},
            "A":   {"label_zh": "过流截面积", "unit": "m²", "desc_zh": "渠道过流截面积"},
            "R_h": {"label_zh": "水力半径", "unit": "m", "desc_zh": "渠道断面水力半径"},
            "S":   {"label_zh": "底坡", "unit": "m/m", "desc_zh": "渠道底坡坡度"}
        },
        "output": {"Q": {"label_zh": "流量", "unit": "m³/s"}},
        "application_zh": "直接计算明渠排涝能力，在城市排水系统设计、农田灌溉和山洪评估中广泛使用"
    },

    "chezy_v": {
        "name_zh": "Chezy流速",
        "desc_zh": "用Chezy公式计算明渠均匀流速",
        "latex": r"V = C\sqrt{R_h S}",
        "inputs": {
            "C":   {"label_zh": "Chezy系数", "unit": "m^{1/2}/s", "desc_zh": "Chezy粗糙系数"},
            "R_h": {"label_zh": "水力半径", "unit": "m", "desc_zh": "渠道断面水力半径"},
            "S":   {"label_zh": "底坡", "unit": "m/m", "desc_zh": "渠道底坡坡度"}
        },
        "output": {"V": {"label_zh": "平均流速", "unit": "m/s"}},
        "application_zh": "Chezy公式是明渠流动最早的流速公式，与Manning配合使用，在河道整治和水力设计中仍有重要参考价值"
    },

    "critical_depth_rect": {
        "name_zh": "矩形临界水深",
        "desc_zh": "计算矩形断面明渠的临界水深",
        "latex": r"y_c = \left(\frac{Q^2}{g b^2}\right)^{1/3}",
        "inputs": {
            "Q": {"label_zh": "流量", "unit": "m³/s", "desc_zh": "渠道流量"},
            "b": {"label_zh": "渠道宽度", "unit": "m", "desc_zh": "矩形渠道底宽"},
            "g": {"label_zh": "重力加速度", "unit": "m/s²", "desc_zh": "重力加速度"}
        },
        "output": {"yc": {"label_zh": "临界水深", "unit": "m"}},
        "application_zh": "临界水深是明渠流态转换的分界点，在溢洪道、量水堰和水跃位置判断中起关键作用"
    },

    "specific_energy": {
        "name_zh": "断面比能",
        "desc_zh": "计算明渠断面比能",
        "latex": r"E = y + \frac{Q^2}{2g A^2}",
        "inputs": {
            "y":      {"label_zh": "水深", "unit": "m", "desc_zh": "渠道水深"},
            "Q":      {"label_zh": "流量", "unit": "m³/s", "desc_zh": "渠道流量"},
            "A_flow": {"label_zh": "过流截面积", "unit": "m²", "desc_zh": "对应水深的过流截面积"},
            "g":      {"label_zh": "重力加速度", "unit": "m/s²", "desc_zh": "重力加速度"}
        },
        "output": {"E": {"label_zh": "断面比能", "unit": "m"}},
        "application_zh": "断面比能是明渠渐变流水面线分析的核心概念，用于判断壅水/降水曲线走势和渠道过渡段设计"
    },

    "hydraulic_jump_ratio": {
        "name_zh": "水跃共轭水深比",
        "desc_zh": "计算水跃前后的共轭水深比",
        "latex": r"\frac{y_2}{y_1} = \frac{1}{2}\left(\sqrt{1 + 8\text{Fr}_1^2} - 1\right)",
        "inputs": {
            "Fr1": {"label_zh": "跃前弗汝德数", "unit": "无量纲", "desc_zh": "水跃上游断面的弗汝德数，需>1"}
        },
        "output": {"ratio": {"label_zh": "共轭水深比", "unit": "无量纲"}},
        "application_zh": "水跃是明渠急流向缓流转换的强耗能现象，共轭水深比决定消力池长度、护坦厚度等关键设计参数"
    },

    "hydraulic_jump_energy": {
        "name_zh": "水跃能量损失",
        "desc_zh": "计算水跃过程中的能量耗散",
        "latex": r"\Delta E = \frac{(y_2 - y_1)^3}{4 y_1 y_2}",
        "inputs": {
            "y1": {"label_zh": "跃前水深", "unit": "m", "desc_zh": "水跃上游断面水深"},
            "y2": {"label_zh": "跃后水深", "unit": "m", "desc_zh": "水跃下游断面水深"}
        },
        "output": {"dE": {"label_zh": "能量损失", "unit": "m"}},
        "application_zh": "水跃可消除流入下游河道的大部分动能，用于大坝消力池、溢洪道消能和城市排水系统急流减速设计"
    },

    "weir_rect": {
        "name_zh": "矩形薄壁堰流量",
        "desc_zh": "计算矩形薄壁堰的自由出流流量",
        "latex": r"Q = \frac{2}{3}C_d b\sqrt{2g}\,H^{3/2}",
        "inputs": {
            "C_d": {"label_zh": "流量系数", "unit": "无量纲", "desc_zh": "堰的流量系数，受堰高和收缩影响"},
            "b":   {"label_zh": "堰宽", "unit": "m", "desc_zh": "矩形堰口的宽度"},
            "H":   {"label_zh": "堰上水头", "unit": "m", "desc_zh": "堰板上游水面到堰顶的高度"},
            "g":   {"label_zh": "重力加速度", "unit": "m/s²", "desc_zh": "重力加速度"}
        },
        "output": {"Q": {"label_zh": "流量", "unit": "m³/s"}},
        "application_zh": "薄壁堰是最经典的明渠流量测量装置，广泛应用于水工实验室、给排水系统中的流量计量和标定"
    },

    # ====== Category 6: Compressible Flow (12) ======

    "speed_of_sound": {
        "name_zh": "声速",
        "desc_zh": "计算理想气体中的声速",
        "latex": r"a = \sqrt{k R T}",
        "inputs": {
            "k": {"label_zh": "比热比", "unit": "无量纲", "desc_zh": "定压比热与定容比热之比，空气≈1.4"},
            "R": {"label_zh": "气体常数", "unit": "J/(kg·K)", "desc_zh": "特定气体常数，空气=287"},
            "T": {"label_zh": "温度", "unit": "K", "desc_zh": "气体绝对温度"}
        },
        "output": {"a": {"label_zh": "声速", "unit": "m/s"}},
        "application_zh": "声速是可压缩流动的基准速度，马赫数计算的必要条件。在超音速风洞、火箭发动机喷管和高速阀门设计中至关重要"
    },

    "mach": {
        "name_zh": "马赫数",
        "desc_zh": "计算流体速度与当地声速之比",
        "latex": r"\text{Ma} = \frac{V}{a}",
        "inputs": {
            "V": {"label_zh": "流速", "unit": "m/s", "desc_zh": "流体速度"},
            "a": {"label_zh": "当地声速", "unit": "m/s", "desc_zh": "当地声速"}
        },
        "output": {"Ma": {"label_zh": "马赫数", "unit": "无量纲"}},
        "application_zh": "马赫数区分亚音速(Ma<1)、跨音速、超音速(Ma>1)和高超音速(Ma>5)流态，是高速空气动力学和航天器再入分析的首选参数"
    },

    "isentropic_T": {
        "name_zh": "等熵温度比",
        "desc_zh": "计算等熵流动中静温与总温之比",
        "latex": r"\frac{T}{T_0} = \left[1 + \frac{k-1}{2}\text{Ma}^2\right]^{-1}",
        "inputs": {
            "Ma": {"label_zh": "马赫数", "unit": "无量纲", "desc_zh": "当地马赫数"},
            "k":  {"label_zh": "比热比", "unit": "无量纲", "desc_zh": "比热比，默认1.4"}
        },
        "output": {"T_ratio": {"label_zh": "等熵温度比", "unit": "无量纲"}},
        "application_zh": "等熵关系是高速喷管设计和气体动力学的基础，温度比直接影响喷管出口推力和壁面冷却设计"
    },

    "isentropic_P": {
        "name_zh": "等熵压力比",
        "desc_zh": "计算等熵流动中静压与总压之比",
        "latex": r"\frac{P}{P_0} = \left[1 + \frac{k-1}{2}\text{Ma}^2\right]^{-k/(k-1)}",
        "inputs": {
            "Ma": {"label_zh": "马赫数", "unit": "无量纲", "desc_zh": "当地马赫数"},
            "k":  {"label_zh": "比热比", "unit": "无量纲", "desc_zh": "比热比"}
        },
        "output": {"P_ratio": {"label_zh": "等熵压力比", "unit": "无量纲"}},
        "application_zh": "等熵压力比决定气体膨胀后的压力恢复程度，在涡轮膨胀机、火箭喷管性能和气体减压阀设计中是核心参数"
    },

    "isentropic_rho": {
        "name_zh": "等熵密度比",
        "desc_zh": "计算等熵流动中密度与总密度之比",
        "latex": r"\frac{\rho}{\rho_0} = \left[1 + \frac{k-1}{2}\text{Ma}^2\right]^{-1/(k-1)}",
        "inputs": {
            "Ma": {"label_zh": "马赫数", "unit": "无量纲", "desc_zh": "当地马赫数"},
            "k":  {"label_zh": "比热比", "unit": "无量纲", "desc_zh": "比热比"}
        },
        "output": {"rho_ratio": {"label_zh": "等熵密度比", "unit": "无量纲"}},
        "application_zh": "密度变化影响气动外形阻力和升力，在高速飞行器机身设计和风洞模型修正中必须精确考虑"
    },

    "area_ratio": {
        "name_zh": "等熵面积比",
        "desc_zh": "计算喷管等熵流动中截面积与喉部面积之比",
        "latex": r"\frac{A}{A^*} = \frac{1}{\text{Ma}}\left[\left(\frac{2}{k+1}\right)\left(1 + \frac{k-1}{2}\text{Ma}^2\right)\right]^{(k+1)/(2(k-1))}",
        "inputs": {
            "Ma": {"label_zh": "马赫数", "unit": "无量纲", "desc_zh": "当地马赫数"},
            "k":  {"label_zh": "比热比", "unit": "无量纲", "desc_zh": "比热比"}
        },
        "output": {"A_ratio": {"label_zh": "面积比(A/A*)", "unit": "无量纲"}},
        "application_zh": "面积-马赫数关系是拉瓦尔喷管几何设计的核心方程，决定超音速风洞和火箭发动机喷管的截面轮廓"
    },

    "normal_shock_P": {
        "name_zh": "正激波压力比",
        "desc_zh": "计算正激波前后的静压比",
        "latex": r"\frac{P_2}{P_1} = 1 + \frac{2k}{k+1}(\text{Ma}_1^2 - 1)",
        "inputs": {
            "M1": {"label_zh": "波前马赫数", "unit": "无量纲", "desc_zh": "激波上游马赫数，需>1"},
            "k":  {"label_zh": "比热比", "unit": "无量纲", "desc_zh": "比热比"}
        },
        "output": {"P_ratio": {"label_zh": "激波压力比", "unit": "无量纲"}},
        "application_zh": "正激波引起压力和温度剧烈跃升，是超音速进气道、激波管和爆炸波传播分析的关键参数"
    },

    "normal_shock_rho": {
        "name_zh": "正激波密度比",
        "desc_zh": "计算正激波前后的密度比",
        "latex": r"\frac{\rho_2}{\rho_1} = \frac{(k+1)\text{Ma}_1^2}{(k-1)\text{Ma}_1^2 + 2}",
        "inputs": {
            "M1": {"label_zh": "波前马赫数", "unit": "无量纲", "desc_zh": "激波上游马赫数"},
            "k":  {"label_zh": "比热比", "unit": "无量纲", "desc_zh": "比热比"}
        },
        "output": {"rho_ratio": {"label_zh": "激波密度比", "unit": "无量纲"}},
        "application_zh": "激波后密度跃升直接影响气动阻力，在弹道导弹再入、超音速战斗机进气道激波控制中至关重要"
    },

    "normal_shock_M2": {
        "name_zh": "正激波波后马赫数",
        "desc_zh": "计算正激波下游的马赫数",
        "latex": r"\text{Ma}_2 = \sqrt{\frac{(k-1)\text{Ma}_1^2 + 2}{2k\text{Ma}_1^2 - (k-1)}}",
        "inputs": {
            "M1": {"label_zh": "波前马赫数", "unit": "无量纲", "desc_zh": "激波上游马赫数"},
            "k":  {"label_zh": "比热比", "unit": "无量纲", "desc_zh": "比热比"}
        },
        "output": {"M2": {"label_zh": "波后马赫数", "unit": "无量纲"}},
        "application_zh": "正激波后始终为亚音速(M2<1)，这一特性使进气道设计中利用激波减速增压成为可能"
    },

    "pm_angle": {
        "name_zh": "Prandtl-Meyer角",
        "desc_zh": "计算给定马赫数下的Prandtl-Meyer膨胀角",
        "latex": r"\nu(\text{Ma}) = \sqrt{\frac{k+1}{k-1}}\arctan\!\sqrt{\frac{k-1}{k+1}(\text{Ma}^2-1)} - \arctan\!\sqrt{\text{Ma}^2-1}",
        "inputs": {
            "Ma": {"label_zh": "马赫数", "unit": "无量纲", "desc_zh": "来流马赫数，需>1"},
            "k":  {"label_zh": "比热比", "unit": "无量纲", "desc_zh": "比热比"}
        },
        "output": {"nu": {"label_zh": "Prandtl-Meyer角", "unit": "°"}},
        "application_zh": "Prandtl-Meyer膨胀波理论用于设计超音速喷嘴膨胀段、飞行器翼型后缘和超音速风洞型面"
    },

    "nozzle_mass_flow": {
        "name_zh": "喷管壅塞质量流量",
        "desc_zh": "计算收缩喷管达到音速(壅塞)时的最大质量流量",
        "latex": r"\dot{m}_{\max} = \frac{P_0 A_t}{\sqrt{T_0}}\sqrt{\frac{k}{R}\left(\frac{2}{k+1}\right)^{(k+1)/(k-1)}}",
        "inputs": {
            "P0":  {"label_zh": "总压", "unit": "Pa", "desc_zh": "喷管入口总压"},
            "T0":  {"label_zh": "总温", "unit": "K", "desc_zh": "喷管入口总温"},
            "A_t": {"label_zh": "喉部面积", "unit": "m²", "desc_zh": "喷管最小截面积"},
            "k":   {"label_zh": "比热比", "unit": "无量纲", "desc_zh": "比热比"},
            "R":   {"label_zh": "气体常数", "unit": "J/(kg·K)", "desc_zh": "气体常数"}
        },
        "output": {"m_dot_max": {"label_zh": "壅塞质量流量", "unit": "kg/s"}},
        "application_zh": "喉部达到音速后下游压力不再影响流量，是火箭发动机推力控制、安全阀泄放量计算和气体输送系统的核心设计约束"
    },

    "expansion_velocity": {
        "name_zh": "等熵膨胀出口速度",
        "desc_zh": "计算气体从高压等熵膨胀到出口压力的理想速度",
        "latex": r"V = \sqrt{\frac{2k}{k-1}RT_0\left[1 - \left(\frac{P_e}{P_0}\right)^{(k-1)/k}\right]}",
        "inputs": {
            "P0":     {"label_zh": "总压", "unit": "Pa", "desc_zh": "膨胀前总压"},
            "P_exit": {"label_zh": "出口压力", "unit": "Pa", "desc_zh": "膨胀后的出口背压"},
            "T0":     {"label_zh": "总温", "unit": "K", "desc_zh": "膨胀前总温"},
            "k":      {"label_zh": "比热比", "unit": "无量纲", "desc_zh": "比热比"},
            "R":      {"label_zh": "气体常数", "unit": "J/(kg·K)", "desc_zh": "气体常数"}
        },
        "output": {"V": {"label_zh": "出口速度", "unit": "m/s"}},
        "application_zh": "等熵膨胀速度是火箭发动机喷管出口速度的理论上限，用于估算发动机比冲和推进效率"
    },

    # ====== Category 7: Orifices & Valves (17) ======

    "orifice_flow": {
        "name_zh": "孔板流量",
        "desc_zh": "通过孔板压差计算体积流量",
        "latex": r"Q = C_d A_o \sqrt{\frac{2\Delta P}{\rho}}",
        "inputs": {
            "C_d":  {"label_zh": "流量系数", "unit": "无量纲", "desc_zh": "孔板流量系数，典型值0.6-0.7"},
            "A_o":  {"label_zh": "孔口面积", "unit": "m²", "desc_zh": "孔板开孔面积"},
            "rho":  {"label_zh": "流体密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "dP":   {"label_zh": "孔板压差", "unit": "Pa", "desc_zh": "孔板前后的压差"}
        },
        "output": {"Q": {"label_zh": "体积流量", "unit": "m³/s"}},
        "application_zh": "孔板流量计是工业最广泛使用的差压式流量测量装置，覆盖水、蒸汽、天然气等介质，标准化程度高"
    },

    "valve_Cv": {
        "name_zh": "阀门流量系数Cv",
        "desc_zh": "由流量和压差反算阀门Cv值",
        "latex": r"C_v = Q\sqrt{\frac{\text{SG}}{\Delta P_{\text{psi}}}}",
        "inputs": {
            "Q_gpm": {"label_zh": "流量", "unit": "gpm(美制)", "desc_zh": "通过阀门的体积流量，美制加仑/分钟"},
            "dP_psi":{"label_zh": "阀门压差", "unit": "psi", "desc_zh": "阀门前后压差，psi"},
            "SG":    {"label_zh": "比重", "unit": "无量纲", "desc_zh": "流体相对于水的比重，水=1.0"}
        },
        "output": {"Cv": {"label_zh": "流量系数Cv", "unit": "无量纲"}},
        "application_zh": "Cv是阀门选型的最重要参数：Cv=1表示在1psi压差下通过1gpm的水。工程中根据所需流量和允许压降选择匹配Cv值的阀门"
    },

    "flow_from_Cv": {
        "name_zh": "由Cv计算流量",
        "desc_zh": "根据已知阀门Cv值和压差计算可通过的流量",
        "latex": r"Q = C_v \sqrt{\frac{\Delta P_{\text{psi}}}{\text{SG}}}",
        "inputs": {
            "Cv":    {"label_zh": "流量系数Cv", "unit": "无量纲", "desc_zh": "阀门的已知Cv值"},
            "dP_psi":{"label_zh": "阀门压差", "unit": "psi", "desc_zh": "阀门前后压差"},
            "SG":    {"label_zh": "比重", "unit": "无量纲", "desc_zh": "流体比重"}
        },
        "output": {"Q": {"label_zh": "流量", "unit": "gpm"}},
        "application_zh": "已知阀门型号和Cv值后，可快速估算在各种压差工况下的流通能力，是阀门选型验证和管路校核的基本方法"
    },

    "Kv_to_Cv": {
        "name_zh": "Kv转Cv",
        "desc_zh": "将欧洲标准的Kv值转换为美制Cv值",
        "latex": r"C_v = 1.156\,K_v",
        "inputs": {
            "Kv": {"label_zh": "Kv值", "unit": "m³/h(欧制)", "desc_zh": "欧洲标准流量系数"}
        },
        "output": {"Cv": {"label_zh": "Cv值", "unit": "美制"}},
        "application_zh": "Cv=1.156Kv，用于欧美阀门标准互转。在国际采购和合资项目中频繁使用，避免因单位混淆导致选型错误"
    },

    "Cv_to_Kv": {
        "name_zh": "Cv转Kv",
        "desc_zh": "将美制Cv值转换为欧洲标准的Kv值",
        "latex": r"K_v = 0.865\,C_v",
        "inputs": {
            "Cv": {"label_zh": "Cv值", "unit": "美制", "desc_zh": "美标流量系数"}
        },
        "output": {"Kv": {"label_zh": "Kv值", "unit": "m³/h"}},
        "application_zh": "Kv=0.865Cv，欧洲/ISO标准阀门选型的基本参数，相当于在1bar压差下通过的水流量(m³/h)"
    },

    "valve_dp_from_Cv": {
        "name_zh": "由Cv计算阀门压降",
        "desc_zh": "根据流量和Cv值反算阀门产生的压降",
        "latex": r"\Delta P_{\text{psi}} = \text{SG}\left(\frac{Q}{C_v}\right)^2",
        "inputs": {
            "Q_gpm": {"label_zh": "流量", "unit": "gpm", "desc_zh": "通过阀门的流量"},
            "Cv":    {"label_zh": "流量系数Cv", "unit": "无量纲", "desc_zh": "阀门Cv值"},
            "SG":    {"label_zh": "比重", "unit": "无量纲", "desc_zh": "流体比重"}
        },
        "output": {"dP": {"label_zh": "阀门压降", "unit": "psi"}},
        "application_zh": "在管路水力计算中，阀门作为阻力元件，需要根据Cv和实际流量确定其产生的压降，用于泵扬程校核"
    },

    "choked_dP": {
        "name_zh": "壅塞流压差",
        "desc_zh": "计算液体阀门发生闪蒸壅塞时的临界压差",
        "latex": r"\Delta P_{\text{choked}} = F_L^2(P_1 - 0.96P_v)",
        "inputs": {
            "P1": {"label_zh": "入口压力", "unit": "Pa", "desc_zh": "阀门入口绝对压力"},
            "P_v":{"label_zh": "蒸气压", "unit": "Pa", "desc_zh": "工作温度下液体的蒸气压"},
            "FL": {"label_zh": "压力恢复系数", "unit": "无量纲", "desc_zh": "阀门压力恢复系数，典型0.8-0.9"}
        },
        "output": {"dP_choked": {"label_zh": "壅塞压差", "unit": "Pa"}},
        "application_zh": "实际压差超过壅塞压差时流量不再增加（闪蒸壅塞），是阀门尺寸过大导致失控的常见原因，选型时必须校验"
    },

    "cavitation_index": {
        "name_zh": "阀门空化指数",
        "desc_zh": "评估阀门下游发生空化的风险",
        "latex": r"K_c = \frac{P_d - P_v}{\frac{1}{2}\rho V^2}",
        "inputs": {
            "P_d": {"label_zh": "下游压力", "unit": "Pa", "desc_zh": "阀门下游最小压力"},
            "P_v": {"label_zh": "蒸气压", "unit": "Pa", "desc_zh": "流体蒸气压"},
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "V":   {"label_zh": "下游流速", "unit": "m/s", "desc_zh": "缩流断面处流速"}
        },
        "output": {"Kc": {"label_zh": "空化指数", "unit": "无量纲"}},
        "application_zh": "空化指数越小，空化风险越大。空化是导致阀门内件损坏、噪声和振动的主要原因，航空航天阀门对空化有极为严格的控制要求"
    },

    "valve_authority": {
        "name_zh": "阀门权度",
        "desc_zh": "计算阀门在管路系统中的控制权度",
        "latex": r"N = \frac{\Delta P_{\text{valve}}}{\Delta P_{\text{total}}}",
        "inputs": {
            "dP_valve": {"label_zh": "阀门压降", "unit": "Pa", "desc_zh": "全开状态下阀门的压降"},
            "dP_total": {"label_zh": "系统总压降", "unit": "Pa", "desc_zh": "回路总压降(含管路、管件、阀门)"}
        },
        "output": {"N": {"label_zh": "阀门权度", "unit": "无量纲"}},
        "application_zh": "阀门权度N推荐0.25-0.5。N太低则阀门控制能力弱(近乎开关)，N太高则系统能耗浪费严重"
    },

    "torricelli": {
        "name_zh": "托里拆利流速",
        "desc_zh": "计算容器小孔自由出流的理想速度",
        "latex": r"V = \sqrt{2gh}",
        "inputs": {
            "h": {"label_zh": "液面高度", "unit": "m", "desc_zh": "孔口中心到自由液面的垂直距离"},
            "g": {"label_zh": "重力加速度", "unit": "m/s²", "desc_zh": "重力加速度"}
        },
        "output": {"V": {"label_zh": "出流速度", "unit": "m/s"}},
        "application_zh": "托里拆利定理是孔口出流的基本公式，用于储罐排空时间估算、消防水枪速度和发动机燃油喷射初步设计"
    },

    "nozzle_v": {
        "name_zh": "喷嘴不可压流速",
        "desc_zh": "计算不可压缩流体经喷嘴加速后的理想出口速度",
        "latex": r"V = \sqrt{\frac{2\Delta P}{\rho}}",
        "inputs": {
            "dP":  {"label_zh": "喷嘴压差", "unit": "Pa", "desc_zh": "喷嘴进出口压差"},
            "rho": {"label_zh": "流体密度", "unit": "kg/m³", "desc_zh": "流体密度"}
        },
        "output": {"V": {"label_zh": "出口速度", "unit": "m/s"}},
        "application_zh": "适用于低速液体喷嘴（水射流、燃油雾化喷嘴、消防炮），高速气流需修正可压缩性"
    },

    "Cd_via_Re": {
        "name_zh": "孔板流量系数(Re)",
        "desc_zh": "通过雷诺数和孔径比计算孔板流量系数",
        "latex": r"C_d = 0.5959 + 0.0312\beta^{2.1} - 0.184\beta^8 + \frac{91.71\beta^{2.5}}{\text{Re}^{0.75}}",
        "inputs": {
            "Re":   {"label_zh": "管道雷诺数", "unit": "无量纲", "desc_zh": "基于管道内径的雷诺数"},
            "beta": {"label_zh": "孔径比(d/D)", "unit": "无量纲", "desc_zh": "孔板孔径与管道内径之比"}
        },
        "output": {"C_d": {"label_zh": "流量系数", "unit": "无量纲"}},
        "application_zh": "ISO 5167标准孔板流量系数的Reader-Harris/Gallagher公式，精度最高，用于标准孔板流量计的高精度计量"
    },

    "expansion_factor": {
        "name_zh": "可压缩膨胀系数",
        "desc_zh": "计算气体流经节流件时密度变化引起的流量修正系数",
        "latex": r"Y = 1 - \frac{0.41 + 0.35\beta^4}{k}\cdot\frac{\Delta P}{P_1}",
        "inputs": {
            "k":    {"label_zh": "比热比", "unit": "无量纲", "desc_zh": "气体比热比"},
            "beta": {"label_zh": "孔径比(d/D)", "unit": "无量纲", "desc_zh": "孔板孔径比"},
            "dP":   {"label_zh": "孔板压差", "unit": "Pa", "desc_zh": "节流件前后压差"},
            "P1":   {"label_zh": "上游压力", "unit": "Pa", "desc_zh": "节流件上游绝对静压"}
        },
        "output": {"Y": {"label_zh": "膨胀系数", "unit": "无量纲"}},
        "application_zh": "气体流经节流装置时密度降低导致流量偏小，膨胀系数Y<1修正此误差，在天然气计量和蒸汽流量测量中不可或缺"
    },

    "orifice_velocity": {
        "name_zh": "孔口缩流速度",
        "desc_zh": "由管道流速和面积比计算孔口处的缩流速度",
        "latex": r"V_o = V_p\left(\frac{D}{d}\right)^2",
        "inputs": {
            "D":      {"label_zh": "管道内径", "unit": "m", "desc_zh": "管道内径"},
            "d":      {"label_zh": "孔口直径", "unit": "m", "desc_zh": "孔板孔径"},
            "V_pipe": {"label_zh": "管道流速", "unit": "m/s", "desc_zh": "管道中的平均流速"}
        },
        "output": {"V_o": {"label_zh": "孔口流速", "unit": "m/s"}},
        "application_zh": "通过连续性方程快速估算孔口处的高速流动，用于孔板空化风险评估和孔板结构强度校核"
    },

    "venturi_q": {
        "name_zh": "文丘里管流量",
        "desc_zh": "计算文丘里管流量计的体积流量",
        "latex": r"Q = \frac{C_d A_t}{\sqrt{1-\beta^4}}\sqrt{\frac{2\Delta P}{\rho}}",
        "inputs": {
            "C_d":  {"label_zh": "流量系数", "unit": "无量纲", "desc_zh": "文丘里管流量系数，典型0.95-0.99"},
            "A_t":  {"label_zh": "喉部面积", "unit": "m²", "desc_zh": "文丘里管喉部截面积"},
            "rho":  {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "dP":   {"label_zh": "喉部压差", "unit": "Pa", "desc_zh": "入口与喉部之间的压差"},
            "beta": {"label_zh": "直径比(d/D)", "unit": "无量纲", "desc_zh": "喉径与管径之比"}
        },
        "output": {"Q": {"label_zh": "体积流量", "unit": "m³/s"}},
        "application_zh": "文丘里管永久压损远小于孔板(仅10-20%)，适用于大流量、低压损要求的场合，如航空燃油流量测量和发动机进气计量"
    },

    "vena_contracta": {
        "name_zh": "缩流断面面积",
        "desc_zh": "计算孔口出流缩流断面的实际面积",
        "latex": r"A_c = C_c A_o",
        "inputs": {
            "A_o": {"label_zh": "孔口面积", "unit": "m²", "desc_zh": "孔板或孔口的几何面积"},
            "C_c": {"label_zh": "收缩系数", "unit": "无量纲", "desc_zh": "收缩系数，锐缘孔≈0.62"}
        },
        "output": {"A_c": {"label_zh": "缩流面积", "unit": "m²"}},
        "application_zh": "缩流效应在孔板空化分析中至关重要：缩流处速度最高、压力最低，是空化最先发生的危险区域"
    },

    "flow_resistance": {
        "name_zh": "流动阻力系数",
        "desc_zh": "由压差和流量计算系统的流动阻力系数",
        "latex": r"K_R = \frac{\Delta P}{Q^2}",
        "inputs": {
            "dP":  {"label_zh": "压差", "unit": "Pa", "desc_zh": "系统总压差"},
            "Q":   {"label_zh": "流量", "unit": "m³/s", "desc_zh": "系统流量"},
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"}
        },
        "output": {"KR": {"label_zh": "阻力系数", "unit": "Pa·s²/m⁶"}},
        "application_zh": "流动阻力系数表征系统固有流动特性，用于管路特性曲线绘制、泵工作点确定和系统堵塞诊断"
    },
# ====== Category 8: Boundary Layer & Drag (10) ======

    "bl_laminar": {
        "name_zh": "层流边界层厚度",
        "desc_zh": "计算平板层流边界层厚度沿流向的分布",
        "latex": r"\delta_{\text{lam}} = \frac{5.0x}{\sqrt{\text{Re}_x}}",
        "inputs": {
            "x":    {"label_zh": "距前缘距离", "unit": "m", "desc_zh": "距平板前缘的流向距离"},
            "Re_x": {"label_zh": "当地雷诺数", "unit": "无量纲", "desc_zh": "基于x的当地雷诺数"}
        },
        "output": {"delta": {"label_zh": "边界层厚度", "unit": "m"}},
        "application_zh": "层流边界层厚度与x^(1/2)成正比，Blasius精确解。在低速翼型、微流动器件和传感器热膜设计中应用"
    },

    "bl_turbulent": {
        "name_zh": "湍流边界层厚度",
        "desc_zh": "计算平板湍流边界层厚度(1/7次方律)",
        "latex": r"\delta_{\text{turb}} = \frac{0.37x}{\text{Re}_x^{1/5}}",
        "inputs": {
            "x":    {"label_zh": "距前缘距离", "unit": "m", "desc_zh": "距平板前缘的流向距离"},
            "Re_x": {"label_zh": "当地雷诺数", "unit": "无量纲", "desc_zh": "基于x的当地雷诺数"}
        },
        "output": {"delta": {"label_zh": "边界层厚度", "unit": "m"}},
        "application_zh": "湍流边界层增长更快(与x^(4/5)成正比)，摩阻更大但抗分离能力更强，在飞行器表面流动控制中需权衡利用"
    },

    "cf_laminar": {
        "name_zh": "层流表面摩擦系数",
        "desc_zh": "计算平板层流的总表面摩擦系数",
        "latex": r"C_f = \frac{1.328}{\sqrt{\text{Re}_L}}",
        "inputs": {
            "Re_L": {"label_zh": "平板雷诺数", "unit": "无量纲", "desc_zh": "基于平板总长度的雷诺数"}
        },
        "output": {"Cf": {"label_zh": "表面摩擦系数", "unit": "无量纲"}},
        "application_zh": "层流Cf仅与Re_L^(-1/2)成正比，显著低于湍流。在高空长航时无人机和滑翔机设计中追求大面积层流"
    },

    "cf_turbulent": {
        "name_zh": "湍流表面摩擦系数",
        "desc_zh": "计算平板湍流的总表面摩擦系数",
        "latex": r"C_f = \frac{0.074}{\text{Re}_L^{1/5}}",
        "inputs": {
            "Re_L": {"label_zh": "平板雷诺数", "unit": "无量纲", "desc_zh": "基于平板总长度的雷诺数"}
        },
        "output": {"Cf": {"label_zh": "表面摩擦系数", "unit": "无量纲"}},
        "application_zh": "湍流摩阻远大于层流(约高3-10倍)，是飞行器巡航阻力(~50%)和大口径长输管道摩阻的主要来源"
    },

    "drag_force": {
        "name_zh": "阻力",
        "desc_zh": "计算物体在流体中运动受到的阻力",
        "latex": r"F_D = \frac{1}{2}C_D \rho V^2 A_{\text{ref}}",
        "inputs": {
            "C_d":   {"label_zh": "阻力系数", "unit": "无量纲", "desc_zh": "物体的阻力系数，取决于形状和Re"},
            "rho":   {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "V":     {"label_zh": "相对速度", "unit": "m/s", "desc_zh": "物体与流体的相对速度"},
            "A_ref": {"label_zh": "参考面积", "unit": "m²", "desc_zh": "迎风面积(钝体)或表面积(平板)"}
        },
        "output": {"F_D": {"label_zh": "阻力", "unit": "N"}},
        "application_zh": "阻力方程是空气动力学和外弹道学的基石。减小Cd和A_ref是飞行器、赛车和弹体气动优化的核心目标"
    },

    "lift_force": {
        "name_zh": "升力",
        "desc_zh": "计算机翼或翼型产生的升力",
        "latex": r"F_L = \frac{1}{2}C_L \rho V^2 A",
        "inputs": {
            "C_l": {"label_zh": "升力系数", "unit": "无量纲", "desc_zh": "翼型升力系数，取决于攻角和形状"},
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "V":   {"label_zh": "飞行速度", "unit": "m/s", "desc_zh": "飞行速度或来流速度"},
            "A":   {"label_zh": "翼面积", "unit": "m²", "desc_zh": "机翼平面面积"}
        },
        "output": {"F_L": {"label_zh": "升力", "unit": "N"}},
        "application_zh": "升力方程是飞行器设计的核心，用于翼型选型、起飞速度和巡航升阻比优化，是航空工程的起点"
    },

    "stokes_drag": {
        "name_zh": "Stokes阻力(球体)",
        "desc_zh": "计算极低雷诺数下球体所受的粘性阻力",
        "latex": r"F_D = 6\pi\mu R V",
        "inputs": {
            "mu": {"label_zh": "动力粘度", "unit": "Pa·s", "desc_zh": "流体动力粘度"},
            "R":  {"label_zh": "球体半径", "unit": "m", "desc_zh": "球体半径"},
            "V":  {"label_zh": "相对速度", "unit": "m/s", "desc_zh": "球体与流体相对速度"}
        },
        "output": {"F_D": {"label_zh": "Stokes阻力", "unit": "N"}},
        "application_zh": "Stokes定律适用于Re<1的蠕动流，用于微粒沉降、气溶胶动力学、生物细胞力学和空气过滤器设计"
    },

    "cd_sphere": {
        "name_zh": "球体阻力系数",
        "desc_zh": "计算球体的阻力系数随雷诺数的变化",
        "latex": r"C_D = \begin{cases} \frac{24}{\text{Re}} & \text{Re}<1 \\ \frac{24}{\text{Re}}(1+0.15\text{Re}^{0.687}) & 1<\text{Re}<1000 \\ 0.44 & \text{Re}\geq 1000 \end{cases}",
        "inputs": {
            "Re": {"label_zh": "雷诺数", "unit": "无量纲", "desc_zh": "基于球直径的雷诺数"}
        },
        "output": {"C_D": {"label_zh": "阻力系数", "unit": "无量纲"}},
        "application_zh": "球体Cd从Stokes区的24/Re过渡到湍流区的~0.44。在颗粒输送、球阀流阻和运动球空气动力学(足球/高尔夫)中广泛应用"
    },

    "terminal_v": {
        "name_zh": "终端沉降速度",
        "desc_zh": "计算球体在流体中自由沉降的终端速度(Stokes区)",
        "latex": r"V_t = \frac{2R^2(\rho_p - \rho_f)g}{9\mu}",
        "inputs": {
            "rho_p": {"label_zh": "颗粒密度", "unit": "kg/m³", "desc_zh": "球体材料密度"},
            "rho_f": {"label_zh": "流体密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "R":     {"label_zh": "球体半径", "unit": "m", "desc_zh": "球体半径"},
            "mu":    {"label_zh": "动力粘度", "unit": "Pa·s", "desc_zh": "流体动力粘度"},
            "g":     {"label_zh": "重力加速度", "unit": "m/s²", "desc_zh": "重力加速度"}
        },
        "output": {"V_t": {"label_zh": "终端速度", "unit": "m/s"}},
        "application_zh": "终端速度用于泥沙沉降计算、油水分离器设计、大气污染物沉降评估和化工反应器颗粒停留时间控制"
    },

    "re_flat_plate": {
        "name_zh": "平板雷诺数",
        "desc_zh": "计算基于平板长度和运动粘度的雷诺数",
        "latex": r"\text{Re}_L = \frac{V L}{\nu}",
        "inputs": {
            "V":  {"label_zh": "来流速度", "unit": "m/s", "desc_zh": "自由来流速度"},
            "L":  {"label_zh": "平板长度", "unit": "m", "desc_zh": "平板总长度"},
            "nu": {"label_zh": "运动粘度", "unit": "m²/s", "desc_zh": "流体运动粘度"}
        },
        "output": {"Re_L": {"label_zh": "平板雷诺数", "unit": "无量纲"}},
        "application_zh": "平板雷诺数Re≈5×10⁵为转捩临界，用于预估边界层从层流到湍流的转换位置和摩阻变化"
    },

    # ====== Category 9: Fluid Power / Hydraulics (11) ======

    "pump_power": {
        "name_zh": "泵功率",
        "desc_zh": "计算泵的实际输入功率(轴功率)",
        "latex": r"P_{\text{pump}} = \frac{Q\Delta P}{\eta}",
        "inputs": {
            "Q":   {"label_zh": "流量", "unit": "m³/s", "desc_zh": "泵输送流量"},
            "dP":  {"label_zh": "泵扬程压差", "unit": "Pa", "desc_zh": "泵进出口总压差"},
            "eta": {"label_zh": "泵效率", "unit": "无量纲", "desc_zh": "泵总效率，典型0.6-0.92"}
        },
        "output": {"P": {"label_zh": "泵功率", "unit": "W"}},
        "application_zh": "泵功率是电机选型和能耗评估的核心参数，直接影响工程系统的运行成本和能源效率"
    },

    "hydraulic_power": {
        "name_zh": "水力功率",
        "desc_zh": "计算流体获得的水力功率(输出功率)",
        "latex": r"P_h = Q\Delta P",
        "inputs": {
            "Q":  {"label_zh": "流量", "unit": "m³/s", "desc_zh": "流体流量"},
            "dP": {"label_zh": "压差", "unit": "Pa", "desc_zh": "流体获得的压力增量"}
        },
        "output": {"Ph": {"label_zh": "水力功率", "unit": "W"}},
        "application_zh": "水力功率是流体实际获得的功率，与泵功率之比等于泵效率，用于能量平衡核算和能效评估"
    },

    "cylinder_force": {
        "name_zh": "液压缸出力",
        "desc_zh": "计算液压缸活塞杆的输出力",
        "latex": r"F = P(A_p - A_r)",
        "inputs": {
            "P":        {"label_zh": "工作压力", "unit": "Pa", "desc_zh": "液压缸工作压力"},
            "A_piston": {"label_zh": "活塞面积", "unit": "m²", "desc_zh": "活塞端面积"},
            "A_rod":    {"label_zh": "活塞杆面积", "unit": "m²", "desc_zh": "活塞杆截面积，默认0"}
        },
        "output": {"F": {"label_zh": "输出力", "unit": "N"}},
        "application_zh": "液压缸是工程机械和航空航天伺服系统的核心执行机构，此公式直接决定作动器的推力和承载能力"
    },

    "cylinder_velocity": {
        "name_zh": "液压缸速度",
        "desc_zh": "由供油流量和活塞面积计算活塞运动速度",
        "latex": r"V = \frac{Q}{A}",
        "inputs": {
            "Q": {"label_zh": "供油流量", "unit": "m³/s", "desc_zh": "进入液压缸的流量"},
            "A": {"label_zh": "有效面积", "unit": "m²", "desc_zh": "活塞有效作用面积"}
        },
        "output": {"V": {"label_zh": "活塞速度", "unit": "m/s"}},
        "application_zh": "决定工程机械动作速度和响应频率，在火箭发动机推力矢量控制(TVC)作动器中要求极高的速度精度"
    },

    "motor_torque": {
        "name_zh": "液压马达扭矩",
        "desc_zh": "计算液压马达的输出扭矩",
        "latex": r"T = \frac{q \Delta P \eta_m}{2\pi}",
        "inputs": {
            "q_displacement": {"label_zh": "排量", "unit": "m³/rev", "desc_zh": "马达每转排量"},
            "dP":             {"label_zh": "压差", "unit": "Pa", "desc_zh": "马达进出口压差"},
            "eta_m":          {"label_zh": "机械效率", "unit": "无量纲", "desc_zh": "马达机械效率，默认0.92"}
        },
        "output": {"T": {"label_zh": "扭矩", "unit": "N·m"}},
        "application_zh": "液压马达在工程机械回转机构、船舶舵机和航空燃油泵驱动中提供高功率密度的旋转动力"
    },

    "motor_speed": {
        "name_zh": "液压马达转速",
        "desc_zh": "由供油流量和排量计算马达转速",
        "latex": r"N = \frac{Q\eta_v}{q}",
        "inputs": {
            "Q":             {"label_zh": "供油流量", "unit": "m³/s", "desc_zh": "马达供油流量"},
            "q_displacement":{"label_zh": "排量", "unit": "m³/rev", "desc_zh": "马达每转排量"},
            "eta_v":         {"label_zh": "容积效率", "unit": "无量纲", "desc_zh": "马达容积效率，默认0.95"}
        },
        "output": {"N": {"label_zh": "转速", "unit": "rev/s"}},
        "application_zh": "排量和转速的乘积关系是液压泵/马达选型的基本方程，决定系统流量需求和响应速度"
    },

    "accumulator": {
        "name_zh": "蓄能器有效容积",
        "desc_zh": "计算气囊式蓄能器在压差下的有效排油量",
        "latex": r"\Delta V = V_0\left[1 - \left(\frac{P_0}{P_1}\right)^{1/n}\right]",
        "inputs": {
            "V0": {"label_zh": "蓄能器总容积", "unit": "m³", "desc_zh": "蓄能器公称容积"},
            "P0": {"label_zh": "充气压力", "unit": "Pa", "desc_zh": "蓄能器预充压力"},
            "P1": {"label_zh": "工作压力", "unit": "Pa", "desc_zh": "系统最高工作压力"},
            "n":  {"label_zh": "多变指数", "unit": "无量纲", "desc_zh": "n≈1等温，n≈1.4绝热"}
        },
        "output": {"dV": {"label_zh": "有效排油量", "unit": "m³"}},
        "application_zh": "蓄能器用于吸收脉动、补偿泄漏、应急供油和能量回收，在航空航天液压系统(起落架、飞控)中不可或缺"
    },

    "pressure_intensifier": {
        "name_zh": "增压器增压比",
        "desc_zh": "计算液压增压器的压力放大倍数",
        "latex": r"N = \frac{A_{\text{large}}}{A_{\text{small}}}",
        "inputs": {
            "A_large": {"label_zh": "大活塞面积", "unit": "m²", "desc_zh": "低压侧大活塞面积"},
            "A_small": {"label_zh": "小活塞面积", "unit": "m²", "desc_zh": "高压侧小活塞面积"}
        },
        "output": {"N": {"label_zh": "增压比", "unit": "无量纲"}},
        "application_zh": "增压器将低压转化为超高压(如350bar→2000bar)，用于超高压阀门试验台和火箭发动机燃料增压"
    },
    "fluid_spring": {
        "name_zh": "流体弹簧刚度",
        "desc_zh": "计算封闭液压系统中流体的弹簧刚度",
        "latex": r"k_f = \frac{K A^2}{V}",
        "inputs": {
            "K_bulk": {"label_zh": "体积模量", "unit": "Pa", "desc_zh": "流体的体积弹性模量"},
            "A": {"label_zh": "活塞面积", "unit": "m²", "desc_zh": "液压缸活塞有效面积"},
            "V": {"label_zh": "流体体积", "unit": "m³", "desc_zh": "封闭腔内流体总体积"}
        },
        "output": {"k_f": {"label_zh": "流体弹簧刚度", "unit": "N/m"}},
        "application_zh": "液压伺服系统动态分析，影响系统固有频率和响应速度，在电液伺服阀和制动系统设计中至关重要"
    },

    "fluid_spring": {
        "name_zh": "液压弹簧刚度",
        "desc_zh": "计算封闭液柱的等效弹簧刚度",
        "latex": r"K_h = \frac{K_{\text{bulk}} A^2}{V}",
        "inputs": {
            "K_bulk": {"label_zh": "体积弹性模量", "unit": "Pa", "desc_zh": "流体体积弹性模量"},
            "A":      {"label_zh": "活塞面积", "unit": "m²", "desc_zh": "作动筒有效面积"},
            "V":      {"label_zh": "液柱体积", "unit": "m³", "desc_zh": "封闭液柱的总体积"}
        },
        "output": {"Kh": {"label_zh": "液压弹簧刚度", "unit": "N/m"}},
        "application_zh": "液压弹簧刚度决定伺服系统的固有频率和动态响应。含气油液刚度急剧下降，排气是液压系统调试的首要步骤"
    },

    "time_constant": {
        "name_zh": "液压时间常数",
        "desc_zh": "计算液压缸充满所需的时间",
        "latex": r"\tau = \frac{V}{Q}",
        "inputs": {
            "V": {"label_zh": "液压缸容积", "unit": "m³", "desc_zh": "液压缸有效容积"},
            "Q": {"label_zh": "供油流量", "unit": "m³/s", "desc_zh": "供油流量"}
        },
        "output": {"tau": {"label_zh": "时间常数", "unit": "s"}},
        "application_zh": "时间常数评估液压系统响应速度，用于推力矢量控制(TVC)、飞行模拟平台等对响应时间有严格要求的系统"
    },

    "pump_eff": {
        "name_zh": "泵总效率",
        "desc_zh": "由容积效率和机械效率计算泵的总效率",
        "latex": r"\eta = \eta_v \cdot \eta_m",
        "inputs": {
            "eta_v": {"label_zh": "容积效率", "unit": "无量纲", "desc_zh": "泵容积效率，反映内泄漏"},
            "eta_m": {"label_zh": "机械效率", "unit": "无量纲", "desc_zh": "泵机械效率，反映摩擦损失"}
        },
        "output": {"eta": {"label_zh": "总效率", "unit": "无量纲"}},
        "application_zh": "泵效率是能耗的核心指标：轴向柱塞泵可达92-95%，离心泵70-85%。效率下降意味着内泄漏增加或机械磨损"
    },

    # ====== Category 10: Water Hammer & Surge (5) ======

    "joukowsky": {
        "name_zh": "Joukowsky水锤压力",
        "desc_zh": "计算瞬时关阀引起的水锤压力峰值",
        "latex": r"\Delta P = \rho a |\Delta V|",
        "inputs": {
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "a":   {"label_zh": "波速", "unit": "m/s", "desc_zh": "压力波传播速度"},
            "dV":  {"label_zh": "速度变化", "unit": "m/s", "desc_zh": "关阀前后流速变化量的绝对值"}
        },
        "output": {"dP": {"label_zh": "水锤压力", "unit": "Pa"}},
        "application_zh": "Joukowsky方程是水锤分析的基本公式。快速关阀ΔP可达数MPa，是长输管道、消防系统和火箭燃料加注管路中必须校核的危险载荷"
    },

    "wave_speed": {
        "name_zh": "压力波速",
        "desc_zh": "考虑管壁弹性的水锤压力波传播速度",
        "latex": r"a = \frac{a_0}{\sqrt{1 + \frac{C K D}{E_p e}}},\quad a_0 = \sqrt{\frac{K}{\rho}}",
        "inputs": {
            "K":      {"label_zh": "体积弹性模量", "unit": "Pa", "desc_zh": "流体体积弹性模量"},
            "rho":    {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "D":      {"label_zh": "管道内径", "unit": "m", "desc_zh": "管道内径"},
            "e":      {"label_zh": "管壁厚度", "unit": "m", "desc_zh": "管壁厚度"},
            "E_pipe": {"label_zh": "管材弹性模量", "unit": "Pa", "desc_zh": "管道材料弹性模量，钢≈2.1×10¹¹"},
            "C":      {"label_zh": "管道约束系数", "unit": "无量纲", "desc_zh": "约束条件系数，默认1.0"}
        },
        "output": {"a": {"label_zh": "波速", "unit": "m/s"}},
        "application_zh": "波速决定关阀的安全时间窗口。管道弹性使波速降为纯流体波速的60-80%，在精确水锤分析中必须考虑管壁弹性"
    },

    "instant_surge": {
        "name_zh": "瞬间关阀涌压",
        "desc_zh": "计算阀门瞬间完全关闭时的最大涌浪压力",
        "latex": r"\Delta P_{\text{surge}} = \rho a V_0",
        "inputs": {
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "a":   {"label_zh": "波速", "unit": "m/s", "desc_zh": "压力波速"},
            "V0":  {"label_zh": "初始流速", "unit": "m/s", "desc_zh": "关阀前的稳定流速"}
        },
        "output": {"dP_surge": {"label_zh": "关阀涌压", "unit": "Pa"}},
        "application_zh": "这是水锤压力最坏情况的估计(V→0)。設計中系统承压至少应为正常工作压力的1.5-3倍以容纳水锤"
    },
    "pipe_period": {
        "name_zh": "管道自振周期",
        "desc_zh": "计算水锤波在管道中往返传播的周期",
        "latex": r"T_r = \frac{2L}{a}",
        "inputs": {
            "L": {"label_zh": "管道长度", "unit": "m", "desc_zh": "管道总长度"},
            "a": {"label_zh": "波速", "unit": "m/s", "desc_zh": "压力波在管道中的传播速度"}
        },
        "output": {"T_r": {"label_zh": "管道周期", "unit": "s"}},
        "application_zh": "水锤防护设计关键参数，当阀门关闭时间小于T_r时发生直接水锤，压力峰值最大"
    },

    "pipe_period": {
        "name_zh": "管道周期",
        "desc_zh": "计算水锤压力波往返所需的时间",
        "latex": r"T_r = \frac{2L}{a}",
        "inputs": {
            "L": {"label_zh": "管道长度", "unit": "m", "desc_zh": "管道总长度"},
            "a": {"label_zh": "波速", "unit": "m/s", "desc_zh": "压力波速"}
        },
        "output": {"Tr": {"label_zh": "管道周期", "unit": "s"}},
        "application_zh": "管道周期是水锤分析的基准时间尺度。关阀时间>2Tr为缓慢关闭(水锤大幅减弱)，<Tr则为快速关闭(最大水锤)"
    },

    "critical_tc": {
        "name_zh": "临界关闭时间",
        "desc_zh": "计算缓慢关闭与快速关闭的临界时间",
        "latex": r"t_c = \frac{2L}{a}",
        "inputs": {
            "L": {"label_zh": "管道长度", "unit": "m", "desc_zh": "管道总长度"},
            "a": {"label_zh": "波速", "unit": "m/s", "desc_zh": "压力波速"}
        },
        "output": {"tc": {"label_zh": "临界关闭时间", "unit": "s"}},
        "application_zh": "阀门关闭时间>tc时水锤显著减弱。工程中通过延长关阀时间(tc的5-10倍)或安装蓄能器/调压井来控制水锤"
    },

    # ====== Category 11: Dimensional Analysis (7) ======

    "re_number": {
        "name_zh": "雷诺数(量纲分析)",
        "desc_zh": "计算雷诺数——惯性力与粘性力之比",
        "latex": r"\text{Re} = \frac{V L}{\nu}",
        "inputs": {
            "V":  {"label_zh": "特征速度", "unit": "m/s", "desc_zh": "特征速度"},
            "L":  {"label_zh": "特征长度", "unit": "m", "desc_zh": "特征长度"},
            "nu": {"label_zh": "运动粘度", "unit": "m²/s", "desc_zh": "流体运动粘度"}
        },
        "output": {"Re": {"label_zh": "雷诺数", "unit": "无量纲"}},
        "application_zh": "雷诺数是流体力学最重要的无量纲数，用于流动相似性保证——模型实验的Re必须与原型相等(或处于同一自模化区)"
    },

    "fr_number": {
        "name_zh": "弗汝德数(量纲分析)",
        "desc_zh": "计算弗汝德数——惯性力与重力之比",
        "latex": r"\text{Fr} = \frac{V}{\sqrt{g L}}",
        "inputs": {
            "V": {"label_zh": "特征速度", "unit": "m/s", "desc_zh": "特征速度"},
            "g": {"label_zh": "重力加速度", "unit": "m/s²", "desc_zh": "重力加速度"},
            "L": {"label_zh": "特征长度", "unit": "m", "desc_zh": "特征长度"}
        },
        "output": {"Fr": {"label_zh": "弗汝德数", "unit": "无量纲"}},
        "application_zh": "Fr是明渠、船舶波浪阻力和溢洪道模型实验的主导相似准则。Fr=1临界流是水跃和跌水的分界线"
    },

    "ma_number": {
        "name_zh": "马赫数(量纲分析)",
        "desc_zh": "计算马赫数——流速与声速之比",
        "latex": r"\text{Ma} = \frac{V}{a}",
        "inputs": {
            "V": {"label_zh": "流速", "unit": "m/s", "desc_zh": "流体速度"},
            "a": {"label_zh": "当地声速", "unit": "m/s", "desc_zh": "当地声速"}
        },
        "output": {"Ma": {"label_zh": "马赫数", "unit": "无量纲"}},
        "application_zh": "Ma是可压缩流动的支配参数。Ma>0.3(空气)必须考虑压缩性效应，是风洞模型设计和高速飞行器缩比实验的基础参数"
    },

    "we_number": {
        "name_zh": "韦伯数",
        "desc_zh": "计算韦伯数——惯性力与表面张力之比",
        "latex": r"\text{We} = \frac{\rho V^2 L}{\sigma}",
        "inputs": {
            "rho":   {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "V":     {"label_zh": "特征速度", "unit": "m/s", "desc_zh": "特征速度"},
            "L":     {"label_zh": "特征长度", "unit": "m", "desc_zh": "特征长度"},
            "sigma": {"label_zh": "表面张力系数", "unit": "N/m", "desc_zh": "表面张力系数"}
        },
        "output": {"We": {"label_zh": "韦伯数", "unit": "无量纲"}},
        "application_zh": "We决定液滴破碎/雾化行为(We>12开始破碎)，在火箭发动机喷注器雾化、燃油喷射和内燃机喷雾设计中关键"
    },

    "eu_number": {
        "name_zh": "欧拉数",
        "desc_zh": "计算欧拉数——压力力与惯性力之比",
        "latex": r"\text{Eu} = \frac{\Delta P}{\rho V^2}",
        "inputs": {
            "dP":  {"label_zh": "特征压差", "unit": "Pa", "desc_zh": "特征压力差"},
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "V":   {"label_zh": "特征速度", "unit": "m/s", "desc_zh": "特征速度"}
        },
        "output": {"Eu": {"label_zh": "欧拉数", "unit": "无量纲"}},
        "application_zh": "欧拉数是管道流动和阀门压损的相似参数。Eu与Re和相对粗糙度相关，是管流摩擦系数f的无量纲化表达(f=2Eu·D/L)"
    },

    "st_number": {
        "name_zh": "斯特劳哈尔数",
        "desc_zh": "计算Strouhal数——非定常惯性力与对流惯性力之比",
        "latex": r"\text{St} = \frac{f L}{V}",
        "inputs": {
            "f": {"label_zh": "特征频率", "unit": "Hz", "desc_zh": "涡脱落频率或振荡频率"},
            "L": {"label_zh": "特征长度", "unit": "m", "desc_zh": "特征长度(圆柱直径为D)"},
            "V": {"label_zh": "特征速度", "unit": "m/s", "desc_zh": "来流速度"}
        },
        "output": {"St": {"label_zh": "斯特劳哈尔数", "unit": "无量纲"}},
        "application_zh": "St≈0.21(圆柱Re≈10³-10⁵)决定卡门涡街脱落频率，是涡街流量计原理和换热器管束流致振动的核心参数"
    },

    "buckingham_pi": {
        "name_zh": "Buckingham π定理",
        "desc_zh": "确定物理问题中独立无量纲参数的最少数量",
        "latex": r"n_{\pi} = n_{\text{vars}} - n_{\text{dims}}",
        "inputs": {
            "n_vars":  {"label_zh": "变量数", "unit": "无量纲", "desc_zh": "问题中涉及的物理变量总数"},
            "n_dims":  {"label_zh": "基本量纲数", "unit": "无量纲", "desc_zh": "独立基本量纲数(力学通常=3:MLT)"}
        },
        "output": {"n_pi": {"label_zh": "π组数", "unit": "无量纲"}},
        "application_zh": "π定理是量纲分析和模型实验设计的理论基础。例如管道流动有7个变量、3个量纲→4个独立π组(Re, ε/D, Eu, L/D)"
    },

    # ====== Category 12: Fluid-Structure Interaction (5) ======

    "fn_fluid_column": {
        "name_zh": "液柱固有频率",
        "desc_zh": "计算一端封闭液柱的轴向振动固有频率",
        "latex": r"f_n = \frac{1}{2\pi}\sqrt{\frac{K A}{\rho L}}",
        "inputs": {
            "K":   {"label_zh": "体积弹性模量", "unit": "Pa", "desc_zh": "流体体积弹性模量"},
            "rho": {"label_zh": "密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "L":   {"label_zh": "液柱长度", "unit": "m", "desc_zh": "封闭液柱长度"},
            "A":   {"label_zh": "截面积", "unit": "m²", "desc_zh": "液柱截面积"}
        },
        "output": {"fn": {"label_zh": "固有频率", "unit": "Hz"}},
        "application_zh": "液柱固有频率必须避开泵脉动频率和结构振动频率。匹配时发生液压共振→压力剧烈波荡→管路疲劳失效"
    },

    "added_mass": {
        "name_zh": "附加质量",
        "desc_zh": "计算物体在流体中加速时带动的附加流体质量",
        "latex": r"m_a = C_m \rho_f V_{\text{fluid}}",
        "inputs": {
            "C_m":       {"label_zh": "附加质量系数", "unit": "无量纲", "desc_zh": "附加质量系数，球体=0.5，圆柱=1.0"},
            "V_fluid":   {"label_zh": "排开流体体积", "unit": "m³", "desc_zh": "结构排开流体的体积"},
            "rho_fluid": {"label_zh": "流体密度", "unit": "kg/m³", "desc_zh": "流体密度"}
        },
        "output": {"ma": {"label_zh": "附加质量", "unit": "kg"}},
        "application_zh": "附加质量使结构有效质量增大（水中≈本体质量量级），导致湿模态频率低于干模态。潜水器和船舶水弹性分析必须计入"
    },

    "vortex_shedding": {
        "name_zh": "涡街脱落频率",
        "desc_zh": "计算圆柱绕流涡街脱落频率",
        "latex": r"f_{\text{vs}} = \frac{\text{St} \cdot V}{D}",
        "inputs": {
            "St": {"label_zh": "Strouhal数", "unit": "无量纲", "desc_zh": "Strouhal数，圆柱≈0.21"},
            "V":  {"label_zh": "来流速度", "unit": "m/s", "desc_zh": "来流速度"},
            "D":  {"label_zh": "圆柱直径", "unit": "m", "desc_zh": "圆柱特征直径"}
        },
        "output": {"f_vs": {"label_zh": "涡脱落频率", "unit": "Hz"}},
        "application_zh": "涡脱落频率与结构固有频率重合时→涡激共振(VIV)→结构疲劳破坏。在热交换器管束、海洋立管和烟囱设计中必须避开"
    },

    "reduced_velocity": {
        "name_zh": "折合速度(VIV)",
        "desc_zh": "计算涡激振动的折合速度，判断锁定区间",
        "latex": r"V_r = \frac{U}{f_n D}",
        "inputs": {
            "U":   {"label_zh": "来流速度", "unit": "m/s", "desc_zh": "来流速度"},
            "f_n": {"label_zh": "结构固有频率", "unit": "Hz", "desc_zh": "结构在水中的固有频率"},
            "D":   {"label_zh": "圆柱直径", "unit": "m", "desc_zh": "圆柱特征直径"}
        },
        "output": {"Vr": {"label_zh": "折合速度", "unit": "无量纲"}},
        "application_zh": "Vr≈5-8为涡激共振锁定区间(VIV lock-in)——结构振幅急剧增大，是深海立管和超高层建筑风振设计的危险区域"
    },
    "fluid_elastic": {
        "name_zh": "流体弹性失稳临界速度",
        "desc_zh": "计算流体诱发结构弹性失稳的临界流速",
        "latex": r"U_c = K_c f_n D \sqrt{\frac{m}{\rho}} \zeta",
        "inputs": {
            "f_n": {"label_zh": "固有频率", "unit": "Hz", "desc_zh": "结构的固有振动频率"},
            "D": {"label_zh": "特征直径", "unit": "m", "desc_zh": "管束或结构的特征直径"},
            "m": {"label_zh": "单位长度质量", "unit": "kg/m", "desc_zh": "结构单位长度的质量"},
            "rho": {"label_zh": "流体密度", "unit": "kg/m³", "desc_zh": "流体的密度"},
            "zeta": {"label_zh": "阻尼比", "unit": "无量纲", "desc_zh": "结构的阻尼比"}
        },
        "output": {"U_crit": {"label_zh": "临界流速", "unit": "m/s"}},
        "application_zh": "换热器管束、核燃料棒等流致振动的稳定性评估，超过临界速度会发生流体弹性失稳导致结构损坏"
    },

    "fluid_elastic": {
        "name_zh": "流体弹性失稳临界速度",
        "desc_zh": "计算管束发生流体弹性失稳的临界来流速度",
        "latex": r"U_{\text{crit}} = \frac{f_n D}{K}\sqrt{\frac{m}{\rho}},\quad K\approx 2.5",
        "inputs": {
            "f_n":  {"label_zh": "固有频率", "unit": "Hz", "desc_zh": "管束在水中一阶固有频率"},
            "D":    {"label_zh": "管径", "unit": "m", "desc_zh": "管子外径"},
            "m":    {"label_zh": "管单位长度质量", "unit": "kg/m", "desc_zh": "含附加质量的单位管长总质量"},
            "rho":  {"label_zh": "流体密度", "unit": "kg/m³", "desc_zh": "流体密度"},
            "zeta": {"label_zh": "阻尼比", "unit": "无量纲", "desc_zh": "结构阻尼比，典型0.005-0.05"}
        },
        "output": {"U_crit": {"label_zh": "临界速度", "unit": "m/s"}},
        "application_zh": "U>U_crit时管束发生流体弹性失稳→管子剧烈碰撞→快速破坏。蒸汽发生器、冷凝器和换热器的管束设计中必须确保流速低于临界值"
    },
}