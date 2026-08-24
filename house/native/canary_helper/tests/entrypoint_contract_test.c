#include "contract.h"
#include "protocol.h"

static int failures = 0;

static void expect_equal(int actual, int expected) {
    if (actual != expected) {
        ++failures;
    }
}

static void test_parent(void) {
    const char *valid[] = {"parent", "--protocol-v1"};
    const char *null_program[] = {NULL, "--protocol-v1"};
    const char *null_selector[] = {"parent", NULL};
    const char *alternate[] = {"parent", "--other"};
    const char *extra[] = {"parent", "--protocol-v1", "extra"};
    struct dh_canary_admission_proof proof = {
        .control_role = DH_CANARY_FD_ROLE_CONTROL,
        .input_role = DH_CANARY_FD_ROLE_CANARY_INPUT,
        .mock_sink_role = DH_CANARY_FD_ROLE_INVALID,
        .status_role = DH_CANARY_FD_ROLE_TYPED_STATUS,
        .ready_transition_valid = 1,
        .codec_round_trip_valid = 1,
    };

    expect_equal(
        dh_parent_entrypoint_admit(2, valid), DH_CANARY_ADMISSION_ACCEPTED
    );
    expect_equal(
        dh_parent_entrypoint_admit_from_proof(2, NULL, &proof),
        DH_CANARY_ADMISSION_NULL_ARGUMENT_VECTOR
    );
    expect_equal(
        dh_parent_entrypoint_admit_from_proof(2, null_program, &proof),
        DH_CANARY_ADMISSION_NULL_PROGRAM_NAME
    );
    expect_equal(
        dh_parent_entrypoint_admit_from_proof(2, null_selector, &proof),
        DH_CANARY_ADMISSION_NULL_SELECTOR
    );
    expect_equal(
        dh_parent_entrypoint_admit_from_proof(1, valid, &proof),
        DH_CANARY_ADMISSION_MISSING_SELECTOR
    );
    expect_equal(
        dh_parent_entrypoint_admit_from_proof(3, extra, &proof),
        DH_CANARY_ADMISSION_EXTRA_ARGUMENTS
    );
    expect_equal(
        dh_parent_entrypoint_admit_from_proof(2, alternate, &proof),
        DH_CANARY_ADMISSION_SELECTOR_MISMATCH
    );
    proof.input_role = DH_CANARY_FD_ROLE_INVALID;
    expect_equal(
        dh_parent_entrypoint_admit_from_proof(2, valid, &proof),
        DH_CANARY_ADMISSION_FD_CONTRACT
    );
    proof.input_role = DH_CANARY_FD_ROLE_CANARY_INPUT;
    proof.codec_round_trip_valid = 0;
    expect_equal(
        dh_parent_entrypoint_admit_from_proof(2, valid, &proof),
        DH_CANARY_ADMISSION_PROTOCOL_CONTRACT
    );
}

static void test_helper(void) {
    const char *valid[] = {"helper", "--protocol-v1"};
    struct dh_canary_admission_proof proof = {
        .control_role = DH_CANARY_FD_ROLE_CONTROL,
        .input_role = DH_CANARY_FD_ROLE_CANARY_INPUT,
        .mock_sink_role = DH_CANARY_FD_ROLE_MOCK_SINK_OUTPUT,
        .status_role = DH_CANARY_FD_ROLE_TYPED_STATUS,
        .ready_transition_valid = 1,
        .codec_round_trip_valid = 1,
    };
    uint8_t malformed[DH_CANARY_HEADER_LENGTH] = {0u};
    struct dh_canary_header header = {0};

    expect_equal(
        dh_helper_entrypoint_admit(2, valid), DH_CANARY_ADMISSION_ACCEPTED
    );
    proof.mock_sink_role = DH_CANARY_FD_ROLE_INVALID;
    expect_equal(
        dh_helper_entrypoint_admit_from_proof(2, valid, &proof),
        DH_CANARY_ADMISSION_FD_CONTRACT
    );
    proof.mock_sink_role = DH_CANARY_FD_ROLE_MOCK_SINK_OUTPUT;
    proof.ready_transition_valid = 0;
    expect_equal(
        dh_helper_entrypoint_admit_from_proof(2, valid, &proof),
        DH_CANARY_ADMISSION_PROTOCOL_CONTRACT
    );
    expect_equal(
        dh_helper_contract_fd_role(99), DH_CANARY_FD_ROLE_INVALID
    );
    expect_equal(
        dh_canary_decode_header(&header, malformed),
        DH_CANARY_CODEC_INVALID_VERSION
    );
}

int main(void) {
    test_parent();
    test_helper();
    return failures == 0 ? 0 : 1;
}
