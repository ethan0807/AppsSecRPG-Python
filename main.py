#!/usr/bin/env python3
"""
AppSec RPG: Guardians of the Code
OWASP Top 10 Quiz Combat Game
Built with Pygame - Retro Pixel Art Edition
"""

import pygame
import sys
import math
import random
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.font.init()

# =============================================================================
# CONSTANTS
# =============================================================================

# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Game
TILE_SIZE = 32
PLAYER_SPEED = 160  # pixels per second
PLAYER_SIZE = 24
ENEMY_SIZE = 24

# Colors - Retro terminal green palette
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BRIGHT_GREEN = (0, 255, 100)
DARK_GREEN = (0, 100, 0)
VERY_DARK_GREEN = (0, 40, 0)
RED = (255, 0, 0)
BRIGHT_RED = (255, 80, 80)
YELLOW = (255, 255, 0)
BRIGHT_YELLOW = (255, 255, 100)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
UI_BG = (0, 20, 0)
UI_BORDER = (0, 150, 0)
UI_TEXT = (0, 200, 0)
UI_TEXT_BRIGHT = (0, 255, 100)
MENU_SELECTED = (0, 80, 0)
MENU_SELECTED_BORDER = (0, 255, 100)
HUD_BG = (0, 0, 0, 200)
SCANLINE_ALPHA = 30

# Game States
class GameState(Enum):
    TITLE = "title"
    OVERWORLD = "overworld"
    COMBAT = "combat"
    PAUSED = "paused"
    DIALOGUE = "dialogue"
    VICTORY = "victory"
    GAME_OVER = "game_over"

# World Map (0 = floor, 1 = wall)
WORLD_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,1],
    [1,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,1],
    [1,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
    [1,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
    [1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

MAP_WIDTH = len(WORLD_MAP[0])
MAP_HEIGHT = len(WORLD_MAP)
WORLD_WIDTH = MAP_WIDTH * TILE_SIZE
WORLD_HEIGHT = MAP_HEIGHT * TILE_SIZE

# Player spawn (tile coordinates)
PLAYER_SPAWN = (20, 18)

# Enemy types with pixel art symbols
ENEMY_TYPES = {
    'INJECTION': {
        'name': 'Injection Demon',
        'symbol': 'SQL',
        'sprite_name': 'injection',
        'category': 'A03: Injection',
        'desc': 'Executes malicious SQL commands',
        'color': (200, 50, 50),
        'baseHp': 50,
        'baseAtk': 12,
        'xpReward': 50,
    },
    'XSS': {
        'name': 'XSS Specter',
        'symbol': '<X>',
        'sprite_name': 'xss',
        'category': 'A03: Injection',
        'desc': 'Injects malicious scripts',
        'color': (255, 140, 0),
        'baseHp': 45,
        'baseAtk': 14,
        'xpReward': 50,
    },
    'CRYPTO': {
        'name': 'Crypto Phantom',
        'symbol': '🔒',
        'sprite_name': 'crypto',
        'category': 'A02: Cryptographic Failures',
        'desc': 'Exposes sensitive data',
        'color': (180, 0, 180),
        'baseHp': 55,
        'baseAtk': 10,
        'xpReward': 55,
    },
    'ACCESS': {
        'name': 'Access Control Wraith',
        'symbol': '🔑',
        'sprite_name': 'access',
        'category': 'A01: Broken Access Control',
        'desc': 'Bypasses authorization checks',
        'color': (0, 180, 180),
        'baseHp': 60,
        'baseAtk': 11,
        'xpReward': 60,
    },
    'DESIGN': {
        'name': 'Insecure Design Golem',
        'symbol': '⚙',
        'sprite_name': 'design',
        'category': 'A04: Insecure Design',
        'desc': 'Missing security controls',
        'color': (120, 120, 0),
        'baseHp': 65,
        'baseAtk': 13,
        'xpReward': 65,
    },
    'CONFIG': {
        'name': 'Config Goblin',
        'symbol': '⚙',
        'sprite_name': 'config',
        'category': 'A05: Security Misconfiguration',
        'desc': 'Default creds, open ports',
        'color': (160, 80, 0),
        'baseHp': 40,
        'baseAtk': 15,
        'xpReward': 45,
    },
    'DESERIALIZE': {
        'name': 'Deserialization Wraith',
        'symbol': '📦',
        'sprite_name': 'deserialize',
        'category': 'A08: Software Integrity Failures',
        'desc': 'Untrusted data deserialization',
        'color': (100, 0, 150),
        'baseHp': 70,
        'baseAtk': 12,
        'xpReward': 70,
    },
    'LOGGING': {
        'name': 'Logging Phantom',
        'symbol': '📝',
        'sprite_name': 'logging',
        'category': 'A09: Logging Failures',
        'desc': 'Insufficient attack detection',
        'color': (80, 80, 80),
        'baseHp': 50,
        'baseAtk': 10,
        'xpReward': 50,
    },
}

ENEMY_SPAWNS = [
    {'x': 5, 'y': 5, 'type': 'INJECTION'},
    {'x': 45, 'y': 5, 'type': 'XSS'},
    {'x': 6, 'y': 18, 'type': 'CRYPTO'},
    {'x': 45, 'y': 18, 'type': 'ACCESS'},
    {'x': 10, 'y': 10, 'type': 'DESIGN'},
    {'x': 40, 'y': 10, 'type': 'CONFIG'},
    {'x': 10, 'y': 14, 'type': 'DESERIALIZE'},
    {'x': 40, 'y': 14, 'type': 'LOGGING'},
]

ENEMY_HP_SCALING = 1.3
ENEMY_ATK_SCALING = 1.2

# OWASP Top 10 Questions (23 questions across 10 categories)
QUESTIONS = {
    'A01: Broken Access Control': [
        {
            'question': 'What is Broken Access Control?',
            'choices': [
                'Users can access resources they should not',
                'Weak encryption algorithms',
                'SQL injection vulnerabilities',
                'Missing security logging'
            ],
            'answer': 0
        },
        {
            'question': 'Which is an example of Insecure Direct Object Reference (IDOR)?',
            'choices': [
                'Changing /user/123 to /user/124 to access another user data',
                'Injecting SQL via input fields',
                'Using default admin credentials',
                'Not logging failed login attempts'
            ],
            'answer': 0
        },
        {
            'question': 'How to prevent Broken Access Control?',
            'choices': [
                'Implement proper authorization checks on every request',
                'Use stronger encryption',
                'Sanitize all inputs',
                'Enable debug logging'
            ],
            'answer': 0
        }
    ],
    'A02: Cryptographic Failures': [
        {
            'question': 'What is a Cryptographic Failure?',
            'choices': [
                'Sensitive data exposed due to weak/no encryption',
                'Broken authentication logic',
                'Cross-site scripting attacks',
                'Insecure deserialization'
            ],
            'answer': 0
        },
        {
            'question': 'Which is a secure password hashing algorithm?',
            'choices': [
                'bcrypt or Argon2',
                'MD5',
                'SHA-1',
                'Base64 encoding'
            ],
            'answer': 0
        },
        {
            'question': 'What should NEVER be transmitted in plaintext?',
            'choices': [
                'Passwords and session tokens',
                'Public API documentation',
                'HTML content',
                'CSS stylesheets'
            ],
            'answer': 0
        }
    ],
    'A03: Injection': [
        {
            'question': 'What is SQL Injection?',
            'choices': [
                'Inserting malicious SQL via user input',
                'Injecting JavaScript into web pages',
                'Uploading malicious files',
                'Brute forcing passwords'
            ],
            'answer': 0
        },
        {
            'question': 'Best defense against SQL Injection?',
            'choices': [
                'Parameterized queries / prepared statements',
                'Escaping special characters',
                'Input validation only',
                'Using stored procedures only'
            ],
            'answer': 0
        },
        {
            'question': 'What is Cross-Site Scripting (XSS)?',
            'choices': [
                'Injecting malicious scripts into trusted websites',
                'Stealing database credentials',
                'Bypassing authentication',
                'Denial of service attacks'
            ],
            'answer': 0
        }
    ],
    'A04: Insecure Design': [
        {
            'question': 'What is Insecure Design?',
            'choices': [
                'Missing or ineffective security controls by design',
                'Implementation bugs in secure code',
                'Weak encryption algorithms',
                'Unpatched software'
            ],
            'answer': 0
        },
        {
            'question': 'How to address Insecure Design?',
            'choices': [
                'Threat modeling and secure design patterns',
                'More penetration testing',
                'Stronger firewalls',
                'Better logging'
            ],
            'answer': 0
        }
    ],
    'A05: Security Misconfiguration': [
        {
            'question': 'What is Security Misconfiguration?',
            'choices': [
                'Default configs, open ports, verbose errors',
                'Weak password policies',
                'SQL injection flaws',
                'Missing encryption'
            ],
            'answer': 0
        },
        {
            'question': 'Which is a security misconfiguration?',
            'choices': [
                'Directory listing enabled on web server',
                'Using parameterized queries',
                'Implementing rate limiting',
                'Encrypting data at rest'
            ],
            'answer': 0
        }
    ],
    'A06: Vulnerable Components': [
        {
            'question': 'What are Vulnerable and Outdated Components?',
            'choices': [
                'Using libraries with known vulnerabilities',
                'Custom code with bugs',
                'Weak encryption',
                'Missing access controls'
            ],
            'answer': 0
        },
        {
            'question': 'How to manage component vulnerabilities?',
            'choices': [
                'Software composition analysis (SCA) and regular updates',
                'Only use custom code',
                'Disable all third-party libraries',
                'Use older stable versions'
            ],
            'answer': 0
        }
    ],
    'A07: Authentication Failures': [
        {
            'question': 'What is an Authentication Failure?',
            'choices': [
                'Weak authentication allowing credential stuffing/brute force',
                'SQL injection in login form',
                'XSS on login page',
                'Missing HTTPS'
            ],
            'answer': 0
        },
        {
            'question': 'Best practice for authentication?',
            'choices': [
                'Multi-factor authentication (MFA) + rate limiting',
                'Complex password requirements only',
                'IP-based blocking only',
                'CAPTCHA on every request'
            ],
            'answer': 0
        }
    ],
    'A08: Software Integrity Failures': [
        {
            'question': 'What is Insecure Deserialization?',
            'choices': [
                'Untrusted data deserialized without validation',
                'Weak encryption of serialized data',
                'SQL injection via serialized objects',
                'XSS via JSON parsing'
            ],
            'answer': 0
        },
        {
            'question': 'How to prevent deserialization attacks?',
            'choices': [
                'Validate/verify serialized data, use safe formats (JSON)',
                'Encrypt all serialized data',
                'Disable serialization entirely',
                'Use only binary formats'
            ],
            'answer': 0
        }
    ],
    'A09: Logging Failures': [
        {
            'question': 'What is a Logging Failure?',
            'choices': [
                'Insufficient logging to detect attacks',
                'Logging too much data',
                'Logs stored in plaintext',
                'Logs not rotated'
            ],
            'answer': 0
        },
        {
            'question': 'What should security logs include?',
            'choices': [
                'Failed logins, access denials, input validation failures',
                'Only successful logins',
                'All HTTP requests',
                'Database query logs only'
            ],
            'answer': 0
        }
    ],
    'A10: SSRF': [
        {
            'question': 'What is Server-Side Request Forgery (SSRF)?',
            'choices': [
                'Server fetches attacker-controlled URLs',
                'Client-side request manipulation',
                'Cross-site request forgery',
                'SQL injection via HTTP headers'
            ],
            'answer': 0
        },
        {
            'question': 'How to prevent SSRF?',
            'choices': [
                'Validate/sanitize user-supplied URLs, allowlist destinations',
                'Disable all outbound HTTP requests',
                'Use HTTPS only',
                'Implement CORS headers'
            ],
            'answer': 0
        }
    ],
}

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Player:
    x: float
    y: float
    width: int = PLAYER_SIZE
    height: int = PLAYER_SIZE
    speed: float = PLAYER_SPEED
    vx: float = 0
    vy: float = 0
    facing: str = 'down'
    moving: bool = False
    anim_frame: int = 0
    anim_timer: float = 0
    
    # Stats
    max_hp: int = 100
    hp: int = 100
    atk: int = 15
    def_: int = 10
    level: int = 1
    exp: int = 0
    exp_to_next: int = 100
    
    # Combat stats
    enemies_defeated: int = 0
    questions_answered: int = 0
    accuracy: Dict[str, int] = field(default_factory=lambda: {'correct': 0, 'total': 0})
    
    # Visual effects
    damage_flash: float = 0
    heal_flash: float = 0
    invulnerable: bool = False
    invuln_timer: float = 0
    screen_shake: float = 0
    
    @property
    def rect(self) -> pygame.Rect:
        half_w, half_h = self.width // 2, self.height // 2
        return pygame.Rect(int(self.x - half_w), int(self.y - half_h), self.width, self.height)


@dataclass
class Enemy:
    id: str
    type: str
    name: str
    symbol: str
    sprite_name: str
    category: str
    description: str
    color: Tuple[int, int, int]
    x: float
    y: float
    spawn_tile: Tuple[int, int]
    width: int = ENEMY_SIZE
    height: int = ENEMY_SIZE
    max_hp: int = 50
    hp: int = 50
    atk: int = 10
    level: int = 1
    xp_reward: int = 50
    alive: bool = True
    defeated: bool = False
    defeated_timer: float = 0
    float_offset: float = 0
    float_dir: int = 1
    anim_frame: int = 0
    anim_timer: float = 0
    damage_flash: float = 0
    wander_target: Tuple[float, float] = (0, 0)
    ai_timer: float = 0
    
    @property
    def rect(self) -> pygame.Rect:
        half_w, half_h = self.width // 2, self.height // 2
        return pygame.Rect(int(self.x - half_w), int(self.y - half_h), self.width, self.height)


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: Tuple[int, int, int]
    life: float
    max_life: float
    size: int
    gravity: float = 0


@dataclass
class CombatState:
    active: bool = False
    enemy: Optional[Enemy] = None
    question: Optional[Dict] = None
    selected_answer: int = 0
    timer: float = 30.0
    max_timer: float = 30.0
    turn: str = 'player'  # 'player' or 'enemy'
    result: Optional[str] = None  # 'correct', 'incorrect', 'timeout'
    result_timer: float = 0
    damage_dealt: int = 0
    damage_taken: int = 0
    typewriter_text: str = ''
    typewriter_index: int = 0
    typewriter_timer: float = 0
    typewriter_speed: float = 30  # ms per character


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def check_collision(entity: Any, world_map: List[List[int]]) -> bool:
    """Check if entity collides with any wall tile."""
    half_w = entity.width / 2
    half_h = entity.height / 2
    
    left_tile = int((entity.x - half_w) // TILE_SIZE)
    right_tile = int((entity.x + half_w) // TILE_SIZE)
    top_tile = int((entity.y - half_h) // TILE_SIZE)
    bottom_tile = int((entity.y + half_h) // TILE_SIZE)
    
    for ty in range(top_tile, bottom_tile + 1):
        for tx in range(left_tile, right_tile + 1):
            if 0 <= ty < MAP_HEIGHT and 0 <= tx < MAP_WIDTH:
                if world_map[ty][tx] == 1:
                    return True
    return False


def resolve_collision(entity: Any, world_map: List[List[int]]):
    """Push entity out of walls."""
    half_w = entity.width / 2
    half_h = entity.height / 2
    
    left_tile = int((entity.x - half_w) // TILE_SIZE)
    right_tile = int((entity.x + half_w) // TILE_SIZE)
    top_tile = int((entity.y - half_h) // TILE_SIZE)
    bottom_tile = int((entity.y + half_h) // TILE_SIZE)
    
    for ty in range(top_tile, bottom_tile + 1):
        for tx in range(left_tile, right_tile + 1):
            if 0 <= ty < MAP_HEIGHT and 0 <= tx < MAP_WIDTH:
                if world_map[ty][tx] == 1:
                    tile_left = tx * TILE_SIZE
                    tile_right = tile_left + TILE_SIZE
                    tile_top = ty * TILE_SIZE
                    tile_bottom = tile_top + TILE_SIZE
                    
                    overlap_left = (entity.x + half_w) - tile_left
                    overlap_right = tile_right - (entity.x - half_w)
                    overlap_top = (entity.y + half_h) - tile_top
                    overlap_bottom = tile_bottom - (entity.y - half_h)
                    
                    min_overlap_x = min(overlap_left, overlap_right)
                    min_overlap_y = min(overlap_top, overlap_bottom)
                    
                    if min_overlap_x < min_overlap_y:
                        if overlap_left < overlap_right:
                            entity.x = tile_left - half_w - 0.1
                        else:
                            entity.x = tile_right + half_w + 0.1
                    else:
                        if overlap_top < overlap_bottom:
                            entity.y = tile_top - half_h - 0.1
                        else:
                            entity.y = tile_bottom + half_h + 0.1


def check_entity_collision(e1: Any, e2: Any) -> bool:
    """Check collision between two entities."""
    half_w1, half_h1 = e1.width / 2, e1.height / 2
    half_w2, half_h2 = e2.width / 2, e2.height / 2
    
    return (abs(e1.x - e2.x) < half_w1 + half_w2 and
            abs(e1.y - e2.y) < half_h1 + half_h2)


def resolve_entity_collision(e1: Any, e2: Any):
    """Push e1 out of e2 (solid collision)."""
    half_w1, half_h1 = e1.width / 2, e1.height / 2
    half_w2, half_h2 = e2.width / 2, e2.height / 2
    
    dx = e1.x - e2.x
    dy = e1.y - e2.y
    
    overlap_x = (half_w1 + half_w2) - abs(dx)
    overlap_y = (half_h1 + half_h2) - abs(dy)
    
    if overlap_x < overlap_y:
        if dx > 0:
            e1.x = e2.x + half_w1 + half_w2 + 0.1
        else:
            e1.x = e2.x - half_w1 - half_w2 - 0.1
    else:
        if dy > 0:
            e1.y = e2.y + half_h1 + half_h2 + 0.1
        else:
            e1.y = e2.y - half_h1 - half_h2 - 0.1


def create_enemy(spawn_data: Dict, level: int = 1) -> Enemy:
    """Create an enemy from spawn data."""
    type_data = ENEMY_TYPES[spawn_data['type']]
    scaling = ENEMY_HP_SCALING ** (level - 1)
    atk_scaling = ENEMY_ATK_SCALING ** (level - 1)
    
    return Enemy(
        id=f"enemy_{spawn_data['type']}_{spawn_data['x']}_{spawn_data['y']}_{random.randint(1000,9999)}",
        type=spawn_data['type'],
        name=type_data['name'],
        symbol=type_data['symbol'],
        sprite_name=type_data['sprite_name'],
        category=type_data['category'],
        description=type_data['desc'],
        color=type_data['color'],
        x=spawn_data['x'] * TILE_SIZE,
        y=spawn_data['y'] * TILE_SIZE,
        spawn_tile=(spawn_data['x'], spawn_data['y']),
        max_hp=int(type_data['baseHp'] * scaling),
        hp=int(type_data['baseHp'] * scaling),
        atk=int(type_data['baseAtk'] * atk_scaling),
        level=level,
        xp_reward=int(type_data['xpReward'] * scaling),
    )


def create_all_enemies(level: int = 1) -> List[Enemy]:
    """Create all enemies from spawn data."""
    return [create_enemy(spawn, level) for spawn in ENEMY_SPAWNS]


def get_random_question(category: str) -> Dict:
    """Get a random question for a category."""
    if category in QUESTIONS and QUESTIONS[category]:
        return random.choice(QUESTIONS[category])
    # Fallback
    return random.choice(QUESTIONS['A03: Injection'])


# =============================================================================
# PIXEL ART SPRITE GENERATION
# =============================================================================

def create_player_sprites() -> Dict[str, List[pygame.Surface]]:
    """Create retro pixel art sprites for player."""
    sprites = {'down': [], 'up': [], 'left': [], 'right': []}
    
    # 4 frames per direction (idle + 3 walk frames)
    for frame in range(4):
        # DOWN facing
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Body
        pygame.draw.rect(surf, (0, 200, 0), (10, 10, 12, 16))
        pygame.draw.rect(surf, (0, 150, 0), (10, 10, 12, 16), 1)
        # Head
        pygame.draw.rect(surf, (0, 220, 0), (11, 6, 10, 8))
        pygame.draw.rect(surf, (0, 170, 0), (11, 6, 10, 8), 1)
        # Eyes
        pygame.draw.rect(surf, BLACK, (13, 8, 2, 2))
        pygame.draw.rect(surf, BLACK, (17, 8, 2, 2))
        # Legs animation
        leg_offset = frame % 2 * 2
        pygame.draw.rect(surf, (0, 180, 0), (11, 24, 4, 6))
        pygame.draw.rect(surf, (0, 180, 0), (17, 24 + leg_offset, 4, 6))
        sprites['down'].append(surf)
        
        # UP facing
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 200, 0), (10, 10, 12, 16))
        pygame.draw.rect(surf, (0, 150, 0), (10, 10, 12, 16), 1)
        pygame.draw.rect(surf, (0, 220, 0), (11, 6, 10, 8))
        pygame.draw.rect(surf, (0, 170, 0), (11, 6, 10, 8), 1)
        # Eyes (back of head - just dots)
        pygame.draw.rect(surf, BLACK, (13, 8, 2, 2))
        pygame.draw.rect(surf, BLACK, (17, 8, 2, 2))
        leg_offset = frame % 2 * 2
        pygame.draw.rect(surf, (0, 180, 0), (11, 24, 4, 6))
        pygame.draw.rect(surf, (0, 180, 0), (17, 24 + leg_offset, 4, 6))
        sprites['up'].append(surf)
        
        # LEFT facing
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 200, 0), (10, 10, 12, 16))
        pygame.draw.rect(surf, (0, 150, 0), (10, 10, 12, 16), 1)
        pygame.draw.rect(surf, (0, 220, 0), (6, 6, 10, 8))  # Head left
        pygame.draw.rect(surf, (0, 170, 0), (6, 6, 10, 8), 1)
        pygame.draw.rect(surf, BLACK, (8, 8, 2, 2))  # One eye visible
        leg_offset = frame % 2 * 2
        pygame.draw.rect(surf, (0, 180, 0), (11, 24, 4, 6))
        pygame.draw.rect(surf, (0, 180, 0), (17, 24 + leg_offset, 4, 6))
        sprites['left'].append(surf)
        
        # RIGHT facing
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 200, 0), (10, 10, 12, 16))
        pygame.draw.rect(surf, (0, 150, 0), (10, 10, 12, 16), 1)
        pygame.draw.rect(surf, (0, 220, 0), (16, 6, 10, 8))  # Head right
        pygame.draw.rect(surf, (0, 170, 0), (16, 6, 10, 8), 1)
        pygame.draw.rect(surf, BLACK, (22, 8, 2, 2))  # One eye visible
        leg_offset = frame % 2 * 2
        pygame.draw.rect(surf, (0, 180, 0), (11, 24, 4, 6))
        pygame.draw.rect(surf, (0, 180, 0), (17, 24 + leg_offset, 4, 6))
        sprites['right'].append(surf)
    
    return sprites


def create_enemy_sprites() -> Dict[str, pygame.Surface]:
    """Create retro pixel art sprites for each enemy type."""
    sprites = {}
    
    for etype, data in ENEMY_TYPES.items():
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        color = data['color']
        dark_color = tuple(max(0, c - 60) for c in color)
        bright_color = tuple(min(255, c + 60) for c in color)
        
        if etype == 'INJECTION':
            # Red demon with horns
            pygame.draw.ellipse(surf, color, (6, 8, 20, 20))
            pygame.draw.ellipse(surf, dark_color, (6, 8, 20, 20), 2)
            # Horns
            pygame.draw.polygon(surf, dark_color, [(10, 10), (6, 2), (14, 10)])
            pygame.draw.polygon(surf, dark_color, [(22, 10), (26, 2), (18, 10)])
            # Eyes
            pygame.draw.rect(surf, YELLOW, (12, 14, 3, 3))
            pygame.draw.rect(surf, YELLOW, (17, 14, 3, 3))
            # Mouth
            pygame.draw.rect(surf, BLACK, (13, 20, 6, 2))
            
        elif etype == 'XSS':
            # Orange ghost with < > symbols
            pygame.draw.ellipse(surf, color, (4, 6, 24, 24))
            pygame.draw.ellipse(surf, dark_color, (4, 6, 24, 24), 2)
            # Wavy bottom
            for i in range(5):
                x = 6 + i * 4
                pygame.draw.arc(surf, color, (x, 24, 8, 10), 0, math.pi)
            # Eyes
            pygame.draw.rect(surf, WHITE, (11, 14, 4, 4))
            pygame.draw.rect(surf, WHITE, (17, 14, 4, 4))
            pygame.draw.rect(surf, BLACK, (12, 15, 2, 2))
            pygame.draw.rect(surf, BLACK, (18, 15, 2, 2))
            # <X> symbol
            font = pygame.font.Font(None, 16)
            text = font.render('<X>', True, WHITE)
            surf.blit(text, (10, 22))
            
        elif etype == 'CRYPTO':
            # Purple lock
            pygame.draw.rect(surf, dark_color, (9, 10, 14, 18), border_radius=2)
            pygame.draw.rect(surf, color, (9, 10, 14, 18), 2, border_radius=2)
            # Shackle
            pygame.draw.arc(surf, color, (8, 4, 16, 16), 0, math.pi, 3)
            # Keyhole
            pygame.draw.circle(surf, BLACK, (16, 16), 3)
            pygame.draw.rect(surf, BLACK, (15, 19, 2, 6))
            
        elif etype == 'ACCESS':
            # Cyan key
            pygame.draw.circle(surf, color, (10, 22), 6)
            pygame.draw.circle(surf, dark_color, (10, 22), 6, 2)
            pygame.draw.circle(surf, BLACK, (10, 22), 2)
            # Key shaft
            pygame.draw.rect(surf, color, (10, 16, 4, 10))
            # Teeth
            pygame.draw.rect(surf, color, (14, 18, 8, 3))
            pygame.draw.rect(surf, color, (14, 14, 6, 3))
            
        elif etype == 'DESIGN':
            # Yellow gear
            center = (16, 16)
            for i in range(8):
                angle = i * math.pi / 4
                x1 = center[0] + math.cos(angle) * 10
                y1 = center[1] + math.sin(angle) * 10
                x2 = center[0] + math.cos(angle) * 14
                y2 = center[1] + math.sin(angle) * 14
                pygame.draw.line(surf, color, (x1, y1), (x2, y2), 3)
            pygame.draw.circle(surf, color, center, 10)
            pygame.draw.circle(surf, dark_color, center, 10, 2)
            pygame.draw.circle(surf, BLACK, center, 4)
            
        elif etype == 'CONFIG':
            # Brown/orange config box
            pygame.draw.rect(surf, color, (6, 6, 20, 20), border_radius=3)
            pygame.draw.rect(surf, dark_color, (6, 6, 20, 20), 2, border_radius=3)
            # Sliders
            for i in range(3):
                y = 10 + i * 6
                pygame.draw.rect(surf, bright_color, (10, y, 12, 3))
                pygame.draw.rect(surf, WHITE, (10 + (i % 3) * 4, y, 3, 3))
            
        elif etype == 'DESERIALIZE':
            # Purple box with arrow
            pygame.draw.rect(surf, color, (6, 6, 20, 20), border_radius=2)
            pygame.draw.rect(surf, dark_color, (6, 6, 20, 20), 2, border_radius=2)
            # Arrow down
            pygame.draw.polygon(surf, WHITE, [(16, 10), (10, 16), (22, 16)])
            # Lines
            pygame.draw.line(surf, bright_color, (10, 20), (22, 20), 2)
            pygame.draw.line(surf, bright_color, (10, 23), (22, 23), 2)
            
        elif etype == 'LOGGING':
            # Gray document
            pygame.draw.rect(surf, color, (8, 4, 16, 24), border_radius=1)
            pygame.draw.rect(surf, dark_color, (8, 4, 16, 24), 2, border_radius=1)
            # Lines
            for i in range(5):
                y = 10 + i * 4
                pygame.draw.line(surf, WHITE, (11, y), (21, y), 1)
            # Corner fold
            pygame.draw.polygon(surf, dark_color, [(20, 4), (24, 4), (24, 8)])
        
        sprites[etype] = surf
    
    return sprites


def create_tile_sprites() -> Dict[int, pygame.Surface]:
    """Create tile sprites for the world map."""
    sprites = {}
    
    # Floor tile (0)
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    surf.fill(VERY_DARK_GREEN)
    # Subtle grid pattern
    for x in range(0, TILE_SIZE, 8):
        pygame.draw.line(surf, (0, 50, 0), (x, 0), (x, TILE_SIZE))
    for y in range(0, TILE_SIZE, 8):
        pygame.draw.line(surf, (0, 50, 0), (0, y), (TILE_SIZE, y))
    # Random noise
    for _ in range(3):
        x = random.randint(0, TILE_SIZE - 1)
        y = random.randint(0, TILE_SIZE - 1)
        surf.set_at((x, y), (0, 80, 0))
    sprites[0] = surf
    
    # Wall tile (1)
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    surf.fill((0, 60, 0))
    # Brick pattern
    for row in range(4):
        y = row * 8
        offset = 16 if row % 2 == 1 else 0
        for col in range(3):
            x = col * 16 + offset
            pygame.draw.rect(surf, (0, 80, 0), (x % TILE_SIZE, y, 14, 6))
            pygame.draw.rect(surf, (0, 40, 0), (x % TILE_SIZE, y, 14, 6), 1)
    sprites[1] = surf
    
    return sprites


# =============================================================================
# PARTICLE SYSTEM
# =============================================================================

class ParticleSystem:
    def __init__(self, max_particles: int = 300):
        self.particles: List[Particle] = []
        self.max_particles = max_particles
    
    def add(self, x: float, y: float, color: Tuple[int, int, int],
            velocity: Tuple[float, float], lifetime: float = 800,
            size: int = 3, gravity: float = 0):
        if len(self.particles) >= self.max_particles:
            self.particles.pop(0)
        self.particles.append(Particle(
            x=x, y=y,
            vx=velocity[0], vy=velocity[1],
            color=color,
            life=lifetime, max_life=lifetime,
            size=size, gravity=gravity
        ))
    
    def add_explosion(self, x: float, y: float, color: Tuple[int, int, int], count: int = 16):
        for _ in range(count):
            angle = random.random() * 2 * math.pi
            speed = 60 + random.random() * 140
            self.add(x, y, color,
                     (math.cos(angle) * speed, math.sin(angle) * speed),
                     400 + random.random() * 400,
                     random.randint(2, 5), 0.1)
    
    def add_damage_number(self, x: float, y: float, amount: int, color: Tuple[int, int, int]):
        """Add floating damage number."""
        # This would need text rendering - simplified as particles
        for _ in range(8):
            angle = random.random() * 2 * math.pi
            speed = 30 + random.random() * 60
            self.add(x, y, color,
                     (math.cos(angle) * speed, math.sin(angle) * speed),
                     600, random.randint(3, 5), -0.05)
    
    def add_heal_effect(self, x: float, y: float):
        for _ in range(12):
            angle = random.random() * 2 * math.pi
            speed = 20 + random.random() * 40
            self.add(x, y, BRIGHT_GREEN,
                     (math.cos(angle) * speed, math.sin(angle) * speed),
                     800, random.randint(3, 6), -0.1)
    
    def update(self, dt: float):
        for p in self.particles[:]:
            p.life -= dt
            if p.life <= 0:
                self.particles.remove(p)
                continue
            p.vy += p.gravity * dt / 1000
            p.x += p.vx * dt / 1000
            p.y += p.vy * dt / 1000
    
    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        for p in self.particles:
            alpha = int(255 * (p.life / p.max_life))
            color = (*p.color, alpha)
            screen_x = int(p.x - camera_x)
            screen_y = int(p.y - camera_y)
            if -10 < screen_x < SCREEN_WIDTH + 10 and -10 < screen_y < SCREEN_HEIGHT + 10:
                pygame.draw.circle(surface, p.color, (screen_x, screen_y), max(1, p.size))


# =============================================================================
# RENDERER - RETRO PIXEL ART STYLE
# =============================================================================

class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        self.font_tiny = pygame.font.Font(None, 16)
        self.font_pixel = pygame.font.SysFont('Courier New', 14, bold=True)
        
        # Create pixel art assets
        self.player_sprites = create_player_sprites()
        self.enemy_sprites = create_enemy_sprites()
        self.tile_sprites = create_tile_sprites()
        
        # Pre-create UI surfaces
        self.create_scanline_surface()
        self.create_vignette_surface()
    
    def create_scanline_surface(self):
        """Create scanline overlay for CRT effect."""
        self.scanline_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 2):
            pygame.draw.line(self.scanline_surface, (0, 0, 0, SCANLINE_ALPHA), (0, y), (SCREEN_WIDTH, y))
    
    def create_vignette_surface(self):
        """Create vignette overlay."""
        self.vignette_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        max_dist = math.hypot(center_x, center_y)
        for y in range(SCREEN_HEIGHT):
            for x in range(SCREEN_WIDTH):
                dist = math.hypot(x - center_x, y - center_y)
                alpha = int(40 * (dist / max_dist) ** 2)
                if alpha > 0:
                    self.vignette_surface.set_at((x, y), (0, 0, 0, alpha))
    
    def draw_text_with_shadow(self, surface: pygame.Surface, text: str, font: pygame.font.Font,
                              x: int, y: int, color: Tuple[int, int, int],
                              shadow_color: Tuple[int, int, int] = BLACK,
                              center: bool = False):
        """Draw text with drop shadow."""
        text_surf = font.render(text, True, color)
        shadow_surf = font.render(text, True, shadow_color)
        if center:
            x -= text_surf.get_width() // 2
        surface.blit(shadow_surf, (x + 2, y + 2))
        surface.blit(text_surf, (x, y))
        return text_surf.get_width(), text_surf.get_height()
    
    def draw_panel(self, surface: pygame.Surface, x: int, y: int, w: int, h: int,
                   border_color: Tuple[int, int, int] = UI_BORDER,
                   bg_color: Tuple[int, int, int] = UI_BG):
        """Draw a retro UI panel."""
        # Background
        pygame.draw.rect(surface, bg_color, (x, y, w, h))
        # Border
        pygame.draw.rect(surface, border_color, (x, y, w, h), 2)
        # Inner highlight
        pygame.draw.rect(surface, (0, 100, 0), (x + 2, y + 2, w - 4, h - 4), 1)
        # Corner brackets
        bracket_size = 8
        corners = [
            (x, y), (x + w - bracket_size, y),
            (x, y + h - bracket_size), (x + w - bracket_size, y + h - bracket_size)
        ]
        for cx, cy in corners:
            pygame.draw.line(surface, UI_TEXT_BRIGHT, (cx, cy), (cx + bracket_size, cy), 2)
            pygame.draw.line(surface, UI_TEXT_BRIGHT, (cx, cy), (cx, cy + bracket_size), 2)
            pygame.draw.line(surface, UI_TEXT_BRIGHT, (cx + bracket_size, cy + bracket_size), (cx, cy + bracket_size), 2)
            pygame.draw.line(surface, UI_TEXT_BRIGHT, (cx + bracket_size, cy + bracket_size), (cx + bracket_size, cy), 2)
    
    def draw_world(self, camera_x: float, camera_y: float):
        """Draw the world map with pixel art tiles."""
        # Visible tile range
        start_tx = max(0, int(camera_x // TILE_SIZE))
        end_tx = min(MAP_WIDTH, int((camera_x + SCREEN_WIDTH) // TILE_SIZE) + 1)
        start_ty = max(0, int(camera_y // TILE_SIZE))
        end_ty = min(MAP_HEIGHT, int((camera_y + SCREEN_HEIGHT) // TILE_SIZE) + 1)
        
        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                tile_type = WORLD_MAP[ty][tx]
                sprite = self.tile_sprites[tile_type]
                screen_x = tx * TILE_SIZE - camera_x
                screen_y = ty * TILE_SIZE - camera_y
                self.screen.blit(sprite, (screen_x, screen_y))
    
    def draw_player(self, player: Player, camera_x: float, camera_y: float):
        """Draw player with pixel art sprite."""
        screen_x = int(player.x - camera_x)
        screen_y = int(player.y - camera_y)
        
        # Select sprite
        facing = player.facing
        if facing not in self.player_sprites:
            facing = 'down'
        frame = player.anim_frame if player.moving else 0
        sprite = self.player_sprites[facing][frame]
        
        # Apply effects
        if player.invulnerable and int(player.invuln_timer / 100) % 2 == 0:
            # Flashing when invulnerable
            return
        
        # Damage flash
        if player.damage_flash > 0:
            flash_surf = sprite.copy()
            flash_surf.fill((255, 50, 50, 180), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(flash_surf, (screen_x - 16, screen_y - 16))
        elif player.heal_flash > 0:
            flash_surf = sprite.copy()
            flash_surf.fill((50, 255, 50, 180), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(flash_surf, (screen_x - 16, screen_y - 16))
        else:
            self.screen.blit(sprite, (screen_x - 16, screen_y - 16))
        
        # Health bar above player
        if player.hp < player.max_hp:
            bar_w = 30
            bar_h = 4
            bx = screen_x - bar_w // 2
            by = screen_y - 28
            pygame.draw.rect(self.screen, DARK_GREEN, (bx, by, bar_w, bar_h))
            hp_w = int(bar_w * player.hp / player.max_hp)
            pygame.draw.rect(self.screen, GREEN, (bx, by, hp_w, bar_h))
            pygame.draw.rect(self.screen, UI_BORDER, (bx, by, bar_w, bar_h), 1)
    
    def draw_enemy(self, enemy: Enemy, camera_x: float, camera_y: float):
        """Draw enemy with pixel art sprite."""
        if not enemy.alive and enemy.defeated_timer >= 500:
            return
        
        screen_x = int(enemy.x - camera_x)
        screen_y = int(enemy.y - camera_y) + int(enemy.float_offset)
        
        # Get sprite
        sprite = self.enemy_sprites.get(enemy.type)
        if sprite:
            # Apply effects
            if enemy.defeated:
                # Fade out
                alpha = max(0, 255 - int(enemy.defeated_timer / 500 * 255))
                sprite_copy = sprite.copy()
                sprite_copy.set_alpha(alpha)
                self.screen.blit(sprite_copy, (screen_x - 16, screen_y - 16))
            elif enemy.damage_flash > 0:
                flash_surf = sprite.copy()
                flash_surf.fill((255, 100, 100, 200), special_flags=pygame.BLEND_RGBA_MULT)
                self.screen.blit(flash_surf, (screen_x - 16, screen_y - 16))
            else:
                self.screen.blit(sprite, (screen_x - 16, screen_y - 16))
        else:
            # Fallback: colored box with symbol
            pygame.draw.rect(self.screen, enemy.color, (screen_x - 12, screen_y - 12, 24, 24))
            pygame.draw.rect(self.screen, WHITE, (screen_x - 12, screen_y - 12, 24, 24), 2)
            font = pygame.font.Font(None, 20)
            text = font.render(enemy.symbol, True, WHITE)
            self.screen.blit(text, (screen_x - text.get_width() // 2, screen_y - 10))
        
        # Health bar
        if enemy.alive and enemy.hp < enemy.max_hp:
            bar_w = 32
            bar_h = 4
            bx = screen_x - bar_w // 2
            by = screen_y - 28
            pygame.draw.rect(self.screen, DARK_GREEN, (bx, by, bar_w, bar_h))
            hp_w = int(bar_w * enemy.hp / enemy.max_hp)
            hp_color = GREEN if enemy.hp > enemy.max_hp * 0.3 else RED
            pygame.draw.rect(self.screen, hp_color, (bx, by, hp_w, bar_h))
            pygame.draw.rect(self.screen, UI_BORDER, (bx, by, bar_w, bar_h), 1)
        
        # Name label (when close to player)
        # TODO: Could add proximity-based name display
    
    def draw_particles(self, particles: ParticleSystem, camera_x: float, camera_y: float):
        particles.draw(self.screen, camera_x, camera_y)
    
    def draw_hud(self, player: Player):
        """Draw retro HUD."""
        # Top panel
        panel_h = 50
        self.draw_panel(self.screen, 5, 5, SCREEN_WIDTH - 10, panel_h)
        
        # Health
        self.draw_text_with_shadow(self.screen, "HP", self.font_small, 20, 12, UI_TEXT)
        bar_w = 150
        bar_h = 16
        bx = 50
        by = 12
        pygame.draw.rect(self.screen, VERY_DARK_GREEN, (bx, by, bar_w, bar_h))
        pygame.draw.rect(self.screen, DARK_GREEN, (bx, by, bar_w, bar_h), 1)
        hp_w = int(bar_w * player.hp / player.max_hp)
        hp_color = GREEN if player.hp > player.max_hp * 0.3 else RED
        pygame.draw.rect(self.screen, hp_color, (bx, by, hp_w, bar_h))
        hp_text = f"{player.hp}/{player.max_hp}"
        self.draw_text_with_shadow(self.screen, hp_text, self.font_tiny, bx + bar_w // 2, by + 1, UI_TEXT_BRIGHT, center=True)
        
        # EXP
        self.draw_text_with_shadow(self.screen, "EXP", self.font_small, 220, 12, UI_TEXT)
        exp_w = 120
        ex = 260
        ey = 12
        pygame.draw.rect(self.screen, VERY_DARK_GREEN, (ex, ey, exp_w, bar_h))
        pygame.draw.rect(self.screen, DARK_GREEN, (ex, ey, exp_w, bar_h), 1)
        exp_fill = int(exp_w * player.exp / player.exp_to_next)
        pygame.draw.rect(self.screen, YELLOW, (ex, ey, exp_fill, bar_h))
        exp_text = f"{player.exp}/{player.exp_to_next}"
        self.draw_text_with_shadow(self.screen, exp_text, self.font_tiny, ex + exp_w // 2, ey + 1, BRIGHT_YELLOW, center=True)
        
        # Level
        self.draw_text_with_shadow(self.screen, f"LV {player.level}", self.font_medium, 400, 10, UI_TEXT_BRIGHT)
        
        # Stats
        self.draw_text_with_shadow(self.screen, f"ATK {player.atk}  DEF {player.def_}", self.font_small, 400, 32, UI_TEXT)
        
        # Defeated count
        self.draw_text_with_shadow(self.screen, f"DEFEATED: {player.enemies_defeated}/8", self.font_small, 600, 12, UI_TEXT_BRIGHT)
        
        # Accuracy
        if player.accuracy['total'] > 0:
            acc = player.accuracy['correct'] * 100 // player.accuracy['total']
            self.draw_text_with_shadow(self.screen, f"ACC: {acc}%", self.font_small, 600, 32, UI_TEXT)
        
        # Mini-map (top right)
        self.draw_minimap(player)
    
    def draw_minimap(self, player: Player):
        """Draw minimap in top right."""
        mm_size = 120
        mm_x = SCREEN_WIDTH - mm_size - 10
        mm_y = 10
        scale = mm_size / max(MAP_WIDTH, MAP_HEIGHT)
        
        # Background
        self.draw_panel(self.screen, mm_x - 2, mm_y - 2, mm_size + 4, mm_size + 4,
                       border_color=DARK_GREEN, bg_color=VERY_DARK_GREEN)
        
        # Draw map
        for ty in range(MAP_HEIGHT):
            for tx in range(MAP_WIDTH):
                if WORLD_MAP[ty][tx] == 1:
                    px = mm_x + int(tx * scale)
                    py = mm_y + int(ty * scale)
                    pw = max(1, int(scale))
                    ph = max(1, int(scale))
                    pygame.draw.rect(self.screen, DARK_GREEN, (px, py, pw, ph))
        
        # Player dot
        px = mm_x + int(player.x / TILE_SIZE * scale)
        py = mm_y + int(player.y / TILE_SIZE * scale)
        pygame.draw.circle(self.screen, BRIGHT_GREEN, (px, py), 3)
        
        # Enemy dots
        for enemy in getattr(self, 'enemies', []):
            if enemy.alive:
                ex = mm_x + int(enemy.x / TILE_SIZE * scale)
                ey = mm_y + int(enemy.y / TILE_SIZE * scale)
                pygame.draw.circle(self.screen, RED, (ex, ey), 2)
    
    def draw_combat(self, combat: CombatState, player: Player):
        """Draw combat overlay with retro terminal style."""
        # Full screen overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        
        # Combat panel
        panel_w = 700
        panel_h = 450
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2
        self.draw_panel(self.screen, panel_x, panel_y, panel_w, panel_h)
        
        # Header
        header_y = panel_y + 15
        self.draw_text_with_shadow(self.screen, "⚔ COMBAT INITIATED ⚔", self.font_medium,
                                  panel_x + panel_w // 2, header_y, UI_TEXT_BRIGHT, center=True)
        
        # Enemy info
        if combat.enemy:
            enemy = combat.enemy
            info_y = header_y + 35
            self.draw_text_with_shadow(self.screen, f"THREAT: {enemy.name}", self.font_medium,
                                      panel_x + 20, info_y, enemy.color)
            self.draw_text_with_shadow(self.screen, f"TYPE: {enemy.category}", self.font_small,
                                      panel_x + 20, info_y + 25, UI_TEXT)
            self.draw_text_with_shadow(self.screen, enemy.description, self.font_tiny,
                                      panel_x + 20, info_y + 48, UI_TEXT)
            
            # Enemy HP bar
            hp_y = info_y + 70
            self.draw_text_with_shadow(self.screen, "ENEMY HP", self.font_small,
                                      panel_x + 20, hp_y, UI_TEXT)
            bar_w = 300
            bar_h = 16
            bx = panel_x + 20
            by = hp_y + 20
            pygame.draw.rect(self.screen, VERY_DARK_GREEN, (bx, by, bar_w, bar_h))
            pygame.draw.rect(self.screen, DARK_GREEN, (bx, by, bar_w, bar_h), 1)
            hp_fill = int(bar_w * max(0, enemy.hp) / enemy.max_hp)
            hp_color = GREEN if enemy.hp > enemy.max_hp * 0.3 else RED
            pygame.draw.rect(self.screen, hp_color, (bx, by, hp_fill, bar_h))
            hp_text = f"{max(0, enemy.hp)}/{enemy.max_hp}"
            self.draw_text_with_shadow(self.screen, hp_text, self.font_tiny,
                                      bx + bar_w // 2, by + 1, UI_TEXT_BRIGHT, center=True)
            
            # Player HP in combat
            self.draw_text_with_shadow(self.screen, "YOUR HP", self.font_small,
                                      panel_x + 350, hp_y, UI_TEXT)
            bx2 = panel_x + 350
            pygame.draw.rect(self.screen, VERY_DARK_GREEN, (bx2, by, bar_w, bar_h))
            pygame.draw.rect(self.screen, DARK_GREEN, (bx2, by, bar_w, bar_h), 1)
            hp_fill2 = int(bar_w * player.hp / player.max_hp)
            pygame.draw.rect(self.screen, GREEN, (bx2, by, hp_fill2, bar_h))
            hp_text2 = f"{player.hp}/{player.max_hp}"
            self.draw_text_with_shadow(self.screen, hp_text2, self.font_tiny,
                                      bx2 + bar_w // 2, by + 1, UI_TEXT_BRIGHT, center=True)
            
            # Timer
            timer_y = by + bar_h + 15
            timer_pct = combat.timer / combat.max_timer
            timer_w = int(300 * timer_pct)
            timer_color = GREEN if timer_pct > 0.5 else (YELLOW if timer_pct > 0.25 else RED)
            self.draw_text_with_shadow(self.screen, f"TIME: {combat.timer:.1f}s", self.font_small,
                                      panel_x + 20, timer_y, timer_color)
            pygame.draw.rect(self.screen, VERY_DARK_GREEN, (panel_x + 20, timer_y + 20, 300, 8))
            pygame.draw.rect(self.screen, timer_color, (panel_x + 20, timer_y + 20, timer_w, 8))
        
        # Question
        if combat.question:
            q_y = panel_y + 180
            self.draw_text_with_shadow(self.screen, "SECURITY QUESTION:", self.font_small,
                                      panel_x + 20, q_y, YELLOW)
            
            # Typewriter text
            q_text = combat.typewriter_text if combat.typewriter_text else combat.question['question']
            self.draw_text_wrapped(q_text, self.font_small, panel_x + 20, q_y + 25,
                                  panel_w - 40, UI_TEXT_BRIGHT)
            
            # Choices
            choice_y = q_y + 100
            for i, choice in enumerate(combat.question['choices']):
                color = UI_TEXT_BRIGHT if i == combat.selected_answer else UI_TEXT
                prefix = "► " if i == combat.selected_answer else "  "
                self.draw_text_with_shadow(self.screen, f"{prefix}{chr(65+i)}) {choice}",
                                          self.font_small, panel_x + 40, choice_y + i * 35, color)
            
            # Result feedback
            if combat.result:
                res_y = choice_y + 150
                if combat.result == 'correct':
                    res_text = f"✓ CORRECT! Damage dealt: {combat.damage_dealt}"
                    res_color = GREEN
                elif combat.result == 'incorrect':
                    res_text = f"✗ WRONG! Damage taken: {combat.damage_taken}"
                    res_color = RED
                else:  # timeout
                    res_text = f"⏱ TIME OUT! Damage taken: {combat.damage_taken}"
                    res_color = RED
                
                self.draw_text_with_shadow(self.screen, res_text, self.font_medium,
                                          panel_x + panel_w // 2, res_y, res_color, center=True)
                
                # Continue prompt
                cont_y = res_y + 40
                alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() / 200))
                cont_color = (0, 255, 100, alpha)
                cont_surf = self.font_small.render("Press ENTER to continue...", True, UI_TEXT_BRIGHT)
                self.screen.blit(cont_surf, (panel_x + panel_w // 2 - cont_surf.get_width() // 2, cont_y))
    
    def draw_text_wrapped(self, text: str, font: pygame.font.Font, x: int, y: int,
                          max_width: int, color: Tuple[int, int, int]):
        """Draw word-wrapped text."""
        words = text.split(' ')
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_surf = font.render(word + ' ', True, color)
            word_w = word_surf.get_width()
            if current_width + word_w > max_width:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_w
            else:
                current_line.append(word)
                current_width += word_w
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines):
            self.draw_text_with_shadow(self.screen, line, font, x, y + i * 22, color)
    
    def draw_pause_menu(self, selection: int):
        """Draw pause menu with highlighted selection."""
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        panel_w = 400
        panel_h = 300
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2
        self.draw_panel(self.screen, panel_x, panel_y, panel_w, panel_h)
        
        # Title
        self.draw_text_with_shadow(self.screen, "◆ PAUSED ◆", self.font_large,
                                  panel_x + panel_w // 2, panel_y + 20, UI_TEXT_BRIGHT, center=True)
        
        options = ["Resume Game", "View Stats", "Controls", "Quit to Title"]
        for i, opt in enumerate(options):
            y = panel_y + 80 + i * 45
            if i == selection:
                # Highlight background
                pygame.draw.rect(self.screen, MENU_SELECTED,
                               (panel_x + 20, y - 5, panel_w - 40, 35))
                pygame.draw.rect(self.screen, MENU_SELECTED_BORDER,
                               (panel_x + 20, y - 5, panel_w - 40, 35), 2)
                # Selection arrow
                self.draw_text_with_shadow(self.screen, "►", self.font_medium,
                                          panel_x + 30, y, UI_TEXT_BRIGHT)
                self.draw_text_with_shadow(self.screen, opt, self.font_medium,
                                          panel_x + 60, y, UI_TEXT_BRIGHT)
            else:
                self.draw_text_with_shadow(self.screen, opt, self.font_medium,
                                          panel_x + 60, y, UI_TEXT)
        
        # Hint
        self.draw_text_with_shadow(self.screen, "↑/↓ Navigate  •  ENTER Select  •  ESC Close",
                                  self.font_tiny, panel_x + panel_w // 2,
                                  panel_y + panel_h - 30, GRAY, center=True)
    
    def draw_dialogue_box(self, text: str, speaker: str):
        """Draw dialogue box at bottom."""
        box_h = 160
        box_y = SCREEN_HEIGHT - box_h - 10
        self.draw_panel(self.screen, 10, box_y, SCREEN_WIDTH - 20, box_h)
        
        # Speaker name
        self.draw_text_with_shadow(self.screen, f"[{speaker}]", self.font_medium,
                                  25, box_y + 10, YELLOW)
        
        # Text with typewriter effect would go here - simplified
        self.draw_text_wrapped(text, self.font_small, 25, box_y + 40,
                              SCREEN_WIDTH - 50, UI_TEXT_BRIGHT)
        
        # Continue prompt
        prompt = "Press SPACE/ENTER to continue..."
        prompt_surf = self.font_tiny.render(prompt, True, GRAY)
        self.screen.blit(prompt_surf, (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2,
                                       box_y + box_h - 25))
    
    def draw_title(self, anim_time: float):
        """Draw retro title screen."""
        self.screen.fill(BLACK)
        
        # Background pattern
        for y in range(0, SCREEN_HEIGHT, 40):
            for x in range(0, SCREEN_WIDTH, 40):
                offset = int(anim_time / 200) % 2
                if (x + y + offset * 20) % 80 < 40:
                    pygame.draw.rect(self.screen, VERY_DARK_GREEN, (x, y, 40, 40))
        
        # Title
        title_y = 100 + int(10 * math.sin(anim_time / 500))
        self.draw_text_with_shadow(self.screen, "APPSEC RPG", self.font_large,
                                  SCREEN_WIDTH // 2, title_y, UI_TEXT_BRIGHT, center=True)
        self.draw_text_with_shadow(self.screen, "GUARDIANS OF THE CODE", self.font_medium,
                                  SCREEN_WIDTH // 2, title_y + 50, GREEN, center=True)
        
        # Subtitle
        self.draw_text_with_shadow(self.screen, "OWASP Top 10 Quiz Combat", self.font_small,
                                  SCREEN_WIDTH // 2, title_y + 100, UI_TEXT, center=True)
        
        # Version
        self.draw_text_with_shadow(self.screen, "v1.0.0  •  Python + Pygame", self.font_tiny,
                                  SCREEN_WIDTH // 2, title_y + 130, GRAY, center=True)
        
        # Enemy showcase
        showcase_y = title_y + 180
        self.draw_text_with_shadow(self.screen, "THREATS TO DEFEAT:", self.font_small,
                                  SCREEN_WIDTH // 2, showcase_y, YELLOW, center=True)
        
        enemy_list = list(ENEMY_TYPES.items())
        for i, (etype, data) in enumerate(enemy_list):
            col = i % 4
            row = i // 4
            ex = SCREEN_WIDTH // 2 - 300 + col * 150
            ey = showcase_y + 30 + row * 60
            
            # Draw mini sprite
            sprite = self.enemy_sprites.get(etype)
            if sprite:
                mini = pygame.transform.scale(sprite, (32, 32))
                self.screen.blit(mini, (ex, ey))
            
            self.draw_text_with_shadow(self.screen, data['name'], self.font_tiny,
                                      ex + 40, ey + 5, UI_TEXT)
            self.draw_text_with_shadow(self.screen, data['category'], self.font_tiny,
                                      ex + 40, ey + 20, GRAY)
        
        # Start prompt
        prompt_y = SCREEN_HEIGHT - 80
        alpha = int(128 + 127 * math.sin(anim_time / 300))
        prompt_color = (min(255, UI_TEXT_BRIGHT[0] + alpha // 4),
                       min(255, UI_TEXT_BRIGHT[1] + alpha // 4),
                       min(255, UI_TEXT_BRIGHT[2] + alpha // 4))
        self.draw_text_with_shadow(self.screen, "PRESS ENTER TO START", self.font_medium,
                                  SCREEN_WIDTH // 2, prompt_y, prompt_color, center=True)
        
        # Controls hint
        self.draw_text_with_shadow(self.screen, "WASD/Arrows: Move  •  SPACE/ENTER: Interact  •  ESC: Pause",
                                  self.font_tiny, SCREEN_WIDTH // 2, prompt_y + 40, GRAY, center=True)
        
        # Apply scanlines
        self.screen.blit(self.scanline_surface, (0, 0))
    
    def draw_game_over(self, player: Player):
        """Draw game over screen."""
        self.screen.fill(BLACK)
        
        self.draw_text_with_shadow(self.screen, "GAME OVER", self.font_large,
                                  SCREEN_WIDTH // 2, 200, RED, center=True)
        self.draw_text_with_shadow(self.screen, f"Level Reached: {player.level}", self.font_medium,
                                  SCREEN_WIDTH // 2, 270, UI_TEXT, center=True)
        self.draw_text_with_shadow(self.screen, f"Enemies Defeated: {player.enemies_defeated}/8", self.font_medium,
                                  SCREEN_WIDTH // 2, 310, UI_TEXT, center=True)
        if player.accuracy['total'] > 0:
            acc = player.accuracy['correct'] * 100 // player.accuracy['total']
            self.draw_text_with_shadow(self.screen, f"Accuracy: {acc}%", self.font_medium,
                                      SCREEN_WIDTH // 2, 350, UI_TEXT, center=True)
        
        self.draw_text_with_shadow(self.screen, "Press ENTER to return to title", self.font_small,
                                  SCREEN_WIDTH // 2, 450, GRAY, center=True)
        
        self.screen.blit(self.scanline_surface, (0, 0))
    
    def draw_victory(self, player: Player):
        """Draw victory screen."""
        self.screen.fill(BLACK)
        
        # Celebration animation
        for i in range(20):
            angle = (pygame.time.get_ticks() / 500 + i * 0.3) % (2 * math.pi)
            x = SCREEN_WIDTH // 2 + math.cos(angle) * 200
            y = SCREEN_HEIGHT // 2 + math.sin(angle) * 100
            color = [GREEN, YELLOW, CYAN, MAGENTA][i % 4]
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 5)
        
        self.draw_text_with_shadow(self.screen, "█ SYSTEM SECURED █", self.font_large,
                                  SCREEN_WIDTH // 2, 200, BRIGHT_GREEN, center=True)
        self.draw_text_with_shadow(self.screen, "ALL VULNERABILITIES NEUTRALIZED", self.font_medium,
                                  SCREEN_WIDTH // 2, 270, UI_TEXT_BRIGHT, center=True)
        
        self.draw_text_with_shadow(self.screen, f"Final Level: {player.level}", self.font_medium,
                                  SCREEN_WIDTH // 2, 330, UI_TEXT, center=True)
        self.draw_text_with_shadow(self.screen, f"Total EXP: {sum(e.xp_reward for e in [] if False) + player.exp}", self.font_medium,
                                  SCREEN_WIDTH // 2, 370, UI_TEXT, center=True)
        if player.accuracy['total'] > 0:
            acc = player.accuracy['correct'] * 100 // player.accuracy['total']
            self.draw_text_with_shadow(self.screen, f"Final Accuracy: {acc}%", self.font_medium,
                                      SCREEN_WIDTH // 2, 410, UI_TEXT, center=True)
        
        self.draw_text_with_shadow(self.screen, "Press ENTER to play again", self.font_small,
                                  SCREEN_WIDTH // 2, 500, GRAY, center=True)
        
        self.screen.blit(self.scanline_surface, (0, 0))
    
    def apply_post_effects(self):
        """Apply CRT scanlines and vignette."""
        self.screen.blit(self.scanline_surface, (0, 0))
        self.screen.blit(self.vignette_surface, (0, 0))


# =============================================================================
# GAME CLASS
# =============================================================================

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AppSec RPG: Guardians of the Code")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.renderer = Renderer(self.screen)
        self.particles = ParticleSystem()
        
        # Game state
        self.state = GameState.TITLE
        self.previous_state = GameState.TITLE
        
        # Entities
        self.player = None
        self.enemies: List[Enemy] = []
        self.camera_x = 0
        self.camera_y = 0
        
        # Combat
        self.combat = CombatState()
        
        # UI
        self.pause_selection = 0
        self.title_anim_time = 0
        self.dialogue_text = ""
        self.dialogue_speaker = ""
        self.dialogue_callback = None
        
        # Input
        self.keys_pressed = set()
        
        self.init_game()
    
    def init_game(self):
        """Initialize/reset game."""
        self.player = Player(
            x=PLAYER_SPAWN[0] * TILE_SIZE,
            y=PLAYER_SPAWN[1] * TILE_SIZE
        )
        self.enemies = create_all_enemies(1)
        self.camera_x = self.player.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2
        self.clamp_camera()
        self.combat = CombatState()
        self.pause_selection = 0
        self.title_anim_time = 0
    
    def clamp_camera(self):
        """Clamp camera to world bounds."""
        self.camera_x = max(0, min(self.camera_x, WORLD_WIDTH - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, WORLD_HEIGHT - SCREEN_HEIGHT))
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                
                if self.state == GameState.TITLE:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state = GameState.OVERWORLD
                        self.show_dialogue("Welcome, Guardian! Defeat the vulnerabilities\nto secure the codebase. Press SPACE near enemies to engage.", "SYSTEM")
                
                elif self.state == GameState.OVERWORLD:
                    if event.key == pygame.K_ESCAPE:
                        self.previous_state = self.state
                        self.state = GameState.PAUSED
                        self.pause_selection = 0
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.check_enemy_interaction()
                
                elif self.state == GameState.COMBAT:
                    if self.combat.result is None:
                        if event.key == pygame.K_UP:
                            self.combat.selected_answer = (self.combat.selected_answer - 1) % 4
                        elif event.key == pygame.K_DOWN:
                            self.combat.selected_answer = (self.combat.selected_answer + 1) % 4
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.resolve_combat_answer()
                    else:
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.end_combat_turn()
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = self.previous_state
                    elif event.key == pygame.K_UP:
                        self.pause_selection = (self.pause_selection - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        self.pause_selection = (self.pause_selection + 1) % 4
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.handle_pause_selection()
                
                elif self.state == GameState.DIALOGUE:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.end_dialogue()
                
                elif self.state in (GameState.GAME_OVER, GameState.VICTORY):
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.init_game()
                        self.state = GameState.TITLE
            
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
    
    def check_enemy_interaction(self):
        """Check if player is near an enemy to start combat (SPACE to engage)."""
        for enemy in self.enemies:
            if enemy.alive:
                dist = math.hypot(self.player.x - enemy.x, self.player.y - enemy.y)
                if dist < 48:  # Interaction range (1.5 tiles)
                    self.start_combat(enemy)
                    break
    
    def start_combat(self, enemy: Enemy):
        """Start combat with an enemy."""
        self.state = GameState.COMBAT
        self.combat = CombatState()
        self.combat.active = True
        self.combat.enemy = enemy
        self.combat.question = get_random_question(enemy.category)
        self.combat.selected_answer = 0
        self.combat.timer = self.combat.max_timer
        self.combat.turn = 'player'
        
        # Typewriter effect
        self.combat.typewriter_text = ""
        self.combat.typewriter_index = 0
        self.combat.typewriter_timer = 0
        
        self.player.screen_shake = 300
        self.particles.add_explosion(enemy.x, enemy.y, enemy.color, 20)
    
    def resolve_combat_answer(self):
        """Resolve the player's answer."""
        if not self.combat.question:
            return
        
        correct = (self.combat.selected_answer == self.combat.question['answer'])
        self.combat.result = 'correct' if correct else 'incorrect'
        self.combat.result_timer = 1500
        
        self.player.accuracy['total'] += 1
        self.player.questions_answered += 1
        
        if correct:
            self.combat.damage_dealt = self.player.atk + random.randint(-3, 3)
            self.combat.enemy.hp -= self.combat.damage_dealt
            self.combat.enemy.damage_flash = 200
            self.particles.add_explosion(self.combat.enemy.x, self.combat.enemy.y, GREEN, 12)
            self.particles.add_damage_number(self.combat.enemy.x, self.combat.enemy.y,
                                           self.combat.damage_dealt, GREEN)
        else:
            self.combat.damage_taken = max(1, self.combat.enemy.atk - self.player.def_ // 2)
            self.player.hp -= self.combat.damage_taken
            self.player.damage_flash = 200
            self.player.screen_shake = 200
            self.particles.add_explosion(self.player.x, self.player.y, RED, 12)
            self.particles.add_damage_number(self.player.x, self.player.y,
                                           self.combat.damage_taken, RED)
        
        # Check if enemy defeated
        if self.combat.enemy.hp <= 0:
            self.combat.enemy.alive = False
            self.combat.enemy.defeated = True
            self.player.enemies_defeated += 1
            self.player.exp += self.combat.enemy.xp_reward
            
            # Level up check
            while self.player.exp >= self.player.exp_to_next:
                self.player.exp -= self.player.exp_to_next
                self.player.level += 1
                self.player.exp_to_next = int(self.player.exp_to_next * 1.5)
                self.player.max_hp += 20
                self.player.hp = self.player.max_hp
                self.player.atk += 3
                self.player.def_ += 2
                self.player.heal_flash = 300
                self.particles.add_heal_effect(self.player.x, self.player.y)
            
            # Check victory
            if all(not e.alive for e in self.enemies):
                self.state = GameState.VICTORY
    
    def end_combat_turn(self):
        """End combat turn, check for enemy turn or continue."""
        self.combat.result = None
        
        if self.combat.enemy and self.combat.enemy.alive:
            # Enemy turn
            self.combat.turn = 'enemy'
            self.combat.timer = self.combat.max_timer
            self.combat.question = get_random_question(self.combat.enemy.category)
            self.combat.selected_answer = 0
            self.combat.typewriter_text = ""
            self.combat.typewriter_index = 0
            self.combat.typewriter_timer = 0
        else:
            self.end_combat()
    
    def end_combat(self):
        """End combat, return to overworld."""
        self.state = GameState.OVERWORLD
        self.combat = CombatState()
        self.player.invulnerable = True
        self.player.invuln_timer = 1000
    
    def handle_pause_selection(self):
        """Handle pause menu selection."""
        if self.pause_selection == 0:  # Resume
            self.state = self.previous_state
        elif self.pause_selection == 1:  # View Stats
            self.show_dialogue(
                f"Level: {self.player.level}\n"
                f"HP: {self.player.hp}/{self.player.max_hp}\n"
                f"ATK: {self.player.atk} | DEF: {self.player.def_}\n"
                f"EXP: {self.player.exp}/{self.player.exp_to_next}\n"
                f"Enemies Defeated: {self.player.enemies_defeated}\n"
                f"Accuracy: {self.player.accuracy['correct']}/{self.player.accuracy['total']}",
                "STATS"
            )
        elif self.pause_selection == 2:  # Controls
            self.show_dialogue(
                "WASD / Arrow Keys: Move\n"
                "SPACE / ENTER: Interact / Continue\n"
                "ESC: Pause Menu\n"
                "Arrow Keys in Combat: Select Answer\n"
                "ENTER in Combat: Confirm Answer",
                "CONTROLS"
            )
        elif self.pause_selection == 3:  # Quit
            self.init_game()
            self.state = GameState.TITLE
    
    def show_dialogue(self, text: str, speaker: str, callback=None):
        """Show dialogue box."""
        self.previous_state = self.state
        self.state = GameState.DIALOGUE
        self.dialogue_text = text
        self.dialogue_speaker = speaker
        self.dialogue_callback = callback
    
    def end_dialogue(self):
        """End dialogue."""
        self.state = self.previous_state
        if self.dialogue_callback:
            self.dialogue_callback()
        self.dialogue_callback = None
    
    def update(self, dt: float):
        """Update game logic."""
        self.title_anim_time += dt
        
        if self.state == GameState.OVERWORLD:
            self.update_overworld(dt)
        elif self.state == GameState.COMBAT:
            self.update_combat(dt)
        
        # Update player effects
        if self.player.damage_flash > 0:
            self.player.damage_flash -= dt
        if self.player.heal_flash > 0:
            self.player.heal_flash -= dt
        if self.player.invulnerable:
            self.player.invuln_timer -= dt
            if self.player.invuln_timer <= 0:
                self.player.invulnerable = False
        
        # Screen shake
        if self.player.screen_shake > 0:
            self.player.screen_shake -= dt
        
        # Particles
        self.particles.update(dt)
        
        # Check game over
        if self.player.hp <= 0 and self.state not in (GameState.GAME_OVER, GameState.VICTORY):
            self.state = GameState.GAME_OVER
    
    def update_overworld(self, dt: float):
        """Update overworld logic."""
        # Player movement
        self.player.vx = 0
        self.player.vy = 0
        self.player.moving = False
        
        if pygame.K_w in self.keys_pressed or pygame.K_UP in self.keys_pressed:
            self.player.vy = -self.player.speed
            self.player.facing = 'up'
            self.player.moving = True
        if pygame.K_s in self.keys_pressed or pygame.K_DOWN in self.keys_pressed:
            self.player.vy = self.player.speed
            self.player.facing = 'down'
            self.player.moving = True
        if pygame.K_a in self.keys_pressed or pygame.K_LEFT in self.keys_pressed:
            self.player.vx = -self.player.speed
            self.player.facing = 'left'
            self.player.moving = True
        if pygame.K_d in self.keys_pressed or pygame.K_RIGHT in self.keys_pressed:
            self.player.vx = self.player.speed
            self.player.facing = 'right'
            self.player.moving = True
        
        # Normalize diagonal
        if self.player.vx != 0 and self.player.vy != 0:
            self.player.vx *= 0.7071
            self.player.vy *= 0.7071
        
        # Apply movement
        new_x = self.player.x + self.player.vx * dt / 1000
        new_y = self.player.y + self.player.vy * dt / 1000
        
        # Check collision with world
        old_x, old_y = self.player.x, self.player.y
        self.player.x = new_x
        if check_collision(self.player, WORLD_MAP):
            self.player.x = old_x
        self.player.y = new_y
        if check_collision(self.player, WORLD_MAP):
            self.player.y = old_y
        
        # Check collision with enemies (solid - can't walk through)
        for enemy in self.enemies:
            if enemy.alive:
                if check_entity_collision(self.player, enemy):
                    # Push player back
                    resolve_entity_collision(self.player, enemy)
        
        # Clamp to world bounds
        half_w = self.player.width / 2
        half_h = self.player.height / 2
        self.player.x = max(half_w, min(self.player.x, WORLD_WIDTH - half_w))
        self.player.y = max(half_h, min(self.player.y, WORLD_HEIGHT - half_h))
        
        # Update camera to follow player
        self.camera_x = self.player.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2
        self.clamp_camera()
        
        # Update enemies
        for enemy in self.enemies:
            if enemy.alive:
                self.update_enemy(enemy, dt)
            elif enemy.defeated:
                enemy.defeated_timer += dt
        
        # Animation
        if self.player.moving:
            self.player.anim_timer += dt
            if self.player.anim_timer > 150:
                self.player.anim_frame = (self.player.anim_frame + 1) % 4
                self.player.anim_timer = 0
    
    def update_enemy(self, enemy: Enemy, dt: float):
        """Update enemy AI and animation."""
        # Floating animation
        enemy.float_offset += enemy.float_dir * 0.05 * dt / 16
        if abs(enemy.float_offset) > 2:
            enemy.float_dir *= -1
        
        # Animation
        enemy.anim_timer += dt
        if enemy.anim_timer > 300:
            enemy.anim_frame = (enemy.anim_frame + 1) % 4
            enemy.anim_timer = 0
        
        # Visual effects
        if enemy.damage_flash > 0:
            enemy.damage_flash -= dt
        
        # Simple AI - wander
        enemy.ai_timer += dt
        if enemy.ai_timer > 3000 + random.random() * 2000:
            enemy.ai_timer = 0
            range_ = 80
            enemy.wander_target = (
                enemy.x + (random.random() - 0.5) * range_,
                enemy.y + (random.random() - 0.5) * range_
            )
            
            # Clamp to valid tiles
            tx = int(enemy.wander_target[0] // TILE_SIZE)
            ty = int(enemy.wander_target[1] // TILE_SIZE)
            if 0 <= ty < MAP_HEIGHT and 0 <= tx < MAP_WIDTH:
                if WORLD_MAP[ty][tx] == 1:
                    enemy.wander_target = (enemy.x, enemy.y)
        
        # Move toward wander target
        if enemy.wander_target != (0, 0):
            dx = enemy.wander_target[0] - enemy.x
            dy = enemy.wander_target[1] - enemy.y
            dist = math.hypot(dx, dy)
            if dist > 10:
                speed = 40
                new_x = enemy.x + (dx / dist) * speed * dt / 1000
                new_y = enemy.y + (dy / dist) * speed * dt / 1000
                
                old_x, old_y = enemy.x, enemy.y
                enemy.x = new_x
                if check_collision(enemy, WORLD_MAP):
                    enemy.x = old_x
                enemy.y = new_y
                if check_collision(enemy, WORLD_MAP):
                    enemy.y = old_y
            else:
                enemy.wander_target = (0, 0)
    
    def update_combat(self, dt: float):
        """Update combat logic."""
        if self.combat.result is None:
            self.combat.timer -= dt / 1000
            if self.combat.timer <= 0:
                self.combat.timer = 0
                self.combat.result = 'timeout'
                self.combat.result_timer = 1500
                self.combat.damage_taken = max(1, self.combat.enemy.atk - self.player.def_ // 2)
                self.player.hp -= self.combat.damage_taken
                self.player.damage_flash = 200
                self.player.screen_shake = 200
                self.particles.add_explosion(self.player.x, self.player.y, RED, 8)
        else:
            self.combat.result_timer -= dt
            if self.combat.result_timer <= 0:
                self.end_combat_turn()
        
        # Typewriter effect
        if self.combat.question and self.combat.typewriter_index < len(self.combat.question['question']):
            self.combat.typewriter_timer += dt
            if self.combat.typewriter_timer >= self.combat.typewriter_speed:
                self.combat.typewriter_timer = 0
                self.combat.typewriter_index += 1
                self.combat.typewriter_text = self.combat.question['question'][:self.combat.typewriter_index]
    
    def draw(self):
        """Draw everything."""
        # Apply screen shake
        shake_x = 0
        shake_y = 0
        if self.player.screen_shake > 0:
            shake_x = random.randint(-3, 3)
            shake_y = random.randint(-3, 3)
        
        if self.state == GameState.TITLE:
            self.renderer.draw_title(self.title_anim_time)
        
        elif self.state in (GameState.OVERWORLD, GameState.COMBAT, GameState.PAUSED):
            # Draw world
            self.renderer.draw_world(self.camera_x + shake_x, self.camera_y + shake_y)
            
            # Draw enemies
            for enemy in self.enemies:
                if enemy.alive or (enemy.defeated and enemy.defeated_timer < 500):
                    self.renderer.draw_enemy(enemy, self.camera_x + shake_x, self.camera_y + shake_y)
            
            # Draw player
            self.renderer.draw_player(self.player, self.camera_x + shake_x, self.camera_y + shake_y)
            
            # Draw particles
            self.renderer.draw_particles(self.particles, self.camera_x + shake_x, self.camera_y + shake_y)
            
            # Draw HUD (only in overworld)
            if self.state == GameState.OVERWORLD:
                self.renderer.enemies = self.enemies  # For minimap
                self.renderer.draw_hud(self.player)
            
            # Draw combat overlay
            if self.state == GameState.COMBAT:
                self.renderer.draw_combat(self.combat, self.player)
            
            # Draw pause menu
            if self.state == GameState.PAUSED:
                self.renderer.draw_pause_menu(self.pause_selection)
        
        elif self.state == GameState.DIALOGUE:
            # Draw underlying world
            self.renderer.draw_world(self.camera_x, self.camera_y)
            for enemy in self.enemies:
                if enemy.alive:
                    self.renderer.draw_enemy(enemy, self.camera_x, self.camera_y)
            self.renderer.draw_player(self.player, self.camera_x, self.camera_y)
            self.renderer.enemies = self.enemies
            self.renderer.draw_hud(self.player)
            # Draw dialogue on top
            self.renderer.draw_dialogue_box(self.dialogue_text, self.dialogue_speaker)
        
        elif self.state == GameState.GAME_OVER:
            self.renderer.draw_game_over(self.player)
        
        elif self.state == GameState.VICTORY:
            self.renderer.draw_victory(self.player)
        
        # Apply post-processing effects
        self.renderer.apply_post_effects()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    print("Starting AppSec RPG: Guardians of the Code")
    print("OWASP Top 10 Quiz Combat Game")
    print("Built with Pygame - Retro Pixel Art Edition")
    print()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()