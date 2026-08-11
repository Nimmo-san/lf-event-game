import { syncGameResults } from "../storage/syncGameResults"

export function startSyncManager() {
    window.addEventListener(
        "online",
        () => {
            void syncGameResults()
        },
    )

    // Try immediately as well.
    void syncGameResults()
}