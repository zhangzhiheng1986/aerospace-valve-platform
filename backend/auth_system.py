#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
航空航天电磁阀研发平台 - 用户认证与管理系统
Authentication and User Management System

功能：
- 用户注册/登录/登出
- JWT Token认证
- 角色权限管理 (管理员/工程师/访客)
- 用户数据持久化
- 会话管理
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import jwt

# JWT配置
JWT_SECRET = secrets.token_hex(32)  # 生产环境应从环境变量读取
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# 用户数据文件路径
USERS_DB_FILE = os.path.join(os.path.dirname(__file__), 'data', 'users.json')
SESSIONS_DB_FILE = os.path.join(os.path.dirname(__file__), 'data', 'sessions.json')


class UserRole(Enum):
    """用户角色枚举"""
    ADMIN = "管理员"        # 完全权限
    ENGINEER = "工程师"     # 技术权限
    VIEWER = "访客"         # 只读权限


@dataclass
class User:
    """用户数据结构"""
    id: str                           # 用户ID (UUID)
    username: str                     # 用户名
    password_hash: str                # 密码哈希
    email: str                        # 邮箱
    role: str                         # 角色
    real_name: str                    # 真实姓名
    department: str                   # 部门
    created_at: str                   # 创建时间
    last_login: Optional[str] = None  # 最后登录时间
    is_active: bool = True            # 是否激活
    avatar: Optional[str] = None      # 头像URL
    
    def to_dict(self) -> Dict:
        """转换为字典（不含密码）"""
        data = asdict(self)
        del data['password_hash']
        return data


@dataclass
class Session:
    """会话数据结构"""
    token: str              # JWT Token
    user_id: str            # 用户ID
    created_at: str         # 创建时间
    expires_at: str         # 过期时间
    ip_address: Optional[str] = None  # IP地址
    user_agent: Optional[str] = None  # 浏览器标识


class AuthSystem:
    """认证系统核心类"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self._ensure_data_dir()
        self._load_data()
        self._create_default_admin()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        data_dir = os.path.dirname(USERS_DB_FILE)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def _load_data(self):
        """加载用户和会话数据"""
        # 加载用户
        if os.path.exists(USERS_DB_FILE):
            try:
                with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_data in data:
                        user = User(**user_data)
                        self.users[user.id] = user
            except Exception as e:
                print(f"Load users error: {e}")
        
        # 加载会话
        if os.path.exists(SESSIONS_DB_FILE):
            try:
                with open(SESSIONS_DB_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for session_data in data:
                        session = Session(**session_data)
                        self.sessions[session.token] = session
            except Exception as e:
                print(f"Load sessions error: {e}")
    
    def _save_users(self):
        """保存用户数据"""
        try:
            data = [asdict(user) for user in self.users.values()]
            with open(USERS_DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save users error: {e}")
    
    def _save_sessions(self):
        """保存会话数据"""
        try:
            data = [asdict(session) for session in self.sessions.values()]
            with open(SESSIONS_DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save sessions error: {e}")
    
    def _create_default_admin(self):
        """创建默认管理员账户"""
        if not any(u.role == UserRole.ADMIN.value for u in self.users.values()):
            admin = User(
                id=secrets.token_hex(8),
                username="admin",
                password_hash=self._hash_password("admin123"),
                email="admin@aerospace-valve.com",
                role=UserRole.ADMIN.value,
                real_name="系统管理员",
                department="系统管理部",
                created_at=datetime.now().isoformat()
            )
            self.users[admin.id] = admin
            self._save_users()
            print("Default admin created: admin / admin123")
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def _generate_token(user_id: str) -> str:
        """生成JWT Token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def _verify_token(token: str) -> Optional[str]:
        """验证JWT Token，返回用户ID或None"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    # ==================== 公共API ====================
    
    def register(self, username: str, password: str, email: str, 
                 real_name: str, department: str, role: str = UserRole.VIEWER.value) -> Tuple[bool, str]:
        """
        用户注册
        Returns: (success, message)
        """
        # 检查用户名是否已存在
        if any(u.username == username for u in self.users.values()):
            return False, "用户名已存在"
        
        # 检查邮箱是否已存在
        if any(u.email == email for u in self.users.values()):
            return False, "邮箱已被注册"
        
        # 验证角色
        valid_roles = [r.value for r in UserRole]
        if role not in valid_roles:
            return False, f"无效角色，可选: {valid_roles}"
        
        # 创建用户
        user = User(
            id=secrets.token_hex(8),
            username=username,
            password_hash=self._hash_password(password),
            email=email,
            role=role,
            real_name=real_name,
            department=department,
            created_at=datetime.now().isoformat()
        )
        
        self.users[user.id] = user
        self._save_users()
        
        return True, "注册成功"
    
    def login(self, username: str, password: str, 
              ip_address: Optional[str] = None, 
              user_agent: Optional[str] = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        用户登录
        Returns: (success, message, user_data_with_token)
        """
        # 查找用户
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            return False, "用户不存在", None
        
        # 验证密码
        if user.password_hash != self._hash_password(password):
            return False, "密码错误", None
        
        # 检查是否激活
        if not user.is_active:
            return False, "账户已被禁用", None
        
        # 生成Token
        token = self._generate_token(user.id)
        
        # 创建会话
        session = Session(
            token=token,
            user_id=user.id,
            created_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(hours=JWT_EXPIRATION_HOURS)).isoformat(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.sessions[token] = session
        
        # 更新最后登录时间
        user.last_login = datetime.now().isoformat()
        
        # 保存数据
        self._save_users()
        self._save_sessions()
        
        # 返回用户数据和Token
        user_data = user.to_dict()
        user_data['token'] = token
        
        return True, "登录成功", user_data
    
    def logout(self, token: str) -> Tuple[bool, str]:
        """用户登出"""
        if token in self.sessions:
            del self.sessions[token]
            self._save_sessions()
            return True, "登出成功"
        return False, "无效Token"
    
    def verify_session(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """
        验证会话
        Returns: (is_valid, user_data)
        """
        user_id = self._verify_token(token)
        if not user_id:
            return False, None
        
        if token not in self.sessions:
            return False, None
        
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return False, None
        
        return True, user.to_dict()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def get_all_users(self) -> List[Dict]:
        """获取所有用户（不含密码）"""
        return [user.to_dict() for user in self.users.values()]
    
    def update_user(self, user_id: str, **kwargs) -> Tuple[bool, str]:
        """
        更新用户信息
        可更新字段: email, real_name, department, role, is_active, avatar
        """
        user = self.users.get(user_id)
        if not user:
            return False, "用户不存在"
        
        allowed_fields = ['email', 'real_name', 'department', 'role', 'is_active', 'avatar']
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(user, key, value)
        
        self._save_users()
        return True, "更新成功"
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """修改密码"""
        user = self.users.get(user_id)
        if not user:
            return False, "用户不存在"
        
        if user.password_hash != self._hash_password(old_password):
            return False, "原密码错误"
        
        user.password_hash = self._hash_password(new_password)
        self._save_users()
        return True, "密码修改成功"
    
    def delete_user(self, user_id: str) -> Tuple[bool, str]:
        """删除用户"""
        if user_id not in self.users:
            return False, "用户不存在"
        
        # 不能删除最后一个管理员
        user = self.users[user_id]
        if user.role == UserRole.ADMIN.value:
            admin_count = sum(1 for u in self.users.values() if u.role == UserRole.ADMIN.value)
            if admin_count <= 1:
                return False, "不能删除最后一个管理员"
        
        del self.users[user_id]
        
        # 删除相关会话
        tokens_to_delete = [token for token, session in self.sessions.items() if session.user_id == user_id]
        for token in tokens_to_delete:
            del self.sessions[token]
        
        self._save_users()
        self._save_sessions()
        return True, "用户已删除"
    
    def get_user_statistics(self) -> Dict:
        """获取用户统计信息"""
        total = len(self.users)
        active = sum(1 for u in self.users.values() if u.is_active)
        by_role = {}
        for role in UserRole:
            count = sum(1 for u in self.users.values() if u.role == role.value)
            by_role[role.value] = count
        
        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'by_role': by_role,
            'online_sessions': len(self.sessions)
        }
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """
        检查用户权限
        permission: 'admin', 'engineer', 'viewer'
        """
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return False
        
        role_permissions = {
            UserRole.ADMIN.value: ['admin', 'engineer', 'viewer'],
            UserRole.ENGINEER.value: ['engineer', 'viewer'],
            UserRole.VIEWER.value: ['viewer']
        }
        
        return permission in role_permissions.get(user.role, [])


# 全局认证系统实例
auth = AuthSystem()
