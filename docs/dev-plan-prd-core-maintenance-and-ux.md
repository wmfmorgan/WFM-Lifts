# Development Plan - Core Maintenance and UX Improvements

## Relevant Files

- `app/utils.py` - Contains `calculate_plates` and `calculate_warmups`. Needs logic fixes for BUG-001 and inventory checks for BUG-002.
- `tests/test_utils.py` - Unit tests for plate calculation logic.
- `app/routes.py` - Contains `rest_day` and `complete_workout` routes. Needs fixes for IMP-001 and IMP-005.
- `tests/test_routes.py` - Unit tests for route-level logic and duplicate logging prevention.
- `app/models.py` - Defines `Plate` and `WorkoutLog` models. Relevant for inventory limits and logging checks.
- `app/templates/dashboard.html` - Dashboard template. Needs updates for visual feedback (IMP-002) and sequential lock.
- `app/static/js/main.js` - Handles set completion clicks and "Complete" button logic. Needs updates for IMP-003, IMP-004, and IMP-005.
- `app/static/css/style.css` - Styles for greyed-out completed sets.

### Notes

- This project follows strict TDD. Tests must be written before production code.
- Use `pytest` to run backend tests.
- UI changes will be verified using the browser tool and manual walkthroughs.
- All development should occur within the Docker environment (`wfm-lifts` image).

## Tasks

- [x] 1.0 [BUG-001] Fix Plate Math Logic Errors (Subtraction and String Formatting)
  - [x] 1.1 Create `tests/test_utils.py` (or update existing) with test cases for 135, 225, 315, 405 lbs to verify incorrect subtraction and hardcoded "2x" strings (RED).
  - [x] 1.2 Fix `calculate_plates` in `app/utils.py`: change `per_side -= plate` to `per_side -= (count * plate)`.
  - [x] 1.3 Fix `calculate_plates` in `app/utils.py`: dynamically build count string (e.g., `f"{count}×{plate}"` if count > 1) (GREEN).
  - [x] 1.4 Verify all plate math tests pass.
- [x] 2.0 [BUG-002] Implement Plate Inventory Limits in Calculation
  - [x] 2.1 Update `tests/test_utils.py` with cases where `working_weight` requires more plates than available in inventory (RED).
  - [x] 2.2 Update `calculate_plates` in `app/utils.py` to accept `available_inventory` (mapping of weight to count) and respect those limits.
  - [x] 2.3 Implement "Warning" logic: return the "perfect" setup but flag missing plates (GREEN).
- [x] 3.0 [IMP-001] Enable Duplicate Logging Prevention for Rest Days
  - [x] 3.1 Create `tests/test_routes.py` and write a test that attempts to log two rest days for the same user on the same date (RED).
  - [x] 3.2 Uncomment and refine the validation logic in `app/routes.py` within the `rest_day` and `complete_workout` routes (GREEN).
  - [x] 3.3 Verify duplicate logs are rejected with a flash message.
- [x] 4.0 [IMP-002] Visual Feedback for Completed Sets (Grey Out Row)
  - [x] 4.1 Update `app/static/css/style.css` to add a `.set.completed` or similar class that applies `opacity: 0.5`, `background-color: #444`, and/or `text-decoration: line-through`.
  - [x] 4.2 Update `app/templates/dashboard.html` to ensure the container element is targeted by the visual change when the button is clicked.
  - [x] 4.3 Update `app/static/js/main.js` to toggle the completed class on the parent row element.
- [x] 5.0 [IMP-003] Enforce Sequential One-Way Set Completion
  - [x] 5.1 Update `app/static/js/main.js` to initialize all sets as disabled except for the first one.
  - [x] 5.2 Implement logic to enable the next set only when the current set is marked "Done".
  - [x] 5.3 Ensure Work Sets are only enabled once all Warmup Sets are completed.
  - [x] 5.4 Verify sequential enforcement in the dashbaord.
- [x] 6.0 [IMP-004] Implement Incomplete Workout Warning Modal
  - [x] 6.1 Create or use a Modal component in `app/templates/dashboard.html` for the warning.
  - [x] 6.2 Update `app/static/js/main.js` to intercept the "COMPLETE" click, check for incomplete work sets, and show the modal if necessary.
  - [x] 6.3 Implement "Yes" (submit anyway) and "No" (dismiss modal) handlers.
- [x] 7.0 [IMP-005] Feedback for Rest Day Logging (Toast Notification)
  - [x] 7.1 Implement a lightweight toast notification container in `app/templates/base.html` or `dashboard.html`.
  - [x] 7.2 Update `app/static/js/main.js` to trigger the toast after a successful rest day log response from the server.
  - [x] 7.3 Update `app/routes.py` to ensure the flash message is still sent for standard non-JS reloads.
