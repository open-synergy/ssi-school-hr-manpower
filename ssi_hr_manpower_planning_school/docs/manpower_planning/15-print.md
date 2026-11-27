# Print Manpower Planning Summary

> **Module:** `ssi_hr_manpower_planning_school`\
> **Extends:** ssi_hr_manpower_planning — model `manpower_planning`, aksi `15-print`

## Additional Pre-Condition

- **Module:** `ssi_hr_manpower_planning_school` is installed.
- **Data:** The planning has a **School** and at least one **Teaching** or **Additional
  Assignments** line (optional; a planning without them is printed as the base work
  instruction describes).

## Additional Post-Condition

- The **School Recap** table is shown below the planning header of the HTML and PDF
  summary. It lists, per school, academic year and category, the needed, filled and
  vacant manpower with the filled and vacant percentage.
- The report shows the following parts before the contract review lines; a part with no
  line is not printed, and its title is not printed either:
  - **Teaching**: subject, grade, classes, weekly hours per class, total classes, total
    weekly hours, teacher and co-teacher of each line. A line without a teacher shows
    **Vacant**.
  - **Additional Assignments**: assignment type, category, hour basis, employee, hours
    and number of classes of each line. A line without an employee shows **Vacant**.
  - **Workload**: per employee, the teaching hours, co-teaching hours, assignment hours
    per week, picket hours per week, total weekly hours, mandatory weekly hours and the
    lacking and excess weekly hours. The row of the lines without an employee shows
    **Vacant**.
- The **Manpower Planning Summary XLSX** workbook has the same **Teaching**,
  **Additional Assignments** and **Workload** parts on the worksheet of the planning,
  before the contract review. It also has a **School Recap** worksheet that sums the
  planning of the same school and academic year when several plannings are printed
  together.
- A planning without lines of the **Teaching** and **Additional Assignments** tabs shows
  no **Teaching** part, and a planning without a **School** shows no **School Recap**
  and no school part. Its printout is the same as before this module.
