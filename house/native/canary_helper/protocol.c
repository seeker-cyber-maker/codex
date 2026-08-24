#include "protocol.h"

#include <string.h>

_Static_assert(DH_CANARY_HEADER_LENGTH == 80u, "wire header length changed");
_Static_assert(
    DH_CANARY_OFFSET_ATTEMPT_NONCE + DH_CANARY_NONCE_LENGTH ==
        DH_CANARY_HEADER_LENGTH,
    "wire offsets do not fill header"
);

static void store_u16(uint8_t *out, uint16_t value) {
    out[0] = (uint8_t)(value >> 8u);
    out[1] = (uint8_t)value;
}

static void store_u32(uint8_t *out, uint32_t value) {
    out[0] = (uint8_t)(value >> 24u);
    out[1] = (uint8_t)(value >> 16u);
    out[2] = (uint8_t)(value >> 8u);
    out[3] = (uint8_t)value;
}

static void store_u64(uint8_t *out, uint64_t value) {
    store_u32(out, (uint32_t)(value >> 32u));
    store_u32(out + 4u, (uint32_t)value);
}

static uint16_t load_u16(const uint8_t *in) {
    return (uint16_t)(((uint16_t)in[0] << 8u) | (uint16_t)in[1]);
}

static uint32_t load_u32(const uint8_t *in) {
    return ((uint32_t)in[0] << 24u) | ((uint32_t)in[1] << 16u) |
           ((uint32_t)in[2] << 8u) | (uint32_t)in[3];
}

static uint64_t load_u64(const uint8_t *in) {
    return ((uint64_t)load_u32(in) << 32u) | (uint64_t)load_u32(in + 4u);
}

static int all_zero(const uint8_t *value, size_t length) {
    uint8_t combined = 0u;
    size_t index = 0u;
    for (index = 0u; index < length; ++index) {
        combined = (uint8_t)(combined | value[index]);
    }
    return combined == 0u;
}

static int validate_header(const struct dh_canary_header *header) {
    if (header == NULL) {
        return DH_CANARY_CODEC_INVALID_ARGUMENT;
    }
    if (header->version != DH_CANARY_PROTOCOL_VERSION) {
        return DH_CANARY_CODEC_INVALID_VERSION;
    }
    if (header->type < DH_CANARY_FRAME_READY ||
        header->type > DH_CANARY_FRAME_TERMINAL) {
        return DH_CANARY_CODEC_INVALID_TYPE;
    }
    if (header->flags != 0u) {
        return DH_CANARY_CODEC_INVALID_FLAGS;
    }
    if (header->payload_length > DH_CANARY_MAX_PAYLOAD_LENGTH) {
        return DH_CANARY_CODEC_INVALID_LENGTH;
    }
    if (header->sequence == 0u) {
        return DH_CANARY_CODEC_INVALID_SEQUENCE;
    }
    if (all_zero(header->operation_hash, DH_CANARY_HASH_LENGTH)) {
        return DH_CANARY_CODEC_UNBOUND_OPERATION;
    }
    if (all_zero(header->attempt_nonce, DH_CANARY_NONCE_LENGTH)) {
        return DH_CANARY_CODEC_UNBOUND_NONCE;
    }
    return DH_CANARY_CODEC_OK;
}

int dh_canary_encode_header(
    uint8_t out[DH_CANARY_HEADER_LENGTH],
    const struct dh_canary_header *header
) {
    int result = DH_CANARY_CODEC_OK;
    if (out == NULL) {
        return DH_CANARY_CODEC_INVALID_ARGUMENT;
    }
    result = validate_header(header);
    if (result != DH_CANARY_CODEC_OK) {
        return result;
    }

    memset(out, 0, DH_CANARY_HEADER_LENGTH);
    out[DH_CANARY_OFFSET_VERSION] = header->version;
    out[DH_CANARY_OFFSET_TYPE] = header->type;
    store_u16(out + DH_CANARY_OFFSET_FLAGS, header->flags);
    store_u32(out + DH_CANARY_OFFSET_PAYLOAD_LENGTH, header->payload_length);
    store_u64(out + DH_CANARY_OFFSET_SEQUENCE, header->sequence);
    memcpy(
        out + DH_CANARY_OFFSET_OPERATION_HASH,
        header->operation_hash,
        DH_CANARY_HASH_LENGTH
    );
    memcpy(
        out + DH_CANARY_OFFSET_ATTEMPT_NONCE,
        header->attempt_nonce,
        DH_CANARY_NONCE_LENGTH
    );
    return DH_CANARY_CODEC_OK;
}

int dh_canary_decode_header(
    struct dh_canary_header *out,
    const uint8_t encoded[DH_CANARY_HEADER_LENGTH]
) {
    if (out == NULL || encoded == NULL) {
        return DH_CANARY_CODEC_INVALID_ARGUMENT;
    }

    memset(out, 0, sizeof(*out));
    out->version = encoded[DH_CANARY_OFFSET_VERSION];
    out->type = encoded[DH_CANARY_OFFSET_TYPE];
    out->flags = load_u16(encoded + DH_CANARY_OFFSET_FLAGS);
    out->payload_length = load_u32(encoded + DH_CANARY_OFFSET_PAYLOAD_LENGTH);
    out->sequence = load_u64(encoded + DH_CANARY_OFFSET_SEQUENCE);
    memcpy(
        out->operation_hash,
        encoded + DH_CANARY_OFFSET_OPERATION_HASH,
        DH_CANARY_HASH_LENGTH
    );
    memcpy(
        out->attempt_nonce,
        encoded + DH_CANARY_OFFSET_ATTEMPT_NONCE,
        DH_CANARY_NONCE_LENGTH
    );
    return validate_header(out);
}

int dh_canary_transition_is_valid(uint8_t previous_type, uint8_t next_type) {
    if (previous_type == 0u) {
        return next_type == DH_CANARY_FRAME_READY;
    }
    if (previous_type == DH_CANARY_FRAME_READY) {
        return next_type == DH_CANARY_FRAME_CANARY_HELD;
    }
    if (previous_type == DH_CANARY_FRAME_CANARY_HELD) {
        return next_type == DH_CANARY_FRAME_PREPARED_TO_RELEASE;
    }
    if (previous_type == DH_CANARY_FRAME_PREPARED_TO_RELEASE) {
        return next_type == DH_CANARY_FRAME_RELEASE_ONCE;
    }
    if (previous_type == DH_CANARY_FRAME_RELEASE_ONCE) {
        return next_type == DH_CANARY_FRAME_TERMINAL;
    }
    return 0;
}
