#pragma once
// Single-threaded host execution; this does not test AVR atomicity.
#define ATOMIC_RESTORESTATE 0
#define ATOMIC_BLOCK(kind) if (true)
