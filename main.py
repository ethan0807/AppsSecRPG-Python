#!/usr/bin/env python3
"""
AppSec RPG: Guardians of the Code
OWASP Top 10 Quiz Combat Game
Built with Pygame
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
PLAYER_SPEED = 180  # pixels per second
PLAYER_SIZE = 24
ENEMY_SIZE = 24

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BRIGHT_GREEN = (0, 255, 100)
DARK_GREEN = (0, 100, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
UI_BG = (10, 10, 20)
UI_BORDER = (0, 150, 0)
UI_TEXT = (0, 200, 0)
UI_TEXT_BRIGHT = (0, 255, 100)
MENU_SELECTED = (0, 80, 0)
HUD_BG = (0, 0, 0, 200)

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
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,1],
    [1,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,1],
    [1,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
    [1,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
    [1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

MAP_WIDTH = len(WORLD_MAP[0])
MAP_HEIGHT = len(WORLD_MAP)
WORLD_WIDTH = MAP_WIDTH * TILE_SIZE
WORLD_HEIGHT = MAP_HEIGHT * TILE_SIZE

# Player spawn (tile coordinates)
PLAYER_SPAWN = (20, 18)

# Game Balance
PLAYER_BASE_HP = 100
PLAYER_BASE_ATK = 15
PLAYER_BASE_DEF = 10
EXP_PER_LEVEL = 100
ENEMY_HP_SCALING = 1.3
ENEMY_ATK_SCALING = 1.2

# HUD
HUD_HEIGHT = 120

# Enemy Types
ENEMY_TYPES = {
    'INJECTION': {
        'name': 'Injection Demon',
        'symbol': '◆',
        'category': 'A03: Injection',
        'desc': 'SQL/Command injection attacks',
        'color': (255, 60, 60),
        'baseHp': 50,
        'baseAtk': 12,
        'xpReward': 30,
    },
    'XSS': {
        'name': 'XSS Specter',
        'symbol': '✦',
        'category': 'A03: Injection',
        'desc': 'Cross-site scripting attacks',
        'color': (255, 150, 0),
        'baseHp': 40,
        'baseAtk': 15,
        'xpReward': 25,
    },
    'CRYPTO': {
        'name': 'Crypto Phantom',
        'symbol': '◈',
        'category': 'A02: Cryptographic Failures',
        'desc': 'Weak encryption, exposed secrets',
        'color': (180, 0, 255),
        'baseHp': 60,
        'baseAtk': 10,
        'xpReward': 35,
    },
    'ACCESS': {
        'name': 'Access Control Wraith',
        'symbol': '■',
        'category': 'A01: Broken Access Control',
        'desc': 'Unauthorized resource access',
        'color': (0, 200, 255),
        'baseHp': 55,
        'baseAtk': 14,
        'xpReward': 30,
    },
    'DESIGN': {
        'name': 'Insecure Design Golem',
        'symbol': '▲',
        'category': 'A04: Insecure Design',
        'desc': 'Missing security controls',
        'color': (255, 255, 0),
        'baseHp': 70,
        'baseAtk': 8,
        'xpReward': 40,
    },
    'MISCONFIG': {
        'name': 'Config Goblin',
        'symbol': '●',
        'category': 'A05: Security Misconfiguration',
        'desc': 'Default creds, open ports',
        'color': (255, 100, 100),
        'baseHp': 35,
        'baseAtk': 18,
        'xpReward': 20,
    },
    'DESERIALIZE': {
        'name': 'Deserialization Wraith',
        'symbol': '◆',
        'category': 'A08: Software Integrity Failures',
        'desc': 'Untrusted data deserialization',
        'color': (150, 0, 200),
        'baseHp': 65,
        'baseAtk': 11,
        'xpReward': 35,
    },
    'LOGGING': {
        'name': 'Logging Phantom',
        'symbol': '◆',
        'category': 'A09: Logging Failures',
        'desc': 'Insufficient attack detection',
        'color': (100, 100, 255),
        'baseHp': 45,
        'baseAtk': 13,
        'xpReward': 25,
    },
}

# Enemy spawns (tile coordinates) - all on floor tiles
ENEMY_SPAWNS = [
    {'x': 5, 'y': 5, 'type': 'INJECTION'},
    {'x': 30, 'y': 5, 'type': 'XSS'},
    {'x': 5, 'y': 12, 'type': 'CRYPTO'},
    {'x': 30, 'y': 15, 'type': 'ACCESS'},
    {'x': 20, 'y': 10, 'type': 'DESIGN'},
    {'x': 10, 'y': 8, 'type': 'MISCONFIG'},
    {'x': 30, 'y': 12, 'type': 'DESERIALIZE'},
    {'x': 20, 'y': 5, 'type': 'LOGGING'},
]

# OWASP Top 10 Questions
QUESTIONS = {
    'A01: Broken Access Control': [
        {
            'question': 'What is Broken Access Control?',
            'choices': [
                'Users can access resources they should not be authorized to access',
                'Encryption keys are hardcoded in source code',
                'SQL queries are constructed via string concatenation',
                'Error messages reveal stack traces to users'
            ],
            'answer': 0
        },
        {
            'question': 'Which is an example of Insecure Direct Object Reference (IDOR)?',
            'choices': [
                'Changing /api/user/123/profile to /api/user/124/profile to view another user\'s data',
                'Injecting <script>alert(1)</script> into a comment field',
                'Using a weak password like "password123"',
                'Leaving debug endpoints enabled in production'
            ],
            'answer': 0
        },
        {
            'question': 'What is the principle of least privilege?',
            'choices': [
                'Users should have only the minimum permissions necessary',
                'All users should have admin access for convenience',
                'Permissions should be granted based on seniority',
                'Developers should have production database access'
            ],
            'answer': 0
        }
    ],
    'A02: Cryptographic Failures': [
        {
            'question': 'What is a Cryptographic Failure?',
            'choices': [
                'Sensitive data transmitted in cleartext or using weak algorithms',
                'User input not validated before database queries',
                'Missing authentication on admin endpoints',
                'Error messages revealing system information'
            ],
            'answer': 0
        },
        {
            'question': 'Which should NEVER be used for password storage?',
            'choices': [
                'MD5 or SHA1 (fast hashes without salt)',
                'bcrypt with cost factor 12',
                'Argon2id with proper parameters',
                'PBKDF2 with 100,000+ iterations'
            ],
            'answer': 0
        },
        {
            'question': 'What is the risk of hardcoding API keys in source code?',
            'choices': [
                'Keys can be exposed via version control or decompilation',
                'It makes the application run slower',
                'It prevents the use of environment variables',
                'It violates coding style guides'
            ],
            'answer': 0
        }
    ],
    'A03: Injection': [
        {
            'question': 'What is SQL Injection?',
            'choices': [
                'User input concatenated directly into SQL queries allowing arbitrary execution',
                'Malicious scripts injected into web pages viewed by other users',
                'Attackers uploading malicious files to the server',
                'Brute forcing passwords via login forms'
            ],
            'answer': 0
        },
        {
            'question': 'How do you prevent SQL Injection?',
            'choices': [
                'Use parameterized queries / prepared statements',
                'Escape special characters with string replacement',
                'Validate input with regex only',
                'Use stored procedures for all queries'
            ],
            'answer': 0
        },
        {
            'question': 'What is Cross-Site Scripting (XSS)?',
            'choices': [
                'Injecting malicious scripts into web pages viewed by other users',
                'Stealing session cookies via network sniffing',
                'Injecting SQL commands into database queries',
                'Overloading server with requests'
            ],
            'answer': 0
        }
    ],
    'A04: Insecure Design': [
        {
            'question': 'What is Insecure Design?',
            'choices': [
                'Missing or ineffective control design that cannot be fixed by implementation',
                'Using outdated libraries with known vulnerabilities',
                'Failing to encrypt sensitive data at rest',
                'Not logging security events'
            ],
            'answer': 0
        },
        {
            'question': 'Which is a secure design practice?',
            'choices': [
                'Threat modeling during design phase',
                'Adding security testing only before release',
                'Using security by obscurity',
                'Trusting all internal network traffic'
            ],
            'answer': 0
        }
    ],
    'A05: Security Misconfiguration': [
        {
            'question': 'What is Security Misconfiguration?',
            'choices': [
                'Default credentials, unnecessary features, open cloud storage, verbose errors',
                'Weak password policies for user accounts',
                'Missing input validation on forms',
                'Not using HTTPS for all pages'
            ],
            'answer': 0
        },
        {
            'question': 'Which is a common misconfiguration?',
            'choices': [
                'Leaving default admin/admin credentials on production systems',
                'Using parameterized queries for database access',
                'Implementing rate limiting on login endpoints',
                'Encrypting data with AES-256'
            ],
            'answer': 0
        }
    ],
    'A06: Vulnerable Components': [
        {
            'question': 'What are Vulnerable and Outdated Components?',
            'choices': [
                'Using libraries/frameworks with known CVEs without patching',
                'Writing custom code instead of using libraries',
                'Not having a CI/CD pipeline',
                'Using microservices architecture'
            ],
            'answer': 0
        },
        {
            'question': 'How to manage component vulnerabilities?',
            'choices': [
                'Use SCA tools, monitor CVEs, automate dependency updates',
                'Only use libraries written in-house',
                'Never update dependencies to avoid breaking changes',
                'Use only the most popular libraries'
            ],
            'answer': 0
        }
    ],
    'A07: Auth Failures': [
        {
            'question': 'What is Identification and Authentication Failure?',
            'choices': [
                'Weak credential recovery, brute force, session fixation, weak passwords',
                'SQL injection in login forms',
                'XSS on registration pages',
                'Missing CSRF tokens on forms'
            ],
            'answer': 0
        },
        {
            'question': 'Which is a secure password policy?',
            'choices': [
                'Minimum 12 chars, MFA enabled, rate limiting, breach checking',
                'Minimum 8 chars, no special chars required',
                'Password rotation every 30 days',
                'Allowing password hints'
            ],
            'answer': 0
        }
    ],
    'A08: Software Integrity': [
        {
            'question': 'What is a Software and Data Integrity Failure?',
            'choices': [
                'Unverified CI/CD pipelines, unsigned code, insecure deserialization',
                'Weak encryption algorithms',
                'Missing security headers',
                'Open redirect vulnerabilities'
            ],
            'answer': 0
        },
        {
            'question': 'What prevents supply chain attacks?',
            'choices': [
                'Signed commits, SBOM, verified dependencies, reproducible builds',
                'Using only internal package mirrors',
                'Disabling all third-party packages',
                'Manual code review of all dependencies'
            ],
            'answer': 0
        }
    ],
    'A09: Logging Failures': [
        {
            'question': 'What is a Security Logging and Monitoring Failure?',
            'choices': [
                'Insufficient logging, no alerting, logs only stored locally',
                'Logging too much information',
                'Using structured logging formats',
                'Centralized log aggregation'
            ],
            'answer': 0
        },
        {
            'question': 'What should be logged for security?',
            'choices': [
                'Failed logins, privilege changes, access violations, input validation failures',
                'Only successful logins',
                'All user keystrokes',
                'Database query performance metrics'
            ],
            'answer': 0
        }
    ],
    'A10: SSRF': [
        {
            'question': 'What is Server-Side Request Forgery (SSRF)?',
            'choices': [
                'Server fetches attacker-controlled URLs, accessing internal resources',
                'Client browser forced to make requests to attacker site',
                'Database queries modified by user input',
                'Session tokens stolen via XSS'
            ],
            'answer': 0
        },
        {
            'question': 'How to prevent SSRF?',
            'choices': [
                'Allowlist URLs, block private IPs, disable HTTP redirects, use fetch proxies',
                'Use HTTPS for all external requests',
                'Validate user input with regex',
                'Rate limit all outbound requests'
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
    vx: float = 0
    vy: float = 0
    width: int = PLAYER_SIZE
    height: int = PLAYER_SIZE
    speed: int = PLAYER_SPEED
    max_hp: int = PLAYER_BASE_HP
    hp: int = PLAYER_BASE_HP
    base_atk: int = PLAYER_BASE_ATK
    atk: int = PLAYER_BASE_ATK
    base_def: int = PLAYER_BASE_DEF
    def_: int = PLAYER_BASE_DEF
    level: int = 1
    exp: int = 0
    exp_to_next: int = EXP_PER_LEVEL
    accuracy: Dict[str, int] = field(default_factory=lambda: {'correct': 0, 'total': 0})
    enemies_defeated: int = 0
    questions_answered: int = 0
    invulnerable: bool = False
    invuln_timer: float = 0
    knockback_x: float = 0
    knockback_y: float = 0
    knockback_timer: float = 0
    anim_frame: int = 0
    anim_timer: float = 0
    facing: str = 'down'
    moving: bool = False
    damage_flash: float = 0
    heal_flash: float = 0
    screen_shake: float = 0


@dataclass
class Enemy:
    id: str
    type: str
    name: str
    symbol: str
    category: str
    description: str
    color: Tuple[int, int, int]
    x: float
    y: float
    width: int = ENEMY_SIZE
    height: int = ENEMY_SIZE
    spawn_tile: Tuple[int, int] = field(default_factory=lambda: (0, 0))
    max_hp: int = 50
    hp: int = 50
    atk: int = 10
    level: int = 1
    xp_reward: int = 20
    alive: bool = True
    defeated: bool = False
    defeated_timer: float = 0
    anim_frame: int = 0
    anim_timer: float = 0
    float_offset: float = 0
    float_dir: int = 1
    damage_flash: float = 0
    ai_timer: float = 0
    ai_state: str = 'idle'
    wander_target: Tuple[float, float] = (0, 0)


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: Tuple[int, int, int]
    life: float
    max_life: float
    size: int = 3
    gravity: float = 0


@dataclass
class CombatState:
    active: bool = False
    enemy: Optional[Enemy] = None
    question: Optional[Dict] = None
    selected_answer: int = 0
    timer: float = 30.0
    max_timer: float = 30.0
    result: Optional[str] = None  # 'correct', 'incorrect', 'timeout'
    result_timer: float = 0
    damage_dealt: int = 0
    damage_taken: int = 0
    turn: str = 'player'  # 'player', 'enemy'
    typewriter_text: str = ''
    typewriter_index: int = 0
    typewriter_timer: float = 0
    typewriter_speed: float = 30  # ms per char


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_random_question(category: str) -> Dict:
    """Get a random question from a category."""
    questions = QUESTIONS.get(category, QUESTIONS['A01: Broken Access Control'])
    return random.choice(questions)


def check_collision(entity, world_map) -> bool:
    """Check if entity collides with wall tiles."""
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


def resolve_collision(entity, world_map):
    """Resolve collision with wall tiles."""
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


def check_entity_collision(e1, e2) -> bool:
    """Check collision between two entities."""
    half_w1, half_h1 = e1.width / 2, e1.height / 2
    half_w2, half_h2 = e2.width / 2, e2.height / 2
    
    return (abs(e1.x - e2.x) < half_w1 + half_w2 and
            abs(e1.y - e2.y) < half_h1 + half_h2)


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


# =============================================================================
# PARTICLE SYSTEM
# =============================================================================

class ParticleSystem:
    def __init__(self, max_particles: int = 200):
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
    
    def add_explosion(self, x: float, y: float, color: Tuple[int, int, int], count: int = 12):
        for _ in range(count):
            angle = random.random() * 2 * math.pi
            speed = 50 + random.random() * 100
            self.add(x, y, color, 
                     (math.cos(angle) * speed, math.sin(angle) * speed),
                     500 + random.random() * 300, 
                     2 + random.random() * 3, 
                     0.1)
    
    def add_damage_number(self, x: float, y: float, amount: int, color: Tuple[int, int, int]):
        self.add(x, y, color, (0, -30), 1000, 0, -0.05)
        # Store damage number as text - we'll render separately
    
    def update(self, dt: float):
        for p in self.particles[:]:
            p.life -= dt
            p.vy += p.gravity * dt
            p.x += p.vx * dt / 1000
            p.y += p.vy * dt / 1000
            if p.life <= 0:
                self.particles.remove(p)
    
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        for p in self.particles:
            alpha = int(255 * (p.life / p.max_life))
            if alpha <= 0:
                continue
            color = (*p.color[:3], alpha)
            px = int(p.x - camera_x)
            py = int(p.y - camera_y)
            if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
                surf = pygame.Surface((p.size * 2, p.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (p.size, p.size), p.size)
                screen.blit(surf, (px - p.size, py - p.size))


# =============================================================================
# RENDERER
# =============================================================================

class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_small = pygame.font.Font(None, 16)
        self.font_medium = pygame.font.Font(None, 20)
        self.font_large = pygame.font.Font(None, 28)
        self.font_title = pygame.font.Font(None, 48)
        self.font_pixel = pygame.font.Font(None, 14)  # Will use default for now
    
    def draw_world(self, camera_x: float, camera_y: float):
        """Draw the world map tiles."""
        # Visible tile range
        start_tx = max(0, int(camera_x // TILE_SIZE) - 1)
        end_tx = min(MAP_WIDTH, int((camera_x + SCREEN_WIDTH) // TILE_SIZE) + 1)
        start_ty = max(0, int(camera_y // TILE_SIZE) - 1)
        end_ty = min(MAP_HEIGHT, int((camera_y + SCREEN_HEIGHT) // TILE_SIZE) + 1)
        
        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                tile_x = tx * TILE_SIZE - camera_x
                tile_y = ty * TILE_SIZE - camera_y
                
                if WORLD_MAP[ty][tx] == 1:
                    # Wall
                    pygame.draw.rect(self.screen, (40, 40, 60), 
                                   (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(self.screen, (80, 80, 100), 
                                   (tile_x, tile_y, TILE_SIZE, TILE_SIZE), 1)
                else:
                    # Floor
                    pygame.draw.rect(self.screen, (15, 15, 25), 
                                   (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
                    # Subtle grid
                    pygame.draw.rect(self.screen, (25, 25, 35), 
                                   (tile_x, tile_y, TILE_SIZE, TILE_SIZE), 1)
    
    def draw_player(self, player: Player, camera_x: float, camera_y: float):
        """Draw the player character."""
        px = int(player.x - camera_x)
        py = int(player.y - camera_y)
        
        # Damage flash
        if player.damage_flash > 0:
            flash_surf = pygame.Surface((player.width, player.height), pygame.SRCALPHA)
            flash_surf.fill((255, 0, 0, min(150, int(player.damage_flash / 10))))
            self.screen.blit(flash_surf, (px - player.width//2, py - player.height//2))
        
        # Player body (retro pixel style)
        color = BRIGHT_GREEN if not player.invulnerable or int(player.invuln_timer * 10) % 2 == 0 else (100, 100, 100)
        
        # Body
        pygame.draw.rect(self.screen, color, 
                        (px - player.width//2, py - player.height//2, 
                         player.width, player.height))
        
        # Face indicator (direction)
        face_color = WHITE
        if player.facing == 'up':
            pygame.draw.rect(self.screen, face_color, (px - 2, py - player.height//2 + 2, 4, 4))
        elif player.facing == 'down':
            pygame.draw.rect(self.screen, face_color, (px - 2, py + player.height//2 - 6, 4, 4))
        elif player.facing == 'left':
            pygame.draw.rect(self.screen, face_color, (px - player.width//2 + 2, py - 2, 4, 4))
        elif player.facing == 'right':
            pygame.draw.rect(self.screen, face_color, (px + player.width//2 - 6, py - 2, 4, 4))
        
        # Health bar above player
        if player.hp < player.max_hp:
            bar_w = 30
            bar_h = 4
            bar_x = px - bar_w // 2
            bar_y = py - player.height//2 - 10
            pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, int(bar_w * player.hp / player.max_hp), bar_h))
            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 1)
    
    def draw_enemy(self, enemy: Enemy, camera_x: float, camera_y: float):
        """Draw an enemy."""
        if not enemy.alive:
            return
        
        ex = int(enemy.x - camera_x + enemy.float_offset)
        ey = int(enemy.y - camera_y)
        
        # Damage flash
        if enemy.damage_flash > 0:
            flash_surf = pygame.Surface((enemy.width, enemy.height), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, min(200, int(enemy.damage_flash / 5))))
            self.screen.blit(flash_surf, (ex - enemy.width//2, ey - enemy.height//2))
        
        # Enemy body
        pygame.draw.rect(self.screen, enemy.color, 
                        (ex - enemy.width//2, ey - enemy.height//2, 
                         enemy.width, enemy.height))
        
        # Symbol
        symbol_surf = self.font_medium.render(enemy.symbol, True, WHITE)
        self.screen.blit(symbol_surf, (ex - symbol_surf.get_width()//2, ey - symbol_surf.get_height()//2))
        
        # Health bar
        if enemy.hp < enemy.max_hp:
            bar_w = 24
            bar_h = 3
            bar_x = ex - bar_w // 2
            bar_y = ey - enemy.height//2 - 8
            pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, int(bar_w * enemy.hp / enemy.max_hp), bar_h))
            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 1)
    
    def draw_hud(self, player: Player):
        """Draw the HUD."""
        hud_y = SCREEN_HEIGHT - HUD_HEIGHT
        
        # HUD background
        hud_surf = pygame.Surface((SCREEN_WIDTH, HUD_HEIGHT), pygame.SRCALPHA)
        hud_surf.fill((0, 0, 0, 220))
        self.screen.blit(hud_surf, (0, hud_y))
        
        # Border
        pygame.draw.line(self.screen, UI_BORDER, (0, hud_y), (SCREEN_WIDTH, hud_y), 2)
        
        # Stats
        stats = [
            f"HP: {player.hp}/{player.max_hp}",
            f"ATK: {player.atk}",
            f"DEF: {player.def_}",
            f"LVL: {player.level}",
            f"EXP: {player.exp}/{player.exp_to_next}",
            f"Enemies: {player.enemies_defeated}",
            f"Accuracy: {player.accuracy['correct']}/{player.accuracy['total']}" 
            if player.accuracy['total'] > 0 else "Accuracy: -"
        ]
        
        for i, stat in enumerate(stats):
            x = 20 + (i % 4) * 190
            y = hud_y + 15 + (i // 4) * 30
            text = self.font_medium.render(stat, True, UI_TEXT)
            self.screen.blit(text, (x, y))
        
        # HP Bar
        bar_w = 200
        bar_h = 16
        bar_x = SCREEN_WIDTH - bar_w - 20
        bar_y = hud_y + 15
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, int(bar_w * player.hp / player.max_hp), bar_h))
        pygame.draw.rect(self.screen, UI_BORDER, (bar_x, bar_y, bar_w, bar_h), 2)
        
        hp_text = self.font_small.render(f"HP: {player.hp}/{player.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (bar_x + bar_w//2 - hp_text.get_width()//2, bar_y + 1))
        
        # EXP Bar
        exp_y = bar_y + 25
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, exp_y, bar_w, 8))
        pygame.draw.rect(self.screen, CYAN, (bar_x, exp_y, int(bar_w * player.exp / player.exp_to_next), 8))
        pygame.draw.rect(self.screen, UI_BORDER, (bar_x, exp_y, bar_w, 8), 1)
    
    def draw_dialogue_box(self, text: str, speaker: str = ""):
        """Draw dialogue box at bottom."""
        box_h = 140
        box_y = SCREEN_HEIGHT - box_h - 10
        box_surf = pygame.Surface((SCREEN_WIDTH - 20, box_h), pygame.SRCALPHA)
        box_surf.fill((0, 0, 0, 230))
        self.screen.blit(box_surf, (10, box_y))
        pygame.draw.rect(self.screen, UI_BORDER, (10, box_y, SCREEN_WIDTH - 20, box_h), 2)
        
        if speaker:
            name_text = self.font_medium.render(speaker, True, YELLOW)
            self.screen.blit(name_text, (20, box_y + 10))
        
        # Word wrap
        words = text.split(' ')
        lines = []
        current_line = []
        max_width = SCREEN_WIDTH - 40
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surf = self.font_small.render(test_line, True, WHITE)
            if test_surf.get_width() > max_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines[:6]):
            text_surf = self.font_small.render(line, True, UI_TEXT)
            self.screen.blit(text_surf, (20, box_y + 35 + i * 18))
        
        # Continue prompt
        prompt = self.font_small.render("[Press SPACE/ENTER to continue]", True, GRAY)
        self.screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, box_y + box_h - 25))
    
    def draw_combat(self, combat: CombatState, player: Player):
        """Draw combat screen."""
        # Background overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 240))
        self.screen.blit(overlay, (0, 0))
        
        # Combat box
        box_w = 700
        box_h = 450
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2
        
        pygame.draw.rect(self.screen, UI_BG, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, UI_BORDER, (box_x, box_y, box_w, box_h), 3)
        
        # Title
        title = self.font_large.render("⚔ COMBAT ENCOUNTER ⚔", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, box_y + 20))
        
        if combat.enemy:
            # Enemy info
            enemy_name = self.font_medium.render(f"{combat.enemy.name} (Lv.{combat.enemy.level})", True, combat.enemy.color)
            self.screen.blit(enemy_name, (box_x + 30, box_y + 70))
            
            cat_text = self.font_small.render(combat.enemy.category, True, CYAN)
            self.screen.blit(cat_text, (box_x + 30, box_y + 95))
            
            # Enemy HP
            ehp_w = 200
            ehp_h = 12
            ehp_x = box_x + 30
            ehp_y = box_y + 120
            pygame.draw.rect(self.screen, RED, (ehp_x, ehp_y, ehp_w, ehp_h))
            pygame.draw.rect(self.screen, GREEN, (ehp_x, ehp_y, int(ehp_w * combat.enemy.hp / combat.enemy.max_hp), ehp_h))
            pygame.draw.rect(self.screen, WHITE, (ehp_x, ehp_y, ehp_w, ehp_h), 1)
            
            ehp_text = self.font_small.render(f"{combat.enemy.hp}/{combat.enemy.max_hp}", True, WHITE)
            self.screen.blit(ehp_text, (ehp_x + ehp_w//2 - ehp_text.get_width()//2, ehp_y - 1))
        
        # Player HP
        php_w = 200
        php_h = 12
        php_x = box_x + box_w - php_w - 30
        php_y = box_y + 120
        pygame.draw.rect(self.screen, RED, (php_x, php_y, php_w, php_h))
        pygame.draw.rect(self.screen, GREEN, (php_x, php_y, int(php_w * player.hp / player.max_hp), php_h))
        pygame.draw.rect(self.screen, WHITE, (php_x, php_y, php_w, php_h), 1)
        
        php_text = self.font_small.render(f"YOU: {player.hp}/{player.max_hp}", True, WHITE)
        self.screen.blit(php_text, (php_x + php_w//2 - php_text.get_width()//2, php_y - 1))
        
        if combat.question:
            # Question
            q_text = combat.typewriter_text if combat.typewriter_text else combat.question['question']
            q_surf = self.font_medium.render(q_text, True, WHITE)
            self.screen.blit(q_surf, (box_x + 30, box_y + 160))
            
            # Timer
            timer_pct = combat.timer / combat.max_timer
            timer_w = 400
            timer_x = box_x + 30
            timer_y = box_y + 200
            pygame.draw.rect(self.screen, DARK_GRAY, (timer_x, timer_y, timer_w, 12))
            timer_color = GREEN if timer_pct > 0.5 else (YELLOW if timer_pct > 0.25 else RED)
            pygame.draw.rect(self.screen, timer_color, (timer_x, timer_y, int(timer_w * timer_pct), 12))
            pygame.draw.rect(self.screen, WHITE, (timer_x, timer_y, timer_w, 12), 1)
            
            timer_text = self.font_small.render(f"{combat.timer:.1f}s", True, WHITE)
            self.screen.blit(timer_text, (timer_x + timer_w + 10, timer_y - 1))
            
            # Answer options
            for i, choice in enumerate(combat.question['choices']):
                ay = box_y + 230 + i * 45
                selected = (i == combat.selected_answer)
                
                if selected:
                    pygame.draw.rect(self.screen, MENU_SELECTED, (box_x + 20, ay - 5, box_w - 40, 40))
                    pygame.draw.rect(self.screen, UI_BORDER, (box_x + 20, ay - 5, box_w - 40, 40), 2)
                    color = UI_TEXT_BRIGHT
                    prefix = "► "
                else:
                    color = UI_TEXT
                    prefix = "  "
                
                choice_text = self.font_small.render(f"{prefix}{chr(65+i)}) {choice}", True, color)
                self.screen.blit(choice_text, (box_x + 35, ay + 5))
        
        if combat.result:
            # Result display
            result_color = GREEN if combat.result == 'correct' else RED
            result_text = "CORRECT!" if combat.result == 'correct' else "INCORRECT!" if combat.result == 'incorrect' else "TIME'S UP!"
            result_surf = self.font_large.render(result_text, True, result_color)
            self.screen.blit(result_surf, (SCREEN_WIDTH//2 - result_surf.get_width()//2, box_y + 350))
            
            if combat.result == 'correct':
                dmg_text = self.font_medium.render(f"Dealt {combat.damage_dealt} damage!", True, GREEN)
            else:
                dmg_text = self.font_medium.render(f"Took {combat.damage_taken} damage!", True, RED)
            self.screen.blit(dmg_text, (SCREEN_WIDTH//2 - dmg_text.get_width()//2, box_y + 390))
    
    def draw_pause_menu(self, selected_index: int):
        """Draw pause menu."""
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Menu box
        box_w = 400
        box_h = 300
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2
        
        pygame.draw.rect(self.screen, UI_BG, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, UI_BORDER, (box_x, box_y, box_w, box_h), 3)
        
        # Title
        title = self.font_large.render("PAUSED", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, box_y + 30))
        
        options = [
            "Resume Game",
            "View Stats",
            "Controls",
            "Quit to Title"
        ]
        
        for i, opt in enumerate(options):
            oy = box_y + 100 + i * 50
            selected = (i == selected_index)
            
            if selected:
                pygame.draw.rect(self.screen, MENU_SELECTED, (box_x + 30, oy - 5, box_w - 60, 40))
                pygame.draw.rect(self.screen, UI_BORDER, (box_x + 30, oy - 5, box_w - 60, 40), 2)
                color = UI_TEXT_BRIGHT
                prefix = "► "
            else:
                color = UI_TEXT
                prefix = "  "
            
            opt_text = self.font_medium.render(f"{prefix}{opt}", True, color)
            self.screen.blit(opt_text, (box_x + 50, oy + 5))
        
        # Controls hint
        hint = self.font_small.render("UP/DOWN: Navigate  |  ENTER: Select  |  ESC: Resume", True, GRAY)
        self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, box_y + box_h - 40))
    
    def draw_title(self, anim_time: float):
        """Draw title screen."""
        self.screen.fill(BLACK)
        
        # Animated background
        for i in range(20):
            x = (anim_time * 20 + i * 100) % (SCREEN_WIDTH + 200) - 100
            y = 100 + math.sin(anim_time * 0.005 + i) * 50
            alpha = int(50 + 30 * math.sin(anim_time * 0.01 + i))
            color = (0, alpha, alpha // 2)
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 2)
        
        # Title
        title1 = self.font_title.render("APPSEC RPG", True, BRIGHT_GREEN)
        title2 = self.font_large.render("Guardians of the Code", True, CYAN)
        self.screen.blit(title1, (SCREEN_WIDTH//2 - title1.get_width()//2, 150))
        self.screen.blit(title2, (SCREEN_WIDTH//2 - title2.get_width()//2, 210))
        
        # Subtitle
        sub = self.font_medium.render("OWASP Top 10 Quiz Combat", True, UI_TEXT)
        self.screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, 260))
        
        # Start prompt
        pulse = int(127 + 127 * math.sin(anim_time * 0.005))
        start_color = (pulse, 255, pulse)
        start_text = self.font_medium.render("PRESS ENTER TO START", True, start_color)
        self.screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 350))
        
        # Controls
        controls = [
            "WASD / Arrow Keys: Move",
            "SPACE / ENTER: Interact / Continue",
            "ESC: Pause Menu",
            "Arrow Keys in Combat: Select Answer"
        ]
        for i, ctrl in enumerate(controls):
            ctrl_text = self.font_small.render(ctrl, True, GRAY)
            self.screen.blit(ctrl_text, (SCREEN_WIDTH//2 - ctrl_text.get_width()//2, 420 + i * 25))
        
        # Version
        ver = self.font_small.render("v1.0.0 - Built with Pygame", True, DARK_GRAY)
        self.screen.blit(ver, (SCREEN_WIDTH//2 - ver.get_width()//2, SCREEN_HEIGHT - 40))
    
    def draw_game_over(self, player: Player):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        
        box_w = 500
        box_h = 350
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2
        
        pygame.draw.rect(self.screen, UI_BG, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, RED, (box_x, box_y, box_w, box_h), 3)
        
        title = self.font_title.render("GAME OVER", True, RED)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, box_y + 40))
        
        stats = [
            f"Level Reached: {player.level}",
            f"Enemies Defeated: {player.enemies_defeated}",
            f"Questions Answered: {player.questions_answered}",
            f"Accuracy: {player.accuracy['correct']}/{player.accuracy['total']}" 
            if player.accuracy['total'] > 0 else "Accuracy: -"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.font_medium.render(stat, True, UI_TEXT)
            self.screen.blit(stat_text, (SCREEN_WIDTH//2 - stat_text.get_width()//2, box_y + 120 + i * 35))
        
        prompt = self.font_medium.render("PRESS ENTER TO RESTART", True, YELLOW)
        self.screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, box_y + box_h - 60))
    
    def draw_victory(self, player: Player):
        """Draw victory screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        
        box_w = 500
        box_h = 350
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2
        
        pygame.draw.rect(self.screen, UI_BG, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, GREEN, (box_x, box_y, box_w, box_h), 3)
        
        title = self.font_title.render("VICTORY!", True, GREEN)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, box_y + 40))
        
        sub = self.font_large.render("You secured the codebase!", True, BRIGHT_GREEN)
        self.screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, box_y + 100))
        
        stats = [
            f"Final Level: {player.level}",
            f"Enemies Defeated: {player.enemies_defeated}",
            f"Questions Answered: {player.questions_answered}",
            f"Accuracy: {player.accuracy['correct']}/{player.accuracy['total']}" 
            if player.accuracy['total'] > 0 else "Accuracy: -"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.font_medium.render(stat, True, UI_TEXT)
            self.screen.blit(stat_text, (SCREEN_WIDTH//2 - stat_text.get_width()//2, box_y + 160 + i * 35))
        
        prompt = self.font_medium.render("PRESS ENTER TO PLAY AGAIN", True, YELLOW)
        self.screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, box_y + box_h - 60))
    
    def draw_particles(self, particles: ParticleSystem, camera_x: float, camera_y: float):
        """Draw particles."""
        particles.draw(self.screen, camera_x, camera_y)


# =============================================================================
# GAME ENGINE
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
                        self.show_dialogue("Welcome, Guardian! Defeat the vulnerabilities\nto secure the codebase.", "SYSTEM")
                
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
        """Check if player is touching an enemy to start combat."""
        for enemy in self.enemies:
            if enemy.alive and check_entity_collision(self.player, enemy):
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
            self.player.accuracy['correct'] += 1
            self.combat.enemy.damage_flash = 200
            self.particles.add_explosion(self.combat.enemy.x, self.combat.enemy.y, GREEN, 8)
        else:
            self.combat.damage_taken = max(1, self.combat.enemy.atk - self.player.def_ // 2)
            self.player.hp -= self.combat.damage_taken
            self.player.damage_flash = 200
            self.player.screen_shake = 200
            self.particles.add_explosion(self.player.x, self.player.y, RED, 8)
        
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
                self.particles.add_explosion(self.player.x, self.player.y, YELLOW, 12)
            
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
        self.player.x += self.player.vx * dt / 1000
        self.player.y += self.player.vy * dt / 1000
        
        # Collision with world
        resolve_collision(self.player, WORLD_MAP)
        
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
                enemy.x += (dx / dist) * speed * dt / 1000
                enemy.y += (dy / dist) * speed * dt / 1000
                resolve_collision(enemy, WORLD_MAP)
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
            self.renderer.draw_hud(self.player)
            # Draw dialogue on top
            self.renderer.draw_dialogue_box(self.dialogue_text, self.dialogue_speaker)
        
        elif self.state == GameState.GAME_OVER:
            self.renderer.draw_game_over(self.player)
        
        elif self.state == GameState.VICTORY:
            self.renderer.draw_victory(self.player)
        
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
    print("Built with Pygame")
    print()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()