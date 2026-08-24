#ifndef DREAM_HOUSE_CANARY_CONTRACT_H
#define DREAM_HOUSE_CANARY_CONTRACT_H

#include <stdint.h>

#define DH_CANARY_FD_CONTROL 3
#define DH_CANARY_FD_INPUT 4
#define DH_CANARY_FD_MOCK_SINK 5
#define DH_CANARY_FD_STATUS 6
#define DH_CANARY_FD_LIMIT 7

enum dh_canary_launch_state {
    DH_CANARY_LAUNCH_DISABLED = 0,
};

enum dh_canary_fd_role {
    DH_CANARY_FD_ROLE_INVALID = 0,
    DH_CANARY_FD_ROLE_CONTROL = 1,
    DH_CANARY_FD_ROLE_CANARY_INPUT = 2,
    DH_CANARY_FD_ROLE_MOCK_SINK_OUTPUT = 3,
    DH_CANARY_FD_ROLE_TYPED_STATUS = 4,
};

enum dh_canary_admission_result {
    DH_CANARY_ADMISSION_ACCEPTED = 0,
    DH_CANARY_ADMISSION_NULL_ARGUMENT_VECTOR = 1,
    DH_CANARY_ADMISSION_NULL_PROGRAM_NAME = 2,
    DH_CANARY_ADMISSION_MISSING_SELECTOR = 3,
    DH_CANARY_ADMISSION_EXTRA_ARGUMENTS = 4,
    DH_CANARY_ADMISSION_NULL_SELECTOR = 5,
    DH_CANARY_ADMISSION_SELECTOR_MISMATCH = 6,
    DH_CANARY_ADMISSION_FD_CONTRACT = 7,
    DH_CANARY_ADMISSION_PROTOCOL_CONTRACT = 8,
};

struct dh_canary_admission_proof {
    int control_role;
    int input_role;
    int mock_sink_role;
    int status_role;
    int ready_transition_valid;
    int codec_round_trip_valid;
};

int dh_parent_contract_launch_state(void);
int dh_parent_contract_fd_role(int descriptor);
int dh_parent_contract_accept_transition(uint8_t previous_type, uint8_t next_type);

int dh_helper_contract_launch_state(void);
int dh_helper_contract_fd_role(int descriptor);
int dh_helper_contract_accept_transition(uint8_t previous_type, uint8_t next_type);

int dh_parent_entrypoint_admit(int argc, const char *const argv[]);
int dh_parent_entrypoint_admit_from_proof(
    int argc,
    const char *const argv[],
    const struct dh_canary_admission_proof *proof
);
int dh_helper_entrypoint_admit(int argc, const char *const argv[]);
int dh_helper_entrypoint_admit_from_proof(
    int argc,
    const char *const argv[],
    const struct dh_canary_admission_proof *proof
);

#endif
