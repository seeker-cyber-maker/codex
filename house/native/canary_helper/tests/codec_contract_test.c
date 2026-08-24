#include "protocol.h"

#include <stdint.h>
#include <string.h>

#define CHECK(condition)        \
    do {                        \
        if (!(condition)) {     \
            return __LINE__;    \
        }                       \
    } while (0)

static struct dh_canary_header valid_header(void) {
    struct dh_canary_header header;
    size_t index = 0u;
    memset(&header, 0, sizeof(header));
    header.version = DH_CANARY_PROTOCOL_VERSION;
    header.type = DH_CANARY_FRAME_READY;
    header.flags = 0u;
    header.payload_length = 0x00000a0bu;
    header.sequence = UINT64_C(0x0102030405060708);
    for (index = 0u; index < DH_CANARY_HASH_LENGTH; ++index) {
        header.operation_hash[index] = (uint8_t)(index + 1u);
    }
    for (index = 0u; index < DH_CANARY_NONCE_LENGTH; ++index) {
        header.attempt_nonce[index] = (uint8_t)(0x80u + index);
    }
    return header;
}

static int check_exact_wire_and_round_trip(void) {
    struct dh_canary_header header = valid_header();
    struct dh_canary_header decoded;
    uint8_t encoded[DH_CANARY_HEADER_LENGTH];
    size_t index = 0u;

    CHECK(dh_canary_encode_header(encoded, &header) == DH_CANARY_CODEC_OK);
    CHECK(encoded[DH_CANARY_OFFSET_VERSION] == DH_CANARY_PROTOCOL_VERSION);
    CHECK(encoded[DH_CANARY_OFFSET_TYPE] == DH_CANARY_FRAME_READY);
    CHECK(encoded[DH_CANARY_OFFSET_FLAGS] == 0u);
    CHECK(encoded[DH_CANARY_OFFSET_FLAGS + 1u] == 0u);
    CHECK(encoded[DH_CANARY_OFFSET_PAYLOAD_LENGTH] == 0x00u);
    CHECK(encoded[DH_CANARY_OFFSET_PAYLOAD_LENGTH + 1u] == 0x00u);
    CHECK(encoded[DH_CANARY_OFFSET_PAYLOAD_LENGTH + 2u] == 0x0au);
    CHECK(encoded[DH_CANARY_OFFSET_PAYLOAD_LENGTH + 3u] == 0x0bu);
    for (index = 0u; index < 8u; ++index) {
        CHECK(encoded[DH_CANARY_OFFSET_SEQUENCE + index] == (uint8_t)(index + 1u));
    }
    CHECK(
        memcmp(
            encoded + DH_CANARY_OFFSET_OPERATION_HASH,
            header.operation_hash,
            DH_CANARY_HASH_LENGTH
        ) == 0
    );
    CHECK(
        memcmp(
            encoded + DH_CANARY_OFFSET_ATTEMPT_NONCE,
            header.attempt_nonce,
            DH_CANARY_NONCE_LENGTH
        ) == 0
    );
    CHECK(dh_canary_decode_header(&decoded, encoded) == DH_CANARY_CODEC_OK);
    CHECK(decoded.version == header.version);
    CHECK(decoded.type == header.type);
    CHECK(decoded.flags == header.flags);
    CHECK(decoded.payload_length == header.payload_length);
    CHECK(decoded.sequence == header.sequence);
    CHECK(
        memcmp(decoded.operation_hash, header.operation_hash, DH_CANARY_HASH_LENGTH) ==
        0
    );
    CHECK(
        memcmp(decoded.attempt_nonce, header.attempt_nonce, DH_CANARY_NONCE_LENGTH) ==
        0
    );
    return 0;
}

static int check_encode_rejections(void) {
    struct dh_canary_header header = valid_header();
    uint8_t encoded[DH_CANARY_HEADER_LENGTH];

    CHECK(
        dh_canary_encode_header(NULL, &header) == DH_CANARY_CODEC_INVALID_ARGUMENT
    );
    CHECK(dh_canary_encode_header(encoded, NULL) == DH_CANARY_CODEC_INVALID_ARGUMENT);
    header.version = 0u;
    CHECK(dh_canary_encode_header(encoded, &header) == DH_CANARY_CODEC_INVALID_VERSION);
    header = valid_header();
    header.type = 0u;
    CHECK(dh_canary_encode_header(encoded, &header) == DH_CANARY_CODEC_INVALID_TYPE);
    header.type = (uint8_t)(DH_CANARY_FRAME_TERMINAL + 1u);
    CHECK(dh_canary_encode_header(encoded, &header) == DH_CANARY_CODEC_INVALID_TYPE);
    header = valid_header();
    header.flags = 1u;
    CHECK(dh_canary_encode_header(encoded, &header) == DH_CANARY_CODEC_INVALID_FLAGS);
    header = valid_header();
    header.payload_length = DH_CANARY_MAX_PAYLOAD_LENGTH + 1u;
    CHECK(dh_canary_encode_header(encoded, &header) == DH_CANARY_CODEC_INVALID_LENGTH);
    header = valid_header();
    header.sequence = 0u;
    CHECK(
        dh_canary_encode_header(encoded, &header) == DH_CANARY_CODEC_INVALID_SEQUENCE
    );
    header = valid_header();
    memset(header.operation_hash, 0, sizeof(header.operation_hash));
    CHECK(
        dh_canary_encode_header(encoded, &header) == DH_CANARY_CODEC_UNBOUND_OPERATION
    );
    header = valid_header();
    memset(header.attempt_nonce, 0, sizeof(header.attempt_nonce));
    CHECK(dh_canary_encode_header(encoded, &header) == DH_CANARY_CODEC_UNBOUND_NONCE);
    return 0;
}

static int check_decode_rejections(void) {
    struct dh_canary_header header = valid_header();
    struct dh_canary_header decoded;
    uint8_t baseline[DH_CANARY_HEADER_LENGTH];
    uint8_t encoded[DH_CANARY_HEADER_LENGTH];

    CHECK(dh_canary_encode_header(baseline, &header) == DH_CANARY_CODEC_OK);
    CHECK(dh_canary_decode_header(NULL, baseline) == DH_CANARY_CODEC_INVALID_ARGUMENT);
    CHECK(dh_canary_decode_header(&decoded, NULL) == DH_CANARY_CODEC_INVALID_ARGUMENT);

    memcpy(encoded, baseline, sizeof(encoded));
    encoded[DH_CANARY_OFFSET_VERSION] = 0u;
    CHECK(dh_canary_decode_header(&decoded, encoded) == DH_CANARY_CODEC_INVALID_VERSION);
    memcpy(encoded, baseline, sizeof(encoded));
    encoded[DH_CANARY_OFFSET_TYPE] = 0u;
    CHECK(dh_canary_decode_header(&decoded, encoded) == DH_CANARY_CODEC_INVALID_TYPE);
    memcpy(encoded, baseline, sizeof(encoded));
    encoded[DH_CANARY_OFFSET_FLAGS + 1u] = 1u;
    CHECK(dh_canary_decode_header(&decoded, encoded) == DH_CANARY_CODEC_INVALID_FLAGS);
    memcpy(encoded, baseline, sizeof(encoded));
    encoded[DH_CANARY_OFFSET_PAYLOAD_LENGTH] = 0u;
    encoded[DH_CANARY_OFFSET_PAYLOAD_LENGTH + 1u] = 0u;
    encoded[DH_CANARY_OFFSET_PAYLOAD_LENGTH + 2u] = 0x10u;
    encoded[DH_CANARY_OFFSET_PAYLOAD_LENGTH + 3u] = 0x01u;
    CHECK(dh_canary_decode_header(&decoded, encoded) == DH_CANARY_CODEC_INVALID_LENGTH);
    memcpy(encoded, baseline, sizeof(encoded));
    memset(encoded + DH_CANARY_OFFSET_SEQUENCE, 0, 8u);
    CHECK(
        dh_canary_decode_header(&decoded, encoded) == DH_CANARY_CODEC_INVALID_SEQUENCE
    );
    memcpy(encoded, baseline, sizeof(encoded));
    memset(encoded + DH_CANARY_OFFSET_OPERATION_HASH, 0, DH_CANARY_HASH_LENGTH);
    CHECK(
        dh_canary_decode_header(&decoded, encoded) ==
        DH_CANARY_CODEC_UNBOUND_OPERATION
    );
    memcpy(encoded, baseline, sizeof(encoded));
    memset(encoded + DH_CANARY_OFFSET_ATTEMPT_NONCE, 0, DH_CANARY_NONCE_LENGTH);
    CHECK(
        dh_canary_decode_header(&decoded, encoded) == DH_CANARY_CODEC_UNBOUND_NONCE
    );
    return 0;
}

static int expected_transition(uint8_t previous_type, uint8_t next_type) {
    if (previous_type == 0u) {
        return next_type == DH_CANARY_FRAME_READY;
    }
    if (previous_type >= DH_CANARY_FRAME_READY &&
        previous_type < DH_CANARY_FRAME_TERMINAL) {
        return next_type == (uint8_t)(previous_type + 1u);
    }
    return 0;
}

static int check_transition_matrix(void) {
    uint8_t previous_type = 0u;
    uint8_t next_type = 0u;
    for (previous_type = 0u; previous_type <= DH_CANARY_FRAME_TERMINAL + 1u;
         ++previous_type) {
        for (next_type = 0u; next_type <= DH_CANARY_FRAME_TERMINAL + 1u;
             ++next_type) {
            CHECK(
                dh_canary_transition_is_valid(previous_type, next_type) ==
                expected_transition(previous_type, next_type)
            );
        }
    }
    return 0;
}

int main(void) {
    int result = check_exact_wire_and_round_trip();
    if (result != 0) {
        return result;
    }
    result = check_encode_rejections();
    if (result != 0) {
        return result;
    }
    result = check_decode_rejections();
    if (result != 0) {
        return result;
    }
    return check_transition_matrix();
}
