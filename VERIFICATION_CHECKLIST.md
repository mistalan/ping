# Post-Merge Verification Checklist

After merging this PR, verify that the CI/CD pipeline is working correctly.

## Immediate Verification (After Merge)

### ✅ Workflow Files Visible
- [ ] Go to repository → `.github/workflows/`
- [ ] Verify 5 workflow files exist:
  - [ ] ci.yml
  - [ ] deploy.yml
  - [ ] release.yml
  - [ ] codeql.yml
  - [ ] multi-platform.yml

### ✅ Status Badges Visible
- [ ] Open README.md
- [ ] Verify CI/CD badges appear at the top
- [ ] Badges should show "passing" or "no runs yet"

### ✅ Actions Tab Enabled
- [ ] Navigate to Actions tab
- [ ] Verify 5 workflows are listed:
  - CI
  - Deploy
  - Release
  - CodeQL Security Analysis
  - Windows Testing

## Test CI Workflow (Automatic on Merge)

The CI workflow should run automatically when this PR is merged.

- [ ] Go to Actions → CI
- [ ] Find the workflow run triggered by the merge
- [ ] Wait for completion (~3-5 minutes)
- [ ] Verify all jobs pass:
  - [ ] validate-powershell
  - [ ] validate-python (3 jobs: 3.12)
  - [ ] lint-python
  - [ ] security-scan
  - [ ] all-checks-complete

**If CI fails:** Check the job logs for errors. Common issues are usually environment-specific.

## Test Deploy Workflow (Automatic on Merge)

The Deploy workflow should also run automatically.

- [ ] Go to Actions → Deploy
- [ ] Find the workflow run triggered by the merge
- [ ] Wait for completion (~2-3 minutes)
- [ ] Verify job passes: `package`
- [ ] Check artifacts are created:
  - [ ] ping-latest-zip
  - [ ] ping-latest-tarball
  - [ ] ping-latest-checksums
- [ ] Download an artifact and verify contents

**If Deploy fails:** Check package creation steps in the logs.

## Test CodeQL Workflow (Automatic on Merge)

- [ ] Go to Actions → CodeQL Security Analysis
- [ ] Find the workflow run triggered by the merge
- [ ] Wait for completion (~5-8 minutes)
- [ ] Verify job passes: `analyze`
- [ ] Go to Security → Code scanning
- [ ] Verify CodeQL results appear (may be empty if no issues found)

## Test Multi-Platform Workflow (Manual)

This workflow tests on multiple platforms. Trigger it manually first:

- [ ] Go to Actions → Windows Testing
- [ ] Click "Run workflow"
- [ ] Select branch: main
- [ ] Click "Run workflow" button
- [ ] Wait for completion (~10-15 minutes)
- [ ] Verify all jobs pass:
  - [ ] test-powershell-cross-platform (3 jobs: Windows)
  - [ ] test-python-versions (9 jobs: 3 OS × 3 Python versions)
  - [ ] integration-test

**Note:** This workflow runs daily automatically, so manual run is optional.

## Test Release Workflow (Manual)

Test creating a release with a git tag:

### Option 1: Using Git Commands (Recommended)

```bash
# Clone the repo (if not already)
git clone https://github.com/mistalan/ping.git
cd ping

# Create and push a test tag
git tag v0.1.0-test
git push origin v0.1.0-test
```

### Option 2: Using GitHub UI

1. Go to Releases
2. Click "Create a new release"
3. Click "Choose a tag"
4. Type `v0.1.0-test`
5. Click "Create new tag on publish"
6. Click "Publish release"

### Verify Release Workflow

- [ ] Go to Actions → Release
- [ ] Wait for completion (~4-6 minutes)
- [ ] Verify job passes: `create-release`
- [ ] Go to Releases
- [ ] Verify new release `v0.1.0-test` exists
- [ ] Verify release has 3 assets:
  - [ ] ping-v0.1.0-test.zip
  - [ ] ping-v0.1.0-test.tar.gz
  - [ ] checksums.txt
- [ ] Verify release notes are auto-generated
- [ ] Download and extract the ZIP
- [ ] Verify it contains all scripts and documentation

**Clean up test release:**
- [ ] Delete the tag: `git push --delete origin v0.1.0-test`
- [ ] Delete the release from GitHub UI

## Verify Dependabot

- [ ] Go to Insights → Dependency graph → Dependabot
- [ ] Verify Dependabot is enabled
- [ ] Check for any pending updates
- [ ] Expect weekly update checks for:
  - GitHub Actions
  - Python (pip)

**Note:** Dependabot PRs will appear over time as dependencies update.

## Verify Security Features

### Security Tab
- [ ] Go to Security tab
- [ ] Verify "Code scanning" is active
- [ ] Verify "Dependabot alerts" is enabled

### CodeQL Scans
- [ ] Go to Security → Code scanning
- [ ] Should see results from CodeQL (may be empty)
- [ ] Verify "Python" language is analyzed

### Scheduled Scans
- [ ] Go to Actions
- [ ] Find scheduled workflow runs (may take time)
- [ ] CodeQL runs weekly (Mondays)
- [ ] Multi-Platform runs daily

## Test Badge Links

- [ ] Click CI badge in README
- [ ] Verify it links to CI workflow
- [ ] Click Deploy badge
- [ ] Verify it links to Deploy workflow
- [ ] Click CodeQL badge
- [ ] Verify it links to CodeQL workflow

## Documentation Verification

- [ ] Open PIPELINE_SUMMARY.md
- [ ] Verify it renders correctly
- [ ] Open QUICK_REFERENCE.md
- [ ] Verify all commands are correct
- [ ] Open .github/WORKFLOWS.md
- [ ] Verify workflow descriptions are accurate
- [ ] Open .github/WORKFLOWS_DETAILED.md
- [ ] Verify diagrams and tables render correctly

## Common Issues and Solutions

### Issue: Workflow doesn't run
**Solution:** 
- Check if Actions are enabled: Settings → Actions → General
- Verify workflow file syntax with yamllint

### Issue: PowerShell tests fail on Linux
**Expected:** Some warnings are normal for Windows-specific cmdlets

### Issue: Permissions error in workflows
**Solution:**
- Go to Settings → Actions → General → Workflow permissions
- Select "Read and write permissions"
- Save

### Issue: Security alerts not appearing
**Solution:**
- Go to Settings → Security & analysis
- Enable "Dependency graph", "Dependabot alerts", and "Code scanning"

### Issue: Artifact download requires login
**Expected:** GitHub requires authentication for artifact downloads
**Alternative:** Use Releases for public downloads

## Success Criteria

Pipeline is working correctly if:
- ✅ All workflows run without errors on merge
- ✅ CI workflow validates code changes
- ✅ Deploy workflow creates downloadable artifacts
- ✅ Release workflow creates versioned releases
- ✅ CodeQL workflow scans for security issues
- ✅ Status badges show "passing"
- ✅ Documentation is complete and accurate

## Next Steps After Verification

1. **Create official v1.0.0 release:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Monitor workflows:**
   - Watch for Dependabot PRs
   - Review security scan results weekly
   - Check multi-platform test results

3. **Update as needed:**
   - Adjust workflows based on usage
   - Add more tests as code evolves
   - Update documentation

4. **Share with team:**
   - Link to QUICK_REFERENCE.md for developers
   - Share release URLs with users
   - Document any custom procedures

## Support

If you encounter issues not covered here:
1. Check workflow logs in Actions tab
2. Review documentation files
3. Consult GitHub Actions documentation
4. Open an issue for help

## Completion

Date verified: _______________

Verified by: _______________

Notes:
_______________________________________________
_______________________________________________
_______________________________________________

All checks passed: ☐ Yes ☐ No (see notes)
