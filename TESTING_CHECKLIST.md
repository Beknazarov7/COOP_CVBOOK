# ✅ Admin CV Management - Testing Checklist

## Pre-Testing Setup
- [ ] Both servers are running:
  - [ ] Co-op Website: `python3 manage.py runserver` (port 8000)
  - [ ] CV Book: `python3 manage.py runserver 8001` (port 8001)
- [ ] You have admin/staff access to the CV Book application
- [ ] There are students with `cohort_status = 'Senior'` in the Co-op database

---

## Test 1: Access Admin Dashboard
- [ ] Navigate to: `http://localhost:8001/cv/admin/dashboard/`
- [ ] Dashboard loads without errors
- [ ] Statistics are displayed (Total CVs, Student CVs, etc.)
- [ ] "Manage Student CVs" button is visible
- [ ] "Manage External CVs" button is visible

**Expected Result**: Dashboard displays correctly with all statistics and buttons.

---

## Test 2: Access Student CVs Management Page
- [ ] Click "Manage Student CVs" button
- [ ] OR navigate directly to: `http://localhost:8001/cv/admin/student-cvs/`
- [ ] Page loads without errors
- [ ] Header shows "Manage Student CVs"
- [ ] "Back to Dashboard" button is visible

**Expected Result**: Student CVs management page loads successfully.

---

## Test 3: Verify Student List Display
- [ ] Table is visible with columns: Name, Email, Major, Cohort, CV Status, Actions
- [ ] Students are listed in the table
- [ ] Students WITHOUT CVs appear first (sorted)
- [ ] Status badges are displayed correctly:
  - [ ] Red "Not Submitted" for students without CVs
  - [ ] Orange "Pending" for unapproved CVs
  - [ ] Blue "Approved" for approved but unpublished CVs
  - [ ] Green "Published" for published CVs

**Expected Result**: All seniors are listed with correct status badges.

---

## Test 4: Test Filtering - Search
- [ ] Enter a student name in the search box
- [ ] Click "Filter" button
- [ ] Results show only matching students
- [ ] Click "Reset" button
- [ ] All students are shown again

**Expected Result**: Search filter works correctly.

---

## Test 5: Test Filtering - Status
- [ ] Select "CV Not Submitted" from Status dropdown
- [ ] Click "Filter" button
- [ ] Results show only students without CVs
- [ ] All shown students have red "Not Submitted" badge

**Expected Result**: Status filter correctly shows only students without CVs.

---

## Test 6: Test Filtering - Cohort
- [ ] Select "Senior" from Cohort dropdown
- [ ] Click "Filter" button
- [ ] Results show only Senior students
- [ ] Click "Reset" button

**Expected Result**: Cohort filter works correctly.

---

## Test 7: Test Filtering - Major
- [ ] Select a major from Major dropdown (e.g., "Computer Science")
- [ ] Click "Filter" button
- [ ] Results show only students with that major
- [ ] Click "Reset" button

**Expected Result**: Major filter works correctly.

---

## Test 8: Test Pagination
- [ ] If there are more than 20 students, pagination controls appear
- [ ] Click "Next" or page number
- [ ] Next page of students loads
- [ ] Click "Previous" to go back

**Expected Result**: Pagination works correctly.

---

## Test 9: Create CV for Student (Main Feature)
- [ ] Find a student with "Not Submitted" status (red badge)
- [ ] Click the green "Create CV" button
- [ ] CV form opens in a new page
- [ ] **VERIFY AUTO-FILL**: Check that the following fields are pre-filled:
  - [ ] Name field contains student's first name
  - [ ] Surname field contains student's last name
  - [ ] Email field contains student's email
  - [ ] Major dropdown shows student's major
  - [ ] Graduation Year dropdown shows student's graduation year
  - [ ] Status dropdown shows "Open to full-time"

**Expected Result**: Form opens with all student data pre-filled correctly.

---

## Test 10: Complete CV Submission
- [ ] Fill in the remaining required fields:
  - [ ] Country (select any)
  - [ ] Education section (at least one entry)
  - [ ] Professional Experience (at least one entry)
  - [ ] Competencies (at least one entry)
  - [ ] Projects (at least one entry)
- [ ] Navigate through all form steps
- [ ] Review the CV on the final step
- [ ] Click "Submit" button
- [ ] Wait for submission to complete

**Expected Result**: CV submits successfully without errors.

---

## Test 11: Verify Auto-Approval for Seniors
- [ ] After submission, navigate back to: `http://localhost:8001/cv/admin/student-cvs/`
- [ ] Find the student you just created a CV for
- [ ] **VERIFY**: Status badge should be GREEN "Published"
- [ ] **NOT** orange "Pending" or blue "Approved"

**Expected Result**: Senior student's CV is automatically approved and published.

---

## Test 12: Verify CV Appears on CV Book
- [ ] Navigate to: `http://localhost:8001/`
- [ ] Look for the student's CV card
- [ ] CV should be visible in the public CV Book

**Expected Result**: CV is publicly visible immediately.

---

## Test 13: Edit Existing CV
- [ ] Go back to: `http://localhost:8001/cv/admin/student-cvs/`
- [ ] Find a student WITH a CV (any status)
- [ ] Click the purple "Edit" button
- [ ] CV edit form opens
- [ ] Existing data is loaded in the form

**Expected Result**: Edit functionality works correctly.

---

## Test 14: Verify Database Integration
- [ ] Open a terminal
- [ ] Connect to Co-op database:
  ```bash
  sqlite3 /home/student/coop/UCA-Co-op-Website/db.sqlite3
  ```
- [ ] Run query:
  ```sql
  SELECT COUNT(*) FROM students WHERE cohort_status = 'Senior';
  ```
- [ ] Note the count
- [ ] Exit sqlite: `.exit`
- [ ] Go to student CVs page
- [ ] Count total students shown (across all pages)
- [ ] Numbers should match (or CV count should be ≤ student count)

**Expected Result**: All seniors from Co-op DB are shown in the admin interface.

---

## Test 15: Error Handling
- [ ] Try to access admin pages without being logged in as staff
- [ ] Should redirect or show permission denied
- [ ] Try creating a CV with missing required fields
- [ ] Should show validation errors

**Expected Result**: Proper error handling and validation.

---

## 🎯 Success Criteria

All tests should pass with the following outcomes:

✅ **Dashboard accessible** and displays statistics
✅ **Student list shows all seniors** from Co-op database
✅ **Filtering works** for search, cohort, major, and status
✅ **Students without CVs are clearly marked** with red badge
✅ **Create CV button pre-fills student data** correctly
✅ **Senior CVs are auto-approved and published** immediately
✅ **CVs appear on public CV Book** without manual approval
✅ **Edit functionality works** for existing CVs
✅ **Pagination works** for large lists
✅ **Error handling** is proper

---

## 🐛 Common Issues and Solutions

### Issue: No students showing up
**Solution**: 
- Check Co-op database has students with `cohort_status = 'Senior'`
- Verify database path in `admin_views.py` is correct
- Check console for SQL errors

### Issue: Form not auto-filling
**Solution**:
- Check browser console for JavaScript errors
- Verify URL parameters are being passed
- Check the 500ms delay in auto-fill script

### Issue: CV not auto-approving
**Solution**:
- Verify `user_type=student` and `cohort_status=Senior` in URL
- Check backend logs for processing errors
- Verify CV submission view is receiving correct parameters

### Issue: URL errors (NoReverseMatch)
**Solution**:
- All URLs should use `cv:` namespace
- Example: `{% url 'cv:admin-student-cvs' %}`

---

## 📊 Test Results

Date Tested: _______________
Tester: _______________

| Test # | Test Name | Pass/Fail | Notes |
|--------|-----------|-----------|-------|
| 1 | Access Dashboard | ⬜ | |
| 2 | Access Student CVs Page | ⬜ | |
| 3 | Verify Student List | ⬜ | |
| 4 | Test Search Filter | ⬜ | |
| 5 | Test Status Filter | ⬜ | |
| 6 | Test Cohort Filter | ⬜ | |
| 7 | Test Major Filter | ⬜ | |
| 8 | Test Pagination | ⬜ | |
| 9 | Create CV - Auto-fill | ⬜ | |
| 10 | Complete CV Submission | ⬜ | |
| 11 | Verify Auto-Approval | ⬜ | |
| 12 | CV on Public Book | ⬜ | |
| 13 | Edit Existing CV | ⬜ | |
| 14 | Database Integration | ⬜ | |
| 15 | Error Handling | ⬜ | |

**Overall Status**: ⬜ All Pass  ⬜ Some Failures  ⬜ Major Issues

---

## 📝 Additional Notes

_Use this space to record any observations, bugs found, or suggestions for improvement:_




---

**Testing Complete!** ✅
