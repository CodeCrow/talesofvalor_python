---
paths:
  - "**/tests**"
---

# Running Tests

`manage.py` is at the repository root, and the apps are inside the
`talesofvalor` package, so test labels need the full dotted path.

## Commands
```bash
# All tests
./manage.py test --settings=talesofvalor.settings.local

# A single app
./manage.py test --settings=talesofvalor.settings.local talesofvalor.characters

# A single module, class or test
./manage.py test --settings=talesofvalor.settings.local talesofvalor.characters.tests.test_influence.ApplyInfluenceTest
```

Add `--noinput` to drop a leftover test database from an interrupted run
instead of being prompted.

The same commands are written up for humans under "Testing > Unit tests" in
`README.md`; keep the two in step when either changes.

## Where tests go

Tests for an app live in that app's own `tests/` package, next to the code
they cover: `talesofvalor/players/tests/test_models.py`,
`talesofvalor/events/tests/test_influence.py`. This holds even when the
feature spans apps - put each app's tests under that app.

## Notes

- Tests run against MySQL, and creating the test database runs every
  migration from scratch, so a migration that only works on an existing
  database will fail here.
- django-cms keeps the logged in user in a threadlocal that outlives a test.
  Call `cms.utils.permissions.set_current_user(None)` in `setUp` before
  creating users, or they get stamped as created by a user the previous test
  rolled back. `talesofvalor.characters.tests.base.InfluenceTestCase` does
  this already.
