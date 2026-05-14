# M16 — HR & Payroll

> **Phase**: phase-1-modules  **SRS ref**: Module 16  **Depends on**: M01, M02, M12  **Est. effort**: L

## Goal

Employee lifecycle: profile, attendance, leave, payroll (salary structure, runs, payslips), probation, notice period, F&F (full & final) settlement, holiday calendar.

## Steps

1. **Models** `apps/hr/`:
   - `Employee(user OneToOne, employee_code unique, doj, dob, gender, branch FK, department FK, designation FK, manager FK self, status=ACTIVE|ON_NOTICE|EXITED|SUSPENDED, bank_account, pan, aadhaar_masked, addresses[], documents[])`.
   - `EmployeeProbation(employee, start, end, status=ACTIVE|CONFIRMED|EXTENDED|TERMINATED, decision_at, decision_by)`.
   - `Attendance(employee, date, status=PRESENT|ABSENT|HALF_DAY|LEAVE|HOLIDAY|WO, in_at, out_at, hours)`.
   - `LeaveType(code, name, accrual_rules_json, max_balance)` + `LeaveBalance(employee, leave_type, balance)` + `LeaveRequest(employee, leave_type, from, to, days, reason, status, approver FK, decided_at)`.
   - `HolidayCalendar(year, branch FK nullable, date, name, is_optional)`.
   - `SalaryStructure(employee, effective_from, ctc, components_json [{code, name, kind=EARNING|DEDUCTION|EMPLOYER_CONTRIB, formula}])`.
   - `PayrollRun(month, branch FK, status=DRAFT|PROCESSED|PAID|CLOSED, run_by, run_at)`.
   - `Payslip(run FK, employee, components_json, gross, deductions, net, generated_pdf)`.
   - `FFSettlement(employee, last_working_day, dues_json, payable, status, settled_at, settled_by)`.
2. **Services**:
   - `attendance_service.mark/import/correct`.
   - `leave_service.apply/approve/reject/cancel`, accruals nightly.
   - `payroll_service.run(month, branch)` — pulls attendance, applies formulas, computes statutory deductions (PF, ESI, PT, TDS estimate), generates payslips, posts to M12.
   - `probation_service.confirm/extend/terminate`.
   - `ff_service.compute(employee)` — leave encashment + bonus + dues − recoveries → payable.
3. **Statutory tables** seeded; rates configurable in M18 (no hardcoding).
4. **Error prefix**: `HR-*`.
5. **Endpoints**: `/api/v1/hr/employees/`, `/attendance/`, `/leaves/`, `/payroll/runs/`, `/payslips/`, `/ff/`, `/holidays/`.
6. **Admin-UI**:
   - Employee list + 360 page.
   - Attendance grid (month view) with bulk-edit.
   - Leave inbox (approver view).
   - Payroll run wizard.
   - Holiday calendar editor.
   - Probation tracker & F&F worksheet.
7. **Self-service portal** (admin-ui under `/me/`): payslips, leave apply, attendance view.
8. **Permissions**: `hr.employee.view/manage`, `hr.attendance.mark/correct`, `hr.leave.approve`, `hr.payroll.run/post`, `hr.ff.process`.
9. **Tests**: payroll math (every component), leave accrual, F&F settlement correctness, M12 posting.
10. **Docs**: `docs/modules/hr/*` + ADR `019-payroll-formula-engine.md`.
11. Commit: `feat(M16): hr & payroll`.

## Verification

### Manual
1. Run payroll for month → payslips PDF generated → M12 JE posted (DR Salary Exp, CR Bank/Statutory liabilities).
2. Leave apply → manager approves → balance reduces.
3. Mark employee on notice → on LWD, F&F worksheet auto-populates.

### Automated
- `pytest backend/tests/hr/ -q` ≥ 85%.
- UI + Playwright + Newman green.

## Definition of Done

- [ ] Payroll closes monthly without manual JE.
- [ ] Self-service portal works.
- [ ] `_state.md` advanced.

## Next step

→ [`M17-notifications.md`](./M17-notifications.md)

## Previous step

← [`M13-reports.md`](./M13-reports.md)
