# UI Context

## Visual Direction
Dark technical workspace. The UI should feel like a developer control panel, not a consumer chatbot.

## Layout

Desktop layout:

```txt
Left sidebar: sessions
Center panel: chat / agent interaction
Right or inline cards: command proposals, approval, execution output
```

Mobile layout may collapse sessions into drawer later.

## Components

- Session sidebar
- New session button
- Chat message list
- User message bubble
- Assistant message bubble
- Command proposal card
- Risk badge
- Approve command button
- Execution output panel
- Streaming status indicators

## Design Principles

1. Clarity over decoration.
2. Every command must be visible before approval.
3. Risk level must be visible.
4. Execution state must be visible.
5. Never hide automation.
6. Make unsafe/disabled states obvious.

## Initial Theme

- Background: near black
- Surface: dark gray
- Text: white / muted gray
- User accent: blue
- Assistant accent: green
- Warning: amber
- Error: red
- Success: green
