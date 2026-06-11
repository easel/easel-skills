# Marketplace Metadata

Use this reference when a release includes plugin or skill marketplace metadata.

## Checks

- Marketplace entries should name each installable item clearly.
- Aggregate entries such as `all` should include every skill intended for bundle
  installation.
- Individual entries should expose exactly the skill they advertise.
- Marketplace source URLs should use HTTPS unless the project explicitly
  documents SSH.
- Wrapper manifests should share the release version with the root manifest when
  they are published together.
- Install instructions should mention both aggregate and individual installs
  when both are supported.

## Release Flow

1. Audit root manifests, marketplace files, wrapper manifests, and install docs.
2. Add or remove entries so installable skills match the actual `skills/`
   directory.
3. Validate from a clean checkout or Docker image when possible.
4. Confirm generated or cache directories are ignored before committing.
