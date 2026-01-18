# Issue Tracker & Roadmap

## Critical Bugs

### [BUG-001] Plate Math Logic Errors
**Severity:** Critical
**Location:** `app/utils.py` -> `calculate_plates()`
**Description:** 
The plate calculation algorithm has two major flaws:
1. **Incorrect Subtraction:** When multiple plates of the same weight are needed (e.g., two 45s), the code calculates the correct count but only subtracts the weight of *one* plate from the remaining target.
   - *Current Code:* `per_side -= plate`
   - *Required Fix:* `per_side -= (count * plate)`
2. **Hardcoded String Formatting:** The output string logic hardcodes the prefix "2x" regardless of the actual count needed. 
   - *Current Code:* `parts.append(f"2×{plate}")`
   - *Behavior:* If 3 plates are needed, it still displays "2x".

### [BUG-002] Plate Inventory Limits Ignored
**Severity:** High
**Location:** `app/utils.py` -> `calculate_plates()`
**Description:**
The calculator fetches the user's available plates but does not respect the quantity (`pair_count`). It assumes infinite availability of any plate found in the database.
- *Impact:* The app might recommend using 3 pairs of 45lb plates when the user only owns 1 pair.

## Improvements / To-Do (oh yeah!)

### [IMP-001] Prevent Duplicate Logging
**Severity:** Low
**Location:** `app/routes.py` -> `rest_day()`
**Description:**
The code block preventing a user from logging multiple workout/rest entries on the same day is currently commented out.
- *Action:* Uncomment the validation logic in `routes.py` lines 204-207.

### [IMP-002] Visual Feedback for Completed Sets
**Severity:** Low
**Location:** `app/templates/dashboard.html` / `app/static/css/style.css`
**Description:**
Currently, when a work set is marked as "completed" (toggled), it only adds a line-through style to the button.
- *Requirement:* The entire row or button should become greyed out (visually distinct) to clearly indicate completion.

### [IMP-003] Enforce Sequential One-Way Set Completion
**Severity:** Medium
**Location:** `app/static/js/main.js`
**Description:**
Users can currently click sets in any order. The protocol demands discipline.
- *Requirement:* 
    1. Sets must be marked "Done" in strict order (Warmup 1 -> Warmup 2 -> Work Set 1).
    2. A set cannot be marked complete until the previous set is complete.
    3. Work sets cannot be attempted until all warmups are done.

### [IMP-004] Incomplete Workout Warning
**Severity:** Medium
**Location:** `app/static/js/main.js` -> `complete-btn` listener
**Description:**
Users can accidentally submit an incomplete workout.
- *Requirement:* If the "COMPLETE" button is clicked but there are unmarked/incomplete work sets:
    1. Show a confirmation modal/alert: "Are you sure you want to complete? There's incomplete work sets."
    2. Provide "Yes" (proceed with failure recorded) and "No" (cancel) options.

### [IMP-005] Feedback for Rest Day Logging
**Severity:** Low
**Location:** `app/routes.py` -> `rest_day()` / `app/static/js/main.js`
**Description:**
Users currently click the "REST" button and the page reloads, but there is no explicit visual confirmation if the action succeeded or failed.
- *Requirement:* Display a toast message or alert upon successfully logging a rest day (e.g., "REST DAY LOGGED — RECOVERY IS KING!") or an error message if it fails.

