<script setup lang="ts">
import type {
  ApprovalDecision,
  ChatMessage,
  ChatResponse,
  CommandApprovalResponse,
  CommandExecutionResponse,
  CommandProposal,
} from '../../types/chat'
import type { HealthResponse } from '../../types/health'

const config = useRuntimeConfig()
const sessionId = 'local-session'
const nextMessageId = ref(3)
const draftMessage = ref('')
const errorMessage = ref<string | null>(null)
const isSending = ref(false)
const health = ref<HealthResponse | null>(null)
const pendingApprovalIds = ref<string[]>([])
const pendingExecutionIds = ref<string[]>([])

const messages = ref<ChatMessage[]>([
  {
    id: 1,
    role: 'assistant',
    content: 'Ready for a terminal task. I will propose safe read-only commands in this phase.',
  },
  {
    id: 2,
    role: 'user',
    content: 'Can you help me inspect this project?',
  },
])

onMounted(async () => {
  try {
    health.value = await $fetch<HealthResponse>('/health', {
      baseURL: config.public.apiBaseUrl,
    })
  } catch {
    health.value = null
  }
})

async function sendMessage() {
  const content = draftMessage.value.trim()

  if (!content || isSending.value) {
    return
  }

  errorMessage.value = null
  messages.value.push({
    id: nextMessageId.value,
    role: 'user',
    content,
  })
  nextMessageId.value += 1
  draftMessage.value = ''
  isSending.value = true

  try {
    const response = await $fetch<ChatResponse>('/chat', {
      baseURL: config.public.apiBaseUrl,
      method: 'POST',
      body: {
        session_id: sessionId,
        message: content,
      },
    })

    messages.value.push({
      id: nextMessageId.value,
      role: 'assistant',
      content: response.message,
      commands: response.commands,
    })
    nextMessageId.value += 1
  } catch {
    errorMessage.value = 'Unable to send chat message to the backend.'
  } finally {
    isSending.value = false
  }
}

async function submitApproval(
  command: CommandProposal,
  decision: ApprovalDecision,
) {
  if (command.status !== 'proposed' || pendingApprovalIds.value.includes(command.id)) {
    return
  }

  errorMessage.value = null
  pendingApprovalIds.value = [...pendingApprovalIds.value, command.id]

  try {
    const response = await $fetch<CommandApprovalResponse>(
      `/commands/${command.id}/approval`,
      {
        baseURL: config.public.apiBaseUrl,
        method: 'POST',
        body: { decision },
      },
    )

    command.status = response.status
  } catch {
    errorMessage.value = 'Unable to record command approval decision.'
  } finally {
    pendingApprovalIds.value = pendingApprovalIds.value.filter(
      (commandId) => commandId !== command.id,
    )
  }
}

function isApprovalPending(commandId: string) {
  return pendingApprovalIds.value.includes(commandId)
}

async function executeCommand(command: CommandProposal) {
  if (command.status !== 'approved' || pendingExecutionIds.value.includes(command.id)) {
    return
  }

  errorMessage.value = null
  pendingExecutionIds.value = [...pendingExecutionIds.value, command.id]

  try {
    const response = await $fetch<CommandExecutionResponse>(
      `/commands/${command.id}/execute`,
      {
        baseURL: config.public.apiBaseUrl,
        method: 'POST',
      },
    )

    command.execution = response
  } catch {
    errorMessage.value = 'Unable to execute approved command in the sandbox.'
  } finally {
    pendingExecutionIds.value = pendingExecutionIds.value.filter(
      (commandId) => commandId !== command.id,
    )
  }
}

function isExecutionPending(commandId: string) {
  return pendingExecutionIds.value.includes(commandId)
}
</script>

<template>
  <main class="app-shell">
    <aside class="session-sidebar" aria-label="Sessions">
      <div>
        <p class="eyebrow">Terminal Agent</p>
        <h1>Control Panel</h1>
      </div>

      <button class="new-session-button" type="button">New Session</button>

      <nav class="session-list" aria-label="Session list">
        <button class="session-item active" type="button">
          <span class="session-name">Local Session</span>
          <span class="session-meta">{{ sessionId }}</span>
        </button>
      </nav>

      <div class="health-row">
        <span class="status-dot" :class="{ online: health?.status === 'ok' }" />
        <span>{{ health?.service ?? 'API disconnected' }}</span>
      </div>
    </aside>

    <section class="chat-panel" aria-labelledby="chat-title">
      <header class="chat-header">
        <div>
          <p class="eyebrow">Phase 6</p>
          <h2 id="chat-title">Docker Execution</h2>
        </div>
        <span class="status-pill">Sandbox required</span>
      </header>

      <div class="message-list" aria-live="polite">
        <article
          v-for="message in messages"
          :key="message.id"
          class="message"
          :class="message.role"
        >
          <span class="message-role">{{ message.role }}</span>
          <p>{{ message.content }}</p>

          <div v-if="message.commands?.length" class="command-list">
            <article
              v-for="command in message.commands"
              :key="command.id"
              class="command-card"
            >
              <div class="command-card-header">
                <span class="command-label">Command proposal</span>
                <span class="risk-badge" :class="command.risk">
                  {{ command.risk }} risk
                </span>
              </div>

              <code>{{ command.cmd }}</code>
              <p>{{ command.explanation }}</p>

              <div class="approval-row">
                <span class="approval-status" :class="command.status">
                  {{ command.status }}
                </span>

                <div class="approval-actions">
                  <button
                    class="approve-button"
                    type="button"
                    :disabled="command.status !== 'proposed' || isApprovalPending(command.id)"
                    @click="submitApproval(command, 'approved')"
                  >
                    Approve
                  </button>
                  <button
                    class="reject-button"
                    type="button"
                    :disabled="command.status !== 'proposed' || isApprovalPending(command.id)"
                    @click="submitApproval(command, 'rejected')"
                  >
                    Reject
                  </button>
                  <button
                    class="execute-button"
                    type="button"
                    :disabled="command.status !== 'approved' || isExecutionPending(command.id)"
                    @click="executeCommand(command)"
                  >
                    Execute
                  </button>
                </div>
              </div>

              <section v-if="command.execution" class="execution-panel">
                <div class="execution-header">
                  <span class="command-label">Execution output</span>
                  <span class="execution-status" :class="command.execution.status">
                    {{ command.execution.status }} · exit {{ command.execution.exit_code }}
                  </span>
                </div>
                <pre>{{ command.execution.output || '(no output)' }}</pre>
              </section>
            </article>
          </div>
        </article>

        <article v-if="isSending" class="message assistant">
          <span class="message-role">assistant</span>
          <p>Preparing command proposal...</p>
        </article>
      </div>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <form class="composer" @submit.prevent="sendMessage">
        <label class="sr-only" for="chat-message">Message</label>
        <textarea
          id="chat-message"
          v-model="draftMessage"
          rows="3"
          placeholder="Ask for a terminal task..."
        />
        <button type="submit" :disabled="isSending || !draftMessage.trim()">
          Send
        </button>
      </form>
    </section>
  </main>
</template>

<style>
:root {
  color: #f8fafc;
  background: #09090b;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
}

body {
  margin: 0;
  min-width: 320px;
  background: #09090b;
}

button,
textarea {
  font: inherit;
}

button {
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.app-shell {
  display: grid;
  min-height: 100vh;
  grid-template-columns: minmax(15rem, 18rem) minmax(0, 1fr);
  background:
    linear-gradient(135deg, rgba(14, 165, 233, 0.08), transparent 28rem),
    #09090b;
}

.session-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  border-right: 1px solid #27272a;
  background: #111113;
  padding: 1.25rem;
}

.eyebrow {
  margin: 0 0 0.45rem;
  color: #38bdf8;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

h1,
h2 {
  margin: 0;
  line-height: 1.1;
  letter-spacing: 0;
}

h1 {
  font-size: 1.55rem;
}

h2 {
  font-size: 1.45rem;
}

.new-session-button,
.session-item,
.composer button,
.approval-actions button {
  border: 1px solid #2563eb;
  border-radius: 8px;
  background: #2563eb;
  color: #eff6ff;
  font-weight: 700;
}

.new-session-button {
  min-height: 2.5rem;
}

.session-list {
  display: grid;
  gap: 0.75rem;
}

.session-item {
  display: grid;
  gap: 0.25rem;
  border-color: #3f3f46;
  background: #18181b;
  padding: 0.9rem;
  text-align: left;
}

.session-item.active {
  border-color: #38bdf8;
}

.session-name {
  color: #f8fafc;
  font-weight: 700;
}

.session-meta {
  color: #a1a1aa;
  font-size: 0.8rem;
}

.health-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-top: auto;
  color: #a1a1aa;
  font-size: 0.85rem;
}

.status-dot {
  width: 0.7rem;
  height: 0.7rem;
  flex: 0 0 auto;
  border-radius: 999px;
  background: #f59e0b;
}

.status-dot.online {
  background: #22c55e;
}

.chat-panel {
  display: grid;
  min-height: 100vh;
  grid-template-rows: auto minmax(0, 1fr) auto auto;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border-bottom: 1px solid #27272a;
  padding: 1.25rem 1.5rem;
}

.status-pill {
  border: 1px solid #14532d;
  border-radius: 999px;
  background: #052e16;
  color: #86efac;
  padding: 0.35rem 0.7rem;
  font-size: 0.8rem;
  font-weight: 700;
}

.message-list {
  display: flex;
  min-height: 0;
  flex-direction: column;
  gap: 0.9rem;
  overflow-y: auto;
  padding: 1.5rem;
}

.message {
  max-width: min(42rem, 88%);
  border: 1px solid #27272a;
  border-radius: 8px;
  background: #18181b;
  padding: 0.9rem 1rem;
}

.message.user {
  align-self: flex-end;
  border-color: #1d4ed8;
  background: #172554;
}

.message.assistant {
  align-self: flex-start;
  border-color: #166534;
  background: #052e16;
}

.message-role {
  display: block;
  margin-bottom: 0.45rem;
  color: #d4d4d8;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}

.message p {
  margin: 0;
  color: #f4f4f5;
  line-height: 1.55;
}

.command-list {
  display: grid;
  gap: 0.75rem;
  margin-top: 0.9rem;
}

.command-card {
  display: grid;
  gap: 0.7rem;
  border: 1px solid #3f3f46;
  border-radius: 8px;
  background: #111113;
  padding: 0.85rem;
}

.command-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.command-label {
  color: #d4d4d8;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}

.command-card code {
  overflow-x: auto;
  border: 1px solid #27272a;
  border-radius: 6px;
  background: #09090b;
  color: #f8fafc;
  padding: 0.75rem;
  white-space: pre;
}

.command-card p {
  color: #d4d4d8;
  font-size: 0.9rem;
}

.risk-badge {
  border: 1px solid #365314;
  border-radius: 999px;
  background: #1a2e05;
  color: #bef264;
  padding: 0.25rem 0.55rem;
  font-size: 0.75rem;
  font-weight: 700;
  white-space: nowrap;
}

.risk-badge.medium {
  border-color: #92400e;
  background: #451a03;
  color: #fcd34d;
}

.risk-badge.high {
  border-color: #991b1b;
  background: #450a0a;
  color: #fca5a5;
}

.approval-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.approval-status {
  border: 1px solid #3f3f46;
  border-radius: 999px;
  background: #18181b;
  color: #d4d4d8;
  padding: 0.25rem 0.55rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.approval-status.approved {
  border-color: #14532d;
  background: #052e16;
  color: #86efac;
}

.approval-status.rejected {
  border-color: #991b1b;
  background: #450a0a;
  color: #fca5a5;
}

.approval-actions {
  display: flex;
  gap: 0.5rem;
}

.approval-actions button {
  min-height: 2.1rem;
  padding: 0 0.75rem;
  font-size: 0.85rem;
}

.approval-actions .approve-button {
  border-color: #16a34a;
  background: #15803d;
}

.approval-actions .reject-button {
  border-color: #b91c1c;
  background: #991b1b;
}

.approval-actions .execute-button {
  border-color: #0891b2;
  background: #0e7490;
}

.execution-panel {
  display: grid;
  gap: 0.65rem;
  border-top: 1px solid #27272a;
  padding-top: 0.8rem;
}

.execution-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.execution-status {
  border: 1px solid #14532d;
  border-radius: 999px;
  background: #052e16;
  color: #86efac;
  padding: 0.25rem 0.55rem;
  font-size: 0.75rem;
  font-weight: 700;
  white-space: nowrap;
}

.execution-status.failed {
  border-color: #991b1b;
  background: #450a0a;
  color: #fca5a5;
}

.execution-panel pre {
  overflow-x: auto;
  margin: 0;
  border: 1px solid #27272a;
  border-radius: 6px;
  background: #09090b;
  color: #f4f4f5;
  padding: 0.75rem;
  white-space: pre-wrap;
}

.error-message {
  margin: 0 1.5rem 1rem;
  color: #fca5a5;
}

.composer {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.75rem;
  border-top: 1px solid #27272a;
  background: #111113;
  padding: 1rem 1.5rem;
}

.composer textarea {
  min-height: 4.5rem;
  resize: vertical;
  border: 1px solid #3f3f46;
  border-radius: 8px;
  background: #18181b;
  color: #f8fafc;
  padding: 0.85rem;
}

.composer textarea::placeholder {
  color: #71717a;
}

.composer button {
  align-self: end;
  min-height: 2.75rem;
  min-width: 5rem;
  padding: 0 1rem;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}

@media (max-width: 760px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .session-sidebar {
    border-right: 0;
    border-bottom: 1px solid #27272a;
  }

  .chat-panel {
    min-height: 72vh;
  }

  .chat-header,
  .composer {
    padding-inline: 1rem;
  }

  .message-list {
    padding: 1rem;
  }

  .message {
    max-width: 100%;
  }

  .composer {
    grid-template-columns: 1fr;
  }

  .composer button {
    width: 100%;
  }

  .approval-row {
    align-items: stretch;
    flex-direction: column;
  }

  .approval-actions {
    display: grid;
    grid-template-columns: 1fr;
  }
}
</style>
