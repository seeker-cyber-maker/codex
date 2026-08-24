#include "contract.h"
#include "protocol.h"

_Static_assert(DH_CANARY_FD_MOCK_SINK == 5, "mock-sink FD contract changed");
_Static_assert(DH_CANARY_FD_STATUS < DH_CANARY_FD_LIMIT, "FD ceiling changed");

int dh_helper_contract_launch_state(void) {
    return DH_CANARY_LAUNCH_DISABLED;
}

int dh_helper_contract_fd_role(int descriptor) {
    if (descriptor == DH_CANARY_FD_CONTROL) {
        return DH_CANARY_FD_ROLE_CONTROL;
    }
    if (descriptor == DH_CANARY_FD_INPUT) {
        return DH_CANARY_FD_ROLE_CANARY_INPUT;
    }
    if (descriptor == DH_CANARY_FD_MOCK_SINK) {
        return DH_CANARY_FD_ROLE_MOCK_SINK_OUTPUT;
    }
    if (descriptor == DH_CANARY_FD_STATUS) {
        return DH_CANARY_FD_ROLE_TYPED_STATUS;
    }
    return DH_CANARY_FD_ROLE_INVALID;
}

int dh_helper_contract_accept_transition(uint8_t previous_type, uint8_t next_type) {
    return dh_canary_transition_is_valid(previous_type, next_type);
}
