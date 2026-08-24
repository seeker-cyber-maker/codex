#ifndef DREAM_HOUSE_CANARY_PROTOCOL_H
#define DREAM_HOUSE_CANARY_PROTOCOL_H

#include <stddef.h>
#include <stdint.h>

#define DH_CANARY_PROTOCOL_VERSION 1u
#define DH_CANARY_HEADER_LENGTH 80u
#define DH_CANARY_HASH_LENGTH 32u
#define DH_CANARY_NONCE_LENGTH 32u
#define DH_CANARY_MAX_PAYLOAD_LENGTH 4096u

#define DH_CANARY_OFFSET_VERSION 0u
#define DH_CANARY_OFFSET_TYPE 1u
#define DH_CANARY_OFFSET_FLAGS 2u
#define DH_CANARY_OFFSET_PAYLOAD_LENGTH 4u
#define DH_CANARY_OFFSET_SEQUENCE 8u
#define DH_CANARY_OFFSET_OPERATION_HASH 16u
#define DH_CANARY_OFFSET_ATTEMPT_NONCE 48u

enum dh_canary_frame_type {
    DH_CANARY_FRAME_READY = 1,
    DH_CANARY_FRAME_CANARY_HELD = 2,
    DH_CANARY_FRAME_PREPARED_TO_RELEASE = 3,
    DH_CANARY_FRAME_RELEASE_ONCE = 4,
    DH_CANARY_FRAME_TERMINAL = 5,
};

struct dh_canary_header {
    uint8_t version;
    uint8_t type;
    uint16_t flags;
    uint32_t payload_length;
    uint64_t sequence;
    uint8_t operation_hash[DH_CANARY_HASH_LENGTH];
    uint8_t attempt_nonce[DH_CANARY_NONCE_LENGTH];
};

enum dh_canary_codec_result {
    DH_CANARY_CODEC_OK = 0,
    DH_CANARY_CODEC_INVALID_ARGUMENT = -1,
    DH_CANARY_CODEC_INVALID_VERSION = -2,
    DH_CANARY_CODEC_INVALID_TYPE = -3,
    DH_CANARY_CODEC_INVALID_FLAGS = -4,
    DH_CANARY_CODEC_INVALID_LENGTH = -5,
    DH_CANARY_CODEC_INVALID_SEQUENCE = -6,
    DH_CANARY_CODEC_UNBOUND_OPERATION = -7,
    DH_CANARY_CODEC_UNBOUND_NONCE = -8,
};

int dh_canary_encode_header(
    uint8_t out[DH_CANARY_HEADER_LENGTH],
    const struct dh_canary_header *header
);

int dh_canary_decode_header(
    struct dh_canary_header *out,
    const uint8_t encoded[DH_CANARY_HEADER_LENGTH]
);

int dh_canary_transition_is_valid(uint8_t previous_type, uint8_t next_type);

#endif
