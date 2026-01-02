Release automation and Zenodo publishing

This project supports automated releases that can publish to PyPI and optionally archive a release on Zenodo to mint a DOI.

Setup

1. Configure Repository Secrets (Settings → Secrets):
   - `PYPI_API_TOKEN` (optional): PyPI "__token__" value for twine upload
   - `ZENODO_TOKEN` (optional): Zenodo personal access token with deposition rights
   - `ZENODO_URL` (optional): defaults to `https://zenodo.org` if not set

2. How Releases trigger workflows
   - Create a GitHub Release (via the website or `gh release create`) with tag `vX.Y.Z` and a short release note.
   - When a release is published, the `release` workflow runs and:
     - Builds the sdist and wheel
     - Uploads to PyPI if `PYPI_API_TOKEN` is set
     - Uploads the built artifacts to the GitHub Release
     - If `ZENODO_TOKEN` is set, creates a Zenodo deposition, uploads the distributions, publishes it, and posts the DOI as a release comment

Notes

- The Zenodo workflow uses the Zenodo REST API directly and requires a personal token; you must add the token to repository secrets. See https://docs.zenodo.org for token creation and deposition details.
- Zenodo will create a DOI for each published deposition. Ensure your release notes and `setup.cfg`/`pyproject.toml` metadata are correct so Zenodo metadata is accurate.
- For more control over Zenodo metadata (authors, affiliations, keywords), we can extend the metadata payload in `.github/workflows/release.yml`.

Example: Create a local release and publish

# create a tag and release
git tag v1.0.0
git push origin v1.0.0

gh release create v1.0.0 --title "v1.0.0" --notes "Initial release"

The release workflow will run and upload artifacts accordingly.

- For richer control over Zenodo metadata, you can add `zenodo-metadata.json` at the repository root with a JSON object containing a `metadata` field; the workflow will merge it into the payload. Example:

```json
{
  "metadata": {
    "creators": [{"name": "Jane Doe", "affiliation": "Acme Labs", "orcid": "0000-0001-2345-6789"}],
    "keywords": ["matrix-evaluation", "benchmarks", "LLM"],
    "related_identifiers": [{"identifier": "https://doi.org/10.1234/example", "relation": "isSupplementTo"}]
  }
}
```

- Use the `Release Dry Run` workflow (Actions → Release Dry Run) to validate the build and Zenodo payload without uploading. Set `dry_run: true` (default) to simulate behavior and inspect `.zenodo/payload.json` and `dist/*` in the run logs.
- When ready to publish, create a GitHub Release and confirm `PYPI_API_TOKEN`/`ZENODO_TOKEN` are set in repository secrets.
