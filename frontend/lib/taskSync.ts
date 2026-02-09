/**
 * Cross-tab task synchronization using BroadcastChannel API
 * When chatbot modifies tasks, the dashboard auto-refreshes
 */

const CHANNEL_NAME = "task-sync";

type TaskSyncEvent = {
  type: "task-created" | "task-deleted" | "task-toggled" | "task-updated" | "tasks-changed";
  timestamp: number;
};

let channel: BroadcastChannel | null = null;

function getChannel(): BroadcastChannel | null {
  if (typeof window === "undefined") return null;
  if (!channel) {
    try {
      channel = new BroadcastChannel(CHANNEL_NAME);
    } catch {
      return null;
    }
  }
  return channel;
}

/** Notify other tabs that tasks have changed */
export function notifyTaskChange(type: TaskSyncEvent["type"] = "tasks-changed") {
  const ch = getChannel();
  if (ch) {
    ch.postMessage({ type, timestamp: Date.now() } satisfies TaskSyncEvent);
  }
  // Also fire a storage event as fallback for same-tab listeners
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("tasks-changed"));
  }
}

/** Subscribe to task change notifications from other tabs */
export function onTaskChange(callback: () => void): () => void {
  const ch = getChannel();
  const handler = () => callback();

  if (ch) {
    ch.addEventListener("message", handler);
  }

  // Also listen for same-tab custom events
  if (typeof window !== "undefined") {
    window.addEventListener("tasks-changed", handler);
  }

  // Refresh when user switches back to this tab
  const focusHandler = () => callback();
  if (typeof window !== "undefined") {
    window.addEventListener("focus", focusHandler);
  }

  // Return cleanup function
  return () => {
    if (ch) {
      ch.removeEventListener("message", handler);
    }
    if (typeof window !== "undefined") {
      window.removeEventListener("tasks-changed", handler);
      window.removeEventListener("focus", focusHandler);
    }
  };
}
