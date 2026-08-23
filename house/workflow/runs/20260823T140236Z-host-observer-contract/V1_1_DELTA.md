# Host observer v1.1 - file-descriptor identity delta

This delta is the smallest repair adopted after outside review. The immutable
council packet and reviewed v1 contract are retained unchanged.

## Problem

Path-based `lstat -> open/read -> lstat` can observe different objects when a
name is replaced between calls. Comparing only size and timestamps is not a
sufficient binding between the inspected path and the bytes hashed.

## Required v1.1 invariant

All discovery and reads are anchored to already-open directory descriptors:

1. Open the declared root as a directory with no symlink traversal.
2. Traverse each component relative to its parent descriptor with no-follow
   semantics. Never reopen a previously validated path by absolute name.
3. Open a candidate regular file relative to its parent descriptor with
   read-only and no-follow flags.
4. `fstat` that file descriptor before reading; bind device, inode, mode, link
   count, size, and high-resolution times.
5. Hash bytes read only from that same descriptor.
6. `fstat` the same descriptor after EOF and require exact identity and stable
   metadata.
7. Re-stat the directory entry relative to the still-open parent and require it
   to name the same device/inode as the open descriptor.
8. Keep directory descriptors open through enumeration and child validation;
   bind pre/post directory metadata and the byte-sorted typed child list.

Any disagreement yields `UNSTABLE_RETRY_REQUIRED`; that attempt contributes no
usable descriptor. Unsupported no-follow or descriptor-relative primitives
yield `OBSERVER_ERROR`, never a path-based fallback.

## Threat-model ceiling

This detects ordinary concurrent replacement and prevents symlink traversal.
It does not claim protection from a compromised kernel, privileged actor able
to spoof filesystem metadata, malicious storage firmware, or mutation after
the observation interval. Those require a later trust, freshness, snapshot, or
signature boundary.

No other v1 field, state, authority boundary, or non-goal changes.
