# Import Teaching Lines from Teaching Assignment

> **Module:** `ssi_hr_manpower_planning_school`\
> **Model:** `manpower_planning`\
> **Menu:** Human Resource > Manpower Planning > Manpower Plannings\
> **Actor:** user in group _Manpower Planning: User_\
> **State:** `draft`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status of the planning is **Draft**.
- **Record:** **School** is filled on the **School** tab of the planning. When
  **Academic Year** is filled too, only the terms of that year can be imported.
- **Data:** The school teaching assignments of the term exist, with lines for the
  homerooms of the planning school (optional; nothing is imported without them).
- **Module:** `ssi_hr_manpower_planning_school` is installed.
- **Access:** user in group _Manpower Planning: User_.

## Flow

1. Open the **Human Resource > Manpower Planning > Manpower Plannings** menu.
2. Open the draft planning to fill.
3. Click the **Import from Teaching Assignment** button.
4. In the wizard that appears, fill in the fields:
   - **Academic Term** _(required)_: Select the term (semester) whose teaching
     assignments are imported. When the planning has an **Academic Year**, only the
     terms of that year are listed.
5. Click **Import**.

## Post-Condition

- The wizard closes and the planning is displayed again.
- One line is added to the **Teaching** tab for each group of main teaching assignment
  lines of the school and the term that share the subject, the grade, the teacher
  employee and the weekly hours:
  - **Classes** are the classes of the grouped lines.
  - **Weekly Hours per Class** is the weekly hours of the grouped lines.
  - **Teacher** is the employee of the teacher. A line is vacant when the teacher has no
    employee.
  - **Co-Teacher** is the employee of the assistant lines that teach the same subject in
    those classes, only when they all point to exactly one employee other than the
    teacher.
  - **Teaching Assignment Lines** shows the main lines, and the assistant lines used,
    the plan line was imported from.
- The added lines stay plan lines that can be edited like any other **Teaching** line.
- Lines already linked to a line of the planning are skipped, so importing again adds
  nothing. Existing lines are never changed or removed.

## Validation

- The import fails **if** the planning is not **Draft** or has no **School**.
- The import fails **if** an imported line breaks a rule of the **Teaching** tab, such
  as a class that another line of the same subject in the planning already uses, or
  weekly hours lower than 1.
