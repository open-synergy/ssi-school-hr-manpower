# Generate Teaching Lines from Curriculum

> **Module:** `ssi_hr_manpower_planning_school`\
> **Model:** `manpower_planning`\
> **Menu:** Human Resource > Manpower Planning > Manpower Plannings\
> **Actor:** user in group _Manpower Planning: User_\
> **State:** `draft`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status of the planning is **Draft**.
- **Record:** **Curriculum** is filled on the **School** tab of the planning, with a
  school curriculum of the planning **School**. The button is not shown without it.
- **Data:** The curriculum has lines, and the classes of the planning school exist for
  the grades of those lines (optional; nothing is generated without them).
- **Module:** `ssi_hr_manpower_planning_school` is installed.
- **Access:** user in group _Manpower Planning: User_.

## Flow

1. Open the **Human Resource > Manpower Planning > Manpower Plannings** menu.
2. Open the draft planning to fill.
3. Click the **Generate from Curriculum** button.

## Post-Condition

- The planning is displayed again.
- One line is added to the **Teaching** tab for each line of the curriculum:
  - **Subject** and **Grade** are the subject and the grade of the curriculum line.
  - **Classes** are all the classes of the planning school that have that grade.
  - **Weekly Hours per Class** is the weekly hours of the curriculum line.
  - **Teacher** is empty, so the line is vacant. Select the teacher on the line.
- A curriculum line is skipped when the planning already has a **Teaching** line with
  the same subject and grade, or when the planning school has no class of that grade.
- Generating again adds nothing for the lines already present. Existing lines are never
  changed or removed.
- The added lines stay plan lines that can be edited like any other **Teaching** line.

## Validation

- Generating fails **if** the planning is not **Draft** or has no **Curriculum**.
- Generating fails **if** a generated line breaks a rule of the **Teaching** tab, such
  as a class that another line of the same subject in the planning already uses.
