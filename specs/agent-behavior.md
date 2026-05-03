# Agent Behavior Specification

## Agent Role
The agent helps developers reason about terminal commands. It can explain commands, propose safe commands, and prepare execution plans. It cannot execute commands by itself.

## Required Output Schema

The agent must produce command plans matching:

```json
{
  "intent": "string",
  "command": "string",
  "risk": "low|medium|high",
  "explanation": "string"
}
```

## Rules

1. Return safe, read-only commands whenever possible.
2. If the task is ambiguous, return an empty command.
3. If the task is dangerous, return an empty command and risk `high`.
4. Never suggest destructive commands such as:
   - `rm -rf`
   - `mkfs`
   - `shutdown`
   - `reboot`
   - fork bombs
5. Do not execute commands.
6. Do not claim a command was executed unless execution service confirms it.
7. Always explain what the command does.
8. Always label risk.

## LangGraph Design

Initial full graph:

```txt
User Input
  ↓
Planner Node
  ↓
Safety Validator Node
  ↓
Command Generator Node
  ↓
Explanation Node
  ↓
Structured Output
```

Simplified first implementation may use one Claude planning node behind LangGraph, but the code should allow expansion into multiple nodes.

## Safety Override
Backend safety rules must override the LLM. If the LLM returns a dangerous command, backend must block or clear it.
