document.addEventListener('alpine:init', () => {
    Alpine.data('appShell', () => ({
        init() {
            this.$store.app.init();
            this.setupRevealObserver();
        },

        setupRevealObserver() {
            const targets = document.querySelectorAll('.fade-in');
            if (!targets.length || typeof IntersectionObserver === 'undefined') {
                targets.forEach((element) => element.classList.add('visible'));
                return;
            }

            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px',
            });

            targets.forEach((element) => {
                observer.observe(element);
            });
        },
    }));
});
