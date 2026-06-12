"""
Dynamic Library Loader — Sprint 2
==================================
Lazy-loads SKILL.md files from skills/ directory.
Parses YAML-like frontmatter and markdown content.
"""

import os
import re
import glob
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Skill:
    """Represents a loaded SKILL.md."""
    name: str
    file_path: str
    description: str = ''
    parameters: Dict = field(default_factory=dict)
    pitfalls: List[str] = field(default_factory=list)
    standards: List[str] = field(default_factory=list)
    procedure: List[str] = field(default_factory=list)
    content: str = ''
    loaded_at: str = ''
    call_count: int = 0
    last_called: str = ''

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'pitfalls': self.pitfalls,
            'standards': self.standards,
            'procedure': self.procedure,
            'call_count': self.call_count,
            'last_called': self.last_called,
        }


class DynamicLibrary:
    """Lazy-loading skill library with auto-discovery."""

    def __init__(self, skills_dir: str = None):
        if skills_dir is None:
            # Default: aerospace-valve-platform/skills/
            self.skills_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), '..', 'skills')
        else:
            self.skills_dir = skills_dir
        self._skills: Dict[str, Skill] = {}
        self._hot_reload: Dict[str, float] = {}  # filename -> mtime

    # ------------------------------------------------------------------
    # Discovery & Loading
    # ------------------------------------------------------------------

    def discover(self) -> List[str]:
        """Scan skills/ directory and return list of skill names found."""
        pattern = os.path.join(self.skills_dir, '*.SKILL.md')
        files = glob.glob(pattern)
        names = []
        for fpath in files:
            name = os.path.splitext(os.path.basename(fpath))[0]
            name = name.replace('.SKILL', '')  # solenoid.SKILL.md -> solenoid.SKILL -> solenoid
            names.append(name)
        return sorted(names)

    def load(self, name: str) -> Optional[Skill]:
        """Load a skill by name (lazy: only if not already loaded or file changed)."""
        # Check if already loaded and file unchanged
        if name in self._skills:
            fpath = self._skills[name].file_path
            if os.path.exists(fpath):
                mtime = os.path.getmtime(fpath)
                if self._hot_reload.get(name) == mtime:
                    self._skills[name].call_count += 1
                    self._skills[name].last_called = datetime.now().isoformat()
                    return self._skills[name]
                # File changed: reload
            else:
                del self._skills[name]

        # Find the file
        fpath = os.path.join(self.skills_dir, f'{name}.SKILL.md')
        if not os.path.exists(fpath):
            # Try alternate pattern
            pattern = os.path.join(self.skills_dir, f'*{name}*.SKILL.md')
            matches = glob.glob(pattern)
            if matches:
                fpath = matches[0]
            else:
                return None

        return self._load_file(name, fpath)

    def load_all(self) -> Dict[str, Skill]:
        """Load all skills in the directory."""
        names = self.discover()
        for name in names:
            self.load(name)
        return self._skills

    def _load_file(self, name: str, fpath: str) -> Optional[Skill]:
        """Parse a SKILL.md file into a Skill object."""
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return None

        skill = Skill(
            name=name,
            file_path=fpath,
            content=content,
            loaded_at=datetime.now().isoformat(),
            call_count=1,
            last_called=datetime.now().isoformat(),
        )

        # Parse frontmatter-style sections
        skill.description = self._extract_section(content, 'description', '# Description')
        skill.pitfalls = self._extract_list_section(content, 'Pitfalls')
        skill.standards = self._extract_list_section(content, 'Standards')
        skill.procedure = self._extract_list_section(content, 'Procedure')
        skill.parameters = self._extract_params(content)

        self._skills[name] = skill
        self._hot_reload[name] = os.path.getmtime(fpath)
        return skill

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_section(content: str, heading: str, alt_heading: str = '') -> str:
        """Extract text under a markdown heading."""
        patterns = [
            rf'^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)',
            rf'^#\s+{re.escape(heading)}\s*\n(.*?)(?=^#\s|\Z)',
        ]
        if alt_heading:
            patterns.insert(0, rf'^{re.escape(alt_heading)}\s*\n(.*?)(?=^##\s|\Z)')
        for pat in patterns:
            m = re.search(pat, content, re.MULTILINE | re.DOTALL)
            if m:
                return m.group(1).strip()
        return ''

    @staticmethod
    def _extract_list_section(content: str, heading: str) -> List[str]:
        """Extract bullet/numbered/emoji items under a heading."""
        text = DynamicLibrary._extract_section(content, heading)
        if not text:
            # Try with Chinese/English mixed headings
            for alt in [f'{heading}', f'{heading}', heading.replace('_', ' ')]:
                text = DynamicLibrary._extract_section(content, alt)
                if text:
                    break
        if not text:
            # Fuzzy match: find heading containing the keyword
            h_match = re.search(rf'^##\s+[^\n]*{re.escape(heading)}[^\n]*\s*\n(.*?)(?=^##\s|\Z)',
                               content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            if h_match:
                text = h_match.group(1).strip()
        if not text:
            return []
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Match bullet, numbered, emoji-prefixed items
            m = re.match(r'^[-*+✓⚠️❌✅🔴🟡🟢]\s*(.+)$', line)
            if m:
                items.append(m.group(1).strip())
                continue
            m = re.match(r'^\d+\.\s+(.+)$', line)
            if m:
                items.append(m.group(1).strip())
        return items

    @staticmethod
    def _extract_params(content: str) -> Dict:
        """Extract parameter table or list from SKILL.md."""
        params = {}
        # Try multiple heading variants
        for heading in ['Parameters', 'Input Parameters', 'Parameters', 'Parameters', '输入参数']:
            param_text = DynamicLibrary._extract_section(content, heading)
            if param_text:
                break
        if not param_text:
            # Fuzzy heading match: Chinese + English keywords
            h_match = re.search(r'^##\s+[^\n]*([Pp]aram|[Ii]nput|[参数輸入])[^\n]*\s*\n(.*?)(?=^##\s|\Z)',
                               content, re.MULTILINE | re.DOTALL)
            if h_match:
                param_text = h_match.group(2).strip()

        if not param_text:
            return params

        # Table format: | param | [unit] | [range/default] | [desc] |
        for line in param_text.split('\n'):
            line = line.strip()
            if line.startswith('|') and not re.match(r'^\|[\s\-:]+\|', line):
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if len(cells) >= 2:
                    key = cells[0].strip('`*_ ')
                    if not key or key.lower() in ('parameter', 'param', ''):
                        continue
                    # Try to parse a numeric default from any cell
                    default = cells[-1]  # Last cell as fallback
                    for c in cells[1:]:
                        try:
                            if c.replace('.', '').replace('-', '').replace('+', '').isdigit():
                                default = float(c)
                                break
                        except ValueError:
                            pass
                    desc = cells[-1] if len(cells) >= 2 else ''
                    params[key] = {'default': default, 'description': desc}

        # Fallback: key-value lines
        if not params:
            for line in param_text.split('\n'):
                line = line.strip()
                m = re.match(r'^[-*]\s+`?(\w+)`?\s*[:=]\s*(.+)$', line)
                if m:
                    key = m.group(1)
                    val = m.group(2).strip()
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                    params[key] = {'default': val, 'description': ''}

        return params

    # ------------------------------------------------------------------
    # Query & Search
    # ------------------------------------------------------------------

    def get(self, name: str) -> Optional[Skill]:
        """Get already-loaded skill (no file I/O). Returns None if not loaded."""
        return self._skills.get(name)

    def ensure(self, name: str) -> Optional[Skill]:
        """Load if needed, return skill."""
        return self.load(name)

    def search(self, query: str) -> List[Skill]:
        """Search loaded skills by name/description/content match."""
        results = []
        q = query.lower()
        for skill in self._skills.values():
            score = 0
            if q in skill.name.lower():
                score += 3
            if q in skill.description.lower():
                score += 2
            if q in skill.content.lower():
                score += 1
            if score > 0:
                results.append((score, skill))
        results.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in results]

    def reload(self, name: str = None) -> Optional[Skill]:
        """Force reload a skill (or all if name is None)."""
        if name:
            if name in self._skills:
                del self._skills[name]
            return self.load(name)
        else:
            self._skills.clear()
            self._hot_reload.clear()
            return None

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def stats(self) -> Dict:
        """Return library statistics."""
        return {
            'skills_dir': self.skills_dir,
            'loaded': len(self._skills),
            'names': list(self._skills.keys()),
            'total_calls': sum(s.call_count for s in self._skills.values()),
            'skills': {name: s.to_dict() for name, s in self._skills.items()},
        }

    def get_procedure_for(self, tool_name: str) -> Optional[str]:
        """Get the design procedure text for a given tool name."""
        # Map tool name to skill name
        tool_to_skill = {
            'analyze_solenoid_valve': 'solenoid',
            'analyze_pressure_valve': 'pressure_valve',
            'analyze_check_valve': 'check_valve',
            'design_spring': 'spring',
            'design_oring': 'oring',
            'design_seal': 'seal',
        }
        skill_name = tool_to_skill.get(tool_name, tool_name)
        skill = self.ensure(skill_name)
        if skill and skill.procedure:
            return '\n'.join(skill.procedure)
        if skill and skill.content:
            return skill.content[:500]
        return None

    def get_pitfalls_for(self, tool_name: str) -> List[str]:
        """Get known pitfalls for a given tool name."""
        tool_to_skill = {
            'analyze_solenoid_valve': 'solenoid',
            'analyze_pressure_valve': 'pressure_valve',
            'analyze_check_valve': 'check_valve',
            'design_spring': 'spring',
            'design_oring': 'oring',
            'design_seal': 'seal',
        }
        skill_name = tool_to_skill.get(tool_name, tool_name)
        skill = self.ensure(skill_name)
        return skill.pitfalls if skill else []


# ============================================================
# Singleton
# ============================================================

_library: Optional[DynamicLibrary] = None


def get_library(skills_dir: str = None) -> DynamicLibrary:
    global _library
    if _library is None:
        _library = DynamicLibrary(skills_dir)
    elif skills_dir and _library.skills_dir != skills_dir:
        _library = DynamicLibrary(skills_dir)
    return _library
