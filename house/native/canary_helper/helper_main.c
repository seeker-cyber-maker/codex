#include "contract.h"
#include "protocol.h"

static int selector_is_protocol_v1(const char *selector) {
    static const char expected[] = "--protocol-v1";
    size_t index = 0u;

    if (selector == NULL) {
        return 0;
    }
    while (expected[index] != '\0') {
        if (selector[index] != expected[index]) {
            return 0;
        }
        ++index;
    }
    return selector[index] == '\0';
}

static int helper_codec_round_trip_valid(void) {
    uint8_t encoded[DH_CANARY_HEADER_LENGTH] = {0u};
    struct dh_canary_header input = {
        .version = DH_CANARY_PROTOCOL_VERSION,
        .type = DH_CANARY_FRAME_READY,
        .flags = 0u,
        .payload_length = 0u,
        .sequence = 1u,
        .operation_hash = {1u},
        .attempt_nonce = {1u},
    };
    struct dh_canary_header output = {0};

    if (dh_canary_encode_header(encoded, &input) != DH_CANARY_CODEC_OK) {
        return 0;
    }
    if (dh_canary_decode_header(&output, encoded) != DH_CANARY_CODEC_OK) {
        return 0;
    }
    return output.type == DH_CANARY_FRAME_READY && output.sequence == 1u;
}

static struct dh_canary_admission_proof helper_proof(void) {
    return (struct dh_canary_admission_proof){
        .control_role = dh_helper_contract_fd_role(DH_CANARY_FD_CONTROL),
        .input_role = dh_helper_contract_fd_role(DH_CANARY_FD_INPUT),
        .mock_sink_role = dh_helper_contract_fd_role(DH_CANARY_FD_MOCK_SINK),
        .status_role = dh_helper_contract_fd_role(DH_CANARY_FD_STATUS),
        .ready_transition_valid = dh_helper_contract_accept_transition(
            0u, DH_CANARY_FRAME_READY
        ),
        .codec_round_trip_valid = helper_codec_round_trip_valid(),
    };
}

int dh_helper_entrypoint_admit_from_proof(
    int argc,
    const char *const argv[],
    const struct dh_canary_admission_proof *proof
) {
    if (argv == NULL || proof == NULL) {
        return DH_CANARY_ADMISSION_NULL_ARGUMENT_VECTOR;
    }
    if (argc < 2) {
        return DH_CANARY_ADMISSION_MISSING_SELECTOR;
    }
    if (argc > 2) {
        return DH_CANARY_ADMISSION_EXTRA_ARGUMENTS;
    }
    if (argv[0] == NULL) {
        return DH_CANARY_ADMISSION_NULL_PROGRAM_NAME;
    }
    if (argv[1] == NULL) {
        return DH_CANARY_ADMISSION_NULL_SELECTOR;
    }
    if (!selector_is_protocol_v1(argv[1])) {
        return DH_CANARY_ADMISSION_SELECTOR_MISMATCH;
    }
    if (proof->control_role != DH_CANARY_FD_ROLE_CONTROL ||
        proof->input_role != DH_CANARY_FD_ROLE_CANARY_INPUT ||
        proof->mock_sink_role != DH_CANARY_FD_ROLE_MOCK_SINK_OUTPUT ||
        proof->status_role != DH_CANARY_FD_ROLE_TYPED_STATUS) {
        return DH_CANARY_ADMISSION_FD_CONTRACT;
    }
    if (!proof->ready_transition_valid || !proof->codec_round_trip_valid) {
        return DH_CANARY_ADMISSION_PROTOCOL_CONTRACT;
    }
    return DH_CANARY_ADMISSION_ACCEPTED;
}

int dh_helper_entrypoint_admit(int argc, const char *const argv[]) {
    const struct dh_canary_admission_proof proof = helper_proof();
    return dh_helper_entrypoint_admit_from_proof(argc, argv, &proof);
}

#ifndef DH_CANARY_ENTRYPOINT_UNIT_TEST
int main(int argc, char *argv[]) {
    return dh_helper_entrypoint_admit(argc, (const char *const *)argv) == DH_CANARY_ADMISSION_ACCEPTED
               ? 0
               : 64;
}
#endif
