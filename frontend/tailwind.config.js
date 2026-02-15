/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Mockup specific colors
                background: "#18181b", // Very dark grey (zinc-950 approx)
                surface: "#27272a",    // Lighter grey for cards/sidebar (zinc-800 approx)
                primary: "#0ea5e9",    // Blue for Connect/Disconnect (sky-500)
                success: "#22c55e",    // Green for Connected (green-500)
                danger: "#ef4444",     // Red for Disconnected status box (red-500)
                "danger-btn": "#b91c1c", // Darker red for disconnect button potentially

                // Standard UI tokens
                border: "#3f3f46",     // zinc-700
                text: {
                    main: "#f4f4f5",   // zinc-100
                    muted: "#a1a1aa",  // zinc-400
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'], // Premium feel
            }
        },
    },
    plugins: [],
}
