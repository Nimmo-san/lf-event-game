import { createRouter, createWebHistory } from "vue-router";

import StartScreen from "../components/StartScreen.vue";
import GameView from "../views/GameView.vue";
import AdminDashboard from "../views/AdminDashboard.vue";
import AdminLayout from "../views/AdminLayout.vue";
import AdminExport from "../views/AdminExport.vue";
// import LeaderboardView from "../views/LeaderboardView.vue";

import { getPlayerSession } from "../services/playerSession";

const router = createRouter({
  history: createWebHistory(),

  routes: [
    {
      path: "/",
      name: "start",
      component: StartScreen,
    },
    {
      path: "/admin",
      component: AdminLayout,
      children: [
        {
          path: "",
          redirect: { name: "admin-dashboard" },
        },
        {
          path: "dashboard",
          name: "admin-dashboard",
          component: AdminDashboard,
        },
        {
          path: "export",
          name: "admin-export",
          component: AdminExport,
        },
      ],
    },

    {
      path: "/game",
      name: "game",
      component: GameView,

      meta: {
        requiresPlayer: true,
      },
    },
    {
      path: "/leaderboard",
      name: "leaderboard",
      component: () => import("../views/LeaderboardView.vue"),
    },
  ],
});

router.beforeEach((to) => {
  const playerSession = getPlayerSession();

  if (to.meta.requiresPlayer && !playerSession) {
    return {
      name: "start",
    };
  }

  if (to.name === "start" && playerSession) {
    return {
      name: "game",
    };
  }
});

export default router;
