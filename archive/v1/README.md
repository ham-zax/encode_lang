# Historical Lambda H/1 prototype

These files preserve the retired positional-vector prototype, including the pre-existing staged specification/calibration/example changes and the first interaction-only bootstrap improvements from the v2 rewrite.

They are not a second supported runtime, an alternate v2 specification, or instructions for the current receiver. The active package is under the repository's root `src/`; its public contract is Lambda H/2. Do not mix a v1 basis declaration, offset-hex packet, or historical test with the current codec.

The historical tests were moved without changing their assertions and were not run during the rewrite. They describe the old implementation only; no v2 test result can be inferred from them. Use Git history at the original prototype revision (`667204d`) when reconstructing the complete old checkout.

The preservation step did not stage changes. A later final inspection found the shared checkout's index populated with the migration; do not assume it still contains only the original five staged files. Earlier material is preserved here and in Git history. No index reset, commit, or push was performed by the implementation pass.
