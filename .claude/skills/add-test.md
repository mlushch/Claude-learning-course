---
name: add-test
description: Create a unit test skeleton for the selected or described function
---

Given a function or class description (or selected code), generate a unit test skeleton.

For C# code: use xUnit with the Arrange/Act/Assert pattern.
For Python code: use pytest with descriptive test function names.

Rules:
- Cover the happy path first
- Add one test for each edge case (null input, empty collection, boundary values)
- Use descriptive test names: `MethodName_Scenario_ExpectedResult`
- Do not implement the test body — leave `// TODO: implement` comments in the assertions
- Output only the test code, no explanation
