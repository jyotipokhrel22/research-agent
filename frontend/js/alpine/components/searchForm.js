document.addEventListener('alpine:init', () => {
    Alpine.data('searchForm', () => ({
        async submit() {
            await this.$store.app.runSearch(this.$store.app.form);
        },
    }));
});
