# Edit Manpower Planning

> **Module:** `ssi_hr_manpower_planning_school`\
> **Extends:** ssi_hr_manpower_planning — model `manpower_planning`, aksi `02-edit`

## Additional Pre-Condition

- **Module:** `ssi_hr_manpower_planning_school` is installed.

## Additional Fields

- The **School**, **Academic Year** and **Curriculum** fields of the **School** tab, and
  the lines of the **Teaching** and **Additional Assignments** tabs, can be changed only
  while the planning is **Draft**. Their fields are described in the Create Manpower
  Planning work instruction of this module.

- The **Teaching Assignment Lines** tags of a **Teaching** line, filled by the import
  from a teaching assignment, can be changed like the other columns of the line.

## Modified Validation

- Saving fails with the same rules as at creation when a **Teaching** line is changed to
  a subject that is not applicable to the grade, to weekly hours lower than 1, to a
  co-teacher equal to the teacher, or to a class already used by another line of the
  same subject.

## Additional Post-Condition

- The **Workload** tab is recalculated from the changed lines.
