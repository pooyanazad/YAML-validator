# Writing release highlights

The release generator compares the preceding version tag reachable from the released commit with that commit. It excludes the current tag on retries and fails on missing/unrelated bases or a tag pointing to a different commit.

For a concise, reviewed summary, add `release-notes/<tag>.md` before releasing. Begin with the exact previous-tag marker:

```markdown
<!-- previous-tag: v3.3.0-20260901 -->
- Describe a user-visible change shipped since that tag.
```

Only describe changes in that range. Existing capabilities belong in the usage documentation. Without a highlights file, the generator reports category counts from commit subjects and links the complete range; it does not invent features. The GitHub report also includes grouped commit details in an expandable section. The README contains only the summary and comparison link.

Generate a report locally without publishing:

```bash
python scripts/release_notes.py --version v3.4.0-20261011 \
  --head refs/tags/v3.4.0-20261011 --output release-body.md
```

The PyPI build regenerates its README with the same generator before building the wheel and source distribution. GitHub/Docker tags and the package version are separate; the PyPI install command uses `__version__` from the released source.

To repair a published GitHub description, run **Refresh Release Notes** with the existing tag. This edits only the description; it does not rebuild Docker, move tags, change PyPI files, or publish packages. PyPI distributions already published under a version cannot be replaced by this workflow.

README update branches require a PR before reaching protected `main`. If the bot cannot open one, enable **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests**, or open the branch's PR manually. The pipeline warning includes the comparison link.
