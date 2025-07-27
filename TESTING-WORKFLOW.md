# Testing Workflow

This document outlines how to test the entire translation workflow with your Azure Functions deployment.

1. Use `/api/start_translation` to start a job.
2. Poll `/api/check_status/{id}` until the translation completes.
3. Retrieve the result from `/api/get_result/{id}`.

Refer to the original French file for detailed examples.
