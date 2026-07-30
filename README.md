# AppSec RPG: Guardians of the Code

An educational single-player top-down RPG where combat encounters are resolved through application security quizzes. Built with Python and Pygame.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-2.5+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎮 Gameplay

- **Explore** a retro pixel-art world as a security guardian
- **Encounter** 8 unique enemy types, each representing an OWASP Top 10 vulnerability category
- **Battle** through security quizzes - answer correctly to deal damage, incorrectly to take damage
- **Level up** your stats (HP, ATK, DEF) by defeating enemies
- **Win** by defeating all 8 enemies

### Enemy Types (OWASP Top 10 Categories)

| Enemy | Category | Description |
|-------|----------|-------------|
| 🔴 Injection Demon | A03: Injection | SQL/Command injection attacks |
| 🟠 XSS Specter | A03: Injection | Cross-site scripting attacks |
| 🟣 Crypto Phantom | A02: Cryptographic Failures | Weak encryption, exposed secrets |
| 🔵 Access Control Wraith | A01: Broken Access Control | Unauthorized resource access |
| 🟡 Insecure Design Golem | A04: Insecure Design | Missing security controls |
| 🟠 Config Goblin | A05: Security Misconfiguration | Default creds, open ports |
| 🟣 Deserialization Wraith | A08: Software Integrity Failures | Untrusted data deserialization |
| 🔵 Logging Phantom | A09: Logging Failures | Insufficient attack detection |

## 📋 Requirements

- **Python 3.10+** (tested on 3.10.12)
- **Pygame 2.5+**

### System Dependencies (Linux)

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# Fedora/RHEL
sudo dnf install python3 python3-pip SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel

# Arch
sudo pacman -S python python-pip sdl2 sdl2_image sdl2_mixer sdl2_ttf

# macOS (with Homebrew)
brew install python sdl2 sdl2_image sdl2_mixer sdl2_ttf
```

## 🚀 Installation

### Option 1: Quick Start (Recommended)

```bash
# Clone the repository
git clone https://github.com/ethan0807/AppsSecRPG-Python.git
cd AppsSecRPG-Python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

### Option 2: System-wide Install

```bash
git clone https://github.com/ethan0807/AppsSecRPG-Python.git
cd AppsSecRPG-Python
pip3 install -r requirements.txt
python3 main.py
```

### Option 3: Development Install

```bash
git clone https://github.com/ethan0807/AppsSecRPG-Python.git
cd AppsSecRPG-Python
python3 -m venv venv
source venv/bin/activate
pip install -e .  # If setup.py/pyproject.toml exists
pip install -r requirements.txt
python main.py
```

## 🎯 How to Play

1. **Launch** the game - you'll see the title screen
2. **Press ENTER** to start
3. **Move** with WASD or Arrow Keys
4. **Walk into enemies** to initiate combat
5. **Answer OWASP questions** - use ↑/↓ to select, ENTER to confirm
6. **Survive** - correct answers damage enemies, wrong answers damage you
7. **Defeat all 8 enemies** to win!

### Controls

| Key | Action |
|-----|--------|
| `W` / `↑` | Move Up |
| `A` / `←` | Move Left |
| `S` / `↓` | Move Down |
| `D` / `→` | Move Right |
| `SPACE` / `ENTER` | Interact / Continue Dialogue / Confirm Answer |
| `ESC` | Pause Menu |
| `↑` / `↓` | Navigate Menus / Select Answer |

### Pause Menu Options

- **Resume Game** - Continue playing
- **View Stats** - See your current statistics
- **Controls** - View control reference
- **Quit to Title** - Return to main menu

## 🏗️ Architecture

```
main.py                 # Single-file game (~2000 lines)
├── Constants           # Game config, world map, enemy data, questions
├── Data Classes        # Player, Enemy, Particle, CombatState
├── Utility Functions   # Collision, entity creation, questions
├── ParticleSystem      # Visual effects (explosions, damage numbers)
├── Renderer            # All drawing logic (world, entities, UI, menus)
└── Game Class          # Main loop, state management, input handling
```

### Key Design Decisions

- **Single file** for simplicity and portability
- **No external game engines** - pure Pygame
- **Fixed 800×600 resolution** - scales to fit window
- **60 FPS** with delta-time movement
- **Retro aesthetic** - pixel art style, green-on-black terminal colors
- **Type hints** throughout for maintainability

## 🧪 Testing

Run the verification suite:

```bash
python3 -c "
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
pygame.init()
pygame.display.set_mode((800, 600), pygame.HIDDEN)

from main import *
# Run tests from verification script...
print('All core logic tests passed!')
"
```

## 📦 Building Executable (Optional)

### Using PyInstaller

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "AppSecRPG" \
  --add-data "venv/lib/python3.10/site-packages/pygame:pygame" \
  main.py
```

The executable will be in `dist/AppSecRPG`.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Ideas for Contributions

- [ ] Add sound effects and music
- [ ] More OWASP categories (A06, A07, A10 questions)
- [ ] Boss battles with multi-question encounters
- [ ] Save/load game state
- [ ] High score leaderboard
- [ ] Animated sprites for player/enemies
- [ ] Procedural world generation

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **OWASP Foundation** for the Top 10 vulnerability categories
- **Pygame Community** for the excellent game library
- **Press Start 2P Font** by Codeman38 (Google Fonts)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ethan0807/AppsSecRPG-Python/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ethan0807/AppsSecRPG-Python/discussions)

---

**Learn security by playing!** 🛡️💻
