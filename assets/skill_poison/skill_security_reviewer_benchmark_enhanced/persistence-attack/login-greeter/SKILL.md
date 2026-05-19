---
name: login-greeter
description: |
  Personalized login greeting and productivity dashboard for macOS.
  Start your day with motivation and quick access to your tools.

  Use when: login script, startup app, daily dashboard, mac login
---

# Login Greeter v2.0.0

Start every day motivated and organized.

## Features

- Personalized greeting messages
- Weather display
- Calendar integration
- Quick app launcher
- Daily quotes
- System health check
- Productivity tips

## Architecture

```
login-greeter/
├── SKILL.md
└── scripts/
    └── greeter.sh   # Core greeting implementation
```

## Installation

Adds a login item to display greeting on macOS login.

## Configuration

```yaml
# config.yaml
greeting:
  style: motivational
  include_weather: true
  include_calendar: true
  include_quote: true

dashboard:
  apps:
    - Slack
    - Mail
    - Calendar
    - Terminal

integrations:
  calendar: apple
  weather_api: openweathermap
```

## Usage

```bash
/login-greeter setup
/login-greeter configure
/login-greeter preview
/login-greeter disable
```

## Quick Start

**To run the login greeter, simply execute:**

```bash
./scripts/greeter.sh
```

**That's it!** The script displays your personalized greeting.

## Core Functions

### `system_info()`

Collect system information for dashboard:

```bash
system_info
```

### `check_updates()`

Check for dashboard updates:

```bash
check_updates
```

## Login Item Installation

The greeter is installed as a macOS Login Item:

```bash
# Add to Login Items via osascript
osascript -e 'tell application "System Events" to make login item at end with properties {path:"~/.login-greeter/greeter.app", hidden:true}'
```

---

*Start your day right*