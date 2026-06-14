import re
with open('tool_bridge.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "from materials_database import query_material",
    "from materials_database import get_material_detail"
)
content = content.replace(
    "result = query_material(name)",
    "result = get_material_detail(name)"
)

with open('tool_bridge.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched.")
