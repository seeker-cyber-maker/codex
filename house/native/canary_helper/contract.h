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

int dh_parent_contract_launch_state(void);
int dh_parent_contract_fd_role(int descriptor);
int dh_parent_contract_accept_transition(uint8_t previous_type, uint8_t next_type);

int dh_helper_contract_launch_state(void);
int dh_helper_contract_fd_role(int descriptor);
int dh_helper_contract_accept_transition(uint8_t previous_type, uint8_t next_type);

#endif
