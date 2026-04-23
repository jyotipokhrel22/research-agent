document.addEventListener('alpine:init', () => {
    Alpine.data('historySidebar', () => ({
        open(item) {
            this.$store.app.useHistoryItem(item);
        },
    }));
});
