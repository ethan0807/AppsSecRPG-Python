#!/usr/bin/env python3
"""
AppSec RPG: Guardians of the Code
Application Security Quiz Combat Game
Built with Pygame - Retro Pixel Art Edition
"""

import pygame
import sys
import os
import math
import random
import array
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


def shuffle_choices(question: Dict) -> Tuple[List[str], int]:
    """Shuffle choices and return new choices list with correct answer index."""
    choices = question['choices'][:]
    correct_answer = choices[question['answer']]
    indices = list(range(len(choices)))
    random.shuffle(indices)
    shuffled_choices = [choices[i] for i in indices]
    new_answer_idx = indices.index(question['answer'])
    return shuffled_choices, new_answer_idx


def generate_8bit_tone(frequency: float, duration: float, sample_rate: int = 44100, wave_type: str = 'square') -> pygame.mixer.Sound:
    """Generate an 8-bit style tone programmatically."""
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    amplitude = 16384  # 16-bit signed max is 32767
    
    for i in range(n_samples):
        t = i / sample_rate
        if wave_type == 'square':
            value = amplitude if (t * frequency) % 1.0 < 0.5 else -amplitude
        elif wave_type == 'triangle':
            value = int(amplitude * 2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.5))) - amplitude)
        else:  # sawtooth
            value = int(amplitude * 2 * (t * frequency - math.floor(t * frequency + 0.5)))
        # Apply envelope
        envelope = min(1.0, t * 10) * min(1.0, (duration - t) * 5)
        buf[i] = int(value * envelope)
    
    sound = pygame.mixer.Sound(buffer=buf)
    return sound


def generate_background_music() -> pygame.mixer.Sound:
    """Generate a simple 8-bit background music loop."""
    sample_rate = 44100
    # Simple melody: notes in Hz (C major scale mostly)
    melody = [
        (523.25, 0.3),  # C5
        (659.25, 0.3),  # E5
        (783.99, 0.3),  # G5
        (1046.50, 0.3), # C6
        (783.99, 0.3),  # G5
        (659.25, 0.3),  # E5
        (523.25, 0.6),  # C5
        (0, 0.3),       # Rest
        (493.88, 0.3),  # B4
        (659.25, 0.3),  # E5
        (739.99, 0.3),  # F#5
        (987.77, 0.3),  # B5
        (739.99, 0.3),  # F#5
        (659.25, 0.3),  # E5
        (493.88, 0.6),  # B4
        (0, 0.3),       # Rest
    ]
    
    total_duration = sum(d for _, d in melody)
    n_samples = int(sample_rate * total_duration)
    buf = array.array('h', [0] * n_samples)
    amplitude = 8192  # Lower amplitude for background
    
    pos = 0
    for freq, dur in melody:
        note_samples = int(sample_rate * dur)
        for i in range(note_samples):
            if pos >= n_samples:
                break
            t = i / sample_rate
            if freq > 0:
                # Square wave with slight harmonic
                value = amplitude if (t * freq) % 1.0 < 0.5 else -amplitude
                # Add subtle second harmonic
                value += int(amplitude * 0.3 * (1 if (t * freq * 2) % 1.0 < 0.5 else -1))
            else:
                value = 0
            # Envelope
            envelope = min(1.0, t * 15) * min(1.0, (dur - t) * 8)
            buf[pos] = int(value * envelope)
            pos += 1
    
    sound = pygame.mixer.Sound(buffer=buf)
    return sound


# =============================================================================
pygame.font.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# =============================================================================
# CONSTANTS
# =============================================================================

# Screen - Larger for better visibility
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Game
TILE_SIZE = 32
PLAYER_SPEED = 180  # pixels per second
PLAYER_SIZE = 24
ENEMY_SIZE = 24

# Colors - Amber/Terminal palette (easier on eyes than pure green)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
AMBER = (255, 191, 0)
BRIGHT_AMBER = (255, 220, 100)
DARK_AMBER = (180, 120, 0)
VERY_DARK_AMBER = (60, 40, 0)
RED = (255, 60, 60)
BRIGHT_RED = (255, 120, 120)
DARK_RED = (180, 40, 40)
YELLOW = (255, 255, 0)
BRIGHT_YELLOW = (255, 255, 120)
CYAN = (0, 255, 255)
BRIGHT_CYAN = (100, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 140, 0)
GRAY = (120, 120, 120)
DARK_GRAY = (60, 60, 60)
UI_BG = (20, 15, 0)
UI_BORDER = (180, 120, 0)
UI_TEXT = (220, 180, 60)
UI_TEXT_BRIGHT = (255, 220, 100)
MENU_SELECTED = (60, 40, 0)
MENU_SELECTED_BORDER = (255, 191, 0)
HUD_BG = (0, 0, 0, 200)
SCANLINE_ALPHA = 20

# Game States
class GameState(Enum):
    TITLE = "title"
    OVERWORLD = "overworld"
    COMBAT = "combat"
    PAUSED = "paused"
    DIALOGUE = "dialogue"
    VICTORY = "victory"
    GAME_OVER = "game_over"

# World Map (0 = floor, 1 = wall) - Larger map
WORLD_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,1],
    [1,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,1],
    [1,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,1],
    [1,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,1],
    [1,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1],
    [1,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

MAP_WIDTH = len(WORLD_MAP[0])
MAP_HEIGHT = len(WORLD_MAP)
WORLD_WIDTH = MAP_WIDTH * TILE_SIZE
WORLD_HEIGHT = MAP_HEIGHT * TILE_SIZE

# Player spawn (tile coordinates)
PLAYER_SPAWN = (20, 18)

# Enemy types with distinct visual identities
ENEMY_TYPES = {
    'INJECTION': {
        'name': 'Injection Demon',
        'symbol': 'SQL',
        'sprite_name': 'injection',
        'category': 'Injection Attacks',
        'desc': 'Executes malicious SQL/NoSQL/LDAP commands',
        'color': (220, 60, 60),
        'glow': (255, 100, 100),
        'baseHp': 50,
        'baseAtk': 12,
        'xpReward': 50,
    },
    'XSS': {
        'name': 'XSS Specter',
        'symbol': '<X>',
        'sprite_name': 'xss',
        'category': 'Cross-Site Scripting',
        'desc': 'Injects malicious scripts into trusted pages',
        'color': (255, 140, 0),
        'glow': (255, 180, 80),
        'baseHp': 45,
        'baseAtk': 14,
        'xpReward': 50,
    },
    'CRYPTO': {
        'name': 'Crypto Phantom',
        'symbol': '🔒',
        'sprite_name': 'crypto',
        'category': 'Cryptographic Failures',
        'desc': 'Exposes sensitive data through weak crypto',
        'color': (180, 60, 200),
        'glow': (220, 140, 255),
        'baseHp': 55,
        'baseAtk': 10,
        'xpReward': 55,
    },
    'ACCESS': {
        'name': 'Access Control Wraith',
        'symbol': '🔑',
        'sprite_name': 'access',
        'category': 'Broken Access Control',
        'desc': 'Bypasses authorization checks',
        'color': (60, 180, 180),
        'glow': (140, 220, 255),
        'baseHp': 60,
        'baseAtk': 11,
        'xpReward': 60,
    },
    'DESIGN': {
        'name': 'Insecure Design Golem',
        'symbol': '⚙',
        'sprite_name': 'design',
        'category': 'Insecure Design',
        'desc': 'Missing security controls by design',
        'color': (160, 160, 40),
        'glow': (220, 220, 100),
        'baseHp': 65,
        'baseAtk': 13,
        'xpReward': 65,
    },
    'CONFIG': {
        'name': 'Config Goblin',
        'symbol': '⚙',
        'sprite_name': 'config',
        'category': 'Security Misconfiguration',
        'desc': 'Default creds, open ports, verbose errors',
        'color': (180, 100, 40),
        'glow': (255, 160, 80),
        'baseHp': 40,
        'baseAtk': 15,
        'xpReward': 45,
    },
    'DESERIALIZE': {
        'name': 'Deserialization Wraith',
        'symbol': '📦',
        'sprite_name': 'deserialize',
        'category': 'Insecure Deserialization',
        'desc': 'Untrusted data deserialized without validation',
        'color': (120, 40, 180),
        'glow': (180, 100, 255),
        'baseHp': 70,
        'baseAtk': 12,
        'xpReward': 70,
    },
    'LOGGING': {
        'name': 'Logging Phantom',
        'symbol': '📝',
        'sprite_name': 'logging',
        'category': 'Logging & Monitoring Failures',
        'desc': 'Insufficient logging to detect attacks',
        'color': (100, 100, 100),
        'glow': (180, 180, 180),
        'baseHp': 50,
        'baseAtk': 10,
        'xpReward': 50,
    },
    'AUTH': {
        'name': 'Auth Bypass Shade',
        'symbol': '👤',
        'sprite_name': 'auth',
        'category': 'Authentication Failures',
        'desc': 'Weak authentication, credential stuffing',
        'color': (200, 80, 100),
        'glow': (255, 140, 160),
        'baseHp': 55,
        'baseAtk': 13,
        'xpReward': 55,
    },
    'SSRF': {
        'name': 'SSRF Specter',
        'symbol': '→',
        'sprite_name': 'ssrf',
        'category': 'Server-Side Request Forgery',
        'desc': 'Server fetches attacker-controlled URLs',
        'color': (100, 180, 80),
        'glow': (160, 255, 120),
        'baseHp': 50,
        'baseAtk': 12,
        'xpReward': 55,
    },
}

# 10 enemy spawns on verified floor tiles
ENEMY_SPAWNS = [
    {'x': 5, 'y': 5, 'type': 'INJECTION'},
    {'x': 44, 'y': 5, 'type': 'XSS'},
    {'x': 6, 'y': 18, 'type': 'CRYPTO'},
    {'x': 45, 'y': 18, 'type': 'ACCESS'},
    {'x': 10, 'y': 10, 'type': 'DESIGN'},
    {'x': 40, 'y': 10, 'type': 'CONFIG'},
    {'x': 10, 'y': 14, 'type': 'DESERIALIZE'},
    {'x': 40, 'y': 14, 'type': 'LOGGING'},
    {'x': 25, 'y': 8, 'type': 'AUTH'},
    {'x': 25, 'y': 16, 'type': 'SSRF'},
]

ENEMY_HP_SCALING = 1.35
ENEMY_ATK_SCALING = 1.25

# =============================================================================
# EXPANDED QUESTION BANK - 60+ Questions Across 12 Categories
# =============================================================================

QUESTIONS = {
    'Injection Attacks': [
        {'question': 'What is SQL Injection?', 'choices': ['Inserting malicious SQL via user input', 'Injecting JavaScript into web pages', 'Uploading malicious files', 'Brute forcing passwords'], 'answer': 0},
        {'question': 'Best defense against SQL Injection?', 'choices': ['Parameterized queries / prepared statements', 'Escaping special characters', 'Input validation only', 'Using stored procedures only'], 'answer': 0},
        {'question': 'What is NoSQL Injection?', 'choices': ['Injecting malicious queries into MongoDB/NoSQL', 'Injecting SQL into NoSQL databases', 'JavaScript injection in databases', 'Cross-site scripting via databases'], 'answer': 0},
        {'question': 'Which prevents LDAP Injection?', 'choices': ['Input validation and escaping LDAP metacharacters', 'Using parameterized LDAP queries', 'Disabling LDAP entirely', 'Both A and B'], 'answer': 3},
        {'question': 'What is Command Injection?', 'choices': ['Executing arbitrary OS commands via user input', 'Injecting SQL commands', 'Injecting JavaScript', 'Buffer overflow attacks'], 'answer': 0},
        {'question': 'How to prevent Command Injection?', 'choices': ['Avoid shell commands, use safe APIs, validate input', 'Escape all shell metacharacters', 'Disable shell access', 'Use only built-in commands'], 'answer': 0},
        {'question': 'What is Second-Order SQL Injection?', 'choices': ['Malicious input stored, executed later in different context', 'Two SQL injections chained', 'Injection in backup queries', 'Double encoding attack'], 'answer': 0},
        {'question': 'What is ORM Injection?', 'choices': ['Injecting via object-relational mapping frameworks', 'Injecting into object models', 'SQL injection in ORM', 'Both A and C'], 'answer': 0},
        {'question': 'What is Template Injection (SSTI)?', 'choices': ['Injecting template expressions to execute code', 'Injecting SQL into templates', 'XSS in template engines', 'CSS injection'], 'answer': 0},
        {'question': 'What is XPath Injection?', 'choices': ['Injecting malicious XPath queries', 'Injecting SQL via XML', 'XSS via XML', 'XML parsing errors'], 'answer': 0},
        {'question': 'What is Header Injection?', 'choices': ['Injecting malicious headers (CRLF injection)', 'HTTP header manipulation', 'Cookie injection', 'Host header attack'], 'answer': 0},
        {'question': 'What is HQL Injection?', 'choices': ['Hibernate Query Language injection', 'HTML Query Language injection', 'Hypertext Query injection', 'Host Query injection'], 'answer': 0},
    ],
    'Cross-Site Scripting': [
        {'question': 'What is Cross-Site Scripting (XSS)?', 'choices': ['Injecting malicious scripts into trusted websites', 'Stealing database credentials', 'Bypassing authentication', 'Denial of service attacks'], 'answer': 0},
        {'question': 'What is Reflected XSS?', 'choices': ['Script reflected off web server in response', 'Script stored in database', 'Script in DOM only', 'Script in cookies'], 'answer': 0},
        {'question': 'What is Stored XSS?', 'choices': ['Malicious script permanently stored on server', 'Script in URL parameters', 'Script in local storage', 'Script in headers'], 'answer': 0},
        {'question': 'What is DOM-based XSS?', 'choices': ['XSS via client-side DOM manipulation', 'XSS via server response', 'XSS via database', 'XSS via cookies'], 'answer': 0},
        {'question': 'Best defense against XSS?', 'choices': ['Context-aware output encoding + CSP', 'Input validation only', 'WAF rules only', 'Disabling JavaScript'], 'answer': 0},
        {'question': 'What does Content Security Policy (CSP) do?', 'choices': ['Restricts script sources to prevent XSS', 'Encrypts content', 'Validates input', 'Logs attacks'], 'answer': 0},
    ],
    'Cryptographic Failures': [
        {'question': 'What is a Cryptographic Failure?', 'choices': ['Sensitive data exposed due to weak/no encryption', 'Broken authentication logic', 'Cross-site scripting attacks', 'Insecure deserialization'], 'answer': 0},
        {'question': 'Which is a secure password hashing algorithm?', 'choices': ['bcrypt or Argon2', 'MD5', 'SHA-1', 'Base64 encoding'], 'answer': 0},
        {'question': 'What should NEVER be transmitted in plaintext?', 'choices': ['Passwords and session tokens', 'Public API documentation', 'HTML content', 'CSS stylesheets'], 'answer': 0},
        {'question': 'What is wrong with using ECB mode for encryption?', 'choices': ['Identical plaintext blocks produce identical ciphertext', 'It is too slow', 'It requires too much memory', 'It is not standardized'], 'answer': 0},
        {'question': 'Why is MD5 unsuitable for password hashing?', 'choices': ['Fast, no salt, vulnerable to collisions', 'Too slow', 'Not widely supported', 'Produces variable length output'], 'answer': 0},
        {'question': 'What is a timing attack?', 'choices': ['Measuring response time to infer secrets', 'Attacking system clock', 'Race condition exploit', 'Replay attack'], 'answer': 0},
        {'question': 'How to prevent timing attacks on string comparison?', 'choices': ['Constant-time comparison functions', 'Add random delays', 'Use shorter strings', 'Disable comparison'], 'answer': 0},
    ],
    'Broken Access Control': [
        {'question': 'What is Broken Access Control?', 'choices': ['Users can access resources they should not', 'Weak encryption algorithms', 'SQL injection vulnerabilities', 'Missing security logging'], 'answer': 0},
        {'question': 'Which is an example of Insecure Direct Object Reference (IDOR)?', 'choices': ['Changing /user/123 to /user/124 to access another user data', 'Injecting SQL via input fields', 'Using default admin credentials', 'Not logging failed login attempts'], 'answer': 0},
        {'question': 'How to prevent Broken Access Control?', 'choices': ['Implement proper authorization checks on every request', 'Use stronger encryption', 'Sanitize all inputs', 'Enable debug logging'], 'answer': 0},
        {'question': 'What is horizontal privilege escalation?', 'choices': ['Accessing another user data at same privilege level', 'Gaining admin from user', 'Escalating via kernel exploit', 'Bypassing firewall'], 'answer': 0},
        {'question': 'What is vertical privilege escalation?', 'choices': ['Gaining higher privileges (user to admin)', 'Accessing peer data', 'Escaping container', 'Bypassing WAF'], 'answer': 0},
    ],
    'Insecure Design': [
        {'question': 'What is Insecure Design?', 'choices': ['Missing or ineffective security controls by design', 'Implementation bugs in secure code', 'Weak encryption algorithms', 'Unpatched software'], 'answer': 0},
        {'question': 'How to address Insecure Design?', 'choices': ['Threat modeling and secure design patterns', 'More penetration testing', 'Stronger firewalls', 'Better logging'], 'answer': 0},
        {'question': 'What is threat modeling?', 'choices': ['Identifying threats and mitigations during design', 'Penetration testing', 'Code review', 'Vulnerability scanning'], 'answer': 0},
        {'question': 'What is a security anti-pattern?', 'choices': ['Common design flaw that creates vulnerabilities', 'Secure coding practice', 'Encryption standard', 'Authentication protocol'], 'answer': 0},
    ],
    'Security Misconfiguration': [
        {'question': 'What is Security Misconfiguration?', 'choices': ['Default configs, open ports, verbose errors', 'Weak password policies', 'SQL injection flaws', 'Missing encryption'], 'answer': 0},
        {'question': 'Which is a security misconfiguration?', 'choices': ['Directory listing enabled on web server', 'Using parameterized queries', 'Implementing rate limiting', 'Encrypting data at rest'], 'answer': 0},
        {'question': 'What should be disabled in production?', 'choices': ['Debug mode, verbose errors, default accounts', 'HTTPS, encryption, logging', 'Rate limiting, CSP, HSTS', 'Authentication, authorization, validation'], 'answer': 0},
        {'question': 'What is the principle of least privilege?', 'choices': ['Grant minimum necessary permissions', 'Grant all permissions by default', 'Grant admin to developers', 'Disable all permissions'], 'answer': 0},
    ],
    'Vulnerable Components': [
        {'question': 'What are Vulnerable and Outdated Components?', 'choices': ['Using libraries with known vulnerabilities', 'Custom code with bugs', 'Weak encryption', 'Missing access controls'], 'answer': 0},
        {'question': 'How to manage component vulnerabilities?', 'choices': ['Software composition analysis (SCA) and regular updates', 'Only use custom code', 'Disable all third-party libraries', 'Use older stable versions'], 'answer': 0},
        {'question': 'What is a Software Bill of Materials (SBOM)?', 'choices': ['Inventory of all components and dependencies', 'Bill for software purchases', 'License compliance document', 'Vulnerability report'], 'answer': 0},
    ],
    'Authentication Failures': [
        {'question': 'What is an Authentication Failure?', 'choices': ['Weak authentication allowing credential stuffing/brute force', 'SQL injection in login form', 'XSS on login page', 'Missing HTTPS'], 'answer': 0},
        {'question': 'Best practice for authentication?', 'choices': ['Multi-factor authentication (MFA) + rate limiting', 'Complex password requirements only', 'IP-based blocking only', 'CAPTCHA on every request'], 'answer': 0},
        {'question': 'What is credential stuffing?', 'choices': ['Using breached credentials on other sites', 'Stuffing credentials into database', 'Injecting credentials via SQL', 'Stealing credentials via XSS'], 'answer': 0},
        {'question': 'What is session fixation?', 'choices': ['Attacker sets user session ID before login', 'Stealing session cookie', 'Predicting session ID', 'Replaying session'], 'answer': 0},
        {'question': 'How to prevent session fixation?', 'choices': ['Regenerate session ID after login', 'Use longer session IDs', 'Encrypt session cookies', 'Disable cookies'], 'answer': 0},
        {'question': 'What is passwordless authentication?', 'choices': ['Auth without passwords (magic links, WebAuthn, etc.)', 'Empty passwords allowed', 'No authentication', 'Using API keys only'], 'answer': 0},
    ],
    'Insecure Deserialization': [
        {'question': 'What is Insecure Deserialization?', 'choices': ['Untrusted data deserialized without validation', 'Weak encryption of serialized data', 'SQL injection via serialized objects', 'XSS via JSON parsing'], 'answer': 0},
        {'question': 'How to prevent deserialization attacks?', 'choices': ['Validate/verify serialized data, use safe formats (JSON)', 'Encrypt all serialized data', 'Disable serialization entirely', 'Use only binary formats'], 'answer': 0},
        {'question': 'What is a gadget chain?', 'choices': ['Series of method calls leading to RCE during deserialization', 'Encryption key chain', 'Certificate chain', 'Dependency chain'], 'answer': 0},
    ],
    'Logging & Monitoring Failures': [
        {'question': 'What is a Logging Failure?', 'choices': ['Insufficient logging to detect attacks', 'Logging too much data', 'Logs stored in plaintext', 'Logs not rotated'], 'answer': 0},
        {'question': 'What should security logs include?', 'choices': ['Failed logins, access denials, input validation failures', 'Only successful logins', 'All HTTP requests', 'Database query logs only'], 'answer': 0},
        {'question': 'What is log injection?', 'choices': ['Injecting malicious content into log files', 'Injecting logs into database', 'Logging injection attacks', 'SQL injection via logs'], 'answer': 0},
    ],
    'Server-Side Request Forgery': [
        {'question': 'What is Server-Side Request Forgery (SSRF)?', 'choices': ['Server fetches attacker-controlled URLs', 'Client-side request manipulation', 'Cross-site request forgery', 'SQL injection via HTTP headers'], 'answer': 0},
        {'question': 'How to prevent SSRF?', 'choices': ['Validate/sanitize user-supplied URLs, allowlist destinations', 'Disable all outbound HTTP requests', 'Use HTTPS only', 'Implement CORS headers'], 'answer': 0},
        {'question': 'What is a blind SSRF?', 'choices': ['SSRF without direct response to attacker', 'SSRF with full response', 'SSRF via blind SQL injection', 'SSRF in blind context'], 'answer': 0},
    ],
    'API Security': [
        {'question': 'What is Broken Object Level Authorization (BOLA)?', 'choices': ['API fails to verify user access to specific objects', 'Broken encryption in API', 'API rate limiting bypass', 'API version mismatch'], 'answer': 0},
        {'question': 'What is Mass Assignment?', 'choices': ['API binds client data to internal objects without filtering', 'Assigning many users at once', 'Bulk API operations', 'Mass data import'], 'answer': 0},
        {'question': 'How to prevent Mass Assignment?', 'choices': ['Explicit allowlists for bindable properties', 'Disable all updates', 'Use only GET requests', 'Encrypt request body'], 'answer': 0},
        {'question': 'What is API rate limiting?', 'choices': ['Restricting requests per client per time window', 'Limiting API versions', 'Limiting response size', 'Limiting endpoints'], 'answer': 0},
        {'question': 'What is GraphQL query depth limiting?', 'choices': ['Preventing deeply nested queries causing DoS', 'Limiting GraphQL versions', 'Limiting query results', 'Limiting mutations'], 'answer': 0},
        {'question': 'What is API security testing?', 'choices': ['Testing API endpoints for vulnerabilities', 'Testing API performance', 'Testing API documentation', 'Testing API versions'], 'answer': 0},
        {'question': 'What is API gateway security?', 'choices': ['Centralized auth, rate limiting, validation', 'Load balancing only', 'Caching only', 'Monitoring only'], 'answer': 0},
        {'question': 'What is CORS misconfiguration?', 'choices': ['Allowing arbitrary origins with credentials', 'Allowing specific origins', 'Blocking all origins', 'Using same-origin policy'], 'answer': 0},
        {'question': 'What is API versioning security?', 'choices': ['Deprecating old versions securely', 'Using only v1', 'No versioning', 'All versions public'], 'answer': 0},
    ],
    'Supply Chain Security': [
        {'question': 'What is a supply chain attack?', 'choices': ['Compromising software via third-party dependencies', 'Attacking physical supply chain', 'Attacking CI/CD pipeline only', 'Vendor phishing'], 'answer': 0},
        {'question': 'What is dependency confusion?', 'choices': ['Public package overrides private with same name', 'Confusing dependency versions', 'Circular dependencies', 'Missing dependencies'], 'answer': 0},
        {'question': 'How to prevent dependency confusion?', 'choices': ['Use scoped packages, pin versions, private registries', 'Avoid all public packages', 'Use only local packages', 'Disable package managers'], 'answer': 0},
        {'question': 'What is SLSA (Supply Chain Levels for Software Artifacts)?', 'choices': ['Framework for supply chain integrity', 'Software license agreement', 'Security logging standard', 'Static analysis tool'], 'answer': 0},
        {'question': 'What is a provenance attestation?', 'choices': ['Verified build metadata', 'Source code license', 'Vulnerability scan result', 'Dependency list'], 'answer': 0},
        {'question': 'What is sigstore?', 'choices': ['Keyless signing for software artifacts', 'Secret storage', 'Certificate authority', 'Package registry'], 'answer': 0},
        {'question': 'What is Software Supply Chain Integrity?', 'choices': ['Ensuring artifacts untampered from build to deploy', 'Fast CI/CD pipelines', 'Automated testing', 'Code review'], 'answer': 0},
    ],
    'Cloud & Container Security': [
        {'question': 'What is container escape?', 'choices': ['Breaking out of container to host', 'Escaping Kubernetes cluster', 'Escaping VPC', 'Escaping subnet'], 'answer': 0},
        {'question': 'What is the principle of least privilege in Kubernetes?', 'choices': ['Pods get minimum required permissions', 'All pods run as root', 'No RBAC', 'Host network for all pods'], 'answer': 0},
        {'question': 'What is a misconfigured S3 bucket?', 'choices': ['Publicly accessible bucket with sensitive data', 'Encrypted bucket', 'Bucket with versioning', 'Bucket in wrong region'], 'answer': 0},
        {'question': 'What is IAM policy over-permission?', 'choices': ['Granting broader permissions than needed', 'No IAM policies', 'Too many IAM users', 'Expired credentials'], 'answer': 0},
        {'question': 'What is Kubernetes RBAC?', 'choices': ['Role-based access control for cluster resources', 'Resource-based access control', 'Root-based access control', 'Remote-based access control'], 'answer': 0},
        {'question': 'What is a Kubernetes admission controller?', 'choices': ['Validates/modifies requests before persistence', 'Controls pod admission to nodes', 'Manages ingress traffic', 'Handles authentication'], 'answer': 0},
        {'question': 'What is cloud metadata service exposure?', 'choices': ['SSRF accessing instance metadata (IMDSv1)', 'Exposed cloud console', 'Public S3 bucket', 'Open security group'], 'answer': 0},
        {'question': 'What is container image scanning?', 'choices': ['Scanning images for vulnerabilities before deploy', 'Scanning running containers', 'Scanning host OS', 'Scanning network traffic'], 'answer': 0},
    ],
}

# Flatten all questions for tracking
ALL_QUESTIONS = []
for cat, qs in QUESTIONS.items():
    for q in qs:
        q['category'] = cat
        ALL_QUESTIONS.append(q)

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
    atk: int = 18
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
    invulnerable: float = 0

@dataclass
class Enemy:
    x: float
    y: float
    width: int = ENEMY_SIZE
    height: int = ENEMY_SIZE
    type: str = 'INJECTION'
    name: str = 'Enemy'
    symbol: str = '?'
    sprite_name: str = 'default'
    category: str = 'Unknown'
    desc: str = ''
    color: Tuple[int, int, int] = (255, 0, 0)
    glow: Tuple[int, int, int] = (255, 100, 100)
    max_hp: int = 50
    hp: int = 50
    atk: int = 10
    xp_reward: int = 25
    level: int = 1
    
    # AI
    patrol_timer: float = 0
    patrol_dir: int = 0
    float_offset: float = 0
    alert: bool = False
    chase_timer: float = 0
    
    # Visual
    damage_flash: float = 0
    defeated: bool = False
    defeat_timer: float = 0

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: Tuple[int, int, int]
    life: float
    max_life: float
    size: float
    type: str = 'normal'  # normal, spark, text

@dataclass
class ParticleSystem:
    particles: List[Particle] = field(default_factory=list)
    
    def add(self, x: float, y: float, color: Tuple[int, int, int], velocity: Tuple[float, float], life: float, size: float, count: int = 1):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 80)
            vx = velocity[0] + math.cos(angle) * speed
            vy = velocity[1] + math.sin(angle) * speed
            self.particles.append(Particle(x, y, vx, vy, color, life, life, size))
    
    def add_explosion(self, x: float, y: float, color: Tuple[int, int, int], count: int = 20):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            self.particles.append(Particle(
                x, y, math.cos(angle) * speed, math.sin(angle) * speed,
                color, random.uniform(300, 600), random.uniform(300, 600),
                random.uniform(2, 5), 'spark'
            ))
    
    def add_damage_number(self, x: float, y: float, damage: int, critical: bool = False):
        color = BRIGHT_RED if critical else YELLOW
        self.particles.append(Particle(x, y, 0, -40, color, 1000, 1000, 16, 'text'))
        self.particles[-1].damage_value = damage
    
    def update(self, dt: float):
        for p in self.particles[:]:
            p.life -= dt
            if p.life <= 0:
                self.particles.remove(p)
                continue
            p.x += p.vx * dt / 1000
            p.y += p.vy * dt / 1000
            p.vy += 20 * dt / 1000  # gravity
    
    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        for p in self.particles:
            # Clamp life ratio to valid range
            life_ratio = max(0.0, min(1.0, p.life / p.max_life))
            alpha = int(255 * life_ratio)
            if p.type == 'text':
                # Damage numbers drawn separately
                continue
            # Ensure color components are valid integers 0-255
            r = max(0, min(255, int(p.color[0])))
            g = max(0, min(255, int(p.color[1])))
            b = max(0, min(255, int(p.color[2])))
            color = (r, g, b, alpha)
            px = int(p.x - camera_x)
            py = int(p.y - camera_y)
            if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
                surf = pygame.Surface((int(p.size * 2), int(p.size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (int(p.size), int(p.size)), int(p.size))
                surface.blit(surf, (px - int(p.size), py - int(p.size)))

@dataclass
class CombatState:
    enemy: Optional[Enemy] = None
    question: Optional[Dict] = None
    choices: List[str] = field(default_factory=list)
    correct_answer_idx: int = 0
    selected: int = 0
    timer: float = 30.0
    max_timer: float = 30.0
    waiting_for_answer: bool = False
    result: Optional[str] = None
    result_timer: float = 0
    damage_dealt: int = 0
    damage_taken: int = 0
    turn: str = 'player'  # 'player', 'enemy'
    typewriter_text: str = ''
    typewriter_timer: float = 0
    typewriter_index: int = 0
    question_asked: bool = False
    used_questions: Set[int] = field(default_factory=set)

# =============================================================================
# SPRITE GENERATION
# =============================================================================

def create_player_sprites() -> Dict[str, List[pygame.Surface]]:
    """Create detailed pixel art player sprites for 4 directions, 2 frames each."""
    sprites = {'down': [], 'up': [], 'left': [], 'right': []}
    colors = {
        'skin': (255, 210, 160),
        'skin_dark': (220, 170, 120),
        'hair': (60, 40, 20),
        'hair_dark': (40, 25, 15),
        'shirt': (60, 100, 180),
        'shirt_dark': (40, 70, 140),
        'pants': (40, 40, 80),
        'pants_dark': (25, 25, 50),
        'boots': (30, 20, 10),
        'eyes': (60, 100, 180),
        'outline': (20, 15, 10),
    }
    
    for direction in ['down', 'up', 'left', 'right']:
        for frame in range(2):
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            px = 4  # offset for 24px character in 32px canvas
            py = 2
            
            # Body proportions
            if direction == 'down':
                # Head
                pygame.draw.ellipse(surf, colors['skin'], (px+6, py+2, 12, 10))
                pygame.draw.ellipse(surf, colors['outline'], (px+6, py+2, 12, 10), 1)
                # Hair
                pygame.draw.ellipse(surf, colors['hair'], (px+5, py+1, 14, 8))
                # Eyes
                eye_y = py + 5 + (frame * 1)
                pygame.draw.circle(surf, colors['eyes'], (px+9, eye_y), 1)
                pygame.draw.circle(surf, colors['eyes'], (px+14, eye_y), 1)
                # Shirt
                pygame.draw.rect(surf, colors['shirt'], (px+4, py+11, 16, 12))
                pygame.draw.rect(surf, colors['shirt_dark'], (px+4, py+11, 16, 12), 1)
                # Pants
                pygame.draw.rect(surf, colors['pants'], (px+6, py+22, 12, 8))
                pygame.draw.rect(surf, colors['pants_dark'], (px+6, py+22, 12, 8), 1)
                # Boots
                boot_y = py + 28 + (frame * 1)
                pygame.draw.rect(surf, colors['boots'], (px+6, boot_y, 5, 4))
                pygame.draw.rect(surf, colors['boots'], (px+13, boot_y, 5, 4))
                
            elif direction == 'up':
                # Head
                pygame.draw.ellipse(surf, colors['skin'], (px+6, py+2, 12, 10))
                pygame.draw.ellipse(surf, colors['outline'], (px+6, py+2, 12, 10), 1)
                # Hair
                pygame.draw.ellipse(surf, colors['hair'], (px+5, py+1, 14, 8))
                # Eyes (back of head - small dots)
                pygame.draw.circle(surf, colors['hair_dark'], (px+9, py+6), 1)
                pygame.draw.circle(surf, colors['hair_dark'], (px+14, py+6), 1)
                # Shirt (back)
                pygame.draw.rect(surf, colors['shirt_dark'], (px+4, py+11, 16, 12))
                pygame.draw.rect(surf, colors['shirt'], (px+4, py+11, 16, 12), 1)
                # Pants
                pygame.draw.rect(surf, colors['pants'], (px+6, py+22, 12, 8))
                pygame.draw.rect(surf, colors['pants_dark'], (px+6, py+22, 12, 8), 1)
                # Boots
                boot_y = py + 28 + (frame * 1)
                pygame.draw.rect(surf, colors['boots'], (px+6, boot_y, 5, 4))
                pygame.draw.rect(surf, colors['boots'], (px+13, boot_y, 5, 4))
                
            elif direction == 'left':
                # Head
                pygame.draw.ellipse(surf, colors['skin'], (px+8, py+2, 10, 12))
                pygame.draw.ellipse(surf, colors['outline'], (px+8, py+2, 10, 12), 1)
                # Hair
                pygame.draw.ellipse(surf, colors['hair'], (px+7, py+1, 12, 8))
                # Eye (profile)
                eye_x = px + 11 + (frame * 1)
                pygame.draw.circle(surf, colors['eyes'], (eye_x, py+7), 1)
                # Shirt
                pygame.draw.rect(surf, colors['shirt'], (px+8, py+12, 12, 14))
                pygame.draw.rect(surf, colors['shirt_dark'], (px+8, py+12, 12, 14), 1)
                # Pants
                pygame.draw.rect(surf, colors['pants'], (px+9, py+24, 10, 8))
                pygame.draw.rect(surf, colors['pants_dark'], (px+9, py+24, 10, 8), 1)
                # Boots
                boot_y = py + 30 + (frame * 1)
                pygame.draw.rect(surf, colors['boots'], (px+9, boot_y, 4, 4))
                pygame.draw.rect(surf, colors['boots'], (px+14, boot_y, 4, 4))
                
            elif direction == 'right':
                # Head
                pygame.draw.ellipse(surf, colors['skin'], (px+6, py+2, 10, 12))
                pygame.draw.ellipse(surf, colors['outline'], (px+6, py+2, 10, 12), 1)
                # Hair
                pygame.draw.ellipse(surf, colors['hair'], (px+5, py+1, 12, 8))
                # Eye (profile)
                eye_x = px + 12 - (frame * 1)
                pygame.draw.circle(surf, colors['eyes'], (eye_x, py+7), 1)
                # Shirt
                pygame.draw.rect(surf, colors['shirt'], (px+6, py+12, 12, 14))
                pygame.draw.rect(surf, colors['shirt_dark'], (px+6, py+12, 12, 14), 1)
                # Pants
                pygame.draw.rect(surf, colors['pants'], (px+7, py+24, 10, 8))
                pygame.draw.rect(surf, colors['pants_dark'], (px+7, py+24, 10, 8), 1)
                # Boots
                boot_y = py + 30 + (frame * 1)
                pygame.draw.rect(surf, colors['boots'], (px+7, boot_y, 4, 4))
                pygame.draw.rect(surf, colors['boots'], (px+12, boot_y, 4, 4))
            
            sprites[direction].append(surf)
    
    return sprites

def create_enemy_sprites() -> Dict[str, pygame.Surface]:
    """Create distinctive pixel art sprites for each enemy type."""
    sprites = {}
    
    for etype, data in ENEMY_TYPES.items():
        surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        cx, cy = 24, 24
        color = data['color']
        glow = data['glow']
        dark = tuple(max(0, c - 60) for c in color)
        
        if etype == 'INJECTION':
            # SQL demon - database cylinder with horns
            pygame.draw.ellipse(surf, color, (8, 6, 32, 10))
            pygame.draw.ellipse(surf, dark, (8, 6, 32, 10), 2)
            pygame.draw.rect(surf, color, (8, 11, 32, 22))
            pygame.draw.line(surf, dark, (8, 11), (8, 33), 2)
            pygame.draw.line(surf, dark, (39, 11), (39, 33), 2)
            pygame.draw.ellipse(surf, color, (8, 29, 32, 10))
            pygame.draw.ellipse(surf, dark, (8, 29, 32, 10), 2)
            # Horns
            pygame.draw.polygon(surf, dark, [(12, 8), (8, 0), (16, 4)])
            pygame.draw.polygon(surf, dark, [(36, 8), (40, 0), (32, 4)])
            # SQL text
            font = pygame.font.SysFont('monospace', 10, bold=True)
            txt = font.render('SQL', True, WHITE)
            surf.blit(txt, (17, 18))
            # Glowing eyes
            pygame.draw.circle(surf, glow, (15, 14), 2)
            pygame.draw.circle(surf, glow, (33, 14), 2)
            
        elif etype == 'XSS':
            # XSS Specter - ghost with script tags
            # Ghost body
            points = [(24, 6), (42, 6), (42, 38), (36, 44), (30, 38), (24, 44), (18, 38), (12, 44), (6, 38), (6, 6)]
            pygame.draw.polygon(surf, color, points)
            pygame.draw.polygon(surf, dark, points, 2)
            # Wavy bottom
            for i in range(3):
                x = 10 + i * 12
                pygame.draw.arc(surf, dark, (x, 36, 12, 12), 0, math.pi, 2)
            # Eyes
            pygame.draw.ellipse(surf, WHITE, (14, 14, 8, 10))
            pygame.draw.ellipse(surf, WHITE, (26, 14, 8, 10))
            pygame.draw.circle(surf, glow, (17, 18), 3)
            pygame.draw.circle(surf, glow, (29, 18), 3)
            # <script> text
            font = pygame.font.SysFont('monospace', 8, bold=True)
            txt = font.render('<script>', True, glow)
            surf.blit(txt, (9, 30))
            
        elif etype == 'CRYPTO':
            # Crypto Phantom - lock with cracked key
            # Lock body
            pygame.draw.rect(surf, color, (12, 18, 24, 20), border_radius=3)
            pygame.draw.rect(surf, dark, (12, 18, 24, 20), 2, border_radius=3)
            # Shackle
            pygame.draw.arc(surf, color, (10, 8, 28, 20), math.pi, 2*math.pi, 4)
            pygame.draw.arc(surf, dark, (10, 8, 28, 20), math.pi, 2*math.pi, 2)
            # Keyhole
            pygame.draw.circle(surf, BLACK, (24, 28), 4)
            pygame.draw.rect(surf, BLACK, (22, 32, 4, 6))
            # Crack
            pygame.draw.line(surf, RED, (20, 22), (28, 34), 2)
            pygame.draw.line(surf, RED, (28, 22), (20, 34), 2)
            # Warning symbol
            pygame.draw.polygon(surf, YELLOW, [(24, 10), (18, 20), (30, 20)])
            pygame.draw.polygon(surf, dark, [(24, 10), (18, 20), (30, 20)], 2)
            
        elif etype == 'ACCESS':
            # Access Control Wraith - key with broken chain
            # Key
            pygame.draw.circle(surf, color, (18, 30), 8)
            pygame.draw.circle(surf, dark, (18, 30), 8, 2)
            pygame.draw.circle(surf, BLACK, (18, 30), 3)
            pygame.draw.rect(surf, color, (16, 30, 20, 6))
            pygame.draw.rect(surf, color, (26, 28, 6, 10))
            pygame.draw.rect(surf, color, (32, 28, 6, 10))
            # Broken chain
            pygame.draw.ellipse(surf, GRAY, (6, 12, 12, 12), 2)
            pygame.draw.ellipse(surf, GRAY, (14, 12, 12, 12), 2)
            pygame.draw.line(surf, RED, (16, 18), (18, 18), 3)
            # Glowing particles
            for i in range(4):
                x = random.randint(6, 42)
                y = random.randint(6, 42)
                pygame.draw.circle(surf, glow, (x, y), 2)
                
        elif etype == 'DESIGN':
            # Insecure Design Golem - gears with missing teeth
            for i in range(3):
                gx = 12 + i * 16
                gy = 12 + i * 8
                # Gear
                pygame.draw.circle(surf, color, (gx, gy), 14, 3)
                pygame.draw.circle(surf, dark, (gx, gy), 14, 1)
                # Missing teeth (insecure)
                for tooth in range(8):
                    if tooth % 3 == 0:  # Missing teeth
                        continue
                    angle = tooth * math.pi / 4
                    x1 = gx + math.cos(angle) * 10
                    y1 = gy + math.sin(angle) * 10
                    x2 = gx + math.cos(angle) * 16
                    y2 = gy + math.sin(angle) * 16
                    pygame.draw.line(surf, color, (x1, y1), (x2, y2), 2)
                # Center hole
                pygame.draw.circle(surf, BLACK, (gx, gy), 4)
                
        elif etype == 'CONFIG':
            # Config Goblin - config file with warning signs
            pygame.draw.rect(surf, color, (8, 6, 32, 36), border_radius=3)
            pygame.draw.rect(surf, dark, (8, 6, 32, 36), 2, border_radius=3)
            # Config lines
            for i in range(6):
                py = 12 + i * 5
                pygame.draw.line(surf, GRAY, (14, py), (38, py), 1)
            # Warning triangles
            for i in range(3):
                wx = 14 + i * 12
                pygame.draw.polygon(surf, YELLOW, [(wx, 20), (wx+6, 20), (wx+3, 16)])
                pygame.draw.polygon(surf, dark, [(wx, 20), (wx+6, 20), (wx+3, 16)], 1)
            # .env text
            font = pygame.font.SysFont('monospace', 8, bold=True)
            txt = font.render('.env', True, glow)
            surf.blit(txt, (20, 34))
            
        elif etype == 'DESERIALIZE':
            # Deserialization Wraith - box with malicious payload
            # Box
            pygame.draw.rect(surf, color, (10, 10, 28, 28), border_radius=2)
            pygame.draw.rect(surf, dark, (10, 10, 28, 28), 2, border_radius=2)
            # Lid
            pygame.draw.rect(surf, tuple(min(255, c+30) for c in color), (8, 8, 32, 8), border_radius=2)
            pygame.draw.rect(surf, dark, (8, 8, 32, 8), 2, border_radius=2)
            # Malicious content leaking
            for i in range(5):
                px = random.randint(14, 38)
                py = random.randint(14, 38)
                pygame.draw.circle(surf, RED, (px, py), 2)
            # Skull
            pygame.draw.circle(surf, WHITE, (24, 24), 6)
            pygame.draw.circle(surf, BLACK, (21, 22), 1)
            pygame.draw.circle(surf, BLACK, (27, 22), 1)
            pygame.draw.line(surf, BLACK, (21, 28), (27, 28), 2)
            
        elif etype == 'LOGGING':
            # Logging Phantom - log file with missing entries
            pygame.draw.rect(surf, color, (10, 6, 28, 36), border_radius=2)
            pygame.draw.rect(surf, dark, (10, 6, 28, 36), 2, border_radius=2)
            # Log lines
            for i in range(8):
                py = 12 + i * 4
                if i in [2, 5, 7]:  # Missing lines (gaps)
                    continue
                pygame.draw.line(surf, GRAY, (16, py), (32, py), 2)
            # Missing indicator
            font = pygame.font.SysFont('monospace', 10, bold=True)
            txt = font.render('...', True, RED)
            surf.blit(txt, (16, 22))
            # Blindfolded eye
            pygame.draw.ellipse(surf, WHITE, (16, 10, 16, 8))
            pygame.draw.line(surf, BLACK, (16, 14), (32, 14), 2)
            
        elif etype == 'AUTH':
            # Auth Bypass Shade - masked figure with broken shield
            # Cloak
            pygame.draw.ellipse(surf, color, (8, 10, 32, 34))
            pygame.draw.ellipse(surf, dark, (8, 10, 32, 34), 2)
            # Mask
            pygame.draw.ellipse(surf, GRAY, (14, 14, 20, 16))
            pygame.draw.ellipse(surf, dark, (14, 14, 20, 16), 1)
            # Eye holes
            pygame.draw.ellipse(surf, BLACK, (18, 18, 6, 8))
            pygame.draw.ellipse(surf, BLACK, (26, 18, 6, 8))
            # Glowing eyes behind mask
            pygame.draw.circle(surf, glow, (20, 21), 2)
            pygame.draw.circle(surf, glow, (28, 21), 2)
            # Broken shield
            pygame.draw.polygon(surf, DARK_GRAY, [(10, 36), (18, 24), (30, 24), (38, 36)])
            pygame.draw.line(surf, RED, (18, 24), (30, 24), 3)
            pygame.draw.line(surf, RED, (24, 20), (24, 36), 3)
            
        elif etype == 'SSRF':
            # SSRF Specter - server with outward arrow
            # Server box
            pygame.draw.rect(surf, color, (8, 12, 32, 24), border_radius=3)
            pygame.draw.rect(surf, dark, (8, 12, 32, 24), 2, border_radius=3)
            # Server lights
            for i in range(3):
                pygame.draw.circle(surf, CYAN, (16, 20 + i * 6), 2)
                pygame.draw.circle(surf, RED, (38, 20 + i * 6), 2)
            # Outward arrow
            pygame.draw.polygon(surf, YELLOW, [(40, 18), (48, 24), (40, 30)])
            pygame.draw.polygon(surf, dark, [(40, 18), (48, 24), (40, 30)], 2)
            # URL bar
            pygame.draw.rect(surf, BLACK, (12, 38, 28, 8), border_radius=2)
            font = pygame.font.SysFont('monospace', 7)
            txt = font.render('http://evil.com', True, RED)
            surf.blit(txt, (14, 39))
        
        sprites[data['sprite_name']] = surf
    
    return sprites

def create_tile_sprites() -> Dict[int, pygame.Surface]:
    """Create tile sprites for floor and walls."""
    sprites = {}
    
    # Floor tile - subtle pattern
    floor = pygame.Surface((TILE_SIZE, TILE_SIZE))
    floor.fill(VERY_DARK_AMBER)
    for _ in range(8):
        x = random.randint(0, TILE_SIZE-1)
        y = random.randint(0, TILE_SIZE-1)
        floor.set_at((x, y), DARK_AMBER)
    # Grid lines
    pygame.draw.line(floor, DARK_AMBER, (0, TILE_SIZE-1), (TILE_SIZE-1, TILE_SIZE-1), 1)
    pygame.draw.line(floor, DARK_AMBER, (TILE_SIZE-1, 0), (TILE_SIZE-1, TILE_SIZE-1), 1)
    sprites[0] = floor
    
    # Wall tile - brick pattern
    wall = pygame.Surface((TILE_SIZE, TILE_SIZE))
    wall.fill(DARK_GRAY)
    for row in range(4):
        for col in range(4):
            x = col * 8 + (row % 2) * 4
            y = row * 8
            pygame.draw.rect(wall, GRAY, (x, y, 7, 7), 1)
    # Highlight top/left
    pygame.draw.line(wall, GRAY, (0, 0), (TILE_SIZE-1, 0), 1)
    pygame.draw.line(wall, GRAY, (0, 0), (0, TILE_SIZE-1), 1)
    sprites[1] = wall
    
    return sprites

def create_ui_elements() -> Dict[str, pygame.Surface]:
    """Create UI panel elements."""
    elements = {}
    
    # Dialogue box
    db = pygame.Surface((SCREEN_WIDTH - 80, 160), pygame.SRCALPHA)
    pygame.draw.rect(db, UI_BG, (0, 0, db.get_width(), db.get_height()), border_radius=8)
    pygame.draw.rect(db, UI_BORDER, (0, 0, db.get_width(), db.get_height()), 3, border_radius=8)
    pygame.draw.rect(db, MENU_SELECTED, (3, 3, db.get_width()-6, db.get_height()-6), 0, border_radius=6)
    elements['dialogue_box'] = db
    
    # Combat panel
    cp = pygame.Surface((SCREEN_WIDTH - 80, 280), pygame.SRCALPHA)
    pygame.draw.rect(cp, UI_BG, (0, 0, cp.get_width(), cp.get_height()), border_radius=8)
    pygame.draw.rect(cp, UI_BORDER, (0, 0, cp.get_width(), cp.get_height()), 3, border_radius=8)
    pygame.draw.rect(cp, MENU_SELECTED, (3, 3, cp.get_width()-6, cp.get_height()-6), 0, border_radius=6)
    elements['combat_panel'] = cp
    
    # HUD panel
    hp = pygame.Surface((220, 100), pygame.SRCALPHA)
    pygame.draw.rect(hp, (0, 0, 0, 200), (0, 0, hp.get_width(), hp.get_height()), border_radius=6)
    pygame.draw.rect(hp, UI_BORDER, (0, 0, hp.get_width(), hp.get_height()), 2, border_radius=6)
    elements['hud_panel'] = hp
    
    # Minimap
    mm = pygame.Surface((160, 160), pygame.SRCALPHA)
    pygame.draw.rect(mm, (0, 0, 0, 200), (0, 0, mm.get_width(), mm.get_height()), border_radius=6)
    pygame.draw.rect(mm, UI_BORDER, (0, 0, mm.get_width(), mm.get_height()), 2, border_radius=6)
    elements['minimap'] = mm
    
    return elements

# =============================================================================
# COLLISION SYSTEM
# =============================================================================

def check_collision(entity, world_map) -> bool:
    """Check if entity collides with any wall tile."""
    left_tile = int(entity.x // TILE_SIZE)
    right_tile = int((entity.x + entity.width - 1) // TILE_SIZE)
    top_tile = int(entity.y // TILE_SIZE)
    bottom_tile = int((entity.y + entity.height - 1) // TILE_SIZE)
    
    for ty in range(top_tile, bottom_tile + 1):
        for tx in range(left_tile, right_tile + 1):
            if 0 <= ty < MAP_HEIGHT and 0 <= tx < MAP_WIDTH:
                if world_map[ty][tx] == 1:
                    return True
    return False

def resolve_collision(entity, world_map):
    """Push entity out of walls."""
    # Try horizontal resolution
    old_x = entity.x
    entity.x = old_x
    if check_collision(entity, world_map):
        # Push left or right
        left_tile = int(entity.x // TILE_SIZE)
        right_tile = int((entity.x + entity.width - 1) // TILE_SIZE)
        top_tile = int(entity.y // TILE_SIZE)
        bottom_tile = int((entity.y + entity.height - 1) // TILE_SIZE)
        
        push_left = push_right = 0
        for ty in range(top_tile, bottom_tile + 1):
            for tx in range(left_tile, right_tile + 1):
                if 0 <= ty < MAP_HEIGHT and 0 <= tx < MAP_WIDTH and world_map[ty][tx] == 1:
                    wall_left = tx * TILE_SIZE
                    wall_right = wall_left + TILE_SIZE
                    push_left = max(push_left, wall_right - entity.x)
                    push_right = max(push_right, entity.x + entity.width - wall_left)
        
        if push_left < push_right:
            entity.x += push_left
        else:
            entity.x -= push_right
    
    # Try vertical resolution
    old_y = entity.y
    entity.y = old_y
    if check_collision(entity, world_map):
        left_tile = int(entity.x // TILE_SIZE)
        right_tile = int((entity.x + entity.width - 1) // TILE_SIZE)
        top_tile = int(entity.y // TILE_SIZE)
        bottom_tile = int((entity.y + entity.height - 1) // TILE_SIZE)
        
        push_up = push_down = 0
        for ty in range(top_tile, bottom_tile + 1):
            for tx in range(left_tile, right_tile + 1):
                if 0 <= ty < MAP_HEIGHT and 0 <= tx < MAP_WIDTH and world_map[ty][tx] == 1:
                    wall_top = ty * TILE_SIZE
                    wall_bottom = wall_top + TILE_SIZE
                    push_up = max(push_up, wall_bottom - entity.y)
                    push_down = max(push_down, entity.y + entity.height - wall_top)
        
        if push_up < push_down:
            entity.y += push_up
        else:
            entity.y -= push_down

def check_entity_collision(e1, e2) -> bool:
    """Check collision between two entities."""
    return (e1.x < e2.x + e2.width and
            e1.x + e1.width > e2.x and
            e1.y < e2.y + e2.height and
            e1.y + e1.height > e2.y)

def resolve_entity_collision(e1, e2):
    """Push e1 out of e2 (solid collision)."""
    overlap_x = min(e1.x + e1.width, e2.x + e2.width) - max(e1.x, e2.x)
    overlap_y = min(e1.y + e1.height, e2.y + e2.height) - max(e1.y, e2.y)
    
    if overlap_x < overlap_y:
        # Push horizontally
        if e1.x < e2.x:
            e1.x = e2.x - e1.width - 1
        else:
            e1.x = e2.x + e2.width + 1
    else:
        # Push vertically
        if e1.y < e2.y:
            e1.y = e2.y - e1.height - 1
        else:
            e1.y = e2.y + e2.height + 1

# =============================================================================
# ENTITY CREATION
# =============================================================================

def create_enemy(spawn_data: Dict, player_level: int) -> Enemy:
    """Create an enemy from spawn data, scaled to player level."""
    etype = spawn_data['type']
    data = ENEMY_TYPES[etype]
    level = max(1, player_level + random.randint(-1, 1))
    
    hp = int(data['baseHp'] * (ENEMY_HP_SCALING ** (level - 1)))
    atk = int(data['baseAtk'] * (ENEMY_ATK_SCALING ** (level - 1)))
    xp = int(data['xpReward'] * (1.2 ** (level - 1)))
    
    return Enemy(
        x=spawn_data['x'] * TILE_SIZE + 4,
        y=spawn_data['y'] * TILE_SIZE + 4,
        type=etype,
        name=data['name'],
        symbol=data['symbol'],
        sprite_name=data['sprite_name'],
        category=data['category'],
        desc=data['desc'],
        color=data['color'],
        glow=data['glow'],
        max_hp=hp,
        hp=hp,
        atk=atk,
        xp_reward=xp,
        level=level,
        patrol_timer=random.uniform(0, 5),
        patrol_dir=random.randint(0, 3),
    )

def create_all_enemies(player_level: int) -> List[Enemy]:
    return [create_enemy(s, player_level) for s in ENEMY_SPAWNS]

# =============================================================================
# QUESTION SYSTEM - No repeats per game
# =============================================================================

class QuestionTracker:
    """Tracks asked questions to prevent repeats."""
    def __init__(self):
        self.asked: Set[int] = set()
        self.by_category: Dict[str, List[int]] = {}
        for i, q in enumerate(ALL_QUESTIONS):
            cat = q['category']
            if cat not in self.by_category:
                self.by_category[cat] = []
            self.by_category[cat].append(i)
    
    def get_question(self, category: str) -> Optional[Dict]:
        """Get a random unasked question from category."""
        if category not in self.by_category:
            category = random.choice(list(self.by_category.keys()))
        
        available = [i for i in self.by_category[category] if i not in self.asked]
        if not available:
            # Reset if all asked in this category
            self.asked.difference_update(self.by_category[category])
            available = self.by_category[category]
        
        if not available:
            return None
        
        idx = random.choice(available)
        self.asked.add(idx)
        return ALL_QUESTIONS[idx]
    
    def reset(self):
        self.asked.clear()

question_tracker = QuestionTracker()

def get_question_for_enemy(enemy: Enemy) -> Dict:
    """Get a unique question for enemy's category."""
    return question_tracker.get_question(enemy.category)

# =============================================================================
# RENDERING
# =============================================================================

class Renderer:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AppSec RPG: Guardians of the Code")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_small = pygame.font.SysFont('monospace', 12, bold=True)
        self.font_medium = pygame.font.SysFont('monospace', 16, bold=True)
        self.font_large = pygame.font.SysFont('monospace', 24, bold=True)
        self.font_title = pygame.font.SysFont('monospace', 36, bold=True)
        self.font_hud = pygame.font.SysFont('monospace', 11, bold=True)
        
        # Sprites
        self.player_sprites = create_player_sprites()
        self.enemy_sprites = create_enemy_sprites()
        self.tile_sprites = create_tile_sprites()
        self.ui_elements = create_ui_elements()
        
        # Scanline overlay
        self.scanlines = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 2):
            pygame.draw.line(self.scanlines, (0, 0, 0, SCANLINE_ALPHA), (0, y), (SCREEN_WIDTH, y))
        
        # Vignette
        self.vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for r in range(max(SCREEN_WIDTH, SCREEN_HEIGHT) // 2, 0, -1):
            alpha = int(60 * (1 - r / (max(SCREEN_WIDTH, SCREEN_HEIGHT) // 2)))
            pygame.draw.circle(self.vignette, (0, 0, 0, alpha), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), r)
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        self.screen_shake = 0
        self.shake_intensity = 0
    
    def update_camera(self, player: Player):
        # Center camera on player
        target_x = player.x - SCREEN_WIDTH // 2
        target_y = player.y - SCREEN_HEIGHT // 2
        
        # Clamp to world bounds
        target_x = max(0, min(target_x, WORLD_WIDTH - SCREEN_WIDTH))
        target_y = max(0, min(target_y, WORLD_HEIGHT - SCREEN_HEIGHT))
        
        # Smooth follow
        self.camera_x += (target_x - self.camera_x) * 0.15
        self.camera_y += (target_y - self.camera_y) * 0.15
        
        # Screen shake
        if self.screen_shake > 0:
            self.camera_x += random.uniform(-self.shake_intensity, self.shake_intensity)
            self.camera_y += random.uniform(-self.shake_intensity, self.shake_intensity)
            self.screen_shake -= 1
    
    def shake(self, intensity: float, duration: int):
        self.shake_intensity = intensity
        self.screen_shake = duration
    
    def draw_world(self, player: Player, enemies: List[Enemy], particles: ParticleSystem):
        # Clear
        self.screen.fill(BLACK)
        
        # Draw visible tiles
        start_tx = max(0, int(self.camera_x // TILE_SIZE) - 1)
        end_tx = min(MAP_WIDTH, int((self.camera_x + SCREEN_WIDTH) // TILE_SIZE) + 1)
        start_ty = max(0, int(self.camera_y // TILE_SIZE) - 1)
        end_ty = min(MAP_HEIGHT, int((self.camera_y + SCREEN_HEIGHT) // TILE_SIZE) + 1)
        
        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                tile = WORLD_MAP[ty][tx]
                if tile in self.tile_sprites:
                    sx = tx * TILE_SIZE - int(self.camera_x)
                    sy = ty * TILE_SIZE - int(self.camera_y)
                    self.screen.blit(self.tile_sprites[tile], (sx, sy))
        
        # Draw enemies
        for enemy in enemies:
            if enemy.defeated:
                continue
            self.draw_enemy(enemy)
        
        # Draw player
        self.draw_player(player)
        
        # Draw particles
        particles.draw(self.screen, self.camera_x, self.camera_y)
        
        # Apply effects
        self.screen.blit(self.scanlines, (0, 0))
        self.screen.blit(self.vignette, (0, 0))
    
    def draw_player(self, player: Player):
        sx = int(player.x - self.camera_x)
        sy = int(player.y - self.camera_y)
        
        if player.damage_flash > 0:
            # Flash white
            flash_surf = self.player_sprites[player.facing][player.anim_frame].copy()
            flash_surf.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(flash_surf, (sx - 4, sy - 2))
        else:
            self.screen.blit(self.player_sprites[player.facing][player.anim_frame], (sx - 4, sy - 2))
        
        # Level indicator
        if player.level > 1:
            lv_text = self.font_small.render(f'Lv.{player.level}', True, YELLOW)
            self.screen.blit(lv_text, (sx - 10, sy - 20))
    
    def draw_enemy(self, enemy: Enemy):
        sx = int(enemy.x - self.camera_x)
        sy = int(enemy.y - self.camera_y)
        
        # Float animation
        float_y = math.sin(enemy.float_offset) * 2
        
        if enemy.defeated:
            # Fade out
            alpha = int(255 * (1 - enemy.defeat_timer / 1000))
            if alpha > 0:
                sprite = self.enemy_sprites[enemy.sprite_name].copy()
                sprite.set_alpha(alpha)
                self.screen.blit(sprite, (sx - 12, sy - 12 + float_y))
            return
        
        # Damage flash
        if enemy.damage_flash > 0:
            flash_surf = self.enemy_sprites[enemy.sprite_name].copy()
            flash_surf.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(flash_surf, (sx - 12, sy - 12 + float_y))
        else:
            self.screen.blit(self.enemy_sprites[enemy.sprite_name], (sx - 12, sy - 12 + float_y))
        
        # HP bar above enemy
        bar_w = 40
        bar_h = 4
        bar_x = sx - bar_w // 2
        bar_y = sy - 20 + float_y
        pygame.draw.rect(self.screen, DARK_RED, (bar_x, bar_y, bar_w, bar_h))
        hp_w = int(bar_w * enemy.hp / enemy.max_hp)
        pygame.draw.rect(self.screen, BRIGHT_RED, (bar_x, bar_y, hp_w, bar_h))
        pygame.draw.rect(self.screen, UI_BORDER, (bar_x, bar_y, bar_w, bar_h), 1)
        
        # Level
        lv_text = self.font_small.render(f'Lv{enemy.level}', True, YELLOW)
        self.screen.blit(lv_text, (sx - 8, sy - 30 + float_y))
        
        # Name when nearby
        dist = math.hypot(enemy.x - (self.camera_x + SCREEN_WIDTH//2), enemy.y - (self.camera_y + SCREEN_HEIGHT//2))
        if dist < 200:
            name_text = self.font_small.render(enemy.name, True, UI_TEXT)
            self.screen.blit(name_text, (sx - name_text.get_width()//2, sy - 40 + float_y))
    
    def draw_hud(self, player: Player, enemies: List[Enemy]):
        # Main HUD panel
        panel = self.ui_elements['hud_panel']
        self.screen.blit(panel, (10, 10))
        
        # HP bar
        hp_text = self.font_hud.render(f'HP: {player.hp}/{player.max_hp}', True, UI_TEXT_BRIGHT)
        self.screen.blit(hp_text, (20, 18))
        bar_w = 180
        bar_h = 10
        pygame.draw.rect(self.screen, DARK_RED, (20, 34, bar_w, bar_h))
        hp_w = int(bar_w * player.hp / player.max_hp)
        pygame.draw.rect(self.screen, BRIGHT_RED, (20, 34, hp_w, bar_h))
        pygame.draw.rect(self.screen, UI_BORDER, (20, 34, bar_w, bar_h), 1)
        
        # EXP bar
        exp_text = self.font_hud.render(f'EXP: {player.exp}/{player.exp_to_next}', True, UI_TEXT_BRIGHT)
        self.screen.blit(exp_text, (20, 50))
        exp_w = int(bar_w * player.exp / player.exp_to_next)
        pygame.draw.rect(self.screen, DARK_AMBER, (20, 66, bar_w, bar_h))
        pygame.draw.rect(self.screen, AMBER, (20, 66, exp_w, bar_h))
        pygame.draw.rect(self.screen, UI_BORDER, (20, 66, bar_w, bar_h), 1)
        
        # Level & Stats
        lv_text = self.font_hud.render(f'Level: {player.level}  ATK: {player.atk}  DEF: {player.def_}', True, UI_TEXT)
        self.screen.blit(lv_text, (20, 82))
        
        # Enemies defeated
        def_text = self.font_hud.render(f'Defeated: {player.enemies_defeated}/{len(enemies)}', True, CYAN)
        self.screen.blit(def_text, (20, 96))
    
    def draw_minimap(self, player: Player, enemies: List[Enemy]):
        mm = self.ui_elements['minimap']
        mm_x = SCREEN_WIDTH - 170
        mm_y = 10
        self.screen.blit(mm, (mm_x, mm_y))
        
        scale = mm.get_width() / WORLD_WIDTH
        
        # Draw map
        for ty in range(MAP_HEIGHT):
            for tx in range(MAP_WIDTH):
                if WORLD_MAP[ty][tx] == 1:
                    px = mm_x + int(tx * TILE_SIZE * scale)
                    py = mm_y + int(ty * TILE_SIZE * scale)
                    pw = max(1, int(TILE_SIZE * scale))
                    ph = max(1, int(TILE_SIZE * scale))
                    pygame.draw.rect(self.screen, DARK_GRAY, (px, py, pw, ph))
        
        # Draw enemies
        for enemy in enemies:
            if not enemy.defeated:
                ex = mm_x + int(enemy.x * scale)
                ey = mm_y + int(enemy.y * scale)
                pygame.draw.circle(self.screen, enemy.color, (ex, ey), 3)
        
        # Draw player
        px = mm_x + int(player.x * scale)
        py = mm_y + int(player.y * scale)
        pygame.draw.circle(self.screen, BRIGHT_AMBER, (px, py), 4)
        pygame.draw.circle(self.screen, AMBER, (px, py), 4, 1)
    
    def draw_dialogue(self, text: str, speaker: str = '', typing: bool = False, progress: float = 1.0):
        db = self.ui_elements['dialogue_box']
        db_x = 40
        db_y = SCREEN_HEIGHT - db.get_height() - 40
        self.screen.blit(db, (db_x, db_y))
        
        # Speaker name
        if speaker:
            name_text = self.font_medium.render(f'► {speaker}', True, BRIGHT_AMBER)
            self.screen.blit(name_text, (db_x + 20, db_y + 15))
        
        # Dialogue text with typewriter effect
        display_text = text[:int(len(text) * progress)] if typing else text
        lines = self.wrap_text(display_text, db.get_width() - 40, self.font_medium)
        for i, line in enumerate(lines):
            if i >= 5: break
            text_surf = self.font_medium.render(line, True, UI_TEXT_BRIGHT)
            self.screen.blit(text_surf, (db_x + 20, db_y + 50 + i * 24))
        
        # Continue prompt
        if not typing or progress >= 1.0:
            prompt = self.font_small.render('▼ PRESS SPACE/ENTER ▼', True, BRIGHT_AMBER)
            prompt_x = db_x + (db.get_width() - prompt.get_width()) // 2
            prompt_y = db_y + db.get_height() - 25
            # Blink
            if int(pygame.time.get_ticks() / 500) % 2 == 0:
                self.screen.blit(prompt, (prompt_x, prompt_y))
    
    def draw_combat(self, combat: CombatState, player: Player, renderer_font=None):
        if not combat.enemy:
            return
        
        cp = self.ui_elements['combat_panel']
        cp_x = 40
        cp_y = (SCREEN_HEIGHT - cp.get_height()) // 2
        self.screen.blit(cp, (cp_x, cp_y))
        
        # Enemy info
        enemy = combat.enemy
        name_text = self.font_large.render(f'{enemy.name}  Lv.{enemy.level}', True, enemy.glow)
        self.screen.blit(name_text, (cp_x + 20, cp_y + 20))
        
        cat_text = self.font_small.render(f'Category: {enemy.category}', True, CYAN)
        self.screen.blit(cat_text, (cp_x + 20, cp_y + 55))
        
        # Enemy HP bar
        bar_w = 300
        bar_h = 12
        pygame.draw.rect(self.screen, DARK_RED, (cp_x + 20, cp_y + 75, bar_w, bar_h))
        hp_w = int(bar_w * enemy.hp / enemy.max_hp)
        pygame.draw.rect(self.screen, BRIGHT_RED, (cp_x + 20, cp_y + 75, hp_w, bar_h))
        pygame.draw.rect(self.screen, UI_BORDER, (cp_x + 20, cp_y + 75, bar_w, bar_h), 2)
        hp_text = self.font_medium.render(f'{enemy.hp} / {enemy.max_hp}', True, WHITE)
        self.screen.blit(hp_text, (cp_x + 20 + bar_w + 10, cp_y + 72))
        
        # Timer
        timer_pct = combat.timer / combat.max_timer
        timer_w = int(300 * timer_pct)
        timer_color = BRIGHT_RED if timer_pct < 0.3 else (YELLOW if timer_pct < 0.6 else BRIGHT_AMBER)
        pygame.draw.rect(self.screen, timer_color, (cp_x + 20, cp_y + 95, timer_w, 6))
        pygame.draw.rect(self.screen, UI_BORDER, (cp_x + 20, cp_y + 95, 300, 6), 1)
        timer_text = self.font_small.render(f'{int(combat.timer)}s', True, timer_color)
        self.screen.blit(timer_text, (cp_x + 330, cp_y + 92))
        
        # Question
        if combat.question:
            q = combat.question
            q_text = f'Q: {q["question"]}'
            lines = self.wrap_text(q_text, cp.get_width() - 40, self.font_medium)
            for i, line in enumerate(lines[:3]):
                q_surf = self.font_medium.render(line, True, UI_TEXT_BRIGHT)
                self.screen.blit(q_surf, (cp_x + 20, cp_y + 115 + i * 22))
            
            # Choices
            for j, choice in enumerate(combat.choices):
                prefix = '► ' if j == combat.selected else '  '
                color = BRIGHT_AMBER if j == combat.selected else UI_TEXT
                choice_text = f'{prefix}{chr(65+j)}) {choice}'
                c_surf = self.font_medium.render(choice_text, True, color)
                # Highlight background
                if j == combat.selected:
                    pygame.draw.rect(self.screen, MENU_SELECTED, (cp_x + 15, cp_y + 185 + j * 26, cp.get_width() - 30, 24), border_radius=4)
                    pygame.draw.rect(self.screen, MENU_SELECTED_BORDER, (cp_x + 15, cp_y + 185 + j * 26, cp.get_width() - 30, 24), 2, border_radius=4)
                self.screen.blit(c_surf, (cp_x + 25, cp_y + 188 + j * 26))
        
        # Result message
        if combat.result:
            result_color = BRIGHT_AMBER if combat.result == 'correct' else BRIGHT_RED
            result_text = self.font_large.render(
                'CORRECT!' if combat.result == 'correct' else 'WRONG!', True, result_color)
            self.screen.blit(result_text, (cp_x + (cp.get_width() - result_text.get_width()) // 2, cp_y + cp.get_height() - 50))
        
        # Player stats
        p_hp_text = self.font_small.render(f'Your HP: {player.hp}/{player.max_hp}', True, UI_TEXT)
        self.screen.blit(p_hp_text, (cp_x + cp.get_width() - 180, cp_y + 20))
    
    def draw_title(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.scanlines, (0, 0))
        self.screen.blit(self.vignette, (0, 0))
        
        # Retro border frame
        frame_margin = 40
        pygame.draw.rect(self.screen, UI_BORDER, (frame_margin, frame_margin, SCREEN_WIDTH - 2*frame_margin, SCREEN_HEIGHT - 2*frame_margin), 3)
        pygame.draw.rect(self.screen, MENU_SELECTED_BORDER, (frame_margin + 3, frame_margin + 3, SCREEN_WIDTH - 2*frame_margin - 6, SCREEN_HEIGHT - 2*frame_margin - 6), 1)
        
        # Title with shadow effect
        title_text = self.font_title.render('APPSEC RPG', True, BRIGHT_AMBER)
        tx = (SCREEN_WIDTH - title_text.get_width()) // 2
        # Shadow
        shadow = self.font_title.render('APPSEC RPG', True, DARK_AMBER)
        self.screen.blit(shadow, (tx + 2, 122))
        self.screen.blit(title_text, (tx, 120))
        
        subtitle = self.font_large.render('Guardians of the Code', True, AMBER)
        sx = (SCREEN_WIDTH - subtitle.get_width()) // 2
        self.screen.blit(subtitle, (sx, 170))
        
        # Version
        ver = self.font_small.render('v2.0 - Extended AppSec Edition', True, DARK_AMBER)
        vx = (SCREEN_WIDTH - ver.get_width()) // 2
        self.screen.blit(ver, (vx, 210))
        
        # Retro decorative elements - corner brackets
        bracket_size = 20
        corners = [
            (frame_margin + 10, frame_margin + 10),
            (SCREEN_WIDTH - frame_margin - 10 - bracket_size, frame_margin + 10),
            (frame_margin + 10, SCREEN_HEIGHT - frame_margin - 10 - bracket_size),
            (SCREEN_WIDTH - frame_margin - 10 - bracket_size, SCREEN_HEIGHT - frame_margin - 10 - bracket_size),
        ]
        for cx, cy in corners:
            pygame.draw.line(self.screen, BRIGHT_AMBER, (cx, cy), (cx + bracket_size, cy), 2)
            pygame.draw.line(self.screen, BRIGHT_AMBER, (cx, cy), (cx, cy + bracket_size), 2)
            pygame.draw.line(self.screen, BRIGHT_AMBER, (cx + bracket_size, cy + bracket_size), (cx, cy + bracket_size), 2)
            pygame.draw.line(self.screen, BRIGHT_AMBER, (cx + bracket_size, cy + bracket_size), (cx + bracket_size, cy), 2)
        
        # Enemy showcase - small sprites with names
        showcase_y = 280
        showcase_x_start = SCREEN_WIDTH // 2 - 300
        enemy_showcase = [
            ('injection', 'Injection', RED),
            ('xss', 'XSS', BRIGHT_RED),
            ('crypto', 'Crypto', CYAN),
            ('access', 'Access', ORANGE),
            ('ssrf', 'SSRF', MAGENTA),
        ]
        for i, (sprite_name, label, color) in enumerate(enemy_showcase):
            x = showcase_x_start + i * 150
            if sprite_name in self.enemy_sprites:
                sprite = self.enemy_sprites[sprite_name]
                # Scale up for showcase
                scaled = pygame.transform.scale(sprite, (48, 48))
                self.screen.blit(scaled, (x, showcase_y))
                # Label
                l_text = self.font_small.render(label, True, color)
                lx = x + 24 - l_text.get_width() // 2
                self.screen.blit(l_text, (lx, showcase_y + 55))
        
        # Divider line
        pygame.draw.line(self.screen, VERY_DARK_AMBER, (frame_margin + 40, 380), (SCREEN_WIDTH - frame_margin - 40, 380), 1)
        
        # Start prompt with blinking
        start_text = self.font_medium.render('PRESS ENTER TO BEGIN', True, BRIGHT_AMBER)
        stx = (SCREEN_WIDTH - start_text.get_width()) // 2
        if int(pygame.time.get_ticks() / 500) % 2 == 0:
            # Blinking arrow
            arrow = self.font_medium.render('►', True, BRIGHT_AMBER)
            self.screen.blit(arrow, (stx - 30, 420))
            self.screen.blit(start_text, (stx, 420))
            arrow2 = self.font_medium.render('◄', True, BRIGHT_AMBER)
            self.screen.blit(arrow2, (stx + start_text.get_width() + 10, 420))
        
        # Controls hint in retro box
        box_y = 480
        box_h = 180
        box_w = 600
        box_x = (SCREEN_WIDTH - box_w) // 2
        pygame.draw.rect(self.screen, UI_BG, (box_x, box_y, box_w, box_h), border_radius=4)
        pygame.draw.rect(self.screen, UI_BORDER, (box_x, box_y, box_w, box_h), 2, border_radius=4)
        
        controls_title = self.font_medium.render('CONTROLS', True, BRIGHT_AMBER)
        ctx = box_x + (box_w - controls_title.get_width()) // 2
        self.screen.blit(controls_title, (ctx, box_y + 10))

        controls = [
            ('WASD / Arrows', 'Move'),
            ('SPACE / ENTER', 'Interact / Attack'),
            ('ESC', 'Pause Menu'),
            ('UP/DOWN Arrows', 'Select Answer'),
            ('1-4 Keys', 'Quick Answer'),
        ]
        key_x = box_x + 30
        desc_x = box_x + 220
        for i, (key, desc) in enumerate(controls):
            key_text = self.font_small.render(key, True, BRIGHT_AMBER)
            desc_text = self.font_small.render(desc, True, UI_TEXT)
            self.screen.blit(key_text, (key_x, box_y + 45 + i * 24))
            self.screen.blit(desc_text, (desc_x, box_y + 45 + i * 24))
        
        # Bottom credits
        credits = self.font_small.render('OWASP Top 10 + Supply Chain, API, Cloud, Crypto, Mobile, DevSecOps, Privacy', True, DARK_AMBER)
        cdx = (SCREEN_WIDTH - credits.get_width()) // 2
        self.screen.blit(credits, (cdx, 700))
    
    def draw_pause(self, selected: int, music_enabled: bool = True):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Pause box
        box_w = 400
        box_h = 350
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2
        
        pygame.draw.rect(self.screen, UI_BG, (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(self.screen, UI_BORDER, (box_x, box_y, box_w, box_h), 3, border_radius=8)
        pygame.draw.rect(self.screen, MENU_SELECTED, (box_x+3, box_y+3, box_w-6, box_h-6), 0, border_radius=6)
        
        # Title
        pause_text = self.font_large.render('PAUSED', True, BRIGHT_AMBER)
        px = box_x + (box_w - pause_text.get_width()) // 2
        self.screen.blit(pause_text, (px, box_y + 30))
        
        # Menu options
        music_text = 'MUSIC: ON' if music_enabled else 'MUSIC: OFF'
        options = ['RESUME', 'STATS', music_text, 'QUIT TO TITLE']
        for i, opt in enumerate(options):
            color = BRIGHT_AMBER if i == selected else UI_TEXT
            prefix = '► ' if i == selected else '  '
            opt_text = self.font_medium.render(f'{prefix}{opt}', True, color)
            ox = box_x + (box_w - opt_text.get_width()) // 2
            oy = box_y + 100 + i * 50
            
            if i == selected:
                pygame.draw.rect(self.screen, MENU_SELECTED, (ox - 10, oy - 2, opt_text.get_width() + 20, 30), border_radius=4)
                pygame.draw.rect(self.screen, MENU_SELECTED_BORDER, (ox - 10, oy - 2, opt_text.get_width() + 20, 30), 2, border_radius=4)
            
            self.screen.blit(opt_text, (ox, oy))
    
    def draw_victory(self, player: Player):
        self.screen.fill(BLACK)
        self.screen.blit(self.scanlines, (0, 0))
        self.screen.blit(self.vignette, (0, 0))
        
        vic_text = self.font_title.render('VICTORY!', True, BRIGHT_AMBER)
        vx = (SCREEN_WIDTH - vic_text.get_width()) // 2
        self.screen.blit(vic_text, (vx, 200))
        
        stats = [
            f'Level Reached: {player.level}',
            f'Enemies Defeated: {player.enemies_defeated}',
            f'Questions Answered: {player.questions_answered}',
            f'Accuracy: {player.accuracy["correct"]}/{player.accuracy["total"]}',
        ]
        for i, stat in enumerate(stats):
            s_text = self.font_medium.render(stat, True, UI_TEXT_BRIGHT)
            sx = (SCREEN_WIDTH - s_text.get_width()) // 2
            self.screen.blit(s_text, (sx, 300 + i * 40))
        
        cont = self.font_medium.render('PRESS ENTER TO PLAY AGAIN', True, BRIGHT_AMBER)
        cx = (SCREEN_WIDTH - cont.get_width()) // 2
        if int(pygame.time.get_ticks() / 500) % 2 == 0:
            self.screen.blit(cont, (cx, 500))
    
    def draw_game_over(self, player: Player):
        self.screen.fill(BLACK)
        self.screen.blit(self.scanlines, (0, 0))
        self.screen.blit(self.vignette, (0, 0))
        
        go_text = self.font_title.render('GAME OVER', True, BRIGHT_RED)
        gx = (SCREEN_WIDTH - go_text.get_width()) // 2
        self.screen.blit(go_text, (gx, 200))
        
        stats = [
            f'Level Reached: {player.level}',
            f'Enemies Defeated: {player.enemies_defeated}',
            f'Questions Answered: {player.questions_answered}',
        ]
        for i, stat in enumerate(stats):
            s_text = self.font_medium.render(stat, True, UI_TEXT)
            sx = (SCREEN_WIDTH - s_text.get_width()) // 2
            self.screen.blit(s_text, (sx, 300 + i * 40))
        
        cont = self.font_medium.render('PRESS ENTER TO TRY AGAIN', True, BRIGHT_RED)
        cx = (SCREEN_WIDTH - cont.get_width()) // 2
        if int(pygame.time.get_ticks() / 500) % 2 == 0:
            self.screen.blit(cont, (cx, 500))
    
    def draw_particle_text(self, particles: ParticleSystem):
        """Draw damage numbers and text particles."""
        for p in particles.particles:
            if p.type != 'text':
                continue
            alpha = int(255 * (p.life / p.max_life))
            if hasattr(p, 'damage_value'):
                text = str(p.damage_value)
                surf = self.font_medium.render(text, True, (*p.color[:3], alpha))
                px = int(p.x - self.camera_x - surf.get_width() // 2)
                py = int(p.y - self.camera_y)
                self.screen.blit(surf, (px, py))
    
    def wrap_text(self, text: str, max_width: int, font) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split(' ')
        lines = []
        current = []
        current_width = 0
        
        for word in words:
            word_surf = font.render(word + ' ', True, WHITE)
            word_width = word_surf.get_width()
            if current_width + word_width > max_width and current:
                lines.append(' '.join(current))
                current = [word]
                current_width = word_width
            else:
                current.append(word)
                current_width += word_width
        
        if current:
            lines.append(' '.join(current))
        
        return lines if lines else ['']

# =============================================================================
# GAME LOGIC
# =============================================================================

class Game:
    def __init__(self):
        self.renderer = Renderer()
        self.state = GameState.TITLE
        self.previous_state = GameState.TITLE
        
        # Entities
        self.player = None
        self.enemies: List[Enemy] = []
        self.particles = ParticleSystem()
        
        # Combat
        self.combat = CombatState()
        
        # Dialogue
        self.dialogue_text = ''
        self.dialogue_speaker = ''
        self.dialogue_typing = False
        self.dialogue_progress = 0.0
        self.dialogue_callback = None
        
        # Pause
        self.pause_selection = 0
        
        # Music
        self.music_enabled = True
        self.bg_music = None
        
        # Input
        self.keys_pressed = set()
        self.last_interact = pygame.time.get_ticks() - 500  # Allow immediate interaction
        
        # Stats
        self.session_stats = {'enemies': 0, 'questions': 0, 'correct': 0}
    
    def reset_game(self):
        """Initialize new game."""
        spawn_x, spawn_y = PLAYER_SPAWN
        self.player = Player(x=spawn_x * TILE_SIZE + 4, y=spawn_y * TILE_SIZE + 4)
        self.enemies = create_all_enemies(1)
        self.particles = ParticleSystem()
        self.combat = CombatState()
        question_tracker.reset()
        self.session_stats = {'enemies': 0, 'questions': 0, 'correct': 0}
        self.state = GameState.OVERWORLD
        self.last_interact = pygame.time.get_ticks() - 500  # Allow immediate interaction
        self.show_intro()
    
    def show_intro(self):
        self.dialogue_text = ("Welcome, Guardian. The realm of Code has been corrupted by "
                             "vulnerabilities manifest as monsters. Defeat them by answering "
                             "security questions correctly. Press SPACE to continue.")
        self.dialogue_speaker = 'SYSTEM'
        self.dialogue_typing = True
        self.dialogue_progress = 0.0
        self.state = GameState.DIALOGUE
        self.dialogue_callback = lambda: setattr(self, 'state', GameState.OVERWORLD)
        # Start background music
        if self.music_enabled and self.bg_music is None:
            self.bg_music = generate_background_music()
            self.bg_music.play(-1)  # Loop indefinitely
            self.bg_music.set_volume(0.3)
    
    def toggle_music(self):
        """Toggle background music on/off."""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            if self.bg_music is None:
                self.bg_music = generate_background_music()
            self.bg_music.play(-1)
            self.bg_music.set_volume(0.3)
        else:
            if self.bg_music:
                self.bg_music.stop()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                
                # Global keys
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.OVERWORLD:
                        self.previous_state = GameState.OVERWORLD
                        self.state = GameState.PAUSED
                        self.pause_selection = 0
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.OVERWORLD
                    elif self.state == GameState.COMBAT:
                        self.previous_state = GameState.COMBAT
                        self.state = GameState.PAUSED
                        self.pause_selection = 0
                
                # State-specific keys
                if self.state == GameState.TITLE:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset_game()
                
                elif self.state == GameState.DIALOGUE:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if self.dialogue_typing:
                            self.dialogue_progress = 1.0
                        else:
                            self.dialogue_typing = False
                            if self.dialogue_callback:
                                self.dialogue_callback()
                                self.dialogue_callback = None
                
                elif self.state == GameState.COMBAT:
                    if self.combat.waiting_for_answer:
                        if event.key == pygame.K_UP:
                            self.combat.selected = (self.combat.selected - 1) % len(self.combat.choices)
                        elif event.key == pygame.K_DOWN:
                            self.combat.selected = (self.combat.selected + 1) % len(self.combat.choices)
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.submit_answer()
                        elif event.key == pygame.K_1:
                            self.combat.selected = 0
                            self.submit_answer()
                        elif event.key == pygame.K_2:
                            self.combat.selected = 1
                            self.submit_answer()
                        elif event.key == pygame.K_3:
                            self.combat.selected = 2
                            self.submit_answer()
                        elif event.key == pygame.K_4:
                            self.combat.selected = 3
                            self.submit_answer()
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_UP:
                        self.pause_selection = (self.pause_selection - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        self.pause_selection = (self.pause_selection + 1) % 4
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.handle_pause_selection()
                
                elif self.state in (GameState.VICTORY, GameState.GAME_OVER):
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset_game()
            
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
        
        return True
    
    def handle_pause_selection(self):
        if self.pause_selection == 0:  # RESUME
            self.state = self.previous_state if self.previous_state != GameState.PAUSED else GameState.OVERWORLD
        elif self.pause_selection == 1:  # STATS
            self.show_stats()
        elif self.pause_selection == 2:  # MUSIC TOGGLE
            self.toggle_music()
        elif self.pause_selection == 3:  # QUIT
            self.state = GameState.TITLE
    
    def show_stats(self):
        p = self.player
        acc = p.accuracy
        acc_pct = (acc['correct'] / acc['total'] * 100) if acc['total'] > 0 else 0
        self.dialogue_text = (f'Level: {p.level} | HP: {p.hp}/{p.max_hp} | ATK: {p.atk} | DEF: {p.def_}\n'
                             f'EXP: {p.exp}/{p.exp_to_next} | Enemies: {p.enemies_defeated}\n'
                             f'Questions: {p.questions_answered} | Accuracy: {acc_pct:.0f}%')
        self.dialogue_speaker = 'STATS'
        self.dialogue_typing = False
        self.dialogue_progress = 1.0
        self.state = GameState.DIALOGUE
        self.dialogue_callback = lambda: setattr(self, 'state', GameState.PAUSED)
    
    def update(self, dt: float):
        if self.state == GameState.OVERWORLD:
            self.update_overworld(dt)
        elif self.state == GameState.COMBAT:
            self.update_combat(dt)
        elif self.state == GameState.DIALOGUE:
            self.update_dialogue(dt)
        
        # Update particles always
        self.particles.update(dt)
        
        # Update camera
        if self.player:
            self.renderer.update_camera(self.player)
    
    def update_overworld(self, dt: float):
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
        
        # Diagonal normalization
        if self.player.vx != 0 and self.player.vy != 0:
            self.player.vx *= 0.7071
            self.player.vy *= 0.7071
        
        # Apply movement with collision
        new_x = self.player.x + self.player.vx * dt / 1000
        new_y = self.player.y + self.player.vy * dt / 1000
        
        self.player.x = new_x
        if check_collision(self.player, WORLD_MAP):
            self.player.x = new_x - self.player.vx * dt / 1000
            resolve_collision(self.player, WORLD_MAP)
        
        self.player.y = new_y
        if check_collision(self.player, WORLD_MAP):
            self.player.y = new_y - self.player.vy * dt / 1000
            resolve_collision(self.player, WORLD_MAP)
        
        # Clamp to world bounds
        self.player.x = max(0, min(self.player.x, WORLD_WIDTH - self.player.width))
        self.player.y = max(0, min(self.player.y, WORLD_HEIGHT - self.player.height))
        
        # Animation
        if self.player.moving:
            self.player.anim_timer += dt
            if self.player.anim_timer > 200:
                self.player.anim_timer = 0
                self.player.anim_frame = (self.player.anim_frame + 1) % 2
        else:
            self.player.anim_frame = 0
            self.player.anim_timer = 0
        
        # Damage flash
        if self.player.damage_flash > 0:
            self.player.damage_flash -= dt
        
        if self.player.invulnerable > 0:
            self.player.invulnerable -= dt
        
        # Update enemies
        for enemy in self.enemies:
            if enemy.defeated:
                enemy.defeat_timer += dt
                if enemy.defeat_timer > 1000:
                    continue
                continue
            
            # Float animation
            enemy.float_offset += 0.05 * dt / 16
            
            # Patrol AI
            enemy.patrol_timer += dt
            if enemy.patrol_timer > 3000:
                enemy.patrol_timer = 0
                enemy.patrol_dir = random.randint(0, 3)
            
            # Simple patrol movement
            patrol_speed = 30
            old_x, old_y = enemy.x, enemy.y
            if enemy.patrol_dir == 0:
                enemy.y -= patrol_speed * dt / 1000
            elif enemy.patrol_dir == 1:
                enemy.y += patrol_speed * dt / 1000
            elif enemy.patrol_dir == 2:
                enemy.x -= patrol_speed * dt / 1000
            elif enemy.patrol_dir == 3:
                enemy.x += patrol_speed * dt / 1000
            
            # Check collision with walls
            if check_collision(enemy, WORLD_MAP):
                enemy.x, enemy.y = old_x, old_y
                enemy.patrol_timer = 3000  # Change direction soon
            
            # Check collision with other enemies
            for other in self.enemies:
                if other is not enemy and not other.defeated:
                    if check_entity_collision(enemy, other):
                        enemy.x, enemy.y = old_x, old_y
                        break
            
            # Check player proximity for alert
            dist = math.hypot(enemy.x - self.player.x, enemy.y - self.player.y)
            if dist < 150:
                enemy.alert = True
                enemy.chase_timer = 2000
            elif enemy.chase_timer > 0:
                enemy.chase_timer -= dt
                if enemy.chase_timer <= 0:
                    enemy.alert = False
            
            # Chase player if alerted
            if enemy.alert and enemy.chase_timer > 0:
                dx = self.player.x - enemy.x
                dy = self.player.y - enemy.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    chase_speed = 60
                    old_x, old_y = enemy.x, enemy.y
                    enemy.x += (dx / dist) * chase_speed * dt / 1000
                    enemy.y += (dy / dist) * chase_speed * dt / 1000
                    
                    if check_collision(enemy, WORLD_MAP):
                        enemy.x, enemy.y = old_x, old_y
            
            # Damage flash
            if enemy.damage_flash > 0:
                enemy.damage_flash -= dt
        
        # Check combat trigger (SPACE/ENTER near enemy)
        interact_pressed = pygame.K_SPACE in self.keys_pressed or pygame.K_RETURN in self.keys_pressed
        current_time = pygame.time.get_ticks()
        
        if interact_pressed and current_time - self.last_interact > 300:
            self.last_interact = current_time
            for enemy in self.enemies:
                if enemy.defeated:
                    continue
                dist = math.hypot(enemy.x - self.player.x, enemy.y - self.player.y)
                if dist < 80:  # Interaction range
                    self.start_combat(enemy)
                    break
    
    def start_combat(self, enemy: Enemy):
        self.combat = CombatState()
        self.combat.enemy = enemy
        self.combat.question = get_question_for_enemy(enemy)
        self.combat.choices, self.combat.correct_answer_idx = shuffle_choices(self.combat.question)
        self.combat.selected = 0
        self.combat.timer = 30.0
        self.combat.waiting_for_answer = True
        self.combat.turn = 'player'
        self.combat.question_asked = True
        self.state = GameState.COMBAT
        self.renderer.shake(3, 10)
        # Clear interaction keys to prevent immediate answer submission
        self.keys_pressed.discard(pygame.K_SPACE)
        self.keys_pressed.discard(pygame.K_RETURN)
    
    def submit_answer(self):
        if not self.combat.waiting_for_answer:
            return
        
        self.combat.waiting_for_answer = False
        self.combat.result_timer = 1500
        self.player.questions_answered += 1
        self.player.accuracy['total'] += 1
        self.session_stats['questions'] += 1
        
        q = self.combat.question
        correct = (self.combat.selected == self.combat.correct_answer_idx)
        
        if correct:
            self.combat.result = 'correct'
            self.player.accuracy['correct'] += 1
            self.session_stats['correct'] += 1
            
            # Damage to enemy
            base_damage = self.player.atk
            variance = random.uniform(0.8, 1.2)
            damage = int(base_damage * variance)
            crit = random.random() < 0.1
            if crit:
                damage = int(damage * 1.5)
            self.combat.damage_dealt = damage
            self.combat.enemy.hp = max(0, self.combat.enemy.hp - damage)
            self.combat.enemy.damage_flash = 200
            self.particles.add_damage_number(self.combat.enemy.x, self.combat.enemy.y - 20, damage, crit)
            self.renderer.shake(5, 15)
            
            if self.combat.enemy.hp <= 0:
                self.defeat_enemy(self.combat.enemy)
        
        else:
            self.combat.result = 'wrong'
            # Enemy counterattacks
            damage = max(1, self.combat.enemy.atk - self.player.def_ // 2)
            self.combat.damage_taken = damage
            self.player.hp = max(0, self.player.hp - damage)
            self.player.damage_flash = 200
            self.player.invulnerable = 500
            self.particles.add_damage_number(self.player.x, self.player.y - 20, damage)
            self.renderer.shake(8, 20)
            
            if self.player.hp <= 0:
                self.state = GameState.GAME_OVER
    
    def defeat_enemy(self, enemy: Enemy):
        enemy.defeated = True
        enemy.defeat_timer = 0
        self.player.enemies_defeated += 1
        self.session_stats['enemies'] += 1
        
        # EXP gain
        exp_gain = enemy.xp_reward
        self.player.exp += exp_gain
        self.particles.add_explosion(enemy.x, enemy.y, enemy.glow, 30)
        
        # Level up check
        while self.player.exp >= self.player.exp_to_next:
            self.player.exp -= self.player.exp_to_next
            self.player.level += 1
            self.player.max_hp += 20
            self.player.hp = self.player.max_hp
            self.player.atk += 3
            self.player.def_ += 2
            self.player.exp_to_next = int(self.player.exp_to_next * 1.5)
            self.particles.add_explosion(self.player.x, self.player.y, BRIGHT_AMBER, 20)
            self.renderer.shake(10, 30)
        
        # Check victory
        alive = [e for e in self.enemies if not e.defeated]
        if not alive:
            self.state = GameState.VICTORY
        else:
            # Show defeat message then return to overworld
            self.dialogue_text = f'{enemy.name} defeated! Gained {exp_gain} EXP.'
            self.dialogue_speaker = 'SYSTEM'
            self.dialogue_typing = True
            self.dialogue_progress = 0.0
            self.state = GameState.DIALOGUE
            self.dialogue_callback = lambda: setattr(self, 'state', GameState.OVERWORLD)
    
    def update_combat(self, dt: float):
        if self.combat.waiting_for_answer:
            self.combat.timer -= dt / 1000.0
            if self.combat.timer <= 0:
                # Time up = wrong answer
                self.combat.selected = -1  # Force wrong
                self.submit_answer()
        elif self.combat.result:
            self.combat.result_timer -= dt
            if self.combat.result_timer <= 0:
                if self.combat.enemy and self.combat.enemy.hp > 0:
                    # Enemy turn
                    self.combat.waiting_for_answer = True
                    self.combat.result = None
                    self.combat.timer = 30.0
                    self.combat.question = get_question_for_enemy(self.combat.enemy)
                    self.combat.choices, self.combat.correct_answer_idx = shuffle_choices(self.combat.question)
                    self.combat.selected = 0
                else:
                    self.state = GameState.OVERWORLD
    
    def update_dialogue(self, dt: float):
        if self.dialogue_typing:
            self.dialogue_progress += dt / 1500  # Typewriter speed
            if self.dialogue_progress >= 1.0:
                self.dialogue_progress = 1.0
                self.dialogue_typing = False
    
    def draw(self):
        if self.state == GameState.TITLE:
            self.renderer.draw_title()
        elif self.state == GameState.OVERWORLD:
            self.renderer.draw_world(self.player, self.enemies, self.particles)
            self.renderer.draw_hud(self.player, self.enemies)
            self.renderer.draw_minimap(self.player, self.enemies)
            self.renderer.draw_particle_text(self.particles)
        elif self.state == GameState.COMBAT:
            # Draw frozen overworld
            self.renderer.draw_world(self.player, self.enemies, self.particles)
            self.renderer.draw_hud(self.player, self.enemies)
            self.renderer.draw_minimap(self.player, self.enemies)
            self.renderer.draw_particle_text(self.particles)
            # Darken overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.renderer.screen.blit(overlay, (0, 0))
            # Combat UI
            self.renderer.draw_combat(self.combat, self.player)
        elif self.state == GameState.PAUSED:
            # Draw frozen overworld
            self.renderer.draw_world(self.player, self.enemies, self.particles)
            self.renderer.draw_hud(self.player, self.enemies)
            self.renderer.draw_minimap(self.player, self.enemies)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.renderer.screen.blit(overlay, (0, 0))
            self.renderer.draw_pause(self.pause_selection, self.music_enabled)
        elif self.state == GameState.DIALOGUE:
            self.renderer.draw_world(self.player, self.enemies, self.particles)
            self.renderer.draw_hud(self.player, self.enemies)
            self.renderer.draw_minimap(self.player, self.enemies)
            self.renderer.draw_particle_text(self.particles)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.renderer.screen.blit(overlay, (0, 0))
            self.renderer.draw_dialogue(self.dialogue_text, self.dialogue_speaker, 
                                       self.dialogue_typing, self.dialogue_progress)
        elif self.state == GameState.VICTORY:
            self.renderer.draw_victory(self.player)
        elif self.state == GameState.GAME_OVER:
            self.renderer.draw_game_over(self.player)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            dt = self.renderer.clock.tick(FPS)
            running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

# =============================================================================
# MAIN
# =============================================================================

def main():
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    game = Game()
    game.run()

if __name__ == '__main__':
    main()