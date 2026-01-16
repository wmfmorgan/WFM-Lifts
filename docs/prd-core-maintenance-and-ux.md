# PRD: Core Maintenance and UX Improvements

## Introduction/Overview
This document outlines the requirements for resolving critical plate calculation bugs and implementing user experience (UX) enhancements for the WFM Lifts application. The goal is to ensure the "Perfect Plate Math" standard is met and to provide a more disciplined, feedback-rich lifting experience.

## Goals
- Fix accuracy issues in plate calculation (BUG-001).
- Integrate plate inventory quantity limits (BUG-002).
- Enforce disciplined, sequential set completion (IMP-003).
- Provide clear visual and interactive feedback for set completion (IMP-002, IMP-005).
- Prevent accidental logging of incomplete workouts (IMP-004).

## User Stories
- **As a lifter**, I want the plate math to be 100% accurate so I don't underload or overload the bar.
- **As a lifter with limited equipment**, I want the app to warn me if I don't have enough plates for the calculated weight.
- **As a disciplined lifter**, I want the app to force me to complete my warmups in order before starting my work sets.
- **As a mobile user**, I want clear visual confirmation that a set is logged or a rest day is recorded.

## Functional Requirements
1.  **Correct Plate Math Subtraction:** The `calculate_plates` function must subtract the total weight of all plates of a specific denomination from the remaining target weight (e.g., if two 45s are used, subtract 90 lbs, not 45 lbs).
2.  **Dynamic Plate Count Formatting:** The output string for plates should reflect the actual count (e.g., "3x45", "4x45") instead of hardcoded "2x".
3.  **Plate Inventory Validation:** The calculation must compare the required plates against the user's `pair_count`.
4.  **Inventory Shortage Warning:** If the user lacks sufficient plates, the app should display the "perfect math" but highlight the missing plates in red/alert style.
5.  **Sequential Set Lock:** 
    - The "Done" / "Work Set" buttons must be disabled except for the next set in the logical sequence.
    - Warmups must be completed 100% before the first Work Set button becomes active.
6.  **Visual Completion Feedback:** 
    - When a set is marked "Done", the entire row or button should be greyed out.
    - Completion status must be toggleable (user can undo a mistake).
7.  **Incomplete Workout Warning:** 
    - Upon clicking "COMPLETE", if any work sets are unmarked, show a warning modal: "Are you sure you want to complete? There's incomplete work sets."
    - Options: "Yes" (Complete with failure recorded) and "No" (Return to workout).
8.  **Rest Day Toast:** Successfully logging a rest day must trigger a modern toast notification: "REST DAY LOGGED — RECOVERY IS KING!".

## Non-Goals (Out of Scope)
- Automatic deload recommendations (reserved for future milestone).
- Bodyweight tracking implementation.
- Redesigning the core layout of the dashboard.

## Design Considerations
- **Greying Out**: Use `opacity: 0.5` or a darker background color for completed set rows.
- **Sequence Lock**: Use the `disabled` attribute on buttons that are not "next".
- **Toast Notifications**: Use a simple JS-based toast or integrate a lightweight library if necessary.

## Technical Considerations
- **Database**: Ensure `Plate` model `pair_count` is correctly queried in `utils.py`.
- **JS State**: `main.js` will need to track the "Active Set Index" for each lift.

## Success Metrics
- 0% plate math errors in testing.
- Successful enforcement of warmup-first discipline in the UI.
- Positive user feedback on "honesty" enforcement.

## Open Questions
- Should we allow "skipping" warmups if the user explicitly overrides a setting? (Current PRD assumes NO skipping).
