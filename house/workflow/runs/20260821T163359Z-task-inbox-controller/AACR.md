# Local task inbox/controller after-action review

Keeping the inbox and task journal in separate databases made the acceptance
crash window observable. Recovery therefore had to demonstrate exact task
receipt replay rather than relying on a single local transaction. The fixture
passed both a deliberate post-submit interruption and lease expiry immediately
before the terminal inbox commit without duplicating task history.

Controller-issued tokens are not caller-selected, status output retains only a
token hash, and the live clock is injected at construction for testing instead
of being overridable per authority-bearing call. This prevents a Python caller
from extending its own lease by supplying an old timestamp.

The remaining weakness is explicit: cooperative fencing does not prevent an
untrusted local process from bypassing this API and opening the task journal
directly. That boundary belongs to a later authenticated writer service or
OS-level isolation, not to this offline fixture.
