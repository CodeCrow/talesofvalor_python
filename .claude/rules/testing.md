---
paths
  - "**/tests**
---

# Running Tests


## Commands
```bash
# All tests
"./talesofvalor/manage.py test --settings=talesofvalor.settings.local"

# Specific tests
"./talesofvalor/manage.py test --settings=talesofvalor.settings.local skills.tests.test_models.test_file.TestClass"

```