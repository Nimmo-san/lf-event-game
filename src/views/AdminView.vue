<script setup lang="ts">
import {
    onMounted,
    ref,
} from "vue";


const API_URL =
    import.meta.env.VITE_API_URL;


interface AdminEntry {
    id: string;
    email: string;
    player_name: string;
    company_name: string;
    score: number;
    lightning_collected: number;
    entered_at: string;
}


const authenticated =
    ref(false);

const adminKey =
    ref("");

const loginError =
    ref("");

const loading =
    ref(false);

const entries =
    ref<AdminEntry[]>([]);

const search =
    ref("");

const name =
    ref("");

const email =
    ref("");

const company =
    ref("");

async function loadEntries() {
    loading.value = true;

    const params =
        new URLSearchParams();

    if (search.value.trim()) {
        params.set(
            "search",
            search.value.trim(),
        );
    }

    if (name.value.trim()) {
        params.set(
            "name",
            name.value.trim(),
        );
    }

    if (email.value.trim()) {
        params.set(
            "email",
            email.value.trim(),
        );
    }

    if (company.value.trim()) {
        params.set(
            "company",
            company.value.trim(),
        );
    }

    try {
        const response =
            await fetch(
                `${API_URL}/admin/entries?${params}`,
                {
                    credentials:
                        "include",
                },
            );

        if (response.status === 401) {
            authenticated.value =
                false;

            return;
        }

        if (!response.ok) {
            throw new Error(
                "Unable to load entries.",
            );
        }

        entries.value =
            await response.json();

        authenticated.value =
            true;

    } finally {
        loading.value = false;
    }
}

async function login() {
    loginError.value = "";

    const response =
        await fetch(
            `${API_URL}/admin/login`,
            {
                method: "POST",

                credentials: "include",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify({
                    key: adminKey.value,
                }),
            },
        );

    if (!response.ok) {
        loginError.value =
            "Invalid admin key.";

        return;
    }

    authenticated.value = true;

    adminKey.value = "";

    await loadEntries();
}
</script>