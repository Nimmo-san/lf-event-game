import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

import "./style.css";
import "./registerSW";
import { startSyncManager } from "./services/gameSync";
import { startLeaderboardSync } from "./services/leaderboardSync.ts";;

const app = createApp(App)

app.use(router)
app.mount("#app");

void startSyncManager(); // forces the app to sync after becoming online
void startLeaderboardSync();
