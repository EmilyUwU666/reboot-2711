# Bounded live read cache

The latest 38.00 report decoded 1,824,187 names but rejected all 302,362 candidate object headers with `Read cache exceeds 256 MB.` Registry slot 1 already resolved to Object/Class. The former append-only 65,536-page cache exhausted its capacity while scanning the registry, before header validation completed. This was a reader resource failure, not evidence of a missing Object class.

Both live probes now use one bounded LRU page cache. Capacity remains 65,536 4-KiB pages (256 MiB of resident page payload, plus collection overhead). On a miss at capacity, the oldest page is evicted before the new page is read. Partial or failed reads are never cached. Retries clear all pages. Reports include cumulative hits, misses, evictions, clears and peak resident pages even when verification fails.

Synthetic checks exercise continued scans beyond capacity, LRU retention, fresh reads after eviction and retry, cross-page reads, short reads, propagated timeouts and invalid bounds. The Windows workflow runs these alongside existing SDK, reflection, capture and native diagnostic checks.

Live memory remains non-atomic. Evicted pages can change before rereading; existing boundary retries and all identity/function/dispatch gates remain in place. This change does not establish 38.00 gameplay support. A new live dispatch JSON is required to verify the next stage on the actual game.
