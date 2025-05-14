# TankWar Game API Documentation

This document describes the API endpoints available for interacting with the TankWar game server.

## Base URL

All endpoints are served at `http://127.0.0.1:5000`

## Endpoints

### Game Status

#### GET `/status`
Returns the complete game state as JSON.

**Response:**
```json
{
    "status": string | null,
    "turn": number,
    "arena": {
        "cell_per_row": number,
        "cell_per_col": number
    },
    "tanks": [
        {
            "x": number,
            "y": number,
            "color": string,
            "orientation": number,
            "turret_orientation": number
        }
    ],
    "missiles": [
        {
            "x": number,
            "y": number,
            "color": string,
            "orientation": number
        }
    ]
}
```

### Turn Management

#### GET `/turn`
Returns the current game turn number.

**Response:** `string` (turn number)

### Action Management

#### POST `/action`
Submit an action for a tank.

**Request Body:**
```json
{
    "action": string,  // One of: "FORWARD", "BACKWARD", "TURN_LEFT", "TURN_RIGHT", "TURN_TURRET_LEFT", "TURN_TURRET_RIGHT", "FIRE", "SCAN"
    "turn": number,    // Current turn number
    "color": string    // Tank color ("black", "blue", "green", "orange", "purple", "red")
}
```

**Response:**
```json
{
    "action": string,
    "turn": number,
    "color": string
}
```

**Error Response (400):**
```json
{
    "error": "action, turn and color fields are required"
}
```

#### GET `/action/<color>`
Get the last action for a specific tank color.

**Response:**
```json
{
    "action": string,
    "color": string
}
```

### Scan Results

#### GET `/scan/<color>`
Get scan results for a specific tank color.

**Response:**
```json
{
    "scan": string,
    "color": string
}
```
Returns empty object `{}` if no scan results available.

### Game Control

#### POST `/game/pause`
Pause the game.

**Response:**
```json
{
    "status": "Game paused"
}
```

#### POST `/game/run`
Resume the game.

**Response:**
```json
{
    "status": "Game running"
}
```

#### POST `/game/reset`
Reset the game state.

**Response:**
```json
{
    "status": "Game reset"
}
```

## Notes

1. The game server runs on port 5000 and accepts connections from localhost (127.0.0.1)
2. Tank colors are limited to: "black", "blue", "green", "orange", "purple", "red"
3. Valid actions are: "FORWARD", "BACKWARD", "TURN_LEFT", "TURN_RIGHT", "TURN_TURRET_LEFT", "TURN_TURRET_RIGHT", "FIRE", "SCAN"
4. The game arena is a grid with dimensions defined in the game state (typically 50x50 cells)
5. Tank orientations and turret orientations are represented as numbers (likely 1-4 for cardinal directions)