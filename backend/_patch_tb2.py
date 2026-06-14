with open('tool_bridge.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''def _material_query(kwargs):
    """Query material database by name or id."""
    try:
        from materials_database import get_material_detail
        name = kwargs.get('material', kwargs.get('name', ''))
        if not name:
            return {'success': False, 'error': 'No material name provided'}
        result = get_material_detail(name)
        if not result:
            return {'success': False, 'error': 'Material "{}" not found'.format(name)}'''

new = '''def _material_query(kwargs):
    """Query material database by name or id."""
    try:
        from materials_database import get_all_materials
        name = kwargs.get('material', kwargs.get('name', ''))
        if not name:
            return {'success': False, 'error': 'No material name provided'}
        mats = get_all_materials()
        result = None
        name_upper = name.upper()
        # Match by id prefix or name prefix (case-insensitive)
        for m in mats:
            mid = str(m.get('id', '')).upper()
            mname = str(m.get('name', '')).upper()
            if mid == name_upper or mname.startswith(name_upper) or name_upper in mname:
                result = m
                break
        if not result:
            return {'success': False, 'error': 'Material "{}" not found'.format(name)}'''

content = content.replace(old, new)

with open('tool_bridge.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched _material_query.")
