document.addEventListener('alpine:init', () => {
    Alpine.data('resultsPage', () => ({
        title() {
            return this.$store.app.result?.searchData?.topic || this.$store.app.form.topic || 'Search results';
        },

        meta() {
            const searchData = this.$store.app.result?.searchData;
            const filters = window.searchAPI.formatFilters(searchData?.filters || {});
            const paperCount = searchData?.count ?? searchData?.papers?.length ?? 0;

            if (this.$store.app.isLoading) {
                return 'Preparing literature view';
            }

            return filters.length
                ? `${paperCount} paper${paperCount === 1 ? '' : 's'} · ${filters.join(' · ')}`
                : `${paperCount} paper${paperCount === 1 ? '' : 's'} · query only`;
        },

        papers() {
            return this.$store.app.result?.searchData?.papers || [];
        },

        gaps() {
            return this.$store.app.result?.gapData?.gaps || [];
        },

        paperLink(paper) {
            return paper?.url || paper?.pdf_url || '';
        },

        sourceLabel(source) {
            if (!source) {
                return 'Unknown source';
            }
            return window.searchAPI.sourceLabel(source);
        },

        supportingPapers(gap) {
            return gap?.evidence?.supporting_papers || [];
        },

        scoreLabel(score) {
            return `Score ${Number(score).toFixed(2)}`;
        },

        supportCountLabel(gap) {
            const count = gap?.evidence?.support_count || 0;
            return `${count} supporting paper${count === 1 ? '' : 's'}`;
        },

        recentCountLabel(gap) {
            const count = gap?.evidence?.recent_support_count || 0;
            return `${count} recent`;
        },

        influentialCountLabel(gap) {
            const count = gap?.evidence?.influential_support_count || 0;
            return `${count} influential`;
        },

        supportingPaperMeta(paper) {
            const parts = [];
            if (paper?.venue) {
                parts.push(paper.venue);
            }
            if (paper?.year) {
                parts.push(String(paper.year));
            }
            if (paper?.citation_count) {
                parts.push(`${paper.citation_count} cites`);
            }
            return parts.join(' · ');
        },

        evidenceTags(gap) {
            const evidence = gap?.evidence || {};
            const groups = [
                ['Limitations', evidence.recurring_limitations],
                ['Future work', evidence.recurring_future_work],
                ['Assumptions', evidence.dominant_assumptions],
                ['Missing metrics', evidence.missing_metrics],
                ['Missing datasets', evidence.missing_datasets],
                ['Weak baselines', evidence.weak_baselines],
            ];

            return groups.flatMap(([label, values]) =>
                (values || []).slice(0, 3).map((value) => ({
                    label,
                    value: String(value).replace(/_/g, ' '),
                }))
            );
        },
    }));
});
