import { registerSW } from "virtual:pwa-register";

export const updateSW = registerSW({
  immediate: true,

  onOfflineReady() {
    console.log("Lightning Flight is ready to play offline.");
  },

  onNeedRefresh() {
    console.log("A new version of Lightning Flight is available.");
  },

  onRegisteredSW(swUrl, registration) {
    console.log("Service worker registered:", swUrl);

    if (!registration) {
      return;
    }
  },

  onRegisterError(error) {
    console.error("Service worker registration failed:", error);
  },
});
