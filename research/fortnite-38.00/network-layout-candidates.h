#pragma once
// Offline storage candidates for exact CL47722112 only. Not a callable SDK.
// No ownership, constructor, destructor, allocator or function-call API is provided.
#include <cstddef>
#include <cstdint>
#include <type_traits>

namespace emilyfn::research38 {
struct ArrayStorage {
    std::uint64_t data_address;
    std::int32_t count;
    std::int32_t capacity;
};
using StringStorage = ArrayStorage;

// Field shapes and offsets are supported by construction/format/destruction
// instructions. Semantic string labels intentionally await further verification.
struct UrlStorageCandidate {
    StringStorage string00;
    StringStorage string10;
    std::int32_t port;
    std::int32_t validity_candidate;
    StringStorage string28;
    StringStorage string38;
    ArrayStorage options;
    StringStorage string58;
};
struct ActiveDriverEntryCandidate {
    std::uint64_t driver_address;
    std::uint64_t definition_address;
};

static_assert(std::is_standard_layout_v<UrlStorageCandidate>);
static_assert(sizeof(ArrayStorage) == 0x10);
static_assert(alignof(ArrayStorage) == 8);
static_assert(offsetof(ArrayStorage, count) == 8);
static_assert(offsetof(ArrayStorage, capacity) == 0xC);
static_assert(sizeof(UrlStorageCandidate) == 0x68);
static_assert(offsetof(UrlStorageCandidate, string10) == 0x10);
static_assert(offsetof(UrlStorageCandidate, port) == 0x20);
static_assert(offsetof(UrlStorageCandidate, validity_candidate) == 0x24);
static_assert(offsetof(UrlStorageCandidate, string28) == 0x28);
static_assert(offsetof(UrlStorageCandidate, string38) == 0x38);
static_assert(offsetof(UrlStorageCandidate, options) == 0x48);
static_assert(offsetof(UrlStorageCandidate, string58) == 0x58);
static_assert(sizeof(ActiveDriverEntryCandidate) == 0x10);
static_assert(offsetof(ActiveDriverEntryCandidate, definition_address) == 8);
} // namespace emilyfn::research38
